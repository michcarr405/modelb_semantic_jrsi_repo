from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path('/mnt/data')
DATA=ROOT/'Figure_5_MP_PRIMARY_recovered_seed_blocks.csv'
OUT=ROOT

BLUE='#0072B2'; LIGHT_BLUE='#8FCDF0'; ORANGE='#E69F00'; GREEN='#009E73'; MAGENTA='#CC79A7'; GREY='#B5B5B5'; DARK_GREY='#555555'; LIGHT_GREY='#F2F2F2'; BLACK='#111111'

mpl.rcParams.update({
    'font.family':'DejaVu Sans','font.size':7.4,'axes.titlesize':7.4,'axes.labelsize':7.4,
    'xtick.labelsize':6.7,'ytick.labelsize':6.7,'legend.fontsize':6.6,'axes.linewidth':0.8,
    'xtick.major.width':0.65,'ytick.major.width':0.65,'xtick.major.size':3.2,'ytick.major.size':3.2,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'
})

# Frozen 64-new-continuation contrast summaries from the prospective high-continuation campaign.
CONTRASTS=pd.DataFrame([
    ('full_minus_neutral',1.9212,1.4057,2.4399,0.00060,True),
    ('full_minus_reduced',1.0234,0.4514,1.5973,0.00504,True),
    ('native_minus_affinity_reassigned',0.7246,0.3195,1.1845,0.00225,True),
    ('native_minus_topology_mismatch',0.3415,0.0441,0.6590,0.05010,False),
    ('alternative_native_minus_cross',0.8138,0.5160,1.1122,0.00090,True),
    ('stable_minus_unstable',0.8962,0.4665,1.2891,0.00225,True),
],columns=['contrast','mean_difference','bootstrap_95_lower','bootstrap_95_upper','q_value_bh_six_contrasts','contrast_passed'])


def clean_axis(ax,show_y=True):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    if not show_y: ax.tick_params(axis='y',labelleft=False)
    ax.set_ylim(-1.0,5.0); ax.set_yticks([-1,0,1,2,3,4,5])


def panel_label(ax,label,x=-0.20,y=1.06):
    ax.text(x,y,f'({label})',transform=ax.transAxes,fontsize=8.2,fontweight='bold',ha='left',va='bottom')


def two_group_panel(ax,left,right,left_label,right_label,title,show_y=False,title2=None):
    for a,b in zip(left,right): ax.plot([0,1],[a,b],color=GREY,lw=0.70,zorder=1)
    ax.scatter(np.zeros(len(left)),left,marker='s',s=17,facecolor=LIGHT_BLUE,edgecolor=BLUE,linewidth=0.65,zorder=3)
    ax.scatter(np.ones(len(right)),right,marker='o',s=18,facecolor='white',edgecolor=ORANGE,linewidth=0.75,zorder=3)
    ax.hlines(np.mean(left),-0.16,0.16,color=BLUE,lw=2.0,zorder=4)
    ax.hlines(np.mean(right),0.84,1.16,color=ORANGE,lw=2.0,zorder=4)
    ax.set_xlim(-0.35,1.35); ax.set_xticks([0,1],[left_label,right_label])
    ax.set_title(title,loc='left',pad=5.0 if title2 is None else 10.0)
    if title2 is not None:
        ax.text(0.0,1.015,title2,transform=ax.transAxes,ha='left',va='bottom',fontsize=6.3,color=DARK_GREY)
    clean_axis(ax,show_y=show_y)


def save_all(fig,stem):
    meta={'Title':'Figure 5: marginal-preserving causal-specificity controls','Author':'JRSI manuscript figure','Subject':'64-new-continuation marginal-preserving causal-specificity campaign'}
    fig.savefig(OUT/f'{stem}.pdf',metadata=meta,bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}.svg',bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}.eps',bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}_600DPI.png',dpi=600,bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}_600DPI.tiff',dpi=600,bbox_inches='tight',pad_inches=0.03)


