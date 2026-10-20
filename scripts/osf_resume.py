#!/usr/bin/env python3
"""Continue a frozen OSF queue with breadth-first, budget-aware file checks.

Read one public storage listing per entry before expanding large projects.
Only transport/parser evidence is produced; data roles and promotions require
source and variable review. Reuses audit_osf's anonymous hourly budget and cache.
"""
import argparse
import bz2
from collections import Counter
import csv
import gzip
import hashlib
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile
from urllib.parse import urlsplit
from audit_osf import Client, data_score, download_one, now, parse_bytes, related, save


def parse_table(raw,name):
    if raw.startswith((b'\xff\xfe',b'\xfe\xff')):
        text=raw.decode('utf-16');encoding='utf-16-bom'
    else:
        try:text=raw.decode('utf-8-sig');encoding='utf-8-sig'
        except UnicodeDecodeError:
            # Successful arbitrary UTF-16 decoding is not evidence of UTF-16.
            # Prefer source-compatible single-byte text unless a BOM says so.
            import chardet
            guess=chardet.detect(raw[:200000]);encoding=guess.get('encoding') or 'cp1252'
            if 'utf-16' in encoding.lower() and b'\x00' not in raw[:1000]:encoding='cp1252'
            try:text=raw.decode(encoding)
            except (UnicodeError,LookupError):text=raw.decode('cp1252');encoding='cp1252'
    sample=text[:60000]
    try:delimiter=csv.Sniffer().sniff(sample,delimiters=',\t;|').delimiter
    except csv.Error:delimiter='\t' if '\t' in sample else ','
    if not any(c in sample for c in ',\t;|'):
        rows=(re.split(r'\s+',line.strip()) for line in text.splitlines() if line.strip());delimiter='whitespace'
    else:rows=csv.reader(io.StringIO(text,newline=None),delimiter=delimiter)
    header=None;widths=Counter();n=0
    for row in rows:
        if not row:continue
        if header is None:header=row
        else:widths[len(row)]+=1;n+=1
    width=len(header or []);table=width>1 and n>0 and widths.get(width,0)/n>=.90
    return {'format':Path(name).suffix.lower()[1:],'parse_status':'parsed_complete_table' if table else 'decoded_text',
            'encoding':encoding,'delimiter':delimiter,'rows_after_first_row':n,'columns':width,
            'column_names':header if table else [],'row_width_counts':dict(widths),'characters':len(text)}


