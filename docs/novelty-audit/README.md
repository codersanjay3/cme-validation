# Novelty audit and pivot ideas (sumedh-agent)

A literature review and novelty audit to decide how to pivot the CME paper into a contribution that is new and publishable at a journal with impact factor above 4 to 5. Run with the hyperresearch deep-research pipeline (github.com/jordan-gibbs/hyperresearch) over about 180 sources, plus checks on our own 13F data.

**This branch is kept up to date as the work continues.** Newest status is at the top of the log below.

## Start here

- [`IDEAS.md`](IDEAS.md): every project idea found, ranked, with novelty status, closest papers, design and journals.
- [`report.md`](report.md): the full audit report (literature map, novelty verdict per pivot, recommendation, journals, identification, referee objections). Status: see log.
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
- Full-universe SEC 13F download (needs an SEC contact email set as `SEC_CONTACT_EMAIL`).
- Team decision on the pivot; Professor Chalmers's view on the model.

## Log

- 2026-11-18: branch created with the audit at the critique stage (report drafted, four critiques done, gap-filling done; patch, citation check and polish still to run).
