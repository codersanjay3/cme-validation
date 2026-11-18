"""
causal_identification.py — Structural identification for the TDI→VIX causal claim.

Approach (standard macro-finance):
  1. VAR Granger causality: does TDI(t-1) predict VIX(t) after controlling for VIX(t-1)?
     Asymmetric result (TDI→VIX but not VIX→TDI) supports the causal direction.
  2. OLS with controls: TDI predicts VIX controlling for lagged VIX, lagged market return,
     and Baker-Bloom-Davis Economic Policy Uncertainty (EPU) index.
  3. Impulse response function from the VAR: VIX response to a one-sigma TDI shock.
  4. EPU instrument check: regress VIX on TDI, instrumenting TDI with EPU(t-1).
     EPU is driven by policy/political events largely independent of portfolio composition.

Data:
  - TDI/VIX: empirical_tdi_results.csv (45 quarters, 2013Q3–2024Q3)
  - EPU: Baker-Bloom-Davis US EPU index, monthly → quarterly (FRED: USEPUINDXM)
  - SPY returns: yfinance (quarterly market return control)
"""

import os
import csv, ssl, urllib.request, math
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
import yfinance as yf

ctx = ssl._create_unverified_context()

# ─── 1. Load TDI / VIX series ────────────────────────────────────────────────
rows = []
with open('/Users/sanjaysubramania/cme_validation/empirical_tdi_results.csv') as f:
    for row in csv.DictReader(f):
        rows.append({
            'label':   row['label'],
            'year':    int(row['year']),
            'quarter': int(row['quarter']),
            'TDI':     float(row['TDI']),
            'VIX':     float(row['VIX_avg']),
            'n':       int(row['n_institutions']),
        })

rows = [r for r in rows if r['n'] >= 50]  # same filter as main paper
rows.sort(key=lambda r: (r['year'], r['quarter']))
print(f"Loaded {len(rows)} quarters: {rows[0]['label']} – {rows[-1]['label']}")

tdi_series = np.array([r['TDI'] for r in rows])
vix_series = np.array([r['VIX'] for r in rows])
labels     = [r['label'] for r in rows]


# ─── 2. Stationarity check (ADF) ─────────────────────────────────────────────
def adf_report(name, series):
    result = adfuller(series, autolag='AIC')
    return f"{name}: ADF stat={result[0]:.3f}, p={result[1]:.3f} {'[stationary]' if result[1]<0.05 else '[non-stationary]'}"

print('\nStationarity:')
print(' ', adf_report('TDI', tdi_series))
print(' ', adf_report('VIX', vix_series))


# ─── 3. Granger causality tests ──────────────────────────────────────────────
print('\n--- Granger Causality ---')
df_gc = pd.DataFrame({'TDI': tdi_series, 'VIX': vix_series})

print('H0: TDI does NOT Granger-cause VIX:')
gc_tdi_vix = grangercausalitytests(df_gc[['VIX', 'TDI']], maxlag=2)
for lag in [1, 2]:
    f_stat = gc_tdi_vix[lag][0]['ssr_ftest'][0]
    p_val  = gc_tdi_vix[lag][0]['ssr_ftest'][1]
    print(f'  lag={lag}: F={f_stat:.3f}, p={p_val:.4f}  {"=> REJECT H0 (TDI Granger-causes VIX)" if p_val<0.1 else ""}')

print('H0: VIX does NOT Granger-cause TDI:')
gc_vix_tdi = grangercausalitytests(df_gc[['TDI', 'VIX']], maxlag=2)
for lag in [1, 2]:
    f_stat = gc_vix_tdi[lag][0]['ssr_ftest'][0]
    p_val  = gc_vix_tdi[lag][0]['ssr_ftest'][1]
    print(f'  lag={lag}: F={f_stat:.3f}, p={p_val:.4f}  {"=> REJECT H0 (VIX Granger-causes TDI)" if p_val<0.1 else ""}')


