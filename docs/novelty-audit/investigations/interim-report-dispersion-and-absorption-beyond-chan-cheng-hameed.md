---
title: Interim report — dispersion-and-absorption-beyond-chan-cheng-hameed
id: interim-report-dispersion-and-absorption-beyond-chan-cheng-hameed
tags:
- investor-horizon-novelty-audit-45a8e3
- locus-dispersion-and-absorption-beyond-chan-cheng-hameed
created: '2026-11-19T01:24:31.892562Z'
status: draft
type: interim
deprecated: false
summary: CCH IA1 already shows dispersion lowers return volatility net of liquidity
  (pre-empts CME slope); residual = crash/fragility horse race and relative absorption;
  section not paper
---

# Interim report: dispersion-and-absorption-beyond-chan-cheng-hameed

**Locus question:** After Chan-Cheng-Hameed (JFQA 2022), what is left of Pivot B: does horizon dispersion lower volatility/crash risk net of Greenwood-Thesmar fragility and liquidity, and do long-horizon holders absorb short-horizon selling within a stock in stress, or do retail/hedge funds?
**Flavor:** dialectical

## What the corpus already said

The corpus flagged [[investor-heterogeneity-and-liquidity]] (Chan-Cheng-Hameed, CCH) as the closest paper and recorded that it tests liquidity outcomes only. It recorded [[do-institutional-investors-stabilize]] (Glossner et al.) as a level-effect, retail-as-liquidity-provider result. It recorded [[issn-0956-8549-717-2]] (Cella-Ellul-Giannetti, CEG) as the level-of-short-horizon-ownership baseline. It recorded [[stock-price-fragility-2]] (Greenwood-Thesmar, GT) as flow-covariance fragility, not horizon dispersion. Also in the vault: [[crash-risk-and-investor-horizon]] (Zhu / Benkraiem et al. JIFMIM 2022, level of short vs long IO and skewness), [[heterogeneity-of-institutional-ownership-and-stock-price-delay]] (Chen-Lee-Sun, ownership-share buckets), [[outside-and-inside-liquidity]] (Bolton-Santos-Scheinkman, theory only). Correction of the corpus summary of CCH: its "NOT tested: volatility" is wrong, see below.

## What the new sources say

**[[internet-appendix]] (CCH Internet Appendix, Table IA1).** The main text (fn. 12, [[investor-heterogeneity-and-liquidity]]) says "high STDCR is negatively related to stock return volatility ... robust to controlling for illiquidity and other stock characteristics." IA1 is quarterly Fama-MacBeth of daily-return SD on lagged STDCR, with Size, BM, past returns, Num_Fund, IO, LOGILLIQ, 1/TURN, LOGCVILLIQ and LOGCVTURN. Coefficients on STDCR are -0.034** to -0.042***, with one specification at -0.012 (t=-0.89), over 1982-2016, and -0.039* to -0.057** over 2000-2016 (t from -1.85 to -2.59). This is the same sign as the CME stock-level result (-0.011, t=-2.4), obtained net of liquidity level and liquidity volatility. So the CME volatility finding is a replication, not a discovery. It is, however, not in the paper's main tables, and CCH treat it as an intermediate channel, not as an outcome. Neither crash risk, skewness nor GT fragility appears.

**[[investor-heterogeneity-and-liquidity]] (CCH full text) on absorption.** The mechanism is conjectural at the holder level: "long-horizon funds can provide liquidity to active mutual funds during fire sales." The tests are indirect. Fund-flow comovement is higher within a churn tercile (Table 2). Coval-Stafford flow-induced trading has larger price impact and reversal in low-STDCR stocks. The 2003 dividend tax cut is the exogenous shock. No test observes who buys. Two further points matter for pivot C and for measurement. CCH use the Gaspar drift-adjusted churn, |N_t P_t − N_{t−1}P_{t−1} − N_{t−1}ΔP_t|, and in a robustness test also a share-based turnover (STDTO, price-free), with similar results (-0.31% illiquidity per SD, 1.58% inverse turnover). So the price-drift contamination point is already known to this literature, and CCH's headline measure is not value-weight turnover contaminated by drift in the CME sense.

