#!/usr/bin/env python3
"""Bounded pilot: participant/item resampling and fixed target-group CV.

Inputs remain local. Only aggregate coefficients, scores and diagnostics are exported.
The resampling conditions on fixed SWOW estimates and lexical covariates.
"""
import argparse
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import pearsonr,spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error,r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

SEED=20261018
CONTROLS=[l+'_'+v for l in ['en','zh'] for v in [
    'target_zipf','cue_zipf_delta','target_length','cue_length_delta','overlap_delta']]
DISTRIBUTIONAL=['en_cosine_delta','zh_cosine_delta']


def corr(x,y):
    return {'n':len(x),'pearson_r':float(pearsonr(x,y).statistic),
            'spearman_rho':float(spearmanr(x,y).statistic)}


def interval(values):
    a=np.asarray(values);a=a[np.isfinite(a)]
    return {'repetitions':len(a),'mean':float(a.mean()),'median':float(np.median(a)),
            'p2_5':float(np.quantile(a,.025)),'p97_5':float(np.quantile(a,.975))}


def participant_samples(private,language,draws,rng):
    sums=sparse.load_npz(private/(language+'_sums.npz'))
    counts=sparse.load_npz(private/(language+'_counts.npz'))
    n=sums.shape[0]
    weights=rng.multinomial(n,np.full(n,1/n),size=draws)
    total_sums=np.asarray(sums.sum(axis=0)).ravel()
    total_counts=np.asarray(counts.sum(axis=0)).ravel()
    sampled_sums=np.asarray(weights@sums)
    sampled_counts=np.asarray(weights@counts)
    means=np.divide(sampled_sums,sampled_counts,out=np.full_like(sampled_sums,np.nan),where=sampled_counts>0)
    original=total_sums/total_counts
    return means[:,1::2]-means[:,::2],original[1::2]-original[::2],sums,counts


def reliability_split(sums,counts,draws,rng):
    all_sums=np.asarray(sums.sum(axis=0)).ravel()
    all_counts=np.asarray(counts.sum(axis=0)).ravel()
    halves=rng.integers(0,2,size=(draws,sums.shape[0]),dtype=np.int8)
    half_sums=np.asarray(halves@sums);half_counts=np.asarray(halves@counts)
    complement_counts=all_counts-half_counts
    first=np.divide(half_sums,half_counts,out=np.full_like(half_sums,np.nan),where=half_counts>0)
    other=np.divide(all_sums-half_sums,complement_counts,out=np.full_like(half_sums,np.nan),where=complement_counts>0)
    return first[:,1::2]-first[:,::2],other[:,1::2]-other[:,::2]


def reliability_summary(a,b):
    correlations=[]
    for x,y in zip(a,b):
        ok=np.isfinite(x)&np.isfinite(y)
        if ok.sum()>=3:correlations.append(float(pearsonr(x[ok],y[ok]).statistic))
    mean=float(np.mean(correlations))
    return {'splits':len(correlations),'mean_split_half_r':mean,
            'spearman_brown_of_mean':2*mean/(1+mean),
            'split_r_p2_5':float(np.quantile(correlations,.025)),
            'split_r_p97_5':float(np.quantile(correlations,.975))}


