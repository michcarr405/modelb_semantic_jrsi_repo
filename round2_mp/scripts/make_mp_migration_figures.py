from __future__ import annotations
from pathlib import Path
import json, math, hashlib, shutil
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT=Path('/mnt/data/JRSI_R2_MP_FIGURE_MIGRATION')
DATA=ROOT/'source_tables'; OUT=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True)

BLUE='#0072B2'; LIGHT_BLUE='#8FCDF0'; ORANGE='#E69F00'; GREEN='#009E73'; LIGHT_GREEN='#9ED9C9'; VERM='#D55E00'; MAGENTA='#CC79A7'; GREY='#B5B5B5'; DARK='#555555'; LIGHT='#F2F2F2'; BLACK='#111111'; YELLOW='#F0E442'
REG_COL={'R0_null':BLACK,'R1_syntactic_only':BLUE,'boundary_uncertain':ORANGE,'R2_viability_relevant':GREEN,'R3_strong_adaptation':MAGENTA}
REG_MARK={'R0_null':'x','R1_syntactic_only':'o','boundary_uncertain':'D','R2_viability_relevant':'s','R3_strong_adaptation':'*'}
REG_LABEL={'R0_null':'Null','R1_syntactic_only':'Syntactic-only','boundary_uncertain':'Boundary / uncertain','R2_viability_relevant':'Viability-relevant','R3_strong_adaptation':'Strong adaptation'}
METHOD_STYLE={'constant':('o',ORANGE),'balanced_random_group':('s',BLUE),'affinity_rank_group':('^',GREEN),'contiguous_substring':('D',VERM),'identity':('*',MAGENTA)}

mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':7.4,'axes.titlesize':7.4,'axes.labelsize':7.4,'xtick.labelsize':6.6,'ytick.labelsize':6.6,'legend.fontsize':6.3,'axes.linewidth':0.8,'xtick.major.width':0.65,'ytick.major.width':0.65,'xtick.major.size':3,'ytick.major.size':3,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})

def panel(ax,l,x=-.14,y=1.04): ax.text(x,y,f'({l})',transform=ax.transAxes,fontweight='bold',fontsize=8.2,ha='left',va='bottom')
def clean(ax): ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
def save(fig, stem, title):
    meta={'Title':title,'Author':'JRSI Round-2 programmatic MP migration','Subject':'Programmatic source-data figure; no generative image editing'}
    for ext in ['pdf','svg','eps']:
        fig.savefig(OUT/f'{stem}.{ext}',metadata=meta if ext=='pdf' else None)
    fig.savefig(OUT/f'{stem}.png',dpi=450); fig.savefig(OUT/f'{stem}.tiff',dpi=300)
    plt.close(fig)

def jitter(n,scale=.035): return np.linspace(-scale,scale,n)

