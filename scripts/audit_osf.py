#!/usr/bin/env python3
"""Anonymous, bounded OSF file inventory and selected-file readability audit.

The cache may contain research data: keep it outside the published repository.
This program never executes downloaded code. Inventory is not dataset validation.
Requires curl; workbook parsing additionally uses openpyxl. Uses HTTP/1.1 because
HTTP/2 downloads failed during the 2026-10-19 OSF infrastructure migration.
"""
import argparse
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import fcntl
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXTRA_IDS = {'C002': ['cs5z3'], 'C006': ['wq2g7'], 'C010': ['5kr8s']}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


class Client:
    def __init__(self, cache):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)

    def throttle(self):
        # Shared across threads and processes so supplemental checks do not
        # evade the anonymous service's request limits.
        with (self.cache/'request-rate.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            lock.seek(0)
            try:last=float(lock.read() or 0)
            except ValueError:last=0
            time.sleep(max(0,1.8-(time.time()-last)))
            lock.seek(0);lock.truncate();lock.write(str(time.time()));lock.flush()

    def api_budget_available(self):
        # OSF documents 100 anonymous requests/hour. Leave room for ordinary
        # browsing. Download URLs are separate from metadata API requests.
        recent=[]
        for path in (self.cache/'http').glob('*.json'):
            try:
                m=json.loads(path.read_text())
                if 'api.osf.io/' in m.get('url',''):
                    recent.extend(a for a in m.get('attempts',[]) if
                        time.time()-datetime.fromisoformat(a['checked_at']).timestamp()<3600)
            except (ValueError,KeyError):
                continue
        return len(recent)<90 and not any(a.get('http_status')==429 for a in recent)

    def get(self, url, *, api=True, max_bytes=50_000_000, refresh=False):
        if api:
            parts = urlsplit(url)
            query = dict(parse_qsl(parts.query))
            query['page[size]'] = '100'
            url = urlunsplit((*parts[:3], urlencode(query), parts.fragment))
        key = hashlib.sha256(url.encode()).hexdigest()
        meta_path = self.cache / 'http' / (key + '.json')
        body_path = self.cache / 'http' / (key + '.body')
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        if meta_path.exists() and body_path.exists() and not refresh:
            old = json.loads(meta_path.read_text())
            if old.get('http_status') == 200:
                return old, body_path
        attempts = []
        for attempt in range(3):
            if api and not self.api_budget_available():
                return {'url':url,'http_status':0,'curl_exit':0,'attempts':[],
                        'not_attempted_reason':'anonymous_api_hourly_budget_or_recent_429',
                        'checked_at':now()},body_path
            self.throttle()
            args = ['curl', '--http1.1', '-4', '-L', '--connect-timeout', '8',
                    '--max-time', '90' if not api else '25', '--max-filesize', str(max_bytes),
                    '-sS', '-o', str(body_path), '-w', '%{http_code}\n%{content_type}\n%{size_download}', url]
            run = subprocess.run(args, capture_output=True, text=True)
            fields = run.stdout.splitlines()
            status = int(fields[0]) if fields and fields[0].isdigit() else 0
            attempts.append({'http_status': status, 'curl_exit': run.returncode,
                             'error': run.stderr.strip()[:300], 'checked_at': now()})
            if status==429:
                break
            if status not in (0, 429, 500, 502, 503, 504) and run.returncode != 18:
                break
            time.sleep([2, 5, 10][attempt])
        result = {'url': url, 'http_status': status, 'content_type': fields[1] if len(fields)>1 else '',
                  'curl_exit': run.returncode, 'bytes_received': body_path.stat().st_size if body_path.exists() else 0,
                  'attempts': attempts, 'checked_at': now()}
        save(meta_path, result)
        return result, body_path

    def json(self, url):
        meta, path = self.get(url)
        if meta['http_status'] != 200 or meta['curl_exit']:
            return meta, None
        try:
            return meta, json.loads(path.read_bytes())
        except (ValueError, UnicodeError):
            return meta, None

    def pages(self, url, log, max_pages=15):
        rows = []
        seen = set()
        while url and url not in seen and len(seen) < max_pages:
            seen.add(url)
            meta, value = self.json(url)
            log.append(meta)
            if value is None:
                return rows, False
            data = value.get('data', [])
            if not isinstance(data, list):
                return rows, False
            rows.extend(data)
            url = value.get('links', {}).get('next')
        return rows, not bool(url)


def related(obj, key):
    return obj.get('relationships', {}).get(key, {}).get('links', {}).get('related', {}).get('href')


def queue():
    catalog = json.loads((ROOT/'data/resources.json').read_text())
    candidates = json.loads((ROOT/'data/discovery-candidates.json').read_text())
    return ([{'resource_id': r['id'], 'name': r['name'], 'kind': 'main', 'osf_ids': r['osf_ids'],
              'source_url': r['source_url']} for r in catalog['resources'] if 'osf' in r['platforms']]
            + [{'resource_id': r['id'], 'name': r['name'], 'kind': 'candidate',
                'osf_ids': list(dict.fromkeys([r['osf_id']] + EXTRA_IDS.get(r['id'], []))),
                'source_url': r['source_url']} for r in candidates['candidates']])


def inventory_one(entry, client, *, max_dirs=24, max_files=3000, max_nodes=8):
    log, nodes, files, limits = [], [], [], []
    pending = deque((node_id, 0) for node_id in entry['osf_ids'])
    seen = set()
    while pending and len(seen) < max_nodes:
        node_id, depth = pending.popleft()
        if node_id in seen:
            continue
        seen.add(node_id)
        obj, endpoint = None, None
        for kind in ('nodes', 'registrations'):
            endpoint = f'https://api.osf.io/v2/{kind}/{node_id}/'
            meta, value = client.json(endpoint)
            log.append(meta)
            if value and isinstance(value.get('data'), dict):
                obj = value['data']
                break
            if meta['http_status'] not in (404, 410):
                break
        if obj is None:
            nodes.append({'id': node_id, 'metadata_read': False, 'endpoint': endpoint,
                          'http_status': meta['http_status']})
            continue
        attr = obj.get('attributes', {})
        n = {'id': node_id, 'metadata_read': True, 'endpoint': endpoint, 'type': obj['type'],
             'title': attr.get('title'), 'description': attr.get('description'),
             'public': attr.get('public'), 'category': attr.get('category'),
             'date_modified': attr.get('date_modified'), 'license': attr.get('node_license'),
             'depth': depth, 'providers': []}
        if obj['type'] == 'registrations':
            original = obj.get('relationships', {}).get('registered_from', {}).get('data', {})
            n['registered_from'] = original.get('id')
            if original.get('id') and original['id'] not in seen:
                pending.append((original['id'], depth+1))
        license_url = related(obj, 'license')
        if license_url:
            lm, lv = client.json(license_url)
            log.append(lm)
            if lv:
                n['license'] = lv.get('data', {}).get('attributes', {})
        # Registrations may contain a frozen copy; list their actual files rather
        # than silently substituting the live project behind registered_from.
        providers_url = related(obj, 'files') or endpoint + 'files/'
        providers, complete = client.pages(providers_url, log)
        if not complete:
            limits.append(f'{node_id}: provider list incomplete')
        dirs = deque()
        for provider in providers:
            pa = provider.get('attributes', {})
            n['providers'].append({'id': provider.get('id'), 'name': pa.get('name')})
            href = related(provider, 'files')
            if href:
                dirs.append((href, '', 0))
        seen_dirs = set()
        while dirs and len(seen_dirs) < max_dirs and len(files) < max_files:
            folder_url, parent_path, folder_depth = dirs.popleft()
            if folder_url in seen_dirs:
                continue
            seen_dirs.add(folder_url)
            contents, complete = client.pages(folder_url, log)
            if not complete:
                limits.append(f'{node_id}: folder listing incomplete: {parent_path}')
            for item in contents:
                a = item.get('attributes', {})
                materialized = a.get('materialized_path') or (parent_path.rstrip('/')+'/'+a.get('name', ''))
                if a.get('kind') == 'folder':
                    href = related(item, 'files')
                    if href and folder_depth < 7:
                        dirs.append((href, materialized, folder_depth+1))
                    elif href:
                        limits.append(f'{node_id}: directory depth cap: {materialized}')
                elif a.get('kind') == 'file':
                    files.append({'node_id': node_id, 'file_id': item['id'], 'name': a.get('name'),
                                  'path': materialized, 'provider': a.get('provider'), 'size': a.get('size'),
                                  'date_modified': a.get('date_modified'), 'version': a.get('current_version'),
                                  'hashes': a.get('extra', {}).get('hashes', {}),
                                  'download_url': item.get('links', {}).get('download'),
                                  'html_url': item.get('links', {}).get('html'),
                                  'info_url': item.get('links', {}).get('info')})
        if dirs:
            limits.append(f'{node_id}: inventory cap reached; {len(dirs)} folders not visited')
        nodes.append(n)
        children_url = related(obj, 'children')
        if children_url and depth < 2:
            children, complete = client.pages(children_url, log)
            if not complete:
                limits.append(f'{node_id}: children list incomplete')
            n['children_ids'] = [child['id'] for child in children]
            pending.extend((child['id'], depth+1) for child in children)
    if pending:
        limits.append(f'node cap reached: {len(pending)} nodes not visited')
    return {**entry, 'checked_at': now(), 'nodes': nodes, 'files': files,
            'file_count': len(files), 'inventory_limits': limits, 'requests': log,
            'identity_review': 'pending_manual_review', 'selected_file_checks': []}


def decode(raw):
    for encoding in ('utf-8-sig', 'utf-16', 'cp1252'):
        try:
            text = raw.decode(encoding)
            if '\x00' not in text:
                return text, encoding
        except UnicodeError:
            pass
    raise ValueError('No supported text encoding')


def parse_bytes(raw, name):
    """Only report dimensions/schema; never publish individual observations."""
    suffix = Path(name).suffix.lower()
    if suffix == '.zip' or raw[:4] == b'PK\x03\x04' and suffix not in ('.xlsx', '.docx', '.pptx'):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            infos = [i for i in z.infolist() if not i.is_dir()]
            record = {'format': 'zip', 'parse_status': 'archive_directory_read', 'member_count': len(infos),
                      'uncompressed_bytes': sum(i.file_size for i in infos),
                      'members': [{'name': i.filename, 'size': i.file_size} for i in infos[:500]],
                      'members_omitted': max(0,len(infos)-500), 'member_checks': []}
            candidates = [i for i in infos if Path(i.filename).suffix.lower() in
                          ('.csv', '.tsv', '.txt', '.xlsx', '.json', '.jsonl', '.sav', '.dta', '.rds', '.rdata', '.rda', '.nmg', '.ldt', '.tab')
                          and 0 < i.file_size <= 30_000_000 and '__MACOSX' not in i.filename]
            candidates.sort(key=lambda i: (-data_score({'name': i.filename, 'path': i.filename, 'size':i.file_size}), i.file_size))
            for item in candidates[:4]:
                try:
                    content = z.read(item)
                    parsed = parse_bytes(content, item.filename)
                    record['member_checks'].append({'member': item.filename, 'sha256': hashlib.sha256(content).hexdigest(), **parsed})
                except Exception as exc:
                    record['member_checks'].append({'member':item.filename, 'parse_status':'failed', 'error':type(exc).__name__+': '+str(exc)[:200]})
            return record
    if suffix in ('.xlsx', '.xlsm'):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
        sheets = []
        for sheet in wb:
            rows = sheet.iter_rows(values_only=True)
            header = next(rows, ())
            row_count = sum(1 for row in rows if any(x is not None for x in row))
            sheets.append({'sheet': sheet.title, 'data_rows_after_first_row': row_count,
                           'columns': len(header), 'column_names': [str(x)[:160] if x is not None else '' for x in header]})
        wb.close()
        return {'format':'xlsx', 'parse_status':'parsed_complete_workbook', 'sheets':sheets}
    if suffix == '.xls':
        import pandas as pd
        frames = pd.read_excel(io.BytesIO(raw), sheet_name=None)
        return {'format':'xls', 'parse_status':'parsed_complete_workbook',
                'sheets':[{'sheet':name,'data_rows_after_first_row':len(df),'columns':len(df.columns),
                           'column_names':[str(x) for x in df.columns]} for name,df in frames.items()]}
    if suffix in ('.rds','.rdata','.rda'):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=suffix) as f:
            f.write(raw);f.flush()
            # Base R reads its own serialization; jsonlite only formats schema.
            expression = r'''args<-commandArgs(TRUE); e<-new.env();
if(args[2]==".rds") {assign("rds_object",readRDS(args[1]),e)} else {load(args[1],envir=e)};
inspect<-function(x,n,depth=0) {
 out<-list(name=n,class=class(x),length=length(x));
 if(is.data.frame(x)||is.matrix(x)) {out$rows<-nrow(x);out$columns<-ncol(x);out$column_names<-colnames(x)}
 else if(is.list(x)&&depth<2) {out$members<-lapply(seq_len(min(length(x),20)),function(i) inspect(x[[i]],if(is.null(names(x)))as.character(i) else names(x)[i],depth+1))};out};
out<-lapply(ls(e),function(n)inspect(get(n,e),n));cat(jsonlite::toJSON(out,auto_unbox=TRUE,null="null"))'''
            run=subprocess.run(['Rscript','--vanilla','-e',expression,f.name,suffix],capture_output=True,text=True,timeout=90)
        if run.returncode:
            raise ValueError('R serialization read failed: '+run.stderr[-220:])
        return {'format':suffix[1:], 'parse_status':'parsed_objects', 'objects':json.loads(run.stdout)}
    if suffix in ('.sav','.dta'):
        import pandas as pd
        df = pd.read_spss(io.BytesIO(raw)) if suffix=='.sav' else pd.read_stata(io.BytesIO(raw))
        return {'format':suffix[1:], 'parse_status':'parsed_complete_table', 'rows':len(df),
                'columns':len(df.columns), 'column_names':[str(x) for x in df.columns]}
    if suffix in ('.wav', '.wave'):
        import wave
        with wave.open(io.BytesIO(raw)) as audio:
            frames=audio.readframes(audio.getnframes())
            return {'format':'wav','parse_status':'decoded_pcm_frames','channels':audio.getnchannels(),
                    'sample_rate':audio.getframerate(),'frames':audio.getnframes(),
                    'duration_seconds':audio.getnframes()/audio.getframerate(),'decoded_bytes':len(frames)}
    if suffix == '.pdf':
        import pypdf
        reader=pypdf.PdfReader(io.BytesIO(raw))
        return {'format':'pdf','parse_status':'extracted_text','pages':len(reader.pages),
                'text_characters':sum(len(page.extract_text() or '') for page in reader.pages)}
    if suffix in ('.docx',):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            xml=z.read('word/document.xml')
        import xml.etree.ElementTree as ET
        root=ET.fromstring(xml)
        return {'format':'docx','parse_status':'parsed_document_xml',
                'text_characters':sum(len(t.text or '') for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))}
    if suffix in ('.nmg','.ldt'):
        text,enc=decode(raw)
        records=[];other_lines=0
        for row in csv.reader(io.StringIO(text,newline=None)):
            # ELP key defines six comma-separated behavioral fields. Numeric
            # trial and item IDs distinguish them from demographic/log lines.
            if len(row)==6 and all(re.fullmatch(r'\s*\d+\s*',v) for v in row[:2]):
                records.append(row)
            else:other_lines+=1
        fields=['trial_order','item_serial_number']+(
            ['lexicality','accuracy','LDT_RT','item'] if suffix=='.ldt' else
            ['coding_RT','coding_category','NMG_RT','item'])
        return {'format':suffix[1:],'parse_status':'parsed_trial_sections','encoding':enc,
                'trial_rows':len(records),'columns':6,'column_names':fields,
                'non_trial_lines_excluded':other_lines,
                'measurement_key':'https://osf.io/download/rd632/'}
    if suffix in ('.csv','.tsv','.txt','.dat','.asc','.tab'):
        text, enc = decode(raw)
        # A text file is not automatically a data table. Require multiple rows
        # with at least two fields and a reasonably consistent width.
        sample=text[:60000]
        try:
            dialect=csv.Sniffer().sniff(sample,delimiters=',\t;|')
            delim=dialect.delimiter
        except csv.Error:
            delim='\t' if '\t' in sample else ','
        if not any(c in sample for c in ',\t;|'):
            rows=(re.split(r'\s+',line.strip()) for line in text.splitlines() if line.strip())
            delim='whitespace'
        else:
            rows=csv.reader(io.StringIO(text,newline=None),delimiter=delim)
        widths=Counter(); header=None; count=0
        for row in rows:
            if not row:
                continue
            if header is None:
                header=row
            else:
                widths[len(row)]+=1;count+=1
        width=len(header or [])
        table=width>1 and count>0 and widths.get(width,0)/max(count,1)>=0.90
        return {'format':suffix[1:],'parse_status':'parsed_complete_table' if table else 'decoded_text',
                'encoding':enc,'delimiter':delim,'rows_after_first_row':count,'columns':width,
                'column_names':header if table else [],'row_width_counts':dict(widths),
                'characters':len(text)}
    if suffix in ('.json','.jsonl','.ndjson','.qsf'):
        text,enc=decode(raw)
        obj=json.loads(text) if suffix in ('.json','.qsf') else [json.loads(line) for line in text.splitlines() if line.strip()]
        first=obj[0] if isinstance(obj,list) and obj else obj
        return {'format':suffix[1:],'parse_status':'parsed_complete_json', 'encoding':enc,
                'top_level_type':type(obj).__name__,'length':len(obj) if hasattr(obj,'__len__') else None,
                'keys':list(first)[:100] if isinstance(first,dict) else []}
    if suffix in ('.r','.rmd','.md','.qmd','.py','.sps','.m','.html','.htm','.textgrid'):
        text,enc=decode(raw)
        return {'format':suffix[1:],'parse_status':'decoded_text','encoding':enc,
                'characters':len(text),'lines':len(text.splitlines())}
    if suffix in ('.png','.jpg','.jpeg'):
        from PIL import Image
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
            return {'format':img.format,'parse_status':'decoded_image','width':img.width,'height':img.height}
    return {'format':suffix[1:], 'parse_status':'download_only_no_supported_parser'}


