from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from PIL import Image, ImageOps, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TABLE_DIR = SCRIPT_DIR / "source_tables"
DEFAULT_OUT_DIR = SCRIPT_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce revised publication-grade JRSI Supplementary Figures S1-S7 from frozen source tables."
    )
    parser.add_argument("--table-dir", type=Path, default=DEFAULT_TABLE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


# Accessible Okabe-Ito-derived palette, matched to the active main-figure package.
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
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "legend.fontsize": 6.0,
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
        "svg.hashsalt": "jrsi-supplementary-figures-v1",
        "savefig.bbox": None,
        "savefig.pad_inches": 0.02,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "mathtext.fontset": "dejavusans",
    }
)

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
    y: float = 1.11,
    size: float = 8.4,
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_all(fig: mpl.figure.Figure, stem: str, size_inches: tuple[float, float]) -> dict[str, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = {ext: OUT / f"{stem}.{ext}" for ext in ["pdf", "svg", "eps", "png"]}
    paths["tiff"] = OUT / f"{stem}.tiff"
    metadata = {
        "Title": stem.replace("_", " "),
        "Author": "JRSI major-revision supplementary-figure production",
        "Subject": "Visualization of frozen quantitative source tables",
        "Keywords": "JRSI; Model B; supplementary figure; accessible colour; vector",
    }
    fig.savefig(paths["pdf"], metadata=metadata, facecolor="white")
    fig.savefig(paths["svg"], metadata={"Title": metadata["Title"], "Creator": metadata["Author"]}, facecolor="white")
    fig.savefig(paths["eps"], format="eps", facecolor="white")
    fig.savefig(paths["png"], dpi=600, facecolor="white")
    with Image.open(paths["png"]) as image:
        image.convert("RGB").save(paths["tiff"], compression="tiff_lzw", dpi=(600, 600))
    plt.close(fig)
    return {
        **{ext: paths[ext].name for ext in paths},
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
    pd.DataFrame(rows).to_csv(OUT / "SUPPLEMENTARY_FIGURE_MANIFEST.csv", index=False)


CONDITION_STYLE = {
    "control": {"label": "Sequence-agnostic", "marker": "o", "colour": ORANGE, "face": WHITE, "line": "--"},
    "selective": {"label": "Sequence-selective", "marker": "s", "colour": BLUE, "face": BLUE, "line": "-"},
}

METHOD_STYLE = {
    "constant": {"marker": "P", "colour": DARK_GRAY, "face": WHITE, "label": "Constant endpoint"},
    "balanced_random_group": {"marker": "o", "colour": SKY, "face": WHITE, "label": "Balanced-random"},
    "affinity_rank_group": {"marker": "^", "colour": BLUE, "face": WHITE, "label": "Affinity-rank"},
    "contiguous_substring": {"marker": "s", "colour": ORANGE, "face": lighten(ORANGE, 0.72), "label": "Contiguous-substring"},
    "identity": {"marker": "D", "colour": VERMILLION, "face": VERMILLION, "label": "Identity endpoint"},
}

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


def regime_handles() -> list[Line2D]:
    handles: list[Line2D] = []
    for regime in REGIME_ORDER:
        style = REGIME_STYLE[regime]
        handles.append(
            Line2D(
                [0], [0], marker=style["marker"],
                color="none" if regime != "R0_null" else style["colour"],
                markerfacecolor=style["face"], markeredgecolor=style["colour"],
                markeredgewidth=0.8, linestyle="none", label=REGIME_LABEL[regime], markersize=5.6,
            )
        )
    return handles


# -----------------------------------------------------------------------------
# Figure S1 - representative frontiers for all p and both regimes
# -----------------------------------------------------------------------------


def draw_small_frontier(
    ax: mpl.axes.Axes,
    points: pd.DataFrame,
    semantic_row: pd.Series,
    title: str,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    show_xlabels: bool,
    show_ylabels: bool,
) -> None:
    points = points.sort_values("retained_information")
    for method, subset in points.groupby("point_method", sort=False):
        style = METHOD_STYLE[method]
        ax.scatter(
            subset["retained_information"], subset["point_viability"],
            s=12 if method in {"constant", "identity"} else 8.5,
            marker=style["marker"], facecolors=style["face"], edgecolors=style["colour"],
            linewidths=0.45, zorder=3,
        )
    frontier = points[["retained_information", "frontier_viability"]].drop_duplicates().sort_values("retained_information")
    ax.step(frontier["retained_information"], frontier["frontier_viability"], where="post", color=BLACK, lw=0.85, zorder=2)
    ax.axhline(float(semantic_row["actual_viability"]), color=MID_GRAY, lw=0.55, ls=":", zorder=1)
    ax.axhline(float(semantic_row["target_viability"]), color=VERMILLION, lw=0.55, ls="--", zorder=1)
    ax.axvline(float(semantic_row["semantic_information"]), color=BLUE, lw=0.55, ls="-.", zorder=1)
    ax.set_title(title, loc="center", pad=3.5, fontsize=6.5)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks([0.0, 0.25, 0.50])
    if not show_xlabels:
        ax.tick_params(labelbottom=False)
    if not show_ylabels:
        ax.tick_params(labelleft=False)
    clean_ax(ax)


def figure_s1() -> dict[str, str]:
    points = load("core_frontier_points.csv")
    semantic = load("core_semantic_replicates.csv")
    selected = semantic[semantic["baseline_replicate"].str.endswith("r00")].copy()
    selected_points = points[points["baseline_replicate"].str.endswith("r00")].copy()

    xlim = (-0.012, 0.545)
    selective_points = selected_points[selected_points["condition"] == "selective"]
    control_points = selected_points[selected_points["condition"] == "control"]
    selective_ylim = (
        float(selective_points["point_viability"].min()) - 0.45,
        float(selective_points["point_viability"].max()) + 0.45,
    )
    control_span = float(control_points["point_viability"].max() - control_points["point_viability"].min())
    control_pad = max(0.025, 0.12 * control_span)
    control_ylim = (
        float(control_points["point_viability"].min()) - control_pad,
        float(control_points["point_viability"].max()) + control_pad,
    )

    size = (7.20, 8.65)
    fig, axes = plt.subplots(4, 5, figsize=size)
    fig.subplots_adjust(left=0.095, right=0.992, bottom=0.080, top=0.885, wspace=0.30, hspace=0.42)
    ps = [round(x, 1) for x in np.arange(0.1, 1.01, 0.1)]
    layout: list[tuple[str, list[float], tuple[float, float]]] = [
        ("selective", ps[:5], selective_ylim),
        ("selective", ps[5:], selective_ylim),
        ("control", ps[:5], control_ylim),
        ("control", ps[5:], control_ylim),
    ]
    letter_index = 0
    for row_index, (condition, row_ps, ylim) in enumerate(layout):
        for col_index, p_value in enumerate(row_ps):
            ax = axes[row_index, col_index]
            replicate_id = f"{condition}_p{p_value:.1f}_r00"
            panel_points = selected_points[selected_points["baseline_replicate"] == replicate_id]
            semantic_row = selected[selected["baseline_replicate"] == replicate_id].iloc[0]
            draw_small_frontier(
                ax,
                panel_points,
                semantic_row,
                rf"$p={p_value:.1f}$",
                xlim,
                ylim,
                show_xlabels=row_index in {1, 3},
                show_ylabels=col_index == 0,
            )
            panel_label(ax, chr(ord("a") + letter_index), x=-0.20, y=1.14, size=6.7)
            letter_index += 1

    fig.text(0.014, 0.685, "Sequence-selective", rotation=90, ha="center", va="center", fontsize=7.4, fontweight="bold")
    fig.text(0.014, 0.285, "Sequence-agnostic", rotation=90, ha="center", va="center", fontsize=7.4, fontweight="bold")
    fig.text(0.54, 0.035, r"Retained information, $I(g(M);Z\mid S)$ (bits)", ha="center", va="center", fontsize=7.1)
    fig.text(0.047, 0.49, "Mean future model fitness", rotation=90, ha="center", va="center", fontsize=7.1)

    method_handles: list[Line2D] = []
    for method in ["constant", "balanced_random_group", "affinity_rank_group", "contiguous_substring", "identity"]:
        style = METHOD_STYLE[method]
        method_handles.append(
            Line2D([0], [0], marker=style["marker"], color="none", markerfacecolor=style["face"],
                   markeredgecolor=style["colour"], markeredgewidth=0.7, label=style["label"], markersize=4.7)
        )
    line_handles = [
        Line2D([0], [0], color=BLACK, lw=0.9, drawstyle="steps-post", label="Cumulative upper frontier"),
        Line2D([0], [0], color=MID_GRAY, lw=0.6, ls=":", label="Actual endpoint"),
        Line2D([0], [0], color=VERMILLION, lw=0.6, ls="--", label="Strict 1% target"),
        Line2D([0], [0], color=BLUE, lw=0.6, ls="-.", label="First target-reaching coordinate"),
    ]
    fig.legend(method_handles, [h.get_label() for h in method_handles], loc="upper center", bbox_to_anchor=(0.5, 0.992), ncol=5,
               frameon=False, columnspacing=0.9, handletextpad=0.35)
    fig.legend(line_handles, [h.get_label() for h in line_handles], loc="upper center", bbox_to_anchor=(0.5, 0.948), ncol=4,
               frameon=False, columnspacing=1.0, handletextpad=0.45, fontsize=5.8)
    return save_all(fig, "FIGURE_S1_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure S2 - complete inference, target, and censoring records
# -----------------------------------------------------------------------------


def bootstrap_series_panel(
    ax: mpl.axes.Axes,
    inference: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    ylim: tuple[float, float] | None = None,
) -> None:
    data = inference[(inference["record_type"] == "block_bootstrap_interval") & (inference["metric"] == metric)]
    for condition in ["control", "selective"]:
        style = CONDITION_STYLE[condition]
        subset = data[data["condition"] == condition].sort_values("inherit_prob")
        x = subset["inherit_prob"].to_numpy(float)
        y = subset["estimate"].to_numpy(float)
        lo = subset["lower"].to_numpy(float)
        hi = subset["upper"].to_numpy(float)
        ax.errorbar(
            x, y, yerr=[y - lo, hi - y], fmt=style["marker"], color=style["colour"],
            markerfacecolor=style["face"], markeredgecolor=style["colour"], markeredgewidth=0.65,
            ls=style["line"], lw=0.9, markersize=4.4, capsize=1.8, elinewidth=0.75, capthick=0.75,
            label=style["label"], zorder=3,
        )
    ax.set_xlim(0.065, 1.035)
    ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    ax.set_xlabel(r"Compositional-coupling probability, $p$")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", pad=5)
    if ylim is not None:
        ax.set_ylim(*ylim)
    clean_ax(ax)


def permutation_panel(ax: mpl.axes.Axes, inference: pd.DataFrame, metric: str, title: str, ylabel: str, colour: str, marker: str) -> None:
    subset = inference[(inference["record_type"] == "replicate_permutation") & (inference["metric"] == metric)].sort_values("inherit_prob")
    ax.plot(subset["inherit_prob"], subset["observed_difference"], color=colour, marker=marker,
            markerfacecolor=colour, markeredgecolor=colour, lw=1.0, markersize=4.2)
    ax.axhline(0, color=LIGHT_GRAY, lw=0.7)
    ax.set_xlim(0.065, 1.035)
    ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    ax.set_xlabel(r"Compositional-coupling probability, $p$")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", pad=5)
    clean_ax(ax)


def target_censoring_matrix(ax: mpl.axes.Axes, inference: pd.DataFrame) -> None:
    targets = inference[inference["record_type"] == "target_reach_count"].copy()
    ps = sorted(targets["inherit_prob"].unique())
    row_specs = [
        ("Agnostic\nreached", "control", "n_target_reached", lighten(GREEN, 0.74)),
        ("Agnostic\ncensored", "control", "n_right_censored", VERY_PALE_GRAY),
        ("Selective\nreached", "selective", "n_target_reached", lighten(BLUE, 0.78)),
        ("Selective\ncensored", "selective", "n_right_censored", VERY_PALE_GRAY),
    ]
    for row_index, (label, condition, column, colour) in enumerate(row_specs):
        subset = targets[targets["condition"] == condition].set_index("inherit_prob")
        for col_index, p_value in enumerate(ps):
            value = int(subset.loc[p_value, column])
            ax.add_patch(Rectangle((col_index, row_index), 1, 1, facecolor=colour, edgecolor=WHITE, linewidth=1.1))
            text = f"{value}/20" if column == "n_target_reached" else str(value)
            ax.text(col_index + 0.5, row_index + 0.5, text, ha="center", va="center", fontsize=6.1, color=BLACK)
    ax.set_xlim(0, len(ps))
    ax.set_ylim(0, len(row_specs))
    ax.invert_yaxis()
    ax.set_xticks(np.arange(len(ps)) + 0.5)
    ax.set_xticklabels([f"{p:.1f}" for p in ps])
    ax.set_yticks(np.arange(len(row_specs)) + 0.5)
    ax.set_yticklabels([x[0] for x in row_specs])
    ax.set_xlabel(r"Compositional-coupling probability, $p$")
    ax.set_title("Target attainment and censoring", loc="left", pad=5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, pad=3)


def figure_s2() -> dict[str, str]:
    inference = load("core_inference_records.csv")
    size = (7.20, 7.35)
    fig = plt.figure(figsize=size)
    grid = fig.add_gridspec(3, 6, height_ratios=[1.0, 0.64, 0.92], left=0.105, right=0.99, bottom=0.085, top=0.90, wspace=0.72, hspace=0.60)
    ax_a = fig.add_subplot(grid[0, 0:3])
    ax_b = fig.add_subplot(grid[0, 3:6])
    ax_c = fig.add_subplot(grid[1, :])
    ax_d = fig.add_subplot(grid[2, 0:2])
    ax_e = fig.add_subplot(grid[2, 2:4])
    ax_f = fig.add_subplot(grid[2, 4:6])

    bootstrap_series_panel(ax_a, inference, "mean_value_of_information", "Mean value of information", r"$\Delta V$ (fitness units)", (-0.25, 13.2))
    panel_label(ax_a, "a", x=-0.18)
    bootstrap_series_panel(ax_b, inference, "median_semantic_information_among_reached", "Median semantic estimate among reached", r"$I_{\mathrm{sem},r}$ (bits)", (-0.02, 0.55))
    panel_label(ax_b, "b", x=-0.18)
    target_censoring_matrix(ax_c, inference)
    panel_label(ax_c, "c", x=-0.105, y=1.14)
    permutation_panel(ax_d, inference, "corrected_conditional_information", "Corrected information difference", "Selective - agnostic (bits)", GREEN, "s")
    panel_label(ax_d, "d", x=-0.25)
    permutation_panel(ax_e, inference, "value_of_information", "Value-of-information difference", "Selective - agnostic (fitness units)", BLUE, "D")
    panel_label(ax_e, "e", x=-0.25)
    permutation_panel(ax_f, inference, "semantic_information", "Semantic-estimate difference", "Selective - agnostic (bits)", PURPLE, "o")
    panel_label(ax_f, "f", x=-0.25)

    condition_handles = [
        Line2D([0], [0], color=CONDITION_STYLE[c]["colour"], marker=CONDITION_STYLE[c]["marker"],
               markerfacecolor=CONDITION_STYLE[c]["face"], markeredgecolor=CONDITION_STYLE[c]["colour"],
               ls=CONDITION_STYLE[c]["line"], label=CONDITION_STYLE[c]["label"], markersize=4.8)
        for c in ["control", "selective"]
    ]
    fig.legend(condition_handles, [h.get_label() for h in condition_handles], loc="upper center", bbox_to_anchor=(0.5, 0.985), ncol=2,
               frameon=False, columnspacing=1.5, handletextpad=0.45)
    return save_all(fig, "FIGURE_S2_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure S3 - all replicate-level value-of-information and semantic estimates
# -----------------------------------------------------------------------------


def raw_replicate_by_p(ax: mpl.axes.Axes, frame: pd.DataFrame, metric: str, title: str, ylabel: str) -> None:
    offsets = {"control": -0.017, "selective": 0.017}
    for condition in ["control", "selective"]:
        style = CONDITION_STYLE[condition]
        subset = frame[frame["condition"] == condition]
        for p_value in sorted(subset["inherit_prob"].unique()):
            values = subset.loc[subset["inherit_prob"] == p_value, metric].to_numpy(float)
            x = np.full(len(values), p_value + offsets[condition]) + stable_jitter(len(values), 0.009)
            ax.scatter(
                x, values, s=13.5, marker=style["marker"],
                facecolors=lighten(style["colour"], 0.76) if condition == "selective" else WHITE,
                edgecolors=style["colour"], linewidths=0.48, zorder=2,
            )
    ax.axhline(0, color=LIGHT_GRAY, lw=0.7, zorder=0)
    ax.set_xlim(0.065, 1.035)
    ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    ax.set_xlabel(r"Compositional-coupling probability, $p$")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", pad=5)
    clean_ax(ax)


def figure_s3() -> dict[str, str]:
    semantic = load("core_semantic_replicates.csv")
    size = (7.20, 3.45)
    fig, axes = plt.subplots(1, 2, figsize=size)
    fig.subplots_adjust(left=0.105, right=0.99, bottom=0.18, top=0.81, wspace=0.31)
    raw_replicate_by_p(axes[0], semantic, "value_of_information", "Value of information", r"$\Delta V$ (fitness units)")
    panel_label(axes[0], "a", x=-0.18, y=1.12)
    raw_replicate_by_p(axes[1], semantic, "semantic_information", "Replicate-specific semantic estimate", r"$I_{\mathrm{sem},r}$ (bits)")
    panel_label(axes[1], "b", x=-0.18, y=1.12)
    handles = [
        Line2D([0], [0], marker=CONDITION_STYLE[c]["marker"], color="none",
               markerfacecolor=CONDITION_STYLE[c]["face"], markeredgecolor=CONDITION_STYLE[c]["colour"],
               markeredgewidth=0.7, label=CONDITION_STYLE[c]["label"], markersize=5.0)
        for c in ["control", "selective"]
    ]
    fig.legend(handles, [h.get_label() for h in handles], loc="upper center", bbox_to_anchor=(0.5, 0.985), ncol=2, frameon=False,
               columnspacing=1.5, handletextpad=0.45)
    return save_all(fig, "FIGURE_S3_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure S4 - all matched seed-block control distributions
# -----------------------------------------------------------------------------


def paired_multicategory_panel(
    ax: mpl.axes.Axes,
    blocks: pd.DataFrame,
    keys: list[str],
    labels: list[str],
    colours: list[str],
    markers: list[str],
    title: str,
) -> None:
    wide = blocks.pivot(index="seed_block", columns="control_or_reference", values="value_of_information")
    x = np.arange(len(keys), dtype=float)
    for seed_block, row in wide.iterrows():
        y = [float(row[k]) for k in keys]
        ax.plot(x, y, color=LIGHT_GRAY, lw=0.55, zorder=1)
    for xi, key, colour, marker in zip(x, keys, colours, markers):
        y = wide[key].to_numpy(float)
        ax.scatter(
            np.full(len(y), xi) + stable_jitter(len(y), 0.055), y, s=14.5, marker=marker,
            facecolors=lighten(colour, 0.74) if marker not in {"x", "+"} else colour,
            edgecolors=colour, linewidths=0.55, zorder=3,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.45, len(keys) - 0.55)
    ax.set_ylim(2.0, 15.4)
    ax.set_title(title, loc="left", pad=5)
    clean_ax(ax)


def figure_s4() -> dict[str, str]:
    blocks = load("causal_specificity_seed_blocks.csv")
    panels = [
        (["native_full_voi", "selection_reduced", "selection_neutral"], ["Full\nselection", "Reduced\nselection", "Neutral"], [BLUE, ORANGE, VERMILLION], ["s", "o", "D"], "Selection strength"),
        (["native_full_voi", "affinity_reassigned", "topology_mismatch"], ["Native\nmapping", "Affinity\nreassigned", "Topology\nmismatch"], [BLUE, ORANGE, GREEN], ["s", "o", "D"], "Native-mapping disruptions"),
        (["alternative_a_native", "alternative_a_cross_b"], ["Topology A\nnative", "A evaluated\nunder B"], [GREEN, ORANGE], ["s", "o"], "Alternative topology A"),
        (["alternative_b_native", "alternative_b_cross_a"], ["Topology B\nnative", "B evaluated\nunder A"], [GREEN, ORANGE], ["s", "o"], "Alternative topology B"),
        (["alternative_native_mean", "alternative_cross_mean"], ["Alternative\nnative mean", "Cross-evaluated\nmean"], [GREEN, ORANGE], ["s", "o"], "Alternative-topology aggregate"),
        (["alternative_native_mean", "temporally_unstable"], ["Stable fixed\nmean", "Temporally\nunstable"], [GREEN, VERMILLION], ["s", "D"], "Stable versus temporally unstable"),
    ]
    size = (7.20, 6.35)
    fig, axes = plt.subplots(2, 3, figsize=size)
    fig.subplots_adjust(left=0.090, right=0.99, bottom=0.105, top=0.925, wspace=0.31, hspace=0.42)
    for idx, (keys, labels, colours, markers, title) in enumerate(panels):
        ax = axes.flat[idx]
        paired_multicategory_panel(ax, blocks, keys, labels, colours, markers, title)
        panel_label(ax, chr(ord("a") + idx), x=-0.22, y=1.11)
        if idx % 3 == 0:
            ax.set_ylabel(r"Value of information, $\Delta V$ (fitness units)")
        else:
            ax.tick_params(labelleft=False)
    return save_all(fig, "FIGURE_S4_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure S5 - raw Stage A/B1/B2 replicate distributions
# -----------------------------------------------------------------------------


B2_FAMILY_ORDER = {"anchor": 0, "window": 1, "position": 2, "metabolite": 3, "fitness": 4}


def ordered_screen_settings(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        spec = json.loads(row["spec_json"])
        stage = str(row["stage"])
        if stage == "A":
            key = (0, float(spec["b_ratio"]), float(spec["p"]), float(spec["sigma_ratio"]), str(row["design_id"]))
        elif stage == "B1":
            key = (1, str(row["design_id"]))
        else:
            key = (2, B2_FAMILY_ORDER.get(str(row["family"]), 99), str(row["design_id"]))
        rows.append({**row.to_dict(), "sort_key": key})
    ordered = pd.DataFrame(rows).sort_values("sort_key").reset_index(drop=True)
    ordered["setting_index"] = np.arange(1, len(ordered) + 1)
    return ordered


def screen_raw_panel(
    ax: mpl.axes.Axes,
    replicates: pd.DataFrame,
    order_map: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    threshold: float,
) -> None:
    stage_style = {
        "A": {"colour": BLUE, "marker": "o"},
        "B1": {"colour": ORANGE, "marker": "^"},
        "B2": {"colour": GREEN, "marker": "s"},
    }
    index_lookup = order_map.set_index("design_id")["setting_index"].to_dict()
    for stage in ["A", "B1", "B2"]:
        subset = replicates[replicates["stage"] == stage]
        style = stage_style[stage]
        for design_id, group in subset.groupby("design_id", sort=False):
            x0 = float(index_lookup[design_id])
            values = group[metric].to_numpy(float)
            ax.scatter(
                np.full(len(values), x0) + stable_jitter(len(values), 0.19), values,
                s=10.0, marker=style["marker"], facecolors=lighten(style["colour"], 0.74),
                edgecolors=style["colour"], linewidths=0.42, zorder=3,
            )
    stage_ranges = {}
    for stage in ["A", "B1", "B2"]:
        vals = order_map.loc[order_map["stage"] == stage, "setting_index"].to_numpy(float)
        stage_ranges[stage] = (vals.min() - 0.5, vals.max() + 0.5)
    for stage, (x0, x1) in stage_ranges.items():
        colour = stage_style[stage]["colour"]
        ax.axvspan(x0, x1, color=lighten(colour, 0.93), zorder=0)
        ax.text((x0 + x1) / 2, 0.985, f"Stage {stage}", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=6.4, fontweight="bold",
                bbox={"facecolor": WHITE, "edgecolor": "none", "pad": 0.8})
    ax.axvline(stage_ranges["A"][1], color=PALE_GRAY, lw=0.9, zorder=1)
    ax.axvline(stage_ranges["B1"][1], color=PALE_GRAY, lw=0.9, zorder=1)
    ax.axhline(threshold, color=DARK_GRAY, ls="--", lw=0.75, zorder=1)
    ax.axhline(0, color=LIGHT_GRAY, lw=0.55, zorder=1)
    ax.set_xlim(0.3, len(order_map) + 0.7)
    ticks = [1, 8, 16, 24, 32, 33, 40, 48, 49, 57, 65]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(x) for x in ticks])
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", pad=5)
    clean_ax(ax)


def figure_s5() -> dict[str, str]:
    replicates = load("generality_screen_replicates.csv")
    summary = load("generality_screen_summary.csv")
    order_map = ordered_screen_settings(summary)
    order_out = order_map[["setting_index", "stage", "family", "design_id", "spec_json", "regime"]].copy()
    order_out.to_csv(OUT / "FIGURE_S5_SETTING_ORDER.csv", index=False)

    size = (7.20, 7.45)
    fig, axes = plt.subplots(3, 1, figsize=size, sharex=True)
    fig.subplots_adjust(left=0.105, right=0.99, bottom=0.095, top=0.93, hspace=0.38)
    screen_raw_panel(axes[0], replicates, order_map, "corrected_information", "Corrected sequence-specific information", r"$I_{\mathrm{seq,corr}}$ (bits)", 0.01)
    panel_label(axes[0], "a", x=-0.105, y=1.10)
    screen_raw_panel(axes[1], replicates, order_map, "value_of_information", "Value of information", r"$\Delta V$ (fitness units)", 0.25)
    panel_label(axes[1], "b", x=-0.105, y=1.10)
    screen_raw_panel(axes[2], replicates, order_map, "adaptive_gain", "Selection-driven fitness gain", r"Adaptive gain (fitness units)", 1.0)
    panel_label(axes[2], "c", x=-0.105, y=1.10)
    axes[2].set_xlabel("Prespecified setting index (ordered by stage; full key supplied with the figure)")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=lighten(BLUE, 0.74), markeredgecolor=BLUE, label="Stage A", markersize=5),
        Line2D([0], [0], marker="^", color="none", markerfacecolor=lighten(ORANGE, 0.74), markeredgecolor=ORANGE, label="Stage B1", markersize=5),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=lighten(GREEN, 0.74), markeredgecolor=GREEN, label="Stage B2", markersize=5),
        Line2D([0], [0], color=DARK_GRAY, ls="--", lw=0.8, label="Prespecified practical threshold"),
    ]
    fig.legend(handles, [h.get_label() for h in handles], loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=4, frameon=False,
               columnspacing=1.2, handletextpad=0.4)
    return save_all(fig, "FIGURE_S5_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure S6 - complete protocol sensitivity across all classification metrics
# -----------------------------------------------------------------------------


def protocol_order(row: pd.Series) -> tuple[int, int]:
    design_id = str(row["design_id"])
    if "_g" in design_id:
        value = int(design_id.split("_g")[1].split("_")[0])
        return (0, value)
    value = int(design_id.split("_h")[1].split("_")[0])
    return (1, value)


def draw_protocol_metric(
    ax: mpl.axes.Axes,
    protocol: pd.DataFrame,
    suffix: str,
    metric_prefix: str,
    ylabel: str,
    threshold: float,
    show_group_labels: bool,
) -> None:
    subset = protocol[protocol["design_id"].str.endswith(suffix)].copy()
    subset[["kind_order", "numeric_value"]] = subset.apply(lambda row: pd.Series(protocol_order(row)), axis=1)
    subset = subset.sort_values(["kind_order", "numeric_value"])
    x_positions = np.asarray([0, 1, 2, 4, 5, 6], dtype=float)
    for x, (_, row) in zip(x_positions, subset.iterrows()):
        style = REGIME_STYLE[str(row["regime"])]
        estimate = float(row[f"{metric_prefix}_mean"])
        lower = float(row[f"{metric_prefix}_low"])
        upper = float(row[f"{metric_prefix}_high"])
        fmt = style["marker"]
        markerface = style["colour"] if str(row["regime"]) == "R0_null" else style["face"]
        ax.errorbar(
            x, estimate, yerr=[[estimate - lower], [upper - estimate]], fmt=fmt, color=style["colour"],
            markerfacecolor=markerface, markeredgecolor=style["colour"], markeredgewidth=0.8,
            markersize=5.0, capsize=2.0, elinewidth=0.9, capthick=0.9, zorder=3,
        )
    ax.axhline(threshold, color=DARK_GRAY, ls="--", lw=0.75, zorder=0)
    ax.axvline(3, color=PALE_GRAY, lw=0.8, zorder=0)
    ax.set_xticks(x_positions)
    ax.set_xlim(-0.55, 6.55)
    ax.set_ylabel(ylabel)
    if show_group_labels:
        ax.set_xticklabels([str(int(value)) for value in subset["numeric_value"]])
        ax.text(1, -0.20, r"Evolution duration, $T_{\mathrm{evo}}$", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=5.9)
        ax.text(5, -0.20, r"Intervention horizon, $\tau_{\mathrm{int}}$", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=5.9)
    else:
        ax.set_xticklabels([])
        ax.tick_params(axis="x", length=0)
    clean_ax(ax)


def figure_s6() -> dict[str, str]:
    protocol = load("generality_protocol_summary.csv")
    specs = [
        ("corrected_information", r"$I_{\mathrm{seq,corr}}$ (bits)", 0.01),
        ("value_of_information", r"$\Delta V$ (fitness units)", 0.25),
        ("adaptive_gain", "Adaptive gain (fitness units)", 1.0),
    ]
    columns = [("B2_default", "Default anchor"), ("A_low_3", "Nearest-boundary setting")]
    size = (7.20, 8.05)
    fig, axes = plt.subplots(3, 2, figsize=size)
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.105, top=0.875, wspace=0.36, hspace=0.56)

    panel_index = 0
    for row_idx, (metric, ylabel, threshold) in enumerate(specs):
        for col_idx, (suffix, _column_label) in enumerate(columns):
            ax = axes[row_idx, col_idx]
            draw_protocol_metric(
                ax, protocol, suffix, metric, ylabel, threshold,
                show_group_labels=(row_idx == len(specs) - 1),
            )
            panel_label(ax, chr(ord("a") + panel_index), x=-0.16, y=1.11)
            panel_index += 1

    fig.text(0.292, 0.900, "Default anchor", ha="center", va="bottom", fontsize=7.3, fontweight="bold")
    fig.text(0.748, 0.900, "Nearest-boundary setting", ha="center", va="bottom", fontsize=7.3, fontweight="bold")

    handles = regime_handles()
    fig.legend(handles, [h.get_label() for h in handles], loc="upper center", bbox_to_anchor=(0.5, 0.985), ncol=5,
               frameon=False, columnspacing=1.2, handletextpad=0.4)
    return save_all(fig, "FIGURE_S6_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Figure S7 - raw nondefault confirmatory replicate records
# -----------------------------------------------------------------------------


def endpoint_panel(ax: mpl.axes.Axes, frame: pd.DataFrame, title: str) -> None:
    x = np.asarray([0, 1, 2], dtype=float)
    for _, row in frame.iterrows():
        y = [float(row["constant_viability"]), float(row["target_viability"]), float(row["actual_viability"])]
        ax.plot(x, y, color=LIGHT_GRAY, lw=0.6, zorder=1)
    endpoint_specs = [
        ("constant_viability", ORANGE, "o", "Constant"),
        ("target_viability", VERMILLION, "^", "Strict 1% target"),
        ("actual_viability", BLUE, "s", "Actual"),
    ]
    for xi, (column, colour, marker, label) in zip(x, endpoint_specs):
        values = frame[column].to_numpy(float)
        ax.scatter(np.full(len(values), xi) + stable_jitter(len(values), 0.055), values, s=17, marker=marker,
                   facecolors=lighten(colour, 0.72), edgecolors=colour, linewidths=0.55, zorder=3)
    # Identity endpoints exactly overlay actual viability; open diamonds make recovery visible.
    values = frame["identity_viability"].to_numpy(float)
    ax.scatter(np.full(len(values), 2.10) + stable_jitter(len(values), 0.045), values, s=18, marker="D",
               facecolors=WHITE, edgecolors=PURPLE, linewidths=0.65, zorder=4)
    ax.set_xticks([0, 1, 2.05])
    ax.set_xticklabels(["Constant", "Target", "Actual +\nidentity"])
    ax.set_xlim(-0.4, 2.45)
    ax.set_ylabel("Mean future model fitness")
    ax.set_title(title, loc="left", pad=5)
    clean_ax(ax)


def raw_confirm_metric(ax: mpl.axes.Axes, frame: pd.DataFrame, metric: str, title: str, ylabel: str) -> None:
    label_colours = {"D0": GREEN, "D1": PURPLE, "D2": ORANGE}
    label_markers = {"D0": "s", "D1": "*", "D2": "D"}
    for x, cid in enumerate(["D0", "D1", "D2"]):
        values = frame[frame["confirm_id"] == cid][metric].to_numpy(float)
        ax.scatter(np.full(len(values), x) + stable_jitter(len(values), 0.11), values, s=19,
                   marker=label_markers[cid], facecolors=lighten(label_colours[cid], 0.72) if cid != "D1" else label_colours[cid],
                   edgecolors=label_colours[cid], linewidths=0.55, zorder=3)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["D0", "D1", "D2"])
    ax.set_title(title, loc="left", pad=5)
    ax.set_ylabel(ylabel)
    ax.axhline(0, color=LIGHT_GRAY, lw=0.65)
    clean_ax(ax)


def semantic_identity_panel(ax: mpl.axes.Axes, frame: pd.DataFrame) -> None:
    positions = {"D0": (0, 1), "D1": (3, 4), "D2": (6, 7)}
    colours = {"D0": GREEN, "D1": PURPLE, "D2": ORANGE}
    for cid, (x_sem, x_id) in positions.items():
        subset = frame[frame["confirm_id"] == cid]
        for _, row in subset.iterrows():
            ax.plot([x_sem, x_id], [float(row["semantic_information"]), float(row["identity_information"])], color=LIGHT_GRAY, lw=0.55)
        sem = subset["semantic_information"].to_numpy(float)
        identity = subset["identity_information"].to_numpy(float)
        ax.scatter(np.full(len(sem), x_sem) + stable_jitter(len(sem), 0.08), sem, s=17, marker="o",
                   facecolors=lighten(colours[cid], 0.70), edgecolors=colours[cid], linewidths=0.55, zorder=3)
        ax.scatter(np.full(len(identity), x_id) + stable_jitter(len(identity), 0.08), identity, s=17, marker="D",
                   facecolors=WHITE, edgecolors=colours[cid], linewidths=0.65, zorder=3)
    ax.set_xticks([0.5, 3.5, 6.5])
    ax.set_xticklabels(["D0", "D1", "D2"])
    ax.set_xlim(-0.6, 7.6)
    ax.set_ylabel("Information (bits)")
    ax.set_title("Semantic estimate versus identity information", loc="left", pad=5)
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=LIGHT_GRAY, markeredgecolor=DARK_GRAY, label="Semantic estimate", markersize=4.8),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=WHITE, markeredgecolor=DARK_GRAY, label="Identity information", markersize=4.8),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=5.6, handletextpad=0.35)
    clean_ax(ax)


