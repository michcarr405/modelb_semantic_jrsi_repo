from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('/mnt/data/JRSI_R2_SUPPLEMENT_PREFREEZE_S5_NO_TITLE_2026-10-06')
DATA=ROOT/'source_tables'
FIG=ROOT/'figures'

mpl.rcParams.update({
    'font.family':'DejaVu Sans','font.size':7.2,'axes.titlesize':7.6,
    'axes.labelsize':7.0,'xtick.labelsize':6.2,'ytick.labelsize':6.2,
    'legend.fontsize':6.0,'axes.linewidth':0.8,'pdf.fonttype':42,'ps.fonttype':42
})

def panel(ax,l,x=-.14,y=1.04):
    ax.text(x,y,f'({l})',transform=ax.transAxes,fontweight='bold',fontsize=8.2,ha='left',va='bottom')

def clean(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

d=pd.read_csv(DATA/'stage_c_summary_n8_mp.csv')
fig,axs=plt.subplots(3,2,figsize=(7.2,7.8),sharex='col')
mets=[
    ('corrected_information_mean','corrected_information_low','corrected_information_high',r'Corrected $I_{seq,corr}$ (bits)',.01),
    ('delta_mp_mean','delta_mp_low','delta_mp_high',r'$\Delta V_{MP}$ (fitness units)',.25),
    ('adaptive_gain_mean','adaptive_gain_low','adaptive_gain_high','Adaptive gain (fitness units)',1.0)
]
settings=[('B2_default','Default parameter setting'),('B2_stride7','Sparse-window setting')]
for col,(src,title) in enumerate(settings):
    g=d[d.source_design_id==src]
    vals=[]
    for gen in [100,150,250]:
        vals.append(g[g.design_id.str.startswith(f'C_g{gen}_')].iloc[0])
    for h in [24,36,60]:
        vals.append(g[g.design_id.str.startswith(f'C_h{h}_')].iloc[0])
    for row,(m,lo,hi,yl,thr) in enumerate(mets):
        ax=axs[row,col]
        xx=np.arange(6)
        mean=np.array([v[m] for v in vals],float)
        low=np.array([v[lo] for v in vals],float)
        high=np.array([v[hi] for v in vals],float)
        for x,mm,ll,hh in zip(xx,mean,low,high):
            ax.errorbar(x,mm,yerr=[[mm-ll],[hh-mm]],fmt='o',mfc='white',mec='black',ecolor='black',ms=4,capsize=2,lw=.7)
        ax.axhline(thr,color='0.35',ls='--',lw=.7)
        ax.axvline(2.5,color='0.75',lw=.6)
        ax.set_ylabel(yl)
        clean(ax)
        panel(ax,chr(97+row*2+col),x=-.16)
        if row==0:
            ax.set_title(title,fontweight='bold')
        if row==2:
            ax.set_xticks(xx,['100','150','250','24','36','60'])
            ax.set_xlabel('Evolution duration                    Intervention horizon\nGenerations')

# Deliberately no figure-level title; panel/column titles and caption provide the hierarchy.
fig.tight_layout(pad=1,w_pad=2,h_pad=1.5)
fig.savefig(FIG/'Figure_S5_MP.pdf',bbox_inches='tight')
fig.savefig(FIG/'Figure_S5_MP.png',dpi=300,bbox_inches='tight')
plt.close(fig)
