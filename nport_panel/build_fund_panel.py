"""
build_fund_panel.py: fund-level (series) panel of equity holdings and share-based
horizons from the SEC Form N-PORT Data Sets (2019Q4 onward).

Input: nport_cache/*_nport.zip (stage2/download_nport.py). Each zip holds the
N-PORT-P filings made public in that calendar quarter: one report per fund series
per fiscal quarter, dated REPORT_DATE (staggered month-ends).

Rules:
1. Reports. Key = (SERIES_ID, REPORT_DATE). An amendment (NPORT-P/A) or any later
   filing for the same key replaces earlier ones: keep the latest FILING_DATE
   (ties: higher accession number).
2. Holdings kept: ASSET_CAT == "EC" (common equity), UNIT == "NS" (number of
   shares), PAYOFF_PROFILE == "Long", BALANCE > 0, CURRENCY_VALUE > 0, a 9-character
   CUSIP other than all zeros. Rows of one report with the same CUSIP are summed.
   (Foreign listings without a CUSIP are not used yet; see README.)
3. Value. CURRENCY_VALUE is the position value in US dollars (Form N-PORT Item C.2.b;
   checked on known prices).
4. Turnover between consecutive reports of the same series, 2 to 4 months apart,
   share-based at one common price per CUSIP and report month (median of value /
   shares across all funds reporting that month; for a position held only in the
   earlier report, that report month's price):
       turnover = 0.5 * sum |N_t - N_{t-1}| * P / (0.5 * (sum N_t * P + sum N_{t-1} * P))
   Split-rebased variant: a position's earlier share count is multiplied by k
   (k or 1/k in SPLITS) only if BOTH the fund's share ratio is within 2% of k AND
   the CUSIP's common price ratio between the two report months is within 10% of
   1/k. (The 13F rule uses the share ratio alone, which mistakes selling exactly
   half a position for a reverse split; N-PORT's monthly prices allow the check.)
   tau = 63 / turnover (quarterly turnover; same definition as the 13F panel),
   clipped to [5, 2000]. Turnover is scaled to a 3-month gap by 3 / gap_months.
   turnover_min (split-rebased) = min(purchases, sales) / average value, the
   prospectus definition, which nets out flow-driven buying or selling. It is used
   to validate against reported turnover; tau stays on the share-based turnover.
5. Calendar period of a report = calendar quarter of REPORT_DATE.

Outputs (nport_panel/ in the repo root, gitignored):
  reports.parquet        one row per kept report: series_id, report_date, accession,
                         filing_date, registrant cik, series name, net assets,
                         monthly flows and returns (median across share classes), counts
  holdings/<YYYY-MM>.parquet   series_id, report_date, cusip, shares, value_usd
  tau.parquet            series_id, report_date, prev_report_date, gap_months, period,
                         turnover, turnover_split, turnover_min, tau, tau_split, n_stocks, eq_value_usd
  build_report.json      counts at every step
Usage: python nport_panel/build_fund_panel.py [--cache nport_cache] [--out nport_panel_data]
Deterministic.
"""
import argparse, json, shutil, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAU_LO, TAU_HI = 5.0, 2000.0
SPLITS = (2, 3, 4, 5, 6, 8, 10, 20)   # same factors as rebuild_13f
HOLD_COLS = ["ACCESSION_NUMBER", "ISSUER_CUSIP", "BALANCE", "UNIT", "CURRENCY_VALUE", "PAYOFF_PROFILE", "ASSET_CAT"]
INFO_COLS = ["ACCESSION_NUMBER", "SERIES_ID", "SERIES_NAME", "NET_ASSETS",
             "SALES_FLOW_MON1", "SALES_FLOW_MON2", "SALES_FLOW_MON3",
             "REDEMPTION_FLOW_MON1", "REDEMPTION_FLOW_MON2", "REDEMPTION_FLOW_MON3",
             "REINVESTMENT_FLOW_MON1", "REINVESTMENT_FLOW_MON2", "REINVESTMENT_FLOW_MON3"]


