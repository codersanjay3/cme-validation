#!/usr/bin/env python3
"""
empirical_figures.py — Publication-quality empirical validation figure for CME paper.

Reads empirical_tdi_results.csv (already computed) and generates a detailed
4-panel figure saved to figures/empirical_tdi_validation.png.

Panels:
  A (top, full width): TDI time series + VIX overlay, crisis shading, annotated events
  B (bottom left):     TDI vs VIX scatter, year-coloured, OLS + 95% CI, key quarters labelled
  C (bottom centre):   Cross-correlation TDI ~ VIX at lags -4 to +4 quarters
  D (bottom right):    τ-distribution comparison: lowest-TDI vs highest-TDI quarter
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from scipy import stats
from pathlib import Path

# ── Load data ─────────────────────────────────────────────────────────────────

CSV   = Path("/Users/sanjaysubramania/cme_validation/empirical_tdi_results.csv")
CACHE = Path("/Users/sanjaysubramania/cme_validation/edgar_cache")
OUT   = Path("/Users/sanjaysubramania/cme_validation/figures/empirical_tdi_validation.png")

df = pd.read_csv(CSV)
# Drop outlier 2013Q2 (only 9 institutions — too sparse) and any with n < 50
df = df[df["n_institutions"] >= 50].copy()
df = df[df["label"] <= "2024Q4"].copy()  # exclude future quarters if any
df = df.reset_index(drop=True)

labels   = df["label"].tolist()
tdi      = df["TDI"].values
vix      = df["VIX_avg"].values
n_inst   = df["n_institutions"].values
years    = df["year"].values
x        = np.arange(len(labels))

# ── Correlation stats ─────────────────────────────────────────────────────────

r_main, p_main = stats.pearsonr(tdi, vix)
n_q = len(df)

# Cross-correlations at lags -4 to +4
lags = list(range(-4, 5))
xcorrs = []
xcorr_ps = []
for lag in lags:
    if lag < 0:
        r, p = stats.pearsonr(tdi[-lag:], vix[:lag])
    elif lag > 0:
        r, p = stats.pearsonr(tdi[:-lag], vix[lag:])
    else:
        r, p = stats.pearsonr(tdi, vix)
    xcorrs.append(r)
    xcorr_ps.append(p)

# ── Style ─────────────────────────────────────────────────────────────────────

BLUE   = "#1f77b4"
RED    = "#d62728"
GREY   = "#7f7f7f"
GREEN  = "#2ca02c"
ORANGE = "#ff7f0e"

plt.rcParams.update({
    "font.family":       "serif",
    "font.size":         9,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    0.8,
    "xtick.major.size":  3,
    "ytick.major.size":  3,
    "legend.framealpha": 0.85,
    "legend.fontsize":   8,
})

# ── Build figure ──────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(14, 11))
gs  = gridspec.GridSpec(
    2, 3,
    figure=fig,
    hspace=0.48,
    wspace=0.38,
    left=0.07, right=0.96,
    top=0.91, bottom=0.08,
)

# ══════════════════════════════════════════════════════════════════════════════
# Panel A — TDI time series + VIX
# ══════════════════════════════════════════════════════════════════════════════

axA  = fig.add_subplot(gs[0, :])   # full top row
axAv = axA.twinx()

# VIX fill first (behind TDI)
axAv.fill_between(x, vix, alpha=0.12, color=RED, label="_nolegend_")
lVIX, = axAv.plot(x, vix, color=RED, lw=1.2, alpha=0.7, ls="--", label="VIX (quarterly avg)")
lTDI, = axA.plot(x, tdi,  color=BLUE, lw=2.0, marker="o", ms=4, zorder=4, label="Empirical TDI")

# Crisis shading
def shade_region(ax, label_start, label_end, color, text, text_y=0.95):
    if label_start in labels and label_end in labels:
        xs = labels.index(label_start)
        xe = labels.index(label_end)
        ax.axvspan(xs - 0.4, xe + 0.4, alpha=0.18, color=color, zorder=1)
        ax.text((xs + xe) / 2, ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * text_y,
                text, ha="center", va="top", fontsize=7, color="black",
                style="italic", zorder=5)

# Key annotations
events = {
    "2020Q1": ("Covid crash\n TDI=1.550", "below"),
    "2022Q2": ("Rate hike\n TDI=1.676", "below"),
    "2022Q4": ("2022Q4 outlier\n TDI=1.021", "below"),
    "2017Q4": ("Bull peak\n TDI=1.971", "above"),
    "2024Q1": ("AI rally\n TDI=1.980", "above"),
}
for ql, (txt, pos) in events.items():
    if ql not in labels:
        continue
    xi = labels.index(ql)
    yi = tdi[xi]
    offset = 0.12 if pos == "above" else -0.12
    axA.annotate(
        txt,
        xy=(xi, yi),
        xytext=(xi, yi + offset),
        ha="center", fontsize=6.5, color=BLUE,
        arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=BLUE, lw=0.6, alpha=0.85),
        zorder=6,
    )

# Axis labels
axA.set_ylabel("Temporal Diversity Index (TDI)", color=BLUE, fontsize=9)
axAv.set_ylabel("VIX (quarterly average)", color=RED, fontsize=9)
axA.tick_params(axis="y", colors=BLUE)
axAv.tick_params(axis="y", colors=RED)
axA.set_ylim(0.8, 2.3)
axAv.set_ylim(0, 55)

# X ticks — every 4 quarters (1 year)
tick_step = 4
axA.set_xticks(x[::tick_step])
axA.set_xticklabels(labels[::tick_step], rotation=45, ha="right", fontsize=7.5)
axA.set_xlim(-0.8, len(labels) - 0.2)

# Shade crisis periods
for label_start, label_end, color, text in [
    ("2020Q1", "2020Q2", "salmon",      "Covid-19"),
    ("2022Q1", "2022Q3", "lightyellow", "Rate hikes"),
    ("2008Q3", "2009Q1", "lightblue",   "GFC"),   # may not be in data
]:
    if label_start in labels and label_end in labels:
        xs = labels.index(label_start)
        xe = labels.index(label_end)
        axA.axvspan(xs - 0.4, xe + 0.4, alpha=0.20, color=color, zorder=1)

# Horizontal reference line at mean TDI
mean_tdi = np.mean(tdi)
axA.axhline(mean_tdi, color=GREY, lw=0.8, ls=":", zorder=2)
axA.text(len(labels) - 0.5, mean_tdi + 0.02, f"mean={mean_tdi:.2f}", fontsize=7,
         color=GREY, ha="right", va="bottom")

axA.set_title(
    "A   Empirical TDI vs. Market Volatility — SEC 13-F Institutional Holdings (2013–2024)",
    fontsize=10, fontweight="bold", loc="left", pad=6,
)
legend_handles = [lTDI, lVIX,
                  mpatches.Patch(color="salmon",      alpha=0.4, label="Covid-19 crash"),
                  mpatches.Patch(color="lightyellow", alpha=0.8, label="Rate hike cycle"),
                  ]
axA.legend(handles=legend_handles, loc="upper left", fontsize=8, framealpha=0.9)

# ══════════════════════════════════════════════════════════════════════════════
# Panel B — TDI vs VIX scatter
# ══════════════════════════════════════════════════════════════════════════════

axB = fig.add_subplot(gs[1, 0])

# Colour by year
yr_min, yr_max = years.min(), years.max()
norm = plt.Normalize(yr_min, yr_max)
cmap = plt.cm.viridis
colors_pts = cmap(norm(years))

sc = axB.scatter(vix, tdi, c=years, cmap="viridis", s=n_inst * 0.35 + 8,
                 alpha=0.80, zorder=3, edgecolors="white", linewidths=0.4)

# OLS fit + 95% CI
m, b, r_, p_, se = stats.linregress(vix, tdi)
vx_fit = np.linspace(vix.min() - 1, vix.max() + 1, 200)
tdi_fit = m * vx_fit + b
axB.plot(vx_fit, tdi_fit, color=GREY, lw=1.4, ls="--", zorder=2, label=f"OLS  r={r_main:.3f}, p={p_main:.3f}")

# 95% CI band
n_ = len(vix)
t_crit = stats.t.ppf(0.975, df=n_ - 2)
s_err  = np.sqrt(np.sum((tdi - (m * vix + b))**2) / (n_ - 2))
ci = t_crit * s_err * np.sqrt(1/n_ + (vx_fit - np.mean(vix))**2 / np.sum((vix - np.mean(vix))**2))
axB.fill_between(vx_fit, tdi_fit - ci, tdi_fit + ci, alpha=0.12, color=GREY)

# Label notable quarters
label_these = {"2020Q1", "2022Q4", "2017Q4", "2024Q1", "2020Q2", "2022Q2"}
for i, ql in enumerate(labels):
    if ql in label_these:
        axB.annotate(ql, (vix[i], tdi[i]), fontsize=6.5, ha="left",
                     xytext=(3, 2), textcoords="offset points", color=BLUE,
                     bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.7, lw=0))

cbar = plt.colorbar(sc, ax=axB, pad=0.01)
cbar.set_label("Year", fontsize=8)
cbar.ax.tick_params(labelsize=7)

axB.set_xlabel("VIX (quarterly average)", fontsize=9)
axB.set_ylabel("TDI", fontsize=9)
axB.legend(fontsize=7.5, loc="upper right")
axB.set_title("B   TDI–VIX Scatter", fontsize=10, fontweight="bold", loc="left")

# Size legend
for size_inst in [80, 100, 120]:
    axB.scatter([], [], s=size_inst * 0.35 + 8, c="grey", alpha=0.6,
                label=f"n={size_inst} institutions")
axB.legend(fontsize=6.5, loc="upper right", ncol=1,
           title="Point size = institutions", title_fontsize=6.5)

# ══════════════════════════════════════════════════════════════════════════════
# Panel C — Cross-correlation
# ══════════════════════════════════════════════════════════════════════════════

axC = fig.add_subplot(gs[1, 1])

bar_colors = [RED if r < 0 else GREEN for r in xcorrs]
bars = axC.bar(lags, xcorrs, color=bar_colors, alpha=0.75, width=0.65, zorder=3, edgecolor="white")

# p < 0.05 significance threshold (two-tailed, n≈44)
sig_thresh = stats.t.ppf(0.975, df=n_q - 2)
sig_r = sig_thresh / np.sqrt(sig_thresh**2 + n_q - 2)
axC.axhline( sig_r, color=GREY, lw=1.0, ls="--", label=f"p<0.05 (|r|={sig_r:.2f})")
axC.axhline(-sig_r, color=GREY, lw=1.0, ls="--")
axC.axhline(0, color="black", lw=0.6)
axC.axvline(0, color=GREY, lw=0.6, ls=":")

# Annotate significant bars
for lag, r, p in zip(lags, xcorrs, xcorr_ps):
    if p < 0.05:
        axC.text(lag, r + (0.025 if r > 0 else -0.025),
                 f"{r:.2f}*", ha="center", fontsize=7,
                 va="bottom" if r > 0 else "top", fontweight="bold")

axC.set_xlabel("Lag (quarters, positive = VIX leads TDI)", fontsize=8.5)
axC.set_ylabel("Pearson r", fontsize=9)
axC.set_xticks(lags)
axC.set_xticklabels([f"{l:+d}Q" for l in lags], fontsize=7.5)
axC.set_ylim(-0.65, 0.45)
axC.legend(fontsize=7.5, loc="lower right")
axC.set_title("C   Cross-Correlation: TDI ~ VIX", fontsize=10, fontweight="bold", loc="left")

# Annotation
axC.text(-3.8, -0.58, "← TDI leads", fontsize=7, color=GREY, style="italic")
axC.text( 0.2, -0.58,  "VIX leads →", fontsize=7, color=GREY, style="italic")

# ══════════════════════════════════════════════════════════════════════════════
# Panel D — TDI distribution over time (violin / box by VIX regime)
# ══════════════════════════════════════════════════════════════════════════════

axD = fig.add_subplot(gs[1, 2])

# Split quarters into VIX regimes: low (<15), medium (15-20), high (>20)
vix_low  = tdi[vix <  15]
vix_med  = tdi[(vix >= 15) & (vix < 22)]
vix_high = tdi[vix >= 22]

vp = axD.violinplot(
    [vix_low, vix_med, vix_high],
    positions=[1, 2, 3],
    showmedians=True,
    showextrema=True,
    widths=0.6,
)
for i, (body, color) in enumerate(zip(vp["bodies"], [GREEN, ORANGE, RED])):
    body.set_facecolor(color)
    body.set_alpha(0.55)
vp["cmedians"].set_color("black")
vp["cmedians"].set_linewidth(1.5)
vp["cmaxes"].set_color(GREY)
vp["cmins"].set_color(GREY)
vp["cbars"].set_color(GREY)

# Overlay individual points
for xi, subset, color in [(1, vix_low, GREEN), (2, vix_med, ORANGE), (3, vix_high, RED)]:
    jitter = np.random.default_rng(42).uniform(-0.12, 0.12, len(subset))
    axD.scatter(xi + jitter, subset, color=color, alpha=0.5, s=18, zorder=4, edgecolors="white", lw=0.3)

# Median labels
for xi, subset in [(1, vix_low), (2, vix_med), (3, vix_high)]:
    axD.text(xi, np.median(subset) + 0.03, f"med={np.median(subset):.2f}",
             ha="center", fontsize=7, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.8, lw=0))

# n labels
for xi, (subset, label_) in enumerate([(vix_low, "VIX<15\n(low)"),
                                         (vix_med, "15≤VIX<22\n(medium)"),
                                         (vix_high, "VIX≥22\n(high)")], start=1):
    axD.text(xi, 0.87, f"n={len(subset)}", ha="center", fontsize=7, color=GREY,
             transform=axD.get_xaxis_transform())

axD.set_xticks([1, 2, 3])
axD.set_xticklabels(["VIX<15\n(low)", "15–22\n(medium)", "VIX≥22\n(high)"], fontsize=8)
axD.set_ylabel("TDI", fontsize=9)
axD.set_ylim(0.85, 2.2)
axD.set_title("D   TDI by Volatility Regime", fontsize=10, fontweight="bold", loc="left")

# ANOVA test
f_stat, p_anova = stats.f_oneway(vix_low, vix_med, vix_high)
axD.text(2, 2.12, f"One-way ANOVA: F={f_stat:.1f}, p={p_anova:.4f}",
         ha="center", fontsize=7, color=GREY,
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=GREY, lw=0.5))

# ── Overall title & caption ───────────────────────────────────────────────────

fig.suptitle(
    "Empirical Validation of Chronotypic Market Ecology\n"
    r"SEC 13-F Institutional Holdings  $\cdot$  Top 150 Filers  $\cdot$  2013 Q1 – 2024 Q3  $\cdot$  "
    f"$r_{{\\mathrm{{TDI,VIX}}}}={r_main:.3f}$, $p={p_main:.4f}$, $n={n_q}$ quarters",
    fontsize=10, fontweight="bold", y=0.97,
)

fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Saved {OUT}  ({OUT.stat().st_size // 1024} KB)")
