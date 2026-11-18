"""
Task 1 — Gamma Sensitivity Analysis
=====================================
CME Project Briefing Section 6, Task 1 (CRITICAL priority).

Sweeps gamma ∈ {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50}
Each gamma: 30 kappa_h levels × 20 seeds = 600 runs
Total: 8 × 600 = 4,800 simulation runs

Outputs:
  Figure A : 8-panel grid (normalised σ and TMFI divergence per gamma)
  Figure B : Overlay of residual fragility gap (norm. TMFI - norm. σ) vs kh
  Figure C : Dual heatmap (gamma × kh) showing TMFI and volatility
  CSVs     : outputs/data/gamma_sweep_g*.csv + gamma_sweep_all.csv

Success criteria (briefing):
  If calm-fragmented divergence holds for all 8 gamma values →
    "Core results are robust to gamma in [0.05, 0.50]."
  If only near gamma=0.20 →  document the boundaries precisely.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import os, sys, time

# ── Path setup ────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from simulation.core import (
    sample_taus, build_network, run_market, diagnostics, tdi, spectral_gap
)

OUT_DATA = os.path.join(PROJECT_ROOT, 'outputs', 'data')
OUT_FIG  = os.path.join(PROJECT_ROOT, 'outputs', 'figures')
os.makedirs(OUT_DATA, exist_ok=True)
os.makedirs(OUT_FIG, exist_ok=True)

# ── Run configuration (briefing Section 2.1) ──────────────────────────────────
N        = 120        # agents
T        = 700        # time steps
N_KH     = 30         # kappa_h grid points
N_SEEDS  = 20         # random seeds per condition
MAX_DEG  = 14         # max out-degree per agent (briefing 2.5)
FUND_VOL = 0.010      # fundamental shock std dev
NOISE_VOL= 0.005      # noise vol (idiosyncratic demand + price noise)
LAM      = 0.008      # price-impact coefficient

GAMMAS   = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
KH_VALS  = np.linspace(0.0, 6.0, N_KH)

# ── Colour scheme (briefing Section 7.4) ──────────────────────────────────────
NC = {
    'navy':     '#1E2761',
    'gold':     '#FFD166',
    'ice_blue': '#CADCFC',
    'blue':     '#0072B2',
    'orange':   '#E69F00',
    'green':    '#009E73',
    'red':      '#CC3311',
    'purple':   '#882255',
    'teal':     '#44AA99',
    'gray':     '#666666',
}

# One colour per gamma value (dark-to-light spectrum)
GAMMA_COLORS = [
    '#1E2761', '#0072B2', '#44AA99', '#009E73',
    '#E69F00', '#CC3311', '#882255', '#440154',
]

plt.rcParams.update({
    'font.family':          'serif',
    'font.size':            9,
    'axes.labelsize':       12,   # ≥12pt (journal requirement)
    'axes.titlesize':       11,
    'xtick.labelsize':      10,
    'ytick.labelsize':      10,
    'legend.fontsize':      9,
    'savefig.dpi':          300,
    'axes.linewidth':       0.8,
    'lines.linewidth':      1.6,
    'axes.spines.top':      False,
    'axes.spines.right':    False,
    'axes.grid':            True,
    'grid.alpha':           0.25,
    'grid.linewidth':       0.4,
    'figure.facecolor':     'white',
})

z_ci = 1.96   # 95% CI multiplier


def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor('#FAFAFA')
    for sp in ax.spines.values():
        sp.set_color('#CCCCCC')
    if title:   ax.set_title(title,  fontsize=11, fontweight='bold', pad=6)
    if xlabel:  ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:  ax.set_ylabel(ylabel, fontsize=12)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SWEEP
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 72)
print("  CME — Task 1: Gamma Sensitivity Analysis")
print("=" * 72)
print(f"  N={N}, T={T}, kh: {N_KH} levels × {N_SEEDS} seeds = {N_KH*N_SEEDS} runs/gamma")
print(f"  Gamma values: {GAMMAS}")
total_runs = len(GAMMAS) * N_KH * N_SEEDS
print(f"  Total runs: {len(GAMMAS)} × {N_KH} × {N_SEEDS} = {total_runs:,}")
print()

# Sample tau distribution once — fixed across all gamma values
# (tau values are fixed in main sweep; only gamma changes)
taus_base, labels_base = sample_taus(N, seed=42)
print(f"  Baseline tau distribution: N={len(taus_base)}, TDI={tdi(taus_base):.3f}")
print()

all_results = {}   # gamma -> pd.DataFrame
t_start = time.time()
total_done = 0

for gi, gamma in enumerate(GAMMAS):
    t_gamma_start = time.time()
    print(f"[{gi+1}/{len(GAMMAS)}] gamma = {gamma:.2f}  "
          f"({N_KH*N_SEEDS} runs)...")
    records = []

    for ki, kh in enumerate(KH_VALS):
        for seed in range(N_SEEDS):
            # Build network once per (kh, seed) condition.
            # Tau is fixed so edge probabilities are deterministic given kh;
            # only which edges are sampled varies by seed.
            adj = build_network(
                taus_base, kappa_h=kh, max_deg=MAX_DEG,
                seed=ki * 10000 + seed
            )

            gp, lr, fn, lp, lam2 = run_market(
                taus_base, adj, T=T,
                lam=LAM, gamma=gamma,
                fund_vol=FUND_VOL, noise_vol=NOISE_VOL,
                seed=ki * 10000 + seed + 500000
            )

            d = diagnostics(gp, lr, fn, lp, taus_base)
            d['kh']    = float(kh)
            d['seed']  = seed
            d['gamma'] = gamma
            d['lam2']  = lam2
            records.append(d)
            total_done += 1

        # Progress every 10 kh steps
        if (ki + 1) % 10 == 0:
            elapsed = time.time() - t_start
            rate = total_done / elapsed if elapsed > 0 else 1
            remaining = (total_runs - total_done) / rate
            print(f"  kh={kh:.2f}  step {ki+1}/{N_KH}  "
                  f"[{total_done:,}/{total_runs:,} runs, "
                  f"ETA {remaining/60:.1f} min]")

    df = pd.DataFrame(records)
    all_results[gamma] = df

    # Save per-gamma CSV immediately (checkpoint)
    csv_path = os.path.join(OUT_DATA, f'gamma_sweep_g{gamma:.2f}.csv')
    df.to_csv(csv_path, index=False)

    # Quick summary
    mg = df.groupby('kh').mean(numeric_only=True)
    vm = mg['vol'].values
    tm = mg['tmfi_v'].values
    vol_ratio  = vm.max() / (vm.min() + 1e-12)
    tmfi_ratio = tm.max() / (tm.min() + 1e-12)
    t_elapsed  = time.time() - t_gamma_start
    print(f"  → Vol ratio: {vol_ratio:.2f}×  |  TMFI ratio: {tmfi_ratio:.1f}×  "
          f"|  ({t_elapsed:.0f}s)\n")

# Save combined CSV
combined = pd.concat(list(all_results.values()), ignore_index=True)
combined.to_csv(os.path.join(OUT_DATA, 'gamma_sweep_all.csv'), index=False)
print(f"  Combined CSV saved ({len(combined):,} rows)\n")

# ── Compute per-gamma summaries ───────────────────────────────────────────────
summaries = {}
for gamma in GAMMAS:
    df   = all_results[gamma]
    mn   = df.groupby('kh').mean(numeric_only=True).reset_index()
    sd   = df.groupby('kh').std(numeric_only=True).reset_index()
    summaries[gamma] = {'mean': mn, 'std': sd}


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE A — 8-panel grid: normalised σ and TMFI divergence per gamma
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Figure A...")

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
fig.suptitle(
    'Figure A — Gamma Sensitivity: Volatility–Fragmentation Divergence\n'
    r'(normalised $\sigma$ and TMFI vs $\kappa_h$; shaded = calm-fragmented zone)',
    fontsize=13, fontweight='bold', y=1.01
)

for idx, gamma in enumerate(GAMMAS):
    ax  = axes[idx // 4][idx % 4]
    mn  = summaries[gamma]['mean']
    sd  = summaries[gamma]['std']
    kh_a = mn['kh'].values
    vm   = mn['vol'].values
    tm   = mn['tmfi_v'].values
    vs   = sd['vol'].values / np.sqrt(N_SEEDS)
    ts   = sd['tmfi_v'].values / np.sqrt(N_SEEDS)

    # Normalise to [0, 1]
    vm_range = vm.max() - vm.min() + 1e-12
    tm_range = tm.max() - tm.min() + 1e-12
    vm_n = (vm - vm.min()) / vm_range
    tm_n = (tm - tm.min()) / tm_range

    # 95% CI bands (normalised)
    vm_lo_n = np.clip((vm - z_ci * vs - vm.min()) / vm_range, 0, 1.2)
    vm_hi_n = np.clip((vm + z_ci * vs - vm.min()) / vm_range, 0, 1.2)
    tm_lo_n = np.clip((tm - z_ci * ts - tm.min()) / tm_range, 0, 1.2)
    tm_hi_n = np.clip((tm + z_ci * ts - tm.min()) / tm_range, 0, 1.2)

    style_ax(ax, xlabel=r'$\kappa_h$', ylabel='Norm. value')

    ax.fill_between(kh_a, vm_lo_n, vm_hi_n, alpha=0.15, color=NC['orange'])
    ax.fill_between(kh_a, tm_lo_n, tm_hi_n, alpha=0.15, color=NC['purple'])
    ax.plot(kh_a, vm_n, color=NC['orange'], lw=2.0,
            label=r'$\sigma$ (norm.)')
    ax.plot(kh_a, tm_n, color=NC['purple'], lw=2.0,
            label='TMFI (norm.)')

    # Calm-fragmented zone: where TMFI is above σ in normalised space
    ax.fill_between(kh_a, vm_n, tm_n,
                    where=(tm_n > vm_n),
                    alpha=0.20, color=NC['red'],
                    label='Calm-fragmented')

    # Statistics
    vol_ratio  = vm.max() / (vm.min() + 1e-12)
    tmfi_ratio = tm.max() / (tm.min() + 1e-12)
    sigma_drop_norm = (vm.max() - vm.min()) / (vm.max() + 1e-12)
    tmfi_drop_norm  = (tm.max() - tm.min()) / (tm.max() + 1e-12)
    residual_gap    = abs(sigma_drop_norm - tmfi_drop_norm)

    ax.set_title(
        f'$\\gamma = {gamma}$  |  '
        f'$\\sigma$: {vol_ratio:.1f}$\\times$  TMFI: {tmfi_ratio:.1f}$\\times$',
        fontsize=10, fontweight='bold'
    )
    ax.set_ylim(-0.08, 1.20)
    ax.text(0.97, 0.04,
            f'Resid. gap: {residual_gap:.2f}',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.25', fc='#fff0f0', ec='none'))

    if idx == 0:
        ax.legend(fontsize=7.5, frameon=True, framealpha=0.92,
                  edgecolor='none', loc='upper right')

fig.tight_layout(pad=1.8)
path_a = os.path.join(OUT_FIG, 'figA_gamma_divergence_panels')
fig.savefig(path_a + '.pdf', bbox_inches='tight')
fig.savefig(path_a + '.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("  Figure A saved.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE B — Residual fragility gap overlay (all gammas on one plot)
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Figure B...")

fig, (ax_main, ax_inset) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(
    r'Figure B — Residual Fragility Gap (norm. TMFI $-$ norm. $\sigma$) vs $\kappa_h$'
    '\nPositive = calm-fragmented regime (core result holds above zero)',
    fontsize=13, fontweight='bold'
)

gap_table = []   # for summary stats

for gi, gamma in enumerate(GAMMAS):
    mn   = summaries[gamma]['mean']
    sd   = summaries[gamma]['std']
    kh_a = mn['kh'].values
    vm   = mn['vol'].values
    tm   = mn['tmfi_v'].values
    vs   = sd['vol'].values / np.sqrt(N_SEEDS)
    ts   = sd['tmfi_v'].values / np.sqrt(N_SEEDS)

    vm_n = (vm - vm.min()) / (vm.max() - vm.min() + 1e-12)
    tm_n = (tm - tm.min()) / (tm.max() - tm.min() + 1e-12)

    gap = tm_n - vm_n   # residual fragility gap

    # 95% CI on the gap (propagate SE)
    vm_se_n = vs / (vm.max() - vm.min() + 1e-12)
    tm_se_n = ts / (tm.max() - tm.min() + 1e-12)
    gap_se  = np.sqrt(vm_se_n**2 + tm_se_n**2)

    ax_main.fill_between(
        kh_a,
        gap - z_ci * gap_se,
        gap + z_ci * gap_se,
        alpha=0.10, color=GAMMA_COLORS[gi]
    )
    ax_main.plot(kh_a, gap, color=GAMMA_COLORS[gi], lw=2.0,
                 label=f'$\\gamma={gamma}$', alpha=0.90)

    gap_table.append({
        'gamma':      gamma,
        'max_gap':    gap.max(),
        'gap_at_kh6': gap[-1],
        'crossover':  kh_a[np.argmax(gap > 0.02)] if (gap > 0.02).any() else np.nan,
        'robust':     gap.max() > 0.05,
    })

ax_main.axhline(0, color='black', ls='--', lw=1.2, alpha=0.7,
                label='Zero (no divergence)')
ax_main.axhspan(0, 1.1, alpha=0.04, color=NC['red'])
style_ax(ax_main,
         xlabel=r'Homophily $\kappa_h$',
         ylabel=r'Norm. TMFI $-$ Norm. $\sigma$')
ax_main.set_ylim(-0.35, 0.85)
ax_main.legend(fontsize=8.5, frameon=True, framealpha=0.95,
               edgecolor='none', bbox_to_anchor=(1.01, 1), loc='upper left')
ax_main.text(0.03, 0.97,
             'Above zero:\nCALM but FRAGMENTED',
             transform=ax_main.transAxes, va='top', fontsize=10,
             color=NC['red'], fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', fc='#fff0f0',
                       ec=NC['red'], alpha=0.85))

# Right panel: max gap and gap at kh=6 per gamma
gap_df = pd.DataFrame(gap_table)
ax_inset.bar(range(len(GAMMAS)),
             gap_df['max_gap'].values,
             color=GAMMA_COLORS, alpha=0.80, label='Max gap')
ax_inset.bar(range(len(GAMMAS)),
             gap_df['gap_at_kh6'].values,
             color=GAMMA_COLORS, alpha=0.45, hatch='///',
             label=r'Gap at $\kappa_h=6$')
ax_inset.axhline(0.05, color=NC['red'], ls=':', lw=1.2,
                 label='Robustness threshold (0.05)')
ax_inset.set_xticks(range(len(GAMMAS)))
ax_inset.set_xticklabels([str(g) for g in GAMMAS], fontsize=10)
style_ax(ax_inset,
         title='Fragility gap by gamma',
         xlabel=r'$\gamma$',
         ylabel='Residual fragility gap')
ax_inset.legend(fontsize=8, frameon=True, framealpha=0.9, edgecolor='none')

fig.tight_layout(pad=1.5)
path_b = os.path.join(OUT_FIG, 'figB_fragility_gap_overlay')
fig.savefig(path_b + '.pdf', bbox_inches='tight')
fig.savefig(path_b + '.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("  Figure B saved.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE C — Heatmap: gamma × kappa_h → TMFI and volatility
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Figure C...")

# Build (n_gamma × n_kh) matrices
tmfi_mat = np.zeros((len(GAMMAS), N_KH))
vol_mat  = np.zeros((len(GAMMAS), N_KH))

for gi, gamma in enumerate(GAMMAS):
    mn = summaries[gamma]['mean']
    tmfi_mat[gi] = mn['tmfi_v'].values
    vol_mat[gi]  = mn['vol'].values

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle(
    r'Figure C — Parameter Space ($\gamma \times \kappa_h$): TMFI, Volatility, and Residual Fragility',
    fontsize=13, fontweight='bold'
)

# --- Panel 1: TMFI heatmap ---
ax = axes[0]
im1 = ax.imshow(
    tmfi_mat, aspect='auto', origin='lower', cmap='YlOrRd',
    extent=[KH_VALS[0], KH_VALS[-1], -0.5, len(GAMMAS) - 0.5]
)
ax.set_yticks(range(len(GAMMAS)))
ax.set_yticklabels([str(g) for g in GAMMAS], fontsize=10)
style_ax(ax,
         title='TMFI (↑ = more fragmentation)',
         xlabel=r'Homophily $\kappa_h$',
         ylabel=r'Friction $\gamma$')
cb1 = plt.colorbar(im1, ax=ax, fraction=0.046, pad=0.04)
cb1.set_label('TMFI', fontsize=10)
cb1.ax.tick_params(labelsize=9)

# --- Panel 2: Volatility heatmap ---
ax = axes[1]
im2 = ax.imshow(
    vol_mat, aspect='auto', origin='lower', cmap='Blues_r',
    extent=[KH_VALS[0], KH_VALS[-1], -0.5, len(GAMMAS) - 0.5]
)
ax.set_yticks(range(len(GAMMAS)))
ax.set_yticklabels([str(g) for g in GAMMAS], fontsize=10)
style_ax(ax,
         title=r'Volatility $\sigma$ (↓ = calmer)',
         xlabel=r'Homophily $\kappa_h$',
         ylabel=r'Friction $\gamma$')
cb2 = plt.colorbar(im2, ax=ax, fraction=0.046, pad=0.04)
cb2.set_label(r'$\sigma$', fontsize=10)
cb2.ax.tick_params(labelsize=9)

# --- Panel 3: Residual fragility gap heatmap ---
gap_mat = np.zeros((len(GAMMAS), N_KH))
for gi, gamma in enumerate(GAMMAS):
    mn = summaries[gamma]['mean']
    vm = mn['vol'].values
    tm = mn['tmfi_v'].values
    vm_n = (vm - vm.min()) / (vm.max() - vm.min() + 1e-12)
    tm_n = (tm - tm.min()) / (tm.max() - tm.min() + 1e-12)
    gap_mat[gi] = tm_n - vm_n

ax = axes[2]
# Diverging colormap: negative=blue (σ dominates), positive=red (fragility dominates)
vmax = np.abs(gap_mat).max()
im3 = ax.imshow(
    gap_mat, aspect='auto', origin='lower', cmap='RdBu_r',
    vmin=-vmax, vmax=vmax,
    extent=[KH_VALS[0], KH_VALS[-1], -0.5, len(GAMMAS) - 0.5]
)
ax.set_yticks(range(len(GAMMAS)))
ax.set_yticklabels([str(g) for g in GAMMAS], fontsize=10)
# Contour line at gap=0
ax.contour(
    np.linspace(KH_VALS[0], KH_VALS[-1], N_KH),
    np.arange(len(GAMMAS)),
    gap_mat,
    levels=[0], colors='black', linewidths=1.5, linestyles='--'
)
style_ax(ax,
         title=r'Residual fragility gap (norm. TMFI $-$ norm. $\sigma$)',
         xlabel=r'Homophily $\kappa_h$',
         ylabel=r'Friction $\gamma$')
cb3 = plt.colorbar(im3, ax=ax, fraction=0.046, pad=0.04)
cb3.set_label('Gap (red = calm-fragmented)', fontsize=9)
cb3.ax.tick_params(labelsize=9)
ax.text(0.97, 0.03, 'Black dashed = divergence boundary',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=8, color='black', style='italic')

fig.tight_layout(pad=1.5)
path_c = os.path.join(OUT_FIG, 'figC_parameter_heatmap')
fig.savefig(path_c + '.pdf', bbox_inches='tight')
fig.savefig(path_c + '.png', bbox_inches='tight', dpi=300)
plt.close(fig)
print("  Figure C saved.")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────────────────────────────────────
total_time = time.time() - t_start
print()
print("=" * 72)
print("TASK 1 — GAMMA SENSITIVITY ANALYSIS: SUMMARY")
print("=" * 72)
print(f"  Total runtime: {total_time/60:.1f} minutes  ({total_done:,} runs)\n")

print(f"  {'gamma':>7}  {'vol@kh=0':>10}  {'vol@kh=6':>10}  "
      f"{'vol_ratio':>10}  {'TMFI@kh=0':>10}  {'TMFI@kh=6':>10}  "
      f"{'max_gap':>9}  {'robust':>8}")
print("  " + "-" * 80)

robust_gammas   = []
nonrobust_gammas = []

for gamma in GAMMAS:
    mn = summaries[gamma]['mean']
    vm = mn['vol'].values
    tm = mn['tmfi_v'].values
    vm_n = (vm - vm.min()) / (vm.max() - vm.min() + 1e-12)
    tm_n = (tm - tm.min()) / (tm.max() - tm.min() + 1e-12)
    gap     = tm_n - vm_n
    vol_ratio = vm[0] / (vm[-1] + 1e-12)
    robust = gap.max() > 0.05

    if robust:
        robust_gammas.append(gamma)
    else:
        nonrobust_gammas.append(gamma)

    # t-test: low kh vs high kh volatility
    df_g  = all_results[gamma]
    lo_v  = df_g[df_g['kh'] < 1.0]['vol']
    hi_v  = df_g[df_g['kh'] > 5.0]['vol']
    t_s, p_v = stats.ttest_ind(lo_v, hi_v) if len(lo_v) > 1 else (0, 1)

    print(f"  {gamma:>7.2f}  {vm[0]:>10.6f}  {vm[-1]:>10.6f}  "
          f"{vol_ratio:>9.2f}×  {tm[0]:>10.6f}  {tm[-1]:>10.6f}  "
          f"{gap.max():>9.3f}  {'✓ YES' if robust else '✗ NO':>8}  "
          f"(p={p_v:.2e})")

print()

# Conclusion
if len(robust_gammas) == len(GAMMAS):
    conclusion = (
        "CONCLUSION: Core results are ROBUST to gamma in [0.05, 0.50].\n"
        "  The calm-fragmented divergence (TMFI > σ in normalised space) holds\n"
        "  across ALL 8 tested gamma values. This strongly validates the model's\n"
        "  main claim and addresses Reviewer Gap 2 from the briefing."
    )
elif len(robust_gammas) > len(GAMMAS) // 2:
    boundary_lo = min(robust_gammas)
    boundary_hi = max(robust_gammas)
    conclusion = (
        f"CONCLUSION: Core results PARTIALLY robust.\n"
        f"  Divergence holds for gamma ∈ [{boundary_lo}, {boundary_hi}].\n"
        f"  Fails for gamma ∈ {nonrobust_gammas}.\n"
        f"  Paper should frame contribution within this range."
    )
else:
    conclusion = (
        f"WARNING: Core results NOT robust across gamma values.\n"
        f"  Divergence holds only for gamma ∈ {robust_gammas}.\n"
        f"  Model may need rethinking per briefing instructions."
    )

print(f"  {conclusion}\n")

# Save gap summary table
gap_df.to_csv(os.path.join(OUT_DATA, 'gamma_gap_summary.csv'), index=False)

print("  Files saved:")
print(f"    outputs/data/gamma_sweep_g*.csv  ({len(GAMMAS)} files)")
print(f"    outputs/data/gamma_sweep_all.csv")
print(f"    outputs/data/gamma_gap_summary.csv")
print(f"    outputs/figures/figA_gamma_divergence_panels.[pdf|png]")
print(f"    outputs/figures/figB_fragility_gap_overlay.[pdf|png]")
print(f"    outputs/figures/figC_parameter_heatmap.[pdf|png]")
print("=" * 72)
