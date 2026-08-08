from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd
from PIL import Image

# -----------------------------------------------------------------------------
# Paths and command-line options
# -----------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TABLE_DIR = SCRIPT_DIR / "source_tables"
DEFAULT_OUT_DIR = SCRIPT_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce publication-grade JRSI Figures 3-8 from frozen source tables."
    )
    parser.add_argument(
        "--table-dir",
        type=Path,
        default=DEFAULT_TABLE_DIR,
        help="Directory containing the eleven frozen figure-source CSV files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for figure exports and the figure manifest.",
    )
    return parser.parse_args()


# -----------------------------------------------------------------------------
# Figure style
# -----------------------------------------------------------------------------

# Okabe-Ito / Nature-recommended colour-blind-safe palette.
BLACK = "#111111"
DARK_GRAY = "#4D4D4D"
MID_GRAY = "#7A7A7A"
LIGHT_GRAY = "#B8B8B8"
PALE_GRAY = "#E7E7E7"
VERY_PALE_GRAY = "#F4F4F4"
WHITE = "#FFFFFF"
BLUE = "#0072B2"
SKY = "#56B4E9"
GREEN = "#009E73"
ORANGE = "#E69F00"
VERMILLION = "#D55E00"
PURPLE = "#CC79A7"
YELLOW = "#F0E442"


def lighten(colour: str, amount: float = 0.72) -> str:
    """Blend a colour toward white. amount=0 returns the original colour."""
    rgb = np.asarray(to_rgb(colour), dtype=float)
    out = rgb + (1.0 - rgb) * amount
    return mpl.colors.to_hex(np.clip(out, 0, 1))


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arimo", "Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "font.size": 7.1,
        "axes.titlesize": 7.3,
        "axes.titleweight": "normal",
        "axes.labelsize": 7.1,
        "axes.linewidth": 0.65,
        "axes.labelpad": 4.5,
        "xtick.labelsize": 6.4,
        "ytick.labelsize": 6.4,
        "legend.fontsize": 6.1,
        "lines.linewidth": 1.05,
        "lines.markersize": 4.0,
        "patch.linewidth": 0.65,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.minor.size": 1.8,
        "ytick.minor.size": 1.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "jrsi-publication-figures-v2",
        "savefig.bbox": None,
        "savefig.pad_inches": 0.02,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "mathtext.fontset": "dejavusans",
    }
)


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

TABLE_DIR: Path
OUT: Path


def load(name: str) -> pd.DataFrame:
    path = TABLE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing frozen source table: {path}")
    return pd.read_csv(path)


def stable_jitter(n: int, width: float) -> np.ndarray:
    if n <= 1:
        return np.zeros(n)
    base = np.linspace(-width, width, n)
    order = np.argsort(np.asarray([(i * 7) % n for i in range(n)]))
    return base[order]


def panel_label(
    ax: mpl.axes.Axes,
    letter: str,
    x: float = -0.15,
    y: float = 1.10,
    size: float = 8.5,
) -> None:
    ax.text(
        x,
        y,
        f"({letter})",
        transform=ax.transAxes,
        fontsize=size,
        fontweight="bold",
        fontstyle="normal",
        ha="left",
        va="top",
        clip_on=False,
        color=BLACK,
    )


def clean_ax(ax: mpl.axes.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BLACK)
    ax.spines["bottom"].set_color(BLACK)
    ax.tick_params(direction="out", colors=BLACK, pad=2.5)
    ax.grid(False)


