from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE = Path('/mnt/data/fig6_source/extracted/JRSI_R2_MP_MIGRATION_DETAILED_SOURCE_TABLES_2026-10-03/migration_freeze_tables/affinity_landscapes')
OUT = Path('/mnt/data')
POP = pd.read_csv(BASE / 'population_level.csv')
LVL = pd.read_csv(BASE / 'landscape_level.csv')
INF = pd.read_csv(BASE / 'landscape_inference.csv')

BLACK = '#111111'
GREY = '#9b9b9b'
LIGHT_GREY = '#d9d9d9'
MID_GREY = '#666666'
VERY_LIGHT = '#f3f3f3'

mpl.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 8.0,
    'axes.titlesize': 9.2,
    'axes.labelsize': 8.6,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 7.2,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.7,
    'ytick.major.width': 0.7,
    'xtick.major.size': 3.2,
    'ytick.major.size': 3.2,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

PANELS = [
    ('B2_default', 'Default parameter setting'),
    ('B2_reward3', 'Higher-reward strong-adaptation'),
    ('B2_stride7', 'Sparse-window viability'),
    ('A_p2_a3', 'Intermediate-coupling viability'),
]


def panel_label(ax, lab):
    ax.text(-0.12, 1.055, f'({lab})', transform=ax.transAxes,
            fontweight='bold', fontsize=9.2, ha='left', va='bottom')


def draw_panel(ax, design, title, lab, ylim, yticks=None):
    p = POP[POP.design_id == design].copy()
    l = LVL[LVL.design_id == design].sort_values('landscape').copy()
    inf = INF[INF.design_id == design].iloc[0]

    # Fixed deterministic jitter so each landscape's nested population points remain visible.
    jitter = np.linspace(-0.16, 0.16, 8)
    for landscape in range(8):
        vals = p[p.landscape == landscape].sort_values('replicate').delta_mp.to_numpy()
        ax.scatter(np.full(len(vals), landscape + 1) + jitter[:len(vals)], vals,
                   s=14, marker='o', facecolors='none', edgecolors=GREY,
                   linewidths=0.65, zorder=2)

    xs = l.landscape.to_numpy() + 1
    means = l.mean_delta_mp.to_numpy()
    lo = l.delta_mp_pop_boot_low.to_numpy()
    hi = l.delta_mp_pop_boot_high.to_numpy()
    passed = l.regime_lower_gt_0p25.astype(bool).to_numpy()

    for x, m, a, b, ok in zip(xs, means, lo, hi, passed):
        ax.errorbar(x, m, yerr=[[m-a], [b-m]], fmt='none', ecolor=BLACK,
                    elinewidth=1.05, capsize=2.7, capthick=0.9, zorder=3)
        ax.scatter([x], [m], s=34, marker='s',
                   facecolors=BLACK if ok else 'white', edgecolors=BLACK,
                   linewidths=1.05, zorder=4)

    ax.axhline(0, color=MID_GREY, lw=0.8, zorder=0)
    ax.axhline(0.25, color=MID_GREY, lw=0.8, ls='--', dashes=(4, 2.5), zorder=0)
    ax.set_xlim(0.55, 8.45)
    ax.set_ylim(*ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.set_xticks(np.arange(1, 9))
    ax.set_title(title, loc='left', pad=7)
    panel_label(ax, lab)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)




def main():
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.15), sharex=False)
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.105, top=0.855,
                        wspace=0.22, hspace=0.36)

    draw_panel(axes[0,0], *PANELS[0], 'a', (-0.25, 5.4), yticks=[0,1,2,3,4,5])
    draw_panel(axes[0,1], *PANELS[1], 'b', (-0.25, 7.2), yticks=[0,1,2,3,4,5,6,7])
    draw_panel(axes[1,0], *PANELS[2], 'c', (-0.25, 3.55), yticks=[0,0.5,1,1.5,2,2.5,3,3.5])
    draw_panel(axes[1,1], *PANELS[3], 'd', (-0.18, 0.86), yticks=[-0.1,0,0.25,0.5,0.75])

    axes[1,0].set_xlabel('Independent affinity landscape')
    axes[1,1].set_xlabel('Independent affinity landscape')

    fig.text(0.018, 0.465, r'MP future-fitness loss, $\Delta V_{\mathrm{MP}}$ (fitness units)',
             rotation=90, va='center', ha='center', fontsize=8.6)

    handles = [
        Line2D([0],[0], marker='o', linestyle='None', markerfacecolor='none', markeredgecolor=GREY,
               markersize=4.5, label='nested evolved population'),
        Line2D([0],[0], marker='s', linestyle='-', color=BLACK, markerfacecolor=BLACK,
               markeredgecolor=BLACK, markersize=5.2, linewidth=1.0, label='landscape mean ± 95% CI'),
        Line2D([0],[0], marker='s', linestyle='None', color=BLACK, markerfacecolor='white',
               markeredgecolor=BLACK, markersize=5.2, label='open square: lower CI ≤ 0.25'),
        Line2D([0],[0], color=MID_GREY, lw=0.8, ls='--', dashes=(4,2.5), label='practical threshold = 0.25'),
    ]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.992), ncol=2,
               frameon=False, handlelength=2.2, columnspacing=1.8, labelspacing=0.8)

    stem = 'Figure_6_MP_PRIMARY_v3_DECLUTTERED'
    pdf = OUT / f'{stem}.pdf'
    png = OUT / f'{stem}_600DPI.png'
    tif = OUT / f'{stem}_600DPI.tiff'
    fig.savefig(pdf, bbox_inches='tight')
    fig.savefig(png, dpi=600, bbox_inches='tight')
    fig.savefig(tif, dpi=600, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    main()
