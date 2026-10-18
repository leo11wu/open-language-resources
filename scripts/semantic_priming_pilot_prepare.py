#!/usr/bin/env python3
"""Prepare private pilot inputs; export source/QC aggregates only.

The private directory contains restricted SWOW-derived values and anonymized
SPAML trial arrays. It must not be copied to the resource repository.
"""
import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
from scipy import sparse
from wordfreq import zipf_frequency, tokenize

from semantic_priming_feasibility import materials, load_norms, score, norm

SEED = 20261018
EXPECTED_SIZES = {'en':147208934, 'zh':21569059}


def file_record(path):
    data = path.read_bytes()
    return {'filename':path.name, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}


def read_trials(root, language, matched):
    path = root / (language + '_prime_trials.csv')
    assert path.stat().st_size == EXPECTED_SIZES[language], 'Incomplete trial release'
    d = pd.read_csv(path, keep_default_na=False)
    original_rows = len(d)
    z = pd.to_numeric(d.target_Z_RT, errors='coerce')
    mask = ((d.keep_target == 'keep') & (d.keep_participant == 'keep') &
            d.target_correct.astype(str).str.lower().eq('true') & z.notna() &
            d.type.isin(['related','unrelated']))
    kept = d.loc[mask, ['unique_trial','observation','word_combo','cue_word','target_word','type','target_duration']].copy()
    kept['z'] = z.loc[mask].astype(float)
    kept['rt'] = pd.to_numeric(kept.pop('target_duration'), errors='coerce')
    labels_per_event = d.groupby('unique_trial').type.nunique()
    ambiguous_ids = set(labels_per_event[labels_per_event>1].index)
    ambiguous_pairs = sorted(d.loc[d.unique_trial.isin(ambiguous_ids),'word_combo'].unique().tolist())
    physical_keys = d.loc[d.type.isin(['related','unrelated'])].groupby(['word_combo','type']).agg(cue_forms=('cue_word','nunique'),target_forms=('target_word','nunique'))
    key_collisions = int(((physical_keys.cue_forms>1)|(physical_keys.target_forms>1)).sum())
    assert key_collisions == 0
    summaries = kept.groupby(['word_combo','type']).agg(mean=('z','mean'), n=('z','size'),
             variance=('z','var'), mean_rt=('rt','mean'), se=('z',lambda x:x.std(ddof=1)/np.sqrt(len(x))))
    published = pd.read_csv(root / (language + '_prime_summary.csv')).set_index('target_word_unique')
    matches, mismatches, missing = [], [], []
    for row in matched:
        for condition in ['related','unrelated']:
            key = (row['word_combo_'+condition],condition)
            label = row['target_word_unique']
            if key not in summaries.index:
                missing.append({'key':label,'condition':condition});continue
            actual = summaries.loc[key]
            mean_error = abs(actual['mean'] - published.loc[label,'avgZ_RT_'+condition])
            n_error = int(actual['n']) - int(published.loc[label,'target_sample_keep_'+condition])
            row_check = {'key':label,'condition':condition,'mean_error':float(mean_error),'n_error':n_error}
            if mean_error > 1e-9 or n_error:
                mismatches.append(row_check)
            else:
                matches.append(row_check)
    qc = {**file_record(path), 'all_rows':original_rows, 'columns':len(d.columns),
          'all_rows_duplicate_unique_trial_extra':int(d.unique_trial.duplicated().sum()),
          'retained_duplicate_unique_trial_extra':int(kept.unique_trial.duplicated().sum()),
          'ambiguous_event_ids':len(ambiguous_ids),'ambiguous_physical_pairs':ambiguous_pairs,
          'concatenated_key_collisions':key_collisions,
          'retained_trials':len(kept), 'retained_participants':int(kept.observation.nunique()),
          'matched_cells':len(matches), 'mismatched_cells':mismatches, 'missing_cells':missing,
          'maximum_absolute_mean_error':max([x['mean_error'] for x in matches+mismatches],default=0)}
    return kept, summaries, published, qc


def overlap(cue, target):
    a,b = set(cue),set(target)
    return len(a & b) / len(a | b) if a | b else 0.0


def frequency(word, language):
    tokens = tokenize(word, language)
    value = zipf_frequency(word,language,wordlist='large',minimum=0.0)
    return (float(value) if value > 0 and len(tokens)==1 else np.nan), len(tokens)