def format_probability_axis(ax: mpl.axes.Axes) -> None:
    ticks = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    ax.set_xlim(0.065, 1.035)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{p:.1f}" for p in ticks])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_all(
    fig: mpl.figure.Figure,
    stem: str,
    size_inches: tuple[float, float],
) -> dict[str, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / f"{stem}.pdf"
    svg = OUT / f"{stem}.svg"
    eps = OUT / f"{stem}.eps"
    png = OUT / f"{stem}.png"
    tif = OUT / f"{stem}.tiff"

    metadata = {
        "Title": stem.replace("_", " "),
        "Author": "JRSI major-revision publication-figure production",
        "Subject": "Visualization of frozen quantitative source tables",
        "Keywords": "JRSI; Model B; publication figure; accessible colour; vector",
    }

    fig.savefig(pdf, metadata=metadata, facecolor="white")
    fig.savefig(
        svg,
        metadata={"Title": metadata["Title"], "Creator": metadata["Author"]},
        facecolor="white",
    )
    fig.savefig(eps, format="eps", facecolor="white")
    fig.savefig(png, dpi=600, facecolor="white")
    with Image.open(png) as image:
        rgb = image.convert("RGB")
        rgb.save(tif, compression="tiff_lzw", dpi=(600, 600))
    plt.close(fig)

    return {
        "pdf": pdf.name,
        "svg": svg.name,
        "eps": eps.name,
        "png": png.name,
        "tiff": tif.name,
        "width_inches": f"{size_inches[0]:.2f}",
        "height_inches": f"{size_inches[1]:.2f}",
    }


def build_manifest(records: dict[str, dict[str, str]]) -> None:
    rows: list[dict[str, object]] = []
    for figure_name, record in records.items():
        for fmt in ["pdf", "svg", "eps", "png", "tiff"]:
            path = OUT / record[fmt]
            width_px: int | str = ""
            height_px: int | str = ""
            mode = ""
            if fmt in {"png", "tiff"}:
                with Image.open(path) as image:
                    width_px, height_px = image.size
                    mode = image.mode
            rows.append(
                {
                    "figure": figure_name,
                    "filename": path.name,
                    "format": fmt,
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "width_inches": record["width_inches"],
                    "height_inches": record["height_inches"],
                    "width_pixels": width_px,
                    "height_pixels": height_px,
                    "resolution_dpi": 600 if fmt in {"png", "tiff"} else "vector",
                    "colour_mode": mode if mode else "vector RGB",
                }
            )
    pd.DataFrame(rows).to_csv(OUT / "PUBLICATION_GRADE_FIGURE_MANIFEST.csv", index=False)


# -----------------------------------------------------------------------------
# Figure 3 - corrected information hierarchy
# -----------------------------------------------------------------------------

CONDITION_STYLE = {
    "control": {
        "label": "Sequence-agnostic",
        "marker": "o",
        "colour": ORANGE,
        "face": WHITE,
        "line": "--",
    },
    "selective": {
        "label": "Sequence-selective",
        "marker": "s",
        "colour": BLUE,
        "face": BLUE,
        "line": "-",
    },
}


def draw_raw_summary_panel(
    ax: mpl.axes.Axes,
    frame: pd.DataFrame,
    metric: str,
    ylabel: str,
    title: str,
    yzero: bool = False,
    summary_frame: pd.DataFrame | None = None,
) -> None:
    offsets = {"control": -0.016, "selective": 0.016}
    probabilities = sorted(frame["inherit_prob"].unique())

    for condition in ["control", "selective"]:
        style = CONDITION_STYLE[condition]
        subset = frame[frame["condition"] == condition]
        means: list[float] = []
        lows: list[float] = []
        highs: list[float] = []

        for probability in probabilities:
            values = subset.loc[subset["inherit_prob"] == probability, metric].to_numpy(float)
            jitter = stable_jitter(len(values), 0.009)
            ax.scatter(
                np.full(len(values), probability + offsets[condition]) + jitter,
                values,
                s=9.5,
                marker=style["marker"],
                facecolors=lighten(style["colour"], 0.76) if condition == "selective" else WHITE,
                edgecolors=style["colour"],
                linewidths=0.45,
                zorder=2,
            )
            means.append(float(np.mean(values)))

            if summary_frame is not None:
                row = summary_frame[
                    (summary_frame["inherit_prob"] == probability)
                    & (summary_frame["condition"] == condition)
                ]
                if len(row) == 1:
                    lows.append(float(row.iloc[0]["lower"]))
                    highs.append(float(row.iloc[0]["upper"]))
                else:
                    lows.append(np.nan)
                    highs.append(np.nan)

        x_line = np.asarray(probabilities) + offsets[condition]
        ax.plot(
            x_line,
            means,
            linestyle=style["line"],
            color=style["colour"],
            marker=style["marker"],
            markerfacecolor=style["face"],
            markeredgecolor=style["colour"],
            markeredgewidth=0.65,
            markersize=3.6,
            linewidth=1.35,
            zorder=4,
            label=style["label"],
        )

        if summary_frame is not None and np.isfinite(lows).all() and np.isfinite(highs).all():
            mean_array = np.asarray(means)
            ax.errorbar(
                x_line,
                mean_array,
                yerr=[mean_array - np.asarray(lows), np.asarray(highs) - mean_array],
                fmt="none",
                ecolor=style["colour"],
                elinewidth=0.8,
                capsize=1.8,
                capthick=0.8,
                zorder=3,
            )

    if yzero:
        ax.axhline(0, color=LIGHT_GRAY, lw=0.7, zorder=0)
    ax.set_title(title, loc="left", pad=5)
    ax.set_xlabel("Compositional-coupling probability, $p$")
    ax.set_ylabel(ylabel)
    format_probability_axis(ax)
    clean_ax(ax)


def figure3() -> dict[str, str]:
    information = load("core_information_replicates.csv")
    semantic = load("core_semantic_replicates.csv")
    inference = load("core_inference_records.csv")
    value_intervals = inference[
        (inference["record_type"] == "block_bootstrap_interval")
        & (inference["metric"] == "mean_value_of_information")
    ].copy()

    size = (7.20, 6.18)
    fig, axes = plt.subplots(2, 2, figsize=size)
    fig.subplots_adjust(
        left=0.105,
        right=0.985,
        bottom=0.095,
        top=0.905,
        wspace=0.30,
        hspace=0.40,
    )

    draw_raw_summary_panel(
        axes[0, 0],
        information,
        "total_information",
        "Total association, $I(M;Z)$ (bits)",
        "Total motif-local-state association",
    )
    panel_label(axes[0, 0], "a")

    draw_raw_summary_panel(
        axes[0, 1],
        information,
        "positional_information",
        "Positional association, $I(M;S)$ (bits)",
        "Motif-position association",
    )
    panel_label(axes[0, 1], "b")

    draw_raw_summary_panel(
        axes[1, 0],
        information,
        "corrected_conditional_information",
        r"Corrected $I(M;Z\mid S)$ (bits)",
        "Position-conditioned sequence-specific information",
        yzero=True,
    )
    panel_label(axes[1, 0], "c")

    draw_raw_summary_panel(
        axes[1, 1],
        semantic,
        "value_of_information",
        r"Value of information, $\Delta V$ (fitness units)",
        "Future-fitness effect of complete grouping",
        yzero=True,
        summary_frame=value_intervals,
    )
    panel_label(axes[1, 1], "d")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=2,
        frameon=False,
        handlelength=2.6,
        columnspacing=2.0,
    )
    fig.align_ylabels(axes[:, 0])
    fig.align_ylabels(axes[:, 1])
    return save_all(fig, "FIGURE_3_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure 4 - information-fitness frontiers and semantic estimates
# -----------------------------------------------------------------------------

METHOD_STYLE = {
    "constant": {"marker": "P", "colour": DARK_GRAY, "face": WHITE, "label": "Constant endpoint"},
    "balanced_random_group": {"marker": "o", "colour": SKY, "face": WHITE, "label": "Balanced-random"},
    "affinity_rank_group": {"marker": "^", "colour": BLUE, "face": WHITE, "label": "Affinity-rank"},
    "contiguous_substring": {"marker": "s", "colour": ORANGE, "face": lighten(ORANGE, 0.72), "label": "Contiguous-substring"},
    "identity": {"marker": "D", "colour": VERMILLION, "face": VERMILLION, "label": "Identity endpoint"},
}


def plot_frontier(
    ax: mpl.axes.Axes,
    points: pd.DataFrame,
    semantic_row: pd.Series,
    title: str,
    common_xlim: tuple[float, float],
    common_ylim: tuple[float, float],
) -> None:
    points = points.sort_values("retained_information").copy()
    for method, subset in points.groupby("point_method", sort=False):
        style = METHOD_STYLE[method]
        ax.scatter(
            subset["retained_information"],
            subset["point_viability"],
            s=25 if method in {"constant", "identity"} else 18,
            marker=style["marker"],
            facecolors=style["face"],
            edgecolors=style["colour"],
            linewidths=0.75,
            zorder=3,
        )

    frontier = (
        points[["retained_information", "frontier_viability"]]
        .drop_duplicates()
        .sort_values("retained_information")
    )
    ax.step(
        frontier["retained_information"],
        frontier["frontier_viability"],
        where="post",
        color=BLACK,
        lw=1.25,
        zorder=2,
    )

    actual = float(semantic_row["actual_viability"])
    target = float(semantic_row["target_viability"])
    semantic = float(semantic_row["semantic_information"])
    ax.axhline(actual, color=MID_GRAY, lw=0.8, ls=":", zorder=1)
    ax.axhline(target, color=VERMILLION, lw=0.9, ls="--", zorder=1)
    ax.axvline(semantic, color=BLUE, lw=0.9, ls="-.", zorder=1)

    ax.set_title(title, loc="left", pad=5)
    ax.set_xlabel(r"Retained information, $I(g(M);Z\mid S)$ (bits)")
    ax.set_ylabel("Mean future model fitness")
    ax.set_xlim(*common_xlim)
    ax.set_ylim(*common_ylim)
    clean_ax(ax)


def categorical_raw_summary(
    ax: mpl.axes.Axes,
    frame: pd.DataFrame,
    metric: str,
    summary_metric: str,
    ylabel: str,
    title: str,
    inference: pd.DataFrame,
    summary_marker: str,
) -> None:
    for x, condition in enumerate(["control", "selective"]):
        style = CONDITION_STYLE[condition]
        values = frame[frame["condition"] == condition][metric].to_numpy(float)
        jitter = stable_jitter(len(values), 0.12)
        ax.scatter(
            np.full(len(values), x) + jitter,
            values,
            s=18,
            marker=style["marker"],
            facecolors=lighten(style["colour"], 0.76) if condition == "selective" else WHITE,
            edgecolors=style["colour"],
            linewidths=0.55,
            zorder=2,
        )
        row = inference[
            (inference["record_type"] == "block_bootstrap_interval")
            & (inference["metric"] == summary_metric)
            & (inference["condition"] == condition)
            & (inference["inherit_prob"] == 1.0)
        ]
        if len(row) == 1:
            result = row.iloc[0]
            estimate = float(result["estimate"])
            lower = float(result["lower"])
            upper = float(result["upper"])
            ax.errorbar(
                [x],
                [estimate],
                yerr=[[estimate - lower], [upper - estimate]],
                fmt=summary_marker,
                color=style["colour"],
                markerfacecolor=style["colour"] if condition == "selective" else WHITE,
                markeredgecolor=style["colour"],
                markeredgewidth=0.8,
                markersize=5.0,
                capsize=2.6,
                elinewidth=1.05,
                capthick=1.0,
                zorder=4,
            )

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Sequence-\nagnostic", "Sequence-\nselective"])
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", pad=5)
    ax.axhline(0, color=LIGHT_GRAY, lw=0.7, zorder=0)
    clean_ax(ax)


def figure4() -> dict[str, str]:
    points = load("core_frontier_points.csv")
    semantic = load("core_semantic_replicates.csv")
    inference = load("core_inference_records.csv")

    selective_id = "selective_p1.0_r00"
    control_id = "control_p1.0_r00"
    selective_points = points[points["baseline_replicate"] == selective_id]
    control_points = points[points["baseline_replicate"] == control_id]
    selective_row = semantic[semantic["baseline_replicate"] == selective_id].iloc[0]
    control_row = semantic[semantic["baseline_replicate"] == control_id].iloc[0]
    semantic_p1 = semantic[semantic["inherit_prob"] == 1.0]

    xmax = max(
        float(selective_points["retained_information"].max()),
        float(control_points["retained_information"].max()),
    ) * 1.06
    ymin = min(
        float(selective_points["point_viability"].min()),
        float(control_points["point_viability"].min()),
    ) - 0.8
    ymax = max(
        float(selective_points["point_viability"].max()),
        float(control_points["point_viability"].max()),
    ) + 0.8

    size = (7.20, 6.45)
    fig = plt.figure(figsize=size)
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.10, 0.86],
        left=0.095,
        right=0.985,
        bottom=0.095,
        top=0.875,
        wspace=0.28,
        hspace=0.48,
    )
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[1, 0])
    ax_d = fig.add_subplot(grid[1, 1])

    plot_frontier(
        ax_a,
        selective_points,
        selective_row,
        "Sequence-selective frontier ($p=1.0$)",
        (0, xmax),
        (ymin, ymax),
    )
    plot_frontier(
        ax_b,
        control_points,
        control_row,
        "Sequence-agnostic frontier ($p=1.0$)",
        (0, xmax),
        (ymin, ymax),
    )
    panel_label(ax_a, "a")
    panel_label(ax_b, "b")

    categorical_raw_summary(
        ax_c,
        semantic_p1,
        "value_of_information",
        "mean_value_of_information",
        r"$\Delta V$ (fitness units)",
        "Value of information",
        inference,
        summary_marker="s",
    )
    panel_label(ax_c, "c", x=-0.16, y=1.10)

    categorical_raw_summary(
        ax_d,
        semantic_p1,
        "semantic_information",
        "median_semantic_information_among_reached",
        r"$I_{\mathrm{sem},r}$ (bits)",
        "Replicate-specific semantic estimate",
        inference,
        summary_marker="D",
    )
    panel_label(ax_d, "d", x=-0.16, y=1.10)

    method_handles: list[Line2D] = []
    for method in [
        "constant",
        "balanced_random_group",
        "affinity_rank_group",
        "contiguous_substring",
        "identity",
    ]:
        style = METHOD_STYLE[method]
        method_handles.append(
            Line2D(
                [0],
                [0],
                marker=style["marker"],
                color="none",
                markerfacecolor=style["face"],
                markeredgecolor=style["colour"],
                markeredgewidth=0.75,
                label=style["label"],
                markersize=5,
            )
        )
    fig.legend(
        method_handles,
        [handle.get_label() for handle in method_handles],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        frameon=False,
        columnspacing=1.0,
        handletextpad=0.4,
    )

    line_handles = [
        Line2D([0], [0], color=BLACK, lw=1.25, drawstyle="steps-post", label="Cumulative upper frontier"),
        Line2D([0], [0], color=MID_GRAY, lw=0.8, ls=":", label="Actual endpoint"),
        Line2D([0], [0], color=VERMILLION, lw=0.9, ls="--", label="Strict 1% target"),
        Line2D([0], [0], color=BLUE, lw=0.9, ls="-.", label="First target-reaching coordinate"),
    ]
    ax_b.legend(
        handles=line_handles,
        loc="upper right",
        frameon=False,
        fontsize=5.7,
        handlelength=2.4,
        borderaxespad=0.3,
    )
    return save_all(fig, "FIGURE_4_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure 5 - selection dependence and mapping specificity
# -----------------------------------------------------------------------------

CONTRASTS = [
    ("full_minus_neutral", "native_full_voi", "selection_neutral", "Full\nselection", "Neutral", "Neutral-selection control"),
    ("full_minus_reduced", "native_full_voi", "selection_reduced", "Full\nselection", "Reduced\nselection", "Reduced-selection control"),
    ("native_minus_affinity_reassigned", "native_full_voi", "affinity_reassigned", "Native\nmapping", "Affinity\nreassigned", "Affinity-profile reassignment"),
    ("native_minus_topology_mismatch", "native_full_voi", "topology_mismatch", "Native\ntopology", "Topology\nmismatch", "Topology mismatch"),
    ("alternative_native_minus_cross", "alternative_native_mean", "alternative_cross_mean", "Alternative\nnative", "Cross-\nevaluated", "Cross-topology evaluation"),
    ("stable_minus_unstable", "alternative_native_mean", "temporally_unstable", "Stable\nfixed", "Temporally\nunstable", "Temporally unstable topology"),
]


def figure5() -> dict[str, str]:
    blocks = load("causal_specificity_seed_blocks.csv")
    contrasts = load("causal_specificity_contrasts.csv").set_index("contrast")
    wide = blocks.pivot(index="seed_block", columns="control_or_reference", values="value_of_information")

    size = (7.20, 7.42)
    fig = plt.figure(figsize=size)
    outer = fig.add_gridspec(
        2,
        3,
        height_ratios=[1.22, 0.86],
        width_ratios=[1, 1, 1.08],
        left=0.132,
        right=0.985,
        bottom=0.075,
        top=0.945,
        wspace=0.34,
        hspace=0.42,
    )
    top = outer[0, :].subgridspec(2, 3, wspace=0.32, hspace=0.62)

    mini_axes: list[mpl.axes.Axes] = []
    for index, (contrast_id, reference, control, reference_label, control_label, title) in enumerate(CONTRASTS):
        ax = fig.add_subplot(top[index // 3, index % 3])
        mini_axes.append(ax)
        reference_values = wide[reference].to_numpy(float)
        control_values = wide[control].to_numpy(float)

        for left_value, right_value in zip(reference_values, control_values):
            ax.plot([0, 1], [left_value, right_value], color=LIGHT_GRAY, lw=0.65, zorder=1)
        ax.scatter(
            np.zeros(len(reference_values)),
            reference_values,
            s=16,
            marker="s",
            facecolors=lighten(BLUE, 0.55),
            edgecolors=BLUE,
            linewidths=0.55,
            zorder=3,
        )
        ax.scatter(
            np.ones(len(control_values)),
            control_values,
            s=16,
            marker="o",
            facecolors=WHITE,
            edgecolors=ORANGE,
            linewidths=0.65,
            zorder=3,
        )
        ax.plot([-0.14, 0.14], [np.mean(reference_values)] * 2, color=BLUE, lw=1.8, zorder=4)
        ax.plot([0.86, 1.14], [np.mean(control_values)] * 2, color=ORANGE, lw=1.8, zorder=4)

        ax.set_xlim(-0.35, 1.35)
        ax.set_ylim(0, 15.6)
        ax.set_xticks([0, 1])
        ax.set_xticklabels([reference_label, control_label], fontsize=6.1)
        if index % 3 == 0:
            ax.set_ylabel(r"$\Delta V$ (fitness units)")
        else:
            ax.tick_params(labelleft=False)
        ax.set_title(title, loc="left", fontsize=7.0, pad=4)
        panel_label(ax, chr(ord("a") + index), x=-0.19 if index % 3 == 0 else -0.13, y=1.14, size=8.1)
        clean_ax(ax)

    ax_forest = fig.add_subplot(outer[1, :2])
    contrast_order = [item[0] for item in CONTRASTS]
    display_labels = [
        "Full - neutral",
        "Full - reduced",
        "Native - reassigned",
        "Native - mismatch",
        "Alt. native - cross",
        "Stable - unstable",
    ]
    category_colours = [BLUE, BLUE, PURPLE, GREEN, GREEN, ORANGE]
    y_positions = np.arange(len(contrast_order))[::-1]
    estimates = contrasts.loc[contrast_order, "mean_difference"].to_numpy(float)
    lower = contrasts.loc[contrast_order, "bootstrap_95_lower"].to_numpy(float)
    upper = contrasts.loc[contrast_order, "bootstrap_95_upper"].to_numpy(float)

    ax_forest.axvline(0, color=LIGHT_GRAY, lw=0.8, zorder=0)
    for y, estimate, low, high, colour in zip(y_positions, estimates, lower, upper, category_colours):
        ax_forest.errorbar(
            estimate,
            y,
            xerr=[[estimate - low], [high - estimate]],
            fmt="s",
            color=colour,
            markerfacecolor=colour,
            markeredgecolor=colour,
            markersize=4.4,
            capsize=2.5,
            elinewidth=1.1,
            capthick=1.0,
            zorder=3,
        )
    ax_forest.set_yticks(y_positions)
    ax_forest.set_yticklabels(display_labels)
    ax_forest.set_xlabel("Paired mean difference in value of information (fitness units)")
    ax_forest.set_xlim(-0.25, 8.8)
    ax_forest.set_title("Six prespecified paired contrasts", loc="left", pad=5)
    panel_label(ax_forest, "g", x=-0.12, y=1.10)
    ax_forest.text(
        0.985,
        1.035,
        "BH-adjusted $q$",
        transform=ax_forest.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.0,
    )
    for y, contrast_id in zip(y_positions, contrast_order):
        q_value = float(contrasts.loc[contrast_id, "q_value_bh_six_contrasts"])
        ax_forest.text(8.68, y, f"{q_value:.4f}", ha="right", va="center", fontsize=6.1)
    clean_ax(ax_forest)

    ax_model = fig.add_subplot(outer[1, 2])
    ax_model.set_axis_off()
    panel_label(ax_model, "h", x=-0.15, y=1.10)
    ax_model.text(0.02, 1.01, "Causal interpretation", transform=ax_model.transAxes, fontsize=7.3, va="bottom")

    def box(
        x: float,
        y: float,
        width: float,
        height: float,
        text: str,
        face: str,
        edge: str,
        fontsize: float = 6.4,
        linewidth: float = 0.9,
    ) -> None:
        patch = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.018,rounding_size=0.014",
            transform=ax_model.transAxes,
            facecolor=face,
            edgecolor=edge,
            linewidth=linewidth,
        )
        ax_model.add_patch(patch)
        ax_model.text(
            x + width / 2,
            y + height / 2,
            text,
            transform=ax_model.transAxes,
            ha="center",
            va="center",
            fontsize=fontsize,
            color=BLACK,
        )

    box(0.07, 0.75, 0.86, 0.15, "Built-in architecture\naffinity -> local state -> fitness", VERY_PALE_GRAY, DARK_GRAY)
    box(0.07, 0.53, 0.86, 0.14, "Full selection + stable\nnative mapping", lighten(BLUE, 0.84), BLUE)
    ax_model.add_patch(
        FancyArrowPatch(
            (0.50, 0.53),
            (0.50, 0.43),
            transform=ax_model.transAxes,
            arrowstyle="-|>",
            mutation_scale=9,
            lw=0.9,
            color=BLACK,
        )
    )
    box(0.10, 0.27, 0.80, 0.14, "Additional mapping-specific\nvalue-of-information component", lighten(GREEN, 0.84), GREEN)
    box(0.06, 0.05, 0.88, 0.13, "Attenuated by weakened selection,\nreassignment, mismatch, cross-evaluation,\nor temporal instability", lighten(ORANGE, 0.88), ORANGE, fontsize=5.9)

    return save_all(fig, "FIGURE_5_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figures 6-8 - generality analyses split from the former crowded Figure 6
# -----------------------------------------------------------------------------

REGIME_ORDER = [
    "R0_null",
    "R1_syntactic_only",
    "boundary_uncertain",
    "R2_viability_relevant",
    "R3_strong_adaptation",
]
REGIME_LABEL = {
    "R0_null": "Null",
    "R1_syntactic_only": "Syntactic-only",
    "boundary_uncertain": "Boundary / uncertain",
    "R2_viability_relevant": "Viability-relevant",
    "R3_strong_adaptation": "Strong adaptation",
}
REGIME_STYLE = {
    "R0_null": {"marker": "x", "colour": DARK_GRAY, "face": DARK_GRAY},
    "R1_syntactic_only": {"marker": "o", "colour": SKY, "face": WHITE},
    "boundary_uncertain": {"marker": "D", "colour": ORANGE, "face": lighten(ORANGE, 0.52)},
    "R2_viability_relevant": {"marker": "s", "colour": GREEN, "face": GREEN},
    "R3_strong_adaptation": {"marker": "*", "colour": PURPLE, "face": PURPLE},
}


def parse_spec(value: str) -> dict[str, object]:
    return json.loads(value)


def regime_handles() -> list[Line2D]:
    handles: list[Line2D] = []
    for regime in REGIME_ORDER:
        style = REGIME_STYLE[regime]
        handles.append(
            Line2D(
                [0],
                [0],
                marker=style["marker"],
                color="none" if regime != "R0_null" else style["colour"],
                markerfacecolor=style["face"],
                markeredgecolor=style["colour"],
                markeredgewidth=0.8,
                linestyle="none",
                label=REGIME_LABEL[regime],
                markersize=5.6,
            )
        )
    return handles


def figure6() -> dict[str, str]:
    summary = load("generality_screen_summary.csv")
    stage_a = summary[summary["stage"] == "A"].copy()
    stage_a["spec"] = stage_a["spec_json"].map(parse_spec)
    stage_a["p_value"] = stage_a["spec"].map(lambda item: float(item["p"]))
    stage_a["sigma_ratio_value"] = stage_a["spec"].map(lambda item: float(item["sigma_ratio"]))
    stage_a["b_ratio_value"] = stage_a["spec"].map(lambda item: float(item["b_ratio"]))

    size = (7.20, 5.20)
    fig, axes = plt.subplots(2, 2, figsize=size)
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.105, top=0.875, wspace=0.33, hspace=0.47)

    ratios = [0.5, 1.6666666666666667, 2.5]
    for index, ratio in enumerate(ratios):
        ax = axes.flat[index]
        data = stage_a[np.isclose(stage_a["b_ratio_value"], ratio)]
        for regime in REGIME_ORDER:
            subset = data[data["regime"] == regime]
            if subset.empty:
                continue
            style = REGIME_STYLE[regime]
            if regime == "R0_null":
                ax.scatter(
                    subset["p_value"],
                    subset["sigma_ratio_value"],
                    s=44,
                    marker=style["marker"],
                    color=style["colour"],
                    linewidths=1.0,
                    zorder=3,
                )
            else:
                ax.scatter(
                    subset["p_value"],
                    subset["sigma_ratio_value"],
                    s=44,
                    marker=style["marker"],
                    facecolors=style["face"],
                    edgecolors=style["colour"],
                    linewidths=0.85,
                    zorder=3,
                )
        ax.set_xlim(0.36, 1.04)
        ax.set_ylim(-0.06, 1.48)
        ax.set_xticks([0.4, 0.6, 0.8, 1.0])
        ax.set_xlabel("Compositional coupling, $p$")
        if index in {0, 2}:
            ax.set_ylabel(r"Affinity-to-noise ratio, $\sigma_a/\Theta$")
        else:
            ax.tick_params(labelleft=False)
        ax.set_title(rf"Positional-bias ratio, $\beta/\Theta={ratio:.2g}$", loc="left", pad=5)
        panel_label(ax, chr(ord("a") + index), x=-0.16, y=1.10)
        clean_ax(ax)

    ax_bar = axes.flat[3]
    stage_counts: dict[str, list[int]] = {}
    for stage_name in ["A", "B1"]:
        values = summary[summary["stage"] == stage_name]["regime"].value_counts()
        stage_counts[stage_name] = [int(values.get(regime, 0)) for regime in REGIME_ORDER]

    y_positions = [1, 0]
    for y, stage_name in zip(y_positions, ["A", "B1"]):
        values = stage_counts[stage_name]
        total = sum(values)
        left = 0.0
        for regime, value in zip(REGIME_ORDER, values):
            if value == 0:
                continue
            style = REGIME_STYLE[regime]
            fraction = value / total
            ax_bar.barh(
                y,
                fraction,
                left=left,
                height=0.42,
                color=style["face"] if regime != "R0_null" else WHITE,
                edgecolor=style["colour"],
                linewidth=0.75,
            )
            if fraction >= 0.08:
                text_colour = WHITE if regime in {"R2_viability_relevant", "R3_strong_adaptation"} else BLACK
                ax_bar.text(left + fraction / 2, y, str(value), ha="center", va="center", fontsize=6.4, color=text_colour)
            left += fraction

    ax_bar.set_xlim(0, 1)
    ax_bar.set_ylim(-0.65, 1.65)
    ax_bar.set_yticks(y_positions)
    ax_bar.set_yticklabels(["Stage A (32 settings)", "Stage B1 (16 settings)"])
    ax_bar.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_bar.set_xticklabels(["0", "25", "50", "75", "100%"])
    ax_bar.set_xlabel("Proportion of tested settings")
    ax_bar.set_title("Prespecified screen composition", loc="left", pad=5)
    panel_label(ax_bar, "d", x=-0.16, y=1.10)
    clean_ax(ax_bar)

    handles = regime_handles()
    fig.legend(
        handles,
        [handle.get_label() for handle in handles],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        frameon=False,
        columnspacing=1.35,
        handletextpad=0.4,
    )
    return save_all(fig, "FIGURE_6_PUBLICATION_GRADE", size)


B2_LABELS = {
    "B2_stride2": "Stride 2",
    "B2_stride5": "Stride 5",
    "B2_stride7": "Stride 7",
    "B2_seg2": "2 segments",
    "B2_seg8": "8 segments",
    "B2_reverse": "Reversed order",
    "B2_jitter": "Boundary jitter",
    "B2_met3": "3 local states",
    "B2_met6": "6 local states",
    "B2_reward1": r"$\omega_+=1$",
    "B2_reward3": r"$\omega_+=3$",
    "B2_penaltylow": r"$\omega_-/\omega_+=0.1$",
    "B2_penaltyhigh": r"$\omega_-/\omega_+=0.5$",
    "B2_floor0": r"$F_{\min}=0$",
    "B2_floor1": r"$F_{\min}=1$",
    "B2_fraction": "Fraction-normalized",
}
B2_ORDER = {
    "window": ["B2_stride2", "B2_stride5", "B2_stride7"],
    "position": ["B2_seg2", "B2_seg8", "B2_reverse", "B2_jitter"],
    "metabolite": ["B2_met3", "B2_met6"],
    "fitness": [
        "B2_reward1",
        "B2_reward3",
        "B2_penaltylow",
        "B2_penaltyhigh",
        "B2_floor0",
        "B2_floor1",
        "B2_fraction",
    ],
}


def figure7() -> dict[str, str]:
    summary = load("generality_screen_summary.csv")
    replicates = load("generality_screen_replicates.csv")
    default_mean = float(summary[summary["design_id"] == "B2_default"]["value_of_information_mean"].iloc[0])

    size = (7.20, 5.35)
    fig, axes = plt.subplots(2, 2, figsize=size)
    fig.subplots_adjust(left=0.165, right=0.985, bottom=0.125, top=0.865, wspace=0.42, hspace=0.43)

    families = [
        ("window", "Window density"),
        ("position", "Positional structure"),
        ("metabolite", "Local-state count"),
        ("fitness", "Fitness formulation and scale"),
    ]

    for index, (family, title) in enumerate(families):
        ax = axes.flat[index]
        subset = summary[(summary["stage"] == "B2") & (summary["family"] == family)].copy()
        order = [design_id for design_id in B2_ORDER[family] if design_id in set(subset["design_id"])]
        subset["display_order"] = subset["design_id"].map({design_id: position for position, design_id in enumerate(order)})
        subset = subset.sort_values("display_order")
        y_positions = np.arange(len(subset))[::-1]

        ax.axvline(0.25, color=DARK_GRAY, ls="--", lw=0.75, zorder=0)
        ax.axvline(default_mean, color=MID_GRAY, ls=":", lw=0.8, zorder=0)

        for y, (_, row) in zip(y_positions, subset.iterrows()):
            design_id = row["design_id"]
            raw = replicates[
                (replicates["stage"] == "B2") & (replicates["design_id"] == design_id)
            ]["value_of_information"].to_numpy(float)
            ax.scatter(
                raw,
                np.full(len(raw), y) + stable_jitter(len(raw), 0.10),
                s=13,
                marker="o",
                facecolors=WHITE,
                edgecolors=LIGHT_GRAY,
                linewidths=0.5,
                zorder=1,
            )
            regime = row["regime"]
            style = REGIME_STYLE[regime]
            estimate = float(row["value_of_information_mean"])
            lower = float(row["value_of_information_low"])
            upper = float(row["value_of_information_high"])
            ax.errorbar(
                estimate,
                y,
                xerr=[[estimate - lower], [upper - estimate]],
                fmt=style["marker"],
                color=style["colour"],
                markerfacecolor=style["face"],
                markeredgecolor=style["colour"],
                markeredgewidth=0.8,
                markersize=5.2,
                capsize=2.0,
                elinewidth=0.9,
                capthick=0.9,
                zorder=3,
            )

        ax.set_yticks(y_positions)
        ax.set_yticklabels([B2_LABELS.get(value, value) for value in subset["design_id"]])
        ax.set_xlim(-0.45, 23.4)
        ax.set_title(title, loc="left", pad=5)
        panel_label(ax, chr(ord("a") + index), x=-0.23 if index % 2 == 0 else -0.18, y=1.10)
        clean_ax(ax)

    fig.supxlabel(r"Value of information, $\Delta V$ (fitness units)", y=0.035, fontsize=7.1)
    handles = regime_handles()
    fig.legend(
        handles,
        [handle.get_label() for handle in handles],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        frameon=False,
        columnspacing=1.35,
        handletextpad=0.4,
    )
    return save_all(fig, "FIGURE_7_PUBLICATION_GRADE", size)


def protocol_order(row: pd.Series) -> tuple[int, int]:
    design_id = str(row["design_id"])
    if "_g" in design_id:
        value = int(design_id.split("_g")[1].split("_")[0])
        return (0, value)
    value = int(design_id.split("_h")[1].split("_")[0])
    return (1, value)


def draw_protocol_panel(
    ax: mpl.axes.Axes,
    protocol: pd.DataFrame,
    suffix: str,
    title: str,
    ylim: tuple[float, float],
    show_threshold: bool,
) -> None:
    subset = protocol[protocol["design_id"].str.endswith(suffix)].copy()
    subset[["kind_order", "numeric_value"]] = subset.apply(lambda row: pd.Series(protocol_order(row)), axis=1)
    subset = subset.sort_values(["kind_order", "numeric_value"])
    x_positions = np.asarray([0, 1, 2, 4, 5, 6], dtype=float)

    for x, (_, row) in zip(x_positions, subset.iterrows()):
        style = REGIME_STYLE[row["regime"]]
        estimate = float(row["value_of_information_mean"])
        lower = float(row["value_of_information_low"])
        upper = float(row["value_of_information_high"])
        ax.errorbar(
            x,
            estimate,
            yerr=[[estimate - lower], [upper - estimate]],
            fmt=style["marker"],
            color=style["colour"],
            markerfacecolor=style["face"],
            markeredgecolor=style["colour"],
            markeredgewidth=0.8,
            markersize=5.2,
            capsize=2.1,
            elinewidth=0.9,
            capthick=0.9,
            zorder=3,
        )
    if show_threshold:
        ax.axhline(0.25, color=DARK_GRAY, ls="--", lw=0.75, zorder=0)
    ax.axvline(3, color=PALE_GRAY, lw=0.8, zorder=0)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([str(int(value)) for value in subset["numeric_value"]])
    ax.set_xlim(-0.55, 6.55)
    ax.set_ylim(*ylim)
    ax.set_ylabel(r"$\Delta V$ (fitness units)")
    ax.set_xlabel("Generations", labelpad=22)
    ax.set_title(title, loc="left", pad=5)
    ax.text(1, -0.17, r"Evolution duration, $T_{\mathrm{evo}}$", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=5.9)
    ax.text(5, -0.17, r"Intervention horizon, $\tau_{\mathrm{int}}$", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=5.9)
    clean_ax(ax)


def figure8() -> dict[str, str]:
    confirmatory_summary = load("generality_confirmatory_summary.csv")
    confirmatory_replicates = load("generality_confirmatory_replicates.csv")
    protocol = load("generality_protocol_summary.csv")
    core_semantic = load("core_semantic_replicates.csv")
    core_inference = load("core_inference_records.csv")

    size = (7.20, 5.78)
    fig = plt.figure(figsize=size)
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 0.90],
        left=0.095,
        right=0.985,
        bottom=0.165,
        top=0.865,
        wspace=0.30,
        hspace=0.53,
    )
    ax_a = fig.add_subplot(grid[0, :])
    ax_b = fig.add_subplot(grid[1, 0])
    ax_c = fig.add_subplot(grid[1, 1])

    default_raw = core_semantic[
        (core_semantic["condition"] == "selective") & (core_semantic["inherit_prob"] == 1.0)
    ]["value_of_information"].to_numpy(float)
    default_ci = core_inference[
        (core_inference["record_type"] == "block_bootstrap_interval")
        & (core_inference["metric"] == "mean_value_of_information")
        & (core_inference["condition"] == "selective")
        & (core_inference["inherit_prob"] == 1.0)
    ].iloc[0]

    groups: list[tuple[str, np.ndarray, float, float, float, str]] = [
        (
            "Default\n($n=20$)",
            default_raw,
            float(default_ci["estimate"]),
            float(default_ci["lower"]),
            float(default_ci["upper"]),
            "R3_strong_adaptation",
        )
    ]
    label_map = {
        "D0": "A_high_2\n($n=8$)",
        "D1": "B2_reward3\n($n=8$)",
        "D2": "A_low_3\n($n=8$)",
    }
    regime_map = {
        "D0": "R2_viability_relevant",
        "D1": "R3_strong_adaptation",
        "D2": "boundary_uncertain",
    }
    for confirm_id in ["D0", "D1", "D2"]:
        raw = confirmatory_replicates[
            confirmatory_replicates["confirm_id"] == confirm_id
        ]["value_of_information"].to_numpy(float)
        row = confirmatory_summary[confirmatory_summary["confirm_id"] == confirm_id].iloc[0]
        groups.append(
            (
                label_map[confirm_id],
                raw,
                float(row["voi_mean"]),
                float(row["voi_low"]),
                float(row["voi_high"]),
                regime_map[confirm_id],
            )
        )

    for x, (label, raw, estimate, lower, upper, regime) in enumerate(groups):
        ax_a.scatter(
            np.full(len(raw), x) + stable_jitter(len(raw), 0.12),
            raw,
            s=17,
            marker="o",
            facecolors=WHITE,
            edgecolors=LIGHT_GRAY,
            linewidths=0.5,
            zorder=1,
        )
        style = REGIME_STYLE[regime]
        ax_a.errorbar(
            x,
            estimate,
            yerr=[[estimate - lower], [upper - estimate]],
            fmt=style["marker"],
            color=style["colour"],
            markerfacecolor=style["face"],
            markeredgecolor=style["colour"],
            markeredgewidth=0.8,
            markersize=6.0,
            capsize=2.5,
            elinewidth=1.0,
            capthick=0.95,
            zorder=3,
        )
    ax_a.axhline(0.25, color=DARK_GRAY, ls="--", lw=0.75)
    ax_a.set_xticks(range(len(groups)))
    ax_a.set_xticklabels([group[0] for group in groups])
    ax_a.set_ylabel(r"Value of information, $\Delta V$ (fitness units)")
    ax_a.set_ylim(-0.35, 20.7)
    ax_a.set_title("Full semantic confirmations", loc="left", pad=5)
    panel_label(ax_a, "a", x=-0.075, y=1.10)
    clean_ax(ax_a)

    draw_protocol_panel(ax_b, protocol, "B2_default", "Default anchor", (9.2, 14.65), show_threshold=False)
    panel_label(ax_b, "b", x=-0.16, y=1.10)
    draw_protocol_panel(ax_c, protocol, "A_low_3", "Nearest-boundary setting", (0.10, 0.34), show_threshold=True)
    panel_label(ax_c, "c", x=-0.16, y=1.10)

    handles = regime_handles()
    fig.legend(
        handles,
        [handle.get_label() for handle in handles],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        frameon=False,
        columnspacing=1.35,
        handletextpad=0.4,
    )
    return save_all(fig, "FIGURE_8_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main() -> None:
    global TABLE_DIR, OUT
    args = parse_args()
    TABLE_DIR = args.table_dir.resolve()
    OUT = args.out_dir.resolve()
    OUT.mkdir(parents=True, exist_ok=True)

    records = {
        "Figure 3": figure3(),
        "Figure 4": figure4(),
        "Figure 5": figure5(),
        "Figure 6": figure6(),
        "Figure 7": figure7(),
        "Figure 8": figure8(),
    }
    build_manifest(records)

    source_destination = OUT / "produce_publication_figures.py"
    if Path(__file__).resolve() != source_destination.resolve():
        shutil.copy2(Path(__file__), source_destination)


if __name__ == "__main__":
    main()
