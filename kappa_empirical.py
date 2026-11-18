"""
kappa_empirical.py — Empirical κ_h proxy from SEC 13-F co-holding patterns.

Method (Chalmers suggestion):
  For each quarter, measure the degree to which institutions with similar tau
  hold similar portfolios. If κ_h is high in reality, like-tau institutions
  should converge on similar holdings (temporal echo chambers forming).

  κ̂_h(t) = Pearson r between:
    - portfolio_similarity(i,j) = cosine similarity of weight vectors
    - tau_proximity(i,j)        = exp(-|log τ_i - log τ_j|)
  computed over all institution pairs (i,j) in quarter t.

  A positive and significant quarterly κ̂_h series means like-horizon
  institutions genuinely cluster together — the CME homophily mechanism
  exists in the data, not just the model.

Output:
  - quarterly κ̂_h time series
  - Correlation of κ̂_h with VIX (does measured homophily predict volatility?)
  - Summary statistics printed and saved to kappa_empirical_results.csv
"""

import json, math, csv
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
import yfinance as yf

CACHE_DIR = Path("/Users/sanjaysubramania/cme_validation/edgar_cache")


# ─── load holdings database ──────────────────────────────────────────────────
print("Loading holdings database...")
with open(CACHE_DIR / "holdings_db.json") as f:
    db = json.load(f)

all_ciks   = list(db.keys())
all_qtrs   = sorted({q for cik_data in db.values() for q in cik_data.keys()})
print(f"  {len(all_ciks)} institutions, {len(all_qtrs)} quarters ({all_qtrs[0]}–{all_qtrs[-1]})")


# ─── helper functions ─────────────────────────────────────────────────────────
def portfolio_weights(holdings):
    """Return {cusip: weight} dict normalised to sum=1."""
    total = sum(h["value_k"] for h in holdings)
    if total == 0:
        return {}
    return {h["cusip"]: h["value_k"] / total for h in holdings}


