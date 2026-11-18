"""
stock_level_test.py — Does clustering of holder horizons predict stock volatility?

PRE-SPECIFIED (before looking at outcomes):
  Primary:   coefficient on DISP (ownership-weighted s.d. of holders' log tau,
             z-scored within quarter) in a regression of log next-quarter
             realized volatility. the Fractal Market Hypothesis predicts NEGATIVE (more clustered
             holders, lower dispersion, more volatile). NOTE: the CME simulation's friction
             channel implies the OPPOSITE sign (see sim_concentration_check.py).
  Secondary: next-quarter minimum daily return (CME predicts negative->more
             extreme crash), next-quarter skewness.
  Controls:  ownership-weighted mean log tau, log #holders, holder HHI, log panel
             value held, log current-quarter realized volatility.
  Inference: Fama-MacBeth with Newey-West (3 lags) on the quarterly slopes;
             robustness: pooled with quarter fixed effects, SE clustered by stock.
  Horizons:  share-based tau (primary) vs value-weight tau (paper baseline).
  Placebo:   tau shuffled across institutions within quarter.
"""
import json, math, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path("/Users/sanjaysubramania/cme_validation")
rng = np.random.default_rng(7)
MIN_HOLDERS = 10

cusip_tk = {c: t for c, t in json.load(open(ROOT / "cusip_ticker.json")).items() if t}
taus = json.load(open(ROOT / "tau_by_inst_quarter.json"))
out = pd.read_csv(ROOT / "stock_quarter_outcomes.csv")
outd = {(r.ticker, r.quarter): r for r in out.itertuples()}

def nextq(q):
    y, n = int(q[:4]), int(q[5])
    return f"{y+1}Q1" if n == 4 else f"{y}Q{n+1}"

print("loading holdings...", flush=True)
db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))
pos = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))   # q -> cusip -> cik10 -> value
for cik, qs in db.items():
    c10 = str(cik).zfill(10)
    for q, hs in qs.items():
        for h in hs:
            if h["cusip"] in cusip_tk:
                pos[q][h["cusip"]][c10] += h["value_k"]
del db

def build(kind, shuffle=False):
    rows = []
    for q, bycus in pos.items():
        tq = taus[kind].get(q, {})
        if shuffle and tq:
            keys = list(tq); vals = rng.permutation([tq[k] for k in keys]); tq = dict(zip(keys, vals))
        for c, holders in bycus.items():
            hs = [(i, v) for i, v in holders.items() if i in tq and v > 0]
            if len(hs) < MIN_HOLDERS:
                continue
            v = np.array([x[1] for x in hs]); w = v / v.sum()
            lt = np.log(np.clip([tq[x[0]] for x in hs], 5, 2000))
            mu = float((w * lt).sum())
            rows.append({"quarter": q, "ticker": cusip_tk[c], "disp": float(np.sqrt((w * (lt - mu) ** 2).sum())),
                         "mean_lt": mu, "log_nh": math.log(len(hs)), "hhi": float((w ** 2).sum()),
                         "log_val": math.log(v.sum())})
    df = pd.DataFrame(rows)
    df = df.groupby(["quarter", "ticker"], as_index=False).mean(numeric_only=True)   # cusips sharing a ticker
    cur, nxt = [], []
    for r in df.itertuples():
        a, b = outd.get((r.ticker, r.quarter)), outd.get((r.ticker, nextq(r.quarter)))
        cur.append(a.rv if a is not None else np.nan)
        nxt.append((b.rv, b.minret, b.skew) if b is not None else (np.nan,) * 3)
    df["rv_cur"] = cur
    df[["rv_next", "min_next", "skew_next"]] = pd.DataFrame(nxt, index=df.index)
    df = df.dropna()
    df = df[(df.rv_cur > 0) & (df.rv_next > 0)]
    df["lrv_cur"] = np.log(df.rv_cur); df["lrv_next"] = np.log(df.rv_next)
    return df