**[[do-institutional-investors-stabilize]] (Glossner-Matos-Ramelli-Wagner).** In Q1-2020 firm-level IO changes were "highly negative skewed ... an overall divestment of institutional investors." Retail investors, via Vanda and Robinhood data, took the other side: "individual investors provided liquidity to stocks shunned by" institutions, and downscaling institutions "did not buy stocks abandoned in Q1 by their fellow downscaling institutional investors." Long-term IO (37% mean) mitigates losses as a level, passive IO (16%) likewise. Hedge funds sell indiscriminately. The paper has no within-stock dispersion and no counterparty test by horizon.

**[[issn-0956-8549-717-2]] (CEG).** Short-horizon institutions sold about 21% of holdings in the Lehman window versus 7% for long-horizon. Long-horizon holders sold too; they sold less. Stocks with more short-horizon holders show larger drops and reversals, and the authors attribute the reversals to "demanding liquidity at times when other potential buyers' capital is scarce." The horizon measure is a predetermined 22-quarter average churn ratio, a level.

**[[stock-price-fragility-2]] (GT).** Fragility is w'Ωw with Ω the covariance of owners' flow shocks, from mutual-fund flow histories. It "strongly predicts price volatility." Ownership diversity enters only via flow covariance and concentration. CCH's own Table 2 (flow comovement higher within a churn tercile) is the bridge: dispersion in horizon is a cheap proxy for low flow covariance, so a horse race against GT fragility is the natural, unperformed test, and a dispersion effect that survives it would be the cleanest residual.

**[[institutional-investor-horizons-and-stock-price-crash-risk]] (Fu, Fang, Yang, Yao, RIBAF 72, 2024; abstract only, paywalled, provenance: RePEc/Elsevier abstract).** China A-shares 2007-2019. Long-term holding mitigates crash risk through curbing managerial myopia and governance; herding, cliques and board features are moderators. This is a level-of-horizon governance story, not dispersion and not liquidity absorption. [[heterogeneous-institutional-investors-short-selling-and-stock-price-crash-risk-e]] (Wen, Xu, Chen, EMFT 2020, abstract): "grey" and independent institutions both raise crash risk in China, type buckets, not dispersion. Adjacent web-search findings (not fetched, abstracts only): Benkraiem-Goutte-Saadi-Zhu-Zhu 2022 (JIFMIM) level of short vs long IO; Pan-Xu-Zhu 2021 (J. Manag. Sci. Eng.) professional vs non-professional IO and crash sensitivity. I found no Chinese or other paper with a stock-level dispersion of holder horizons as the regressor for crash risk (search-limited; ~6 queries, no Google Scholar access).

**[[nber-working-paper-series-17]] (Barbon-Di Maggio-Franzoni-Landier, JF 2019).** In fire-sale liquidations of a distressed fund, other managers trade in the same direction in 30-42% of positions (per search snippet; the figure was not verified in the fetched PDF), with clients of the distressed fund's brokers preying early and buying back later. This weakens the premise that other institutions mostly supply liquidity to a fire-selling institution.

## Evidence synthesis

### Position A: long-horizon holders absorb short-horizon selling, so dispersion stabilises
Best case: theory (Bolton-Santos-Scheinkman outside liquidity), CCH's price-impact and reversal results by STDCR (a heterogeneous base reduces Coval-Stafford price pressure), CCH IA1 (STDCR lowers return volatility net of liquidity), flow-comovement within churn terciles, and CEG's 7% vs 21% selling gap. This is a coherent story for a stock-level reduced form: a dispersed base has less correlated liquidity demand, which is exactly GT's fragility logic. The CME stock-level slope (-0.011, t=-2.4) fits.

