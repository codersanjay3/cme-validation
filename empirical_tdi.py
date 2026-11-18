#!/usr/bin/env python3
"""
empirical_tdi.py — Empirical Temporal Diversity Index from SEC 13-F filings

Method:
  1. Download quarterly 13-F-HR filings for top ~150 institutional filers from EDGAR
  2. Compute per-institution portfolio turnover Q-over-Q
  3. Map turnover → effective lookback horizon τ (trading days):  τ = 63 / turnover
  4. Compute TDI = −Σ f_k ln(f_k), K=16 bins over log(τ), same formula as cme_canonical.py
  5. Correlate quarterly TDI with quarterly average VIX
  6. Plot and report

Data sources:
  - Holdings: SEC EDGAR (free, public API)
  - VIX: Yahoo Finance (^VIX)

Coverage: 2013 Q1 to 2024 Q3 (post-XML standardisation era)

Caching: all EDGAR downloads saved to edgar_cache/ to avoid re-fetching.
"""

import os
import time
import json
import gzip
import csv
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats

# ── Configuration ────────────────────────────────────────────────────────────

CACHE_DIR = Path("/Users/sanjaysubramania/cme_validation/edgar_cache")
OUT_DIR   = Path("/Users/sanjaysubramania/cme_validation/figures")
CACHE_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

START_YEAR   = 2013   # XML format standardised
END_YEAR     = 2024
END_QUARTER  = 3      # last complete quarter as of mid-2024

# How many institutions to track (sorted by filing consistency)
TOP_N_FILERS = 150

# TDI parameters — must match cme_canonical.py exactly
TDI_K    = 16
TAU_MIN  = 1.0    # trading days
TAU_MAX  = 2000.0 # ~8 years — matches Definition 2 upper bound ln(2000)

# τ bounds after turnover mapping
TAU_FLOOR = 5.0    # 1 week minimum
TAU_CAP   = 2000.0 # matches TAU_MAX upper bound (prevents artificial mass point at log(1260))