CONTROLS = ["mean_lt", "log_nh", "hhi", "log_val", "lrv_cur"]

def fama_macbeth(df, y, lags=3):
    betas = []
    for q, g in df.groupby("quarter"):
        if len(g) < 60:
            continue
        X = g[["disp"] + CONTROLS].copy()
        X = (X - X.mean()) / X.std()
        X = sm.add_constant(X)
        m = sm.OLS(((g[y] - g[y].mean()) / g[y].std()).values, X.values).fit()
        betas.append(m.params[1])
    b = np.array(betas)
    r = sm.OLS(b, np.ones(len(b))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(b.mean()), float(r.tvalues[0]), float(r.pvalues[0]), len(b), int(df.shape[0])

def pooled_fe(df, y):
    d = df.copy()
    for c in ["disp"] + CONTROLS:
        d[c] = (d[c] - d.groupby("quarter")[c].transform("mean")) / d[c].std()
    d["yy"] = (d[y] - d.groupby("quarter")[y].transform("mean")) / d[y].std()
    m = sm.OLS(d["yy"], sm.add_constant(d[["disp"] + CONTROLS])).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d.ticker)[0]})
    return float(m.params["disp"]), float(m.tvalues["disp"]), float(m.pvalues["disp"])

def twoway_fe(df, y):
    d = df.copy()
    cols = ["disp"] + CONTROLS + [y]
    for c in cols:
        d[c] = (d[c] - d[c].mean()) / d[c].std()
    for _ in range(8):
        for key in ("ticker", "quarter"):
            d[cols] = d[cols] - d.groupby(key)[cols].transform("mean")
    m = sm.OLS(d[y], d[["disp"] + CONTROLS]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.ticker)[0]})
    return float(m.params["disp"]), float(m.tvalues["disp"]), float(m.pvalues["disp"])

results = {}
for kind, label in (("x", "share-based tau (primary)"), ("w", "value-weight tau (paper baseline)")):
    df = build(kind)
    print(f"\n=== {label}: {len(df)} stock-quarters, {df.ticker.nunique()} stocks, "
          f"{df.quarter.nunique()} quarters ===")
    print(f"mean DISP = {df.disp.mean():.3f}, corr(DISP, mean_lt) = {df[['disp','mean_lt']].corr().iloc[0,1]:+.2f}")
    for y, name, expect in (("lrv_next", "log next-qtr realized vol", "-"),
                            ("min_next", "next-qtr min daily return", "+ (less negative when dispersed)"),
                            ("skew_next", "next-qtr skewness", "+")):
        b, t, p, nq, n = fama_macbeth(df, y)
        bf, tf, pf = pooled_fe(df, y)
        print(f"  {name:28s} FM beta(DISP)={b:+.4f} (NW t={t:+.2f}, p={p:.3f}, {nq} qtrs) | "
              f"pooled FE beta={bf:+.4f} (cluster t={tf:+.2f}, p={pf:.3f})   [CME predicts sign: {expect}]")
        results[f"{kind}:{y}"] = {"fm_beta": b, "fm_t": t, "fe_beta": bf, "fe_t": tf, "n": n}
    bt, tt, pt = twoway_fe(df, "lrv_next")
    print(f"  STOCK + QUARTER FE (within-stock changes only) lrv_next: beta(DISP)={bt:+.4f} (cluster t={tt:+.2f}, p={pt:.3f})")
    results[f"{kind}:twoway"] = {"beta": bt, "t": tt}
    if kind == "x":
        dp = build("x", shuffle=True)
        b, t, p, nq, n = fama_macbeth(dp, "lrv_next")
        print(f"  PLACEBO (tau shuffled across institutions) lrv_next: FM beta={b:+.4f} (t={t:+.2f})")
        results["placebo"] = {"fm_beta": b, "fm_t": t}
json.dump(results, open(ROOT / "stock_level_results.json", "w"), indent=1)