### Position B: retail, arbitrageurs and hedge-fund counterparties absorb; long-horizon institutions merely sell less
Best case: Glossner et al. show institutions in aggregate were net sellers and retail took the other side, and downscaling institutions did not buy back what peers sold. CEG show long-horizon holders sold too. Barbon et al. show co-trading in the same direction, not counter-trading. Koijen-Richmond-Yogo (corpus) show long-horizon types have the smallest price impact, which is a low-elasticity-demand fact, not absorption. Under this view, dispersion helps only through composition: a base with many low-flow-sensitivity holders sells less in total, a level effect that a share-of-long-horizon control would absorb.

**How I read the two sides.** The factual dispute is narrower than the labels suggest. Position A's volatility and liquidity predictions are supported at stock level (CCH, with IA1), but its mechanism, counterparty absorption, has never been observed. Position B's retail evidence is from one episode (2020Q1) and one data vendor, and shows who bought in aggregate, not whether, within a stock, long-horizon holders bought from short-horizon holders. Both can be true. Aggregate institutions can net-sell while long-horizon holders within a given stock sell less than short-horizon ones; "absorption" would then mean relative, not absolute, buying. Quarterly 13F can measure only net changes, so absorption must be defined as: for stocks with large short-horizon net selling, do long-horizon holders' share changes exceed what composition predicts? That is testable in 2008Q3/Q4, 2020Q1, 2022 but intra-quarter round trips are invisible and short-horizon selling is endogenous to the stress. Flow-induced trading (Coval-Stafford) is the only credible instrument, and CCH already use it.

Sign conflict with the CME simulation: the second opposing pair (mixing raises variance via Kondor 2012-type disagreement and ABM friction) concerns trading volume and announcement-window variance. The stock-level empirical sign is now supported by two independent estimates (CCH IA1 and the CME slope), so the simulated friction channel is the outlier. It should be re-signed or dropped from the empirical claim.

## Committed position

Most of Pivot B is already done. CCH 2022 published the dispersion measure, the churn construction (drift-adjusted, with a share-based robustness), the liquidity outcomes, the fund-flow-comovement mechanism, the flow-induced-trading test, the tax-reform identification, and (in the Internet Appendix and fn. 12) the sign of dispersion on return volatility net of liquidity, which is exactly what the CME stock-level regression shows. The CME slope (-0.011, t=-2.4, survivors only, no CRSP) therefore cannot be presented as a finding; at best it is an out-of-sample, 2013-2026 replication of an IA table, with weaker data. What remains is narrow: (1) holder-horizon dispersion as a determinant of crash risk and negative skewness, where I found only level-of-horizon papers (Zhu/Benkraiem 2022, Fu et al. RIBAF 2024, Wen et al. 2020); (2) a horse race of horizon dispersion against Greenwood-Thesmar flow-covariance fragility (and against short-horizon IO level and Bushee-type composition shares), asking whether dispersion carries information beyond flow covariance; and (3) a direct, 13F-feasible within-stock absorption test in named stress episodes. On (3), existing evidence leans against a strong version: aggregate institutions net-sold and retail bought (Glossner), long-horizon holders also sold (CEG, 7% vs 21%), and co-trading dominates counter-trading in distressed liquidations (Barbon et al.). A new paper would most plausibly find a relative, not absolute, absorption effect: long-horizon holders' net selling is smaller, not negative. That is publishable as a fact but modest. Because the quarterly 13F cannot see intra-quarter absorption, the headline claim would rest on a reduced form, not on observed counterparties. My load-bearing reason: the only genuinely open part of B depends on outcomes (crash, skewness, fragility-adjusted volatility) where I found no direct prior art, but the dispersion-to-liquidity and dispersion-to-volatility sign is pre-empted, so B can carry a section, not a journal-level paper by itself.

