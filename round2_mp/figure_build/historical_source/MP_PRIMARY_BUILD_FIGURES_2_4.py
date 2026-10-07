from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT=Path('/mnt/data/r2work/mp_primary_figures_2_4')
FREEZE=ROOT/'JRSI_R2_MP_MIGRATION_SCIENTIFIC_FREEZE_2026-10-02'
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
REP=ROOT/'rep0_frontier_reconstruction'

# Source-faithful palette, consistent with the previous JRSI build.
BLUE='#0072B2'; ORANGE='#E69F00'; GREEN='#009E73'; VERMILION='#D55E00'; PURPLE='#CC79A7'
LIGHT_BLUE='#56B4E9'; GREY='#666666'; LIGHT_GREY='#B8B8B8'; BLACK='#111111'; WHITE='#FFFFFF'

mpl.rcParams.update({
    'font.family':'sans-serif','font.sans-serif':['Arial','Arimo','Helvetica','Nimbus Sans','DejaVu Sans'],
    'font.size':9.4,'axes.titlesize':10.5,'axes.labelsize':9.4,'xtick.labelsize':8.3,'ytick.labelsize':8.3,
    'legend.fontsize':8.0,'axes.linewidth':0.8,'pdf.fonttype':42,'ps.fonttype':42,
})

def clean_ax(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out',length=4,width=0.8)

def panel_label(ax,label,x=-0.13,y=1.035):
    ax.text(x,y,f'({label})',transform=ax.transAxes,fontweight='bold',fontsize=11,va='bottom')

def jitter(n,width=0.009):
    return np.linspace(-width,width,n) if n>1 else np.zeros(n)

def save_all(fig,stem):
    for ext in ['pdf','svg','eps','png','tiff']:
        kw={'bbox_inches':'tight','pad_inches':0.03}
        if ext in ('png','tiff'): kw['dpi']=600
        fig.savefig(OUT/f'{stem}.{ext}',**kw)

def box(ax,xy,w,h,text,fc='#F7F7F7',ec='#777777',fontsize=8.2,bold=False):
    x,y=xy
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.015',fc=fc,ec=ec,lw=1.0)
    ax.add_patch(p); ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fontsize,fontweight='bold' if bold else 'normal')
    return p

def arrow(ax,start,end,text=None):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=10,lw=1.0,color='#555555'))
    if text:
        mx=(start[0]+end[0])/2; my=(start[1]+end[1])/2
        ax.text(mx,my+0.04,text,ha='center',va='bottom',fontsize=7.5,color=GREY)

def tiny_profile(ax,x,y,vals,label=None):
    bw=0.025; gap=0.010; base=y
    ax.plot([x-0.005,x+4*bw+3*gap+0.005],[base,base],color=GREY,lw=0.7)
    for i,v in enumerate(vals):
        ax.add_patch(Rectangle((x+i*(bw+gap),base),bw,0.12*v,facecolor='#EEEEEE',edgecolor='#555555',lw=0.6))
    if label: ax.text(x-0.012,base+0.055,label,ha='right',va='center',fontsize=7.4)