def _tsv(z, name, usecols=None, chunksize=None):
    return pd.read_csv(z.open(name + ".tsv"), sep="\t", dtype=str, usecols=usecols,
                       chunksize=chunksize, keep_default_na=False, na_values=[""])


def load_zip(path):
    """Report table and filtered equity holdings for one data-set zip."""
    z = zipfile.ZipFile(path)
    sub = _tsv(z, "SUBMISSION", ["ACCESSION_NUMBER", "FILING_DATE", "SUB_TYPE", "REPORT_DATE"])
    reg = _tsv(z, "REGISTRANT", ["ACCESSION_NUMBER", "CIK"])
    info = _tsv(z, "FUND_REPORTED_INFO", INFO_COLS)
    ret = _tsv(z, "MONTHLY_TOTAL_RETURN", ["ACCESSION_NUMBER", "MONTHLY_TOTAL_RETURN1",
                                           "MONTHLY_TOTAL_RETURN2", "MONTHLY_TOTAL_RETURN3"])
    for c in ret.columns[1:]:
        ret[c] = pd.to_numeric(ret[c], errors="coerce")
    ret = ret.groupby("ACCESSION_NUMBER").median()   # median across share classes
    rep = sub.merge(reg, on="ACCESSION_NUMBER", how="left").merge(info, on="ACCESSION_NUMBER", how="inner")
    rep = rep.join(ret, on="ACCESSION_NUMBER")
    rep["FILING_DATE"] = pd.to_datetime(rep.FILING_DATE, format="%d-%b-%Y")
    rep["REPORT_DATE"] = pd.to_datetime(rep.REPORT_DATE, format="%d-%b-%Y")
    for c in INFO_COLS[3:]:
        rep[c] = pd.to_numeric(rep[c], errors="coerce")
    parts = []
    for ch in _tsv(z, "FUND_REPORTED_HOLDING", HOLD_COLS, chunksize=2_000_000):
        ch = ch[(ch.ASSET_CAT == "EC") & (ch.UNIT == "NS") & (ch.PAYOFF_PROFILE == "Long")]
        ch = ch[ch.ISSUER_CUSIP.str.fullmatch(r"[0-9A-Z]{9}", na=False) & (ch.ISSUER_CUSIP != "000000000")]
        sh = pd.to_numeric(ch.BALANCE, errors="coerce")
        v = pd.to_numeric(ch.CURRENCY_VALUE, errors="coerce")
        ok = (sh > 0) & (v > 0)
        parts.append(pd.DataFrame({"accession": ch.ACCESSION_NUMBER[ok], "cusip": ch.ISSUER_CUSIP[ok],
                                   "shares": sh[ok].astype("float64"), "value_usd": v[ok].astype("float64")}))
    hold = pd.concat(parts, ignore_index=True).groupby(["accession", "cusip"], as_index=False).sum()
    rep = rep.rename(columns={"ACCESSION_NUMBER": "accession", "FILING_DATE": "filing_date", "SUB_TYPE": "sub_type",
                              "REPORT_DATE": "report_date", "CIK": "registrant_cik", "SERIES_ID": "series_id",
                              "SERIES_NAME": "series_name", "NET_ASSETS": "net_assets"})
    rep.columns = [c.lower() for c in rep.columns]
    return rep, hold


def resolve_reports(rep):
    """Rule 1: latest filing per (series_id, report_date)."""
    rep = rep.dropna(subset=["series_id", "report_date"])
    rep = rep.sort_values(["series_id", "report_date", "filing_date", "accession"])
    return rep.groupby(["series_id", "report_date"]).tail(1)


def month_key(d):
    return d.dt.strftime("%Y-%m")


def split_rebase(sh0, sh1, price_ratio):
    """Rebase earlier shares for splits confirmed by both the fund's share ratio and the common price ratio."""
    sh0 = np.asarray(sh0, dtype="float64")
    out = sh0.copy()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.asarray(sh1, dtype="float64") / sh0
        for k in SPLITS:
            for f in (k, 1.0 / k):
                hit = (np.abs(r / f - 1) < 0.02) & (np.abs(price_ratio * f - 1) < 0.10) & (out == sh0) & (sh0 > 0)
                out = np.where(hit, sh0 * f, out)
    return out