def equal_n_diagnostic(private,f,draws,rng):
    k=np.min(f[[l+'_'+c+'_n' for l in ['en','zh'] for c in ['related','unrelated']]].to_numpy(),axis=1).astype(int)
    cell_values={}
    for l in ['en','zh']:
        with np.load(private/(l+'_cell_trials.npz')) as z:
            order=np.argsort(z['cell'],kind='stable');cells=z['cell'][order];values=z['z'][order]
        split=np.searchsorted(cells,np.arange(2*len(f)+1))
        cell_values[l]=[values[split[i]:split[i+1]] for i in range(2*len(f))]
    correlations=[]
    for _ in range(draws):
        scores={}
        for l in ['en','zh']:
            means=np.array([rng.choice(v,k[i//2],replace=False).mean() for i,v in enumerate(cell_values[l])])
            scores[l]=means[1::2]-means[::2]
        correlations.append(float(pearsonr(f.association_difference,scores['zh']-scores['en']).statistic))
    return {'draws':draws,'rule':'per item, same minimum trial N across both conditions and languages; sampling without replacement',
            'per_condition_n_min':int(k.min()),'per_condition_n_median':float(np.median(k)),
            'correlation_distribution_not_population_CI':interval(correlations)}


def components(f):
    parents=list(range(len(f)))
    def find(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parents[b]=a
    seen={}
    for i,row in f.reset_index(drop=True).iterrows():
        for lang in ['en','zh']:
            for slot in ['target','related','unrelated']:
                word=(lang,row[lang+'_'+slot])
                if word in seen:union(i,seen[word])
                else:seen[word]=i
    sizes=pd.Series([find(i) for i in range(len(f))]).value_counts()
    return {'components':len(sizes),'largest_component':int(sizes.iloc[0]),
            'largest_component_proportion':float(sizes.iloc[0]/len(f)),
            'component_sizes_descending':sizes.to_list()}


def controlled_fit(f,mask,predictor,bootstrap_y,rng,controls):
    idx=np.flatnonzero(mask)
    sub=f.iloc[idx]
    fields=controls+[predictor]
    raw=sub[fields].to_numpy(dtype=float)
    scale=raw.std(axis=0);scale[scale==0]=1
    x=sm.add_constant((raw-raw.mean(axis=0))/scale,has_constant='add')
    y=sub.y_difference.to_numpy()
    fit=sm.OLS(y,x).fit(cov_type='cluster',cov_kwds={'groups':sub.zh_target.to_numpy()})
    target_col=len(fields)
    ci=fit.conf_int()[target_col]
    groups,codes=np.unique(sub.zh_target,return_inverse=True)
    estimates=[]
    for yy in bootstrap_y[:,idx]:
        w=rng.multinomial(len(groups),np.full(len(groups),1/len(groups)))[codes]
        weighted=x*np.sqrt(w[:,None]);outcome=yy*np.sqrt(w)
        estimates.append(float(np.linalg.lstsq(weighted,outcome,rcond=None)[0][target_col]))
    return {'n':len(sub),'chinese_target_groups':len(groups),'covariates':controls,
            'predictor':predictor,'effect_unit':'change in z-RT priming language difference per one SD predictor',
            'beta_per_sd':float(fit.params[target_col]),
            'target_cluster_robust_95CI':[float(ci[0]),float(ci[1])],
            'participant_and_target_bootstrap_95_interval':interval(estimates),
            'r_squared_in_sample':float(fit.rsquared),'predictor_sd_raw':float(scale[-1])}


def crossvalidation(f,mask,predictor,controls,purge_words=False,fold_seed=None):
    sub=f.loc[mask].reset_index(drop=True)
    y=sub.y_difference.to_numpy()
    predictions={name:np.zeros(len(sub)) for name in ['training_mean','baseline','plus_association']}
    fold_sizes=[]
    if fold_seed is None:
        folds=list(GroupKFold(5).split(sub,groups=sub.zh_target))
    else:
        unique=sub.zh_target.unique().copy()
        np.random.default_rng(fold_seed).shuffle(unique)
        assignment={g:i%5 for i,g in enumerate(unique)}
        group_fold=sub.zh_target.map(assignment).to_numpy()
        folds=[(np.flatnonzero(group_fold!=k),np.flatnonzero(group_fold==k)) for k in range(5)]
    for train,test in folds:
        overlaps={}
        purge=np.ones(len(train),dtype=bool)
        for lang in ['en','zh']:
            training_words=sub.loc[train,[lang+'_'+x for x in ['target','related','unrelated']]]
            test_words=set(sub.loc[test,[lang+'_'+x for x in ['target','related','unrelated']]].to_numpy().ravel())
            leak=training_words.isin(test_words).any(axis=1).to_numpy()
            purge &= ~leak
            overlaps[lang]=int(leak.sum())
        fit_train=train[purge] if purge_words else train
        assert len(fit_train)>len(controls)+2
        if purge_words:
            for lang in ['en','zh']:
                fields=[lang+'_'+x for x in ['target','related','unrelated']]
                assert not (set(sub.loc[fit_train,fields].to_numpy().ravel()) & set(sub.loc[test,fields].to_numpy().ravel()))
        predictions['training_mean'][test]=y[fit_train].mean()
        for name,features in [('baseline',controls),('plus_association',controls+[predictor])]:
            model=make_pipeline(StandardScaler(),Ridge(alpha=1.0))
            model.fit(sub.loc[fit_train,features],y[fit_train])
            predictions[name][test]=model.predict(sub.loc[test,features])
        fold_sizes.append({'train':len(train),'test':len(test),'training_rows_sharing_any_test_word':overlaps,
                           'training_rows_left_after_all_word_purge':int(purge.sum()),'actual_training_rows':len(fit_train)})
    scores={name:{'r_squared_oof':float(r2_score(y,pred)),
                  'rmse_oof':float(np.sqrt(mean_squared_error(y,pred)))} for name,pred in predictions.items()}
    return {'n':len(sub),'folds':5,'group':'Chinese target word','ridge_alpha':1.0,
            'fold_seed':fold_seed,
            'all_within_language_word_overlap_purged':purge_words,
            'scaling_fit_on_training_only':True,'scores':scores,
            'delta_R2_plus_minus_baseline':scores['plus_association']['r_squared_oof']-scores['baseline']['r_squared_oof'],
            'delta_RMSE_plus_minus_baseline':scores['plus_association']['rmse_oof']-scores['baseline']['rmse_oof'],
            'fold_diagnostics':fold_sizes,'claim_limit':('word-disjoint train/test within each language and fold; no claim of generalization to other tasks or languages' if purge_words else 'conditional target-group prediction; shared words across roles remain, not unseen-lexicon generalization')}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--bootstrap',type=int,default=500)
    args=p.parse_args()
    f=pd.read_csv(args.private_dir/'features-private.csv')
    assert len(f)==529, 'Expected strict cohort after the physical-event audit'
    rng=np.random.default_rng(SEED)
    samples={};split={};raw={};measurement={}
    for l in ['en','zh']:
        samples[l],raw[l],sums,counts=participant_samples(args.private_dir,l,args.bootstrap,rng)
        assert np.max(abs(raw[l]-f[l+'_priming'].to_numpy()))<1e-12
        split[l]=reliability_split(sums,counts,100,rng)
        measurement[l]=reliability_summary(*split[l])
    bootstrap_y=samples['zh']-samples['en']
    measurement['crosslanguage_difference']=reliability_summary(split['zh'][0]-split['en'][0],split['zh'][1]-split['en'][1])
    all_controls=CONTROLS+DISTRIBUTIONAL
    base_mask=f[all_controls+['association_difference']].notna().all(axis=1).to_numpy()
    no_duplicates=base_mask & ~f.zh_duplicate_target.to_numpy(dtype=bool)
    specifications=[('primary_R1',base_mask,'association_difference',all_controls),
                    ('frequency_form_only',f[CONTROLS+['association_difference']].notna().all(axis=1).to_numpy(),'association_difference',CONTROLS),
                    ('unique_translated_targets',no_duplicates,'association_difference',all_controls),
                    ('R123_sensitivity',base_mask,'association_R123_difference',all_controls),
                    ('backward_sensitivity',base_mask & f.backward_difference.notna().to_numpy(),'backward_difference',all_controls)]
    fits={};cv={}
    for name,mask,predictor,controls in specifications:
        fits[name]=controlled_fit(f,mask,predictor,bootstrap_y,rng,controls)
        if name in ['primary_R1','R123_sensitivity','backward_sensitivity']:
            cv[name]=crossvalidation(f,mask,predictor,controls)
    cv['primary_R1_word_purged']=crossvalidation(f,base_mask,'association_difference',all_controls,purge_words=True)
    partition=[]
    for seed in range(SEED,SEED+10):
        q=crossvalidation(f,base_mask,'association_difference',all_controls,purge_words=True,fold_seed=seed)
        partition.append({'seed':seed,'baseline_R2':q['scores']['baseline']['r_squared_oof'],
                          'plus_association_R2':q['scores']['plus_association']['r_squared_oof'],
                          'delta_R2':q['delta_R2_plus_minus_baseline']})
    report={'schema_version':'1.0.0','checked_on':'2026-10-18','stage':'exploratory_pilot_not_confirmatory',
            'seed':SEED,'decision':'adjust','cohort_n':len(f),
            'raw_primary':corr(f.association_difference,f.y_difference),
            'raw_rt_sensitivity':corr(f.association_difference,f.zh_priming_rt-f.en_priming_rt),
            'participant_bootstrap_raw_r':interval([pearsonr(f.association_difference,yy).statistic for yy in bootstrap_y]),
            'participant_split_reliability':measurement,'equal_n_diagnostic':equal_n_diagnostic(args.private_dir,f,50,rng),
            'controlled_models':fits,'target_group_cv':cv,
            'purged_partition_sensitivity':{'partitions':10,'selection':'all seeds 20261018 through 20261027; no best-seed selection',
               'positive_delta_R2_partitions':sum(q['delta_R2']>0 for q in partition),
               'delta_R2_partition_distribution_not_CI':interval([q['delta_R2'] for q in partition]),
               'plus_association_R2_partition_distribution_not_CI':interval([q['plus_association_R2'] for q in partition]),
               'all_partitions':partition},
            'lexical_dependency_full_cohort':components(f),
            'lexical_dependency_primary_cohort':components(f.loc[base_mask]),
            'uncertainty_scope':'Participant resampling within each language plus Chinese-target resampling; SWOW estimates/covariates fixed; shared cue vocabulary and SWOW sampling error not fully modeled',
            'semantic_gold_validation':False,'new_llm_experiment_run':False,
            'individual_data_redistributed':False,
            'limits':['No causal or bilingual dominance identification','Wordfreq snapshot/segmentation and source cosine completeness limit coverage',
                      'Only 60 material pairs assistant-screened; no independent human consensus','CV shares cue and cross-role vocabulary',
                      'Pilot protocol was written after the previous feasibility result was known']}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['decision','cohort_n','participant_split_reliability','controlled_models','target_group_cv','lexical_dependency_primary_cohort']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
