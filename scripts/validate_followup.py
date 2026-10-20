"""Check count, scope, role and provenance invariants for follow-up snapshots."""
import hashlib
import re


def validate(audit, catalog, candidates, root, check):
    rows=audit['records'];s=audit['summary']
    main=[r for r in rows if r['kind']=='main']
    pending=[r for r in rows if r['kind']=='candidate_source']
    files=[f for r in rows for f in r['selected_file_checks']]
    check(len(rows)==len({r['resource_id'] for r in rows})==65,'Follow-up fixed queue count differs')
    check(len(main)==s['main_reviewed']==audit['target']['existing_main']==60,'Follow-up main count differs')
    check(len(pending)==s['candidate_sources_reviewed']==5,'Follow-up candidate source count differs')
    check({r['resource_id'] for r in rows}==set(audit['target']['resource_ids']),'Follow-up queue IDs differ')
    check(s['complete_downloads']==sum(f['download_status']=='complete' for f in files),'Follow-up download count differs')
    check(s['readable_complete_files']==sum(f['readable_complete'] for f in files),'Follow-up read count differs')
    check(s['partial_file_reads']==sum(len(r['partial_file_checks']) for r in rows),'Follow-up prefix count differs')
    check(sum(s[k] for k in ['main_with_readable_data','main_with_partial_data_only',
        'main_with_only_supporting_reads','main_without_readable_selected_files'])==60,'Follow-up disjoint main states differ')
    check(audit['entrypoint_checks_complete'] and not audit['all_resources_fully_validated'],'Follow-up overstates full validation')
    check(not audit['individual_data_redistributed'],'Follow-up redistributes observations')
    current={r['id']:r for r in catalog['resources']}
    for row in rows:
        data=[f for f in row['selected_file_checks'] if f['readable_complete'] and
              f['file_role'] in ['empirical_or_norm_data','corpus_derived_data']]
        check(row['readable_data_file_count']==len(data),'Follow-up data-role count differs: '+row['resource_id'])
        for f in row['selected_file_checks']:
            if not f['readable_complete']:continue
            check(f['download_status']=='complete' and bool(re.fullmatch('[0-9a-f]{64}',f.get('sha256',''))),
                  'Readable file lacks complete download or hash')
            check(f.get('listed_size_matches') is not False and f.get('published_sha256_matches') is not False
                and f.get('github_blob_matches') is not False,'Readable file source checksum differs')
            check(f['parse']['parse_status'] not in ['failed','download_only_no_supported_parser'],
                  'Unparsed follow-up file counted as read')
        for f in row['partial_file_checks']:
            check(f['complete_parent_file_downloaded'] is False,'Partial read masquerades as complete download')
            check(f['parse']['parse_status']=='parsed_bounded_table_prefix','Partial read lacks parsed prefix')
            check(bool(re.fullmatch('[0-9a-f]{64}',f.get('sha256',''))),'Prefix lacks local-byte checksum')
        if row['kind']=='main':check(row['resource_id'] in current,'Follow-up main resource missing')
    for rid in ['R086','R107','R176','R140']:
        row=next(r for r in rows if r['resource_id']==rid)
        check(row['readable_data_file_count']==0,'Materials counted as primary observations: '+rid)
    added=next(r for r in rows if r['resource_id']=='C012')
    check(added.get('promoted_to')=='R181' and added['readable_data_file_count']==4,'C012 promotion lacks four real-data tables')
    check(s['newly_promoted_candidates']==1,'Follow-up promotion count differs')
    if audit['catalog_version']==catalog['catalog_version']:
        check(s['remaining_candidates']==candidates['candidate_count']==11,'Follow-up remaining candidates differ')
        check('C012' not in {r['id'] for r in candidates['candidates']} and 'R181' in current,'Promoted candidate mapping invalid')
    for code in audit['processing_code']:
        check(hashlib.sha256((root/code['path']).read_bytes()).hexdigest()==code['sha256'],
              'Follow-up code hash differs: '+code['path'])
