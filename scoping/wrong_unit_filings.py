"""
Idea scoping ("fake whales"): which 13F filings used the wrong VALUE unit, and how
big did their positions look to anyone reading the raw field under the rule in force?

Same per-filing implied-price check as rebuild_13f/build_panel.py::to_dollars, run on
the staged raw values (panel_13f/stage/*.parquet): a filing whose median
(value / shares) relative to the cross-filer median price of the same CUSIP and
period sits between 300 and 3000 times too high is "inflated" (reads 1000x too big
under the rule in force); between 1/3000 and 1/300 is "deflated" (1000x too small).
Reference prices use CUSIP-periods with at least 3 filers within the same zip.

Run from the repo root:  python scoping/wrong_unit_filings.py
Outputs: results/scoping_wrong_unit_filings.json (summary) and
panel_13f/scoping/wrong_unit_accessions.parquet (per filing; gitignored).
No randomness.
"""
import glob, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "panel_13f"
UNIT_CUTOFF = pd.Timestamp("2023-01-03")

filings = pd.read_parquet(PANEL / "filings.parquet")[["accession", "cik", "filing_date", "kind"]]
rows = []
for f in sorted(glob.glob(str(PANEL / "stage" / "*.parquet"))):
    d = pd.read_parquet(f).merge(filings, on="accession", how="inner")
    d = d[(d.shares > 0) & (d.value_raw > 0)]
    d["value_rule"] = np.where(d.filing_date < UNIT_CUTOFF, d.value_raw * 1000.0, d.value_raw)
    p = d.value_rule / d.shares
    ref = p.groupby([d.period, d.cusip]).transform("median")
    nh = d.groupby(["period", "cusip"]).cik.transform("nunique")
    d["ratio"] = (p / ref).where(nh >= 3)
    a = d.groupby("accession").agg(cik=("cik", "first"), period=("period", "first"),
                                   filing_date=("filing_date", "first"), kind=("kind", "first"),
                                   ratio=("ratio", "median"), n_pos=("cusip", "size"),
                                   value_as_read=("value_rule", "sum"))
    a["state"] = np.select([a.ratio.between(300, 3000), a.ratio.between(1 / 3000, 1 / 300)],
                           ["inflated", "deflated"], "ok")
    a["value_true"] = np.where(a.state == "inflated", a.value_as_read / 1000,
                               np.where(a.state == "deflated", a.value_as_read * 1000, a.value_as_read))
    # how big do the largest positions look: as-read value of the top position vs the
    # sum of true values held by all other filers in that CUSIP-period
    bad = d[d.accession.isin(a.index[a.state == "inflated"])]
    if len(bad):
        tot = d.assign(v_true=np.where(d.accession.isin(a.index[a.state == "inflated"]), d.value_rule / 1000, d.value_rule)) \
               .groupby(["period", "cusip"]).v_true.sum()
        top = bad.sort_values("value_rule").groupby("accession").tail(1)
        top = top.join(tot, on=["period", "cusip"])
        a.loc[top.accession, "top_as_read_over_all_holders"] = (top.value_rule / top.v_true).values
    rows.append(a.reset_index())
acc = pd.concat(rows).drop_duplicates("accession")
(PANEL / "scoping").mkdir(exist_ok=True)
acc.to_parquet(PANEL / "scoping" / "wrong_unit_accessions.parquet")
acc["year"] = acc.filing_date.dt.year
inf = acc[acc.state == "inflated"]
out = {
    "filings_checked": int(len(acc)),
    "by_state": acc.state.value_counts().to_dict(),
    "inflated_by_filing_year": inf.year.value_counts().sort_index().to_dict(),
    "deflated_by_filing_year": acc[acc.state == "deflated"].year.value_counts().sort_index().to_dict(),
    "inflated_pre_2023_share": round(float((inf.filing_date < UNIT_CUTOFF).mean()), 3),
    "inflated_distinct_filers": int(inf.cik.nunique()),
    "inflated_median_positions": int(inf.n_pos.median()),
    "inflated_true_aum_usd_m_median": round(float(inf.value_true.median() / 1e6), 1),
    "inflated_as_read_aum_usd_bn_median": round(float(inf.value_as_read.median() / 1e9), 1),
    "inflated_as_read_aum_over_1tn": int((inf.value_as_read > 1e12).sum()),
    "inflated_top_position_as_read_over_all_true_holdings_median": round(float(inf.top_as_read_over_all_holders.median()), 1),
    "inflated_original_vs_amendment": inf.kind.value_counts().to_dict(),
}
(ROOT / "results").mkdir(exist_ok=True)
json.dump(out, open(ROOT / "results" / "scoping_wrong_unit_filings.json", "w"), indent=1, default=int)
print(json.dumps(out, indent=1, default=int))
