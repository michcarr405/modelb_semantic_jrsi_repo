from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
DATA=Path("."); FIG=Path("."); BLACK="#111111"
REG_COL={'R0_null':'#111111','R1_syntactic_only':'#0072B2','boundary_uncertain':'#E69F00','R2_viability_relevant':'#009E73','R3_strong_adaptation':'#CC79A7'}
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':7.4,'axes.titlesize':7.4,'axes.labelsize':7.4,'xtick.labelsize':6.6,'ytick.labelsize':6.6,'legend.fontsize':6.3,'axes.linewidth':0.8,'xtick.major.width':0.65,'ytick.major.width':0.65,'xtick.major.size':3,'ytick.major.size':3,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
def clean(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
def panel(ax,l,x=-.065,y=1.04):
    ax.text(x,y,f'({l})',transform=ax.transAxes,fontweight='bold',fontsize=8.2,ha='left',va='bottom')

d=pd.read_csv(DATA/'stage_ab_summary_n8_mp.csv').sort_values(['stage','design_id']).reset_index(drop=True)
x=np.arange(1,len(d)+1); stages=d.stage.to_numpy()
fig,axs=plt.subplots(3,1,figsize=(7.2,7.75),sharex=True)
mets=[('corrected_information_mean','corrected_information_low','corrected_information_high','Corrected $I_{seq,corr}$ (bits)',.01),('delta_mp_mean','delta_mp_low','delta_mp_high',r'$\Delta V_{\rm MP}$ (fitness units)',.25),('adaptive_gain_mean','adaptive_gain_low','adaptive_gain_high','Adaptive gain (fitness units)',1.0)]
bounds=[]
for st in ['A','B1','B2']:
    ix=np.where(stages==st)[0]; bounds.append((ix.min()+1,ix.max()+1,st))
faces={'A':'#EAF2F8','B1':'#FFF4E5','B2':'#EAF7F3'}
full_labels={
    'A':'Stage A\nfocused mechanistic\nscreen (1-32)',
    'B1':'Stage B1\nbroad multivariable\nscreen (33-48)',
    'B2':'Stage B2\nstructural-family\nscreen (49-65)',
}
for k,(mcol,lo,hi,yl,thr) in enumerate(mets):
    ax=axs[k]
    for a,b,st in bounds:
        ax.axvspan(a-.5,b+.5,color=faces[st],zorder=0)
    ax.axvline(32.5,color='0.55',lw=.6,ls=':'); ax.axvline(48.5,color='0.55',lw=.6,ls=':')
    for i,row in d.iterrows():
        c=REG_COL[row.regime]
        ax.errorbar(x[i],row[mcol],yerr=[[row[mcol]-row[lo]],[row[hi]-row[mcol]]],fmt='o',ms=2.8,mfc=c,mec=c,ecolor=c,lw=.5,capsize=1)
    ax.axhline(thr,color=BLACK,ls='--',lw=.7)
    ax.set_ylabel(yl)
    ax.set_title(['Corrected sequence-specific information','Marginal-preserving intervention effect','Selection-driven fitness gain'][k],loc='left')
    panel(ax,chr(97+k))
    clean(ax)
    if k==0:
        trans=ax.get_xaxis_transform()
        ax.text(16.5,.935,full_labels['A'],ha='center',va='top',fontsize=5.5,fontweight='bold',transform=trans,linespacing=1.05)
        ax.text(40.5,.935,full_labels['B1'],ha='center',va='top',fontsize=5.5,fontweight='bold',transform=trans,linespacing=1.05)
        ax.text(57,.935,full_labels['B2'],ha='center',va='top',fontsize=5.5,fontweight='bold',transform=trans,linespacing=1.05)
axs[-1].set_xlabel('Prespecified setting index (ordered by stage; $n=8$ per setting)')
axs[-1].set_xlim(.5,len(d)+.5)
axs[-1].set_xticks([1,8,16,24,32,40,48,57,65])
fig.tight_layout(pad=1,h_pad=1.25)
fig.savefig(FIG/'Figure_S4_MP.pdf',bbox_inches='tight',metadata={'Title':'Supplementary Figure S4: Stage A/B1/B2 domain-map metrics','Author':'JRSI Round-2 programmatic build','Subject':'Source-data figure; no generative image editing'})
fig.savefig(FIG/'Figure_S4_MP.png',dpi=450,bbox_inches='tight')
plt.close(fig)