def confirmatory_audit_matrix(ax: mpl.axes.Axes, frame: pd.DataFrame) -> None:
    cols = ["D0", "D1", "D2"]
    rows = [
        ("Target reached", lambda g: int(g["target_reached"].sum())),
        ("No right censoring", lambda g: int((g["censoring"] == "none").sum())),
        ("Identity information exact", lambda g: int(g["identity_information_recovered"].sum())),
        ("Identity viability exact", lambda g: int(g["identity_viability_recovered"].sum())),
    ]
    for ri, (label, func) in enumerate(rows):
        for ci, cid in enumerate(cols):
            group = frame[frame["confirm_id"] == cid]
            value = func(group)
            ax.add_patch(Rectangle((ci, ri), 1, 1, facecolor=lighten(GREEN, 0.82), edgecolor=WHITE, linewidth=1.2))
            ax.text(ci + 0.5, ri + 0.5, f"{value}/8", ha="center", va="center", fontsize=6.4)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 4)
    ax.invert_yaxis()
    ax.set_xticks(np.arange(3) + 0.5)
    ax.set_xticklabels(cols)
    ax.set_yticks(np.arange(4) + 0.5)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_title("Target, censoring, and endpoint audit", loc="left", pad=5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, pad=3)


def figure_s7() -> dict[str, str]:
    confirm = load("generality_confirmatory_replicates.csv")
    size = (7.20, 6.65)
    fig = plt.figure(figsize=size)
    grid = fig.add_gridspec(2, 3, left=0.095, right=0.99, bottom=0.09, top=0.94, wspace=0.38, hspace=0.48)
    axes = [fig.add_subplot(grid[0, i]) for i in range(3)] + [fig.add_subplot(grid[1, i]) for i in range(3)]
    titles = {"D0": "D0: viability-relevant representative", "D1": "D1: strong-adaptation representative", "D2": "D2: boundary representative"}
    for idx, cid in enumerate(["D0", "D1", "D2"]):
        endpoint_panel(axes[idx], confirm[confirm["confirm_id"] == cid], titles[cid])
        panel_label(axes[idx], chr(ord("a") + idx), x=-0.23, y=1.11)
    raw_confirm_metric(axes[3], confirm, "value_of_information", "Value of information", r"$\Delta V$ (fitness units)")
    panel_label(axes[3], "d", x=-0.23, y=1.11)
    semantic_identity_panel(axes[4], confirm)
    panel_label(axes[4], "e", x=-0.23, y=1.11)
    confirmatory_audit_matrix(axes[5], confirm)
    panel_label(axes[5], "f", x=-0.23, y=1.11)
    return save_all(fig, "FIGURE_S7_PUBLICATION_GRADE", size)


