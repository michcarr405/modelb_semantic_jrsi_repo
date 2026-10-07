from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT=Path('/mnt/data/JRSI_R2_SUPPLEMENT_PREFREEZE_S6_SPACING_2026-10-06')
DATA=ROOT/'source_tables'
FIG=ROOT/'figures'

# Match the source-faithful Supplement figure styling.
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

# Rebuild former S9/current S6 from the same frozen diagnostic source table,
# omitting only the immediate-fitness graphical panel. Those values remain
# reported numerically in Table S3(a).
d=pd.read_csv(DATA/'mp_marginal_diagnostics_summary.csv')
cond_order=['submitted_constant','m000_constant','m004_balanced_random_group','m015_affinity_rank_group','m024_contiguous_substring','m027_contiguous_substring','m029_contiguous_substring','m033_identity']
labels={
    'submitted_constant':'Pre-softmax affinity-\naveraging comparator',
    'm000_constant':'MP constant',
    'm004_balanced_random_group':'MP balanced-random\n16 groups',
    'm015_affinity_rank_group':'MP affinity-rank\n64 groups',
    'm024_contiguous_substring':'MP contiguous-substring\nstart 0, length 2',
    'm027_contiguous_substring':'MP contiguous-substring\nstart 3, length 2',
    'm029_contiguous_substring':'MP contiguous-substring\nstart 1, length 3',
    'm033_identity':'MP identity endpoint'
}
sel=d.set_index('condition').loc[cond_order]
y=np.arange(len(sel))

fig=plt.figure(figsize=(7.2,5.25))
gs=fig.add_gridspec(2,5,left=.09,right=.985,bottom=.09,top=.97,wspace=1.25,hspace=.48)
ax_a=fig.add_subplot(gs[0,0:2])
# Leave the centre GridSpec column empty so panel (b)'s long y-axis labels
# have dedicated space and cannot intrude into panel (a).
ax_b=fig.add_subplot(gs[0,3:5])
ax_c=fig.add_subplot(gs[1,1:4])

ax=ax_a
ax.barh(y,sel.mean_segment_tv,color='0.78',edgecolor='black',linewidth=.4)
ax.set_yticks(y,[labels[c] for c in cond_order]); ax.invert_yaxis()
ax.set_xlabel(r'Mean TV in expected $P(Z\mid S)$')
ax.set_title('One-site marginal distortion',loc='left')
panel(ax,'a',x=-.22); clean(ax); ax.set_xscale('log')

ax=ax_b
ax.barh(y,sel.mean_adjacency_tv,color='0.78',edgecolor='black',linewidth=.4)
ax.set_yticks(y,[labels[c] for c in cond_order]); ax.invert_yaxis()
ax.set_xlabel('Mean adjacency-category TV')
ax.set_title('Relational change',loc='left')
panel(ax,'b',x=-.22); clean(ax)

ax=ax_c
c=d.set_index('condition').loc[['native','submitted_constant','m000_constant']]
xx=np.arange(3); w=.23
ax.bar(xx-w,c.mean_promoting,width=w,label='Promoting',edgecolor='black',linewidth=.3)
ax.bar(xx,c.mean_reducing,width=w,label='Reducing',edgecolor='black',linewidth=.3)
ax.bar(xx+w,c.mean_neutral,width=w,label='Neutral',edgecolor='black',linewidth=.3)
ax.set_xticks(xx,['Native','Pre-softmax\ncomparator','MP constant'])
ax.set_ylabel('Expected adjacency fraction')
ax.set_title('Adjacency composition',loc='left')
panel(ax,'c',x=-.18); clean(ax); ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(1.02,1.0),borderaxespad=0)

for ext,kwargs in [('pdf',{}),('png',{'dpi':300})]:
    fig.savefig(FIG/f'Figure_S6_MP.{ext}',bbox_inches='tight',**kwargs)
plt.close(fig)
