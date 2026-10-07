from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path('/mnt/data/r2work/fig3_v4')
IN=ROOT/'inputs'; OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
BLUE='#0072B2'; ORANGE='#E69F00'; GREY='#666666'; LIGHT_GREY='#B8B8B8'

mpl.rcParams.update({
    'font.family':'sans-serif','font.sans-serif':['Arial','Arimo','Helvetica','Nimbus Sans','DejaVu Sans'],
    'font.size':9.4,'axes.titlesize':10.5,'axes.labelsize':9.4,'xtick.labelsize':8.3,'ytick.labelsize':8.3,
    'legend.fontsize':8.0,'axes.linewidth':0.8,'pdf.fonttype':42,'ps.fonttype':42,
})

def clean_ax(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out',length=4,width=0.8)

def panel_label(ax,label,x=-0.13,y=1.085):
    ax.text(x,y,f'({label})',transform=ax.transAxes,fontweight='bold',fontsize=11,va='bottom')

def jitter(n,width=0.009):
    return np.linspace(-width,width,n) if n>1 else np.zeros(n)

def save_all(fig,stem):
    # Vector master plus raster exports at 600 dpi (>= JRSI minimum 300 dpi).
    fig.savefig(OUT/f'{stem}.pdf',bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}.svg',bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}.eps',bbox_inches='tight',pad_inches=0.03)
    fig.savefig(OUT/f'{stem}.png',bbox_inches='tight',pad_inches=0.03,dpi=600)
    fig.savefig(OUT/f'{stem}.tiff',bbox_inches='tight',pad_inches=0.03,dpi=600,pil_kwargs={'compression':'tiff_lzw'})

def main():
    rep=pd.read_csv(IN/'core_mp_replicates.csv')
    inf=pd.read_csv(IN/'core_mp_inference.csv')
    fig,axs=plt.subplots(2,2,figsize=(7.45,6.32)); a,b,c,d=axs.ravel()
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
        ax.set_title(title,loc='left',pad=12)
        ax.set_xlabel(r'Compositional-coupling probability, $p$')
        ax.set_ylabel(ylabel)
        ax.set_xticks([0.1,0.3,0.5,0.7,0.9,1.0])
    panel_label(a,'a'); panel_label(b,'b'); panel_label(c,'c')

    ctrl=rep[rep.condition=='control']; sel=rep[rep.condition=='selective']
    for p,g in sel.groupby('inherit_prob'):
        d.scatter(np.full(len(g),p)+jitter(len(g)),g.delta_mp,s=20,facecolors='none',edgecolors=BLUE,marker='s',lw=0.75,zorder=2)
    for p,g in ctrl.groupby('inherit_prob'):
        d.scatter(np.full(len(g),p)+jitter(len(g)),g.delta_mp,s=16,facecolors='none',edgecolors=ORANGE,marker='o',lw=0.65,zorder=2)
    smean=sel.groupby('inherit_prob').delta_mp.mean().sort_index()
    d.plot(smean.index,smean.values,color=BLUE,marker='s',ms=5,lw=1.9,mfc=BLUE,mec=BLUE,label='Sequence-selective',zorder=3)
    d.plot(sorted(ctrl.inherit_prob.unique()),np.zeros(10),color=ORANGE,marker='o',ms=4.6,lw=1.5,ls='--',mfc='white',mec=ORANGE,label='Sequence-agnostic',zorder=3)
    x=inf.inherit_prob.to_numpy(); y=inf.mean_delta_mp.to_numpy(); lo=inf.bootstrap_95_lower.to_numpy(); hi=inf.bootstrap_95_upper.to_numpy()
    d.errorbar(x,y,yerr=[y-lo,hi-y],fmt='none',ecolor=BLUE,elinewidth=1.0,capsize=2.3,zorder=4)
    d.axhline(0,color=LIGHT_GREY,lw=0.8)
    d.set_ylim(-0.05,4.60)
    d.set_title('Marginal-preserving causal effect',loc='left',pad=12)
    d.set_xlabel(r'Compositional-coupling probability, $p$')
    d.set_ylabel('MP future-fitness loss,\n' + r'$\Delta V_{\mathrm{MP}}$ (fitness units)', labelpad=10)
    d.set_xticks([0.1,0.3,0.5,0.7,0.9,1.0])
    d.text(0.03,0.95,'20/20 selective populations positive at every p\nAgnostic effect = 0 exactly',transform=d.transAxes,va='top',fontsize=7.5,color=GREY)
    panel_label(d,'d')

    handles=[Line2D([0],[0],color=ORANGE,marker='o',mfc='white',mec=ORANGE,ls='--',lw=1.7,label='Sequence-agnostic'),Line2D([0],[0],color=BLUE,marker='s',mfc=BLUE,mec=BLUE,ls='-',lw=1.7,label='Sequence-selective')]
    fig.legend(handles=handles,loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(0.5,1.015))
    fig.subplots_adjust(top=0.895,left=0.115,right=0.985,bottom=0.09,wspace=0.40,hspace=0.46)
    save_all(fig,'Figure_3_MP_PRIMARY_v4_TWO_LINE_LABEL')
    plt.close(fig)

if __name__=='__main__': main()