def turnover_pairs(cur, prev, price_cur, price_prev):
    """cur, prev: holdings rows (pair_id, cusip, shares). Returns per pair_id turnover."""
    m = cur.merge(prev, on=["pair_id", "cusip"], how="outer", suffixes=("_1", "_0"))
    m[["shares_0", "shares_1"]] = m[["shares_0", "shares_1"]].fillna(0.0)
    m["p"] = m.cusip.map(price_cur)
    m["p"] = m.p.fillna(m.cusip.map(price_prev))
    m = m.dropna(subset=["p"])
    m["shares_0s"] = split_rebase(m.shares_0.to_numpy(), m.shares_1.to_numpy(),
                                  (m.cusip.map(price_cur) / m.cusip.map(price_prev)).to_numpy())
    d = m.shares_1 - m.shares_0s
    g = m.assign(tr=(m.shares_1 - m.shares_0).abs() * m.p, trs=d.abs() * m.p,
                 buy=d.clip(lower=0) * m.p, sell=(-d).clip(lower=0) * m.p,
                 v0=m.shares_0 * m.p, v0s=m.shares_0s * m.p, v1=m.shares_1 * m.p).groupby("pair_id")
    t = g[["tr", "trs", "buy", "sell", "v0", "v0s", "v1"]].sum()
    t["turnover"] = 0.5 * t.tr / (0.5 * (t.v0 + t.v1))
    t["turnover_split"] = 0.5 * t.trs / (0.5 * (t.v0s + t.v1))
    # prospectus definition: lesser of purchases or sales over average value (flows net out)
    t["turnover_min"] = np.minimum(t.buy, t.sell) / (0.5 * (t.v0s + t.v1))
    return t[["turnover", "turnover_split", "turnover_min"]]


