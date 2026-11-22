# DECISIONS: the project's shared memory

Append-only. Newest entries at the bottom. Never edit or delete an old entry; add a new one that corrects it.

Entry template:

```
## YYYY-MM-DD <agent-name>: <one-line title>
- Changed: files and scripts
- Numbers: name, old value, new value, script and seed
- Why:
- Open: what is unresolved, and who should check
- Beads/issues: ids
```

---

## 2026-11-18 sanjay-agent: baseline state when the repo was created

Where the project stands, so no agent has to rediscover it.

**What holds up**
- Clustering assumption: investors with similar horizons hold more similar portfolios. Mean kappa-hat 0.158, positive in all 50 quarters. Newey-West t = 19.0 at 3 lags, 16.3 at 8 lags, effective sample about 24. Block bootstrap range 0.145 to 0.175. Permutation test significant at 5% in 48 of 50 quarters (fails 2013Q3, 2013Q4; at 1% also fails 2016Q4).
- Simulation: more clustering lowers simulated volatility by a factor of 1.31 and belief fragmentation by 14.25, held in a 30-seed replication.
- Stock-level test (survivors only, about 60% of securities matched to tickers): similar-horizon owners go with slightly higher next-quarter volatility. Stock and quarter fixed effects, share-based horizons: -0.0106 (t = -2.42, p = 0.016). Weight-based: -0.0047, not significant. Effect is about 1% of a standard deviation.

**What was corrected**
1. The "17 lags" correction was never computed. Real Newey-West now reported.
2. "Significant at p < 0.001 in every quarter" became 48 of 50 under a permutation test.
3. Horizon diversity versus VIX (r = -0.53 to -0.59) is mostly price drift. Share-based turnover gives r about -0.06. Reported as a measurement artifact.
4. The Granger result runs opposite to the model and does not reproduce on the rebuilt series. Marked suggestive.
5. Temporal liquidity versus VIX is mostly mechanical, since volatility is inside the measure. Sample is 45 quarters, not 36.
6. MOVE is a published ICE Bank of America index, not ours.
7. The claim that compressing horizons raises simulated volatility was unsupported. Properly run, volatility falls.
8. Uniform-mode bound derived as lambda n beta / pbar, about 0.0013.
9. Temporal liquidity peak at moderate clustering is not statistically reliable.
10. Closest related work (Cella, Ellul, Giannetti, RFS 2013) was missing and is now cited.

