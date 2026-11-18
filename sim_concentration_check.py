"""
sim_concentration_check.py — Does compressing the horizon distribution raise simulated volatility?

The old sweep (simulate.py: tdi_concentration_sweep) built a compressed tau
distribution but never passed it to simulate_one_run, which draws its own tau.
Here we inject the compressed sampler into the canonical simulation, so the
simulated agents really have the compressed horizons.

Also produces the model-implied standardised slope of volatility on horizon
dispersion (sd of log tau), for comparison with the stock-level estimate.
"""
import json, sys
import numpy as np
from scipy import stats
import cme_canonical as cc

CONCS = [0.5, 1.0, 1.5, 2.0, 3.0]
KHS = [0.5, 2.0]
N_SEEDS = 25
captured = {}

def make_sampler(conc):
    def sampler(n=cc.N_AGENTS, seed=42):
        rng = np.random.default_rng(seed)
        out = []
        for count, mu, sig, (lo, hi) in zip(cc.TYPE_COUNTS, cc.TYPE_MU, cc.TYPE_SIGMA, cc.TYPE_BOUNDS):
            got = []
            while len(got) < count:
                d = np.exp(rng.normal(mu, sig / conc, 5000))
                got.extend(d[(d >= lo) & (d <= hi)].tolist())
            out.extend(max(1, int(round(x))) for x in got[:count])
        tau = np.array(out)
        captured["tau"] = tau
        return tau
    return sampler

rows = []
for kh in KHS:
    for conc in CONCS:
        cc.sample_tau = make_sampler(conc)
        for seed in range(N_SEEDS):
            r = cc.simulate_one_run(kh=kh, seed=seed)
            lt = np.log(captured["tau"])
            rows.append({"kh": kh, "conc": conc, "seed": seed, "vol": r["volatility"],
                         "tdi": cc.compute_tdi(captured["tau"]), "disp": float(lt.std()),
                         "tmfi": r["tmfi"]})
        print(f"kh={kh} conc={conc} done", flush=True)

json.dump(rows, open("sim_concentration_results.json", "w"))
import pandas as pd
d = pd.DataFrame(rows)
for kh, g in d.groupby("kh"):
    print(f"\n=== kappa_h = {kh} ===")
    print(g.groupby("conc")[["vol", "tdi", "disp"]].mean().round(5).to_string())
    r, p = stats.pearsonr(g.disp, g.vol)
    print(f"pooled r(dispersion, volatility) = {r:+.3f} (p={p:.2g})  [model-implied standardised slope]")
    r2, p2 = stats.pearsonr(g.tdi, g.vol)
    print(f"pooled r(TDI, volatility)        = {r2:+.3f} (p={p2:.2g})")
    w = g.copy()
    for c in ("vol", "disp"):
        w[c] = w[c] - w.groupby("conc")[c].transform("mean")
    rw, pw = stats.pearsonr(w.disp, w.vol)
    print(f"within-concentration r(dispersion, volatility) = {rw:+.3f} (p={pw:.2g})")
    lo, hi = g[g.conc == 0.5].vol.values, g[g.conc == 3.0].vol.values
    t, pt = stats.ttest_ind(hi, lo, equal_var=False)
    print(f"vol at conc=3 vs conc=0.5: {hi.mean():.5f} vs {lo.mean():.5f}  (Welch t={t:+.2f}, p={pt:.2g})")