def figure2():
    fig,axs=plt.subplots(2,2,figsize=(7.35,5.55))
    for ax in axs.ravel():
        ax.set_axis_off(); ax.set_xlim(0,1); ax.set_ylim(0,1)
    a,b,c,d=axs.ravel()
    # (a) native kernel
    panel_label(a,'a',x=-0.08,y=1.00); a.set_title('Native sequence-dependent kernel',loc='left',pad=5)
    a.text(0.03,0.88,r'Motif identity $m$ and segment $s$ define',fontsize=8.5)
    a.text(0.03,0.81,r'$P_0(z\mid m,s)$',fontsize=14,fontweight='bold')
    tiny_profile(a,0.10,0.42,[0.20,0.70,0.95,0.35],'m₁')
    tiny_profile(a,0.10,0.24,[0.75,0.35,0.25,0.90],'m₂')
    tiny_profile(a,0.53,0.42,[0.45,0.90,0.55,0.20],'m₃')
    tiny_profile(a,0.53,0.24,[0.90,0.20,0.65,0.45],'m₄')
    a.text(0.03,0.09,'Profiles are probabilities after softmax;\nlocal-state classes are categorical labels.',fontsize=7.8,color=GREY)
    # (b) grouping
    panel_label(b,'b',x=-0.08,y=1.00); b.set_title('Grouping map',loc='left',pad=5)
    b.text(0.04,0.87,r'$g(m)=q$ assigns motif identities to grouping classes.',fontsize=8.5)
    box(b,(0.06,0.58),0.22,0.16,'m₁',fontsize=8.5); box(b,(0.06,0.33),0.22,0.16,'m₂',fontsize=8.5)
    box(b,(0.06,0.08),0.22,0.16,'m₃',fontsize=8.5); box(b,(0.39,0.08),0.22,0.16,'m₄',fontsize=8.5)
    box(b,(0.70,0.50),0.22,0.20,'group q = 1\nm₁, m₂',fc='#E8F1F8',ec=BLUE,bold=True)
    box(b,(0.70,0.14),0.22,0.20,'group q = 2\nm₃, m₄',fc='#FFF1D7',ec=ORANGE,bold=True)
    arrow(b,(0.28,0.66),(0.70,0.60)); arrow(b,(0.28,0.41),(0.70,0.58)); arrow(b,(0.28,0.16),(0.70,0.24)); arrow(b,(0.61,0.16),(0.70,0.23))
    b.text(0.04,0.015,'Sequence identities are unchanged; grouping controls which motif distinctions are retained.',fontsize=7.4,color=GREY)
    # (c) aggregation
    panel_label(c,'c',x=-0.08,y=1.00); c.set_title('Probability-space aggregation',loc='left',pad=5)
    c.text(0.03,0.84,r'Within each group $q$ and segment $s$, current branch frequencies',fontsize=8.0)
    c.text(0.03,0.77,r'$w_t(m\mid q,s)$ weight the native kernels:',fontsize=8.0)
    c.text(0.03,0.62,r'$Q_t(z\mid q,s)=\sum_{m:g(m)=q} w_t(m\mid q,s)P_0(z\mid m,s)$',fontsize=12.0,fontweight='bold')
    box(c,(0.04,0.31),0.24,0.15,'Current branch\ncomposition',fontsize=8.0)
    box(c,(0.38,0.31),0.24,0.15,'Native kernels\n$P_0$',fontsize=8.0)
    box(c,(0.72,0.31),0.24,0.15,'Group kernel\n$Q_t$',fc='#E5F3EF',ec=GREEN,fontsize=8.0,bold=True)
    arrow(c,(0.28,0.385),(0.38,0.385),r'$w_t$'); arrow(c,(0.62,0.385),(0.72,0.385))
    c.text(0.03,0.10,'Weights are recomputed from the current intervention-branch population,\nnot fixed from the baseline population.',fontsize=7.8,color=GREY)
    # (d) intervention/preservation
    panel_label(d,'d',x=-0.08,y=1.00); d.set_title('Intervention and preservation identity',loc='left',pad=5)
    box(d,(0.04,0.71),0.31,0.14,'All motifs in group q\nuse the same $Q_t$',fc='#E5F3EF',ec=GREEN,bold=True)
    d.text(0.42,0.78,'Removed',fontsize=8.3,fontweight='bold',color=VERMILION)
    d.text(0.42,0.70,'within-group motif-specific\nlocal-state dependence',fontsize=7.7)
    d.text(0.42,0.53,'Preserved',fontsize=8.3,fontweight='bold',color=GREEN)
    d.text(0.42,0.45,r'expected one-site $P(Z\mid S)$',fontsize=7.7)
    d.text(0.42,0.30,'Not forced to remain fixed',fontsize=8.3,fontweight='bold',color=ORANGE)
    d.text(0.42,0.20,'adjacency-category frequencies\nand downstream fitness',fontsize=7.7)
    d.text(0.04,0.04,r'$\sum_q P_t(q\mid s)Q_t(z\mid q,s)=\sum_m P_t(m\mid s)P_0(z\mid m,s)$',fontsize=9.6,fontweight='bold')
    fig.subplots_adjust(left=0.055,right=0.985,bottom=0.06,top=0.95,wspace=0.20,hspace=0.26)
    save_all(fig,'Figure_2_MP_primary'); plt.close(fig)