def fig2():
    fig,ax=plt.subplots(figsize=(510/72,354/72)); ax.set_axis_off();
    ax.text(.5,.97,'Marginal-preserving counterfactual grouping intervention',ha='center',va='top',fontsize=11)
    xs=[.04,.25,.47,.69]; ws=[.17,.16,.18,.26]; y=.29; h=.54
    titles=['Native motif kernels','Grouping map','Probability-space aggregation','Intervened group kernels']
    faces=['#F7F7F7','#F7F7F7','#EEF7FB','#EEF8F4']; edges=[DARK,DARK,BLUE,GREEN]
    for x,w,t,fc,ec in zip(xs,ws,titles,faces,edges):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008',fc=fc,ec=ec,lw=1.0,transform=ax.transAxes)); ax.text(x+w/2,y+h-.035,t,ha='center',va='top',fontsize=7.6,fontweight='bold',transform=ax.transAxes)
    # native kernels
    ax.text(.125,.72,r'$P_0(z\mid m,s)$',ha='center',fontsize=9,transform=ax.transAxes)
    motifs=['AABDC','CDABA','AACBD','DABCD']; yy=[.64,.56,.48,.40]
    for i,(m,yyi) in enumerate(zip(motifs,yy)):
        ax.text(.055,yyi,m,fontsize=6.5,transform=ax.transAxes,va='center')
        vals=np.array([[.2,.7,.4,.55],[.45,.35,.72,.2],[.62,.25,.4,.75],[.3,.58,.25,.66]])[i]
        for j,v in enumerate(vals): ax.add_patch(Rectangle((.105+j*.018,yyi-.018),.012,.06*v,fc=LIGHT_BLUE,ec=BLUE,lw=.4,transform=ax.transAxes))
    ax.text(.125,.335,'Motif identity changes\nthe local-state kernel',ha='center',fontsize=6.3,transform=ax.transAxes)
    # grouping
    ax.text(.33,.69,r'$g:\mathcal{M}\rightarrow\{1,\ldots,K_g\}$',ha='center',fontsize=8,transform=ax.transAxes)
    ax.text(.29,.59,'AABDC\nCDABA',ha='center',va='center',fontsize=6.4,transform=ax.transAxes)
    ax.text(.37,.59,'group 1',ha='center',va='center',fontsize=6.4,color=BLUE,transform=ax.transAxes)
    ax.text(.29,.45,'AACBD\nDABCD',ha='center',va='center',fontsize=6.4,transform=ax.transAxes)
    ax.text(.37,.45,'group 2',ha='center',va='center',fontsize=6.4,color=GREEN,transform=ax.transAxes)
    # aggregation
    ax.text(.56,.69,r'$w_t(m\mid g,s)$',ha='center',fontsize=8,transform=ax.transAxes)
    ax.text(.56,.60,'current population\nmotif frequencies',ha='center',fontsize=6.5,transform=ax.transAxes)
    ax.text(.56,.50,r'$Q_t(z\mid g,s)=$',ha='center',fontsize=8,transform=ax.transAxes)
    ax.text(.56,.44,r'$\sum_m w_t(m\mid g,s)P_0(z\mid m,s)$',ha='center',fontsize=7.2,transform=ax.transAxes)
    ax.text(.56,.345,'Aggregation occurs after softmax',ha='center',fontsize=6.2,color=DARK,transform=ax.transAxes)
    # intervened
    ax.text(.82,.69,r'$P_{\rm MP}(z\mid m,s)=Q_t(z\mid g(m),s)$',ha='center',fontsize=7.5,transform=ax.transAxes)
    ax.text(.82,.58,'Within each group and segment,\nmotif-specific kernel distinctions\nare removed',ha='center',fontsize=6.4,transform=ax.transAxes)
    ax.text(.82,.44,r'$\sum_qP_t(q\mid s)Q_t(z\mid q,s)$',ha='center',fontsize=7.3,transform=ax.transAxes)
    ax.text(.82,.385,r'$=\sum_mP_t(m\mid s)P_0(z\mid m,s)$',ha='center',fontsize=7.3,transform=ax.transAxes)
    ax.text(.82,.325,r'Expected $P(Z\mid S)$ preserved',ha='center',fontsize=6.6,color=GREEN,fontweight='bold',transform=ax.transAxes)
    for a,b in [((.21,.56),(.245,.56)),((.415,.56),(.465,.56)),((.655,.56),(.685,.56))]: ax.add_patch(FancyArrowPatch(a,b,transform=ax.transAxes,arrowstyle='-|>',mutation_scale=10,lw=1,color=BLACK))
    ax.plot([.035,.96],[.245,.245],color=GREY,lw=.8,transform=ax.transAxes)
    ax.text(.04,.205,'Constant endpoint',fontweight='bold',fontsize=6.8,transform=ax.transAxes); ax.text(.04,.155,r'$K_g=1$: all motifs share one $Q_t(z\mid s)$',fontsize=6.2,transform=ax.transAxes)
    ax.text(.35,.205,'Identity endpoint',fontweight='bold',fontsize=6.8,transform=ax.transAxes); ax.text(.35,.155,r'$K_g=|\mathcal{M}|$: native kernels recovered exactly',fontsize=6.2,transform=ax.transAxes)
    ax.text(.66,.205,'Unchanged',fontweight='bold',fontsize=6.8,transform=ax.transAxes); ax.text(.66,.145,'starting population; sequence identities;\npositional segments; adjacency categories;\npopulation-update rule',fontsize=6.0,transform=ax.transAxes)
    ax.text(.04,.07,'Changed: motif-specific local-state kernels within grouping classes.  The projection is recomputed from the current intervention-branch population each generation.',fontsize=6.2,transform=ax.transAxes)
    save(fig,'Figure_2_MP','Figure 2: marginal-preserving grouping intervention')

def fig3():
    d=pd.read_csv(DATA/'core_mp_replicates.csv'); ps=sorted(d.inherit_prob.unique()); fig,axs=plt.subplots(2,2,figsize=(7.2,444.96/72)); axs=axs.ravel()
    metrics=[('total_information','Total association, $I(M;Z)$ (bits)','Total motif-local-state association'),('positional_information','Positional association, $I(M;S)$ (bits)','Motif-position association'),('corrected_conditional_information',r'Corrected $I(M;Z\mid S)$ (bits)','Position-conditioned sequence-specific information'),('delta_mp',r'$\Delta V_{\rm MP}$ (fitness units)','Future-fitness effect of marginal-preserving complete grouping')]
    for k,(col,yl,title) in enumerate(metrics):
        ax=axs[k]
        for cond,lab,c,mk,off in [('control','Sequence-agnostic',ORANGE,'o',-.006),('selective','Sequence-selective',BLUE,'s',.006)]:
            means=[]
            for p in ps:
                g=d[(d.condition==cond)&(d.inherit_prob==p)]; x=np.full(len(g),p+off)+jitter(len(g),.003)
                ax.scatter(x,g[col],s=9,facecolors='none' if cond=='control' else c,edgecolors=c,marker=mk,lw=.45,alpha=.8)
                means.append(g[col].mean())
            ax.plot(ps,means,color=c,lw=1.2,marker=mk,ms=3,label=lab)
        ax.set_xlabel('Compositional-coupling probability, $p$'); ax.set_ylabel(yl); ax.set_title(title,loc='left',pad=4); panel(ax,chr(97+k)); clean(ax)
        if k==3: ax.axhline(0,color=GREY,lw=.7,ls='--')
    axs[0].legend(loc='upper left',frameon=False,ncol=2,bbox_to_anchor=(0,1.18))
    fig.tight_layout(pad=1.0,w_pad=1.2,h_pad=1.5); save(fig,'Figure_3_MP','Figure 3: sequence-specific information and marginal-preserving fitness effect')

