from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE=Path('/mnt/data/JRSI_R2_MP_FIGURE_MIGRATION')
df=pd.read_csv(BASE/'source_tables/mp_marginal_diagnostics_summary.csv')
# exclude native identity duplicate from map comparison but keep native for composition
order=['submitted_constant','m000_constant','m004_balanced_random_group','m015_affinity_rank_group','m024_contiguous_substring','m027_contiguous_substring','m029_contiguous_substring','m033_identity']
short={
'submitted_constant':'Submitted\nconstant',
'm000_constant':'MP\nconstant',
'm004_balanced_random_group':'MP balanced\n16 groups',
'm015_affinity_rank_group':'MP affinity\n64 groups',
'm024_contiguous_substring':'MP sub.\n0:2',
'm027_contiguous_substring':'MP sub.\n3:2',
'm029_contiguous_substring':'MP sub.\n1:3',
'm033_identity':'MP\nidentity',
}
sel=df.set_index('condition').loc[order].reset_index()
fig,axs=plt.subplots(2,2,figsize=(7.2,6.1))
# a P(Z|S) TV, symlog to show precision
ax=axs[0,0]
y=np.arange(len(sel))
vals=sel['mean_segment_tv'].to_numpy(); plotvals=np.where(vals==0,1e-16,vals)
ax.scatter(plotvals,y,s=35)
ax.set_xscale('log'); ax.set_xlim(5e-17,0.3)
ax.set_yticks(y); ax.set_yticklabels([short[x] for x in order],fontsize=7)
ax.invert_yaxis(); ax.set_xlabel('Mean TV in expected $P(Z\\mid S)$')
ax.set_title('(a) One-site marginal distortion',loc='left',fontsize=9)
ax.axvline(1e-12,ls='--',lw=.8)
# b adjacency TV
ax=axs[0,1]
ax.scatter(sel['mean_adjacency_tv'],y,s=35)
ax.set_yticks(y); ax.set_yticklabels([short[x] for x in order],fontsize=7)
ax.invert_yaxis(); ax.set_xlabel('Mean adjacency-category TV')
ax.set_title('(b) Relational change',loc='left',fontsize=9)
# c category composition
ax=axs[1,0]
comp=df.set_index('condition').loc[['native','submitted_constant','m000_constant']]
x=np.arange(3); w=.22
for j,(col,lab) in enumerate([('mean_promoting','Promoting'),('mean_reducing','Reducing'),('mean_neutral','Neutral')]):
    ax.bar(x+(j-1)*w,comp[col].to_numpy(),width=w,label=lab)
ax.set_xticks(x); ax.set_xticklabels(['Native','Submitted\nconstant','MP\nconstant'],fontsize=7)
ax.set_ylabel('Expected adjacency fraction'); ax.set_title('(c) Adjacency composition',loc='left',fontsize=9)
ax.legend(frameon=False,fontsize=7,ncol=1)
# d expected initial fitness
ax=axs[1,1]
ax.scatter(sel['mean_expected_initial_fitness'],y,s=35)
ax.axvline(float(df.loc[df.condition=='native','mean_expected_initial_fitness'].iloc[0]),ls=':',lw=.9)
ax.set_yticks(y); ax.set_yticklabels([short[x] for x in order],fontsize=7)
ax.invert_yaxis(); ax.set_xlabel('Expected initial mean fitness')
ax.set_title('(d) Immediate expected fitness',loc='left',fontsize=9)
for ax in axs.flat:
    ax.tick_params(labelsize=7)
fig.tight_layout(pad=1.2,w_pad=1.5,h_pad=1.4)
out=BASE/'figures/Figure_S9_MP'
for ext in ['pdf','svg','png','eps']:
    fig.savefig(str(out)+'.'+ext,dpi=300,bbox_inches='tight')
plt.close(fig)
from PIL import Image
im=Image.open(str(out)+'.png').convert('RGB'); im.save(str(out)+'.tiff',compression='tiff_lzw',dpi=(300,300))
print(str(out)+'.pdf')