EDGAR_HEADERS = {
    "User-Agent": "CME-Validation jaysubbu@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}
EDGAR_RATE = 0.12   # seconds between requests (stay under EDGAR's 10 req/s limit)

# ── EDGAR helpers ─────────────────────────────────────────────────────────────

def edgar_get(url: str, cache_key: str | None = None, binary: bool = False):
    """Fetch URL with local disk cache and polite rate limiting."""
    if cache_key:
        p = CACHE_DIR / cache_key
        if p.exists():
            return p.read_bytes() if binary else p.read_text(encoding="utf-8", errors="replace")
    time.sleep(EDGAR_RATE)
    r = requests.get(url, headers=EDGAR_HEADERS, timeout=30)
    r.raise_for_status()
    data = r.content if binary else r.text
    if cache_key:
        p = CACHE_DIR / cache_key
        p.parent.mkdir(parents=True, exist_ok=True)
        if binary:
            p.write_bytes(data)
        else:
            p.write_text(data if isinstance(data, str) else data.decode("utf-8", errors="replace"))
    return data


def quarter_range():
    """Yield (year, quarter) pairs from START_YEAR Q1 to END_YEAR/END_QUARTER."""
    for y in range(START_YEAR, END_YEAR + 1):
        for q in range(1, 5):
            if y == END_YEAR and q > END_QUARTER:
                break
            yield y, q


def quarter_label(year, q):
    return f"{year}Q{q}"


# ── Step 1: Identify top 13-F-HR filers from EDGAR full-index ────────────────

def get_all_13f_filers():
    """
    Download EDGAR quarterly company.gz index files, filter for 13F-HR,
    return a Counter of {cik: number_of_quarters_filed}.
    """
    from collections import Counter
    cik_counts = Counter()
    cik_names  = {}

    print("Scanning EDGAR full-index for 13F-HR filers ...")
    for year, q in quarter_range():
        url       = f"https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{q}/company.gz"
        cache_key = f"index/{year}_Q{q}_company.gz"
        try:
            raw = edgar_get(url, cache_key, binary=True)
        except Exception as e:
            print(f"  {year} Q{q}: index fetch failed ({e})")
            continue

        try:
            with gzip.open(io.BytesIO(raw), "rt", encoding="latin-1") as f:
                for line in f:
                    # Fixed-width format: company(62) form_type(12) cik(12) date(12) filename
                    if len(line) < 86:
                        continue
                    company   = line[0:62].strip()
                    form_type = line[62:74].strip()
                    cik_raw   = line[74:86].strip()
                    if form_type in ("13F-HR", "13F-HR/A"):
                        cik = cik_raw.lstrip("0") or "0"
                        cik_counts[cik] += 1
                        cik_names[cik]   = company
        except Exception as e:
            print(f"  {year} Q{q}: parse failed ({e})")

    return cik_counts, cik_names


def select_top_filers(cik_counts, cik_names, n=TOP_N_FILERS):
    """Return the n CIKs with most quarterly filings (proxy for large, consistent institutions)."""
    ranked = sorted(cik_counts.items(), key=lambda x: -x[1])
    result = []
    for cik, cnt in ranked[:n]:
        result.append({"cik": cik, "filings": cnt, "name": cik_names.get(cik, "")})
    return result


# ── Step 2: Download 13-F-HR XML holdings per filer per quarter ───────────────

def get_filings_for_cik(cik: str):
    """Return list of {form, filed, accession, period_of_report} dicts from submissions API."""
    padded = cik.zfill(10)
    url    = f"https://data.sec.gov/submissions/CIK{padded}.json"
    cache_key = f"submissions/{padded}.json"
    try:
        raw = edgar_get(url, cache_key)
        data = json.loads(raw)
    except Exception:
        return []

    filings = []
    recent  = data.get("filings", {}).get("recent", {})
    forms   = recent.get("form", [])
    dates   = recent.get("filingDate", [])
    accnos  = recent.get("accessionNumber", [])
    periods = recent.get("reportDate", [])

    for form, date, acc, period in zip(forms, dates, accnos, periods):
        if form in ("13F-HR",):
            filings.append({
                "form":   form,
                "filed":  date,
                "accession": acc.replace("-", ""),
                "period": period,
            })

    # Also check older filings
    for page_key in ["files"]:
        for file_entry in data.get("filings", {}).get(page_key, []):
            fname = file_entry.get("name", "")
            if fname.endswith(".json"):
                sub_url = f"https://data.sec.gov/submissions/{fname}"
                sub_cache = f"submissions/{fname}"
                try:
                    sub_raw  = edgar_get(sub_url, sub_cache)
                    sub_data = json.loads(sub_raw)
                    forms2   = sub_data.get("form", [])
                    dates2   = sub_data.get("filingDate", [])
                    accnos2  = sub_data.get("accessionNumber", [])
                    periods2 = sub_data.get("reportDate", [])
                    for form, date, acc, period in zip(forms2, dates2, accnos2, periods2):
                        if form in ("13F-HR",):
                            filings.append({
                                "form":   form,
                                "filed":  date,
                                "accession": acc.replace("-", ""),
                                "period": period,
                            })
                except Exception:
                    pass

    return filings


def period_to_quarter(period_str: str):
    """Convert '2023-09-30' to (2023, 3)."""
    try:
        y, m, _ = period_str.split("-")
        y, m = int(y), int(m)
        q = (m - 1) // 3 + 1
        return y, q
    except Exception:
        return None, None


def fetch_holdings_xml(cik: str, accession: str):
    """
    Download the primary infotable XML for a 13-F-HR filing.
    Returns list of {cusip, value_k} dicts (value in $thousands).
    """
    padded    = cik.zfill(10)
    acc_dash  = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
    index_url = (
        f"https://www.sec.gov/Archives/edgar/data/{padded}/"
        f"{accession}/{acc_dash}-index.htm"
    )
    cache_idx = f"filings/{padded}/{accession}_index.htm"

    # Get filing index to find the XML document name
    try:
        idx_html = edgar_get(index_url, cache_idx)
    except Exception:
        # Try alternative index URL
        try:
            index_url2 = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={padded}&type=13F-HR&dateb=&owner=include&count=40"
            idx_html = ""
        except Exception:
            return []

    # Look for infotable XML in the index
    xml_filename = None
    for line in idx_html.splitlines():
        low = line.lower()
        if "infotable" in low and ".xml" in low:
            # Extract filename
            import re
            m = re.search(r'href="([^"]+\.xml)"', line, re.IGNORECASE)
            if m:
                xml_filename = m.group(1).split("/")[-1]
                break
        if "primary_doc.xml" in low or ("13f" in low and ".xml" in low):
            import re
            m = re.search(r'href="([^"]+\.xml)"', line, re.IGNORECASE)
            if m:
                xml_filename = m.group(1).split("/")[-1]

    if not xml_filename:
        # Fallback: try common name patterns
        for candidate in ["infotable.xml", "primary_doc.xml", "form13fInfoTable.xml"]:
            xml_url = (
                f"https://www.sec.gov/Archives/edgar/data/{padded}/"
                f"{accession}/{candidate}"
            )
            cache_xml = f"filings/{padded}/{accession}_{candidate}"
            try:
                xml_text = edgar_get(xml_url, cache_xml)
                if "<informationTable" in xml_text or "<infoTable" in xml_text.lower():
                    xml_filename = candidate
                    break
            except Exception:
                continue
        if not xml_filename:
            return []

    xml_url = (
        f"https://www.sec.gov/Archives/edgar/data/{padded}/"
        f"{accession}/{xml_filename}"
    )
    cache_xml = f"filings/{padded}/{accession}_{xml_filename}"
    try:
        xml_text = edgar_get(xml_url, cache_xml)
    except Exception:
        return []

    return parse_holdings_xml(xml_text)


def parse_holdings_xml(xml_text: str):
    """Parse 13-F-HR infotable XML, return list of {cusip, value_k}."""
    holdings = []
    try:
        # Strip namespace declarations to simplify parsing
        import re
        xml_text = re.sub(r'\s+xmlns[^=]*="[^"]*"', "", xml_text)
        xml_text = re.sub(r'<([^/\s>]+):', "<", xml_text)  # strip namespace prefixes
        xml_text = re.sub(r'</([^/\s>]+):', "</", xml_text)

        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return holdings

    for entry in root.iter():
        tag = entry.tag.lower().replace("{", "").split("}")[-1]
        if tag in ("infotable", "edgarsubmission"):
            continue
        if tag == "infotable" or "infotable" in tag:
            pass

    # Collect all infoTable entries
    for entry in root.iter():
        tag = entry.tag.lower()
        if "infotable" not in tag and tag not in ("infotable",):
            continue

    # Try different tag patterns for table rows
    row_tags = ["infoTable", "InfoTable", "infotable"]
    rows = []
    for rt in row_tags:
        rows = root.findall(f".//{rt}")
        if rows:
            break
    if not rows:
        # Try any tag that contains cusip children
        for child in root.iter():
            cusip_el = child.find("cusip") or child.find("CUSIP")
            if cusip_el is not None:
                rows = list(root.iter(child.tag))
                break

    for row in rows:
        cusip_el = (
            row.find("cusip") or row.find("CUSIP") or
            row.find("cusip") or
            next((c for c in row if "cusip" in c.tag.lower()), None)
        )
        val_el = (
            row.find("value") or row.find("VALUE") or
            next((c for c in row if c.tag.lower() == "value"), None)
        )
        if cusip_el is not None and val_el is not None:
            try:
                cusip = cusip_el.text.strip() if cusip_el.text else ""
                value = int(val_el.text.strip().replace(",", "")) if val_el.text else 0
                if cusip and value > 0:
                    holdings.append({"cusip": cusip, "value_k": value})
            except (ValueError, AttributeError):
                continue

    return holdings


# ── Step 3: Compute turnover and τ ───────────────────────────────────────────

def compute_turnover(holdings_prev: list, holdings_curr: list) -> float | None:
    """
    Compute quarterly portfolio turnover between two periods.
    Turnover = ($ bought + $ sold) / (2 × avg total portfolio value)
    Returns turnover as a fraction (0 to 1+), or None if data too sparse.
    """
    if not holdings_prev or not holdings_curr:
        return None

    prev = {h["cusip"]: h["value_k"] for h in holdings_prev}
    curr = {h["cusip"]: h["value_k"] for h in holdings_curr}

    total_prev = sum(prev.values())
    total_curr = sum(curr.values())
    if total_prev < 1000 or total_curr < 1000:  # < $1M, too small
        return None

    all_cusips = set(prev) | set(curr)
    bought = sold = 0.0
    for c in all_cusips:
        p = prev.get(c, 0)
        q = curr.get(c, 0)
        if q > p:
            bought += q - p
        else:
            sold += p - q

    avg_portfolio = (total_prev + total_curr) / 2.0
    turnover = (bought + sold) / (2.0 * avg_portfolio)
    return float(turnover)


def turnover_to_tau(turnover: float) -> float:
    """
    Map quarterly turnover fraction to effective lookback τ in trading days.
    τ = 63 / turnover  (one quarter ≈ 63 trading days)
    Clipped to [TAU_FLOOR, TAU_CAP].
    """
    if turnover <= 0:
        return TAU_CAP
    tau = 63.0 / turnover
    return float(np.clip(tau, TAU_FLOOR, TAU_CAP))


# ── Step 4: Compute TDI ───────────────────────────────────────────────────────

def compute_tdi(tau_values: list[float]) -> float | None:
    """
    Compute TDI = −Σ f_k ln(f_k) over K=16 bins of log(τ).
    Same formula as cme_canonical.py.
    """
    if len(tau_values) < 5:
        return None
    # Definition 2 uses log(τ), NOT log(τ+1). For empirical τ∈[TAU_FLOOR, TAU_CAP]=[5,2000],
    # log(τ) is always defined (τ≥5>0). Using log(τ+1) causes τ=TAU_CAP=2000 to give
    # log(2001)=7.6014 > log(2000)=7.6009, silently dropping those values from the histogram.
    log_tau = np.log(np.array(tau_values, dtype=float))
    log_min = np.log(TAU_MIN)
    log_max = np.log(TAU_MAX)
    counts, _ = np.histogram(log_tau, bins=TDI_K, range=(log_min, log_max))
    total = counts.sum()
    if total == 0:
        return None
    freqs = counts / total
    freqs = freqs[freqs > 0]
    tdi = -np.sum(freqs * np.log(freqs))
    return float(tdi)


# ── Step 5: VIX data ──────────────────────────────────────────────────────────

def get_quarterly_vix():
    """
    Download VIX daily closes via yfinance, return quarterly averages as a
    dict {(year, quarter): mean_vix}.
    """
    import yfinance as yf
    print("Downloading VIX data ...")
    vix = yf.download("^VIX", start=f"{START_YEAR}-01-01", end=f"{END_YEAR}-12-31",
                      progress=False, auto_adjust=True)
    if vix.empty:
        print("  VIX download failed — trying CBOE direct CSV ...")
        url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
        try:
            vix = pd.read_csv(url, parse_dates=["DATE"], index_col="DATE")
            vix.columns = [c.strip() for c in vix.columns]
            vix = vix.rename(columns={"CLOSE": "Close"})
        except Exception as e:
            print(f"  CBOE CSV also failed: {e}")
            return {}

    close = vix["Close"].squeeze()
    close.index = pd.to_datetime(close.index)
    close = close.dropna()

    # TIMING NOTE: VIX is computed as an intra-quarter average of daily closes,
    # while 13-F filings are end-of-quarter snapshots of portfolio holdings.
    # This timing mismatch (flow vs. stock) may attenuate the TDI–VIX correlation
    # because intra-quarter VIX variation is averaged away rather than measured
    # at the same moment the 13-F snapshot is taken.

    result = {}
    for (y, q) in quarter_range():
        m_start = (q - 1) * 3 + 1
        m_end   = m_start + 2
        mask = (close.index.year == y) & (close.index.month >= m_start) & (close.index.month <= m_end)
        subset = close[mask]
        if len(subset) > 0:
            result[(y, q)] = float(subset.mean())

    return result


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    # ── 1. Identify top filers ──────────────────────────────────────────────
    cik_counts_path = CACHE_DIR / "cik_counts.json"
    if cik_counts_path.exists():
        print("Loading cached filer list ...")
        with open(cik_counts_path) as f:
            saved = json.load(f)
        cik_counts = saved["counts"]
        cik_names  = saved["names"]
    else:
        cik_counts, cik_names = get_all_13f_filers()
        with open(cik_counts_path, "w") as f:
            json.dump({"counts": dict(cik_counts), "names": cik_names}, f)

    top_filers = select_top_filers(cik_counts, cik_names, TOP_N_FILERS)
    print(f"\nTop {len(top_filers)} filers selected. Top 5:")
    for f in top_filers[:5]:
        print(f"  CIK {f['cik']}: {f['name']} ({f['filings']} filings)")

    # ── 2. Build holdings database ──────────────────────────────────────────
    holdings_db_path = CACHE_DIR / "holdings_db.json"
    if holdings_db_path.exists():
        print("\nLoading cached holdings database ...")
        with open(holdings_db_path) as f:
            holdings_db = json.load(f)
    else:
        holdings_db = {}  # holdings_db[cik][quarter_label] = [holdings]

    need_save = False
    total_filers = len(top_filers)

    for idx, filer in enumerate(top_filers):
        cik = filer["cik"]
        print(f"\n[{idx+1}/{total_filers}] {filer['name']} (CIK {cik})")

        if cik not in holdings_db:
            holdings_db[cik] = {}

        filings = get_filings_for_cik(cik)
        print(f"  Found {len(filings)} 13F-HR filings")

        for filing in filings:
            y, q = period_to_quarter(filing["period"])
            if y is None:
                continue
            if y < START_YEAR or (y == END_YEAR and q > END_QUARTER):
                continue
            qlabel = quarter_label(y, q)
            if qlabel in holdings_db[cik]:
                continue  # already cached

            holdings = fetch_holdings_xml(cik, filing["accession"])
            if holdings:
                holdings_db[cik][qlabel] = holdings
                print(f"    {qlabel}: {len(holdings)} positions")
                need_save = True
            else:
                print(f"    {qlabel}: no holdings parsed")

    if need_save:
        print("\nSaving holdings database ...")
        with open(holdings_db_path, "w") as f:
            json.dump(holdings_db, f)

    # ── 3. Compute turnover and τ per institution per quarter ───────────────
    print("\nComputing turnover and τ ...")
    quarters = list(quarter_range())
    tau_by_quarter = defaultdict(list)  # {(y,q): [tau values]}

    for cik, qdata in holdings_db.items():
        sorted_quarters = sorted(qdata.keys())
        for i in range(1, len(sorted_quarters)):
            prev_ql = sorted_quarters[i - 1]
            curr_ql = sorted_quarters[i]

            # Verify they are consecutive quarters
            py, pq = int(prev_ql[:4]), int(prev_ql[5])
            cy, cq = int(curr_ql[:4]), int(curr_ql[5])
            expected_next = (py, pq + 1) if pq < 4 else (py + 1, 1)
            if (cy, cq) != expected_next:
                continue  # gap in filings; skip

            turnover = compute_turnover(qdata[prev_ql], qdata[curr_ql])
            if turnover is None or turnover <= 0:
                continue

            tau = turnover_to_tau(turnover)
            tau_by_quarter[(cy, cq)].append(tau)

    # ── 4. Compute TDI per quarter ──────────────────────────────────────────
    print("Computing quarterly TDI ...")
    tdi_series = {}
    tau_count_series = {}
    for yq, taus in sorted(tau_by_quarter.items()):
        tdi = compute_tdi(taus)
        if tdi is not None:
            tdi_series[yq] = tdi
            tau_count_series[yq] = len(taus)
            print(f"  {yq[0]}Q{yq[1]}: TDI={tdi:.4f}  n={len(taus)}")

    # ── 5. VIX ──────────────────────────────────────────────────────────────
    vix_quarterly = get_quarterly_vix()

    # ── 6. Merge and correlate ───────────────────────────────────────────────
    common_quarters = sorted(set(tdi_series) & set(vix_quarterly))
    if len(common_quarters) < 4:
        print(f"\nOnly {len(common_quarters)} quarters in common — too few to correlate.")
        return

    tdi_vals = [tdi_series[q] for q in common_quarters]
    vix_vals = [vix_quarterly[q] for q in common_quarters]
    labels   = [f"{y}Q{q}" for y, q in common_quarters]

    # ── Apply n≥50 filter FIRST — this is the primary analysis series ─────────
    # All downstream statistics (contemporaneous, lags, exclusions) use this
    # filtered series only.  The raw 46-quarter series is NOT used for any
    # reported statistic — doing so would include e.g. 2013Q2 with n=9.
    quarters_n50 = [q for q in common_quarters if tau_count_series.get(q, 0) >= 50]
    tdi_n50 = np.array([tdi_series[q] for q in quarters_n50])
    vix_n50 = np.array([vix_quarterly[q] for q in quarters_n50])
    n_n50 = len(quarters_n50)
    print(f"\nn≥50 filter: {n_n50} quarters retained (dropped {len(common_quarters) - n_n50})")

    # 1. Contemporaneous correlation (main result)
    r, p = stats.pearsonr(tdi_n50, vix_n50)
    n = n_n50
    print(f"Main r(TDI,VIX) = {r:.4f}, p = {p:.4f}, n = {n}")

    # 2. Forward-lag: TDI[t] → VIX[t+1] — CME causal prediction
    fwd_tdi = tdi_n50[:-1]
    fwd_vix = vix_n50[1:]
    r_fwd, p_fwd = stats.pearsonr(fwd_tdi, fwd_vix)
    print(f"Forward-lag r(TDI[t], VIX[t+1]) = {r_fwd:.4f}, p = {p_fwd:.4f}, n = {len(fwd_tdi)}")

    # 3. Reverse-lag: VIX[t] → TDI[t+1] — reverse causation test
    rev_vix = vix_n50[:-1]
    rev_tdi = tdi_n50[1:]
    r_rev, p_rev = stats.pearsonr(rev_vix, rev_tdi)
    print(f"Reverse-lag r(VIX[t], TDI[t+1]) = {r_rev:.4f}, p = {p_rev:.4f}, n = {len(rev_vix)}")

    # 4. Sensitivity: exclude 2022 Q4 (on n≥50 series, not raw series)
    mask_excl = [q != (2022, 4) for q in quarters_n50]
    tdi_excl = tdi_n50[mask_excl]
    vix_excl = vix_n50[mask_excl]
    r_ex, p_ex = stats.pearsonr(tdi_excl, vix_excl)
    print(f"Excl 2022Q4 r = {r_ex:.4f}, p = {p_ex:.6f}, n = {len(tdi_excl)}")

    # ── 7. Save CSV ──────────────────────────────────────────────────────────
    csv_path = Path("/Users/sanjaysubramania/cme_validation/empirical_tdi_results.csv")
    rows = []
    for (y, q), tdi, vix in zip(common_quarters, tdi_vals, vix_vals):
        rows.append({
            "year": y, "quarter": q,
            "label": f"{y}Q{q}",
            "TDI": round(tdi, 5),
            "VIX_avg": round(vix, 3),
            "n_institutions": tau_count_series.get((y, q), 0),
        })
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")

    # ── 8. Figures ───────────────────────────────────────────────────────────
    print("Generating figures ...")
    labels_n50 = [f"{y}Q{q}" for y, q in quarters_n50]
    _plot_results(labels_n50, list(tdi_n50), list(vix_n50), r, p, n)


def _plot_results(labels, tdi_vals, vix_vals, r, p, n):
    x = np.arange(len(labels))
    fig = plt.figure(figsize=(14, 10))
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.40, wspace=0.35)

    # ── Panel A: TDI time series ────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1b = ax1.twinx()
    l1, = ax1.plot(x, tdi_vals, "b-o", ms=4, lw=1.5, label="TDI (empirical)")
    l2, = ax1b.plot(x, vix_vals, "r-s", ms=3, lw=1.2, alpha=0.7, label="VIX (avg)")
    ax1.set_ylabel("Temporal Diversity Index", color="b")
    ax1b.set_ylabel("VIX (quarterly average)", color="r")
    ax1.tick_params(axis="y", colors="b")
    ax1b.tick_params(axis="y", colors="r")

    tick_step = max(1, len(labels) // 12)
    ax1.set_xticks(x[::tick_step])
    ax1.set_xticklabels(labels[::tick_step], rotation=45, ha="right", fontsize=8)
    ax1.set_title("Empirical TDI vs. VIX (2013–2024)", fontsize=12, fontweight="bold")
    lines = [l1, l2]
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper right", fontsize=9)

    # Shade crisis periods
    crisis_regions = [
        ("2020Q1", "2020Q2", "Covid-19", "salmon"),
        ("2022Q1", "2022Q4", "Rate hike cycle", "lightyellow"),
    ]
    for start_ql, end_ql, label_text, color in crisis_regions:
        if start_ql in labels and end_ql in labels:
            xs = labels.index(start_ql)
            xe = labels.index(end_ql)
            ax1.axvspan(xs, xe, alpha=0.25, color=color, label=label_text)

    # ── Panel B: Scatter TDI vs VIX ─────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.scatter(vix_vals, tdi_vals, c=x, cmap="viridis", s=30, alpha=0.8, zorder=3)
    m, b = np.polyfit(vix_vals, tdi_vals, 1)
    vx_line = np.linspace(min(vix_vals), max(vix_vals), 100)
    ax2.plot(vx_line, m * vx_line + b, "k--", lw=1.2, label=f"r={r:.3f}, p={p:.3f}")
    ax2.set_xlabel("VIX (quarterly average)")
    ax2.set_ylabel("TDI")
    ax2.set_title("TDI vs. VIX scatter", fontsize=10, fontweight="bold")
    ax2.legend(fontsize=9)

    # Colorbar for time
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(0, len(labels) - 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax2, fraction=0.04)
    cbar.set_label("Time (earlier → later)", fontsize=8)

    # ── Panel C: τ distribution for a low-VIX vs high-VIX quarter ──────────
    ax3 = fig.add_subplot(gs[1, 1])
    vix_arr = np.array(vix_vals)
    low_vix_idx  = int(np.argmin(vix_arr))
    high_vix_idx = int(np.argmax(vix_arr))

    ax3.text(0.5, 0.5,
             f"Low VIX: {labels[low_vix_idx]}\nTDI={tdi_vals[low_vix_idx]:.3f}\n\n"
             f"High VIX: {labels[high_vix_idx]}\nTDI={tdi_vals[high_vix_idx]:.3f}\n\n"
             f"Pearson r = {r:.3f}\np = {p:.4f}\nn = {n} quarters",
             transform=ax3.transAxes,
             ha="center", va="center", fontsize=10,
             bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.4))
    ax3.axis("off")
    ax3.set_title("Key statistics", fontsize=10, fontweight="bold")

    fig.suptitle(
        "Chronotypic Market Ecology — Empirical Validation\n"
        f"TDI computed from SEC 13-F-HR holdings ({n} quarters, top-{TOP_N_FILERS} institutions)",
        fontsize=11, fontweight="bold", y=0.99,
    )

    out_path = OUT_DIR / "empirical_tdi_validation.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to {out_path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
