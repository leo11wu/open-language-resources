#!/usr/bin/env python3
"""Search the resource catalog without third-party dependencies."""
import argparse
import json
from pathlib import Path
from verification import CHECK_LABELS, check_state

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT/'data/resources.json').read_text(encoding='utf-8'))
    labels = {c['id']:c['label'] for c in catalog['categories']}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keyword',nargs='?',default='')
    parser.add_argument('--category',choices=list(labels))
    parser.add_argument('--access',choices=list(catalog['access_modes']))
    parser.add_argument('--lang',help='Language search tag, e.g. zh or en; zh includes zh-Hans/zh-Hant')
    parser.add_argument('--tag',help='Exact Chinese topic tag, e.g. 词频')
    parser.add_argument('--index',choices=['main','norare','candidates'],default='main',help='Search main catalog, source metadata, or unconfirmed leads')
    parser.add_argument('--platform',help='Hosting/discovery platform, e.g. osf or github (main only)')
    parser.add_argument('--origin',choices=['human_observations','human_norms','corpus_annotation','synthetic_stimuli','derived_data','mixed_or_unspecified','materials_only','discovery_portal'])
    parser.add_argument('--status',choices=['released_data','described_resource','materials_only','discovery_portal'])
    parser.add_argument('--evidence',help='Evidence type, e.g. publisher_data_statement (main only)')
    parser.add_argument('--check-state',choices=list(CHECK_LABELS),help='Recorded file-check scope, independent of data release status (main only)')
    parser.add_argument('--format',choices=['text','json'],default='text')
    args = parser.parse_args()
    if args.index!='main':
        unsupported=args.access or args.origin or args.status or args.evidence or args.platform or args.check_state
        if unsupported: parser.error('Access, platform, origin, status and evidence filters apply to the main catalog only.')
        if args.index=='norare' and args.category: parser.error('The NoRaRe source index has measure/language tags, not main-catalog categories.')
        if args.index=='norare':
            rows=json.loads((ROOT/'data/source-indexes/norare.json').read_text())['records']
        else:
            rows=json.loads((ROOT/'data/discovery-candidates.json').read_text())['candidates']
        lang_alias={'zh':'zho','cmn':'zho','en':'eng','es':'spa','de':'deu','fr':'fra','nl':'nld','pl':'pol','it':'ita','ru':'rus','ja':'jpn','ko':'kor','pt':'por'}
        selected=[]
        for r in rows:
            if args.category and r.get('category')!=args.category: continue
            if args.tag and args.tag not in r.get('search_tags',[]): continue
            if args.lang:
                if args.index=='candidates': parser.error('The candidates index has no verified language tags; use a keyword instead.')
                code=lang_alias.get(args.lang.split('-')[0].lower(),args.lang.lower())
                labels_language=' '.join(r['language_scope']).casefold()
                language_names={'zho':'chinese','eng':'english','spa':'spanish','deu':'german','fra':'french','nld':'dutch','ita':'italian','rus':'russian','jpn':'japanese','kor':'korean','por':'portuguese','pol':'polish'}
                if code not in r['language_codes'] and language_names.get(code,code) not in labels_language: continue
            text=json.dumps(r,ensure_ascii=False).casefold()
            if args.keyword.casefold() not in text: continue
            selected.append(r)
        if args.format=='json': print(json.dumps(selected,ensure_ascii=False,indent=2))
        else:
            print(f'{len(selected)} {args.index} records (not added to the main resource count)')
            for r in selected:
                if args.index=='norare': print(f"\n{r['source_id']}\n语言：{', '.join(r['language_scope'])}\n测量：{', '.join(r['search_tags'])}\n{r['upstream_description']}\n{r['original_url'] or r['source_metadata_url']}")
                else: print(f"\n{r['id']} {r['name']}\n待核对：{r['reason']}\n{r['source_url']}")
        return 0
    selected = []
    for r in catalog['resources']:
        if args.category and r['category'] != args.category:
            continue
        if args.access and r['access_mode'] != args.access:
            continue
        if args.platform and args.platform.lower() not in r['platforms']: continue
        if args.origin and r['data_origin']!=args.origin: continue
        if args.status and r['data_status']!=args.status: continue
        if args.evidence and r['verification']['evidence_type']!=args.evidence: continue
        if args.check_state and check_state(r)!=args.check_state: continue
        if args.lang and not any(code.casefold()==args.lang.casefold() or code.casefold().startswith(args.lang.casefold()+'-') for code in r['language_codes']):
            continue
        if args.tag and args.tag not in r['tags']:
            continue
        text = ' '.join([r['name'],r['language_scope'],r['data_type'],r['description'],r['limitations'],labels[r['category']],*r['tags']]).casefold()
        if args.keyword.casefold() not in text:
            continue
        selected.append(r)
    if args.format == 'json':
        print(json.dumps(selected,ensure_ascii=False,indent=2))
    else:
        print(f'{len(selected)} resources')
        for r in selected:
            print(f"\n{r['id']} {r['name']}\n{r['description']}\n文件核验：{CHECK_LABELS[check_state(r)]}\n获取：{r['access_notes']}\n{r['source_url']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