def source_cosines(root, language):
    d = pd.read_csv(root/(language+'_stimuli.csv'),keep_default_na=False)
    d = d.loc[d.type.isin(['related','unrelated']) & d.cue_type.eq('word') & d.target_type.eq('word')]
    d[language+'_cosine'] = pd.to_numeric(d[language+'_cosine'],errors='coerce')
    fields = [language+'_cue',language+'_target','type']
    duplicate_counts = d.groupby(fields)[language+'_cosine'].nunique()
    assert duplicate_counts.max() <= 1, 'Inconsistent cosine for same physical stimulus'
    return d.drop_duplicates(fields).set_index(fields)[language+'_cosine'].to_dict()


def build_sparse(kept, features, language, private):
    cells = {}
    for j,r in features.iterrows():
        for offset,condition in enumerate(['related','unrelated']):
            combo = r[language+'_'+condition] + r[language+'_target']
            cells.setdefault((combo,condition),[]).append(2*j+offset)
    keys = pd.Series(list(zip(kept.word_combo,kept.type)),index=kept.index)
    chosen = kept.loc[keys.isin(cells)].copy()
    chosen['cols'] = keys.loc[chosen.index].map(cells)
    chosen = chosen.explode('cols')
    persons, _ = pd.factorize(chosen.observation,sort=True)
    cols = chosen.cols.to_numpy(dtype=int)
    values = chosen.z.to_numpy(dtype=float)
    matrix = sparse.coo_matrix((values,(persons,cols)), shape=(persons.max()+1,2*len(features))).tocsr()
    counts = sparse.coo_matrix((np.ones(len(cols)),(persons,cols)), shape=matrix.shape).tocsr()
    sparse.save_npz(private/(language+'_sums.npz'),matrix)
    sparse.save_npz(private/(language+'_counts.npz'),counts)
    np.savez_compressed(private/(language+'_cell_trials.npz'),cell=cols,z=values)
    physical = chosen.drop_duplicates('unique_trial')
    assert chosen.unique_trial.nunique() == chosen.index.nunique(), 'Duplicated physical event in eligible cohort'
    return {'participants_in_cohort':int(matrix.shape[0]),'cohort_trial_incidences':len(chosen),
            'physical_trials':len(physical),'duplicate_unique_trial_extra':int(chosen.unique_trial.duplicated().sum()),'cells':int(matrix.shape[1])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--stimuli-dir',type=Path,required=True)
    p.add_argument('--private-dir',type=Path,required=True)
    p.add_argument('--qc-output',type=Path,required=True)
    args = p.parse_args()
    args.private_dir.mkdir(parents=True,exist_ok=True)
    items = {lang:materials(args.input_dir,lang)[0] for lang in ['en','zh']}
    matched = {lang:json.loads((args.input_dir/('spaml-matched-'+lang+'.json')).read_text()) for lang in items}
    norms = {lang:load_norms(args.input_dir,lang,items[lang]) for lang in items}
    trial_results = {lang:read_trials(args.input_dir,lang,matched[lang]) for lang in items}
    cosines = {lang:source_cosines(args.stimuli_dir,lang) for lang in items}
    links = json.loads((args.input_dir/'spaml-author-links-one-to-one.json').read_text())['links']
    target_counts = {lang:Counter(v['target'] for v in items[lang].values()) for lang in items}
    frequency_cache = {}
    rows = []
    for link in links:
        record = {'translation_id':int(link['translation_id'])}
        valid = True
        for lang in items:
            key = link[lang+'_key']; item = items[lang][key]
            a = score(norms[lang],item,'R1')
            if a is None or item['target'] in [item['related'],item['unrelated']]:
                valid=False;break
            record[lang+'_key']=key
            record.update({lang+'_'+k:v for k,v in item.items()})
            for measure,response_set,reverse in [('association','R1',False),('association_R123','R123',False),('backward','R1',True)]:
                record[lang+'_'+measure]=score(norms[lang],item,response_set,reverse=reverse)
            stats = trial_results[lang][1]
            for condition in ['related','unrelated']:
                physical=(item[condition]+item['target'],condition)
                observed=stats.loc[physical]
                record[lang+'_'+condition+'_n']=int(observed['n'])
                record[lang+'_'+condition+'_var']=float(observed['variance'])
                record[lang+'_'+condition+'_mean']=float(observed['mean'])
                record[lang+'_'+condition+'_rt']=float(observed['mean_rt'])
                record[lang+'_'+condition+'_cosine']=float(cosines[lang].get((item[condition],item['target'],condition),np.nan))
            record[lang+'_priming']=record[lang+'_unrelated_mean']-record[lang+'_related_mean']
            record[lang+'_priming_rt']=record[lang+'_unrelated_rt']-record[lang+'_related_rt']
            record[lang+'_priming_se_naive']=np.sqrt(sum(record[lang+'_'+c+'_var']/record[lang+'_'+c+'_n'] for c in ['related','unrelated']))
            record[lang+'_published_priming']=float(trial_results[lang][2].loc[key,'avgZ_prime'])
            record[lang+'_duplicate_target']=target_counts[lang][item['target']]>1
            for field in ['target','related','unrelated']:
                token=(item[field],lang)
                if token not in frequency_cache:frequency_cache[token]=frequency(*token)
                record[lang+'_'+field+'_zipf'],record[lang+'_'+field+'_token_count']=frequency_cache[token]
            record[lang+'_cue_zipf_delta']=record[lang+'_related_zipf']-record[lang+'_unrelated_zipf']
            record[lang+'_target_length']=len(item['target'])
            record[lang+'_cue_length_delta']=len(item['related'])-len(item['unrelated'])
            record[lang+'_overlap_delta']=overlap(item['related'],item['target'])-overlap(item['unrelated'],item['target'])
            record[lang+'_cosine_delta']=record[lang+'_related_cosine']-record[lang+'_unrelated_cosine']
        if valid:rows.append(record)
    candidates = pd.DataFrame(rows).reset_index(drop=True)
    assert len(candidates)==530, 'Prior cohort not reproduced'
    sample = candidates.iloc[np.sort(np.random.default_rng(SEED).choice(len(candidates),60,replace=False))]
    removed = []
    eligible = np.ones(len(candidates),dtype=bool)
    for i,row in candidates.iterrows():
        for lang in items:
            combos = {row[lang+'_'+c]+row[lang+'_target'] for c in ['related','unrelated']}
            ambiguous = bool(combos & set(trial_results[lang][3]['ambiguous_physical_pairs']))
            degenerate = row[lang+'_related']==row[lang+'_unrelated']
            if ambiguous or degenerate:
                eligible[i]=False
                removed.append({'translation_id':int(row.translation_id),'language':lang,
                                'ambiguous_trial_labels':ambiguous,'same_prime_both_conditions':degenerate})
    f = candidates.loc[eligible].reset_index(drop=True)
    f['y_difference']=f.zh_priming-f.en_priming
    f['association_difference']=f.zh_association-f.en_association
    f['association_R123_difference']=f.zh_association_R123-f.en_association_R123
    f['backward_difference']=f.zh_backward-f.en_backward
    f.to_csv(args.private_dir/'features-private.csv',index=False)
    sample[['translation_id','en_key','zh_key','en_related','en_target','en_unrelated',
            'zh_related','zh_target','zh_unrelated']].to_csv(args.private_dir/'semantic-sample.csv',index=False)
    all_ids = pd.read_excel(args.input_dir/'spaml_translation.xlsx')
    unresolved=all_ids.loc[~all_ids.id.isin([r['translation_id'] for r in links]),
             ['id','en_cue','en_target','zh_cue_Melinna','zh_target_Melinna']]
    unresolved.to_csv(args.private_dir/'unresolved-seven.csv',index=False)
    matrices={lang:build_sparse(trial_results[lang][0],f,lang,args.private_dir) for lang in items}
    metadata={'checked_on':'2026-10-18','stage':'exploratory_pilot_preparation',
              'candidate_cohort_n':len(candidates),'cohort_n':len(f),'excluded_after_event_audit':removed,
              'random_semantic_sample_n':len(sample),'semantic_sampling_frame_n':len(candidates),'seed':SEED,
              'trial_replay':{lang:trial_results[lang][3] for lang in items},'cohort_matrices':matrices,
              'replication_max_error':{lang:float(abs(f[lang+'_priming']-f[lang+'_published_priming']).max()) for lang in items},
              'duplicated_target_candidates':{lang:int(f[lang+'_duplicate_target'].sum()) for lang in items},
              'missing_author_cosine_delta':{lang:int(f[lang+'_cosine_delta'].isna().sum()) for lang in items},
              'frequency_screen':{lang:{field:{'missing_or_multitoken':int(f[lang+'_'+field+'_zipf'].isna().sum()),
                          'multitoken':int((f[lang+'_'+field+'_token_count']!=1).sum())} for field in ['target','related','unrelated']} for lang in items},
              'input_hashes':[file_record(args.input_dir/n) for n in ['spaml-author-links-one-to-one.json','spaml-matched-en.json','spaml-matched-zh.json','en_prime_summary.csv','zh_prime_summary.csv']],
              'private_individual_data_published':False,'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'wordfreq':'3.1.1'}}
    args.qc_output.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(metadata,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
