"""
build_panel.py: full-universe, share-based, unit-consistent 13F panel.

Input: the SEC Form 13F Data Sets zips in sec13f_cache/ (see download.py).
Each zip has tab-separated SUBMISSION, COVERPAGE and INFOTABLE files keyed by
ACCESSION_NUMBER. Column names follow the SEC's data-set readme; the reader
matches them case-insensitively and fails loudly if a required one is missing.

Rules (each answers a problem found in the audit, docs/novelty-audit/):
1. Units. 13F market value is in thousands of dollars for filings made before
   2023-01-03 and in dollars from that date (SEC data-set readme). VALUE is put
   in dollars using the FILING date, so late amendments are handled too. Then a
   per-filing implied-price check rescales filings that kept the old unit (or
   switched early): see to_dollars().
2. Share counts only. Rows with SSHPRNAMTTYPE != "SH" (principal amounts) and
   option rows (PUTCALL set) are dropped.
3. Filing types. 13F-HR and 13F-HR/A only; 13F-NT notices carry no holdings.
4. Amendments. Per (CIK, period): the latest original-or-RESTATEMENT filing is
   the base; every NEW HOLDINGS amendment filed after it adds its rows.
5. Turnover is share-based. Every position in period t is valued at one common
   price per CUSIP for period t (median of VALUE/SHARES across all filers), so
   price moves cannot create turnover. Exited positions use the period-t price
   if any filer still holds the CUSIP, else the t-1 price.
       turnover = 0.5 * sum |N_t - N_{t-1}| * P / (0.5 * (sum N_t * P + sum N_{t-1} * P))
   tau = 63 / turnover, clipped to [5, 2000] trading days (as in the paper).
   A split-rebased variant applies the existing price_adjusted_tdi rule.

Outputs (in panel_13f/, gitignored):
  filings.parquet    one row per accession: cik, period, filing_date, kind
  positions/<period>.parquet  cik, period, cusip, shares, value_usd (after rules 1-4)
  stage/<zip>.parquet         compact per-zip staging rows (can be deleted after a build)
  tau.parquet        cik, period, turnover, tau, turnover_split, tau_split,
                     n_positions, aum_usd
  build_report.json  row counts at every step, so each rule's effect is logged

Usage: python rebuild_13f/build_panel.py [--cache sec13f_cache] [--out panel_13f]
Deterministic; no randomness.
"""
import argparse, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UNIT_CUTOFF = pd.Timestamp("2023-01-03")
FIRST_PERIOD = "2013Q1"   # earliest report period kept (data sets begin with 2013 filings)
TAU_LO, TAU_HI = 5.0, 2000.0
SPLITS = (2, 3, 4, 5, 6, 8, 10, 20)

def _read(zf, stem, cols):
    names = {Path(n).name.upper(): n for n in zf.namelist()}
    key = next((k for k in names if k.startswith(stem) and k.endswith((".TSV", ".TXT"))), None)
    if key is None:
        raise KeyError(f"{stem} file not found in {zf.filename}: {sorted(names)}")
    with zf.open(names[key]) as fh:
        header = fh.readline().decode("utf-8", errors="replace").rstrip("\r\n").split("\t")
    upper = {h.strip().upper(): h for h in header}
    missing = [c for c in cols if c not in upper]
    if missing:
        raise KeyError(f"{key} in {zf.filename} lacks columns {missing}; has {header}")
    with zf.open(names[key]) as fh:
        df = pd.read_csv(fh, sep="\t", dtype=str, keep_default_na=False, quoting=3,
                         on_bad_lines="warn", usecols=[upper[c] for c in cols], encoding_errors="replace")
    df.columns = [c.strip().upper() for c in df.columns]
    return df[cols]

def _date(s):
    d = pd.to_datetime(s, format="%d-%b-%Y", errors="coerce")
    bad = d.isna() & s.ne("")
    if bad.any():
        d[bad] = pd.to_datetime(s[bad], errors="coerce")
    return d

def _quarter(d):
    return d.dt.year.astype("Int64").astype(str) + "Q" + d.dt.quarter.astype("Int64").astype(str)