def _frontier_panel(ax,bid):
    ms=pd.read_csv(DATA/'core_p1_map_summary.csv'); fr=pd.read_csv(DATA/'core_p1_frontier_points.csv'); m=ms[ms.baseline_replicate==bid]; f=fr[fr.baseline_replicate==bid].sort_values('corrected_retained_information')
    for meth,g in m.groupby('method'):
        mk,c=METHOD_STYLE.get(meth,('o',DARK)); ax.scatter(g.corrected_retained_information,g.viability_mean,s=18,marker=mk,facecolor='white' if meth!='identity' else c,edgecolor=c,lw=.7,zorder=3)
    ax.step(f.corrected_retained_information,f.frontier_viability,where='post',color=BLACK,lw=1.1)
    ax.axhline(f.actual_viability.iloc[0],color=GREY,ls=':',lw=.9); ax.axhline(f.constant_viability.iloc[0],color=ORANGE,ls='--',lw=.8)
    ax.set_xlabel('Corrected retained information (bits)'); ax.set_ylabel('Mean future model fitness'); clean(ax)

def fig4():
    ms=pd.read_csv(DATA/'core_p1_map_summary.csv'); first=pd.read_csv(DATA/'core_p1_first_target_summary.csv'); core=pd.read_csv(DATA/'core_mp_replicates.csv'); fig,axs=plt.subplots(2,2,figsize=(7.2,464.4/72)); axs=axs.ravel()
    _frontier_panel(axs[0],'selective_p1.0_r00'); axs[0].set_title('Representative marginal-preserving frontier ($p=1.0$)',loc='left'); panel(axs[0],'a')
    # map-average recovery
    av=ms.groupby(['map_id','method','endpoint_type'],as_index=False).agg(info=('corrected_retained_information','mean'),recovery=('recovery_fraction','mean'))
    for meth,g in av.groupby('method'):
        mk,c=METHOD_STYLE.get(meth,('o',DARK)); axs[1].scatter(g['info'],g['recovery'],s=22,marker=mk,facecolor='white' if meth!='identity' else c,edgecolor=c,lw=.8,label=meth.replace('_',' '))
    axs[1].axhline(1,color=GREY,ls=':',lw=.8); axs[1].set_xlabel('Mean corrected retained information (bits)'); axs[1].set_ylabel('Mean recovery fraction'); axs[1].set_title('Map-average continuous recovery',loc='left'); panel(axs[1],'b'); clean(axs[1])
    # delta p1
    p1=core[core.inherit_prob==1.0]
    for i,(cond,c,mk) in enumerate([('control',ORANGE,'o'),('selective',BLUE,'s')]):
        g=p1[p1.condition==cond]; axs[2].scatter(np.full(len(g),i)+jitter(len(g),.08),g.delta_mp,s=18,facecolor='white' if cond=='control' else c,edgecolor=c,marker=mk,lw=.6); axs[2].hlines(g.delta_mp.mean(),i-.18,i+.18,color=c,lw=2)
    axs[2].set_xticks([0,1],['Sequence-\nagnostic','Sequence-\nselective']); axs[2].set_ylabel(r'$\Delta V_{\rm MP}$ (fitness units)'); axs[2].set_title('Marginal-preserving constant-endpoint effect',loc='left'); axs[2].axhline(0,color=GREY,lw=.7); panel(axs[2],'c'); clean(axs[2])
    # rho
    rho=ms.groupby('baseline_replicate').apply(lambda x: x.corrected_retained_information.corr(x.recovery_fraction,method='spearman'),include_groups=False).to_numpy()
    axs[3].scatter(np.ones(len(rho))+jitter(len(rho),.08),rho,s=18,facecolor=LIGHT_GREEN,edgecolor=GREEN,lw=.6); axs[3].hlines(np.median(rho),.78,1.22,color=GREEN,lw=2); axs[3].axhline(0,color=GREY,lw=.7); axs[3].set_xlim(.5,1.5); axs[3].set_xticks([1],['Selective\n$p=1.0$']); axs[3].set_ylabel(r'Spearman $\rho$'); axs[3].set_title('Within-population information–recovery association',loc='left'); panel(axs[3],'d'); clean(axs[3])
    handles=[]
    for meth,(mk,c) in METHOD_STYLE.items(): handles.append(plt.Line2D([],[],marker=mk,ls='',mfc='white' if meth!='identity' else c,mec=c,label=meth.replace('_',' '),ms=5))
    axs[1].legend(handles=handles,frameon=False,fontsize=5.6,loc='lower right')
    fig.tight_layout(pad=1.0,w_pad=1.3,h_pad=1.5); save(fig,'Figure_4_MP','Figure 4: marginal-preserving continuous intervention frontier')