# -----------------------------------------------------------------------------
# Proof sheets and main
# -----------------------------------------------------------------------------


def make_contact_sheet(records: dict[str, dict[str, str]], grayscale: bool = False) -> Path:
    thumbs: list[tuple[str, Image.Image]] = []
    for figure_name, record in records.items():
        path = OUT / record["png"]
        with Image.open(path) as im:
            img = im.convert("RGB")
            if grayscale:
                img = ImageOps.grayscale(img).convert("RGB")
            img.thumbnail((1350, 1350), Image.Resampling.LANCZOS)
            thumbs.append((figure_name, img.copy()))
    margin = 30
    title_h = 36
    cols = 2
    cell_w = 1420
    cell_h = max(img.height for _, img in thumbs) + title_h + 50
    rows = math.ceil(len(thumbs) / cols)
    canvas = Image.new("RGB", (cols * cell_w + (cols + 1) * margin, rows * cell_h + (rows + 1) * margin), "white")
    draw = ImageDraw.Draw(canvas)
    for idx, (name, img) in enumerate(thumbs):
        row, col = divmod(idx, cols)
        x = margin + col * cell_w
        y = margin + row * cell_h
        draw.text((x, y), name, fill=BLACK)
        x_img = x + (cell_w - img.width) // 2
        canvas.paste(img, (x_img, y + title_h))
    out = OUT / "qc_proofs" / ("GRAYSCALE_PROOF_CONTACT_SHEET.png" if grayscale else "COLOR_PROOF_CONTACT_SHEET.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(200, 200))
    return out


def main() -> None:
    global TABLE_DIR, OUT
    args = parse_args()
    TABLE_DIR = args.table_dir.resolve()
    OUT = args.out_dir.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    records = {
        "Figure S1": figure_s1(),
        "Figure S2": figure_s2(),
        "Figure S3": figure_s3(),
        "Figure S4": figure_s4(),
        "Figure S5": figure_s5(),
        "Figure S6": figure_s6(),
        "Figure S7": figure_s7(),
    }
    build_manifest(records)
    make_contact_sheet(records, grayscale=False)
    make_contact_sheet(records, grayscale=True)
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
