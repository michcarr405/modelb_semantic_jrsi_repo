from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE=Path('/mnt/data/fig7_work/JRSI_R2_MP_MIGRATION_DETAILED_SOURCE_TABLES_2026-10-03/migration_freeze_tables')
OUT=Path('/mnt/data')

# restrained palette consistent with Figures 6-7
BLACK='#111111'; GREY='#666666'; LIGHT_GREY='#B8B8B8'
GREEN='#009E73'; PURPLE='#CC79A7'; BLUE='#0072B2'; ORANGE='#E69F00'; LIGHT_BLUE='#56B4E9'
REGIME_COLORS={
    'R0_null':'#555555',
    'R1_syntactic_only':LIGHT_BLUE,
    'boundary_uncertain':ORANGE,
    'R2_viability_relevant':GREEN,
    'R3_strong_adaptation':PURPLE,
}
REGIME_MARKERS={
    'R0_null':'x',
    'R1_syntactic_only':'o',
    'boundary_uncertain':'D',
    'R2_viability_relevant':'s',
    'R3_strong_adaptation':'*',
}
REGIME_LABELS={
    'R0_null':'Null',
    'R1_syntactic_only':'Syntactic-only',
    'boundary_uncertain':'Boundary / uncertain',
    'R2_viability_relevant':'Viability-relevant',
    'R3_strong_adaptation':'Strong adaptation',
}

mpl.rcParams.update({
    'font.family':'sans-serif',
    'font.sans-serif':['Arial','Arimo','Helvetica','Nimbus Sans','DejaVu Sans'],
    'font.size':8.5,
    'axes.titlesize':9.6,
    'axes.labelsize':8.8,
    'xtick.labelsize':7.7,
    'ytick.labelsize':7.7,
    'legend.fontsize':7.2,
    'axes.linewidth':0.8,
    'pdf.fonttype':42,
    'ps.fonttype':42,
})

