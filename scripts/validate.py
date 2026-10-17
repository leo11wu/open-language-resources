#!/usr/bin/env python3
"""Check catalog integrity; optionally apply the full JSON Schema validator."""
import datetime
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from verification import verification_queue

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
        check(r['data_status'] in schema['$defs']['resource']['properties']['data_status']['enum'],prefix+'Unknown resource status')
        check(r['data_origin'] in schema['$defs']['resource']['properties']['data_origin']['enum'],prefix+'Unknown data origin')
        check(len(r['platforms'])==len(set(r['platforms'])) and bool(r['platforms']),prefix+'Invalid platforms')
        check(len(r['osf_ids'])==len(set(r['osf_ids'])),prefix+'Duplicate OSF IDs')
        check(all(re.fullmatch('[a-z0-9]{5}',oid) for oid in r['osf_ids']),prefix+'Invalid OSF ID')
        check(('osf' in r['platforms'])==bool(r['osf_ids']),prefix+'OSF platform and node identifiers disagree')
        for url in r['verification']['evidence_urls']:
            parsed=urlparse(url)
            check(parsed.scheme in ['http','https'] and bool(parsed.netloc),prefix+'Invalid evidence URL')
    source=json.loads((ROOT/'data/source-indexes/norare.json').read_text())
    source_rows=source['records']
    source_ids=[r['source_id'] for r in source_rows]
    check(source['record_count']==len(source_rows),'Source index count mismatch')
    check(len(source_ids)==len(set(source_ids)),'Duplicate source identifiers')
    check(source['current_source_metadata_count']==sum('source_metadata_2026' in r['found_in'] for r in source_rows),'Current source count mismatch')
    check(source['cldf_snapshot_count']==sum('cldf_snapshot_2025' in r['found_in'] for r in source_rows),'CLDF snapshot count mismatch')
    for r in source_rows:
        check(r['evidence_type']=='source_catalog_metadata' and r['original_files_checked'] is False,'Source index overstates verification')
        check(all(rid in ids for rid in r['related_main_ids']),'Source index has invalid main ID')
        check(all(sid in source_ids for sid in r['possible_successor_source_ids']),'Source index has invalid successor ID')
    candidate=json.loads((ROOT/'data/discovery-candidates.json').read_text())
    check(candidate['candidate_count']==len(candidate['candidates']),'Candidate count mismatch')
    check(len({x['id'] for x in candidate['candidates']})==len(candidate['candidates']),'Duplicate candidate IDs')
    for row in candidate['candidates']:
        check(row['category'] in categories and row['counts_as_main_resource'] is False,'Candidate categorization invalid')
    queue=json.loads((ROOT/'data/verification-queue.json').read_text())
    check(queue==verification_queue(catalog,source,candidate),'Verification queue differs from recorded resource evidence')
    audit_paths=sorted((ROOT/'data').glob('candidate-audit-*.json'))
    for path in audit_paths:
        audit=json.loads(path.read_text())
        rows=audit['records']; promoted=[x for x in rows if x['outcome']=='promoted']; remaining=[x for x in rows if x['outcome']!='promoted']
        check(audit['reviewed_count']==len(rows),'Candidate audit total mismatch')
        check(audit['promoted_count']==len(promoted) and audit['remaining_count']==len(remaining),'Candidate audit outcome count mismatch')
        check(len({x['candidate_id'] for x in rows})==len(rows),'Duplicate candidate audit IDs')
        for row in promoted:
            check(row['main_resource_id'] in ids,'Promoted candidate main ID missing')
            check(row['verified_data_url'] and row['evidence_urls'],'Promoted candidate lacks data/evidence URL')
        if path==audit_paths[-1]:
            check({x['candidate_id'] for x in remaining}=={x['id'] for x in candidate['candidates']},'Latest audit and remaining candidate list disagree')
            check(not ({x['candidate_id'] for x in promoted}&{x['id'] for x in candidate['candidates']}),'Promoted candidates still counted as pending')
    # Public catalog metadata must not embed anonymous-review or access tokens.
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in ['.json','.jsonl','.md']:
            check(not re.search(r'(?:view_only|access_token|auth_token)=',path.read_text(),re.I),'Review/access token embedded in '+str(path.relative_to(ROOT)))
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
    print(f'Valid: {len(resources)} resources, {len(categories)} categories, {len(source_rows)} source records, {candidate["candidate_count"]} candidates; JSON/JSONL agree. Full JSON Schema: {full_schema}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
