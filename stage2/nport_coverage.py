"""
Stage 2 scoping: what one quarter of the N-PORT data sets contains.

For each zip given (default: every nport_cache/*_nport.zip), reports filings,
series, report-date spread, holdings rows, common-stock rows in shares (ASSET_CAT
EC, UNIT NS) and how many carry a usable CUSIP, and counts equity funds
(at least 80% of reported value in common stock and at least 20 stocks).
Writes results/stage2_nport_coverage.json and, per zip, the equity-fund series
list to nport_cache/equity_series_<q>.csv (used by stage2/link_events.py).

Run from the repo root:  python stage2/nport_coverage.py [zip ...]
"""
import json, sys, zipfile
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "nport_cache"
EQ_SHARE, MIN_STOCKS, MIN_NAV = 0.8, 20, 1e8


def coverage(path):
    z = zipfile.ZipFile(path)
    rd = lambda t, **k: pd.read_csv(z.open(t + ".tsv"), sep="\t", dtype=str, **k)
    sub = rd("SUBMISSION")
    fri = rd("FUND_REPORTED_INFO", usecols=["ACCESSION_NUMBER", "SERIES_ID", "SERIES_NAME", "NET_ASSETS"])
    reg = rd("REGISTRANT", usecols=["ACCESSION_NUMBER", "CIK"])
    sub["rmonth"] = pd.to_datetime(sub.REPORT_DATE, format="%d-%b-%Y").dt.strftime("%Y-%m")
    parts = []
    cols = ["ACCESSION_NUMBER", "ISSUER_CUSIP", "UNIT", "ASSET_CAT", "CURRENCY_VALUE"]
    for ch in pd.read_csv(z.open("FUND_REPORTED_HOLDING.tsv"), sep="\t", dtype=str, chunksize=2_000_000, usecols=cols):
        v = pd.to_numeric(ch.CURRENCY_VALUE, errors="coerce").fillna(0)
        eq = (ch.ASSET_CAT == "EC") & (ch.UNIT == "NS")
        cus = ch.ISSUER_CUSIP.str.fullmatch(r"[0-9A-Z]{9}", na=False) & (ch.ISSUER_CUSIP != "000000000")
        parts.append(pd.DataFrame({"acc": ch.ACCESSION_NUMBER, "n": 1, "v": v, "n_eq": eq.astype(int),
                                   "v_eq": v.where(eq, 0), "n_eq_cusip": (eq & cus).astype(int)})
                     .groupby("acc").sum())
    a = pd.concat(parts).groupby(level=0).sum()
    a["eq_share"] = a.v_eq / a.v.where(a.v > 0)
    m = a.join(fri.set_index("ACCESSION_NUMBER"), how="left")
    m["nav"] = pd.to_numeric(m.NET_ASSETS, errors="coerce")
    eqf = m[(m.eq_share >= EQ_SHARE) & (m.n_eq >= MIN_STOCKS)]
    q = Path(path).name.split("_")[0]
    eqf[["SERIES_ID", "SERIES_NAME", "nav", "n_eq"]].drop_duplicates("SERIES_ID").to_csv(
        CACHE / f"equity_series_{q}.csv", index=False)
    rm = sub.rmonth.value_counts()
    return {
        "zip": Path(path).name, "filings": int(len(sub)), "amendments": int((sub.SUB_TYPE == "NPORT-P/A").sum()),
        "series": int(fri.SERIES_ID.nunique()), "registrants": int(reg.CIK.nunique()),
        "report_months_with_100plus_filings": {k: int(v) for k, v in rm[rm >= 100].sort_index().items()},
        "holding_rows": int(a.n.sum()), "common_stock_share_rows": int(a.n_eq.sum()),
        "common_stock_share_rows_with_cusip": int(a.n_eq_cusip.sum()),
        "equity_funds": int(len(eqf)), "equity_funds_nav_100m_plus": int((eqf.nav >= MIN_NAV).sum()),
        "equity_funds_median_stocks": int(eqf.n_eq.median()),
        "equity_funds_total_nav_usd_bn": round(float(eqf.nav.sum()) / 1e9, 1),
        "definition": f"equity fund: >= {EQ_SHARE:.0%} of value in common stock (EC, NS), >= {MIN_STOCKS} stocks",
    }


def main():
    zips = sys.argv[1:] or sorted(str(p) for p in CACHE.glob("*_nport.zip"))
    out = [coverage(z) for z in zips]
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results" / "stage2_nport_coverage.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
