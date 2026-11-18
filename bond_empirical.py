"""
Empirical bond market TDI analysis using SEC N-PORT filings.

Each N-PORT filing is one bond fund series. We compute the weighted average
maturity (WAM) of each fund as a proxy for tau (holding horizon). TDI is
the Shannon entropy of the log(tau) distribution across fund series within
a quarter, analogous to the equity TDI from 13F filings in the main paper.
We then correlate quarterly TDI with ^MOVE bond volatility.
"""

import os
import ssl, urllib.request, json, re, math
from datetime import datetime, date
from collections import defaultdict
import yfinance as yf
import numpy as np
from scipy import stats

ctx = ssl._create_unverified_context()
HEADERS = {'User-Agent': 'research ' + os.environ.get('SEC_CONTACT_EMAIL', 'set-SEC_CONTACT_EMAIL')}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode('utf-8', errors='replace')


def get_filing_dates(cik, max_filings=200):
    """Return list of (filing_date_str, accession_number) for N-PORT-P filings."""
    url = f'https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json'
    data = json.loads(fetch(url))
    filings = data['filings']['recent']
    out = []
    for form, accn, dt in zip(filings['form'], filings['accessionNumber'], filings['filingDate']):
        if form == 'NPORT-P':
            out.append((dt, accn))
        if len(out) >= max_filings:
            break
    return out


def parse_wam_from_xml(xml_text, filing_date_str):
    """
    Compute weighted average maturity (WAM) in years from N-PORT XML.
    Uses <pctVal> and <maturityDt> for debt securities.
    Returns WAM in years or None if insufficient debt holdings.
    """
    filing_dt = datetime.strptime(filing_date_str, '%Y-%m-%d').date()

    # Extract (pct_val, maturity_date) pairs
    weighted_days = 0.0
    total_weight = 0.0

    # Find all invstOrSec blocks
    for sec_match in re.finditer(r'<invstOrSec>(.*?)</invstOrSec>', xml_text, re.DOTALL):
        sec = sec_match.group(1)
        pct_match = re.search(r'<pctVal>([^<]+)</pctVal>', sec)
        mat_match = re.search(r'<maturityDt>([^<]+)</maturityDt>', sec)
        if not pct_match or not mat_match:
            continue
        try:
            pct = float(pct_match.group(1))
            mat_dt = datetime.strptime(mat_match.group(1).strip(), '%Y-%m-%d').date()
            days = (mat_dt - filing_dt).days
            if days <= 0 or days > 365 * 50:  # sanity: 1d to 50yr
                continue
            weighted_days += pct * days
            total_weight += pct
        except (ValueError, OverflowError):
            continue

    if total_weight < 10.0:  # need at least ~10% in debt securities
        return None
    return (weighted_days / total_weight) / 365.25  # years


def get_all_accessions_for_date(cik, target_date, all_filings):
    """Return all accession numbers filed on target_date for this CIK."""
    return [a for d, a in all_filings if d == target_date]


def fetch_xml(cik, accn):
    accn_clean = accn.replace('-', '')
    url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn_clean}/primary_doc.xml'
    try:
        return fetch(url, timeout=45)
    except Exception as e:
        print(f'    XML fetch failed for {accn}: {e}')
        return None


def compute_tdi(wams_years, n_bins=16, tau_min_yr=0.1, tau_max_yr=30.0):
    """
    Shannon entropy of log(tau) distribution, matching main paper's TDI formula.
    tau in trading days: tau_td = wam_years * 252.
    Uses 16 bins over log space matching the 1-2000 trading-day range.
    """
    tau_tds = [w * 252 for w in wams_years]
    log_taus = [math.log(t) for t in tau_tds if t > 0]
    if len(log_taus) < 3:
        return None
    log_min = math.log(tau_min_yr * 252)
    log_max = math.log(tau_max_yr * 252)
    bins = np.linspace(log_min, log_max, n_bins + 1)
    counts, _ = np.histogram(log_taus, bins=bins)
    total = counts.sum()
    if total == 0:
        return None
    probs = counts / total
    entropy = -sum(p * math.log(p) for p in probs if p > 0)
    return entropy


# ─── Step 1: collect quarterly filing dates ───────────────────────────────────
BOND_CIKS = {
    'PIMCO':    810893,
    'Vanguard': 106444,
    'BlackRock': 276463,
}

print('Fetching filing lists from EDGAR...')
all_filings_by_cik = {}
for name, cik in BOND_CIKS.items():
    filings = get_filing_dates(cik, max_filings=500)
    all_filings_by_cik[cik] = filings
    dates = sorted({d for d, _ in filings}, reverse=True)
    print(f'  {name}: {len(filings)} N-PORT filings, {len(dates)} unique dates: {dates[:5]}')

# Identify quarterly dates: one per ~3-month window
# Collect all unique dates across all funds, then group by quarter
all_dates = sorted(
    {d for filings in all_filings_by_cik.values() for d, _ in filings},
    reverse=True
)

