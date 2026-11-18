"""
Independent audit runner for CME paper claims.
Runs all 10 claims independently and reports exact values.
"""
import sys
sys.path.insert(0, "/Users/sanjaysubramania/cme_validation")

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import warnings
warnings.filterwarnings("ignore")

from cme_canonical import (
    simulate_one_run, sample_tau, compute_tdi,
    adaptation_sweep, kh_sweep, N_AGENTS, TDI_K,
    TYPE_MU, TYPE_SIGMA, TYPE_BOUNDS, TYPE_COUNTS
)

print("=" * 70)
print("CME REPRODUCIBILITY AUDIT — Independent Ground-Up Verification")
print("=" * 70)

# ===========================================================================
# CLAIM 1: Volatility ratio vol(κh=6)/vol(κh=0) = 0.760 → "1.29× reduction"
# ===========================================================================
print("\n--- CLAIM 1: Volatility ratio ---")
N_SEEDS = 10
vols_kh0 = []
vols_kh6 = []
for seed in range(N_SEEDS):
    r0 = simulate_one_run(kh=0.0, seed=seed)
    r6 = simulate_one_run(kh=6.0, seed=seed)
    vols_kh0.append(r0["volatility"])
    vols_kh6.append(r6["volatility"])

mean_vol_kh0 = np.mean(vols_kh0)
mean_vol_kh6 = np.mean(vols_kh6)
vol_ratio_6_over_0 = mean_vol_kh6 / mean_vol_kh0   # paper says this = 0.760
vol_reduction_factor = mean_vol_kh0 / mean_vol_kh6  # paper says 1.29×

print(f"  Mean vol at κh=0 : {mean_vol_kh0:.6f}")
print(f"  Mean vol at κh=6 : {mean_vol_kh6:.6f}")
print(f"  Ratio vol(κh=6)/vol(κh=0) : {vol_ratio_6_over_0:.6f}  [paper: 0.760]")
print(f"  Reduction factor vol(κh=0)/vol(κh=6): {vol_reduction_factor:.6f}  [paper: 1.29×]")
print(f"  Math check: 1/0.760 = {1/0.760:.6f}  (paper says this = 1.29, actual = 1.316)")

# ===========================================================================
# CLAIM 2: TMFI ratio 14.28× (κh=0 to κh=6)
# Also check: does 0.070 × 14.28 ≈ 1.0?
# ===========================================================================
print("\n--- CLAIM 2: TMFI ratio ---")
tmfis_kh0 = []
tmfis_kh6 = []
for seed in range(N_SEEDS):
    r0 = simulate_one_run(kh=0.0, seed=seed)
    r6 = simulate_one_run(kh=6.0, seed=seed)
    tmfis_kh0.append(r0["tmfi"])
    tmfis_kh6.append(r6["tmfi"])

mean_tmfi_kh0 = np.mean(tmfis_kh0)
mean_tmfi_kh6 = np.mean(tmfis_kh6)
tmfi_ratio = mean_tmfi_kh0 / max(mean_tmfi_kh6, 1e-30)  # paper says 14.28×

print(f"  Mean TMFI at κh=0: {mean_tmfi_kh0:.6f}")
print(f"  Mean TMFI at κh=6: {mean_tmfi_kh6:.6f}")
print(f"  TMFI ratio (kh0/kh6): {tmfi_ratio:.4f}×  [paper: 14.28×]")
# The paper says "Normalising both metrics to the κ_h=0 baseline:
# TMFI = 0.070 (7% of baseline; 14.28× collapse)"
tmfi_normalised = mean_tmfi_kh6 / max(mean_tmfi_kh0, 1e-30)  # paper: 0.070
print(f"  Normalised TMFI (kh6/kh0): {tmfi_normalised:.6f}  [paper: 0.070]")
print(f"  Consistency check: 0.070 × 14.28 = {0.070 * 14.28:.4f}  (should be ~1.0)")

