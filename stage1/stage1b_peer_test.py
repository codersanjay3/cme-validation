"""
Stage 1b: do institutions' horizons move toward their overlap neighbours' horizons?

Implements docs/stage1/PREREGISTRATION.md exactly (committed before this ran).

  log tau_{i,t+1} = b * NH_{i,t} + a * log tau_{i,t} + c1 * log AUM_{i,t} + c2 * log npos_{i,t}
                    + institution FE + style-by-quarter FE + e,   SE two-way clustered (institution, quarter)

NH_{i,t}: mean over i's k nearest neighbours (cosine of value weights at t-1)
of log tau of the neighbour's trades between t-1 and t computed only over
CUSIPs i did not hold at t-1 (same prices and split rule as the panel),
using neighbours with >= 5 such CUSIPs.

Placebos: (1) future neighbours (top-k at t+4, not at t-1), same NH
construction; (2) NH shuffled within style-by-quarter cells (seed 20261119).
Gate 1b: b > 0 with p < 0.05; future placebo n.s. at 5% or < b/2; shuffled n.s.
Secondary: raw neighbour horizon, quarter FE only, nonlinearity, k = 5 and 20.

Run from the repo root: python stage1/stage1b_peer_test.py
Outputs: results/stage1b_results.json; per-quarter neighbour data cached in
panel_13f/stage1/ (gitignored).
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rebuild_13f"))
from common import ROOT, PANEL, MIN_POS, MIN_AUM, qn, qlabel, load_tau, demean
import build_panel as bp

KMAX, K, MIN_NONHELD, SEED = 20, 10, 5, 20261119
CACHE = PANEL / "stage1"
CACHE.mkdir(exist_ok=True)

def positions(q):
    p = PANEL / "positions" / f"{q}.parquet"
    return pd.read_parquet(p) if p.exists() else None

def eligible(pos):
    g = pos.groupby("cik").agg(n=("cusip", "size"), aum=("value_usd", "sum"))
    return set(g[(g.n >= MIN_POS) & (g.aum >= MIN_AUM)].index)

def topk_neighbours(pos, ciks, kmax=KMAX):
    """Top-kmax cosine neighbours on value weights (each institution's own weights)."""
    p = pos[pos.cik.isin(ciks)]
    ci = {c: i for i, c in enumerate(sorted(ciks))}
    cu = {c: i for i, c in enumerate(p.cusip.unique())}
    w = p.value_usd / p.groupby("cik").value_usd.transform("sum")
    X = sp.csr_matrix((w.to_numpy(), (p.cik.map(ci).to_numpy(), p.cusip.map(cu).to_numpy())),
                      shape=(len(ci), len(cu)))
    norms = np.sqrt(np.asarray(X.multiply(X).sum(1)).ravel())
    X = sp.diags(1 / np.where(norms > 0, norms, 1)) @ X
    XT = X.T.tocsc()
    names = np.array(sorted(ciks))
    rows = []
    for s in range(0, X.shape[0], 400):
        S = (X[s:s + 400] @ XT).toarray()
        for r in range(S.shape[0]):
            S[r, s + r] = -1.0                                   # exclude self
        idx = np.argpartition(-S, kmax, axis=1)[:, :kmax]
        for r in range(S.shape[0]):
            order = idx[r][np.lexsort((names[idx[r]], -S[r, idx[r]]))]  # ties by CIK
            rows += [(names[s + r], names[j], rank + 1, S[r, j]) for rank, j in enumerate(order)]
    return pd.DataFrame(rows, columns=["i", "j", "rank", "cos"])

def neighbour_table(p0, p1, price_t, price_prev):
    """Per (j, cusip) trade and value components between t-1 and t, as in the panel."""
    m = p0[["cik", "cusip", "shares"]].merge(p1[["cik", "cusip", "shares"]], on=["cik", "cusip"],
                                             how="outer", suffixes=("_0", "_1")).fillna({"shares_0": 0.0, "shares_1": 0.0})
    m = m[m.cik.isin(set(p0.cik) & set(p1.cik))]
    m["p"] = m.cusip.map(price_t).fillna(m.cusip.map(price_prev))
    m = m.dropna(subset=["p"])
    both = (m.shares_0 > 0) & (m.shares_1 > 0)
    m["s0"] = m.shares_0.astype("float64")
    pratio = (m.cusip.map(price_t) / m.cusip.map(price_prev)).to_numpy()
    m.loc[both, "s0"] = bp._split_rebase(m.loc[both, "shares_0"].to_numpy(), m.loc[both, "shares_1"].to_numpy(),
                                         pratio[both.to_numpy()])
    m["tr"] = (m.shares_1 - m.s0).abs() * m.p
    m["v0"], m["v1"] = m.s0 * m.p, m.shares_1 * m.p
    return m[["cik", "cusip", "tr", "v0", "v1"]].rename(columns={"cik": "j"})

def log_tau_from(tr, v0, v1):
    to = 0.5 * tr / (0.5 * (v0 + v1))
    return np.log(np.clip(63.0 / np.where(to > 1e-3, to, np.nan), 5, 2000))

def nh_for(pairs, held_prev, jt):
    """Mean non-held-stock log tau of each i's neighbours in `pairs` (columns i, j)."""
    tot = jt.groupby("j").agg(TR=("tr", "sum"), V0=("v0", "sum"), V1=("v1", "sum"), NC=("cusip", "size")).reset_index()
    ov = pairs[["i", "j"]].merge(held_prev, left_on="i", right_on="cik").merge(jt, on=["j", "cusip"])
    ov = ov.groupby(["i", "j"]).agg(tr=("tr", "sum"), v0=("v0", "sum"), v1=("v1", "sum"), nc=("cusip", "size")).reset_index()
    d = pairs[["i", "j"]].merge(tot, on="j").merge(ov, on=["i", "j"], how="left").fillna({"tr": 0, "v0": 0, "v1": 0, "nc": 0})
    d = d[(d.NC - d.nc) >= MIN_NONHELD]
    d["lt"] = log_tau_from(d.TR - d.tr, d.V0 - d.v0, d.V1 - d.v1)
    return d.dropna(subset=["lt"]).groupby("i").lt.agg(["mean", "size"])

# ---------------------------------------------------------------- build NH per quarter
panel = load_tau()
quarters = sorted(panel.period.unique(), key=qn)
nets = {}
def net(q):
    if q not in nets:
        f = CACHE / f"net_{q}.parquet"
        if f.exists():
            nets[q] = pd.read_parquet(f)
        else:
            pos = positions(q)
            nets[q] = None if pos is None else topk_neighbours(pos, eligible(pos))
            if nets[q] is not None:
                nets[q].to_parquet(f, index=False)
    return nets[q]

rows = []
for t in quarters:
    prev, fut = qlabel(qn(t) - 1), qlabel(qn(t) + 4)
    cf = CACHE / f"nh_{t}.parquet"
    if cf.exists():
        rows.append(pd.read_parquet(cf)); continue
    p0, p1 = positions(prev), positions(t)
    if p0 is None or p1 is None:
        continue
    price_t = (p1.value_usd / p1.shares).groupby(p1.cusip).median()
    price_prev = (p0.value_usd / p0.shares).groupby(p0.cusip).median()
    jt = neighbour_table(p0, p1, price_t, price_prev)
    held_prev = p0[["cik", "cusip"]]
    n0 = net(prev)
    out = pd.DataFrame({"i": panel.loc[panel.period == t, "cik"].unique()})
    for k in (5, 10, 20):
        r = nh_for(n0[(n0["rank"] <= k)], held_prev, jt)
        out = out.merge(r.rename(columns={"mean": f"NH_k{k}", "size": f"n_k{k}"}), left_on="i", right_index=True, how="left")
    # raw neighbour horizon: neighbours' panel log tau at t (all their positions)
    lt_t = panel.loc[panel.period == t].set_index("cik").ltau
    r = n0[n0["rank"] <= K].assign(lt=lambda d: d.j.map(lt_t)).dropna(subset=["lt"]).groupby("i").lt.mean()
    out["NHraw"] = out.i.map(r)
    # share of neighbours below the quarter median horizon (nonlinearity check)
    med = lt_t.median()
    r = n0[n0["rank"] <= K].assign(lt=lambda d: d.j.map(lt_t)).dropna(subset=["lt"]).groupby("i").lt.apply(lambda s: float((s < med).mean()))
    out["share_short"] = out.i.map(r)
    # future-neighbour placebo: top-K at t+4 that are not top-K at t-1
    nf = net(fut)
    if nf is not None:
        cur = set(zip(n0[n0["rank"] <= K].i, n0[n0["rank"] <= K].j))
        fpairs = nf[nf["rank"] <= K]
        fpairs = fpairs[[(a, b) not in cur for a, b in zip(fpairs.i, fpairs.j)]]
        fpairs = fpairs[fpairs.j.isin(set(jt.j))]
        r = nh_for(fpairs, held_prev, jt)
        out = out.merge(r.rename(columns={"mean": "NH_future", "size": "n_future"}), left_on="i", right_index=True, how="left")
    out["period"] = t
    out.to_parquet(cf, index=False)
    rows.append(out)
    print(t, "focal", len(out), "with NH_k10", int(out.NH_k10.notna().sum()), flush=True)

nh = pd.concat(rows, ignore_index=True).rename(columns={"i": "cik"})

# ---------------------------------------------------------------- regression data
lead = panel[["cik", "qn", "ltau"]].assign(qn=lambda d: d.qn - 1).rename(columns={"ltau": "y"})
d = panel.merge(nh, on=["cik", "period"], how="inner").merge(lead, on=["cik", "qn"], how="inner")

def twoway_ols(df, y, xs, fes):
    s = df.dropna(subset=[y] + xs).copy()
    s = s[s.groupby("cik").cik.transform("size") >= 2]
    r = demean(s, [y] + xs, fes)
    X, Y = r[xs].to_numpy(), r[y].to_numpy()
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ Y
    u = Y - X @ beta
    def meat(groups):
        sc = pd.DataFrame(X * u[:, None]).groupby(groups.to_numpy()).sum().to_numpy()
        G = sc.shape[0]
        return sc.T @ sc * G / (G - 1)
    V = XtX_inv @ (meat(s.cik) + meat(s.period) - meat(s.cik + "|" + s.period)) @ XtX_inv
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    tval = beta / se
    G = min(s.cik.nunique(), s.period.nunique())
    p = 2 * stats.t.sf(np.abs(tval), df=G - 1)
    return {x: {"b": float(b), "se": float(e), "t": float(tt), "p": float(pp)} for x, b, e, tt, pp in zip(xs, beta, se, tval, p)} | {"_n": int(len(s)), "_institutions": int(s.cik.nunique()), "_quarters": int(s.period.nunique())}

CTRL = ["ltau", "laum", "lnpos"]
FE = ["cik", "style_q"]
res = {}
res["primary_k10"] = twoway_ols(d, "y", ["NH_k10"] + CTRL, FE)
res["placebo_future"] = twoway_ols(d, "y", ["NH_future"] + CTRL, FE) if "NH_future" in d else None
rng = np.random.default_rng(SEED)
d["NH_shuffled"] = d.groupby("style_q").NH_k10.transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index))
res["placebo_shuffled"] = twoway_ols(d, "y", ["NH_shuffled"] + CTRL, FE)
res["secondary_raw_neighbour_horizon"] = twoway_ols(d, "y", ["NHraw"] + CTRL, FE)
res["secondary_quarter_fe_only"] = twoway_ols(d, "y", ["NH_k10"] + CTRL, ["cik", "period"])
d["NHxshort"] = (d.NH_k10 - d.NH_k10.mean()) * (d.share_short - d.share_short.mean())
res["secondary_nonlinearity"] = twoway_ols(d, "y", ["NH_k10", "share_short", "NHxshort"] + CTRL, FE)
res["secondary_k5"] = twoway_ols(d, "y", ["NH_k5"] + CTRL, FE)
res["secondary_k20"] = twoway_ols(d, "y", ["NH_k20"] + CTRL, FE)

