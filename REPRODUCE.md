# Reproduction Guide — Chronotypic Market Ecology

Subramanian & Seetharaman (2026). Tested on Python 3.11+, macOS/Linux.

## Setup

```bash
pip install -r requirements.txt
cd cme_validation/
```

## Reproducing all paper figures (Fig 1–8)

```bash
python3 cme_canonical.py --figures
# All PNGs saved to figures/
```

Expected terminal output (abridged):
```
Saved fig1a.png  ∆TDI(κ_h=0)=-0.150  ∆TDI(κ_h=6)=-0.114
Saved fig2a.png  vol reduction 1.29×
Saved fig2b.png  ratio=0.776  t=15.10
Saved fig5.png   TMFI ratio at κ_h=6: 14.3×
Saved fig6b.png  (Temporal Liquidity vs κ_h)
```

## Key quantitative results

| Result | Script | Expected output |
|--------|--------|----------------|
| Mean TDI = 2.36 | `python3 cme_canonical.py` | `mean TDI = 2.3990` |
| Vol suppression 1.29× (t=15.1) | `python3 cme_canonical.py` | `vol reduction 1.29×  t=15.10` |
| TMFI ratio 14.28× | `python3 cme_canonical.py` | `TMFI ratio at κ_h=6: 14.3×` |
| TL peak κh = 3.0 | `python3 cme_canonical.py` | `TL peak at κ_h = 3.00` |
| ∆TDI at κh=3: −0.114 | `python3 cme_canonical.py` | `κ_h=3.0: ... ∆TDI=-0.107` |

## Robustness checks (n = 160, 320)

```bash
python3 robustness_n.py
```

Expected output:
```
  80   0.6560   1.315×   11.43   2.3845
 160   0.6294   1.302×    5.62   2.4263
 320   0.6167   1.338×    3.09   2.4599
```

## Empirical validation (SEC 13-F)

```bash
python3 empirical_tdi.py
# Requires internet access to download EDGAR filings
# Expected: r=-0.526, p=0.0002, n=45
```

## Random seeds

All stochastic results use `numpy` seeds 0–29 (30 seeds) unless otherwise noted.
The TL sweep (Fig 8) uses 50 seeds (0–49).
Set `numpy.random.seed(s)` before each `CMESimulation()` call for exact replication.

## File index

| File | Purpose |
|------|---------|
| `cme_canonical.py` | Canonical simulation — all paper figures and statistics |
| `robustness_n.py` | n=160/320 robustness checks (§6 Limitations) |
| `empirical_tdi.py` | EDGAR 13-F empirical pipeline (§6.2) |
| `tl_sweep_v2.py` | Extended TL sweep (50 seeds) |
| `fix_e5.py` | Concentration parameter sensitivity (Fig 4) |
| `figures/` | All generated PNG figures |

## Added analyses (Oct 2026)

| File | Purpose | Output |
|------|---------|--------|
| `kappa_hac_tests.py` | Newey-West at several lags, lag-selection rules, block bootstrap, within-quarter permutation test for kappa-hat | `kappa_hac_results.json` |
| `price_adjusted_tdi.py` | TDI from value-weight vs share-based turnover (splits rebased); VIX correlation and Granger tests | `price_adjusted_tdi_results.csv`, `tau_by_inst_quarter.json` |
| `make_drift_figure.py` | Price-drift figure | `figures/drift_check.png` |
| `bond_discover.py`, `bond_by_type.py` | Vanguard bond funds by credit type, par-based behavioural tau vs MOVE | `bond_by_type_results.json` |
| `map_cusips.py`, `stock_prices.py` | CUSIP to ticker (OpenFIGI), daily prices (Yahoo Finance), quarterly outcomes | `cusip_ticker.json`, `stock_quarter_outcomes.csv` |
| `stock_level_test.py` | Holder-horizon dispersion vs next-quarter volatility (Fama-MacBeth, fixed effects, placebo) | `stock_level_results.json` |
| `worked_example.py` | Prints two-institution worked example for slides | stdout |

Order: `empirical_tdi.py` (holdings cache) -> `price_adjusted_tdi.py` -> `map_cusips.py` -> `stock_prices.py` -> `stock_level_test.py`.
Compile the paper locally with `tectonic cme_frl_submission.tex`.
