from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
DATA=Path("."); FIG=Path(".")
# ---------- Figure S2: two nonredundant panels only ----------
BLUE='#0072B2'; LIGHT_BLUE='#8FCDF0'; GREEN='#009E73'; BLACK='#111111'; GREY='#B5B5B5'
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':7.4,'axes.titlesize':7.4,'axes.labelsize':7.4,'xtick.labelsize':6.6,'ytick.labelsize':6.6,'legend.fontsize':6.3,'axes.linewidth':0.8,'xtick.major.width':0.65,'ytick.major.width':0.65,'xtick.major.size':3,'ytick.major.size':3,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
def clean(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
def panel(ax,l,x=-.14,y=1.04):
    ax.text(x,y,f'({l})',transform=ax.transAxes,fontweight='bold',fontsize=8.2,ha='left',va='bottom')
inf=pd.read_csv(DATA/'core_mp_inference.csv').sort_values('inherit_prob')
rep=pd.read_csv(DATA/'core_mp_replicates.csv')
ps=inf.inherit_prob.to_numpy()
m=rep.groupby(['condition','inherit_prob'])['corrected_conditional_information'].mean().unstack(0)
info_diff=(m['selective']-m['control']).reindex(ps).to_numpy()
fig,axs=plt.subplots(1,2,figsize=(7.2,3.25),constrained_layout=True)
ax=axs[0]; ax.plot(ps,info_diff,marker='s',lw=1.4,color=GREEN,ms=4); ax.set_ylabel('Sequence-selective - agnostic (bits)'); ax.set_title('Corrected-information difference',loc='left'); panel(ax,'a'); clean(ax)
ax=axs[1]; ax.plot(ps,inf.mean_delta_mp,marker='s',lw=1.4,color=BLUE,ms=4); ax.fill_between(ps,inf.bootstrap_95_lower,inf.bootstrap_95_upper,color=LIGHT_BLUE,alpha=.45,lw=0); ax.axhline(0,color=GREY,lw=.7); ax.set_ylabel('Sequence-selective - agnostic\n(fitness units)'); ax.set_title('MP intervention-effect difference',loc='left'); panel(ax,'b'); clean(ax)
for ax in axs:
    ax.set_xlabel('Compositional-coupling probability, $p$')
fig.savefig(FIG/'Figure_S2_MP.pdf',bbox_inches='tight',metadata={'Title':'Supplementary Figure S2: complementary core inferential diagnostics','Author':'JRSI Round-2 programmatic build','Subject':'Source-data figure; no generative image editing'})
fig.savefig(FIG/'Figure_S2_MP.png',dpi=450,bbox_inches='tight')
plt.close(fig)

