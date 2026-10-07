from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
DATA=Path("."); FIG=Path(".")
GREY="#B3B3B3"; GREEN="#009E73"; ORANGE="#E69F00"
def save(fig,path):
 fig.savefig(path,bbox_inches="tight"); plt.close(fig)
# ---- Reduced Figure S3: only alternative-topology disaggregation ----
def paired(ax, left, right, left_label, right_label, title, panel):
    y1=left.to_numpy(float); y2=right.to_numpy(float)
    for a,b in zip(y1,y2): ax.plot([0,1],[a,b],color=GREY,lw=0.9,zorder=1)
    ax.scatter(np.zeros(len(y1)),y1,s=28,marker='s',facecolors='none',edgecolors=GREEN,zorder=2)
    ax.scatter(np.ones(len(y2)),y2,s=28,marker='o',facecolors='none',edgecolors=ORANGE,zorder=2)
    ax.set_xlim(-0.3,1.3); ax.set_xticks([0,1],[left_label,right_label])
    ax.set_ylim(-1,5); ax.spines[['top','right']].set_visible(False)
    ax.set_title(title,loc='left',fontsize=10); ax.text(-0.18,1.04,f'({panel})',transform=ax.transAxes,fontweight='bold',fontsize=11)
    ax.tick_params(axis='x',labelsize=8); ax.tick_params(axis='y',labelsize=8)

def build_s3():
    d=pd.read_csv(DATA/'causal_specificity_seed_blocks_64new.csv').sort_values('seed_block')
    fig,axs=plt.subplots(1,3,figsize=(11,4.25),sharey=True,constrained_layout=True)
    paired(axs[0],d['alternative_a_native'],d['alternative_a_cross_b'],'Topology A\nnative','A evaluated\nunder B','Alternative topology A','a')
    paired(axs[1],d['alternative_b_native'],d['alternative_b_cross_a'],'Topology B\nnative','B evaluated\nunder A','Alternative topology B','b')
    paired(axs[2],d['alternative_native_mean'],d['alternative_cross_mean'],'Alternative\nnative mean','Cross-evaluated\nmean','Alternative-topology aggregate','c')
    axs[0].set_ylabel('$\\Delta V_{\\rm MP}$ (fitness units)')
    save(fig,FIG/'Figure_S3_MP.pdf')


build_s3()
