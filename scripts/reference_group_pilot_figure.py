#!/usr/bin/env python3
"""Plot only the published aggregate pilot JSON; no private data required."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args()
    x=json.loads(a.input.read_text());h=x['human'];m=x['models']
    fig,ax=plt.subplots(1,3,figsize=(15.8,5.0),gridspec_kw={'width_ratios':[1.3,1.1,1.1]})
    vals=[h['primary_corrected_squared_L2'],h['primary_half_replication']['between_minus_within_cross_half_inner_product'],h['demographic_sensitivity']['matched_distance']]
    cis=[h['primary_multiplier_interval95'],h['primary_half_replication']['multiplier_interval95'],h['demographic_sensitivity']['matched_interval95']]
    labels=['Equal-N primary\n1,968 cues; 20/group','Disjoint-half replication\n1,697 cues; 8/cell','Age-bin / gender matched\n1,153 cues; 20/group']
    for i,(v,ci) in enumerate(zip(vals,cis)):
        ax[0].errorbar(v,2-i,xerr=[[v-ci[0]],[ci[1]-v]],fmt='o',color='#21616d',capsize=4,ms=7,lw=2)
    ax[0].set_yticks([2,1,0],labels,fontsize=10);ax[0].set_ylim(-.6,2.6)
    ax[0].axvline(0,color='.6',ls='--',lw=1);ax[0].set_xlim(-.001,.043)
    ax[0].set_xlabel('Estimated squared distribution difference')
    ax[0].set_title('A  Human group signal',loc='left',fontweight='bold')
    shares=[r['US_share'] for r in m['references']]
    colors={'Mistral':'#d08b28','Llama3':'#24739b','Haiku':'#8c5a90'}
    for name,color in colors.items():
        ds=[];ov=[]
        for ref in m['references']:
            row=next(r for r in ref['models'] if r['name']==name);ds.append(row['distance']);ov.append(row['overlap'])
        ax[1].plot(shares,ds,'o-',label=name,color=color,lw=2,ms=5)
        ax[2].plot(shares,ov,'o-',label=name,color=color,lw=2,ms=5)
    ax[1].set_title('B  Distribution distance',loc='left',fontweight='bold')
    ax[1].set_ylabel('U-corrected squared L2 (lower is closer)');ax[1].set_ylim(0,.6)
    ax[2].set_title('C  Same-response probability',loc='left',fontweight='bold')
    ax[2].set_ylabel('Overlap probability (higher is more overlap)');ax[2].set_ylim(0,.16)
    for a1 in ax:
        a1.spines[['top','right']].set_visible(False);a1.grid(axis='y',alpha=.18)
    for a1 in ax[1:]:
        a1.set_xticks([0,.25,.5,.75,1],['UK','25%','50%','75%','US'])
        a1.set_xlabel('US share of the human reference (total N=20)')
    ax[2].legend(frameon=False,loc='center left',bbox_to_anchor=(1.01,.5))
    fig.subplots_adjust(left=.15,right=.91,bottom=.24,top=.85,wspace=.50)
    fig.suptitle('English reference-group pilot: stable aggregate human differences; unchanged model order within each metric',fontsize=13,y=.98)
    fig.text(.15,.06,'A: exploratory 95% participant + cue multiplier intervals; samples differ across rows.\nB-C: primary equal-N estimates on 1,952 common cues; all five reference mixtures retain the same model order within a metric.\nDifferent metrics rank the models differently. Archived model outputs; no new LLM generation.',fontsize=9,va='bottom',color='.25')
    a.output_prefix.parent.mkdir(parents=True,exist_ok=True)
    for ext in ['svg','png','pdf']:
        fig.savefig(str(a.output_prefix)+'.'+ext,dpi=180,facecolor='white')
    plt.close(fig)


if __name__=='__main__':main()
