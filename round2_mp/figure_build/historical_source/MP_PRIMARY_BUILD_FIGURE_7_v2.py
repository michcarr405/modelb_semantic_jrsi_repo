from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path('/mnt/data/fig7_work/JRSI_R2_MP_MIGRATION_DETAILED_SOURCE_TABLES_2026-10-03')
SRC = ROOT/'migration_freeze_tables'/'screen_n8'
OUT = Path('/mnt/data')

SUMMARY = SRC/'stage_ab_summary_n8_mp.csv'
COUNTS = SRC/'regime_counts_n8_mp.csv'

# Restrained colour-blind-safe palette used throughout the R2 artwork.
GREY = '#666666'
LIGHT_GREY = '#B5B5B5'
BLACK = '#111111'
BLUE = '#56B4E9'
ORANGE = '#E69F00'
GREEN = '#009E73'
MAGENTA = '#CC79A7'
REGIME_COLORS = {
    'R0_null': GREY,
    'R1_syntactic_only': BLUE,
    'boundary_uncertain': ORANGE,
    'R2_viability_relevant': GREEN,
    'R3_strong_adaptation': MAGENTA,
}
REGIME_LABELS = {
    'R0_null': 'Null',
    'R1_syntactic_only': 'Syntactic-only',
    'boundary_uncertain': 'Boundary / uncertain',
    'R2_viability_relevant': 'Viability-relevant',
    'R3_strong_adaptation': 'Strong adaptation',
}
ORDER = ['R0_null','R1_syntactic_only','boundary_uncertain','R2_viability_relevant','R3_strong_adaptation']

mpl.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':7.4,
    'axes.titlesize':7.8,
    'axes.labelsize':7.4,
    'xtick.labelsize':6.6,
    'ytick.labelsize':6.6,
    'legend.fontsize':6.4,
    'axes.linewidth':0.8,
    'xtick.major.width':0.65,
    'ytick.major.width':0.65,
    'xtick.major.size':3.2,
    'ytick.major.size':3.2,
    'pdf.fonttype':42,
    'ps.fonttype':42,
    'svg.fonttype':'none',
})

def clean_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out')


def panel_label(ax, label, x=-0.15, y=1.045):
    ax.text(x,y,f'({label})',transform=ax.transAxes,fontweight='bold',fontsize=8.3,va='bottom',ha='left')


def save_all(fig, stem):
    meta = {
        'Title':'Figure 7: expanded n=8 marginal-preserving domain map',
        'Author':'JRSI Round-2 programmatic figure production',
        'Subject':'Programmatic source-faithful figure from frozen MP migration tables',
    }
    fig.savefig(OUT/f'{stem}.pdf', metadata=meta)
    fig.savefig(OUT/f'{stem}.svg')
    fig.savefig(OUT/f'{stem}.eps')
    fig.savefig(OUT/f'{stem}_600DPI.png', dpi=600)
    fig.savefig(OUT/f'{stem}_600DPI.tiff', dpi=600)


