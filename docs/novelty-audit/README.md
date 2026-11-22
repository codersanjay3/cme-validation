# Novelty audit and pivot ideas (sumedh-agent)

A literature review and novelty audit to decide how to pivot the CME paper into a contribution that is new and publishable at a journal with impact factor above 4 to 5. Run with the hyperresearch deep-research pipeline (github.com/jordan-gibbs/hyperresearch) over about 180 sources, plus checks on our own 13F data.

**This branch is kept up to date as the work continues.** Newest status is at the top of the log below.

## Start here

- [`ideas-round2-2026-11-21.md`](ideas-round2-2026-11-21.md): second idea search after Stage 2 scoping (six new candidates, ranked).
- [`IDEAS.md`](IDEAS.md): every project idea found, ranked, with novelty status, closest papers, design and journals.
- [`report.md`](report.md): the full audit report (literature map, novelty verdict per pivot, recommendation, journals, identification, referee objections). **Final: passed every ship check** (10,691 words, 89 sources cited, 40 citations per 1,000 words, all quotes verbatim, no retracted sources).
- [`sources.csv`](sources.csv): bibliography of every source in the research vault (metadata and our one-line summaries only; full texts are not committed).

## Bottom line so far

1. Recommended pivot: **horizon contagion**, the first identified peer effect in institutional investment horizon through portfolio-overlap networks, run as a staged, pre-registered programme on the full SEC 13F universe with manager-level shocks to neighbours.
2. Named fallback: a US stress-episode paper on whether long-horizon holders absorb short-horizon selling within a stock.
3. The current paper's empirical headlines are pre-empted, mechanical or replications: dispersion and liquidity/volatility (Chan-Cheng-Hameed, JFQA 2022), price-drift-free turnover (Gaspar-Massa-Matos 2005), homophily (mostly mechanical). They become modules.
4. The impact-factor bar is not the constraint: Finance Research Letters is already 7.1. The constraint is a contribution that is not a replication.
5. Data fix needed whatever the pivot: the 2022Q4 TDI minimum is an artefact of the SEC's 2023 switch to dollar values (issue #1).

## Folder map

| Path | What it is |
|---|---|
| `IDEAS.md` | Ranked list of all project ideas |
| `report.md` | Audit report (updated as the pipeline finishes) |
| `sources.csv` | Bibliography: note id, title, URL, summary, tags |
| `investigations/` | Six focused investigations, each ending in a committed position |
| `drafts/` | Three independent drafts (lead with A; contrarian case for absorption; staged programme) |
| `process/query.md` | The exact research question given to the pipeline |
| `process/loci.json`, `process/comparisons.md` | The questions investigated in depth and how their answers interact |
| `process/source-tensions.json`, `process/contradiction-graph.json` | Where the literature disagrees, and our reading |
| `process/corpus-critic-results.md` | Adversarial searches for papers that would kill each idea |
| `process/critic-findings-*.json` | Four critiques of the report |
| `process/orchestrator-notes.md` | Running notes, including outcome-free checks on our data |
| `process/evidence-digest.md` | Key claims with verbatim quotes and source ids |

## Data checks done on our own panel (outcome-free)

- Within-institution sd of log horizon 0.55 vs 0.92 total; AR(1) 0.75 (share-based, 147 institutions, 50 quarters).
- After institution and quarter fixed effects, 33% of variance remains; quarter effects alone explain about 2%.
- Top-5 nearest-neighbour overlap network: about 100 institutions per quarter; median 32 to 42 friends-of-friends that are not friends.
- 13F unit break: `scripts/check_13f_unit_break.py`, `scripts/check_share_tdi_unit_fix.py` (see DECISIONS.md).

## Open items