def fig6():
    d=pd.read_csv(DATA/'stage_ab_summary_n8_mp.csv'); A=d[d.stage=='A'].copy(); A['spec']=A.spec_json.map(json.loads); A['p']=A.spec.map(lambda s:s['p']); A['sig']=A.spec.map(lambda s:s['sigma_ratio']); A['br']=A.spec.map(lambda s:s['b_ratio'])
    fig=plt.figure(figsize=(7.2,374.4/72)); gs=fig.add_gridspec(2,3,height_ratios=[1,1],left=.09,right=.98,bottom=.12,top=.92,wspace=.28,hspace=.42)
    axes=[fig.add_subplot(gs[0,i]) for i in range(3)]; axd=fig.add_subplot(gs[1,:])
    brs=[.5,1.6666666667,2.5]
    for i,(ax,br) in enumerate(zip(axes,brs)):
        g=A[np.isclose(A.br,br)]
        for reg,rg in g.groupby('regime'):
            ax.scatter(rg.p,rg.sig,s=30,marker=REG_MARK[reg],facecolor='white' if reg in ['R0_null','R1_syntactic_only','boundary_uncertain'] else REG_COL[reg],edgecolor=REG_COL[reg],lw=.8,label=REG_LABEL[reg])
        ax.set_xlim(.32,1.04); ax.set_ylim(-.05,1.45); ax.set_xlabel('Compositional coupling, $p$');
        if i==0: ax.set_ylabel(r'Affinity-to-noise ratio, $\sigma_a/\Theta$')
        ax.set_title(rf'Positional-bias ratio, $\beta/\Theta={br:.1f}$' if br!=1.6666666667 else r'Positional-bias ratio, $\beta/\Theta\approx1.7$',loc='left'); panel(ax,chr(97+i)); clean(ax)
    counts=d[d.stage.isin(['A','B1'])].groupby(['stage','regime']).size().unstack(fill_value=0)
    y=[1,0]; stages=['A','B1']; left=np.zeros(2)
    order=['R0_null','R1_syntactic_only','boundary_uncertain','R2_viability_relevant','R3_strong_adaptation']
    for reg in order:
        vals=np.array([counts.loc[s,reg] if reg in counts.columns else 0 for s in stages],float); totals=np.array([counts.loc[s].sum() for s in stages]); pct=vals/totals*100
        axd.barh(y,pct,left=left,color=REG_COL[reg],edgecolor='white',height=.45,label=REG_LABEL[reg]);
        for yy,ll,v in zip(y,left,pct):
            if v>7: axd.text(ll+v/2,yy,f'{int(round(v*totals[y.index(yy)]/100))}',ha='center',va='center',fontsize=6,color='white' if reg in ['R0_null','R2_viability_relevant'] else BLACK)
        left+=pct
    axd.set_yticks(y,['Stage A (32 settings)','Stage B1 (16 settings)']); axd.set_xlim(0,100); axd.set_xlabel('Proportion of tested settings'); axd.set_title('Prespecified screen composition after MP migration',loc='left'); panel(axd,'d',x=-.055); clean(axd); axd.legend(ncol=5,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.35),fontsize=5.8)
    save(fig,'Figure_6_MP','Figure 6: marginal-preserving regime map')

def fig7():
    d=pd.read_csv(DATA/'stage_ab_summary_n8_mp.csv'); b=d[d.stage=='B2'].set_index('design_id'); default=float(b.loc['B2_default','delta_mp_mean'])
    groups=[('Window density',[('B2_stride2','Stride 2'),('B2_stride5','Stride 5'),('B2_stride7','Stride 7')]),('Positional structure',[('B2_seg2','2 segments'),('B2_seg8','8 segments'),('B2_reverse','Reversed order'),('B2_jitter','Boundary jitter')]),('Local-state count',[('B2_met3','3 local states'),('B2_met6','6 local states')]),('Fitness formulation and scale',[('B2_reward1',r'$\omega_+=1$'),('B2_reward3',r'$\omega_+=3$'),('B2_penaltylow',r'$\omega_-/\omega_+=0.1$'),('B2_penaltyhigh',r'$\omega_-/\omega_+=0.5$'),('B2_floor0',r'$F_{min}=0$'),('B2_floor1',r'$F_{min}=1$'),('B2_fraction','Fraction-normalized')])]
    fig,axs=plt.subplots(2,2,figsize=(7.2,385.2/72)); axs=axs.ravel()
    for k,(title,items) in enumerate(groups):
        ax=axs[k]; ys=np.arange(len(items))[::-1]
        for yy,(did,lab) in zip(ys,items):
            r=b.loc[did]; c=REG_COL[r.regime]; mk=REG_MARK[r.regime]
            ax.errorbar(r.delta_mp_mean,yy,xerr=[[r.delta_mp_mean-r.delta_mp_low],[r.delta_mp_high-r.delta_mp_mean]],fmt='none',ecolor=c,elinewidth=.9,capsize=2)
            ax.scatter(r.delta_mp_mean,yy,s=25,marker=mk,facecolor='white' if r.regime in ['R0_null','R1_syntactic_only','boundary_uncertain'] else c,edgecolor=c,lw=.7)
        ax.axvline(.25,color=BLACK,ls='--',lw=.7); ax.axvline(default,color=GREY,ls=':',lw=.8); ax.set_yticks(ys,[x[1] for x in items]); ax.set_xlabel(r'$\Delta V_{\rm MP}$ (fitness units)'); ax.set_title(title,loc='left'); panel(ax,chr(97+k)); clean(ax)
    handles=[plt.Line2D([],[],marker=REG_MARK[r],ls='',mfc='white' if r in ['R0_null','R1_syntactic_only','boundary_uncertain'] else REG_COL[r],mec=REG_COL[r],label=REG_LABEL[r],ms=5) for r in REG_COL]
    fig.legend(handles=handles,ncol=5,frameon=False,loc='upper center',bbox_to_anchor=(.5,.995),fontsize=5.8); fig.tight_layout(rect=[0,.02,1,.94],pad=1.0,w_pad=1.5,h_pad=1.4); save(fig,'Figure_7_MP','Figure 7: structural-family support under the marginal-preserving operator')

