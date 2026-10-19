#!/usr/bin/env python3
"""Equal-N US/UK SWOW pilot and conditional LWOW comparison.

Private inputs/intermediates stay outside the repository. Only aggregate JSON
is written to --output. No training or new model generation is performed.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import platform
import unicodedata
import zipfile

import numpy as np
import pandas as pd

SEED=20261019
BOOT=500
INVALID_RAW={'','NA','#Missing','#Unknown'}
REGIONS=['United States','United Kingdom']
MODELS={'Mistral':'mistral_free_associations.jsonl','Llama3':'llama3-8b_free_associations.jsonl','Haiku':'haiku_free_associations.jsonl'}


def norm(x):
    return ' '.join(unicodedata.normalize('NFKC',str(x)).lower().split())


def missing(x):
    # Literal "nan" is an English word (e.g. a grandmother), not an automatic NA.
    return not isinstance(x,str) or x.strip() in INVALID_RAW


def digest(p):
    b=p.read_bytes()
    return {'file':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
            'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}


def summarize_draws(a):
    a=np.asarray(a,dtype=float)
    return {'mean':float(a.mean()),'median':float(np.median(a)),
            'p025':float(np.quantile(a,.025)),'p975':float(np.quantile(a,.975)),
            'min':float(a.min()),'max':float(a.max()),'fraction_above_zero':float((a>0).mean())}


def interval(a):
    return [float(x) for x in np.quantile(np.asarray(a),[.025,.975])]


def read_humans(path):
    with zipfile.ZipFile(path) as z:
        name='SWOW-EN.R100.20180827.csv'
        d=pd.read_csv(io.BytesIO(z.read(name)),keep_default_na=False,low_memory=False,
             usecols=['participantID','cue','R1','age','gender','country','nativeLanguage','created_at'])
    audit={'all_rows':len(d),'all_cues':int(d.cue.nunique()),'all_people':int(d.participantID.nunique()),'member':name}
    dup=d.loc[d.duplicated(['participantID','cue'],keep=False)]
    conflict=dup.groupby(['participantID','cue']).R1.nunique().gt(1)
    bad=set(conflict.loc[conflict].index)
    audit['duplicate_rows_beyond_first']=int(d.duplicated(['participantID','cue']).sum())
    audit['duplicate_R1_conflicting_keys']=len(bad)
    if bad:
        d=d.loc[[tuple(x) not in bad for x in d[['participantID','cue']].to_numpy()]]
    d=d.drop_duplicates(['participantID','cue'],keep='first').copy()
    d['cue_key']=d.cue.map(norm)
    collisions=set(d.groupby('cue_key').cue.nunique().loc[lambda x:x.gt(1)].index)
    audit['ambiguous_normalized_cue_keys']=len(collisions)
    d=d.loc[d.nativeLanguage.isin(REGIONS)&~d.cue_key.isin(collisions)].copy()
    d['response']=d.R1.map(norm)
    audit['regional_rows_before_missing_filter']=len(d)
    audit['regional_missing_R1_rows']=int(d.R1.map(missing).sum())
    d=d.loc[~d.R1.map(missing)].copy()
    d['kind']=d.nativeLanguage.map(dict(zip(REGIONS,['US','UK'])))
    d['age_bin']=pd.cut(pd.to_numeric(d.age),[16,30,45,60,101],right=False,labels=False).astype(int)
    d['stratum']=d.age_bin.astype(str)+'_'+d.gender.astype(str)
    d['year']=d.created_at.astype(str).str[:4]
    counts=d.groupby(['cue_key','kind']).participantID.nunique().unstack(fill_value=0)
    cues=sorted(counts.loc[counts[['US','UK']].ge(20).all(axis=1)].index)
    audit['qualified_cues']=len(cues)
    d['pid']=pd.factorize(d.participantID,sort=True)[0]
    audit['regional_people_valid_all_cues']=int(d.pid.nunique())
    d=d.loc[d.cue_key.isin(cues)].copy()
    audit['eligible_rows_by_group']=d.kind.value_counts().to_dict()
    audit['eligible_people_by_group']=d.groupby('kind').pid.nunique().to_dict()
    return d.reset_index(drop=True),cues,audit


def read_spelling(path):
    pairs=[x.split('\t') for x in path.read_text().splitlines() if x.strip()]
    assert all(len(x)==2 for x in pairs),'Unexpected spelling table structure'
    return {norm(a):norm(b) for a,b in pairs}


class Encoded:
    def __init__(self,frames,cues,spelling):
        self.cues=list(cues); self.C=len(cues)
        cm={x:i for i,x in enumerate(cues)}
        self.d=pd.concat(frames,ignore_index=True).copy()
        self.d=self.d.loc[self.d.cue_key.isin(cm)].reset_index(drop=True)
        self.d['ci']=self.d.cue_key.map(cm).astype(int)
        self.edge_cues={}
        for col,values in [('edge',self.d.response),('spell',self.d.response.map(lambda x:spelling.get(x,x)))]:
            keys=self.d.ci.astype(str)+'\x1f'+values
            codes,unique=pd.factorize(keys,sort=False)
            self.d[col]=codes
            self.edge_cues[col]=np.array([int(x.split('\x1f',1)[0]) for x in unique],dtype=int)
        self.pid=self.d.pid.fillna(-1).astype(int).to_numpy()
        self.npeople=max(1,int(self.pid.max())+1)
        self.ci=self.d.ci.to_numpy()
        self.edges={k:self.d[k].to_numpy() for k in self.edge_cues}

    def pool(self,kind,subset=None):
        mask=self.d.kind.eq(kind).to_numpy()
        if subset is not None:mask &= subset
        rows=np.flatnonzero(mask)
        by=[rows[self.ci[rows]==i] for i in range(self.C)]
        maxn=max(map(len,by)); p=np.full((self.C,maxn),-1,dtype=int)
        for i,r in enumerate(by):p[i,:len(r)]=r
        return p,np.array(list(map(len,by)))

    def sample(self,pool,n,rng):
        p,counts=pool
        assert counts.min()>=n
        priorities=rng.random(p.shape);priorities[p<0]=np.inf
        positions=np.argsort(priorities,axis=1)[:,:n]
        return np.take_along_axis(p,positions,axis=1)

    def stats(self,sample,col='edge',person_weights=None,record_weights=None):
        ee=self.edges[col][sample];ec=self.edge_cues[col]
        if person_weights is not None:w=person_weights[self.pid[sample]]
        elif record_weights is not None:w=record_weights
        else:w=np.ones(sample.shape)
        sw=w.sum(axis=1);sw2=np.square(w).sum(axis=1)
        counts=np.bincount(ee.ravel(),weights=w.ravel(),minlength=len(ec))
        p=counts/sw[ec]
        squares=np.bincount(ec,weights=counts*counts,minlength=self.C)
        u=(squares-sw2)/(sw*sw-sw2)
        return p,u

    def dot(self,p,q,col='edge'):
        return np.bincount(self.edge_cues[col],weights=p*q,minlength=self.C)

    def distance(self,s,t,col='edge'):
        return s[1]+t[1]-2*self.dot(s[0],t[0],col)

    def naive(self,p,q,col='edge'):
        return np.bincount(self.edge_cues[col],weights=(p-q)**2,minlength=self.C)


def human_boot(e,samples,metric,col='edge',seed=SEED+10000):
    rng=np.random.default_rng(seed);out=[]
    for _ in range(BOOT):
        wp=rng.exponential(size=e.npeople);wc=rng.exponential(size=e.C)
        st=[e.stats(s,col,person_weights=wp) for s in samples]
        v=metric(e,st,col)
        out.append(float(np.average(v,weights=wc)))
    return out


def distance_metric(e,s,col):return e.distance(s[0],s[1],col)


def replication_metric(e,s,col):
    # Order: US A, US B, UK A, UK B. Global participant halves are disjoint.
    return e.dot(s[0][0]-s[2][0],s[1][0]-s[3][0],col)


def describe_demography(e,samples):
    out={}
    for name,s in samples.items():
        d=e.d.iloc[s.ravel()];people=d.drop_duplicates('pid')
        def desc(x):return {'n':len(x),'mean_age':float(x.age.astype(float).mean()),
            'gender_proportions':{k:float(v) for k,v in x.gender.value_counts(normalize=True).items()},
            'year_proportions':{str(k):float(v) for k,v in x.year.value_counts(normalize=True).sort_index().items()}}
        out[name]={'sampled_response_rows':desc(d),'unique_people':desc(people),
                   'country_same_as_native_variety_fraction':float(d.country.eq(REGIONS[['US','UK'].index(name)]).mean())}
    return out


def half_samples(d,cues,spelling,seed):
    rng=np.random.default_rng(seed);side={}
    for k in ['US','UK']:
        pp=np.sort(d.loc[d.kind.eq(k),'pid'].unique());rng.shuffle(pp)
        side.update({int(p):int(i>=len(pp)//2) for i,p in enumerate(pp)})
    d=d.copy();d['side']=d.pid.map(side)
    n=d.groupby(['cue_key','kind','side']).size().unstack(['kind','side'],fill_value=0)
    cols=[('US',0),('US',1),('UK',0),('UK',1)]
    keep=sorted(n.loc[n.reindex(columns=cols,fill_value=0).ge(8).all(axis=1)].index)
    e=Encoded([d],keep,spelling)
    ss=[e.sample(e.pool(k,e.d.side.eq(side).to_numpy()),8,rng) for k,side in cols]
    assert not set(e.pid[ss[0]].ravel())&set(e.pid[ss[1]].ravel())
    assert not set(e.pid[ss[2]].ravel())&set(e.pid[ss[3]].ravel())
    return e,ss


def demographic_match(d,cues,spelling):
    rng=np.random.default_rng(SEED+80000);left=[];right=[];keep=[]
    for cue,g in d.groupby('cue_key',sort=True):
        pairs=[]
        for st,s in g.groupby('stratum',sort=True):
            a=s.index[s.kind.eq('US')].to_numpy();b=s.index[s.kind.eq('UK')].to_numpy()
            rng.shuffle(a);rng.shuffle(b);pairs.extend(zip(a[:min(len(a),len(b))],b[:min(len(a),len(b))]))
        if len(pairs)>=20:
            choose=rng.choice(len(pairs),20,replace=False)
            left.extend(pairs[i][0] for i in choose);right.extend(pairs[i][1] for i in choose);keep.append(cue)
    if not keep:return {'cues':0}
    x=d.loc[left+right].copy();e=Encoded([x],keep,spelling)
    s=[e.sample(e.pool(k),20,rng) for k in ['US','UK']]
    point=float(e.distance(*[e.stats(a) for a in s]).mean())
    matched_counts=e.d.groupby(['cue_key','kind','stratum']).size().unstack('kind',fill_value=0)
    assert (matched_counts.US==matched_counts.UK).all()
    ci=interval(human_boot(e,s,distance_metric,seed=SEED+80001))
    # Same words, fresh unstratified samples, to separate matching from selection.
    e0=Encoded([d],keep,spelling)
    s0=[e0.sample(e0.pool(k),20,rng) for k in ['US','UK']]
    p0=float(e0.distance(*[e0.stats(a) for a in s0]).mean())
    ci0=interval(human_boot(e0,s0,distance_metric,seed=SEED+80002))
    return {'cues':len(keep),'exact_age_bin_gender_counts_matched':True,'matched_distance':point,'matched_interval95':ci,
            'unmatched_same_cues_distance':p0,'unmatched_same_cues_interval95':ci0}


def run_humans(d,cues,spelling,private):
    e=Encoded([d],cues,spelling);rng=np.random.default_rng(SEED)
    pools={k:e.pool(k) for k in ['US','UK']}
    samples={k:e.sample(pools[k],20,rng) for k in pools}
    point={col:float(e.distance(e.stats(samples['US'],col),e.stats(samples['UK'],col),col).mean()) for col in ['edge','spell']}
    draws=[]
    for _ in range(BOOT):
        ss=[e.sample(pools[k],20,rng) for k in ['US','UK']]
        draws.append(float(e.distance(e.stats(ss[0]),e.stats(ss[1])).mean()))
    ci=interval(human_boot(e,list(samples.values()),distance_metric))
    cis=interval(human_boot(e,list(samples.values()),distance_metric,'spell'))
    h,hs=half_samples(d,cues,spelling,SEED)
    st=[h.stats(s) for s in hs]
    between=.5*(h.naive(st[0][0],st[3][0])+h.naive(st[2][0],st[1][0]))
    within=.5*(h.naive(st[0][0],st[1][0])+h.naive(st[2][0],st[3][0]))
    rep=replication_metric(h,st,'edge')
    assert np.allclose(between-within,rep,atol=1e-12)
    den=np.sqrt(np.square(st[0][0]-st[2][0]).sum()*np.square(st[1][0]-st[3][0]).sum())
    rpoint=float(rep.mean());rci=interval(human_boot(h,hs,replication_metric,seed=SEED+20000))
    sst=[h.stats(s,'spell') for s in hs];rs=float(replication_metric(h,sst,'spell').mean())
    rsci=interval(human_boot(h,hs,replication_metric,'spell',SEED+20000))
    splits=[]
    for seed in range(SEED,SEED+10):
        he,ss=half_samples(d,cues,spelling,seed)
        val=float(replication_metric(he,[he.stats(s) for s in ss],'edge').mean())
        splits.append({'seed':seed,'cues':he.C,'cross_half_excess':val})
    match=demographic_match(d,cues,spelling)
    gate=ci[0]>0 and rci[0]>0 and rsci[0]>0
    out={'cues':len(cues),'people_per_group_per_cue':20,'seed':SEED,'resampling_iterations':BOOT,
         'primary_corrected_squared_L2':point['edge'],'primary_multiplier_interval95':ci,
         'equal_N_allocation_distribution_not_confidence_interval':summarize_draws(draws),
         'spelling_normalized_distance':point['spell'],'spelling_normalized_interval95':cis,
         'primary_half_replication':{'cues':h.C,'people_per_cell':8,'participant_halves_disjoint':True,
             'between_group_empirical_squared_L2':float(between.mean()),'within_group_empirical_squared_L2':float(within.mean()),
             'between_minus_within_cross_half_inner_product':rpoint,'multiplier_interval95':rci,
             'contrast_vector_cosine':float(rep.sum()/den),'fraction_cues_with_positive_cross_half_product':float((rep>0).mean()),
             'spelling_normalized_cross_half_product':rs,'spelling_normalized_interval95':rsci},
         'ten_fixed_participant_splits':splits,'demographic_sensitivity':match,
         'demographics_of_primary_equal_N_sample':describe_demography(e,samples),
         'spelling_mapping_changed_fraction_by_group':{k:float(e.d.loc[e.d.kind.eq(k),'response'].map(lambda x:spelling.get(x,x)!=x).mean()) for k in ['US','UK']},
         'gate':{'pass':bool(gate),'rule':'primary 20-person distance, disjoint-half excess, and spelling-normalized disjoint-half excess each have multiplier lower bound > 0',
                 'scope':'aggregate signal; not reliable differences for every individual cue; not cultural causation'}}
    np.savez_compressed(private/'human-selected-rows.npz',US=samples['US'],UK=samples['UK'])
    return out


def read_models(root,cues):
    frames=[];audit=[];wanted=set(cues)
    for kind,filename in MODELS.items():
        path=root/filename;rows=[];all_rows=0;bad_schema=0;missing_count=0
        for line in path.open():
            item=json.loads(line);all_rows+=1
            cue=norm(item.get('cue',''))
            if cue not in wanted:continue
            response=item.get('response')
            if not isinstance(response,list) or not response or not isinstance(response[0],str):bad_schema+=1;continue
            if missing(response[0]):missing_count+=1;continue
            r=norm(response[0])
            rows.append((cue,r,kind,-1))
        f=pd.DataFrame(rows,columns=['cue_key','response','kind','pid']);frames.append(f)
        counts=f.groupby('cue_key').size()
        audit.append({**digest(path),'kind':kind,'all_jsonl_rows':all_rows,'valid_R1_rows_on_human_cues':len(f),
                      'missing_or_invalid_response0_rows':missing_count+bad_schema,'schema_or_empty_list_rows':bad_schema,
                      'covered_cues':len(counts),'minimum_valid_R1_per_covered_cue':int(counts.min()),
                      'cues_at_least_20':int(counts.ge(20).sum())})
    common=set(cues)
    for f in frames:common &= set(f.groupby('cue_key').size().loc[lambda n:n.ge(20)].index)
    return frames,sorted(common),audit


def model_scores(e,human,models,col='edge',wp=None,model_weights=None):
    scores=[];overlaps=[]
    mstats=[e.stats(models[k],col,record_weights=None if model_weights is None else model_weights[k]) for k in MODELS]
    for nUS in [0,5,10,15,20]:
        w=nUS/20
        us=e.stats(human['US'][:,:nUS],col,person_weights=wp) if nUS else None
        uk=e.stats(human['UK'][:,:20-nUS],col,person_weights=wp) if nUS<20 else None
        if us is None:p,u=uk
        elif uk is None:p,u=us
        else:
            p=w*us[0]+(1-w)*uk[0]
            u=w*w*us[1]+(1-w)**2*uk[1]+2*w*(1-w)*e.dot(us[0],uk[0],col)
        row=[];overlap=[]
        for q,qu in mstats:
            dot=e.dot(q,p,col);row.append(qu+u-2*dot);overlap.append(dot)
        scores.append(np.stack(row,axis=1));overlaps.append(np.stack(overlap,axis=1))
    return np.stack(scores,axis=1),np.stack(overlaps,axis=1)  # C x reference x model


def run_models(d,cues,spelling,root,private):
    frames,common,audit=read_models(root,cues)
    assert common,'No common eligible cues'
    e=Encoded([d]+frames,common,spelling);rng=np.random.default_rng(SEED+30000)
    pools={k:e.pool(k) for k in ['US','UK']+list(MODELS)}
    human={k:e.sample(pools[k],20,rng) for k in ['US','UK']}
    models={k:e.sample(pools[k],20,rng) for k in MODELS}
    e.d[['cue_key','response','kind','pid']].to_pickle(private/'joint-frame.pkl')
    np.savez_compressed(private/'joint-selected-rows.npz',**human,**models)
    point,ov=model_scores(e,human,models)
    point=point.mean(axis=0);ov=ov.mean(axis=0)
    model_concentration={k:float(e.stats(s)[1].mean()) for k,s in models.items()}
    vocabulary_size=int(e.d.response.nunique())
    human_concentration=point[:,0]-model_concentration['Mistral']+2*ov[:,0]
    al=[];alov=[]
    for _ in range(BOOT):
        h={k:e.sample(pools[k],20,rng) for k in ['US','UK']}
        m={k:e.sample(pools[k],20,rng) for k in MODELS}
        ds,os=model_scores(e,h,m);al.append(ds.mean(axis=0));alov.append(os.mean(axis=0))
    al=np.asarray(al);alov=np.asarray(alov)
    bb=[];bbo=[]
    for _ in range(BOOT):
        wp=rng.exponential(size=e.npeople);wc=rng.exponential(size=e.C)
        wm={k:rng.exponential(size=s.shape) for k,s in models.items()}
        ds,os=model_scores(e,human,models,wp=wp,model_weights=wm)
        bb.append(np.average(ds,axis=0,weights=wc));bbo.append(np.average(os,axis=0,weights=wc))
    bb=np.asarray(bb);bbo=np.asarray(bbo)
    sp,so=model_scores(e,human,models,'spell');sp=sp.mean(axis=0);so=so.mean(axis=0)
    names=list(MODELS);refs=[];pairs=[]
    for j,share in enumerate([0,.25,.5,.75,1]):
        refs.append({'US_share':share,'human_total_per_cue':20,
            'models':[{ 'name':n,'distance':float(point[j,k]),'distance_interval95':interval(bb[:,j,k]),
                        'overlap':float(ov[j,k]),'overlap_interval95':interval(bbo[:,j,k]),
                        'allocation_distance':summarize_draws(al[:,j,k]),
                        'probability_best_in_allocation_draws':float((np.argmin(al[:,j,:],axis=1)==k).mean()),
                        'probability_best_in_multiplier_draws':float((np.argmin(bb[:,j,:],axis=1)==k).mean()),
                        'spelling_normalized_distance':float(sp[j,k]),'spelling_normalized_overlap':float(so[j,k])} for k,n in enumerate(names)],
             'point_distance_order':[names[k] for k in np.argsort(point[j])],
             'point_overlap_order':[names[k] for k in np.argsort(-ov[j])],
             'human_U_concentration':float(human_concentration[j])})
        for k,a in enumerate(refs[-1]['models']):
            a['probability_best_overlap_in_allocation_draws']=float((np.argmax(alov[:,j,:],axis=1)==k).mean())
            a['probability_best_overlap_in_multiplier_draws']=float((np.argmax(bbo[:,j,:],axis=1)==k).mean())
    for a in range(len(names)):
        for b in range(a+1,len(names)):
            dif=point[:,a]-point[:,b];bd=bb[:,:,a]-bb[:,:,b]
            cis=[interval(bd[:,j]) for j in range(5)]
            opposite=dif[0]*dif[4]<0
            excludes=lambda x:x[0]>0 or x[1]<0
            pairs.append({'model_A':names[a],'model_B':names[b],
                'distance_A_minus_B_by_reference':[float(x) for x in dif],
                'paired_interval95_by_reference':cis,
                'US_minus_UK_change_in_pairwise_gap':float(dif[4]-dif[0]),
                'change_interval95':interval(bd[:,4]-bd[:,0]),
                'point_order_reversal':bool(opposite),
                'interval_supported_reversal':bool(opposite and excludes(cis[0]) and excludes(cis[4]))})
            od=ov[:,a]-ov[:,b];ob=bbo[:,:,a]-bbo[:,:,b]
            oci=[interval(ob[:,j]) for j in range(5)]
            pairs[-1].update({'overlap_A_minus_B_by_reference':[float(v) for v in od],
                'overlap_paired_interval95_by_reference':oci,
                'interval_supported_overlap_reversal':bool(od[0]*od[4]<0 and excludes(oci[0]) and excludes(oci[4]))})
    shifts=[]
    for k,n in enumerate(names):
        shifts.append({'name':n,'US_minus_UK_distance':float(point[4,k]-point[0,k]),
                       'paired_interval95':interval(bb[:,4,k]-bb[:,0,k]),
                       'US_minus_UK_overlap':float(ov[4,k]-ov[0,k]),
                       'overlap_change_interval95':interval(bbo[:,4,k]-bbo[:,0,k])})
    return {'cues':e.C,'human_cues_not_in_all_model_eligible_sets':len(cues)-e.C,
            'human_per_reference_per_cue':20,'stored_model_responses_per_model_per_cue':20,
            'model_inputs':audit,'references':refs,'pairwise_comparisons':pairs,'model_reference_shifts':shifts,
            'any_interval_supported_distance_reversal':any(x['interval_supported_reversal'] for x in pairs),
            'any_interval_supported_overlap_reversal':any(x['interval_supported_overlap_reversal'] for x in pairs),
            'posthoc_score_diagnostic':{'reason':'Primary distance and planned overlap give opposite model rankings; no primary metric was changed.',
                'model_U_concentration':model_concentration,'global_response_vocabulary_size':vocabulary_size,
                'uniform_global_vocabulary_overlap':1/vocabulary_size,
                'uniform_global_vocabulary_L2_by_reference':[float(v-1/vocabulary_size) for v in human_concentration],
                'scope':'Analytic data-dependent uniform baseline, added after primary results; descriptive score calibration, not a new confirmatory comparison.'},
            'limits':['Conditional on these archived model versions/prompts and first stored responses; not current-model rankings.',
                      'Model-record resampling does not quantify between-run or model-version uncertainty.',
                      'Exploratory pairwise intervals are not multiplicity-adjusted.',
                      'Only aggregate scores are published; no SWOW item distributions.']}


def self_test():
    # Known independent multinomial samples: unbiased within-collision terms.
    a=np.array([2,1]);b=np.array([1,2]);n=3
    u=lambda x:float((x*(x-1)).sum()/(n*(n-1)))
    direct=u(a)+u(b)-2*float((a*b).sum()/n**2)
    assert np.isclose(direct,-2/9)
    rng=np.random.default_rng(41)
    for _ in range(20):
        p=rng.dirichlet(np.ones(6),size=4);a,b,c,d=p
        between=((a-d)**2).sum()/2+((c-b)**2).sum()/2
        within=((a-b)**2).sum()/2+((c-d)**2).sum()/2
        assert np.isclose(between-within,((a-c)*(b-d)).sum())
    tiny=pd.DataFrame({'cue_key':['x']*8,'response':['a','a','b','b','a','c','c','c'],
        'kind':['US']*4+['UK']*4,'pid':list(range(8))})
    e=Encoded([tiny],['x'],{})
    ss=[np.array([[0,1,2,3]]),np.array([[4,5,6,7]])]
    v=e.distance(*[e.stats(x) for x in ss])[0]
    aa=Counter(tiny.response[:4]);bb=Counter(tiny.response[4:])
    manual=sum(z*(z-1) for z in aa.values())/12+sum(z*(z-1) for z in bb.values())/12-2*sum(aa[k]*bb[k] for k in aa)/16
    assert np.isclose(v,manual)
    vw=e.distance(*[e.stats(x,person_weights=np.ones(8)) for x in ss])[0]
    assert np.isclose(v,vw)
    return {'unbiased_U_toy_counts':True,'cross_half_identity':True,'vectorized_vs_counter':True,'unit_weights_agree':True}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=['human','models'],required=True)
    p.add_argument('--swow',type=Path,required=True)
    p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--private-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.private_dir.mkdir(parents=True,exist_ok=True)
    tests=self_test();d,cues,audit=read_humans(a.swow)
    spelling=read_spelling(a.source_dir/'EnglishCustomDict.txt')
    if a.stage=='human':
        result={'date':'2026-10-19','stage':'exploratory_equal_N_reference_group_pilot',
          'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},
          'input_audit':audit,'inputs':[digest(a.swow),digest(a.source_dir/'EnglishCustomDict.txt')],
          'self_tests':tests,'human':run_humans(d,cues,spelling,a.private_dir)}
        d.to_pickle(a.private_dir/'human-eligible.pkl')
        (a.private_dir/'human-cues.json').write_text(json.dumps(cues))
    else:
        result=json.loads(a.output.read_text())
        assert result['human']['gate']['pass'],'Human stability gate did not pass; no model effects evaluated'
        result['models']=run_models(d,cues,spelling,a.source_dir,a.private_dir)
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    plan=Path(__file__).resolve().parents[1]/'research/reference-group-pilot-plan-2026-10-19.md'
    result['plan_sha256']=hashlib.sha256(plan.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'stage':a.stage,'cues':len(cues),'human_gate':result['human']['gate'],
         'distance':result['human']['primary_corrected_squared_L2'],
         'interval':result['human']['primary_multiplier_interval95'],
         'half':result['human']['primary_half_replication'],
         'models_complete':'models' in result},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