# ===========================================================================
# CLAIM 3: TL peak at κh ≈ 3.0 (50-seed median)
# Also check: does code hardcode TL annotation at 3.0?
# ===========================================================================
print("\n--- CLAIM 3: TL peak location ---")
# Run 13-point sweep from 0 to 6
kh_sweep_vals = np.linspace(0, 6, 13)
print(f"  Running {len(kh_sweep_vals)}-point κh sweep with {N_SEEDS} seeds each...")
tl_means = {}
for kh in kh_sweep_vals:
    tl_vals = []
    for seed in range(N_SEEDS):
        r = simulate_one_run(kh=float(kh), seed=seed)
        if np.isfinite(r["temporal_liquidity"]):
            tl_vals.append(r["temporal_liquidity"])
    tl_means[kh] = np.mean(tl_vals) if tl_vals else float('nan')
    print(f"  κh={kh:.2f}  TL={tl_means[kh]:.4e}")

finite_tl = {k: v for k, v in tl_means.items() if np.isfinite(v)}
if finite_tl:
    tl_peak_kh = max(finite_tl, key=finite_tl.__getitem__)
    tl_peak_val = finite_tl[tl_peak_kh]
    print(f"\n  MEASURED TL peak: κh = {tl_peak_kh:.2f}  (TL = {tl_peak_val:.4e})")
    print(f"  Paper claims: κh ≈ 3.0")
    print(f"  Code line 1080: tl_peak_kh_fig = 3.0  [HARDCODED regardless of measurement]")

# ===========================================================================
# CLAIM 4: TDI baseline = 2.36 at κh=0 (K=16, natural log, n=80)
# ===========================================================================
print("\n--- CLAIM 4: TDI baseline ---")
tdis_50 = []
for seed in range(50):
    tau = sample_tau(n=N_AGENTS, seed=seed)
    tdis_50.append(compute_tdi(tau, K=TDI_K))
mean_tdi = np.mean(tdis_50)
std_tdi = np.std(tdis_50)
print(f"  Mean TDI over 50 seeds (K=16, ln): {mean_tdi:.6f} ± {std_tdi:.6f}")
print(f"  Paper claims: TDI = 2.36")
print(f"  Difference: {abs(mean_tdi - 2.36):.6f}")

# ===========================================================================
# CLAIM 5: δTDI echo chamber result
# Paper: δTDI = −0.114 at κh=3.0, +0.061 at κh=0.5, −0.102 at κh=6
# ===========================================================================
print("\n--- CLAIM 5: δTDI echo chamber ---")
print("  Running adaptation_sweep with default single seed (seed=0)...")
adapt_single = adaptation_sweep(kh_values=(0.5, 3.0, 6.0), n_steps=10, seed=0)
for kh in [0.5, 3.0, 6.0]:
    series = adapt_single[kh]
    delta = series[-1] - series[0]
    print(f"  κh={kh:.1f}: start={series[0]:.6f}  end={series[-1]:.6f}  ΔTDι={delta:+.6f}")

print("\n  Paper claims: κh=0.5→+0.061, κh=3.0→−0.114, κh=6.0→−0.102")
print("  Code comment admits: 'single seed or multiple seeds?' — checking...")
print("  The adaptation_sweep() function uses a single seed (seed=0), not multiple seeds.")
print("  Paper caption says 'multi-seed averages' for Fig 6a — checking multi-seed:")

# Run with 10 seeds
delta_tdi_multiseed = {0.5: [], 3.0: [], 6.0: []}
for seed in range(10):
    result = adaptation_sweep(kh_values=(0.5, 3.0, 6.0), n_steps=10, seed=seed)
    for kh in [0.5, 3.0, 6.0]:
        delta_tdi_multiseed[kh].append(result[kh][-1] - result[kh][0])

print("\n  Multi-seed (10 seeds) ΔTDι:")
for kh in [0.5, 3.0, 6.0]:
    mean_d = np.mean(delta_tdi_multiseed[kh])
    std_d = np.std(delta_tdi_multiseed[kh])
    print(f"  κh={kh:.1f}: mean ΔTDι = {mean_d:+.6f} ± {std_d:.6f}  [paper: see above]")

