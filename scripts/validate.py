#!/usr/bin/env python3
"""Check catalog integrity; optionally apply the full JSON Schema validator."""
import datetime
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT/'data/resources.json').read_text(encoding='utf-8'))
    schema = json.loads((ROOT/'schema/resources.schema.json').read_text(encoding='utf-8'))
    resources = catalog['resources']
    categories = {c['id'] for c in catalog['categories']}
    expected_fields = set(schema['$defs']['resource']['required'])
    ids = [r['id'] for r in resources]
    errors = []
    def check(condition,message):
        if not condition:
            errors.append(message)
    check(catalog['resource_count']==len(resources),'resource_count does not match actual rows')
    check(len(ids)==len(set(ids)),'Duplicate stable IDs')
    check(len(categories)==len(catalog['categories']),'Duplicate category IDs')
    check(len({r['name'] for r in resources})==len(resources),'Duplicate resource names')
    check(len({r['source_url'] for r in resources})==len(resources),'Duplicate primary source URLs')
    datetime.date.fromisoformat(catalog['updated_on'])
    for r in resources:
        prefix = r['id']+': '
        check(set(r)==expected_fields,prefix+'Unexpected or missing fields')
        check(bool(re.fullmatch(r'R[0-9]{3,}',r['id'])),prefix+'Malformed ID')
        check(r['category'] in categories,prefix+'Unknown category')
        check(r['access_mode'] in catalog['access_modes'],prefix+'Unknown access mode')
        check(r['entry_type'] in schema['$defs']['resource']['properties']['entry_type']['enum'],prefix+'Unknown entry type')
        check(all(isinstance(r[key],str) and bool(r[key].strip()) for key in ['name','description','access_notes','license_note','limitations','language_scope','data_type']),prefix+'Empty descriptive field')
        for key in ['tags','language_codes']:
            check(bool(r[key]) and len(r[key])==len(set(r[key])),prefix+'Empty or duplicated '+key)
        for url in [r['source_url'],*r['additional_urls']]:
            parsed = urlparse(url)
            check(parsed.scheme in ['http','https'] and bool(parsed.netloc),prefix+'Invalid URL '+url)
        check(len(r['related_ids'])==len(set(r['related_ids'])),prefix+'Duplicate related IDs')
        check(all(x in ids and x!=r['id'] for x in r['related_ids']),prefix+'Missing or self-referencing related ID')
        date = datetime.date.fromisoformat(r['verification']['documentation_checked_on'])
        check(date<=datetime.date.fromisoformat(catalog['updated_on']),prefix+'Check date is later than catalog update')
        check(type(r['verification']['download_tested']) is bool,prefix+'Invalid download status')
        check(type(r['verification']['data_files_validated']) is bool,prefix+'Invalid validation status')
    lines = [json.loads(line) for line in (ROOT/'data/resources.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    check(lines==resources,'JSONL differs from canonical JSON')
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        full_schema = 'not run (optional jsonschema package unavailable; core integrity checks still applied)'
    else:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema,format_checker=FormatChecker())
        for error in validator.iter_errors(catalog):
            errors.append('JSON Schema: '+error.json_path+' '+error.message)
        full_schema = 'applied'
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        return 1
    print(f'Valid: {len(resources)} resources, {len(categories)} categories; JSON/JSONL agree. Full JSON Schema: {full_schema}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