# ─── 4. VAR(p) with AIC selection ───────────────────────────────────────────
print('\n--- VAR model ---')
model = VAR(df_gc)
lag_order = model.select_order(maxlags=4)
p_aic = lag_order.aic
print(f'AIC-selected lag order: p={p_aic}')

res = model.fit(p_aic)
print(res.summary())


# ─── 5. Impulse Response Function ───────────────────────────────────────────
irf = res.irf(10)
# Extract VIX response to TDI shock (orthogonalized, TDI ordered first)
# IRF shape: (periods, n_vars, n_vars)
vix_to_tdi_shock = irf.orth_irfs[:, 1, 0]  # VIX (col 1) to TDI shock (col 0)
print('\nImpulse response of VIX to 1-sigma TDI shock (quarters 0-6):')
for i, v in enumerate(vix_to_tdi_shock[:7]):
    print(f'  t+{i}: {v:+.3f}')


# ─── 6. OLS with controls ────────────────────────────────────────────────────
print('\n--- OLS with controls ---')

# Fetch SPY quarterly returns as macro control
spy = yf.download('SPY', start='2012-01-01', end='2025-06-01',
                  interval='3mo', progress=False, auto_adjust=True)
spy_close = spy['Close'].iloc[:, 0] if hasattr(spy['Close'].columns, '__iter__') else spy['Close']
spy_ret = spy_close.pct_change().dropna()
spy_qtr = {}
for idx, val in spy_ret.items():
    dt = idx.date() if hasattr(idx, 'date') else None
    if dt:
        q_str = f"{dt.year}Q{(dt.month-1)//3+1}"
        spy_qtr[q_str] = float(val) * 100

# Fetch EPU (Baker-Bloom-Davis) from FRED
print('Fetching EPU from FRED...')
try:
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=USEPUINDXM'
    req = urllib.request.Request(url, headers={'User-Agent': 'research ' + os.environ.get('SEC_CONTACT_EMAIL', 'set-SEC_CONTACT_EMAIL')})
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        epu_text = r.read().decode()
    epu_rows = [line.split(',') for line in epu_text.strip().split('\n')[1:]]
    epu_monthly = {row[0][:7]: float(row[1]) for row in epu_rows if row[1].strip() != '.'}
    # Quarterly average
    epu_qtr = defaultdict(list)
    for ym, val in epu_monthly.items():
        year, month = int(ym[:4]), int(ym[5:7])
        q_str = f"{year}Q{(month-1)//3+1}"
        epu_qtr[q_str].append(val)
    epu_qmean = {q: np.mean(v) for q, v in epu_qtr.items()}
    print(f'  EPU loaded: {len(epu_qmean)} quarters')
except Exception as e:
    print(f'  EPU fetch failed: {e}')
    epu_qmean = {}

# Build regression dataset
X_rows = []
for i, r in enumerate(rows):
    if i == 0:
        continue  # need lagged values
    lag_row = rows[i - 1]
    q = r['label']
    epu = epu_qmean.get(q)
    spy_r = spy_qtr.get(q)
    if epu is None or spy_r is None:
        continue
    X_rows.append({
        'label':    q,
        'VIX':      r['VIX'],
        'TDI':      r['TDI'],
        'VIX_lag1': lag_row['VIX'],
        'TDI_lag1': lag_row['TDI'],
        'EPU':      epu,
        'SPY_ret':  spy_r,
    })

print(f'  {len(X_rows)} quarters with all controls')