def fig8():
    sd=pd.read_csv(DATA/'stage_d_confirmation_summary.csv')
    sc=pd.read_csv(DATA/'stage_c_summary_n8_mp.csv')
    coreinf=pd.read_csv(DATA/'core_mp_inference.csv')
    p1=coreinf[np.isclose(coreinf.inherit_prob,1.0)].iloc[0]
    fig=plt.figure(figsize=(7.2,416.16/72)); gs=fig.add_gridspec(2,2,height_ratios=[1.05,1],left=.09,right=.98,bottom=.11,top=.93,wspace=.30,hspace=.48); axa=fig.add_subplot(gs[0,:]); axb=fig.add_subplot(gs[1,0]); axc=fig.add_subplot(gs[1,1])
    entries=[('Default\n(n = 20)',float(p1.mean_delta_mp),float(p1.bootstrap_95_lower),float(p1.bootstrap_95_upper),MAGENTA)]
    for _,r in sd.iterrows():
        c=GREEN if r.design_id in ['A_p2_a3','B2_stride7'] else MAGENTA
        entries.append((f"{r.design_id}\n(n = 8)",float(r.delta_mp_mean),float(r.delta_mp_low),float(r.delta_mp_high),c))
    for i,(lab,m,lo,hi,c) in enumerate(entries):
        axa.errorbar(i,m,yerr=[[m-lo],[hi-m]],fmt='none',ecolor=c,capsize=3,lw=.9); axa.scatter(i,m,s=35,marker='s',facecolor=c,edgecolor=c)
    axa.axhline(.25,color=BLACK,ls='--',lw=.7); axa.set_xticks(np.arange(len(entries)),[e[0] for e in entries]); axa.set_ylabel(r'$\Delta V_{\rm MP}$ (fitness units)'); axa.set_title('Full marginal-preserving confirmations',loc='left'); panel(axa,'a',x=-.055); clean(axa)
    def protocol(ax,source,title):
        g=sc[sc.source_design_id==source].copy(); vals=[]
        for gen in [100,150,250]: vals.append(g[g.design_id.str.startswith(f'C_g{gen}_')].iloc[0])
        for h in [24,36,60]: vals.append(g[g.design_id.str.startswith(f'C_h{h}_')].iloc[0])
        xx=np.arange(6); means=np.array([r.delta_mp_mean for r in vals]); lo=np.array([r.delta_mp_low for r in vals]); hi=np.array([r.delta_mp_high for r in vals])
        col=MAGENTA if source=='B2_default' else GREEN
        ax.errorbar(xx,means,yerr=[means-lo,hi-means],fmt='o',mfc='white',mec=col,ecolor=col,capsize=2,lw=.8); ax.axhline(.25,color=BLACK,ls='--',lw=.7); ax.axvline(2.5,color=GREY,lw=.7); ax.set_xticks(xx,['100','150','250','24','36','60']); ax.set_xlabel(r'Evolution duration, $T_{evo}$            Intervention horizon, $\tau_{int}$'); ax.set_ylabel(r'$\Delta V_{\rm MP}$ (fitness units)'); ax.set_title(title,loc='left'); clean(ax)
    protocol(axb,'B2_default','Default anchor'); panel(axb,'b'); protocol(axc,'B2_stride7','Nearest-boundary setting'); panel(axc,'c');
    save(fig,'Figure_8_MP','Figure 8: MP confirmations and protocol sensitivity')

def s1():
    ms=pd.read_csv(DATA/'core_p1_map_summary.csv'); fr=pd.read_csv(DATA/'core_p1_frontier_points.csv'); fig,axs=plt.subplots(4,5,figsize=(7.2,622.8/72),sharex=True); axs=axs.ravel()
    for i,bid in enumerate(sorted(ms.baseline_replicate.unique())):
        ax=axs[i]; m=ms[ms.baseline_replicate==bid]; f=fr[fr.baseline_replicate==bid].sort_values('corrected_retained_information')
        for meth,g in m.groupby('method'):
            mk,c=METHOD_STYLE.get(meth,('o',DARK)); ax.scatter(g.corrected_retained_information,g.viability_mean,s=8,marker=mk,facecolor='white' if meth!='identity' else c,edgecolor=c,lw=.35)
        ax.step(f.corrected_retained_information,f.frontier_viability,where='post',color=BLACK,lw=.7); ax.axhline(f.actual_viability.iloc[0],color=GREY,ls=':',lw=.5); ax.set_title(f'r = {i:02d}',fontsize=6.7,loc='left'); clean(ax)
        if i%5==0: ax.set_ylabel('Future fitness')
        if i>=15: ax.set_xlabel('Corrected retained\ninformation (bits)')
    handles=[plt.Line2D([],[],marker=mk,ls='',mfc='white' if meth!='identity' else c,mec=c,label=meth.replace('_',' '),ms=4) for meth,(mk,c) in METHOD_STYLE.items()]
    fig.legend(handles=handles,ncol=5,frameon=False,loc='upper center',bbox_to_anchor=(.5,.995),fontsize=5.7); fig.suptitle('Replicate-specific marginal-preserving frontiers at $p=1.0$',y=.965,fontsize=8.3); fig.tight_layout(rect=[.02,.02,1,.94],pad=.6,w_pad=.5,h_pad=.8); save(fig,'Figure_S1_MP','Supplementary Figure S1: all 20 p=1 marginal-preserving frontiers')