def extended_parse(raw,name):
    suffix=Path(name).suffix.lower()
    if suffix in ('.csv','.tsv','.txt','.dat','.asc','.tab'):return parse_table(raw,name)
    if suffix=='.zip':
        parsed=parse_bytes(raw,name)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            checked={f.get('member') or f.get('name') for f in parsed.get('member_checks',[])}
            for info in archive.infolist():
                if info.filename in checked or not info.filename.lower().endswith(('.csv','.tsv')):continue
                if info.file_size>150_000_000:continue
                digest=hashlib.sha256()
                with archive.open(info) as member:
                    for chunk in iter(lambda:member.read(1024*1024),b''):digest.update(chunk)
                delimiter='\t' if info.filename.lower().endswith('.tsv') else ','
                widths=Counter();header=None;n=0
                with archive.open(info) as member:
                    for row in csv.reader(io.TextIOWrapper(member,encoding='utf-8-sig',newline=''),delimiter=delimiter):
                        if header is None:header=row
                        else:widths[len(row)]+=1;n+=1
                parsed.setdefault('member_checks',[]).append({'name':info.filename,
                    'bytes':info.file_size,'sha256':digest.hexdigest(),'crc_checked_by_zip_reader':True,
                    'parse':{'format':'csv','parse_status':'parsed_complete_table',
                    'encoding':'utf-8-sig','delimiter':delimiter,'rows_after_first_row':n,
                    'columns':len(header or []),'column_names':header or [],'row_width_counts':dict(widths)}})
        return parsed
    if suffix in ('.rtf','.doc'):
        with tempfile.NamedTemporaryFile(suffix=suffix) as f:
            f.write(raw);f.flush()
            run=subprocess.run(['/usr/bin/textutil','-convert','txt','-stdout','-format',suffix[1:],f.name],
                capture_output=True,timeout=30)
        if run.returncode==0 and run.stdout:
            text=run.stdout.decode('utf-8')
            return {'format':suffix[1:],'parse_status':'extracted_document_text',
                    'characters':len(text),'lines':len(text.splitlines())}
        return {'format':suffix[1:],'parse_status':'download_only_no_supported_parser'}
    if suffix in ('.bz2','.gz'):
        opener=bz2.BZ2File if suffix=='.bz2' else gzip.GzipFile
        with opener(io.BytesIO(raw)) as f:plain=f.read(150_000_001)
        if len(plain)>150_000_000:return {'format':suffix[1:],'parse_status':'decompression_exceeds_150MB_cap'}
        return {'format':suffix[1:],'parse_status':'decompressed_complete_member','uncompressed_bytes':len(plain),
                'member_sha256':hashlib.sha256(plain).hexdigest(),'member_parse':extended_parse(plain,name[:-len(suffix)])}
    if suffix=='.sav':
        with tempfile.NamedTemporaryFile(suffix='.sav') as f:
            f.write(raw);f.flush()
            code='a<-commandArgs(TRUE);d<-foreign::read.spss(a[1],to.data.frame=TRUE,use.value.labels=FALSE);cat(jsonlite::toJSON(list(rows=nrow(d),columns=ncol(d),column_names=names(d)),auto_unbox=TRUE))'
            run=subprocess.run(['Rscript','--vanilla','-e',code,f.name],capture_output=True,text=True,timeout=90)
        if run.returncode:raise ValueError(run.stderr[-250:])
        return {'format':'sav','parse_status':'parsed_complete_table',**json.loads(run.stdout)}
    if suffix=='.mat':
        from scipy.io import loadmat
        try:
            arrays=loadmat(io.BytesIO(raw))
            return {'format':'mat','parse_status':'loaded_mat_variables','variables':[
                {'name':key,'shape':list(value.shape),'dtype':str(value.dtype),'elements':int(value.size)}
                for key,value in arrays.items() if not key.startswith('__') and hasattr(value,'shape')]}
        except NotImplementedError:
            import h5py
            with h5py.File(io.BytesIO(raw),'r') as f:
                records=[]
                def visit(key,value):
                    if isinstance(value,h5py.Dataset):
                        entry={'name':key,'shape':list(value.shape),'dtype':str(value.dtype)}
                        if value.shape and all(value.shape):
                            # HDF5 containers can be much larger when decoded;
                            # explicitly distinguish sample reads from full reads.
                            value[tuple(slice(0,min(2,n)) for n in value.shape)]
                            entry['read_scope']='first_two_per_dimension'
                        records.append(entry)
                f.visititems(visit)
            return {'format':'mat_hdf5','parse_status':'hdf5_hierarchy_and_selected_values_read','datasets':records}
    if suffix in ('.cha','.eaf','.xml'):
        text=raw.decode('utf-8-sig')
        return {'format':suffix[1:],'parse_status':'decoded_text','characters':len(text),'lines':len(text.splitlines())}
    return parse_bytes(raw,name)


def absorb(items, result, folder='/', endpoint=None):
    for item in items:
        a=item.get('attributes',{});kind=a.get('kind')
        path=a.get('materialized_path') or folder.rstrip('/')+'/'+a.get('name','')
        if kind=='folder':
            href=related(item,'files')
            if href and not any(f['url']==href for f in result['folders']):
                result['folders'].append({'url':href,'path':path,'visited':False})
        elif kind=='file':
            n=item.get('relationships',{}).get('node',{}).get('data',{}).get('id')
            if not any(f['file_id']==item['id'] for f in result['files']):
                result['files'].append({'node_id':n,'file_id':item['id'],'name':a.get('name'),
                  'path':path,'provider':a.get('provider'),'size':a.get('size'),
                  'version':a.get('current_version'),'date_modified':a.get('date_modified'),
                  'hashes':a.get('extra',{}).get('hashes',{}),
                  'download_url':item.get('links',{}).get('download'),
                  'html_url':item.get('links',{}).get('html')})


def empty(entry):
    return {**entry,'checked_at':now(),'nodes':[],'requests':[],'files':[],
            'folders':[],'roots':[],'limits':[],'selected_file_checks':[]}


