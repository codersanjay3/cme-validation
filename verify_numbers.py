"""
verify_numbers.py — Run canonical CME simulation (30 seeds, kh=0 vs kh=6)
and output the exact TMFI ratio and paired t-stat for paper.

This resolves issues 3.1 and 7.1 identified in the fundamental audit.
"""
import sys
sys.path.insert(0, "/Users/sanjaysubramania/cme_validation")

# Import only what we need from cme_canonical
from cme_canonical import simulate_one_run
import numpy as np
from scipy import stats

N_SEEDS = 30
KH_LOW  = 0.0
KH_HIGH = 6.0

print(f"Running {N_SEEDS} seeds at kh={KH_LOW} and kh={KH_HIGH}...")
print("(This takes ~2-3 minutes for 60 runs)\n")

vols_low, vols_high = [], []
tmfi_low, tmfi_high = [], []

for seed in range(N_SEEDS):
    r0 = simulate_one_run(kh=KH_LOW,  seed=seed)
    r6 = simulate_one_run(kh=KH_HIGH, seed=seed)
    vols_low.append(r0["volatility"])
    vols_high.append(r6["volatility"])
    tmfi_low.append(r0["tmfi"])
    tmfi_high.append(r6["tmfi"])
    print(f"  seed {seed:2d}: vol0={r0['volatility']:.6f}  vol6={r6['volatility']:.6f}"
          f"  tmfi0={r0['tmfi']:.6f}  tmfi6={r6['tmfi']:.6f}")

vols_low  = np.array(vols_low)
vols_high = np.array(vols_high)
tmfi_low  = np.array(tmfi_low)
tmfi_high = np.array(tmfi_high)

# Paired t-test (same seed at kh=0 vs kh=6)
t_stat, p_val = stats.ttest_rel(vols_low, vols_high)

vol_ratio  = vols_low.mean()  / vols_high.mean()
tmfi_ratio = tmfi_low.mean()  / tmfi_high.mean()

print(f"\n{'='*60}")
print(f"RESULTS ({N_SEEDS} seeds, paired design)")
print(f"{'='*60}")
print(f"Volatility kh=0  : {vols_low.mean():.6f} ± {vols_low.std():.6f}")
print(f"Volatility kh=6  : {vols_high.mean():.6f} ± {vols_high.std():.6f}")
print(f"Volatility ratio : {vol_ratio:.4f}x   [paper claims: 1.310x]")
print(f"Paired t-stat    : {t_stat:.3f}       [paper claims: 5.57, prior runs: 9.96/12.6]")
print(f"p-value          : {p_val:.2e}")
print()
print(f"TMFI kh=0        : {tmfi_low.mean():.6f} ± {tmfi_low.std():.6f}")
print(f"TMFI kh=6        : {tmfi_high.mean():.6f} ± {tmfi_high.std():.6f}")
print(f"TMFI ratio       : {tmfi_ratio:.4f}x   [paper claims: 14.25x, prior runs: ~15x]")
