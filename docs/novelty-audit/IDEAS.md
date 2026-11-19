# Project ideas found during the novelty audit

Every candidate study the audit produced, with its novelty status, closest prior work, what it needs, and where it could go. Status as of 2026-11-18. Confidence figures are judgements, not statistics; the basis for each is in `report.md` and `process/corpus-critic-results.md`.

Ranking: 1 is the recommended headline; 2 is the named fallback; the rest are modules or side papers.

| # | Idea | Novelty status | Closest prior work | Role |
|---|---|---|---|---|
| 1 | Horizon contagion | Open as an estimand (about 65 to 70%) | Pastor-Stambaugh-Taylor (turnover commonality); Hong-Kubik-Stein; Pool-Stoffman-Yonker; Blocher; MacDonald (2025, stock-level influence); Escobar-Pedraza (retail) | Headline paper |
| 2 | Who absorbs short-horizon selling in stress | Open at the within-stock, by-horizon level | Cella-Ellul-Giannetti (level); Chan-Cheng-Hameed (conjectured, untested); Glossner et al. (retail absorbed in 2020); Coval-Stafford; Aragon-Strahan 2012 (institutional ownership dampened Lehman liquidity loss) | Named fallback paper |
| 3 | US holder-horizon dispersion and crash risk | Partly pre-empted | Chan-Cheng-Hameed (liquidity, and volatility in their appendix); Chen-Lu-Qin 2026 (China, tail risk) | Section of 1 or 2 |
| 4 | Calibrated adaptive-horizon ABM | Novel only in calibrated form (about 70%) | Oldham 2019 (fixed horizon classes, performance rewiring); LeBaron 2001 | Final section of 1 |
| 5 | Horizon homophily in co-holding | Mostly mechanical as measured | Crane-Koch-Michenaud; Gualdi et al.; Chan-Cheng-Hameed flow comovement | Motivating fact for 1 |
| 6 | Price-drift contamination of turnover | Pre-empted since 2005 | Gaspar-Massa-Matos; Yan-Zhang | Data appendix |
| 7 | 13F dollar-unit break (2023) as a measurement note | Not novel (known to practitioners; follow-up search 2026-11-19) | Practitioner 13F analyses; StoneX and Barclays unit corrections; open-source parsers | Data-integrity appendix only |
| 8 | US vs China comparison of horizon dispersion and tail risk | Not yet audited beyond Chen-Lu-Qin | Chen-Lu-Qin 2026 | Possible JIFMIM-type paper |
| 9 | Horizon contagion and absorption in bond funds (N-PORT) | Not audited | Timmer 2018; Manconi-Massa-Yasuda 2012 | Extension using the team's N-PORT data |
| 10 | Passive-to-active horizon spillover | Not audited separately | MacDonald 2025 (passive investors influence active ones, stock level) | Mechanism test inside 1 |

## 1. Horizon contagion (recommended)

**Question.** Does an institution's investment horizon move toward the horizons of the institutions whose portfolios overlap with its own?

**Why it is open.** No paper was found that regresses an institution's own turnover, holding period or horizon on its network neighbours' horizons. Institutional peer-effect papers study what is held, traded or flowed. Papers with trading activity as the peer outcome are retail. Searches: about 18 web and OpenAlex/Crossref framings, a 2023-2026 working-paper sweep, a Chinese-language sweep, Liang-Wu-Yin (abstract and reference list), MacDonald (abstract). Limits: no SSRN or Google Scholar full text, CNKI not searched.

**Why nobody did it.** The obvious design does not identify it. Turnover has a common component that is strongest among similar funds. Same-horizon funds get correlated flows. Friends-of-friends instruments from a sampled network are invalid. Regressing an outcome on peers' mean outcome is mechanical.

**Design that could work.**
- Stage 0: rebuild the panel from the free SEC Form 13F Data Sets (full filer universe, share counts, 2013Q3 on) with the 2023 unit fix.
- Stage 1, pre-registered: variance decomposition and a descriptive neighbour test with style-by-quarter fixed effects and a future-neighbour placebo. First gate already passed in our data: 33% of the variance of log share-based horizon survives institution and quarter fixed effects (kill threshold 10%); quarter effects alone explain about 2%.
- Stage 2: event study on neighbours' manager shocks (deaths, bereavements, departures), on the template of Liu-Sulaeman-Shu-Yeung (Review of Finance 2023). Fund mergers only as robustness, excluding BlackRock-BGI (Lewellen-Lowry 2021; Massa-Schumacher-Wang 2021).
- Friends-of-friends instruments as robustness only, built on the full network (Chandrasekhar-Lewis Proposition 3.4, part 3), with Anderson-Rubin sets.