- **Position:** Pivot B is worth a section (the crash/fragility horse-race plus a relative-absorption test) within a larger paper, not a stand-alone paper for an IF>4-5 journal; the volatility sign result must be recast as a replication of CCH IA1.
- **Confidence:** medium (about 65%) on "not a stand-alone paper"; medium-low (about 45%) that no near-duplicate on dispersion-to-crash exists, since searches were limited to web search without Google Scholar or SSRN full-text and I could not read the RIBAF paper's full text.
- **Boundary conditions:** Holds for US 13F-based dispersion measured by cross-holder SD of churn (or log tau). A dispersion measure that is not mechanically tied to the number of holders and size (CCH control Num_Fund, IO, HHI), plus survivor-free CRSP data, might change the weight of the replication. Outside 13F-observable quarterly net changes, the evidence is insufficient.
- **What would change this position:** (i) A dispersion-to-crash or skewness effect with t above 3 surviving GT fragility, short-horizon IO level, IO breadth, size and liquidity controls, in both 1982-2016 and 2013-2026, would make B a stand-alone short paper at JBF/JFM tier. (ii) A within-stock design showing long-horizon holders are net buyers (positive share change) in stocks with large short-horizon selling in at least two stress episodes (2008Q3-Q4, 2020Q1), robust to the Coval-Stafford instrument, would upgrade it to a first-order fact. (iii) Discovery of an existing paper (SSRN 2023-2026) doing dispersion-to-crash would downgrade it to nothing; the full RIBAF 2024 text could do this if it contains a dispersion measure, which the abstract does not suggest.
- **Evidence weight:** 1 closest-paper full text plus appendix (CCH) supports the sign and pre-empts it; 3 empirical papers (Glossner, CEG, Barbon) lean against strong absorption; 1 theory paper (Bolton et al.) supports it; the crash-risk Chinese papers (2 abstracts only) are level/type, not dispersion; 1 conceptual bridge (CCH Table 2 to GT fragility) is untested.

**Prescriptive increments to use if B is kept as a section.** (a) Report the dispersion slope next to CCH IA1 as a replication and show it survives GT fragility; (b) outcome = next-year crash indicator or negative skewness (NCSKEW, DUVOL), regressors = ownership-weighted SD of log tau plus short-horizon IO share; (c) absorption test = for stocks in the top-decile short-horizon net selling in 2008Q3-Q4 and 2020Q1, regress long-horizon holders' change in shares-held fraction on the interaction of short-horizon selling and dispersion, instrumenting with Coval-Stafford flow-induced trading; (d) always use the share-based turnover, not value-weight, and show it with Gaspar drift-adjusted churn too.

## Open questions

- Full text of Fu et al. (RIBAF 2024) and the Chinese-language institutional-heterogeneity crash literature (CNKI) not read; confirm no dispersion regressor.
- Whether any SSRN 2023-2026 paper cites CCH and uses dispersion for crash risk or fragility (RePEc lists only two citing papers, neither a clear follow-up).
- Bond-fund (N-PORT) liquidity-supplying vs liquidity-demanding fund-style literature (Wang-Zhang corporate-bond fire sales; Jiang, Li, Wang) was not read; relevant to the team's N-PORT data.
- Exact Barbon et al. 30-42% same-direction figure should be verified in the PDF.
- Whether the CME value-weight tau is contaminated relative to Gaspar's drift-adjusted churn (CCH's formula already subtracts N_{t-1}ΔP).

## Sources

1. [[investor-heterogeneity-and-liquidity]] Chan-Cheng-Hameed (JFQA 2022)
2. [[internet-appendix]] CCH Internet Appendix (IA1 volatility)
3. [[do-institutional-investors-stabilize]] Glossner et al.
4. [[issn-0956-8549-717-2]] Cella-Ellul-Giannetti
5. [[stock-price-fragility-2]] Greenwood-Thesmar
6. [[institutional-investor-horizons-and-stock-price-crash-risk]] Fu et al. RIBAF 2024 (abstract)
7. [[heterogeneous-institutional-investors-short-selling-and-stock-price-crash-risk-e]] Wen-Xu-Chen 2020 (abstract)
8. [[nber-working-paper-series-17]] Barbon et al. (JF 2019)
9. [[crash-risk-and-investor-horizon]], [[heterogeneity-of-institutional-ownership-and-stock-price-delay]], [[outside-and-inside-liquidity]] (corpus)