def roots(entry,client,old=None):
    result=old or empty(entry)
    if result['roots'] or result.get('source_requires_authentication'):
        return result
    if entry['kind']=='candidate_source':
        node_id=entry['osf_ids'][0]
        meta,value=client.json(f'https://api.osf.io/v2/nodes/{node_id}/')
        result['requests'].append(meta)
        if not value:
            result['source_requires_authentication']=meta['http_status'] in (401,403)
            result['source_metadata_failure']=meta
            return result
        node=value['data'];a=node.get('attributes',{})
        result['nodes'].append({'id':node_id,'title':a.get('title'),'public':a.get('public'),
                                'description':a.get('description'),'type':node['type']})
        if a.get('public') is not True:
            result['source_requires_authentication']=True
            return result
    for node_id in entry['osf_ids']:
        for typ in ('nodes','registrations'):
            url=f'https://api.osf.io/v2/{typ}/{node_id}/files/osfstorage/'
            items,complete=client.pages(url,result['requests'])
            m=result['requests'][-1]
            if m['http_status']==200:
                result['roots'].append({'node_id':node_id,'type':typ,'url':url,'complete':complete})
                absorb(items,result,endpoint=url)
                if not complete:result['limits'].append('Root listing not complete: '+url)
                break
            if m['http_status']!=404:
                result['limits'].append('Storage endpoint not read: '+url)
                break
        # A representative public release is sufficient for a selected-file
        # check; record the uninspected alias/version rather than count twice.
        if result['files'] or result['folders']:
            break
    result['checked_at']=now()
    return result


def folder_score(folder):
    path=folder['path'].lower();score=0
    if re.search('data|raw|clean|rating|trial|response|corpus|norm|transcript',path):score+=12
    if re.search('code|analys|figure|paper|poster|stimuli|material|image|prereg',path):score-=8
    if re.search('version|release',path):score+=2
    return score


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['roots','expand','read'])
    p.add_argument('--cache',required=True)
    p.add_argument('--queue',required=True)
    p.add_argument('--ids',nargs='*')
    p.add_argument('--workers',type=int,default=3)
    p.add_argument('--folders-per-entry',type=int,default=1)
    p.add_argument('--files-per-entry',type=int,default=2)
    p.add_argument('--max-bytes',type=int,default=80_000_000)
    p.add_argument('--selected',help='JSON mapping entry IDs to exact file IDs')
    args=p.parse_args();cache=Path(args.cache);client=Client(cache)
    entries=json.loads(Path(args.queue).read_text())
    if args.ids:entries=[e for e in entries if e['resource_id'] in args.ids]
    selection=json.loads(Path(args.selected).read_text()) if args.selected else None
    def run(entry):
        dest=cache/'resume-inventories'/(entry['resource_id']+'.json')
        result=json.loads(dest.read_text()) if dest.exists() else empty(entry)
        if args.stage=='roots':result=roots(entry,client,result)
        elif args.stage=='expand':
            for _ in range(args.folders_per_entry):
                folders=sorted([f for f in result['folders'] if not f['visited']],key=lambda f:(-folder_score(f),f['path']))
                if not folders:break
                folder=folders[0]
                items,complete=client.pages(folder['url'],result['requests'])
                if result['requests'][-1]['http_status']==200:
                    folder['visited']=True;folder['listing_complete']=complete
                    absorb(items,result,folder['path'],folder['url'])
                else:
                    result['limits'].append('Folder not read: '+folder['path']);break
        else:
            files=result['files']
            if selection is not None:files=[f for f in files if f['file_id'] in selection.get(entry['resource_id'],[])]
            else:
                files=sorted([f for f in files if data_score(f)>0 and (f.get('size') or 0)<=args.max_bytes],
                             key=lambda f:(-data_score(f),f.get('size') or 0))[:args.files_per_entry]
            checks={c['file_id']:c for c in result['selected_file_checks']}
            for f in files:
                checked=download_one(f,client,args.max_bytes)
                previous=checks.get(f['file_id'])
                if previous and previous.get('request')!=checked.get('request'):
                    checked['previous_requests']=previous.get('previous_requests',[])+[previous['request']]
                if checked.get('download_status')=='complete':
                    path=cache/'http'/(hashlib.sha256(f['download_url'].encode()).hexdigest()+'.body')
                    try:checked['parse']=extended_parse(path.read_bytes(),f['name'])
                    except Exception as exc:checked['parse']={'parse_status':'failed','error':type(exc).__name__+': '+str(exc)[:250]}
                checks[f['file_id']]=checked
            result['selected_file_checks']=list(checks.values())
        save(dest,result)
        return {'id':entry['resource_id'],'files':len(result['files']),
                 'unvisited_folders':sum(not f['visited'] for f in result['folders']),
                 'last_http':result['requests'][-1].get('http_status') if result['requests'] else None,
                 'source_requires_auth':result.get('source_requires_authentication',False),
                 'checks':[(c['name'],c['download_status'],c.get('parse',{}).get('parse_status')) for c in result['selected_file_checks']]}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        fs={pool.submit(run,e):e for e in entries}
        for f in as_completed(fs):
            try:print(json.dumps(f.result(),ensure_ascii=False),flush=True)
            except Exception as exc:print(json.dumps({'id':fs[f]['resource_id'],'error':repr(exc)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
