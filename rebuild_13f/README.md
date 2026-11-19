# Full-universe 13F rebuild (Stage 0 of the pivot)

Replaces the top-150 EDGAR scrape (`edgar_cache/holdings_db.json`) with every 13F filer, using the SEC's free **Form 13F Data Sets** (structured quarterly files with share counts, 2013Q2 onward). This is step zero for every pivot idea in `docs/novelty-audit/IDEAS.md` (on branch `sumedh-agent/novelty-audit`): it answers the sampled-network critique of the overlap network and makes horizons share-based and unit-consistent.

## Run

```bash
export SEC_CONTACT_EMAIL="you@example.com"   # SEC requires a real contact; set your own
python rebuild_13f/download.py --list        # what the SEC currently offers
python rebuild_13f/download.py               # downloads to sec13f_cache/ (gitignored), resumable
python rebuild_13f/build_panel.py            # writes panel_13f/ (gitignored)
python rebuild_13f/test_build_panel.py       # 11 hand-worked checks on a synthetic data set
```

## What the builder does

| Rule | Why |
|---|---|
| VALUE in dollars by **filing date** (thousands before 2023-01-03, dollars after) | The SEC unit change created the 2022Q4 artefact in the current paper (issue #1) |
| Per-filing **implied-price check**: a filing whose median value/shares is about 1000x off the cross-sectional price is rescaled | Some filers kept reporting in thousands after the change (practitioner reports of a few percent of reports in 2026Q2; StoneX misreported 2022Q4 to 2025Q1; Barclays amended 2024) |
| Keep `SSHPRNAMTTYPE = SH`, drop option rows (`PUTCALL` set) | Share counts only; options are not holdings |
| 13F-HR and 13F-HR/A only; notices dropped | Notices carry no holdings |
| Per (CIK, period): latest original or RESTATEMENT is the base; later NEW HOLDINGS amendments add rows | Amendments are common and change positions |
| Turnover at one common price per CUSIP-period (median across all filers) | Price moves cannot create turnover (the drift problem) |
| Split-rebased variant (same rule as `price_adjusted_tdi.py`) | Splits look like trades in share counts |
| tau = 63 / turnover, clipped to [5, 2000]; zero turnover gives no tau, as in `price_adjusted_tdi.py` | Same horizon definition as the paper |

## Outputs (`panel_13f/`)

- `filings.parquet`: accession, cik, period, filing date, kind (original, restatement, new_holdings)
- `positions/<period>.parquet`: cik, period, cusip, shares, value_usd (one file per quarter)
- `stage/`: compact per-zip staging files (safe to delete after a build)
- `tau.parquet`: cik, period, turnover, tau, turnover_split, tau_split, n_positions, aum_usd
- `build_report.json`: counts at every step, so each rule's effect is visible

## Not yet done

- Column names checked against the real files (2026-11-19): all required columns present. One three-month file: 9,900 holdings filings, 3.68 million share rows, parsed in 3 s at 1.3 GB peak memory.
- Validate against the existing top-150 panel (`tau_by_inst_quarter.json`) for overlapping CIKs.
- Overlap network on the full universe, the variance decomposition (Stage 1a) and the pre-registered descriptive test (Stage 1b).
- Fund-level manager data for the Stage 2 shock design is not in 13F; needs N-PORT or CRSP mutual-fund data.