# Keep one date per calendar quarter (pick latest date in each quarter)
quarters_seen = set()
quarterly_dates = []
for d in all_dates:
    dt = datetime.strptime(d, '%Y-%m-%d').date()
    q = (dt.year, (dt.month - 1) // 3)
    if q not in quarters_seen:
        quarters_seen.add(q)
        quarterly_dates.append(d)

quarterly_dates = sorted(quarterly_dates)[-12:]  # last 12 quarters max
print(f'\nUsing {len(quarterly_dates)} quarterly dates: {quarterly_dates}')


# ─── Step 2: compute per-quarter TDI ─────────────────────────────────────────
print('\nFetching N-PORT XMLs and computing WAMs...')
quarterly_tdi = {}

for qdate in quarterly_dates:
    print(f'\n  Quarter ending {qdate}:')
    wams = []

    for name, cik in BOND_CIKS.items():
        filings = all_filings_by_cik[cik]

        # For this quarter, find the closest filing date <= qdate
        cik_dates = sorted({d for d, _ in filings if d <= qdate}, reverse=True)
        if not cik_dates:
            continue
        best_date = cik_dates[0]

        # Get all accessions filed on that date (= all fund series)
        accessions = [a for d, a in filings if d == best_date][:8]  # cap at 8 per family
        print(f'    {name} ({best_date}): {len(accessions)} series')

        for accn in accessions:
            xml = fetch_xml(cik, accn)
            if xml is None:
                continue
            wam = parse_wam_from_xml(xml, best_date)
            if wam is not None and 0.1 < wam < 35:
                wams.append(wam)

    print(f'    => {len(wams)} fund WAMs: {[round(w,2) for w in wams]}')

    if len(wams) >= 4:
        tdi = compute_tdi(wams)
        if tdi is not None:
            quarterly_tdi[qdate] = tdi
            print(f'    => TDI = {tdi:.4f}')


# ─── Step 3: fetch ^MOVE quarterly volatility ─────────────────────────────────
print('\nFetching ^MOVE bond volatility index...')
move = yf.download('^MOVE', start='2022-01-01', end='2027-01-01',
                   interval='1mo', progress=False, auto_adjust=True)

# Compute quarterly mean of ^MOVE (it IS a vol index, not price, so mean is the vol)
move_close = move['Close']
if hasattr(move_close.columns, '__iter__'):
    move_close = move_close.iloc[:, 0]  # drop Ticker level if MultiIndex
move_monthly = move_close.dropna()
move_qtr = {}
for idx_dt, val in move_monthly.items():
    dt = idx_dt.date() if hasattr(idx_dt, 'date') else datetime.strptime(str(idx_dt)[:10], '%Y-%m-%d').date()
    q = (dt.year, (dt.month - 1) // 3)
    move_qtr.setdefault(q, []).append(float(val))

move_qtr_mean = {q: np.mean(vals) for q, vals in move_qtr.items()}

# Also try AGG realized vol as backup
print('Fetching AGG (bond ETF) for realized vol...')
agg = yf.download('AGG', start='2022-01-01', end='2027-01-01',
                  interval='1mo', progress=False, auto_adjust=True)
agg_close = agg['Close']
if hasattr(agg_close.columns, '__iter__'):
    agg_close = agg_close.iloc[:, 0]
agg_ret = agg_close.pct_change().dropna()
agg_qtr_std = {}
for idx_dt, val in agg_ret.items():
    if hasattr(idx_dt, 'date'):
        dt = idx_dt.date()
    elif isinstance(idx_dt, str):
        dt = datetime.strptime(idx_dt[:10], '%Y-%m-%d').date()
    else:
        dt = idx_dt
    q = (dt.year, (dt.month - 1) // 3)
    agg_qtr_std.setdefault(q, []).append(float(val))

agg_qtr_std = {q: np.std(vals) * math.sqrt(12) * 100 for q, vals in agg_qtr_std.items()
               if len(vals) >= 2}


# ─── Step 4: merge and correlate ─────────────────────────────────────────────
print('\n--- Results ---')
tdi_vals, move_vals, agg_vals = [], [], []
quarters_used = []

for qdate in sorted(quarterly_tdi.keys()):
    tdi = quarterly_tdi[qdate]
    dt = datetime.strptime(qdate, '%Y-%m-%d').date()
    q = (dt.year, (dt.month - 1) // 3)

    move_v = move_qtr_mean.get(q)
    agg_v = agg_qtr_std.get(q)

    if move_v is not None:
        tdi_vals.append(tdi)
        move_vals.append(move_v)
        quarters_used.append(qdate)
    if agg_v is not None and len(agg_vals) == len(tdi_vals) - 1:
        agg_vals.append(agg_v)

print(f'\nQuarters with both TDI and ^MOVE: {len(tdi_vals)}')
if len(tdi_vals) < 4:
    print('WARNING: too few matched quarters for reliable correlation')

for qd, t, m in zip(quarters_used, tdi_vals, move_vals):
    print(f'  {qd}  TDI={t:.4f}  ^MOVE={m:.1f}')

if len(tdi_vals) >= 4:
    r_move, p_move = stats.pearsonr(tdi_vals, move_vals)
    print(f'\nr(TDI_bond, ^MOVE) = {r_move:.3f}  p = {p_move:.4f}  (n={len(tdi_vals)})')
    if p_move < 0.05:
        direction = 'negative' if r_move < 0 else 'positive'
        print(f'  => Significant {direction} correlation: higher bond TDI ~ '
              f'{"lower" if r_move < 0 else "higher"} bond volatility')
    else:
        print(f'  => Not significant at 0.05 level')

if len(agg_vals) >= 4:
    r_agg, p_agg = stats.pearsonr(tdi_vals[:len(agg_vals)], agg_vals)
    print(f'\nr(TDI_bond, AGG_vol) = {r_agg:.3f}  p = {p_agg:.4f}  (n={len(agg_vals)})')

print('\n--- Summary ---')
print('Bond market temporal diversity (TDI) estimated from N-PORT fund WAMs.')
print('Tau proxy = weighted average maturity (years) * 252 trading days.')
print(f'Fund families: PIMCO (CIK 810893), Vanguard (CIK 106444), BlackRock (CIK 276463).')
