"""
tl_sweep_v2.py — High-quality multi-run sweep to find the true TL peak κh.

Problem with prior sweep:
  TL = 1/(vol * |ACF_lag1|) → when ACF_lag1 ≈ 0, TL → ∞ spuriously.
  Single-run noise dominated. This version uses:
    - 50 seeds per κh point (vs 10 before)
    - Fine grid: κh = 0, 0.1, ..., 1.5, then 0.25 steps to 6.0
    - Median TL per κh point (robust against inf outliers)
    - Filtered TL using only runs where |ACF_lag1| > 0.01

Usage:
    cd /Users/sanjaysubramania/cme_validation
    python tl_sweep_v2.py
"""

import sys
import os
import numpy as np

# Ensure we import from the right directory
sys.path.insert(0, "/Users/sanjaysubramania/cme_validation")
from cme_canonical import simulate_one_run

# ── Grid ──────────────────────────────────────────────────────────────────────
# Fine grid 0.0–1.5 (step 0.10), then coarser 1.75–6.0 (step 0.25)
kh_fine   = np.round(np.arange(0.0, 1.51, 0.10), 2)
kh_coarse = np.round(np.arange(1.75, 6.01, 0.25), 2)
KH_GRID   = np.concatenate([kh_fine, kh_coarse])

N_SEEDS        = 50
ACF_THRESHOLD  = 0.01   # |ACF_lag1| must exceed this to be "valid"

# ── Run sweep ─────────────────────────────────────────────────────────────────
print("=" * 65)
print("TL SWEEP v2 — 50 seeds × fine grid — median-based")
print("=" * 65)
print()
print(f"{'κh':>6}  {'median_TL':>14}  {'mean_TL':>14}  "
      f"{'n_valid':>8}  {'n_inf':>6}  {'med_|ACF|':>10}")
print("-" * 70)

results = {}   # kh → list of raw run dicts

for kh in KH_GRID:
    runs = []
    for seed in range(N_SEEDS):
        r = simulate_one_run(kh=float(kh), seed=seed)
        runs.append(r)

    tl_all    = np.array([r["temporal_liquidity"]  for r in runs])
    acf_all   = np.array([abs(r["acf_lag1"])        for r in runs])

    # Median (handles inf gracefully — np.nanmedian ignores nan, but infs sort high)
    # Replace inf with nan for median computation
    tl_finite   = np.where(np.isfinite(tl_all), tl_all, np.nan)
    median_tl   = float(np.nanmedian(tl_finite))
    mean_tl     = float(np.nanmean(tl_finite))
    n_inf       = int(np.sum(~np.isfinite(tl_all)))

    # Filtered: only runs where |ACF_lag1| > threshold
    valid_mask  = acf_all > ACF_THRESHOLD
    n_valid     = int(valid_mask.sum())
    tl_valid    = tl_all[valid_mask]
    # Replace any remaining inf in valid set
    tl_valid_f  = np.where(np.isfinite(tl_valid), tl_valid, np.nan)
    median_tl_v = float(np.nanmedian(tl_valid_f)) if n_valid > 0 else np.nan
    med_acf     = float(np.nanmedian(acf_all))

    results[float(kh)] = dict(
        median_tl=median_tl,
        mean_tl=mean_tl,
        median_tl_valid=median_tl_v,
        n_valid=n_valid,
        n_inf=n_inf,
        med_acf=med_acf,
        runs=runs,
    )

    print(f"{kh:>6.2f}  {median_tl:>14.4e}  {mean_tl:>14.4e}  "
          f"{n_valid:>5}/{N_SEEDS}  {n_inf:>6}  {med_acf:>10.4f}",
          flush=True)

print("-" * 70)

# ── Find peak (median-based, all runs) ───────────────────────────────────────
finite_kh = {kh: v["median_tl"] for kh, v in results.items()
             if np.isfinite(v["median_tl"])}
peak_kh_all   = max(finite_kh, key=finite_kh.__getitem__)
peak_tl_all   = finite_kh[peak_kh_all]

# Find peak using filtered (valid ACF) median
finite_kh_v = {kh: v["median_tl_valid"] for kh, v in results.items()
               if np.isfinite(v["median_tl_valid"])}
peak_kh_v   = max(finite_kh_v, key=finite_kh_v.__getitem__)
peak_tl_v   = finite_kh_v[peak_kh_v]

print()
print(f"PEAK (median, all runs) :  κh={peak_kh_all:.2f}  (median TL = {peak_tl_all:.3e})")
print(f"PEAK (median, |ACF|>{ACF_THRESHOLD}) :  κh={peak_kh_v:.2f}  (median TL = {peak_tl_v:.3e})")

# ── Verdict ───────────────────────────────────────────────────────────────────
def verdict(kh_val):
    if abs(kh_val - 0.25) <= 0.10:
        return f"prior estimate 0.25"
    elif abs(kh_val - 0.50) <= 0.10:
        return f"figure annotation 0.50"
    elif abs(kh_val - 0.75) <= 0.10:
        return f"text/caption 0.75"
    else:
        return f"new value {kh_val:.2f} (neither paper claim)"