def main():
    df=pd.read_csv(DATA).sort_values('seed_block').reset_index(drop=True)
    fig=plt.figure(figsize=(7.2,7.42))
    gs=fig.add_gridspec(3,3,height_ratios=[1.0,1.0,1.72],left=0.120,right=0.985,bottom=0.065,top=0.965,wspace=0.32,hspace=0.60)
    axes=[fig.add_subplot(gs[r,c]) for r in range(2) for c in range(3)]
    axa,axb,axc,axd,axe,axf=axes
    two_group_panel(axa,df.native_full,df.selection_neutral,'Full\nselection','Neutral','Neutral-selection control',show_y=True)
    two_group_panel(axb,df.native_full,df.selection_reduced,'Full\nselection','Reduced\nselection','Reduced-selection control')
    two_group_panel(axc,df.native_full,df.affinity_reassigned,'Native\nmapping','Affinity\nreassigned','Affinity-profile reassignment')
    two_group_panel(axd,df.native_full,df.topology_mismatch,'Native\ntopology','Topology\nmismatch','Topology mismatch',show_y=True,title2='borderline / inconclusive')
    two_group_panel(axe,df.alternative_native_mean,df.alternative_cross_mean,'Alternative\nnative','Cross-\nevaluated','Cross-topology evaluation')
    two_group_panel(axf,df.alternative_native_mean,df.temporally_unstable,'Stable\nfixed','Temporally\nunstable','Temporally unstable topology')
    axa.set_ylabel(r'$\Delta V_{\rm MP}$ (fitness units)'); axd.set_ylabel(r'$\Delta V_{\rm MP}$ (fitness units)')
    for ax,lab in zip(axes,list('abcdef')): panel_label(ax,lab)

    # panel g
    axg=fig.add_subplot(gs[2,0:2]); pos=axg.get_position(); axg.set_position([pos.x0+0.040,pos.y0,pos.width-0.040,pos.height])
    order=[
        ('full_minus_neutral','Full - neutral',BLACK),
        ('full_minus_reduced','Full - reduced',BLACK),
        ('native_minus_affinity_reassigned','Native - reassigned',BLACK),
        ('native_minus_topology_mismatch','Native - mismatch',BLACK),
        ('alternative_native_minus_cross','Alt. native - cross',BLACK),
        ('stable_minus_unstable','Stable - unstable',BLACK),
    ]
    cmap=CONTRASTS.set_index('contrast'); y=np.arange(len(order))[::-1]
    axg.axvline(0,color=GREY,lw=0.85,zorder=0)
    for (_,lab,col),yy in zip(order,y):
        r=cmap.loc[_]
        m=float(r.mean_difference); lo=float(r.bootstrap_95_lower); hi=float(r.bootstrap_95_upper); ok=bool(r.contrast_passed)
        axg.errorbar(m,yy,xerr=[[m-lo],[hi-m]],fmt='none',ecolor=col,elinewidth=1.0,capsize=2.4,capthick=0.9,zorder=2)
        axg.scatter([m],[yy],s=27 if ok else 31,marker='s',facecolor=col if ok else 'white',edgecolor=col,linewidth=0.6 if ok else 1.1,zorder=3)
    axg.set_yticks(y,[x[1] for x in order]); axg.set_xlabel(r'Paired mean difference in $\Delta V_{\rm MP}$ (fitness units)'); axg.set_title('Six prespecified paired contrasts',loc='left',pad=5.0)
    axg.spines['top'].set_visible(False); axg.spines['right'].set_visible(False); axg.set_xlim(-0.25,3.05); axg.set_xticks([0,0.5,1.0,1.5,2.0,2.5,3.0]); panel_label(axg,'g',x=-0.13,y=1.045)
    axg.text(0.985,1.045,'BH-adjusted $q$',transform=axg.transAxes,ha='right',va='bottom',fontsize=6.6)
    qx=2.98
    for yy,(key,_,_) in zip(y,order):
        r=cmap.loc[key]; q=float(r.q_value_bh_six_contrasts); ok=bool(r.contrast_passed)
        qtxt=f'{q:.5f}' + ('' if ok else '*')
        axg.text(qx,yy,qtxt,ha='right',va='center',fontsize=6.2)
    axg.text(0.985,1.005,r'open: $q\geq0.05$',transform=axg.transAxes,ha='right',va='bottom',fontsize=5.4,color=DARK_GREY)

    # panel h
    axh=fig.add_subplot(gs[2,2]); axh.set_axis_off(); panel_label(axh,'h',x=-0.18,y=1.04); axh.text(0.00,0.985,'Causal interpretation',ha='left',va='top',fontsize=7.4)
    def box(x,y0,w,h,text,edge,face):
        p=FancyBboxPatch((x,y0),w,h,boxstyle='round,pad=0.012,rounding_size=0.012',linewidth=1.0,edgecolor=edge,facecolor=face,transform=axh.transAxes,clip_on=False); axh.add_patch(p)
        axh.text(x+w/2,y0+h/2,text,transform=axh.transAxes,ha='center',va='center',fontsize=5.9,linespacing=1.0)
    box(0.05,0.73,0.90,0.15,'Built-in architecture\naffinity -> local state -> fitness',DARK_GREY,LIGHT_GREY)
    box(0.05,0.52,0.90,0.14,'Full selection + stable\nnative mapping',BLUE,'#CFE3F0')
    axh.add_patch(FancyArrowPatch((0.50,0.52),(0.50,0.45),transform=axh.transAxes,arrowstyle='-|>',mutation_scale=8,linewidth=1.0,color=BLACK))
    box(0.08,0.29,0.84,0.14,'Additional sequence-dependent\nrelational component beyond\none-site marginals',GREEN,'#D6EFE8')
    box(0.01,0.055,0.98,0.17,'Attenuated by weakened selection,\naffinity reassignment, cross-evaluation,\nor temporal instability;\nacute topology mismatch borderline',ORANGE,'#FFF7E8')

    save_all(fig,'Figure_5_MP_PRIMARY_v3_BLACK_FOREST')
    plt.close(fig)

    # numeric verification
    checks=[]
    pairs=[
        ('full_minus_neutral','native_full','selection_neutral'),('full_minus_reduced','native_full','selection_reduced'),
        ('native_minus_affinity_reassigned','native_full','affinity_reassigned'),('native_minus_topology_mismatch','native_full','topology_mismatch'),
        ('alternative_native_minus_cross','alternative_native_mean','alternative_cross_mean'),('stable_minus_unstable','alternative_native_mean','temporally_unstable')]
    for key,a,b in pairs:
        direct=float((df[a]-df[b]).mean()); frozen=float(cmap.loc[key,'mean_difference'])
        checks.append((key,direct,frozen,abs(direct-frozen)))
    pd.DataFrame(checks,columns=['contrast','direct_mean_from_recovered_vector_source','frozen_report_mean','absolute_difference']).to_csv(OUT/'FIGURE_5_MP_PRIMARY_v1_NUMERIC_QC.csv',index=False)

if __name__=='__main__': main()
