"""
validate_turnover.py: compare N-PORT holdings-based turnover with the turnover rate
funds report in their prospectus (SEC Mutual Fund Prospectus Risk/Return Summary
data sets, XBRL element PortfolioTurnoverRate, one value per series and fiscal year).

Prospectus turnover = lesser of purchases or sales over average net assets, for the
fiscal year, including trades inside the quarter. Holdings-based annual turnover here
= sum of the series' quarterly share-based turnovers (nport_panel_data/tau.parquet)
over the 12 months ending at the prospectus period date (ddate), requiring 4
transitions. Holdings-based turnover misses intra-quarter round trips, so it should
sit below the reported rate; the test is how well the two rank funds.

Downloads the Risk/Return data sets for 2019 onward into nport_cache/rr/ (needs
SEC_CONTACT_EMAIL). Run from the repo root: python nport_panel/validate_turnover.py
Output: results/nport_turnover_validation.json. Deterministic.
"""
import json, os, re, sys, time, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RR = ROOT / "nport_cache" / "rr"
PAGE = "https://www.sec.gov/data-research/sec-markets-data/mutual-fund-prospectus-riskreturn-summary-data-sets"


def download():
    contact = os.environ.get("SEC_CONTACT_EMAIL", "")
    if "@" not in contact:
        sys.exit("Set SEC_CONTACT_EMAIL (see APIS.md).")
    s = requests.Session(); s.headers["User-Agent"] = "CME-Validation " + contact
    links = sorted(set(re.findall(r'href="([^"]+_rr1\.zip)"', s.get(PAGE, timeout=60).text)))
    RR.mkdir(parents=True, exist_ok=True)
    for l in links:
        name = l.rsplit("/", 1)[-1]
        if name[:4] < "2019" or (RR / name).exists():
            continue
        time.sleep(1)
        r = s.get("https://www.sec.gov" + l, timeout=600); r.raise_for_status()
        (RR / name).write_bytes(r.content)
        print("downloaded", name, len(r.content) // 1_000_000, "MB", flush=True)


def prospectus_turnover():
    rows = []
    for z in sorted(RR.glob("*_rr1.zip")):
        with zipfile.ZipFile(z) as zf:
            for ch in pd.read_csv(zf.open("num.tsv"), sep="\t", dtype=str, chunksize=2_000_000,
                                  usecols=["adsh", "tag", "ddate", "series", "value"]):
                rows.append(ch[ch.tag == "PortfolioTurnoverRate"])
    r = pd.concat(rows)
    r["value"] = pd.to_numeric(r.value, errors="coerce")
    r["ddate"] = pd.to_datetime(r.ddate, format="%Y%m%d", errors="coerce")
    r = r.dropna(subset=["series", "ddate", "value"])
    # one value per series and period date: median across share classes and repeat filings
    return r.groupby(["series", "ddate"]).value.median().rename("reported").reset_index()


def main():
    if "--no-download" not in sys.argv:
        download()
    rep = prospectus_turnover()
    tau = pd.read_parquet(ROOT / "nport_panel_data" / "tau.parquet")
    tau = tau[tau.turnover.notna()]
    out = []
    for s, g in tau.groupby("series_id"):
        p = rep[rep.series == s]
        for d, v in zip(p.ddate, p.reported):
            w = g[(g.report_date > d - pd.DateOffset(months=12)) & (g.report_date <= d + pd.DateOffset(days=5))]
            if len(w) == 4:
                out.append((s, d, v, float(w.turnover.sum()), float(w.turnover_split.sum())))
    m = pd.DataFrame(out, columns=["series", "ddate", "reported", "holdings", "holdings_split"])
    m = m[(m.reported > 0) & (m.reported < 20)]
    res = {"prospectus_values": int(len(rep)), "matched_fund_years": int(len(m)), "funds": int(m.series.nunique())}
    if len(m):
        for c in ("holdings", "holdings_split"):
            res[c] = {"spearman_with_reported": round(float(m[c].rank().corr(m.reported.rank())), 3),
                      "pearson_log": round(float(np.corrcoef(np.log(m[c].clip(1e-3)), np.log(m.reported.clip(1e-3)))[0, 1]), 3),
                      "median_ratio_to_reported": round(float((m[c] / m.reported).median()), 3),
                      "share_below_reported": round(float((m[c] < m.reported).mean()), 3)}
        res["reported_median"] = round(float(m.reported.median()), 3)
    json.dump(res, open(ROOT / "results" / "nport_turnover_validation.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