def cosine_sim(w1, w2):
    """Cosine similarity between two sparse weight dicts."""
    common = set(w1) & set(w2)
    if not common:
        return 0.0
    dot   = sum(w1[c] * w2[c] for c in common)
    norm1 = math.sqrt(sum(v**2 for v in w1.values()))
    norm2 = math.sqrt(sum(v**2 for v in w2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def quarterly_turnover(cik, q_curr, q_prev):
    """Portfolio turnover between two quarters for one institution."""
    h_curr = db.get(cik, {}).get(q_curr)
    h_prev = db.get(cik, {}).get(q_prev)
    if not h_curr or not h_prev:
        return None
    w1 = portfolio_weights(h_prev)
    w2 = portfolio_weights(h_curr)
    all_cusips = set(w1) | set(w2)
    to = sum(abs(w1.get(c, 0) - w2.get(c, 0)) for c in all_cusips) / 2
    return to if to > 0.001 else None  # discard near-zero (inactive filers)


def prev_quarter(q):
    """Return the previous quarter string, e.g. '2023Q2' → '2023Q1'."""
    year, qn = int(q[:4]), int(q[5])
    if qn == 1:
        return f"{year-1}Q4"
    return f"{year}Q{qn-1}"


# ─── step 1: compute tau per institution per quarter ─────────────────────────
print("\nComputing per-institution tau from Q-over-Q turnover...")
tau_db = defaultdict(dict)   # tau_db[cik][quarter] = tau (trading days)

for cik in all_ciks:
    qtrs = sorted(db[cik].keys())
    for i, q in enumerate(qtrs[1:], 1):
        q_prev = qtrs[i - 1]
        to = quarterly_turnover(cik, q, q_prev)
        if to is not None:
            tau_db[cik][q] = 63.0 / to

tau_counts = {q: sum(1 for cik in tau_db if q in tau_db[cik]) for q in all_qtrs}
qtrs_usable = [q for q in all_qtrs if tau_counts.get(q, 0) >= 10]
print(f"  {len(qtrs_usable)} quarters with ≥10 institutions having tau estimates")


# ─── step 2: compute κ̂_h per quarter ────────────────────────────────────────
print("\nComputing quarterly κ̂_h (tau-proximity ↔ portfolio-similarity correlation)...")

kappa_results = []

for q in qtrs_usable:
    # Collect institutions with both tau and holdings in this quarter
    institutions = [
        cik for cik in all_ciks
        if q in tau_db[cik] and q in db.get(cik, {})
    ]
    if len(institutions) < 8:
        continue

    # Build weight vectors and tau values
    weights = {}
    taus    = {}
    for cik in institutions:
        w = portfolio_weights(db[cik][q])
        if w:
            weights[cik] = w
            taus[cik]    = tau_db[cik][q]

    inst_list = [c for c in institutions if c in weights]
    n = len(inst_list)
    if n < 8:
        continue

    # Pairwise: portfolio cosine similarity and tau proximity
    sim_vals   = []
    prox_vals  = []

    for i in range(n):
        for j in range(i + 1, n):
            ci, cj = inst_list[i], inst_list[j]
            sim  = cosine_sim(weights[ci], weights[cj])
            # tau proximity = exp(-|log τ_i - log τ_j|), same formula as CME
            tau_i, tau_j = taus[ci], taus[cj]
            prox = math.exp(-abs(math.log(tau_i + 1) - math.log(tau_j + 1)))
            sim_vals.append(sim)
            prox_vals.append(prox)

    if len(sim_vals) < 20:
        continue

    r, p = stats.pearsonr(prox_vals, sim_vals)
    rho, p_s = stats.spearmanr(prox_vals, sim_vals)
    kappa_results.append({
        "quarter": q,
        "kappa_hat": r,
        "kappa_spearman": rho,
        "p_pearson": p,
        "p_spearman": p_s,
        "n_institutions": n,
        "n_pairs": len(sim_vals),
    })
    print(f"  {q}: n={n:3d}  κ̂={r:+.3f}  p={p:.3f}  ρ={rho:+.3f}")


# ─── step 3: correlate κ̂_h with VIX ─────────────────────────────────────────
print("\nFetching VIX...")
vix = yf.download("^VIX", start="2012-01-01", end="2027-01-01",
                  interval="1mo", progress=False, auto_adjust=True)
vix_close = vix["Close"]
if hasattr(vix_close.columns, "__iter__"):
    vix_close = vix_close.iloc[:, 0]

vix_qtr = defaultdict(list)
for idx, val in vix_close.dropna().items():
    from datetime import datetime
    dt = idx.date() if hasattr(idx, "date") else datetime.strptime(str(idx)[:10], "%Y-%m-%d").date()
    q_str = f"{dt.year}Q{(dt.month-1)//3+1}"
    vix_qtr[q_str].append(float(val))

vix_qmean = {q: np.mean(v) for q, v in vix_qtr.items()}

# Merge κ̂ with VIX
kappa_vals, vix_vals, quarters_used = [], [], []
for row in kappa_results:
    vix_v = vix_qmean.get(row["quarter"])
    if vix_v:
        kappa_vals.append(row["kappa_hat"])
        vix_vals.append(vix_v)
        quarters_used.append(row["quarter"])

print(f"\nMatched quarters: {len(kappa_vals)}")

if len(kappa_vals) >= 8:
    r_kv, p_kv = stats.pearsonr(kappa_vals, vix_vals)
    rho_kv, p_s_kv = stats.spearmanr(kappa_vals, vix_vals)
    print(f"\nr(κ̂_h, VIX) = {r_kv:+.3f}  p = {p_kv:.4f}  n={len(kappa_vals)}")
    print(f"ρ(κ̂_h, VIX) = {rho_kv:+.3f}  p = {p_s_kv:.4f}  (Spearman)")

    # Forward lag: does κ̂(t) predict VIX(t+1)?
    r_lag, p_lag = stats.pearsonr(kappa_vals[:-1], vix_vals[1:])
    print(f"r(κ̂_h(t), VIX(t+1)) = {r_lag:+.3f}  p = {p_lag:.4f}  n={len(kappa_vals)-1}  [forward lag]")

# ─── step 4: is κ̂_h itself significant? (t-test vs 0) ─────────────────────
kappa_arr = np.array(kappa_vals)
t_stat, p_ttest = stats.ttest_1samp(kappa_arr, 0.0)
print(f"\nMean κ̂_h = {kappa_arr.mean():+.4f} ± {kappa_arr.std():.4f}")
print(f"  t-test vs 0: t = {t_stat:.3f}, p = {p_ttest:.4f}")
if p_ttest < 0.05:
    print("  => κ̂_h is significantly positive: like-tau institutions DO co-hold more than chance")
else:
    print("  => κ̂_h not significantly different from 0")

# ─── step 5: save results ────────────────────────────────────────────────────
out_path = Path("/Users/sanjaysubramania/cme_validation/kappa_empirical_results.csv")
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "quarter", "kappa_hat", "kappa_spearman", "p_pearson", "p_spearman",
        "n_institutions", "n_pairs", "VIX"
    ])
    writer.writeheader()
    vix_lookup = dict(zip(quarters_used, vix_vals))
    for row in kappa_results:
        row2 = dict(row)
        row2["VIX"] = vix_lookup.get(row["quarter"], "")
        writer.writerow(row2)

print(f"\nResults saved to {out_path}")
print("\n--- Interpretation ---")
print("κ̂_h > 0 means: institutions with similar tau tend to hold similar stocks")
print("    (temporal echo chambers exist in real data)")
print("r(κ̂_h, VIX) > 0 means: quarters with higher observed homophily have higher vol")
print("    (CME long-run destabilising channel confirmed empirically)")