def s2():
    d=pd.read_csv(DATA/'core_mp_replicates.csv'); inf=pd.read_csv(DATA/'core_mp_inference.csv'); ps=sorted(d.inherit_prob.unique()); fig,axs=plt.subplots(3,2,figsize=(7.2,529.2/72)); axs=axs.ravel()
    # a delta mean
    for cond,c,mk in [('control',ORANGE,'o'),('selective',BLUE,'s')]: axs[0].plot(ps,[d[(d.condition==cond)&(d.inherit_prob==p)].delta_mp.mean() for p in ps],marker=mk,color=c,lw=1,label=cond)
    axs[0].set_ylabel(r'Mean $\Delta V_{\rm MP}$'); axs[0].set_title('Mean marginal-preserving intervention effect',loc='left')
    # b corrected info
    for cond,c,mk in [('control',ORANGE,'o'),('selective',BLUE,'s')]: axs[1].plot(ps,[d[(d.condition==cond)&(d.inherit_prob==p)].corrected_conditional_information.mean() for p in ps],marker=mk,color=c,lw=1)
    axs[1].set_ylabel('Corrected information (bits)'); axs[1].set_title('Mean corrected sequence-specific information',loc='left')
    # c positive blocks
    axs[2].plot(inf.inherit_prob,inf.positive_blocks,marker='s',color=BLUE); axs[2].set_ylim(0,21); axs[2].set_ylabel('Positive selective blocks / 20'); axs[2].set_title('Positive marginal-preserving effects',loc='left')
    # d diff info
    dif=[]
    for p in ps: dif.append(d[(d.condition=='selective')&(d.inherit_prob==p)].corrected_conditional_information.mean()-d[(d.condition=='control')&(d.inherit_prob==p)].corrected_conditional_information.mean())
    axs[3].plot(ps,dif,marker='s',color=GREEN); axs[3].set_ylabel('Selective - agnostic (bits)'); axs[3].set_title('Corrected-information difference',loc='left')
    # e delta diff
    axs[4].plot(inf.inherit_prob,inf.mean_delta_mp,marker='s',color=BLUE); axs[4].fill_between(inf.inherit_prob,inf.bootstrap_95_lower,inf.bootstrap_95_upper,color=LIGHT_BLUE,alpha=.4); axs[4].set_ylabel('Selective - agnostic (fitness units)'); axs[4].set_title('MP intervention-effect difference',loc='left')
    # f q
    axs[5].semilogy(inf.inherit_prob,inf.q_value_bh_10,marker='s',color=MAGENTA); axs[5].axhline(.05,color=GREY,ls='--',lw=.7); axs[5].set_ylabel('BH-adjusted $q$'); axs[5].set_title('Replicate-level inference',loc='left')
    for i,ax in enumerate(axs): ax.set_xlabel('Compositional-coupling probability, $p$'); panel(ax,chr(97+i)); clean(ax)
    axs[0].legend(['Sequence-agnostic','Sequence-selective'],frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(0,1.18),fontsize=5.8); fig.tight_layout(pad=1,w_pad=1.5,h_pad=1.6); save(fig,'Figure_S2_MP','Supplementary Figure S2: complete MP core inferential record')

def s3():
    d=pd.read_csv(DATA/'core_mp_replicates.csv'); fig,axs=plt.subplots(1,2,figsize=(7.2,248.4/72));
    for ax,col,yl,title in [(axs[0],'delta_mp',r'$\Delta V_{\rm MP}$ (fitness units)','Marginal-preserving intervention effect'),(axs[1],'corrected_conditional_information',r'Corrected $I(M;Z\mid S)$ (bits)','Corrected sequence-specific information')]:
        for cond,c,mk,off in [('control',ORANGE,'o',-.006),('selective',BLUE,'s',.006)]:
            g=d[d.condition==cond]; ax.scatter(g.inherit_prob+off+np.tile(jitter(20,.003),10),g[col],s=9,marker=mk,facecolor='white' if cond=='control' else c,edgecolor=c,lw=.4,alpha=.8)
        ax.set_xlabel('Compositional-coupling probability, $p$'); ax.set_ylabel(yl); ax.set_title(title,loc='left'); clean(ax)
    panel(axs[0],'a'); panel(axs[1],'b'); fig.tight_layout(pad=1,w_pad=1.5); save(fig,'Figure_S3_MP','Supplementary Figure S3: replicate-level MP core distributions')