**Closest design precedent (added 2026-11-19).** Luo (SSRN 5983719): after natural disasters, institutions in socially connected but unaffected areas adopt similar sustainability tilts. Same logic as the shock arm here (exogenous shock to peers, spillover to the focal institution), different outcome.

**Theory.** Strategic complementarity among short-horizon traders (Froot-Scharfstein-Stein 1992; Chamley 2007; Cespa-Vives) predicts a positive peer effect, possibly with tipping, so test nonlinearity.

**Stage 1 result (2026-11-19, PR #6).** Both pre-registered gates pass on the full universe: 30.4% of horizon variance moves within institutions; neighbours' horizon in stocks the institution did not hold predicts its next-quarter horizon, b = +0.032 (t = 5.3); future-neighbour placebo -0.008 (negative), shuffled placebo +0.0035 (n.s.). Small (about 2% of a within SD per SD) and descriptive. Implied long-run response about 0.044, the same order as the model's assumed 0.06.

**Decision rule.** Rough joint success probability about 0.35 before Stage 1. Switch to idea 2 if fewer than about 30 usable neighbour manager shocks exist in 2013-2026, or if the Stage 1 coefficient does not survive style-by-quarter fixed effects and the placebo. Stages 0 and 1 are shared with idea 2, so starting with idea 1 costs nothing until the shock gate.

**Journals.** Review of Finance (2024 JIF 8.4), then Management Science (4.9) and JFQA (4.1 in the 2025 release).

## 2. Who absorbs short-horizon selling (fallback)

Within a stock, in named stress episodes (2008Q3-Q4, 2011, 2015Q3, 2018Q4, 2020Q1, 2022), do long-horizon holders buy what short-horizon holders sell, or only sell less? Evidence leans toward "sell less". Chan-Cheng-Hameed conjecture absorption but never test it at the holder level. Design: holder-by-episode and stock-by-episode fixed effects, Coval-Stafford flow-induced trading as the instrument, and an accounting split of absorption into long-horizon filers, other filers and non-filers (which nests the retail finding of Glossner et al.). Journals: JFQA, Review of Finance, Management Science; Journal of Financial Stability or Journal of Banking and Finance as the next tier.

## 3. US holder-horizon dispersion and crash risk

Chan-Cheng-Hameed (JFQA 2022) already show dispersion predicts better liquidity, and their appendix shows lower volatility; our stock-level slope (-0.011) is a weaker replication. What remains: crash risk and negative skewness (NCSKEW, DUVOL) in the US, in a horse race against Greenwood-Thesmar flow fragility, with share-based horizons. Section, not a paper.

## 4. Calibrated adaptive-horizon ABM

Keep the CME model only if the adaptation rate is set to the estimated peer coefficient from idea 1 and an absorption channel is calibrated from idea 2, then test out of sample. Withdraw the uncalibrated friction result: its sign is contradicted by the two direct empirical tests. ABM-friendly journals (JEDC 1.8, JEBO 2.7) are below the impact-factor bar, so this works only as the last section of an empirical paper.

## 5. Horizon homophily in co-holding

kappa-hat = 0.158 is likely mostly mechanical (index-tracking geometry, drift-contaminated horizons, type demand). Defensible only as a residual: active-weight cosine, share-based horizons, dyadic regressions with institution fixed effects and dyadic-robust errors, and a bipartite configuration-model null. Pass mark suggested by the audit: the horizon coefficient keeps about half its raw size (about 0.08) under those controls.

## 6. Price-drift contamination

Pre-empted: the standard Gaspar-Massa-Matos churn rate already nets out passive price changes. Keep as a data appendix.

## 7. The 13F unit break as a measurement note

Downgraded on 2026-11-19: the issue is known to practitioners (late switchers, corrected filings, open-source fixes), so it is not novel as a stand-alone note. It still matters for us: since 2023-01-03, 13F values are reported in dollars, not thousands. Any pipeline that stores raw values and differences them across quarters gets a 1000x break at 2022Q4. In our data it produced the paper's "sample minimum" TDI in 2022Q4 (1.021, corrected 1.918) and moved r(TDI, VIX) from -0.526 to -0.641. Whether other published or circulating work was affected has not been checked. A novelty check is needed before treating this as a letter.

## 8 to 10. Side ideas, not yet audited

- US vs China dispersion and tail risk, building on Chen-Lu-Qin (2026).
- Bond funds (N-PORT): horizon contagion or absorption among bond funds, using the team's existing N-PORT data.
- Passive-to-active spillover: MacDonald (2025) finds passive investors influence active ones at the stock level; test whether low-turnover neighbours lengthen active institutions' horizons.
