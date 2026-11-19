"""Shared helpers for the Stage 1 tests (see docs/stage1/PREREGISTRATION.md)."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "panel_13f"
MIN_POS, MIN_AUM = 20, 1e8

def qn(q):
    return int(q[:4]) * 4 + int(q[5])

def qlabel(n):
    y, r = divmod(n - 1, 4)
    return f"{y}Q{r + 1}"

def load_tau():
    """Institution-quarter horizons with the pre-registered filters and style cells."""
    t = pd.read_parquet(PANEL / "tau.parquet")
    t["cik"] = t.cik.astype(str)
    t = t.dropna(subset=["tau_split"])
    t["qn"] = t.period.map(qn)
    t["ltau"] = np.log(t.tau_split)
    t["laum"] = np.log(t.aum_usd)
    t["lnpos"] = np.log(t.n_positions)
    # n_positions in tau.parquet is the count at t; require >= MIN_POS at t and at t-1
    prev = t[["cik", "qn", "n_positions"]].assign(qn=lambda d: d.qn + 1).rename(columns={"n_positions": "npos_prev"})
    t = t.merge(prev, on=["cik", "qn"], how="left")
    t = t[(t.n_positions >= MIN_POS) & (t.npos_prev >= MIN_POS) & (t.aum_usd >= MIN_AUM)].copy()
    t["ltau_q"] = t.groupby("period").ltau.transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False))
    t["laum_t"] = t.groupby("period").laum.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False))
    t["style_q"] = t.period + "_" + t.ltau_q.astype(int).astype(str) + "_" + t.laum_t.astype(int).astype(str)
    return t.reset_index(drop=True)

def demean(df, cols, fes, iters=200, tol=1e-10):
    """Alternating projections: residualise cols on several sets of fixed effects."""
    out = df[cols].astype(float).copy()
    for _ in range(iters):
        before = out.to_numpy().copy()
        for fe in fes:
            out = out - out.groupby(df[fe]).transform("mean")
        if np.max(np.abs(out.to_numpy() - before)) < tol:
            break
    return out