- Liang-Wu-Yin (SSRN 5048159) full text unread; Chinese literature (CNKI) not searched directly.
- Count of usable neighbour manager shocks in 2013-2026 (decides idea 1 vs idea 2).
- Full-universe panel: built and validated (PR #4, release `data-rebuild-v1`). Stage 1 passed (PR #6). Next: Stage 2 needs fund-level manager data (N-PORT or CRSP mutual funds).
- Team decision on the pivot; Professor Chalmers's view on the model.

## Log

- 2026-11-21: N-PORT fund panel built (PR #9, `nport_panel/` on branch `sumedh-agent/nport-panel`). All 28 zips: 331,119 fund reports, 312,867 quarterly turnover rows on 17,203 series. Holdings turnover ranks equity funds like their prospectus turnover (Spearman 0.79, 27,866 fund-years). Lame-duck events (counts only, no outcomes read): 197 equity announcements, 105 with a stated date, 46 usable; MDE 0.19 to 0.27 log points (a 20 to 30% turnover shift). Growing the event set comes before pre-registration. Side finding: the 13F split rule mistakes half-sales for reverse splits (96.8% of its firings lack a confirming price move), so Stage 1 needs a rerun (bead cme-d0m).
- 2026-11-21: SSRN check for lame-duck managers (about 700 SSRN papers via Crossref, 33 queries): no pre-emption. New mechanism test from Lee, Nam, Pool and Zhang (2025): contract evaluation horizon in fund SAIs.
- 2026-11-21: idea search round 2 (`ideas-round2-2026-11-21.md`). Six new candidates checked against the literature and our data. Recommended: lame-duck managers (planned retirements as a dated end of a manager's career; does the fund's horizon shorten or lengthen?), core open, data ready (231 announcements, median 4.5-month window). Second: fake whales (3,128 13F filings that read 1000x too large as a salience experiment), open but first stage unproven. Vote recall is close to pre-empted (Li and Zhu 2025). SSRN still needs a manual search.
- 2026-11-19: Stage 2 feasibility with free data (PR #7, `docs/stage2/FEASIBILITY.md` on branch `sumedh-agent/stage2-nport`). N-PORT data sets give fund-level share counts and CUSIPs (2019Q4 to 2026Q3; 6,478 equity funds per quarter). Form 497 manager events link to N-PORT through filing-header series IDs: deaths 6 announcements on equity funds (fails the count gate), retirements 231 (passes). Power check: one shocked neighbour of 10 moves the peer variable by a tenth of the shock, so the design can only detect effects 15x to 25x the Stage 1 slope. Recommendation: switch the headline to idea 2 with Stage 1 as a descriptive section, or scope shocks that hit many neighbours at once. Team decision needed (bead cme-x59).
- 2026-11-19: Stage 1 done, both pre-registered gates pass (PR #6, `docs/stage1/` on branch `sumedh-agent/stage1-tests`). 1a: 30.4% of horizon variance moves within institutions (gate 10%). 1b: neighbours' horizon in stocks the institution did not hold predicts its next-quarter horizon, b = +0.032 (t = 5.3); future-neighbour placebo negative, shuffled placebo zero. Small and descriptive; Stage 2 (manager shocks) next, bead cme-i7t.
- 2026-11-19: Stage 0 done. Full-universe 13F panel built from the SEC data sets (322k filings, 13,124 institutions, 287k institution-quarter horizons, 2013Q1 to 2026Q2), validated against the top-150 panel (rank correlation 0.934), shared as release `data-rebuild-v1` (PR #4).
- 2026-11-19: follow-up search (`followup-search-2026-11-19.md`): no pre-emption of idea 1 found (Liang-Wu-Yin abstract, Chinese co-holding literature, manager-change designs); new design precedent for idea 1 (Luo, social-network contagion after disasters); Aragon-Strahan added to idea 2; idea 7 downgraded (known to practitioners). Side result: 13F unit mixing understated the paper's stock-level slope; unit-fixed -0.0200 (t = -4.96) vs -0.0106 (issue #5).
- 2026-11-19: Stage 0 code ready on branch `sumedh-agent/13f-rebuild` (PR #4): SEC Form 13F Data Sets downloader and full-universe, share-based, unit-consistent panel builder; fixture test 10/10. Real run waits on `SEC_CONTACT_EMAIL` (bead cme-csl).
- 2026-11-19: report FINAL. Readability pass applied (16 of 19 suggestions; 3 skipped because they dropped words). Ship gate passed on all checks. Next: team decision on the pivot (bead cme-x59), count usable manager shocks, full-universe SEC 13F download.
- 2026-11-18: citation check done (378 citation-sentence pairs checked; 41 fixes applied, incl. 2 wrong-source swaps and all non-verbatim quotes removed) and polish pass done (about 640 words of repetition cut). Quote-integrity and lint gates now clean. Readability pass and final ship gate next.
- 2026-11-18: report patched with 35 of 41 critic findings (search scopes stated, confidence bases explained, joint-probability decision rule added in Section 4.4, 15 new sources incl. MacDonald 2025, FMH tests, herding baselines, 13F data limits). Citation check and polish still running.
- 2026-11-18: branch created with the audit at the critique stage (report drafted, four critiques done, gap-filling done; patch, citation check and polish still to run).