def s5():
    d=pd.read_csv(DATA/'stage_ab_summary_n8_mp.csv').sort_values(['stage','design_id']).reset_index(drop=True); x=np.arange(1,len(d)+1); stages=d.stage.to_numpy(); fig,axs=plt.subplots(3,1,figsize=(7.2,536.4/72),sharex=True)
    mets=[('corrected_information_mean','corrected_information_low','corrected_information_high','Corrected $I_{seq,corr}$ (bits)',.01),('delta_mp_mean','delta_mp_low','delta_mp_high',r'$\Delta V_{\rm MP}$ (fitness units)',.25),('adaptive_gain_mean','adaptive_gain_low','adaptive_gain_high','Adaptive gain (fitness units)',1.0)]
    bounds=[]
    for st in ['A','B1','B2']:
        ix=np.where(stages==st)[0]; bounds.append((ix.min()+1,ix.max()+1,st))
    for k,(m,lo,hi,yl,thr) in enumerate(mets):
        ax=axs[k]
        for a,b,st in bounds: ax.axvspan(a-.5,b+.5,color={'A':'#EAF2F8','B1':'#FFF4E5','B2':'#EAF7F3'}[st],zorder=0)
        for i,r in d.iterrows():
            c=REG_COL[r.regime]; ax.errorbar(x[i],r[m],yerr=[[r[m]-r[lo]],[r[hi]-r[m]]],fmt='o',ms=2.8,mfc=c,mec=c,ecolor=c,lw=.5,capsize=1)
        ax.axhline(thr,color=BLACK,ls='--',lw=.7); ax.set_ylabel(yl); ax.set_title(['Corrected sequence-specific information','Marginal-preserving intervention effect','Selection-driven fitness gain'][k],loc='left'); panel(ax,chr(97+k),x=-.065); clean(ax)
    axs[-1].set_xlabel('Prespecified setting index (ordered by stage; n = 8 per setting)'); axs[-1].set_xlim(.5,len(d)+.5); axs[-1].set_xticks([1,8,16,24,32,33,40,48,49,57,65]); fig.tight_layout(pad=1,h_pad=1.2); save(fig,'Figure_S5_MP','Supplementary Figure S5: setting-level MP domain map with n=8 per setting')

def s6():
    d=pd.read_csv(DATA/'stage_c_summary_n8_mp.csv'); fig,axs=plt.subplots(3,2,figsize=(7.2,579.6/72),sharex='col'); mets=[('corrected_information_mean','corrected_information_low','corrected_information_high','Corrected $I_{seq,corr}$ (bits)',.01),('delta_mp_mean','delta_mp_low','delta_mp_high',r'$\Delta V_{\rm MP}$ (fitness units)',.25),('adaptive_gain_mean','adaptive_gain_low','adaptive_gain_high','Adaptive gain (fitness units)',1.0)]
    for col,(source,title) in enumerate([('B2_default','Default anchor'),('B2_stride7','Nearest-boundary setting')]):
        g=d[d.source_design_id==source]
        vals=[]
        for gen in [100,150,250]: vals.append(g[g.design_id.str.startswith(f'C_g{gen}_')].iloc[0])
        for h in [24,36,60]: vals.append(g[g.design_id.str.startswith(f'C_h{h}_')].iloc[0])
        for row,(m,lo,hi,yl,thr) in enumerate(mets):
            ax=axs[row,col]; xx=np.arange(6); mean=np.array([v[m] for v in vals]); low=np.array([v[lo] for v in vals]); high=np.array([v[hi] for v in vals]); colors=[REG_COL[v.regime] for v in vals];
            for x0,mm,ll,hh,c,v in zip(xx,mean,low,high,colors,vals): ax.errorbar(x0,mm,yerr=[[mm-ll],[hh-mm]],fmt=REG_MARK[v.regime],mfc='white' if v.regime in ['R0_null','R1_syntactic_only','boundary_uncertain'] else c,mec=c,ecolor=c,ms=4,capsize=2,lw=.7)
            ax.axhline(thr,color=BLACK,ls='--',lw=.7); ax.axvline(2.5,color=GREY,lw=.6); ax.set_ylabel(yl); clean(ax); panel(ax,chr(97+row*2+col),x=-.16)
            if row==0: ax.set_title(title,fontweight='bold')
            if row==2: ax.set_xticks(xx,['100','150','250','24','36','60']); ax.set_xlabel('Evolution duration, $T_{evo}$        Intervention horizon, $\tau_{int}$')
    fig.tight_layout(pad=1,w_pad=2,h_pad=1.4); save(fig,'Figure_S6_MP','Supplementary Figure S6: MP protocol sensitivity at n=8')