def figure3():
    rep=pd.read_csv(FREEZE/'results/core/core_mp_replicates.csv')
    inf=pd.read_csv(FREEZE/'results/core/core_mp_inference.csv')
    fig,axs=plt.subplots(2,2,figsize=(7.45,6.25)); a,b,c,d=axs.ravel()
    for ax in axs.ravel(): clean_ax(ax)
    specs=[
        (a,'total_information',r'Total association, $I(M;Z)$ (bits)','Total motif-local-state association'),
        (b,'positional_information',r'Positional association, $I(M;S)$ (bits)','Motif-position association'),
        (c,'corrected_conditional_information',r'Corrected $I(M;Z\mid S)$ (bits)','Corrected sequence-specific information'),
    ]
    for ax,col,ylabel,title in specs:
        for cond,color,marker,ls,label in [('control',ORANGE,'o','--','Sequence-agnostic'),('selective',BLUE,'s','-','Sequence-selective')]:
            dd=rep[rep.condition==cond]
            for p,g in dd.groupby('inherit_prob'):
                ax.scatter(np.full(len(g),p)+jitter(len(g)),g[col],s=18,facecolors='none',edgecolors=color,marker=marker,lw=0.7,zorder=2)
            m=dd.groupby('inherit_prob')[col].mean().sort_index()
            ax.plot(m.index,m.values,color=color,marker=marker,ms=4.8,lw=1.8,ls=ls,markerfacecolor='white' if cond=='control' else color,markeredgecolor=color,zorder=3,label=label)
        ax.set_title(title,loc='left',pad=5); ax.set_xlabel(r'Compositional-coupling probability, $p$'); ax.set_ylabel(ylabel); ax.set_xticks([0.1,0.3,0.5,0.7,0.9,1.0])
    panel_label(a,'a'); panel_label(b,'b'); panel_label(c,'c')
    # MP causal effect
    ctrl=rep[rep.condition=='control']
    sel=rep[rep.condition=='selective']
    for p,g in sel.groupby('inherit_prob'):
        d.scatter(np.full(len(g),p)+jitter(len(g)),g.delta_mp,s=20,facecolors='none',edgecolors=BLUE,marker='s',lw=0.75,zorder=2)
    for p,g in ctrl.groupby('inherit_prob'):
        d.scatter(np.full(len(g),p)+jitter(len(g)),g.delta_mp,s=16,facecolors='none',edgecolors=ORANGE,marker='o',lw=0.65,zorder=2)
    smean=sel.groupby('inherit_prob').delta_mp.mean().sort_index()
    d.plot(smean.index,smean.values,color=BLUE,marker='s',ms=5,lw=1.9,mfc=BLUE,mec=BLUE,label='Sequence-selective',zorder=3)
    # exact zero agnostic line
    d.plot(sorted(ctrl.inherit_prob.unique()),np.zeros(10),color=ORANGE,marker='o',ms=4.6,lw=1.5,ls='--',mfc='white',mec=ORANGE,label='Sequence-agnostic',zorder=3)
    x=inf.inherit_prob.to_numpy(); y=inf.mean_delta_mp.to_numpy(); lo=inf.bootstrap_95_lower.to_numpy(); hi=inf.bootstrap_95_upper.to_numpy()
    d.errorbar(x,y,yerr=[y-lo,hi-y],fmt='none',ecolor=BLUE,elinewidth=1.0,capsize=2.3,zorder=4)
    d.axhline(0,color=LIGHT_GREY,lw=0.8)
    d.set_title('Marginal-preserving causal effect',loc='left',pad=5); d.set_xlabel(r'Compositional-coupling probability, $p$'); d.set_ylabel(r'MP future-fitness loss, $\Delta V_{\mathrm{MP}}$ (fitness units)'); d.set_xticks([0.1,0.3,0.5,0.7,0.9,1.0])
    d.text(0.03,0.95,'20/20 selective populations positive at every p\nAgnostic effect = 0 exactly',transform=d.transAxes,va='top',fontsize=7.5,color=GREY)
    panel_label(d,'d')
    handles=[Line2D([0],[0],color=ORANGE,marker='o',mfc='white',mec=ORANGE,ls='--',lw=1.7,label='Sequence-agnostic'),Line2D([0],[0],color=BLUE,marker='s',mfc=BLUE,mec=BLUE,ls='-',lw=1.7,label='Sequence-selective')]
    fig.legend(handles=handles,loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(0.5,1.01))
    fig.subplots_adjust(top=0.91,left=0.11,right=0.985,bottom=0.09,wspace=0.40,hspace=0.40)
    save_all(fig,'Figure_3_MP_primary'); plt.close(fig)

