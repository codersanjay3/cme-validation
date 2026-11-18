"""
kappa_hac_tests.py — Proper inference for the quarterly kappa-hat series.

Addresses Chalmers' question: how many lags are in the Newey-West estimate, and
are there tests for how many are needed?  Also addresses cross-sectional
dependence: pairs within a quarter share institutions, so the pairwise Pearson
p-values overstate significance.  We use a permutation test instead.

Outputs (stdout + kappa_hac_results.json):
  1. Series diagnostics: AR(1), Ljung-Box, ACF
  2. Newey-West t-stat for mean(kappa) at lags 0..8 plus data-driven choices
     (Newey-West 1994 plug-in rule, Andrews-style AR(1) rule, Schwert rule)
  3. Moving-block bootstrap CI for the mean
  4. Permutation test: shuffle tau across institutions within each quarter
"""
import json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf

ROOT = Path("/Users/sanjaysubramania/cme_validation")
rng = np.random.default_rng(20261027)

# ── 1. series diagnostics ───────────────────────────────────────────────────
df = pd.read_csv(ROOT / "kappa_empirical_results.csv")
k = df["kappa_hat"].to_numpy()
T = len(k)
print(f"T = {T} quarters, mean = {k.mean():.4f}, sd = {k.std(ddof=1):.4f}")

rho = acf(k, nlags=8, fft=False)
print("ACF lags 1..8:", np.round(rho[1:], 3))
lb = acorr_ljungbox(k, lags=[1, 2, 4, 8], return_df=True)
print("Ljung-Box:\n", lb)

# ── 2. Newey-West at explicit and data-driven lags ──────────────────────────
X = np.ones((T, 1))
res_rows = []

def nw_t(L):
    m = sm.OLS(k, X).fit(cov_type="HAC", cov_kwds={"maxlags": L, "use_correction": True})
    return float(m.tvalues[0]), float(m.bse[0]), float(m.pvalues[0])

for L in range(0, 9):
    t, se, p = nw_t(L)
    res_rows.append({"rule": f"fixed L={L}", "lags": L, "se": se, "t": t, "p": p})

rule_schwert = int(math.floor(4 * (T / 100) ** 0.25))
rule_nw94 = int(math.floor(4 * (T / 100) ** (2 / 9)))
r1 = rho[1]
alpha = 4 * r1**2 / (1 - r1**2) ** 2
rule_andrews = int(math.ceil(1.1447 * (alpha * T) ** (1 / 3)))
for name, L in [("Schwert 4(T/100)^(1/4)", rule_schwert),
                ("Newey-West 1994 4(T/100)^(2/9)", rule_nw94),
                ("Andrews AR(1) plug-in", min(rule_andrews, T // 2))]:
    t, se, p = nw_t(L)
    res_rows.append({"rule": name, "lags": L, "se": se, "t": t, "p": p})

out = pd.DataFrame(res_rows)
print("\nNewey-West t-stat for H0: mean kappa = 0")
print(out.to_string(index=False, float_format=lambda x: f"{x:.4g}"))

# effective sample size from AR(1)
n_eff = T * (1 - r1) / (1 + r1)
print(f"\nAR(1) rho = {r1:.3f}  =>  n_eff = T(1-rho)/(1+rho) = {n_eff:.1f}")
print(f"Naive t = {k.mean()/(k.std(ddof=1)/math.sqrt(T)):.2f}; "
      f"n_eff-adjusted t = {k.mean()/(k.std(ddof=1)/math.sqrt(max(n_eff,2))):.2f}")

# ── 3. moving-block bootstrap ───────────────────────────────────────────────
B, blk = 5000, max(2, rule_nw94 + 1)
means = np.empty(B)
for b in range(B):
    idx = []
    while len(idx) < T:
        s = rng.integers(0, T - blk + 1)
        idx.extend(range(s, s + blk))
    means[b] = k[np.array(idx[:T])].mean()
lo, hi = np.percentile(means, [2.5, 97.5])
print(f"\nMoving-block bootstrap (block={blk}): mean 95% CI = [{lo:.4f}, {hi:.4f}]")

# ── 4. permutation test (tau shuffled across institutions within quarter) ───
print("\nLoading holdings for permutation test...")
with open(ROOT / "edgar_cache" / "holdings_db.json") as f:
    db = json.load(f)

def weights(h):
    tot = sum(x["value_k"] for x in h)
    return {x["cusip"]: x["value_k"] / tot for x in h} if tot else {}

def turnover(cik, q, qp):
    a, b = db[cik].get(q), db[cik].get(qp)
    if not a or not b:
        return None
    w2, w1 = weights(a), weights(b)
    to = sum(abs(w1.get(c, 0) - w2.get(c, 0)) for c in set(w1) | set(w2)) / 2
    return to if to > 0.001 else None

def cos(w1, w2):
    com = set(w1) & set(w2)
    if not com:
        return 0.0
    n1 = math.sqrt(sum(v * v for v in w1.values()))
    n2 = math.sqrt(sum(v * v for v in w2.values()))
    return sum(w1[c] * w2[c] for c in com) / (n1 * n2) if n1 and n2 else 0.0

NPERM = 500
perm_p, perm_obs = {}, {}
for q in df["quarter"]:
    insts, taus, ws = [], [], []
    for cik in db:
        if q not in db[cik]:
            continue
        qs = sorted(db[cik])
        i = qs.index(q)
        if i == 0:
            continue
        to = turnover(cik, q, qs[i - 1])
        w = weights(db[cik][q])
        if to is not None and w:
            insts.append(cik); taus.append(63.0 / to); ws.append(w)
    n = len(insts)
    iu, ju = np.triu_indices(n, 1)
    sim = np.array([cos(ws[a], ws[b]) for a, b in zip(iu, ju)])
    lt = np.log(np.array(taus) + 1)
    obs = np.corrcoef(np.exp(-np.abs(lt[iu] - lt[ju])), sim)[0, 1]
    ge = 0
    for _ in range(NPERM):
        lp = rng.permutation(lt)
        r = np.corrcoef(np.exp(-np.abs(lp[iu] - lp[ju])), sim)[0, 1]
        ge += r >= obs
    perm_p[q] = (ge + 1) / (NPERM + 1)
    perm_obs[q] = float(obs)

pv = np.array(list(perm_p.values()))
print(f"Permutation p < 0.05 in {int((pv < 0.05).sum())}/{len(pv)} quarters; "
      f"< 0.01 in {int((pv < 0.01).sum())}/{len(pv)}; "
      f"max p = {pv.max():.4f}; floor = {1/(NPERM+1):.4f}")
from scipy.stats import combine_pvalues
print("Fisher combined p (independence across quarters assumed):",
      combine_pvalues(pv, method="fisher")[1])

json.dump({
    "T": T, "mean": float(k.mean()), "ar1": float(r1), "n_eff": float(n_eff),
    "rules": {"schwert": rule_schwert, "nw94": rule_nw94, "andrews": int(min(rule_andrews, T // 2))},
    "nw_table": res_rows, "block_boot_ci": [float(lo), float(hi)],
    "perm_p": perm_p, "perm_nperm": NPERM,
}, open(ROOT / "kappa_hac_results.json", "w"), indent=1)
print("\nsaved kappa_hac_results.json")