def load_zip(path, report):
    with zipfile.ZipFile(path) as zf:
        sub = _read(zf, "SUBMISSION", ["ACCESSION_NUMBER", "FILING_DATE", "SUBMISSIONTYPE", "CIK", "PERIODOFREPORT"])
        cov = _read(zf, "COVERPAGE", ["ACCESSION_NUMBER", "ISAMENDMENT", "AMENDMENTTYPE", "REPORTTYPE"])
        inf = _read(zf, "INFOTABLE", ["ACCESSION_NUMBER", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL"])
    r = report.setdefault(Path(path).name, {})
    r["submissions"], r["infotable_rows"] = len(sub), len(inf)
    f = sub.merge(cov, on="ACCESSION_NUMBER", how="left")
    f = f[f.SUBMISSIONTYPE.str.upper().isin(["13F-HR", "13F-HR/A"])]
    f = f[~f.REPORTTYPE.str.upper().str.contains("NOTICE", na=False)]
    f["filing_date"], f["period_end"] = _date(f.FILING_DATE), _date(f.PERIODOFREPORT)
    f = f.dropna(subset=["filing_date", "period_end"])
    amend = f.ISAMENDMENT.str.upper().eq("Y")
    newh = f.AMENDMENTTYPE.str.upper().str.contains("NEW HOLDINGS", na=False)
    f["kind"] = np.where(amend & newh, "new_holdings", np.where(amend, "restatement", "original"))
    f["cik"] = f.CIK.str.lstrip("0")
    f["period"] = _quarter(f.period_end)
    f = f.rename(columns={"ACCESSION_NUMBER": "accession"})[["accession", "cik", "period", "filing_date", "kind"]]
    r["holdings_filings"] = len(f)
    inf = inf[inf.ACCESSION_NUMBER.isin(f.accession)]
    keep = inf.SSHPRNAMTTYPE.str.upper().eq("SH") & inf.PUTCALL.str.strip().eq("")
    r["rows_dropped_not_shares_or_options"] = int((~keep).sum())
    inf = inf[keep].rename(columns={"ACCESSION_NUMBER": "accession"})
    inf["shares"] = pd.to_numeric(inf.SSHPRNAMT.str.replace(",", ""), errors="coerce").astype("float64")
    inf["value_raw"] = pd.to_numeric(inf.VALUE.str.replace(",", ""), errors="coerce").astype("float64")
    inf["cusip"] = inf.CUSIP.str.upper().str.strip()
    inf = inf.dropna(subset=["shares", "value_raw"])
    inf = inf[(inf.shares > 0) & (inf.value_raw > 0) & (inf.cusip.str.len() >= 8)]
    return f, inf[["accession", "cusip", "shares", "value_raw"]]

def resolve_amendments(filings):
    """Return the accessions that make up each (cik, period) holdings report."""
    f = filings.sort_values(["cik", "period", "filing_date", "accession"])
    base = f[f.kind != "new_holdings"].groupby(["cik", "period"]).tail(1)[["cik", "period", "accession", "filing_date"]]
    base = base.rename(columns={"accession": "base_acc", "filing_date": "base_date"})
    nh = f[f.kind == "new_holdings"].merge(base, on=["cik", "period"], how="inner")
    nh = nh[nh.filing_date >= nh.base_date]
    use = pd.concat([base.rename(columns={"base_acc": "accession"})[["cik", "period", "accession"]],
                     nh[["cik", "period", "accession"]]], ignore_index=True)
    return use.drop_duplicates()

def to_dollars(info):
    """Rule 1 plus a per-filing implied-price check.

    The filing-date rule alone is not enough: some filers kept reporting in
    thousands after 2023-01-03 (practitioner reports of a few percent of
    reports as late as 2026Q2; StoneX disclosed misreporting from 2022Q4 to
    2025Q1; Barclays amended a 2024 filing). For each accession, compare the
    median implied price (value / shares) with the cross-sectional median
    price of the same CUSIP and period (CUSIPs held by at least 3 filers). A
    filing whose median ratio sits near 1/1000 is rescaled up, near 1000 down.
    Returns (info with value_usd, counts of rescaled accessions).
    """
    info = info.copy()
    dated = info.filing_date < UNIT_CUTOFF
    info["value_usd"] = np.where(dated, info.value_raw * 1000.0, info.value_raw)
    p = info.value_usd / info.shares
    grp = info.groupby(["period", "cusip"])
    ref = p.groupby([info.period, info.cusip]).transform("median")
    n_holders = grp.cik.transform("nunique")
    ratio = (p / ref).where(n_holders >= 3)
    acc_ratio = ratio.groupby(info.accession).transform("median")
    up = acc_ratio.between(1 / 3000, 1 / 300)
    down = acc_ratio.between(300, 3000)
    info.loc[up, "value_usd"] *= 1000.0
    info.loc[down, "value_usd"] /= 1000.0
    counts = {"rows_by_date_in_thousands": int(dated.sum()), "rows_by_date_in_dollars": int((~dated).sum()),
              "accessions_rescaled_up": int(info.loc[up, "accession"].nunique()),
              "accessions_rescaled_down": int(info.loc[down, "accession"].nunique())}
    return info, counts

def _split_rebase(prev_sh, cur_sh):
    r = cur_sh / prev_sh
    out = prev_sh.copy()
    for k in SPLITS:
        hit = (np.abs(r - k) / k < 0.02) | (np.abs(r - 1 / k) * k < 0.02)
        out = np.where(hit & (out == prev_sh), prev_sh * r, out)
    return out

def turnover_panel(pos):
    price = (pos.assign(p=pos.value_usd / pos.shares).groupby(["period", "cusip"]).p.median().rename("p_common"))
    periods = sorted(pos.period.unique())
    nxt = {a: b for a, b in zip(periods, periods[1:])
           if (int(b[:4]) * 4 + int(b[5])) - (int(a[:4]) * 4 + int(a[5])) == 1}
    rows = []
    for a, b in nxt.items():
        pa, pb = pos[pos.period == a], pos[pos.period == b]
        m = pa[["cik", "cusip", "shares"]].merge(pb[["cik", "cusip", "shares"]], on=["cik", "cusip"], how="outer",
                                                 suffixes=("_0", "_1")).fillna({"shares_0": 0.0, "shares_1": 0.0})
        m = m[m.cik.isin(set(pa.cik) & set(pb.cik))]
        pr_b = price.xs(b, level="period") if b in price.index.get_level_values(0) else pd.Series(dtype=float)
        pr_a = price.xs(a, level="period")
        m["p"] = m.cusip.map(pr_b).fillna(m.cusip.map(pr_a))
        m = m.dropna(subset=["p"])
        both = (m.shares_0 > 0) & (m.shares_1 > 0)
        m["shares_0s"] = m.shares_0.astype("float64")
        m.loc[both, "shares_0s"] = _split_rebase(m.loc[both, "shares_0"].to_numpy(), m.loc[both, "shares_1"].to_numpy())
        g = m.assign(tr=(m.shares_1 - m.shares_0).abs() * m.p, trs=(m.shares_1 - m.shares_0s).abs() * m.p,
                     v0=m.shares_0 * m.p, v0s=m.shares_0s * m.p, v1=m.shares_1 * m.p).groupby("cik")
        t = g[["tr", "trs", "v0", "v0s", "v1"]].sum()
        t["turnover"] = 0.5 * t.tr / (0.5 * (t.v0 + t.v1))
        t["turnover_split"] = 0.5 * t.trs / (0.5 * (t.v0s + t.v1))
        t["period"] = b
        rows.append(t[["period", "turnover", "turnover_split"]].reset_index())
    tau = pd.concat(rows, ignore_index=True)
    for c, n in (("turnover", "tau"), ("turnover_split", "tau_split")):
        tau[n] = np.clip(63.0 / tau[c].where(tau[c] > 1e-3), TAU_LO, TAU_HI)
    size = pos.groupby(["cik", "period"]).agg(n_positions=("cusip", "nunique"), aum_usd=("value_usd", "sum")).reset_index()
    return tau.merge(size, on=["cik", "period"], how="left")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(ROOT / "sec13f_cache"))
    ap.add_argument("--out", default=str(ROOT / "panel_13f"))
    args = ap.parse_args()
    cache, out = Path(args.cache), Path(args.out)
    out.mkdir(exist_ok=True)
    # Streaming build: the full universe does not fit in memory at once.
    # Pass 1: one zip at a time -> compact staging parquet (rows tagged with period).
    # Pass 2: one period at a time -> amendments, units, aggregation.
    # Pass 3: two consecutive periods at a time -> turnover (same turnover_panel as tested).
    import pyarrow.dataset as ds
    import shutil
    stage, posdir = out / "stage", out / "positions"
    for d in (stage, posdir):
        shutil.rmtree(d, ignore_errors=True)   # never mix outputs of two builds
        d.mkdir(parents=True)
    report, F = {}, []
    zips = sorted(cache.glob("*.zip"))
    if not zips:
        raise SystemExit(f"no zips in {cache}; run rebuild_13f/download.py first")
    for z in zips:
        f, i = load_zip(z, report)
        F.append(f)
        i = i.merge(f[["accession", "period"]], on="accession").sort_values("period")
        i.to_parquet(stage / f"{z.stem}.parquet", index=False)
        print(f"{z.name}: {len(f)} holdings filings, {len(i)} share rows", flush=True)
        del i
    filings = pd.concat(F, ignore_index=True).drop_duplicates("accession")
    # The data sets start with filings made in 2013; report periods far earlier
    # (e.g. 1987, 2001) are filer date errors. Keep periods from FIRST_PERIOD on.
    pkey = filings.period.str[:4].astype(int) * 4 + filings.period.str[5].astype(int)
    too_early = pkey < (int(FIRST_PERIOD[:4]) * 4 + int(FIRST_PERIOD[5]))
    report["_filings_dropped_period_before_" + FIRST_PERIOD] = int(too_early.sum())
    filings = filings[~too_early]
    filings.to_parquet(out / "filings.parquet", index=False)
    use = resolve_amendments(filings)
    meta = use.merge(filings[["accession", "filing_date"]], on="accession")
    dataset = ds.dataset(str(stage), format="parquet")
    periods = sorted(meta.period.unique(), key=lambda q: (int(q[:4]), int(q[5])))
    unit_counts = {"rows_by_date_in_thousands": 0, "rows_by_date_in_dollars": 0,
                   "accessions_rescaled_up": 0, "accessions_rescaled_down": 0}
    n_pos, ciks = 0, set()
    for q in periods:
        rows = dataset.to_table(filter=ds.field("period") == q,
                                columns=["accession", "cusip", "shares", "value_raw"]).to_pandas()
        rows = rows.merge(meta[meta.period == q], on="accession")
        if rows.empty:
            continue
        rows, c = to_dollars(rows)
        for k in unit_counts:
            unit_counts[k] += c[k]
        p = rows.groupby(["cik", "period", "cusip"], as_index=False)[["shares", "value_usd"]].sum()
        p.to_parquet(posdir / f"{q}.parquet", index=False)
        n_pos += len(p); ciks |= set(p.cik)
        print(f"{q}: {len(p)} positions, {p.cik.nunique()} filers", flush=True)
    del dataset
    taus, done = [], [q for q in periods if (posdir / f"{q}.parquet").exists()]
    for a, b in zip(done, done[1:]):
        if (int(b[:4]) * 4 + int(b[5])) - (int(a[:4]) * 4 + int(a[5])) != 1:
            continue
        pair = pd.concat([pd.read_parquet(posdir / f"{a}.parquet"), pd.read_parquet(posdir / f"{b}.parquet")])
        t = turnover_panel(pair)
        taus.append(t[t.period == b])
    tau = pd.concat(taus, ignore_index=True) if taus else pd.DataFrame()
    tau.to_parquet(out / "tau.parquet", index=False)
    summary = {"zips": len(zips), "holdings_filings": int(len(filings)),
               "amendment_kinds": filings.kind.value_counts().to_dict(),
               "reports_used": int(use.groupby(["cik", "period"]).ngroups),
               **unit_counts,
               "positions": int(n_pos), "institutions": len(ciks), "periods": done,
               "tau_rows": int(len(tau)), "tau_median": float(tau.tau.median()) if len(tau) else None,
               "per_zip": report}
    (out / "build_report.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("per_zip", "periods")}, indent=1, default=str))

if __name__ == "__main__":
    main()
