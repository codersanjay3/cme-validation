# Idea search, round 2 (2026-11-21)

Why a second round: Stage 2 scoping (PR #7) showed the horizon-contagion shock design is badly underpowered, and the team did not want either fallback (idea 2 headline, or multi-neighbour shocks). This round looked for new ideas that use the data we already built: the full-universe 13F panel, N-PORT fund holdings (2019Q4 to 2026Q3), and the Form 497 manager events linked to N-PORT series.

Method: six candidates; three parallel literature checks (Google Scholar and SSRN blocked automated access, so they used OpenAlex, RePEc/IDEAS, NBER, journal sites, ECGI, arXiv and web search; every paper below was opened in the check, not cited from memory); plus data checks on our own panel (scripts on branch `sumedh-agent/idea-scoping`). **Gap common to all verdicts: SSRN-only working papers from 2024 to 2026 could not be searched directly.** That has to be closed by hand before committing to any of these.

## Ranking

| Rank | Idea | Novelty verdict | Data | Main risk |
|---|---|---|---|---|
| 1 | Lame-duck managers | Partly done, core open (about 65 to 70%) | Ready | Short pre-departure windows |
| 2 | Fake whales (wrong-unit 13F filings as a salience experiment) | Open | 3,128 inflated filings ready | First stage (did anyone see the wrong values?) not shown |
| 3 | Turnover gap (reported minus holdings-based turnover) | Partly done | Ready, but only about 6 fiscal years | Short panel for persistence and pricing |
| 4 | Open data paper (13F + N-PORT horizons) | Partly done | Ready | Layline (Balogh) already publishes free 13F holdings |
| 5 | Retirement price pressure | Partly done, close to open | Ready | Low power; fold into idea 1 |
| 6 | Vote recall (new N-PX shares-on-loan field) | Close to pre-empted | Needs per-filing N-PX parsing | Li and Zhu (2025) do almost exactly this |

## 1. Lame-duck managers (recommended)

**Question.** When a fund manager's career has a known end date, does the portfolio's horizon change? Planned retirements announced in Form 497 supplements fix the remaining career horizon months in advance, independent of recent performance (unlike most manager-turnover samples). Two theories predict opposite signs: short-termism near the end of a career (the CEO horizon problem, Dechow and Sloan 1991), against longer horizons once career concerns fade (career-concerns models; van Binsbergen, Han, Ruan and Xing 2021 find turnover falls with tenure). The test separates them.

**Design.** Fund-quarter panel from N-PORT (share-based turnover as in the 13F rebuild, active share, style drift; risk from N-PORT monthly returns). Event time relative to the announcement and the stated retirement date. Controls: same-family funds and matched funds without a departure; within-manager comparisons where one manager runs several series; split by successor (named co-manager vs new manager). The successor's rebalancing and any price pressure on heavily held stocks (idea 5) become a section.

**Data facts (ours).** 231 retirement announcements on N-PORT equity funds, 938 fund series, 129 trusts (`results/stage2_event_link.json`). 130 announcements state a retirement date (121 to the day); median lag from filing to retirement 4.5 months, 59% at least 3 months, 34% at least 6 months (`results/scoping_retirement_windows.json`). Power is not the Stage 2 problem here: the outcome is the fund's own horizon, so there is no 1/k dilution.

**Closest papers (all opened in the check).**
- Khorana (2001), JFQA 36(3): risk shifting before and turnover after manager replacement; 393 performance-driven replacements, 1979 to 1991, retirements not separated.
- Chevalier and Ellison (1999), QJE: younger managers take less unsystematic risk (cross-section).
- van Binsbergen, Han, Ruan and Xing (2021), SSRN 3920863: equilibrium model in which horizons lengthen as career growth shrinks; turnover falls about 1.9% per year of tenure (CRSP/Morningstar to 2019). Closest framing; cross-sectional, no dated end of career.
- Clare, Motson, Sapuric and Todorovic (2014), IRFA: UK manager changes, retirement pooled with other reasons, performance only.
- Kostovetsky and Warner (2015), JFQA: departures and lagged performance and flows.
- Wang and Ko (2017), IREF: Chinese manager turnover types, performance only.
- Jin and Scherbina (2011), RFS: new managers sell inherited losers.

**What makes ours new.** Dated, planned, non-performance end of career; holdings-based outcomes in the pre-departure window; a direct test between the two theories; successor-type split.

**Before committing.** SSRN title search done (below, no pre-emption); still open: SSRN abstract search by hand and CNKI. Then build the N-PORT fund panel (download all 28 quarters) and pre-register.

### SSRN check (2026-11-21)

SSRN's own search sits behind a bot check that automated browsers cannot pass, so SSRN was searched through Crossref, where every SSRN paper has a DOI with prefix 10.2139: 33 queries (retirement, lame duck, career horizon, succession, departure announcement, tenure, age, key person, resignation, manager deaths, personal horizon), papers from 2015 on, about 700 distinct SSRN papers screened by title. Crossref matches titles and metadata, not abstracts or full text.

**No pre-emption found.** Closest new items:
- Cui, Ding, Han, Shen and Suardi (2026), SSRN 6878904: China's two-child policy as a shock to anticipated career costs of female fund managers; performance, volatility and style change. Same logic (an anticipated change in career prospects moves portfolio choices), different shock and country.
- Xu, Han and Wu (2026), SSRN 7061359: managers strategically resign from poorly performing funds while keeping others. Departures chosen by the manager, the opposite of a planned retirement.
- Lee, Nam, Pool and Zhang (2025), SSRN 5440154 / 5739548: compensation evaluation horizons disclosed in fund SAIs; long-horizon contracts lead to long-term investments. **Use as a mechanism test:** the lame-duck effect should be larger when the retiring manager's pay is evaluated over a short window, and smaller when deferred pay ties the manager to results after leaving. SAIs are free on EDGAR.
- Kang, Bams, Ebrahimnejad and Tehranian (2024), SSRN 5011836: exogenous horizon variation from disclosure dates; different mechanism.
- Marino, Kirmse and Previti (2025), SSRN 5397288, "Manager Taxation and Investment Horizon": no abstract available; check by hand.

Remaining gap: abstract and full-text search on SSRN itself (needs a person to pass the bot check), and CNKI.

## 2. Fake whales

**Question.** Do 13F filings that read 1000 times too large, holding their information content fixed, move attention, volume or prices of the held stocks? A natural experiment on the salience of disclosed position size.

**Data facts (ours, `results/scoping_wrong_unit_filings.json`).** Of 316,973 filings, 3,128 read 1000 times too large under the rule in force (filers writing dollars where thousands were required), from 620 filers, about 300 a year from 2014 to 2022 and almost none after 2023. Median as-read assets $295 billion against a true $295 million; 686 filings read above $1 trillion; the filer's largest position typically reads larger than all other filers' true holdings in that stock combined (median 1.4 times). Another 9,375 filings, almost all after 2023, read 1000 times too small (thousands where dollars were required).

**Closest work.** Cao, Da, Jiang and Yang (Management Science, forthcoming) on strategic 13F restatements, which drops clerical errors; Lim (2026, Research Square) placebo test of 13F filing-date reactions using Norges Bank's empty filings; Brown and Schwarz on filing-date trading; Cao, Du, Zhang and Yang on copycat attention from EDGAR logs; Carvalho, Klagge and Moench on the United Airlines stale-news shock; Anderson and Brockman on 13F misfilings (no market test).

**Main risk.** Some tools already infer the unit per filing (davemanuel.com) or convert to dollars (sec-api.io); no direct proof yet that a major site showed one of our inflated filings uncorrected. Related cases exist (Mirae's 2026 Berkshire share-class error shown at $264.6 billion; a July 2026 viral misreading of an XRP ETF position). The first step would be to establish what popular trackers and EDGAR's own rendering displayed for a sample of the 3,128 filings, and whether free attention data (EDGAR log files) cover the years.

## 3. Turnover gap

Prospectus turnover (`oef:PortfolioTurnoverRate`, SEC Risk/Return Summary data sets, 2010 to 2026) minus holdings-based turnover from N-PORT measures trading that quarterly snapshots miss. Elton, Gruber, Blake, Krasny and Ozelge (2010, JBF) measure this in aggregate; An, Huang, Lou, Wen and Xu (2025, LSE FMG DP 923) use it as a constraint when inferring intra-quarter trades. No fund-level study of its size, persistence, determinants and consequences was found. Limit: about six fiscal years of free holdings. Public N-PORT stays quarterly at least until late 2027 (monthly disclosure delayed). Best used as a measurement section inside idea 1 or as a short paper.

## 4. Open data paper

Raw free 13F holdings already exist: Balogh's Layline data (Harvard Dataverse, 2013 to 2026, CC BY), whose author already has a Scientific Data descriptor on insider trading (2023); public N-PORT holdings with code from Cavani, Maggiori and Schreger (NBER WP 34494). Ours would add the per-filing unit audit, dollar-consistent values, validated share-based horizons and a 13F to N-PORT crosswalk. Scientific Data impact factor 7.2 (2025). Worth doing only as a companion release to a research paper.

## 5. Retirement price pressure

No paper tests prices of stocks heavily held by a fund whose manager announced retirement. Close: Jin and Scherbina (2011); Coval and Stafford (2007); Dyakov and Verbeek (2013); Shive and Yun (2013); Huang, Ringgenberg and Zhang (2023); Wardlaw (2020) finds small flow-pressure effects with no reversal, which lowers the prior. Fold into idea 1.

## 6. Vote recall

Li and Zhu (2025), "(Re)call of Duty," ECGI WP 1107/2025 (SSRN 4757185), use N-PORT and the new N-PX shares-on-loan field for recall by horizon, lending fees, close votes and outcomes. Left open: 13F managers' N-PX filings, the 2024-25 and 2025-26 seasons, unrecalled fractions. Not recommended as a headline.
