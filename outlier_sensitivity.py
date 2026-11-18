#!/usr/bin/env python3
"""
outlier_sensitivity.py — Assess influence of 2022 Q4 on the TDI–VIX correlation.

Loads empirical_tdi_results.csv (produced by empirical_tdi.py) and computes:
  1. Pearson r(TDI, VIX) with all quarters (should be ~-0.526)
  2. Pearson r(TDI, VIX) with 2022 Q4 excluded
"""

import pandas as pd
from scipy import stats

CSV_PATH = "/Users/sanjaysubramania/cme_validation/empirical_tdi_results.csv"

df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} quarters from {CSV_PATH}")

# Full-sample correlation
r_full, p_full = stats.pearsonr(df["TDI"], df["VIX_avg"])
n_full = len(df)
print(f"\nFull sample (n={n_full}):")
print(f"  r(TDI, VIX) = {r_full:.3f}  (p = {p_full:.4f})")

# Exclude 2022 Q4
mask = ~((df["year"] == 2022) & (df["quarter"] == 4))
df_excl = df[mask]
r_excl, p_excl = stats.pearsonr(df_excl["TDI"], df_excl["VIX_avg"])
n_excl = len(df_excl)
print(f"\nExcluding 2022 Q4 (n={n_excl}):")
print(f"  r(TDI, VIX) = {r_excl:.3f}  (p = {p_excl:.4f})")

print(f"\nChange in r: {r_full:.3f} -> {r_excl:.3f}  (delta = {r_excl - r_full:+.3f})")
