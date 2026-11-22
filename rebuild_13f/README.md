# Full-universe 13F rebuild (Stage 0 of the pivot)

Replaces the top-150 EDGAR scrape (`edgar_cache/holdings_db.json`) with every 13F filer, using the SEC's free **Form 13F Data Sets** (structured quarterly files with share counts, 2013Q2 onward). This is step zero for every pivot idea in `docs/novelty-audit/IDEAS.md` (on branch `sumedh-agent/novelty-audit`): it answers the sampled-network critique of the overlap network and makes horizons share-based and unit-consistent.

## Run

```bash
export SEC_CONTACT_EMAIL="you@example.com"   # SEC requires a real contact; set your own
python rebuild_13f/download.py --list        # what the SEC currently offers
python rebuild_13f/download.py               # downloads to sec13f_cache/ (gitignored), resumable
python rebuild_13f/build_panel.py            # writes panel_13f/ (gitignored)
python rebuild_13f/build_panel.py --tau-only # recompute tau.parquet from existing positions/ only
python rebuild_13f/test_build_panel.py       # 13 hand-worked checks on a synthetic data set
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
| Split-rebased variant: rebase by k only if the share ratio is within 2% of k AND the common price ratio is within 10% of 1/k (price check added 2026-11-21, bead cme-d0m) | Splits look like trades in share counts; without the price check, selling exactly half or doubling a position looked like a split |
| tau = 63 / turnover, clipped to [5, 2000]; zero turnover gives no tau, as in `price_adjusted_tdi.py` | Same horizon definition as the paper |

## Outputs (`panel_13f/`)

- `filings.parquet`: accession, cik, period, filing date, kind (original, restatement, new_holdings)
- `positions/<period>.parquet`: cik, period, cusip, shares, value_usd (one file per quarter)
- `stage/`: compact per-zip staging files (safe to delete after a build)
- `tau.parquet`: cik, period, turnover, tau, turnover_split, tau_split, n_positions, aum_usd
- `build_report.json`: counts at every step, so each rule's effect is visible

## First full build (2026-11-19)

- 54 SEC data sets (3.0 GB), 322,015 holdings filings, 13,124 institutions, 76 million positions, 287,197 institution-quarter horizons (median tau 647 trading days), periods 2013Q1 to 2026Q2. Build time about 3 minutes, 2.4 GB peak memory.
- Unit check: 8,754 filings still in thousands after 2023-01-03 rescaled up; 2,723 already in dollars before it rescaled down (about 3.6% of filings). 940 filings with report periods before 2013 (filer date errors) dropped.
- Validation against `tau_by_inst_quarter.json` (series x): 99.8% of old institution-quarters found; rank correlation 0.934 (0.926 within quarter); median absolute log difference 0.009; 92% within a factor of 1.5; worst quarter 2022Q4 (0.83), the unit-break quarter, where the new panel is meant to differ. Details: `results/validate_rebuild_vs_top150.json`, `results/rebuild_13f_build_report.json`.
- Shared outputs: GitHub release `data-rebuild-v1` (tau.parquet, filings.parquet, build report, download manifest, SHA256SUMS). Positions (755 MB) are not uploaded; rebuild them from the SEC files in about 3 minutes.

## Not yet done

- Column names checked against the real files (2026-11-19): all required columns present. One three-month file: 9,900 holdings filings, 3.68 million share rows, parsed in 3 s at 1.3 GB peak memory.
- Overlap network on the full universe, the variance decomposition (Stage 1a) and the pre-registered descriptive test (Stage 1b).
- Fund-level manager data for the Stage 2 shock design is not in 13F; needs N-PORT or CRSP mutual-fund data.