def figure4():
    repmap=pd.read_csv(REP/'map_summary_rep0.csv')
    avg=pd.read_csv(FREEZE/'results/core_frontier/map_across_population_summary.csv')
    within=pd.read_csv(FREEZE/'results/core_frontier/within_population_monotonicity.csv')
    fam=pd.read_csv(FREEZE/'results/core_frontier/family_monotonicity.csv')
    key=json.loads((FREEZE/'results/core_frontier/CONTINUOUS_FRONTIER_RESULTS.json').read_text())
    fig,axs=plt.subplots(2,2,figsize=(7.45,6.25)); a,b,c,d=axs.ravel()
    for ax in [a,b,c,d]: clean_ax(ax)
    styles={
        'constant':('P',GREY,'white','Constant endpoint'),
        'balanced_random_group':('o',LIGHT_BLUE,'white','Balanced-random'),
        'affinity_rank_group':('^',BLUE,'white','Affinity-rank'),
        'contiguous_substring':('s',ORANGE,'#FFF2B2','Contiguous-substring'),
        'identity':('D',VERMILION,VERMILION,'Identity endpoint'),
    }
    # panel a representative r00, fixed by replicate index rather than outcome selection
    for method,g in repmap.groupby('method'):
        mk,ec,fc,label=styles[method]
        a.scatter(g.corrected_retained_information,g.recovery_fraction,s=39,marker=mk,facecolors=fc,edgecolors=ec,lw=1.0,zorder=3)
    sp=repmap.sort_values('corrected_retained_information')
    # cumulative upper recovery envelope
    upper=np.maximum.accumulate(sp.recovery_fraction.to_numpy())
    a.step(sp.corrected_retained_information,upper,where='post',color=BLACK,lw=1.2,zorder=1)
    a.axhline(0,color=LIGHT_GREY,lw=0.7); a.axhline(1,color=LIGHT_GREY,lw=0.7,ls='--')
    a.set_xlim(-0.006,0.27); a.set_ylim(-0.18,1.08); a.set_xlabel(r'Corrected retained information (bits)'); a.set_ylabel('Future-fitness recovery fraction'); a.set_title('Representative population frontier',loc='left',pad=5); panel_label(a,'a')
    r0=float(within.loc[within.baseline_replicate=='selective_p1.0_r00','spearman_info_recovery'].iloc[0]); a.text(0.04,0.93,rf'$\rho={r0:.3f}$; 64 continuations per map',transform=a.transAxes,fontsize=7.7,color=GREY)
    # panel b map-average relation
    for method,g in avg.groupby('method'):
        mk,ec,fc,label=styles[method]
        b.scatter(g.mean_info,g.mean_recovery,s=43,marker=mk,facecolors=fc,edgecolors=ec,lw=1.0,zorder=3)
        if method in ['balanced_random_group','affinity_rank_group','contiguous_substring']:
            gg=g.sort_values('mean_info'); b.plot(gg.mean_info,gg.mean_recovery,color=ec,lw=0.9,alpha=0.65,zorder=1)
    b.axhline(0,color=LIGHT_GREY,lw=0.7); b.axhline(1,color=LIGHT_GREY,lw=0.7,ls='--')
    b.set_xlim(-0.006,0.27); b.set_ylim(-0.04,1.05); b.set_xlabel('Mean corrected retained information (bits)'); b.set_ylabel('Mean recovery fraction'); b.set_title('Across-map average relation',loc='left',pad=5); panel_label(b,'b')
    b.text(0.04,0.93,rf'Spearman $\rho={key["map_average_spearman"]:.4f}$',transform=b.transAxes,fontsize=8.2,fontweight='bold')
    # panel c within-pop Spearman
    vals=within.sort_values('spearman_info_recovery').spearman_info_recovery.to_numpy(); xx=np.arange(1,len(vals)+1)
    c.scatter(xx,vals,s=31,facecolors='white',edgecolors=BLUE,lw=1.0)
    c.axhline(key['within_population_spearman_mean'],color=GREEN,lw=1.5,label='Mean')
    c.axhline(key['within_population_spearman_median'],color=PURPLE,lw=1.3,ls='--',label='Median')
    c.axhline(0,color=LIGHT_GREY,lw=0.7)
    c.set_xlim(0.3,20.7); c.set_ylim(0.52,1.01); c.set_xticks([1,5,10,15,20]); c.set_xlabel('Population, sorted by Spearman coefficient'); c.set_ylabel(r'Within-population Spearman $\rho$'); c.set_title('Within-population monotonicity',loc='left',pad=5); panel_label(c,'c')
    c.text(0.04,0.08,'20/20 positive\nmean {:.4f}; median {:.4f}; min {:.4f}'.format(key['within_population_spearman_mean'],key['within_population_spearman_median'],key['within_population_spearman_min']),transform=c.transAxes,fontsize=7.6,color=GREY)
    # panel d family monotonicity
    order=['balanced_random_group','affinity_rank_group','contiguous_substring']; labels=['Balanced-random','Affinity-rank','Contiguous-substring']; cols=[LIGHT_BLUE,BLUE,ORANGE]
    yy=np.arange(3)[::-1]
    for y0,meth,lab,col in zip(yy,order,labels,cols):
        r=fam[fam.method==meth].iloc[0]
        d.scatter([r.spearman_map_average],[y0],s=60,marker='s',facecolors=col,edgecolors=col,zorder=3)
        d.text(0.887,y0-0.22,f'n={int(r.n_maps)} maps',fontsize=7.2,color=GREY)
        d.text(1.016,y0,'strictly nondecreasing: '+('yes' if bool(r.strictly_nondecreasing_recovery) else 'no'),va='center',ha='right',fontsize=7.1,color=GREEN if bool(r.strictly_nondecreasing_recovery) else ORANGE)
    d.set_xlim(0.88,1.02); d.set_ylim(-0.38,2.35); d.set_yticks(yy,labels); d.set_xlabel(r'Map-average Spearman $\rho$'); d.set_title('Intervention-family monotonicity',loc='left',pad=5); panel_label(d,'d')
    # legend shared for map families
    handles=[]
    for method in ['constant','balanced_random_group','affinity_rank_group','contiguous_substring','identity']:
        mk,ec,fc,label=styles[method]; handles.append(Line2D([0],[0],marker=mk,color='none',mec=ec,mfc=fc,ms=6.5,label=label))
    fig.legend(handles=handles,ncol=5,frameon=False,loc='upper center',bbox_to_anchor=(0.5,1.01),columnspacing=0.9,handletextpad=0.35)
    fig.subplots_adjust(top=0.91,left=0.11,right=0.985,bottom=0.09,wspace=0.36,hspace=0.40)
    save_all(fig,'Figure_4_MP_primary'); plt.close(fig)

def manifest():
    rows=[]
    for p in sorted(OUT.glob('Figure_*_MP_primary.*')):
        rows.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_bytes':p.stat().st_size})
    pd.DataFrame(rows).to_csv(OUT/'MP_PRIMARY_FIGURES_2_4_MANIFEST_SHA256.csv',index=False)

if __name__=='__main__':
    figure2(); figure3(); figure4(); manifest()
