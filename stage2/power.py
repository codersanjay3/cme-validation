"""
Stage 2 scoping: can a neighbour manager-shock design detect the Stage 1 effect?

Reduced form for a fund i exposed to a shocked neighbour j (one of i's k neighbours):
    effect on log tau_i  =  b * (1/k) * delta_j
where b is the peer coefficient (Stage 1b: +0.0324) and delta_j is the first stage,
the change in the shocked fund's own log tau. The minimum detectable b at 5%
(two-sided) with 80% power from N independent exposed observations is
    MDE_b = 2.80 * sigma / (sqrt(N) * delta_j / k),
with sigma the within standard deviation of the outcome (Stage 1b: 0.461).
This is optimistic: exposed observations of one shock share the shock (clustering),
and the regressor uses an equal-weighted average over k neighbours.

Run from the repo root:  python stage2/power.py
Reads results/stage1b_results.json and, if present, results/stage2_event_link.json.
Writes results/stage2_power.json. No randomness.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s1 = json.load(open(ROOT / "results" / "stage1b_results.json"))
b = s1["results"]["primary_k10"]["NH_k10"]["b"]
sigma = round(s1["scale"]["sd_y_within"], 3)
K = 10
out = {"b_stage1": round(b, 4), "sigma_within_y": sigma, "k": K, "grid": []}
for shocks in (30, 100, 300, 1000, 3000):
    for exposed_per_shock in (10,):
        n = shocks * exposed_per_shock
        for delta in (0.25, 0.5, 1.0):
            mde = 2.80 * sigma / (n ** 0.5 * delta / K)
            out["grid"].append({"shocks": shocks, "exposed_obs": n, "first_stage_delta": delta,
                                "mde_b": round(mde, 3), "mde_over_stage1_b": round(mde / b, 1)})
link = ROOT / "results" / "stage2_event_link.json"
if link.exists():
    out["event_counts_used"] = json.load(open(link))
json.dump(out, open(ROOT / "results" / "stage2_power.json", "w"), indent=1)
for g in out["grid"]:
    print(g)