def s7():
    r=pd.read_csv(DATA/'stage_d_replicate_summary.csv'); s=pd.read_csv(DATA/'stage_d_confirmation_summary.csv'); fig=plt.figure(figsize=(7.2,478.8/72)); gs=fig.add_gridspec(2,3,left=.08,right=.98,bottom=.10,top=.94,wspace=.32,hspace=.45); axes=[fig.add_subplot(gs[i,j]) for i in range(2) for j in range(3)]
    for k,cid in enumerate(['D0','D1','D2']):
        ax=axes[k]; g=r[r.confirm_id==cid].sort_values('replicate');
        for _,row in g.iterrows(): ax.plot([0,1],[row.constant_mean,row.actual_mean],color=GREY,lw=.7)
        ax.scatter(np.zeros(len(g)),g.constant_mean,s=18,facecolor='white',edgecolor=ORANGE,lw=.6); ax.scatter(np.ones(len(g)),g.actual_mean,s=18,marker='s',facecolor=BLUE,edgecolor=BLUE,lw=.6); ax.set_xticks([0,1],['MP constant','Actual']); ax.set_ylabel('Mean future model fitness'); ax.set_title(f'{cid}: {g.design_id.iloc[0]}',loc='left'); panel(ax,chr(97+k)); clean(ax)
    ax=axes[3]
    for i,cid in enumerate(['D0','D1','D2']):
        g=r[r.confirm_id==cid]; ax.scatter(np.full(len(g),i)+jitter(len(g),.07),g.delta_mp,s=18,facecolor=LIGHT_GREEN,edgecolor=GREEN,lw=.5); ax.hlines(g.delta_mp.mean(),i-.17,i+.17,color=GREEN,lw=2)
    ax.axhline(.25,color=BLACK,ls='--',lw=.7); ax.set_xticks(range(3),['D0','D1','D2']); ax.set_ylabel(r'$\Delta V_{\rm MP}$ (fitness units)'); ax.set_title('Marginal-preserving intervention effect',loc='left'); panel(ax,'d'); clean(ax)
    ax=axes[4]
    for i,cid in enumerate(['D0','D1','D2']):
        g=r[r.confirm_id==cid]; ax.scatter(np.full(len(g),i)+jitter(len(g),.07),g.spearman_info_recovery,s=18,facecolor='white',edgecolor=MAGENTA,lw=.6); ax.hlines(g.spearman_info_recovery.median(),i-.17,i+.17,color=MAGENTA,lw=2)
    ax.axhline(0,color=GREY,lw=.7); ax.set_xticks(range(3),['D0','D1','D2']); ax.set_ylabel(r'Within-population Spearman $\rho$'); ax.set_title('Continuous information–recovery association',loc='left'); panel(ax,'e'); clean(ax)
    ax=axes[5]; ax.set_axis_off(); panel(ax,'f',x=-.08); ax.set_title('Confirmation audit',loc='left',pad=6)
    rows=[r'Positive $\Delta V_{MP}$',r'Positive $\rho$','Identity recovery exact']; y=[.72,.52,.32]
    for rr,yy in zip(rows,y): ax.text(.02,yy,rr,transform=ax.transAxes,fontsize=6.5,ha='left')
    for j,cid in enumerate(['D0','D1','D2']):
        ss=s[s.confirm_id==cid].iloc[0]; ax.text(.60+j*.13,.88,cid,transform=ax.transAxes,ha='center',fontweight='bold',fontsize=6.6); vals=[f"{int(ss.positive_blocks)}/8",f"{int(ss.positive_spearman_blocks)}/8",'8/8' if ss.identity_exact_all else 'no'];
        for v,yy in zip(vals,y): ax.text(.60+j*.13,yy,v,transform=ax.transAxes,ha='center',fontsize=6.4)
    save(fig,'Figure_S7_MP','Supplementary Figure S7: MP Stage-D replicate and audit records')

def s8():
    l=pd.read_csv(DATA/'landscape_level.csv'); inf=pd.read_csv(DATA/'landscape_inference.csv'); designs=['B2_default','B2_reward3','B2_stride7','A_p2_a3']; fig,axs=plt.subplots(2,2,figsize=(7.2,5.7)); axs=axs.ravel()
    for k,(ax,did) in enumerate(zip(axs,designs)):
        g=l[l.design_id==did].sort_values('landscape'); x=np.arange(8); ax.errorbar(x,g.mean_delta_mp,yerr=[g.mean_delta_mp-g.delta_mp_pop_boot_low,g.delta_mp_pop_boot_high-g.mean_delta_mp],fmt='s',mfc=LIGHT_GREEN, mec=GREEN, ecolor=GREEN,capsize=2,lw=.8,ms=4); ax.axhline(.25,color=BLACK,ls='--',lw=.7); ax.axhline(0,color=GREY,lw=.6); ax.set_xticks(x,[f'L{i}' for i in range(8)]); ax.set_ylabel(r'Mean $\Delta V_{\rm MP}$'); ax.set_title(did,loc='left'); panel(ax,chr(97+k)); clean(ax)
    fig.suptitle('Independent affinity-landscape replication (8 populations per landscape)',y=.985,fontsize=8.2); fig.tight_layout(rect=[0,0,1,.96],pad=1.0,w_pad=1.3,h_pad=1.4); save(fig,'Figure_S8_MP','Supplementary Figure S8: independent affinity-landscape replication')

def main():
    fig2(); fig3(); fig4(); fig6(); fig7(); fig8(); s1(); s2(); s3(); s5(); s6(); s7(); s8()
    # Copy already-programmatic high-continuation causal-specificity figures into integrated set.
    src=Path('/mnt/data/JRSI_R2_MP_FIGURES/figures')
    for old,new in [('R2_FIGURE_5_MP_CAUSAL_SPECIFICITY','Figure_5_MP'),('R2_FIGURE_S4_MP_CAUSAL_SPECIFICITY','Figure_S4_MP')]:
        for ext in ['pdf','svg','eps','png','tiff']:
            p=src/f'{old}.{ext}'
            if p.exists(): shutil.copy2(p,OUT/f'{new}.{ext}')
    # manifest
    def sh(p):
        h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
    man={'source_tables':{p.name:sh(p) for p in sorted(DATA.glob('*'))},'figures':{p.name:sh(p) for p in sorted(OUT.glob('*'))},'note':'All figures generated programmatically from frozen source tables; Figure 5/S4 copied from prior programmatic 64-continuation production. No generative editor used.'}
    (ROOT/'SHA256_MANIFEST.json').write_text(json.dumps(man,indent=2))

if __name__=='__main__': main()
