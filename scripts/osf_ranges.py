#!/usr/bin/env python3
"""Read bounded public-file byte ranges without claiming complete downloads.

Raw responses and redirect headers stay in --cache, outside the catalogue.
CSV previews omit the last possibly truncated line. ZIP previews inspect the
central directory and decompress only a bounded prefix of a chosen CSV member.
Neither scope validates a complete archive or a complete observation table.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import zipfile
import zlib
from audit_osf import now, save
from osf_resume import parse_table


def fetch(url, interval, cache):
    key=hashlib.sha256((url+'#range='+interval).encode()).hexdigest()
    path=cache/(key+'.body');header=cache/(key+'.headers')
    run=subprocess.run(['curl','--http1.1','-4','-L','--connect-timeout','10',
        '--max-time','60','--max-filesize','3000000','--range',interval,
        '-sS','-D',str(header),'-o',str(path),'-w','%{http_code}',url],capture_output=True,text=True)
    raw=path.read_bytes() if path.exists() else b''
    content_ranges=[line.strip() for line in header.read_text(errors='replace').splitlines()
                    if line.lower().startswith('content-range:')] if header.exists() else []
    result={'url':url,'requested_range':interval,'checked_at':now(),
        'http_status':int(run.stdout) if run.stdout.isdigit() else 0,
        'curl_exit':run.returncode,'error':run.stderr.strip()[:240],
        'bytes_received':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
        'content_range':content_ranges[-1] if content_ranges else None}
    save(cache/(key+'.json'),result)
    if result['http_status']!=206 or run.returncode:
        raise ValueError(json.dumps(result))
    return raw,result


def csv_prefix(raw,name):
    end=raw.rfind(b'\n')
    if end<0:raise ValueError('No complete line in bounded prefix')
    parsed=parse_table(raw[:end+1],name)
    parsed['parse_status']='parsed_bounded_table_prefix'
    parsed['truncated_final_line_omitted']=True
    return parsed


def check(file,cache):
    result={**file,'checked_at':now(),'download_status':'partial_range',
            'complete_parent_file_downloaded':False,'requests':[]}
    if file['name'].lower().endswith('.zip'):
        tail,req=fetch(file['download_url'],'-65557',cache);result['requests'].append(req)
        if not file.get('size'):raise ValueError('Archive size required from source inventory')
        offset=file['size']-len(tail)
        with zipfile.ZipFile(io.BytesIO(tail)) as archive:
            infos=archive.infolist()
        result['archive_members']=[{'name':x.filename,'uncompressed_bytes':x.file_size,
            'compressed_bytes':x.compress_size} for x in infos]
        candidates=[x for x in infos if x.filename.lower().endswith(('.csv','.tsv','.txt'))
                    and not x.filename.startswith('__MACOSX/')]
        if not candidates:raise ValueError('No text table member in inspected directory')
        member=min(candidates,key=lambda x:x.compress_size)
        start=member.header_offset+offset
        header,req=fetch(file['download_url'],f'{start}-{start+4095}',cache)
        result['requests'].append(req)
        if header[:4]!=b'PK\x03\x04':raise ValueError('Local ZIP header not found')
        fn,extra=struct.unpack_from('<HH',header,26)
        data_start=start+30+fn+extra
        stop=data_start+min(member.compress_size,262144)-1
        compressed,req=fetch(file['download_url'],f'{data_start}-{stop}',cache)
        result['requests'].append(req)
        if member.compress_type==8:
            decoder=zlib.decompressobj(-15);plain=decoder.decompress(compressed,3000000)
        elif member.compress_type==0:plain=compressed
        else:raise ValueError('Unsupported ZIP compression method')
        result.update({'read_scope':'archive_directory_and_member_prefix',
            'member_name':member.filename,'member_complete':False,
            'member_prefix_bytes':len(plain),'member_prefix_sha256':hashlib.sha256(plain).hexdigest(),
            'parse':csv_prefix(plain,member.filename)})
    else:
        raw,req=fetch(file['download_url'],'0-262143',cache);result['requests'].append(req)
        result.update({'read_scope':'table_prefix','parse':csv_prefix(raw,file['name'])})
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',required=True)
    p.add_argument('--ids',nargs='+',required=True);args=p.parse_args()
    base=Path(args.cache);cache=base/'ranges';cache.mkdir(exist_ok=True)
    for rid in args.ids:
        inv=json.loads((base/'resume-inventories'/(rid+'.json')).read_text())
        name='ia_Paragraph.csv.zip' if rid=='R123' else 'compiled.csv'
        file=next(f for f in inv['files'] if f['name']==name)
        try:result=check(file,cache)
        except Exception as exc:result={**file,'checked_at':now(),'read_scope':'failed_range_attempt','error':str(exc)[:1500]}
        save(cache/(rid+'.json'),result)
        print(json.dumps({'id':rid,'scope':result['read_scope'],'parse':result.get('parse')}),flush=True)


if __name__=='__main__':main()