def clean_ax(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out',length=3.8,width=0.8)

def panel_label(ax,lab,x=-0.17,y=1.055):
    ax.text(x,y,f'({lab})',transform=ax.transAxes,fontweight='bold',fontsize=10.5,va='bottom')

def jitter(n,width=0.09):
    if n<=1: return np.zeros(n)
    return np.linspace(-width,width,n)

def save_all(fig,stem):
    fig.savefig(OUT/f'{stem}.pdf',bbox_inches='tight',pad_inches=0.04)
    fig.savefig(OUT/f'{stem}_600DPI.png',dpi=600,bbox_inches='tight',pad_inches=0.04)
    fig.savefig(OUT/f'{stem}_600DPI.tiff',dpi=600,bbox_inches='tight',pad_inches=0.04)

stage_c=pd.read_csv(BASE/'stage_c/stage_c_summary_n8_mp.csv')
stage_d_sum=pd.read_csv(BASE/'stage_d/stage_d_confirmation_summary.csv')
stage_d_rep=pd.read_csv(BASE/'stage_d/stage_d_replicate_summary.csv')
core_rep=pd.read_csv(BASE/'core/core_mp_replicates.csv')
core_inf=pd.read_csv(BASE/'core/core_mp_inference.csv')

fig=plt.figure(figsize=(7.45,6.25))
gs=fig.add_gridspec(2,2,left=0.105,right=0.985,top=0.91,bottom=0.12,wspace=0.32,hspace=0.50)
axa=fig.add_subplot(gs[0,0]); axb=fig.add_subplot(gs[0,1]); axc=fig.add_subplot(gs[1,0]); axd=fig.add_subplot(gs[1,1])
for ax in [axa,axb,axc,axd]: clean_ax(ax)

# Panels a/b: protocol sensitivity
x=np.arange(6)
xticks=['100','150','250','24','36','60']

def protocol_panel(ax, source_design_id, title, lab):
    d=stage_c[stage_c.source_design_id==source_design_id].copy()
    order=[f'C_g100_{source_design_id}',f'C_g150_{source_design_id}',f'C_g250_{source_design_id}',f'C_h24_{source_design_id}',f'C_h36_{source_design_id}',f'C_h60_{source_design_id}']
    d=d.set_index('design_id').loc[order].reset_index()
    for xi,r in d.iterrows():
        reg=r['regime']; col=REGIME_COLORS[reg]; mk=REGIME_MARKERS[reg]
        mfc='white' if reg in ['R0_null','R1_syntactic_only','boundary_uncertain','R2_viability_relevant'] else col
        ax.errorbar([xi],[r.delta_mp_mean],
                    yerr=[[r.delta_mp_mean-r.delta_mp_low],[r.delta_mp_high-r.delta_mp_mean]],
                    fmt=mk,ms=7.5,mfc=mfc,mec=col,mew=1.1,color=col,capsize=3,lw=1.1,zorder=3)
    ax.axhline(0,color=LIGHT_GREY,lw=0.8,zorder=0)
    ax.axhline(0.25,color=GREY,lw=0.9,ls='--',zorder=0)
    ax.axvline(2.5,color='#DDDDDD',lw=0.9,zorder=0)
    ax.set_xticks(x,xticks)
    ax.set_xlabel('Evolution duration                 Intervention horizon\nGenerations')
    ax.set_ylabel('MP future-fitness loss,\n' + r'$\Delta V_{\rm MP}$ (fitness units)')
    ax.set_title(title,loc='left',pad=5)
    panel_label(ax,lab)
    ax.set_ylim(-0.05,3.75)

protocol_panel(axa,'B2_default','Protocol sensitivity: default parameter setting','a')
protocol_panel(axb,'B2_stride7','Protocol sensitivity: sparse-window setting','b')

# Regime legend only for protocol panels
handles=[]
for k in ['R2_viability_relevant','R3_strong_adaptation']:
    handles.append(Line2D([0],[0],marker=REGIME_MARKERS[k],color='none',mec=REGIME_COLORS[k],
                          mfc='white' if k=='R2_viability_relevant' else REGIME_COLORS[k],ms=6.5,label=REGIME_LABELS[k]))
fig.legend(handles=handles,frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(0.50,0.985),columnspacing=1.3,handletextpad=0.45)

# Panel c: confirmations -- default core reference + three nondefault Stage D
# default p=1 core reference
core=core_rep[(core_rep.condition=='selective')&(core_rep.inherit_prob==1.0)].copy()
ci=core_inf[core_inf.inherit_prob==1.0].iloc[0]
labels=['Default\nparameter setting','Intermediate-coupling\nviability','Higher-reward\nstrong-adaptation','Sparse-window\nviability']
xs=np.arange(4)
# individual points
axc.scatter(np.full(len(core),0)+jitter(len(core),0.10),core.delta_mp,s=18,facecolors='white',edgecolors=LIGHT_GREY,lw=0.7,zorder=1)
axc.errorbar([0],[ci.mean_delta_mp],yerr=[[ci.mean_delta_mp-ci.bootstrap_95_lower],[ci.bootstrap_95_upper-ci.mean_delta_mp]],
             fmt='s',ms=7.5,mfc=BLACK,mec=BLACK,color=BLACK,capsize=3,lw=1.2,zorder=4)
# three nondefaults
for j,cid in enumerate(['D0','D1','D2'],start=1):
    g=stage_d_rep[stage_d_rep.confirm_id==cid].copy()
    r=stage_d_sum[stage_d_sum.confirm_id==cid].iloc[0]
    axc.scatter(np.full(len(g),j)+jitter(len(g),0.09),g.delta_mp,s=18,facecolors='white',edgecolors=LIGHT_GREY,lw=0.7,zorder=1)
    axc.errorbar([j],[r.delta_mp_mean],yerr=[[r.delta_mp_mean-r.delta_mp_low],[r.delta_mp_high-r.delta_mp_mean]],
                 fmt='s',ms=7.5,mfc=BLACK,mec=BLACK,color=BLACK,capsize=3,lw=1.2,zorder=4)
axc.axhline(0,color=LIGHT_GREY,lw=0.8)
axc.axhline(0.25,color=GREY,lw=0.9,ls='--')
axc.set_xticks(xs,labels,rotation=14,ha='right')
axc.set_ylabel('MP future-fitness loss,\n' + r'$\Delta V_{\rm MP}$ (fitness units)')
axc.set_title('Targeted MP confirmations',loc='left',pad=5)
panel_label(axc,'c')
axc.set_ylim(-0.08,5.15)

# Panel d: graded-frontier confirmation, 3 nondefault settings
labs_d=['Intermediate-coupling\nviability','Higher-reward\nstrong-adaptation','Sparse-window\nviability']
for j,cid in enumerate(['D0','D1','D2']):
    g=stage_d_rep[stage_d_rep.confirm_id==cid].copy()
    r=stage_d_sum[stage_d_sum.confirm_id==cid].iloc[0]
    axd.scatter(np.full(len(g),j)+jitter(len(g),0.08),g.spearman_info_recovery,s=20,facecolors='white',edgecolors=LIGHT_GREY,lw=0.7,zorder=1)
    axd.errorbar([j],[r.mean_within_population_spearman],
                 yerr=[[r.mean_within_population_spearman-r.spearman_low],[r.spearman_high-r.mean_within_population_spearman]],
                 fmt='s',ms=7.2,mfc=BLACK,mec=BLACK,color=BLACK,capsize=3,lw=1.2,zorder=4)
    # map-average rho as open diamond
    axd.scatter([j],[r.map_average_spearman],s=42,marker='D',facecolors='white',edgecolors=BLUE,lw=1.0,zorder=5)
axd.axhline(0,color=LIGHT_GREY,lw=0.8)
axd.set_xticks(np.arange(3),labs_d,rotation=12,ha='right')
axd.set_ylabel('Spearman ' + r'$\rho$' + '\n(retained information vs recovery)')
axd.set_title('Graded information-recovery confirmation',loc='left',pad=5)
panel_label(axd,'d')
axd.set_ylim(0.25,1.05)
axd.legend(handles=[
    Line2D([0],[0],marker='s',color=BLACK,mfc=BLACK,mec=BLACK,linestyle='none',ms=6,label='Mean within-population rho + 95% CI'),
    Line2D([0],[0],marker='D',color='none',mfc='white',mec=BLUE,linestyle='none',ms=5.5,label='Map-average rho')
],frameon=False,loc='lower right',fontsize=6.8,handletextpad=0.45)

# Numeric QC export
rows=[]
for source in ['B2_default','B2_stride7']:
    d=stage_c[stage_c.source_design_id==source]
    rows.append({'block':'protocol','setting':source,'n_variants':len(d),'min_delta_mp':d.delta_mp_mean.min(),'min_lower_ci':d.delta_mp_low.min(),'strong_count':int((d.regime=='R3_strong_adaptation').sum()),'viability_count':int((d.regime=='R2_viability_relevant').sum())})
rows.append({'block':'confirmation','setting':'default_core','n_variants':1,'min_delta_mp':ci.mean_delta_mp,'min_lower_ci':ci.bootstrap_95_lower,'strong_count':np.nan,'viability_count':np.nan})
for _,r in stage_d_sum.iterrows():
    rows.append({'block':'confirmation','setting':r.design_id,'n_variants':1,'min_delta_mp':r.delta_mp_mean,'min_lower_ci':r.delta_mp_low,'strong_count':np.nan,'viability_count':np.nan})
pd.DataFrame(rows).to_csv(OUT/'FIGURE_8_MP_PRIMARY_v2_NUMERIC_QC.csv',index=False)

save_all(fig,'Figure_8_MP_PRIMARY_v2_QC')
plt.close(fig)