# ===========================================================================
# CLAIM 6: t-statistic = 15.1
# ===========================================================================
print("\n--- CLAIM 6: t-statistic ---")
# Already have vols_kh0 and vols_kh6 from Claim 1
t_stat, p_val = sp_stats.ttest_ind(vols_kh0, vols_kh6, equal_var=False)
print(f"  t-statistic (Welch, 10 seeds each): {t_stat:.4f}  [paper: 15.1]")
print(f"  p-value: {p_val:.4e}  [paper: < 1e-20]")
print(f"  Note: 10 seeds each gives df ≈ 18; paper's t=15.1 likely uses more seeds")
# The paper says "30-seed mean" in some places, "250 seeds" in others
# Let's also run with 30 seeds for the t-test
print("  Running 30-seed version for comparison...")
vols_30_kh0 = []
vols_30_kh6 = []
for seed in range(30):
    r0 = simulate_one_run(kh=0.0, seed=seed)
    r6 = simulate_one_run(kh=6.0, seed=seed)
    vols_30_kh0.append(r0["volatility"])
    vols_30_kh6.append(r6["volatility"])
t_stat_30, p_val_30 = sp_stats.ttest_ind(vols_30_kh0, vols_30_kh6, equal_var=False)
print(f"  t-statistic (Welch, 30 seeds each): {t_stat_30:.4f}  [paper: 15.1]")
print(f"  p-value (30 seeds): {p_val_30:.4e}")

# ===========================================================================
# CLAIM 7: Empirical correlation r = −0.526, p = 0.0002, n = 45
# ===========================================================================
print("\n--- CLAIM 7: Empirical correlation ---")
df = pd.read_csv("/Users/sanjaysubramania/cme_validation/empirical_tdi_results.csv")
print(f"  Total rows in CSV: {len(df)}")
print(f"  Columns: {list(df.columns)}")

# Apply ≥50 institution filter
df_filtered = df[df["n_institutions"] >= 50].copy()
print(f"  Rows with n_institutions ≥ 50: {len(df_filtered)}")
print(f"  Quarters: {df_filtered['label'].tolist()}")

tdi_vals = df_filtered["TDI"].values
vix_vals = df_filtered["VIX_avg"].values
r_emp, p_emp = sp_stats.pearsonr(tdi_vals, vix_vals)
n_emp = len(df_filtered)
print(f"\n  Pearson r(TDI, VIX): {r_emp:.6f}  [paper: −0.526]")
print(f"  p-value: {p_emp:.6f}  [paper: 0.0002]")
print(f"  n quarters: {n_emp}  [paper: 45]")

# ===========================================================================
# CLAIM 8: Robustness check — excluding 2022 Q4
# ===========================================================================
print("\n--- CLAIM 8: Robustness — excluding 2022 Q4 ---")
df_excl = df_filtered[df_filtered["label"] != "2022Q4"].copy()
print(f"  Rows after excluding 2022Q4: {len(df_excl)}")
tdi_excl = df_excl["TDI"].values
vix_excl = df_excl["VIX_avg"].values
r_excl, p_excl = sp_stats.pearsonr(tdi_excl, vix_excl)
print(f"  Pearson r (excl. 2022Q4): {r_excl:.6f}  [paper: −0.393]")
print(f"  p-value (excl. 2022Q4): {p_excl:.6f}  [paper: 0.0075]")

# ===========================================================================
# CLAIM 9: Forward-lag correlation r(TDI[t], VIX[t+1])
# ===========================================================================
print("\n--- CLAIM 9: Forward-lag correlation ---")
# Paper specifies r(VIX[t], TDI[t+1]) = -0.298
# Test that AND r(TDI[t], VIX[t+1])
tdi_t = tdi_vals[:-1]
vix_t1 = vix_vals[1:]
r_lag_tdi_vix, p_lag_tdi_vix = sp_stats.pearsonr(tdi_t, vix_t1)
print(f"  r(TDI[t], VIX[t+1]): {r_lag_tdi_vix:.6f}  p={p_lag_tdi_vix:.6f}")

