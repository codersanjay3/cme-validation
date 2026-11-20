"""
validate_vs_top150.py: compare the rebuilt horizons with the current top-150 panel.

Old: tau_by_inst_quarter.json, series "x" (share-based, split-rebased; built by
price_adjusted_tdi.py from the top-150 EDGAR scrape, prices per filing).
New: panel_13f/tau.parquet, column tau_split (share-based, split-rebased; full
universe, common price per CUSIP-quarter, unit fix and amendment rules).

Reports, for institution-quarters present in both: coverage, rank correlation
of log tau overall and within quarter, median absolute log difference, and the
quarters where the two disagree most (expected around 2022Q4 to 2025 because of
the unit fixes). Also reports the size of the full universe per quarter.

Run from the repo root after build_panel.py:
    python rebuild_13f/validate_vs_top150.py
Output: results/validate_rebuild_vs_top150.json
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]

old = json.load(open(ROOT / "tau_by_inst_quarter.json"))["x"]
o = pd.DataFrame([(q, str(c).lstrip("0"), float(t)) for q, m in old.items() for c, t in m.items()],
                 columns=["period", "cik", "tau_old"])
o["tau_old"] = o.tau_old.clip(5, 2000)
n = pd.read_parquet(ROOT / "panel_13f" / "tau.parquet")
n["cik"] = n.cik.astype(str).str.lstrip("0")
m = o.merge(n[["period", "cik", "tau_split", "tau", "n_positions"]], on=["period", "cik"], how="inner").dropna(subset=["tau_split"])
m["lo"], m["ln"] = np.log(m.tau_old), np.log(m.tau_split)
m["absdiff"] = (m.lo - m.ln).abs()

def within(df):
    d = df.copy()
    for c in ("lo", "ln"):
        d[c] = d[c] - d.groupby("period")[c].transform("mean")
    return float(np.corrcoef(d.lo, d.ln)[0, 1])

by_q = m.groupby("period").apply(lambda g: pd.Series({
    "n": len(g), "spearman": stats.spearmanr(g.lo, g.ln)[0] if len(g) > 5 else np.nan,
    "median_abs_log_diff": g.absdiff.median()})).reset_index()
universe = n.groupby("period").cik.nunique().rename("filers_full_universe")
out = {
    "overlap_institution_quarters": int(len(m)),
    "old_institution_quarters": int(len(o)),
    "coverage_of_old": round(len(m) / len(o), 3),
    "spearman_all": round(float(stats.spearmanr(m.lo, m.ln)[0]), 3),
    "pearson_within_quarter": round(within(m), 3),
    "median_abs_log_diff": round(float(m.absdiff.median()), 3),
    "share_within_factor_1_5": round(float((m.absdiff < np.log(1.5)).mean()), 3),
    "worst_quarters": by_q.sort_values("spearman").head(8).round(3).to_dict("records"),
    "filers_per_quarter_full_universe": {k: int(v) for k, v in universe.items()},
}
(ROOT / "results").mkdir(exist_ok=True)
json.dump(out, open(ROOT / "results" / "validate_rebuild_vs_top150.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "filers_per_quarter_full_universe"}, indent=1))
print("filers per quarter (full universe), first/last:", list(out["filers_per_quarter_full_universe"].items())[:2],
      list(out["filers_per_quarter_full_universe"].items())[-2:])