def build_tau(reports, holddir):
    """Rule 4, one current report month at a time (loads that month and the 4 before)."""
    r = reports.sort_values(["series_id", "report_date"]).copy()
    r["prev_report_date"] = r.groupby("series_id").report_date.shift(1)
    r["gap_months"] = ((r.report_date.dt.year - r.prev_report_date.dt.year) * 12
                       + (r.report_date.dt.month - r.prev_report_date.dt.month))
    pairs = r[r.gap_months.between(2, 4)][["series_id", "report_date", "prev_report_date", "gap_months"]].reset_index(drop=True)
    pairs["pair_id"] = np.arange(len(pairs))
    pairs["m1"], pairs["m0"] = month_key(pairs.report_date), month_key(pairs.prev_report_date)
    cache, price = {}, {}

    def load(m):
        if m not in cache:
            p = holddir / f"{m}.parquet"
            h = pd.read_parquet(p) if p.exists() else pd.DataFrame(columns=["series_id", "report_date", "cusip", "shares", "value_usd"])
            cache[m] = h
            price[m] = (h.value_usd / h.shares).groupby(h.cusip).median() if len(h) else pd.Series(dtype=float)
        return cache[m]

    out = []
    for m1, grp in pairs.groupby("m1", sort=True):
        h1 = load(m1).merge(grp[["series_id", "report_date", "pair_id"]], on=["series_id", "report_date"])
        h0 = []
        for m0, g0 in grp.groupby("m0"):
            h0.append(load(m0).merge(g0[["series_id", "prev_report_date", "pair_id"]],
                                     left_on=["series_id", "report_date"], right_on=["series_id", "prev_report_date"]))
        h0 = pd.concat(h0, ignore_index=True)
        # price for positions only in the earlier report: that report month's median price
        p_prev = pd.concat([price[m] for m in grp.m0.unique()]).groupby(level=0).median()
        t = turnover_pairs(h1[["pair_id", "cusip", "shares"]], h0[["pair_id", "cusip", "shares"]], price[m1], p_prev)
        out.append(grp.join(t, on="pair_id"))
        for m in [k for k in cache if k < (pd.Timestamp(m1 + "-01") - pd.DateOffset(months=5)).strftime("%Y-%m")]:
            cache.pop(m); price.pop(m)
    tau = pd.concat(out, ignore_index=True)
    for c in ("turnover", "turnover_split", "turnover_min"):
        tau[c] = tau[c] * 3.0 / tau.gap_months
    for c, n in (("turnover", "tau"), ("turnover_split", "tau_split")):
        tau[n] = np.clip(63.0 / tau[c].where(tau[c] > 1e-3), TAU_LO, TAU_HI)
    tau["period"] = tau.report_date.dt.year.astype(str) + "Q" + tau.report_date.dt.quarter.astype(str)
    size = reports[["series_id", "report_date", "n_stocks", "eq_value_usd"]]
    return tau.drop(columns=["pair_id", "m0", "m1"]).merge(size, on=["series_id", "report_date"], how="left")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(ROOT / "nport_cache"))
    ap.add_argument("--out", default=str(ROOT / "nport_panel_data"))
    args = ap.parse_args()
    cache, out = Path(args.cache), Path(args.out)
    zips = sorted(cache.glob("*_nport.zip"))
    if not zips:
        raise SystemExit(f"no zips in {cache}; run stage2/download_nport.py first")
    stage, holddir = out / "stage", out / "holdings"
    for d in (stage, holddir):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    report, R = {"zips": [z.name for z in zips]}, []
    for z in zips:
        rep, hold = load_zip(z)
        hold.to_parquet(stage / f"{z.stem}.parquet", index=False)
        R.append(rep)
        report[z.stem] = {"reports": int(len(rep)), "equity_rows": int(len(hold))}
        print(f"{z.name}: {len(rep)} reports, {len(hold)} equity share rows", flush=True)
    allrep = pd.concat(R, ignore_index=True).drop_duplicates("accession")
    reports = resolve_reports(allrep)
    report["reports_all"], report["reports_kept"] = int(len(allrep)), int(len(reports))
    keep = set(reports.accession)
    # re-partition kept holdings by report month
    meta = reports[["accession", "series_id", "report_date"]]
    bymonth = {}
    for f in sorted(stage.glob("*.parquet")):
        h = pd.read_parquet(f)
        h = h[h.accession.isin(keep)].merge(meta, on="accession")
        for m, g in h.groupby(month_key(h.report_date)):
            bymonth.setdefault(m, []).append(g.drop(columns="accession"))
    n_rows = 0
    sizes = []
    for m, parts in sorted(bymonth.items()):
        g = pd.concat(parts, ignore_index=True)
        g.to_parquet(holddir / f"{m}.parquet", index=False)
        n_rows += len(g)
        sizes.append(g.groupby(["series_id", "report_date"]).agg(n_stocks=("cusip", "nunique"), eq_value_usd=("value_usd", "sum")))
    sizes = pd.concat(sizes).reset_index()
    reports = reports.merge(sizes, on=["series_id", "report_date"], how="left")
    reports["n_stocks"] = reports.n_stocks.fillna(0).astype(int)
    reports["eq_value_usd"] = reports.eq_value_usd.fillna(0.0)
    reports.to_parquet(out / "reports.parquet", index=False)
    report["equity_rows_kept"] = n_rows
    tau = build_tau(reports, holddir)
    tau.to_parquet(out / "tau.parquet", index=False)
    report["tau_rows"] = int(len(tau))
    report["tau_rows_gap3"] = int((tau.gap_months == 3).sum())
    report["series_with_tau"] = int(tau.series_id.nunique())
    report["report_months"] = [str(reports.report_date.min().date()), str(reports.report_date.max().date())]
    json.dump(report, open(out / "build_report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in report.items() if not k.endswith("_nport")}, indent=1))


if __name__ == "__main__":
    main()