def main():
    df = pd.read_csv(SUMMARY)
    counts = pd.read_csv(COUNTS)
    df['spec'] = df['spec_json'].map(json.loads)

    A = df[df.stage=='A'].copy()
    B1 = df[df.stage=='B1'].copy().sort_values('design_id').reset_index(drop=True)
    B2 = df[df.stage=='B2'].copy()

    # Stage A public plotting coordinates.
    A['p'] = A['spec'].map(lambda d: float(d['p']))
    A['sigma_ratio'] = A['spec'].map(lambda d: float(d['sigma_ratio']))
    A['b_ratio'] = A['spec'].map(lambda d: float(d['b_ratio']))

    fig = plt.figure(figsize=(7.2,6.60))
    gs = fig.add_gridspec(2,2,left=0.105,right=0.985,bottom=0.090,top=0.855,wspace=0.34,hspace=0.50)
    axa = fig.add_subplot(gs[0,0])
    axb = fig.add_subplot(gs[0,1])
    axc = fig.add_subplot(gs[1,0])
    axd = fig.add_subplot(gs[1,1])
    for ax in (axa,axb,axc,axd): clean_ax(ax)

    # Shared regime legend: colour alone encodes classification.
    regime_handles = [Patch(facecolor=REGIME_COLORS[k], edgecolor='none', label=REGIME_LABELS[k]) for k in ORDER]
    fig.legend(handles=regime_handles, frameon=False, ncol=5, loc='upper center',
               bbox_to_anchor=(0.5,0.988), columnspacing=1.1, handlelength=1.0, handletextpad=0.35)

    # (a) Focused mechanistic map: marker shape encodes positional-bias/noise ratio.
    def ratio_marker(x):
        if abs(x-0.5) < 0.12: return 'o'
        if abs(x-2.5) < 0.12: return '^'
        return 's'
    for _,r in A.iterrows():
        axa.scatter(r.p, r.sigma_ratio, s=42, marker=ratio_marker(r.b_ratio),
                    facecolor=REGIME_COLORS[r.regime], edgecolor=BLACK, linewidth=0.45, zorder=3)
    axa.set_xlim(0.35,1.05); axa.set_ylim(-0.05,1.47)
    axa.set_xticks([0.4,0.6,0.8,1.0]); axa.set_yticks([0,0.45,0.90,1.35])
    axa.set_xlabel(r'Compositional coupling, $p$')
    axa.set_ylabel(r'Affinity-to-noise ratio, $\sigma_a/\Theta$')
    axa.set_title('Focused mechanistic screen (32 settings)', loc='left', pad=5)
    panel_label(axa,'a',x=-0.17)
    ratio_handles = [
        Line2D([0],[0],marker='o',ls='none',mec=BLACK,mfc='white',ms=5.4,label=r'$\beta/\Theta=0.5$'),
        Line2D([0],[0],marker='s',ls='none',mec=BLACK,mfc='white',ms=5.4,label=r'$\beta/\Theta\approx1.7$'),
        Line2D([0],[0],marker='^',ls='none',mec=BLACK,mfc='white',ms=5.4,label=r'$\beta/\Theta=2.5$'),
    ]
    fig.legend(handles=ratio_handles, frameon=False, ncol=3, loc='upper center',
               bbox_to_anchor=(0.29,0.938), borderaxespad=0.0,
               columnspacing=0.9, handletextpad=0.25)

    # (b) Broad multivariable screen: retain prespecified setting order, no public design IDs.
    x = np.arange(1,len(B1)+1)
    axb.axhline(0,color=LIGHT_GREY,lw=0.8,zorder=0)
    axb.axhline(0.25,color=GREY,lw=0.9,ls='--',zorder=0)
    for xi,(_,r) in zip(x,B1.iterrows()):
        col = REGIME_COLORS[r.regime]
        axb.errorbar(xi,r.delta_mp_mean,
                     yerr=[[r.delta_mp_mean-r.delta_mp_low],[r.delta_mp_high-r.delta_mp_mean]],
                     fmt='o',ms=4.7,mfc=col,mec=BLACK,mew=0.4,color=col,ecolor=col,
                     elinewidth=0.9,capsize=2.0,zorder=3)
    axb.set_xlim(0.3,16.7)
    axb.set_xticks([1,4,8,12,16])
    axb.set_xlabel('Screen setting (prespecified order)')
    axb.set_ylabel(r'MP future-fitness loss, $\Delta V_{\rm MP}$')
    axb.set_title('Broad multivariable screen (16 settings)',loc='left',pad=5)
    panel_label(axb,'b',x=-0.17)

    # (c) Structural families: show every non-anchor setting, grouped by family.
    B2p = B2[B2.family!='anchor'].copy()
    fam_order = ['window','position','metabolite','fitness']
    fam_labels = ['Window\ndensity','Positional\nstructure','Local-state\ncount','Fitness\nformulation']
    rng = np.random.default_rng(0)  # deterministic display jitter only
    axc.axhline(0,color=LIGHT_GREY,lw=0.8,zorder=0)
    axc.axhline(0.25,color=GREY,lw=0.9,ls='--',zorder=0)
    for j,fam in enumerate(fam_order):
        g = B2p[B2p.family==fam].sort_values('design_id')
        if len(g)==1:
            offs=np.array([0.0])
        else:
            offs=np.linspace(-0.16,0.16,len(g))
        for off,(_,r) in zip(offs,g.iterrows()):
            col=REGIME_COLORS[r.regime]
            axc.errorbar(j+off,r.delta_mp_mean,
                         yerr=[[r.delta_mp_mean-r.delta_mp_low],[r.delta_mp_high-r.delta_mp_mean]],
                         fmt='o',ms=4.7,mfc=col,mec=BLACK,mew=0.4,color=col,ecolor=col,
                         elinewidth=0.85,capsize=1.8,zorder=3)
    axc.set_xticks(range(4),fam_labels)
    axc.set_ylabel(r'MP future-fitness loss, $\Delta V_{\rm MP}$')
    axc.set_title('Structural-family screen (16 settings)',loc='left',pad=5)
    panel_label(axc,'c',x=-0.17)

    # (d) Domain-level composition: 100% stacked bars with counts printed inside.
    stage_order = ['A','B1','B2']
    stage_labels = ['Focused map\n(32)','Broad screen\n(16)','Structural families\n(17)']
    y = np.arange(3)
    for yi,(st,lab) in enumerate(zip(stage_order,stage_labels)):
        r = counts[counts.stage==st].iloc[0]
        total = int(sum(int(r[k]) for k in ORDER))
        left=0.0
        for k in ORDER:
            v=int(r[k])
            if v==0: continue
            frac=100.0*v/total
            axd.barh(yi,frac,left=left,height=0.56,color=REGIME_COLORS[k],edgecolor='white',linewidth=0.7)
            if frac >= 8:
                # White on dark grey/green/magenta; black on light blue/orange.
                tc = 'white' if k in ('R0_null','R2_viability_relevant','R3_strong_adaptation') else BLACK
                axd.text(left+frac/2,yi,str(v),ha='center',va='center',fontsize=6.6,color=tc)
            left += frac
    axd.set_xlim(0,100)
    axd.set_xticks([0,25,50,75,100],[0,25,50,75,'100%'])
    axd.set_yticks(y,stage_labels)
    axd.invert_yaxis()
    axd.set_xlabel('Proportion of tested settings')
    axd.set_title('MP domain summary (65 settings)',loc='left',pad=5)
    panel_label(axd,'d',x=-0.17)

    save_all(fig,'Figure_7_MP_PRIMARY_v2_QC')
    plt.close(fig)

    # Numeric verification record.
    rows=[]
    for st in stage_order:
        r=counts[counts.stage==st].iloc[0]
        total=sum(int(r[k]) for k in ORDER)
        rec={'stage':st,'n_settings':total}
        for k in ORDER: rec[k]=int(r[k])
        rows.append(rec)
    pd.DataFrame(rows).to_csv(OUT/'FIGURE_7_MP_PRIMARY_v2_NUMERIC_QC.csv',index=False)

if __name__=='__main__':
    main()