if len(X_rows) >= 15:
    import numpy as np
    Y = np.array([r['VIX'] for r in X_rows])
    # Model 1: VIX ~ TDI_lag1 + VIX_lag1 (controls for persistence)
    X1 = np.column_stack([
        np.ones(len(X_rows)),
        [r['TDI_lag1'] for r in X_rows],
        [r['VIX_lag1'] for r in X_rows],
    ])
    b1, res1, _, _ = np.linalg.lstsq(X1, Y, rcond=None)
    yhat1 = X1 @ b1
    resid1 = Y - yhat1
    n, k = len(Y), X1.shape[1]
    s2 = resid1 @ resid1 / (n - k)
    cov = s2 * np.linalg.inv(X1.T @ X1)
    se = np.sqrt(np.diag(cov))
    t_tdi = b1[1] / se[1]
    p_tdi = 2 * (1 - stats.t.cdf(abs(t_tdi), df=n-k))
    r2 = 1 - np.var(resid1) / np.var(Y)
    print(f'\nModel 1: VIX ~ TDI(t-1) + VIX(t-1)')
    print(f'  TDI(t-1) coeff = {b1[1]:.3f}  SE={se[1]:.3f}  t={t_tdi:.3f}  p={p_tdi:.4f}')
    print(f'  VIX(t-1) coeff = {b1[2]:.3f}  SE={se[2]:.3f}')
    print(f'  R² = {r2:.3f}  (n={n})')

    # Model 2: add EPU and SPY return
    X2 = np.column_stack([
        np.ones(len(X_rows)),
        [r['TDI_lag1'] for r in X_rows],
        [r['VIX_lag1'] for r in X_rows],
        [r['EPU'] for r in X_rows],
        [r['SPY_ret'] for r in X_rows],
    ])
    b2, res2, _, _ = np.linalg.lstsq(X2, Y, rcond=None)
    yhat2 = X2 @ b2
    resid2 = Y - yhat2
    n, k2 = len(Y), X2.shape[1]
    s2b = resid2 @ resid2 / (n - k2)
    cov2 = s2b * np.linalg.inv(X2.T @ X2)
    se2 = np.sqrt(np.diag(cov2))
    t_tdi2 = b2[1] / se2[1]
    p_tdi2 = 2 * (1 - stats.t.cdf(abs(t_tdi2), df=n-k2))
    r2b = 1 - np.var(resid2) / np.var(Y)
    print(f'\nModel 2: VIX ~ TDI(t-1) + VIX(t-1) + EPU + SPY_return')
    print(f'  TDI(t-1) coeff = {b2[1]:.3f}  SE={se2[1]:.3f}  t={t_tdi2:.3f}  p={p_tdi2:.4f}')
    print(f'  VIX(t-1) coeff = {b2[2]:.3f}  SE={se2[2]:.3f}')
    print(f'  EPU coeff      = {b2[3]:.3f}  SE={se2[3]:.3f}')
    print(f'  SPY_ret coeff  = {b2[4]:.3f}  SE={se2[4]:.3f}')
    print(f'  R² = {r2b:.3f}  (n={n})')


# ─── 7. IV / 2SLS with EPU(t-1) as instrument for TDI ───────────────────────
print('\n--- 2SLS: TDI instrumented by EPU(t-1) ---')

iv_rows = []
for i, r in enumerate(rows):
    if i < 2:
        continue
    lag1 = rows[i - 1]
    lag2 = rows[i - 2]
    q = r['label']
    epu_lag1 = epu_qmean.get(lag1['label'])
    epu_lag2 = epu_qmean.get(lag2['label'])
    spy_r = spy_qtr.get(q)
    if None in (epu_lag1, epu_lag2, spy_r):
        continue
    iv_rows.append({
        'VIX':      r['VIX'],
        'TDI':      r['TDI'],
        'VIX_lag1': lag1['VIX'],
        'TDI_lag1': lag1['TDI'],
        'EPU_lag1': epu_lag1,
        'EPU_lag2': epu_lag2,
        'SPY_ret':  spy_r,
    })