def data_score(file):
    path=file.get('path',file.get('name','')).lower()
    ext=Path(path).suffix
    score=0
    if ext in ('.csv','.tsv','.xlsx','.xls','.rds','.rdata','.rda','.sav','.dta','.jsonl'):
        score+=10
    if ext=='.zip': score+=5
    if ext=='.txt': score+=2
    if re.search(r'data|raw|clean|response|rating|norm|trial|participant|res_humans|result',path): score+=9
    if re.search(r'stimuli|stimulus|materials|filler|poster|script|model|contrast|summary|output|backup',path): score-=8
    if re.search(r'readme|dictionary|codebook',path): score+=3
    if ext in ('.r','.rmd','.pdf','.docx','.pptx','.png','.jpg','.wav','.mp3'):score-=9
    if file.get('size',0) and file['size']>50_000_000:score-=25
    return score


def download_one(file, client, max_bytes=50_000_000):
    result={key:file.get(key) for key in ('node_id','file_id','name','path','download_url','size','version','date_modified')}
    url=file.get('download_url')
    if not url:
        return {**result,'download_status':'no_download_url'}
    if file.get('size') and file['size']>max_bytes:
        return {**result,'download_status':'not_attempted_exceeds_size_cap','max_bytes':max_bytes}
    meta,path=client.get(url,api=False,max_bytes=max_bytes)
    result['request']=meta
    result['download_status']='complete' if meta['http_status']==200 and meta['curl_exit']==0 else 'failed'
    if result['download_status']!='complete':return result
    raw=path.read_bytes()
    result['sha256']=hashlib.sha256(raw).hexdigest()
    result['downloaded_bytes']=len(raw)
    result['listed_size_matches']=file.get('size')==len(raw) if file.get('size') is not None else None
    published=file.get('hashes',{}).get('sha256')
    result['published_sha256_matches']=result['sha256']==published if published else None
    if b'<!DOCTYPE html' in raw[:100] or b'<html' in raw[:100]:
        result['html_instead_of_data']=True
    try:
        result['parse']=parse_bytes(raw,file['name'])
    except Exception as exc:
        result['parse']={'parse_status':'failed','error':type(exc).__name__+': '+str(exc)[:250]}
    result['data_role']='pending_manual_review'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['inventory','download'])
    parser.add_argument('--cache',required=True)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--ids',nargs='*')
    parser.add_argument('--selected',help='JSON mapping resource IDs to file IDs; overrides ranking')
    parser.add_argument('--files-per-resource',type=int,default=2)
    parser.add_argument('--retry-incomplete',action='store_true',help='Re-enumerate incomplete inventories, preserving prior file reads')
    parser.add_argument('--max-bytes',type=int,default=50_000_000)
    args=parser.parse_args();client=Client(args.cache)
    entries=queue()
    if args.ids:entries=[x for x in entries if x['resource_id'] in args.ids]
    if args.stage=='inventory':
        def run(entry):
            dest=Path(args.cache)/'inventories'/(entry['resource_id']+'.json')
            old=json.loads(dest.read_text()) if dest.exists() else None
            if old and not args.retry_incomplete:return old
            result=inventory_one(entry,client)
            if old:
                result['selected_file_checks']=old.get('selected_file_checks',[])
            save(dest,result);return result
    else:
        selection=json.loads(Path(args.selected).read_text()) if args.selected else None
        def run(entry):
            dest=Path(args.cache)/'inventories'/(entry['resource_id']+'.json')
            result=json.loads(dest.read_text())
            files=result['files']
            if selection is not None:
                wanted=selection.get(entry['resource_id'],[])
                files=[x for x in files if x['file_id'] in wanted]
            else:
                files=sorted([x for x in files if data_score(x)>0],key=lambda x:(-data_score(x),x.get('size') or 0))[:args.files_per_resource]
            existing={x['file_id']:x for x in result.get('selected_file_checks',[])}
            for file in files:existing[file['file_id']]=download_one(file,client,args.max_bytes)
            result['selected_file_checks']=list(existing.values());save(dest,result);return result
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(run,entry):entry for entry in entries}
        for future in as_completed(futures):
            entry=futures[future]
            try:
                result=future.result()
                print(json.dumps({'resource_id':result['resource_id'],'files':result['file_count'],
                                  'limits':len(result['inventory_limits']),
                                  'nodes':[(n['id'],n.get('title'),n.get('http_status')) for n in result['nodes']],
                                  'checks':[(c['name'],c.get('download_status'),c.get('parse',{}).get('parse_status')) for c in result['selected_file_checks']]},ensure_ascii=False),flush=True)
            except Exception as exc:
                print(json.dumps({'resource_id':entry['resource_id'],'error':repr(exc)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
