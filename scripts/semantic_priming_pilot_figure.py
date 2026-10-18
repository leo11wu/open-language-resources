#!/usr/bin/env python3
"""Render a standalone scientific pilot figure from exported aggregate results."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--results',type=Path,required=True)
    p.add_argument('--svg',type=Path,required=True)
    p.add_argument('--png',type=Path,required=True)
    args=p.parse_args();d=json.loads(args.results.read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'svg.hashsalt':'semantic-pilot-20261018'})
    fig,(a,b)=plt.subplots(1,2,figsize=(11.6,4.7),gridspec_kw={'width_ratios':[1,1.55]})
    stages=['Mapped candidates','SWOW, no repetition','Valid physical contrast','Frequency/form controls','Also source cosine']
    counts=[993,530,d['cohort_n'],d['controlled_models']['frequency_form_only']['n'],d['controlled_models']['primary_R1']['n']]
    y=np.arange(len(stages))
    a.barh(y,counts,height=.58,color=['#A5B6C6','#7299BD','#568CAD','#39759C','#245875'])
    a.invert_yaxis();a.set_yticks(y,stages);a.set_xlim(0,1120)
    a.set_xlabel('Candidate item pairs');a.set_title('A  Pilot coverage',loc='left',weight='bold',pad=14)
    for yy,n in zip(y,counts):a.text(n+15,yy,str(n),va='center',fontsize=11)
    names=['primary_R1','R123_sensitivity','backward_sensitivity']
    labels=[label+'\n(n='+str(d['controlled_models'][key]['n'])+')' for key,label in zip(names,['Forward R1','Forward R123','Backward R1'])]
    for yy,key in enumerate(names):
        r=d['controlled_models'][key];ci=r['participant_and_target_bootstrap_95_interval'];beta=r['beta_per_sd']
        b.errorbar(beta,yy,xerr=[[beta-ci['p2_5']],[ci['p97_5']-beta]],fmt='o',color='#245875',
                   capsize=5,markersize=7,elinewidth=1.8)
        b.text(ci['p97_5']+.003,yy,f"{beta:.3f}",va='center',fontsize=10)
    b.axvline(0,color='#777777',lw=1,ls='--',zorder=0)
    b.set_yticks(np.arange(3),labels);b.invert_yaxis();b.set_ylim(2.65,-.65)
    b.set_xlim(-.035,.082);b.set_xticks([-.02,0,.02,.04,.06,.08])
    b.set_xlabel('Change in priming language difference\nper 1 SD association predictor (z-RT units)')
    b.set_title('B  Adjusted associations and uncertainty',loc='left',weight='bold',pad=14)
    b.grid(axis='x',alpha=.15)
    fig.subplots_adjust(left=.17,right=.98,bottom=.24,top=.87,wspace=.66)
    fig.text(.03,.06,'Exploratory pilot. Panel B: 95% percentile intervals from 500 participant + target resamples.\nSWOW estimates are held fixed; intervals do not include all sources of measurement error.',fontsize=9,color='#444444')
    args.svg.parent.mkdir(parents=True,exist_ok=True);args.png.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.svg,metadata={'Date':None,'Description':'Pilot aggregate coverage and adjusted association estimates.'})
    fig.savefig(args.png,dpi=180)
    plt.close(fig)


if __name__=='__main__':main()
