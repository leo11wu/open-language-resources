#!/usr/bin/env python3
"""Participant split-half stability of local SWOW R1 estimates; aggregate export."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
from scipy import sparse
from semantic_priming_feasibility import ARCHIVES, INVALID, norm
from semantic_priming_pilot_analyze import reliability_summary


def halves(input_dir,f,language,rng):
    name,checksum,marker=ARCHIVES[language]
    archive=(input_dir/name).read_bytes()
    assert hashlib.sha256(archive).hexdigest()==checksum
    with ZipFile(io.BytesIO(archive)) as z:
        member=next(n for n in z.namelist() if marker in n)
        with z.open(member) as stream:
            d=pd.read_csv(stream,usecols=['participantID','cue','R1'],keep_default_na=False)
    for field in ['cue','R1']:d[field]=d[field].map(norm)
    query=pd.DataFrame([{'cue':r[language+'_'+condition],'target':r[language+'_target'],
                        'cell':2*i+j} for i,r in f.iterrows()
                        for j,condition in enumerate(['related','unrelated'])])
    d=d.loc[~d.R1.isin(INVALID) & d.cue.isin(query.cue)]
    merged=d.merge(query,on='cue',how='inner',validate='many_to_many')
    person,_=pd.factorize(merged.participantID,sort=True)
    cell=merged.cell.to_numpy(dtype=int)
    counts=sparse.coo_matrix((np.ones(len(merged)),(person,cell)),shape=(person.max()+1,2*len(f))).tocsr()
    hit=merged.R1.eq(merged.target).to_numpy()
    hits=sparse.coo_matrix((np.ones(hit.sum()),(person[hit],cell[hit])),shape=counts.shape).tocsr()
    assignment=rng.integers(0,2,size=(100,counts.shape[0]),dtype=np.int8)
    n1=np.asarray(assignment@counts);k1=np.asarray(assignment@hits)
    nt=np.asarray(counts.sum(axis=0));kt=np.asarray(hits.sum(axis=0))
    with np.errstate(invalid='ignore',divide='ignore'):
        first=k1/n1;second=(kt-k1)/(nt-n1)
    all_prob=(kt/nt).ravel();delta=all_prob[1::2]-all_prob[::2]
    assert np.max(abs(-delta-f[language+'_association'].to_numpy()))<1e-12
    first=first[:,::2]-first[:,1::2]
    second=second[:,::2]-second[:,1::2]
    return first,second,{'participant_ids_in_queried_cues':int(counts.shape[0]),
                        'query_cell_incidences':len(merged),'queried_cues':int(query.cue.nunique())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--private-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();f=pd.read_csv(args.private_dir/'features-private.csv')
    rng=np.random.default_rng(20261019)
    out={};parts={};scope={}
    for lang in ['en','zh']:
        a,b,scope[lang]=halves(args.input_dir,f,lang,rng)
        parts[lang]=(a,b);out[lang]=reliability_summary(a,b)
    out['crosslanguage_association_difference']=reliability_summary(parts['zh'][0]-parts['en'][0],parts['zh'][1]-parts['en'][1])
    report={'checked_on':'2026-10-18','stage':'exploratory_measurement_diagnostic',
            'cohort_n':len(f),'seed':20261019,'scope':scope,'reliability':out,
            'method':'100 random participant halves within each language; calculate related-minus-unrelated R1 probabilities per half',
            'limits':['Conditional on released balanced samples and observed word forms',
                      'Shared zero edges do not establish zero association in the population',
                      'No direct disattenuation or new model/predictor selection'],
            'individual_data_redistributed':False}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