**Open items**
- The rebuilt horizon-diversity series correlates only 0.50 with the original paper series (2022Q4: original 1.02, rebuilt 1.77). Cause not found. Needs an independent check by someone who did not build it.
- Model decision: option A (horizon-dependent stabiliser), B (horizon-dependent liquidity), or C (keep the model and report the tension). Professor Chalmers's view requested.
- WRDS/CRSP access requested, to remove survivorship bias and ticker-matching loss.
- Scripts need uploading to Zenodo (the paper's data-availability statement claims they are included).
- Bond analysis is descriptive only (7 Vanguard funds, 27 quarters each).

## 2026-11-18 sanjay-agent: repo made public, everything consolidated

- Changed: repo is public. Added `chronotypic_market_ecology/` (earlier gamma-sweep project), `docs/meetings`, `docs/decks`, `docs/archive`, `APIS.md`, `DATA.md`, `ONBOARDING.md`. `requirements.txt` now includes requests, statsmodels, yfinance.
- SEC User-Agent contact is now read from the `SEC_CONTACT_EMAIL` env var in five scripts (was hardcoded). Set it before running any EDGAR script.
- Data (edgar_cache, bond_cache, stock_prices.pkl) is in GitHub Release `data-v1`, not in git.
- Numbers: none changed.
- Open: scripts were not re-run after the env-var change; the earlier open items above are unchanged. Sumedh (`sumedhgodcoder`) has write access.

## 2026-11-19 sumedh-agent: full-universe 13F rebuild code (Stage 0)
- Changed: new `rebuild_13f/` (download.py, build_panel.py, test_build_panel.py, README.md); `.gitignore` adds `sec13f_cache/` and `panel_13f/`; `requirements.txt` adds pyarrow. No existing script edited.
- What it does: downloads the SEC Form 13F Data Sets (all filers, share counts, 2013Q2 onward) and builds a share-based, unit-consistent panel: VALUE converted to dollars by filing date (thousands before 2023-01-03), share rows only, options dropped, notices dropped, restatements replace and new-holdings amendments add, turnover at one common price per CUSIP-period, split-rebased variant, tau = 63/turnover clipped to [5, 2000].
- Numbers: none. Verified on a hand-built fixture (10 of 10 checks pass, including the unit fix, amendment handling and split rebase).
- Why: Stage 0 for every pivot idea in the novelty audit (branch sumedh-agent/novelty-audit); answers the sampled-network critique and the 2022Q4 unit artefact.
- Open: real download needs each person's own `SEC_CONTACT_EMAIL`; then validate against the top-150 panel and confirm SEC column names. Stage 2 manager shocks need fund-level data (N-PORT or CRSP MF), not in 13F.
- Beads/issues: cme-x59 (pivot), cme-csl (rebuild).

## 2026-11-19 sumedh-agent: 13F rebuild adds a per-filing unit check
- Changed: `rebuild_13f/build_panel.py` gains `to_dollars()`: after the filing-date rule, each filing's median implied price (value/shares) is compared with the cross-sectional median for the same CUSIP-period (CUSIPs with at least 3 holders); filings near 1/1000 or 1000 are rescaled. Fixture extended (filer 5 still in thousands after the change); 11 of 11 checks pass.
- Numbers: none.
- Why: follow-up literature search found the filing-date rule is not enough. A practitioner analysis reports a few percent of 2026Q2 holdings reports still in thousands; StoneX disclosed it misreported from 2022Q4 to 2025Q1; Barclays amended a 2024 filing to fix units.
- Open: the same check should be considered for any existing script that reads raw 13F values (empirical_tdi.py, price_adjusted_tdi.py); real-data run still waits on SEC_CONTACT_EMAIL.
- Beads/issues: cme-csl, #1, #4.

## 2026-11-19 sumedh-agent: full-universe 13F panel built and validated
- Changed: `rebuild_13f/build_panel.py` streams per zip and per quarter, stores shares as floats, drops report periods before 2013Q1 (940 filer date errors) and clears stale outputs; new `rebuild_13f/validate_vs_top150.py`; `results/rebuild_13f_build_report.json`, `results/validate_rebuild_vs_top150.json`. Release `data-rebuild-v1` holds tau.parquet and filings.parquet.
- Numbers (no paper number changed): 322,015 holdings filings, 13,124 institutions, 287,197 institution-quarter horizons, 2013Q1 to 2026Q2; about 3,300 filers per quarter in 2013 rising to about 8,600 in 2026 (top-150 panel: about 133). Unit check rescaled 8,754 filings up and 2,723 down. Against the top-150 share-based horizons: 99.8% coverage, rank correlation 0.934, median absolute log difference 0.009; 2022Q4 agrees least (0.83), as expected from the unit fix.
- Why: Stage 0 of the pivot; answers the sampled-network critique; makes every horizon share-based and unit-consistent.
- Open: rerun the stock-level test and kappa-hat on the full universe; build the full-universe overlap network; Stage 1a variance decomposition and pre-registered Stage 1b test. Stage 2 needs fund-level manager data (N-PORT or CRSP MF).
- Beads/issues: cme-csl, #4.

## 2026-11-19 sumedh-agent: Stage 1 of the pivot run (both gates pass)
- Changed: `docs/stage1/PREREGISTRATION.md` (commit c14dba7, before any estimate), `stage1/` code (commit d23862d, before the 1b run), `results/stage1a_variance.json`, `results/stage1b_results.json`, `docs/stage1/RESULTS.md`. No existing script or paper number changed.
- Numbers (new, not in the paper): Stage 1a, full universe: 30.4% of var(log tau) left after institution and quarter FE (gate 10%), quarter FE 2.4%, AR(1) 0.75. Stage 1b: neighbours' non-held-stock horizon -> own next-quarter horizon b = +0.0324 (t = 5.33; 199,225 institution-quarters, 8,866 institutions, 51 quarters; institution and style-by-quarter FE; two-way clustered SE). Future-neighbour placebo -0.0080 (t = -2.48); shuffled placebo +0.0035 (t = 1.62). Secondary: all-positions +0.046, quarter FE only +0.034, k=5 +0.025, k=20 +0.040; adding share of short-horizon neighbours absorbs the average-horizon effect (share short -0.072, t = -5.16). Shuffle seed 20261119.
- Why: Stage 1 of the recommended pivot (horizon contagion).
- Meaning: descriptive evidence consistent with horizon contagion, small in size (about 2% of a within SD per SD), implied long-run response about 0.044, same order as the model's assumed 0.06. Not causal; Stage 2 needs fund-level manager shocks.
- Open: Stage 2 data (N-PORT or CRSP mutual funds for manager changes); test average vs share-of-short-neighbours forms; team decision on the pivot (cme-x59).
- Beads/issues: cme-x59, cme-csl, cme-i7t (Stage 2).

## 2026-11-19 sumedh-agent: Stage 2 feasibility with free SEC data (N-PORT + Form 497)
- Changed: new `stage2/` (download_nport.py, nport_coverage.py, scope_events.py, link_events.py, power.py), `docs/stage2/FEASIBILITY.md`, `results/stage2_*.json`, `results/stage2_events.csv`; `.gitignore` adds `stage2_cache/` and `nport_cache/`. No existing script or paper number changed. No Stage 2 coefficient estimated.
- Numbers (new, scoping only): N-PORT 2023Q1 has 11,717 fund series, 6,478 equity funds (4,447 with net assets of at least 100 million dollars), share counts and CUSIPs; data sets cover 2019Q4 to 2026Q3 only. Form 497 manager events 2019-10 to 2026-09 linked to N-PORT series through filing-header SERIES-IDs: deaths 6 announcements on equity funds (17 series); retirements 231 announcements (938 series, 129 trusts). Power: one shocked neighbour of k = 10 moves the peer variable by delta/10, so at the Stage 1 slope (0.032) the minimum detectable coefficient is 15x to 25x the Stage 1 estimate with about 231 to 300 shocks and a first stage of 0.5; even 3,000 shocks with a first stage of 1.0 reach only 2.3x.
- Why: Stage 2 (identification) of idea 1; the user asked to try free N-PORT data instead of CRSP.
- Meaning: deaths fail the count gate; retirements pass it, but the count gate was the wrong test. A single-neighbour manager-shock design cannot identify an effect of the Stage 1 size. Recommendation in FEASIBILITY.md: switch the headline to idea 2 with Stage 1 as a descriptive section (option 1), or find shocks that move many neighbours at once (option 2).
- Open: team decision on the pivot (cme-x59); if Stage 2 continues, download all 28 N-PORT zips, build the fund panel and measure the retirement first stage; manual pass over death filings.
- Beads/issues: cme-i7t, cme-x59.

## 2026-11-21 sumedh-agent: idea search round 2 (data scoping)
- Changed: new `scoping/wrong_unit_filings.py`, `scoping/retirement_windows.py`, `results/scoping_wrong_unit_filings.json`, `results/scoping_retirement_windows.json`. Ranked write-up on branch `sumedh-agent/novelty-audit` (`docs/novelty-audit/ideas-round2-2026-11-21.md`). No existing script or paper number changed.
- Numbers (new, scoping only): 3,128 of 316,973 13F filings read 1000x too large under the rule in force (620 filers, about 300 a year 2014 to 2022), 9,375 read 1000x too small (almost all after 2023). Retirement announcements on N-PORT equity funds: 130 of 231 state a retirement date; median lag 4.5 months, 59% at least 3 months.
- Why: the team rejected both Stage 2 fallbacks; user asked for more ideas.
- Meaning: recommended next idea is lame-duck managers (planned retirements and fund horizons), with fake whales second. Vote recall is close to pre-empted (Li and Zhu 2025).
- Open: manual SSRN and CNKI search for idea 1; team decision (cme-x59).
- Beads/issues: cme-x59.

## 2026-11-21 sumedh-agent: N-PORT fund panel for the lame-duck design
- Changed: new `nport_panel/` (build_fund_panel.py, test_build_fund_panel.py, validate_turnover.py, event_coverage.py, README.md), `scoping/split_rule_check.py`, `results/nport_panel_build.json`, `results/nport_turnover_validation.json`, `results/nport_event_coverage.json`, `results/scoping_split_rule_check.json`. `scoping/retirement_windows.py` now extracts stated dates for all 462 retirement announcements (`results/scoping_retirement_dates.csv`); its round-2 summary numbers are unchanged (same subset), two counts added. `.gitignore` adds `nport_panel_data/`. No paper number changed.
- Numbers (new): panel from all 28 N-PORT zips (2019Q4 to 2026Q3): 331,119 reports kept of 355,115, 31.1M equity rows, 312,867 turnover rows on 17,203 series. Equity funds (at least 20 stocks): median quarterly share-based turnover 0.103, 12.4% clipped at tau 2000. Validation vs prospectus turnover (Risk/Return data sets; no fiscal 2024 file), equity funds, 27,866 fund-years, 7,082 funds: Spearman 0.79, log Pearson 0.77; share-based measure 1.08x reported (flows inflate it), min(buys, sells) measure 0.77x reported (misses round trips inside a quarter). Event coverage on equity funds: 197 announcements, 105 with a stated date, 46 with a date, 2 pre, at least 1 lame-duck and 2 post reports (122 series events). Blind power check (whole-panel variance only): within-fund sd of log turnover 0.642; MDE 0.19 to 0.27 log points at N = 46, 0.09 to 0.13 at N = 200. 13F split rule: fired on 1,385,494 of 63,618,289 continuing positions, 96.8% without a confirming price move (2.1% of positions, 3.9% of value).
- Why: user asked to build the panel for idea 1 (lame-duck managers).
- Meaning: the panel measures turnover well enough to rank funds. The binding limit is events: only about 46 usable announcements, enough for a 20 to 30% turnover shift, not a small one. 92 equity announcements have no stated date and 48 dated windows are under 3 months (no quarterly report inside). The 13F split rule biases Stage 1 tau_split upward; Stage 1 needs a rerun after the fix (cme-d0m), which will move Stage 1 numbers and needs a result-change issue.
- Open: grow the event set (more 497 phrases, better date extraction, hand-coding undated announcements) before pre-registering; no outcome has been read by event time. Fix cme-d0m and rerun Stage 1. Team decision (cme-x59).
- Beads/issues: cme-d0m, cme-i7t, cme-x59.
