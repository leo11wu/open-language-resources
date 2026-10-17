#!/usr/bin/env python3
"""Search the resource catalog without third-party dependencies."""
import argparse
import json
from pathlib import Path

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
    parser.add_argument('--format',choices=['text','json'],default='text')
    args = parser.parse_args()
    selected = []
    for r in catalog['resources']:
        if args.category and r['category'] != args.category:
            continue
        if args.access and r['access_mode'] != args.access:
            continue
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
            print(f"\n{r['id']} {r['name']}\n{r['description']}\n获取：{r['access_notes']}\n{r['source_url']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
