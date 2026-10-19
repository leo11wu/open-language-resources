#!/usr/bin/env python3
"""Verify published aggregate/provenance consistency without licensed inputs."""
import hashlib
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=root/'data/reference-group-pilot-2026-10-19.json'
x=json.loads(p.read_text());h=x['human'];m=x['models']
for key,path in [('script_sha256','scripts/reference_group_pilot.py'),('plan_sha256','research/reference-group-pilot-plan-2026-10-19.md')]:
    assert x[key]==hashlib.sha256((root/path).read_bytes()).hexdigest(),path+' hash differs'
assert h['cues']==1968 and m['cues']==1952
assert h['people_per_group_per_cue']==m['human_per_reference_per_cue']==20
assert len(h['ten_fixed_participant_splits'])==10 and len(m['references'])==5
assert h['primary_half_replication']['participant_halves_disjoint']
assert x['verification']['human_Counter_recalculation']['matches_vectorized_result']
assert x['verification']['model_endpoint_Counter_recalculation']['matches_vectorized_scores']
assert x['verification']['human_full_deterministic_replay_equal']
sources={a['kind']:a for a in m['model_inputs']}
expected={'Mistral':'7a39663e156481c190328ce26a5f3961af053116','Llama3':'7139885abaa8516487bbc84cdfe3ebbfb9fbb3e7','Haiku':'522b0d52f3111fbe26f7f10e0e29b8896348e336'}
assert {k:v['git_blob_sha1'] for k,v in sources.items()}==expected
assert sum(a['all_jsonl_rows'] for a in sources.values())==3742979
for ref in m['references']:
    assert ref['human_total_per_cue']==20
    assert ref['point_distance_order']==[a['name'] for a in sorted(ref['models'],key=lambda a:a['distance'])]
    assert ref['point_overlap_order']==[a['name'] for a in sorted(ref['models'],key=lambda a:-a['overlap'])]
endpoints=[{a['name']:a for a in ref['models']} for ref in [m['references'][0],m['references'][-1]]]
for row in m['model_reference_shifts']:
    k=row['name'];delta=endpoints[1][k]['distance']-endpoints[0][k]['distance']
    assert math.isclose(delta,row['US_minus_UK_distance'],abs_tol=1e-12)
assert not m['any_interval_supported_distance_reversal']
assert not m['any_interval_supported_overlap_reversal']
def finite(obj):
    if isinstance(obj,float):assert math.isfinite(obj)
    elif isinstance(obj,dict):
        for v in obj.values():finite(v)
    elif isinstance(obj,list):
        for v in obj:finite(v)
finite(x)
print('Reference-group pilot valid: hashes, source counts, equal-N units, aggregate replay, endpoint scores and ranking statements agree.')