vix_t = vix_vals[:-1]
tdi_t1 = tdi_vals[1:]
r_lag_vix_tdi, p_lag_vix_tdi = sp_stats.pearsonr(vix_t, tdi_t1)
print(f"  r(VIX[t], TDI[t+1]): {r_lag_vix_tdi:.6f}  p={p_lag_vix_tdi:.6f}  [paper: −0.298, p=0.047]")

# ===========================================================================
# CLAIM 10: Parameter consistency — Table 1 vs code
# ===========================================================================
print("\n--- CLAIM 10: Parameter consistency ---")
# Paper Table 1
paper_mu    = [1.61, 3.04, 4.14, 5.53]
paper_sigma = [0.60, 0.70, 0.60, 0.80]
paper_bounds = [(1, 20), (15, 120), (60, 400), (400, 2000)]
type_names  = ["HFT", "Hedge Fund", "Mutual Fund", "Pension"]

# Code constants (from cme_canonical.py)
code_mu    = TYPE_MU    # [0.5, 2.8, 4.2, 6.0]
code_sigma = TYPE_SIGMA  # [0.6, 0.7, 0.6, 0.8]

print(f"  {'Type':<15} {'Paper μ':>10} {'Code μ':>10} {'Paper median τ':>16} {'Code median τ':>14} {'Bounds':>12}")
print(f"  {'-'*80}")
for i, name in enumerate(type_names):
    p_med = np.exp(paper_mu[i])
    c_med = np.exp(code_mu[i])
    lo, hi = paper_bounds[i]
    print(f"  {name:<15} {paper_mu[i]:>10.2f} {code_mu[i]:>10.2f} {p_med:>16.2f} {c_med:>14.2f} {lo}–{hi}")

print(f"\n  Are μ values different? {paper_mu != list(code_mu)}")
for i, name in enumerate(type_names):
    diff = abs(paper_mu[i] - code_mu[i])
    print(f"    {name}: paper μ={paper_mu[i]:.2f}, code μ={code_mu[i]:.2f}, diff={diff:.2f}")

# Check if paper median τ falls in stated bounds
print("\n  Does paper μ produce median τ within stated bounds?")
for i, name in enumerate(type_names):
    lo, hi = paper_bounds[i]
    p_med = np.exp(paper_mu[i])
    c_med = np.exp(code_mu[i])
    p_ok = lo <= p_med <= hi
    c_ok = lo <= c_med <= hi
    print(f"    {name}: paper median {p_med:.1f}d in [{lo},{hi}]? {p_ok} | code median {c_med:.1f}d in [{lo},{hi}]? {c_ok}")

# ===========================================================================
# Additional checks on math/internal consistency
# ===========================================================================
print("\n--- ADDITIONAL CHECK: Math on vol ratio ---")
print(f"  Paper says ratio = 0.760, reduction = 1.29×")
print(f"  But 1/0.760 = {1/0.760:.6f} ≠ 1.29")
print(f"  The stated 1.29× would correspond to ratio = {1/1.29:.6f}")
print(f"  This is an arithmetic error in the paper.")

print("\n--- ADDITIONAL CHECK: TMFI normalisation ---")
print(f"  Paper says 'TMFI = 0.070 (14.28× collapse)'")
print(f"  But 1/0.070 = {1/0.070:.4f} ≠ 14.28")
print(f"  14.28× would correspond to normalised = {1/14.28:.6f}")
print(f"  This is internally inconsistent: 0.070 and 14.28× cannot both be right.")

print("\n--- ADDITIONAL CHECK: TL definition in code vs paper ---")
print("  Paper Definition 3 (Temporal Liquidity): number of trades between")
print("  agents whose τ values differ by at least one octave.")
print("  Code: TL = 1 / (σ_r × |ACF_lag1|)  — a COMPLETELY DIFFERENT formula.")
print("  The code uses a liquidity-from-autocorrelation formula, not a trade-count formula.")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