if len(iv_rows) >= 15:
    Y_iv = np.array([r['VIX'] for r in iv_rows])
    D    = np.array([r['TDI'] for r in iv_rows])     # endogenous: TDI(t)
    Z    = np.array([r['EPU_lag1'] for r in iv_rows]) # instrument: EPU(t-1)
    X_ctrl = np.column_stack([
        np.ones(len(iv_rows)),
        [r['VIX_lag1'] for r in iv_rows],
    ])

    # First stage: TDI ~ EPU(t-1) + VIX(t-1)
    X_fs = np.column_stack([X_ctrl, Z])
    b_fs, _, _, _ = np.linalg.lstsq(X_fs, D, rcond=None)
    D_hat = X_fs @ b_fs
    resid_fs = D - D_hat
    n_iv = len(iv_rows)
    s2_fs = resid_fs @ resid_fs / (n_iv - X_fs.shape[1])
    cov_fs = s2_fs * np.linalg.inv(X_fs.T @ X_fs)
    t_z = b_fs[2] / np.sqrt(cov_fs[2, 2])
    p_z = 2 * (1 - stats.t.cdf(abs(t_z), df=n_iv - X_fs.shape[1]))
    F_first = t_z ** 2  # approximate F with single instrument
    print(f'First stage: EPU(t-1) → TDI(t)')
    print(f'  coeff = {b_fs[2]:.4f}  t = {t_z:.3f}  p = {p_z:.4f}')
    print(f'  F-stat ≈ {F_first:.2f}  {"[STRONG instrument F>10]" if F_first>10 else "[weak instrument]"}')

    # Second stage: VIX ~ D_hat + VIX(t-1)
    X_ss = np.column_stack([X_ctrl, D_hat])
    b_ss, _, _, _ = np.linalg.lstsq(X_ss, Y_iv, rcond=None)
    yhat_ss = X_ss @ b_ss
    resid_ss = Y_iv - yhat_ss
    s2_ss = resid_ss @ resid_ss / (n_iv - X_ss.shape[1])
    cov_ss = s2_ss * np.linalg.inv(X_ss.T @ X_ss)
    t_2sls = b_ss[2] / np.sqrt(cov_ss[2, 2])
    p_2sls = 2 * (1 - stats.t.cdf(abs(t_2sls), df=n_iv - X_ss.shape[1]))
    r2_iv = 1 - np.var(resid_ss) / np.var(Y_iv)
    print(f'Second stage: VIX ~ TDI_hat + VIX(t-1)')
    print(f'  TDI(2SLS) coeff = {b_ss[2]:.3f}  t = {t_2sls:.3f}  p = {p_2sls:.4f}')
    print(f'  R² = {r2_iv:.3f}  (n={n_iv})')

    # Wu-Hausman endogeneity test
    # Augment OLS with first-stage residuals; significant residual coeff → endogeneity
    X_wh = np.column_stack([X_ctrl, D, resid_fs])
    b_wh, _, _, _ = np.linalg.lstsq(X_wh, Y_iv, rcond=None)
    yhat_wh = X_wh @ b_wh
    resid_wh = Y_iv - yhat_wh
    s2_wh = resid_wh @ resid_wh / (n_iv - X_wh.shape[1])
    cov_wh = s2_wh * np.linalg.inv(X_wh.T @ X_wh)
    t_wh = b_wh[3] / np.sqrt(cov_wh[3, 3])
    p_wh = 2 * (1 - stats.t.cdf(abs(t_wh), df=n_iv - X_wh.shape[1]))
    print(f'Wu-Hausman endogeneity test: t={t_wh:.3f}  p={p_wh:.4f}')
    if p_wh > 0.1:
        print('  => TDI not significantly endogenous; OLS is consistent')
    else:
        print('  => TDI is endogenous; 2SLS preferred')

print('\n--- Summary ---')
print('Granger causality: does lagged TDI predict VIX after controlling for lagged VIX?')
print('OLS with controls: is the TDI coefficient robust to EPU and market returns?')
print('2SLS: using EPU(t-1) as IV for TDI to address potential reverse causality.')