b, pb = res["primary_k10"]["NH_k10"]["b"], res["primary_k10"]["NH_k10"]["p"]
fb = res["placebo_future"]["NH_future"] if res["placebo_future"] else None
sb = res["placebo_shuffled"]["NH_shuffled"]
gate = {"1_b_positive_p_lt_05": bool(b > 0 and pb < 0.05),
        "2_future_placebo_ns_or_lt_half_b": bool(fb is not None and (fb["p"] >= 0.05 or fb["b"] < b / 2)),
        "3_shuffled_placebo_ns": bool(sb["p"] >= 0.05)}
gate["pass"] = all(gate.values())
sd = {"sd_NH_k10_within": float(demean(d.dropna(subset=["NH_k10"]), ["NH_k10"], FE)["NH_k10"].std()),
      "sd_y_within": float(demean(d.dropna(subset=["NH_k10"]), ["y"], FE)["y"].std())}
out = {"preregistration": "docs/stage1/PREREGISTRATION.md (commit c14dba7)", "results": res, "gate_1b": gate, "scale": sd}
json.dump(out, open(ROOT / "results" / "stage1b_results.json", "w"), indent=1)
for k, v in res.items():
    if v:
        main = [x for x in v if not x.startswith("_") and x not in CTRL]
        print(f"{k:38s}", " | ".join(f"{x}: b={v[x]['b']:+.4f} t={v[x]['t']:+.2f} p={v[x]['p']:.3f}" for x in main), f"| n={v['_n']}")
print("GATE 1b:", gate)
print("scale:", sd)