print()
print(f"VERDICT (all-runs median):  closest to → {verdict(peak_kh_all)}")
print(f"VERDICT (filtered median):  closest to → {verdict(peak_kh_v)}")

# ── Choose canonical peak (prefer filtered) ────────────────────────────────
canonical_peak = peak_kh_v  # ACF-filtered is more reliable

# ── Update PAPER_PATCHES.md ──────────────────────────────────────────────────
patches_path = "/Users/sanjaysubramania/cme_validation/PAPER_PATCHES.md"

# Read existing content (if any) to preserve E2/E3 patches
existing = ""
try:
    with open(patches_path) as f:
        existing = f.read()
except FileNotFoundError:
    pass

# Build updated E1 block
e1_block = f"""
══════════════════════════════════════════════════════════════
PATCH E1 — Temporal Liquidity peak (Section 4.5 + Fig 6b caption)
           UPDATED by tl_sweep_v2.py  (50 seeds × fine grid, median)
══════════════════════════════════════════════════════════════

Sweep method : 50 seeds per κh, fine grid (0–1.5 step 0.10, then 0.25 steps)
Peak estimate: median TL, runs filtered by |ACF_lag1| > {ACF_THRESHOLD}

  All-runs median peak:   κh = {peak_kh_all:.2f}  (TL = {peak_tl_all:.3e})
  ACF-filtered peak:      κh = {peak_kh_v:.2f}  (TL = {peak_tl_v:.3e})
  Canonical (adopted):    κh = {canonical_peak:.2f}

Paper text/caption says: κh ≈ 0.75
Paper figure annotation: κh = 0.50
Measured canonical:      κh = {canonical_peak:.2f}  → {verdict(canonical_peak).upper()}

OLD (Section 4.5, third paragraph):
  "Temporal Liquidity peaks at moderate κ_h ≈ 0.75 (Fig. 6b), where the
   network is connected enough for price signals to propagate but not so
   homophilic as to fragment into insulated cliques."

NEW:
  "Temporal Liquidity peaks at moderate κ_h ≈ {canonical_peak:.2f} (Fig. 6b),
   where the network is connected enough for price signals to propagate
   but not so homophilic as to fragment into insulated cliques."

OLD (Figure 6b caption):
  "TL peaks at κ_h ≈ 0.75; moderate connectivity is optimal."

NEW:
  "TL peaks at κ_h ≈ {canonical_peak:.2f}; moderate connectivity is optimal."

ACTION: Update the star annotation in Figure 6b to 'Peak κ_h = {canonical_peak:.2f}'
        so text, caption, and figure are mutually consistent.
"""

# Try to replace just the E1 section in existing patches; otherwise prepend
e1_header = "PATCH E1"
if e1_header in existing:
    # Replace from E1 header to the next ══ block (or end)
    lines = existing.split("\n")
    out_lines = []
    in_e1 = False
    replaced = False
    for line in lines:
        if e1_header in line and not replaced:
            in_e1 = True
            # Inject updated block
            out_lines.append(e1_block)
            replaced = True
        elif in_e1:
            # Skip old E1 content until we hit the next === block or PATCH E2
            if line.startswith("══") and "PATCH E1" not in line:
                in_e1 = False
                out_lines.append(line)
            # else skip
        else:
            out_lines.append(line)
    new_content = "\n".join(out_lines)
else:
    header = "# Paper Text Patches — E1, E2, E3\nGenerated by tl_sweep_v2.py\n"
    new_content = header + e1_block + existing

with open(patches_path, "w") as f:
    f.write(new_content)

print()
print(f"PAPER_PATCHES.md updated: {patches_path}")
print()
print("=" * 65)
print("SUMMARY")
print("=" * 65)
print(f"  κh sweep: {len(KH_GRID)} points × {N_SEEDS} seeds = {len(KH_GRID)*N_SEEDS} runs")
print(f"  TL peak (all-runs  median): κh = {peak_kh_all:.2f}")
print(f"  TL peak (ACF-filtered med): κh = {peak_kh_v:.2f}  ← canonical")
print(f"  Closest paper claim: {verdict(canonical_peak)}")
if abs(canonical_peak - 0.50) <= 0.10:
    print("  → Figure annotation (0.50) is correct; text/caption (0.75) needs fixing.")
elif abs(canonical_peak - 0.75) <= 0.10:
    print("  → Text/caption (0.75) is correct; figure annotation (0.50) needs fixing.")
elif abs(canonical_peak - 0.25) <= 0.10:
    print("  → Neither paper claim correct; both need updating to 0.25.")
else:
    print(f"  → Both paper claims wrong; true peak is {canonical_peak:.2f}.")
print("=" * 65)
