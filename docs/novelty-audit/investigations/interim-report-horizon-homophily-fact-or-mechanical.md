---
title: Interim report — horizon-homophily-fact-or-mechanical
id: interim-report-horizon-homophily-fact-or-mechanical
tags:
- investor-horizon-novelty-audit-45a8e3
- locus-horizon-homophily-fact-or-mechanical
created: '2026-11-19T01:24:33.785250Z'
status: draft
type: interim
deprecated: false
summary: D (horizon homophily in co-holding) is largely mechanical under index-tracking,
  drift-contaminated tau and type/characteristic demand; defensible only as residual
  after active-weight cosine, share-based tau, FE and BiCM
---

# Interim report: horizon-homophily-fact-or-mechanical

**Locus question:** Is "similar-horizon institutions hold similar portfolios" (cosine portfolio similarity vs horizon proximity, mean 0.158, positive in 50/50 quarters, NW t=19) a new fact, or mechanically implied by Bushee-type clustering, characteristic-based demand, horizon-type stock preferences, index tracking and shared managers, and does it survive a bipartite configuration-model null or degree/size controls?
**Flavor:** dialectical

## What the corpus already said

No paper in the vault tests horizon proximity as a predictor of pairwise portfolio similarity. The partial pre-emptions are all adjacent. [[institutional-investor-cliques-and-governance]] (Crane-Koch-Michaely) finds co-holding cliques are populated by Bushee-dedicated institutions and avoided by quasi-indexers, and that within-clique dispersion of institution type is much smaller than across the sample (e.g. corporate-pension indicator SD 0.152 overall vs 0.087 within cliques). [[investor-heterogeneity-and-liquidity]] (Chan-Cheng-Hameed) shows flows co-move more among funds in the same churn tercile. [[working-paper-2515]] (Ozdagli-Ryfe) shows a common asset manager produces similar portfolios and trades. [[statistically-validated-network-of-portfolio-overlaps-and-systemic-risk-pmc]] (Gualdi et al.) supplies the BiCM null. [[nber-working-paper-series-12]] is Koijen-Yogo (NBER w21749, demand system).

## What the new sources say

**Crane-Koch-Michaely (full text read).** "Institutions that belong to cliques are most likely to be dedicated investors and least likely to be quasi-indexers (as classified by Bushee, 1998)." and "institutions within the same clique tend be more similar to each other than they are to institutions outside of their clique across a variety of institutional characteristics... This is particularly true for institutional type indicators." The authors read this as "suggestive of coordination, as investors of the same type may be more likely to interact", and acknowledge the Manski correlated-effects problem: acting similarly "because they have similar information sets". Relevance: type-assortativity in co-holding is already documented, in a clique (not pairwise-horizon) design, with Bushee types (which are built from turnover and concentration). D's fact is the pairwise, continuous-horizon analogue of an existing result.

**Chan-Cheng-Hameed (full text read).** Abstract: "Fund flows are more correlated among funds with similar investment horizon, consistent with correlated demand for liquidity." They measure horizon by churn rate (Gaspar-Massa-Matos) and build a stock-level dispersion measure: "the standard deviation of the churn rate of all institutions holding a stock, scaled by the average churn rate", finding higher dispersion goes with more liquidity and lower volatility of liquidity, with a 2003 tax-reform shock for identification. Relevance: horizon-homogeneity as a source of correlated behaviour is published; also pre-empts pivot B (holder-horizon dispersion) at the liquidity level, flagged for the B investigator.

**Koijen-Yogo (full text read).** Institutional demand is characteristics-based with institution-specific latent demand; institutions differ systematically in how they load on characteristics. Implication for D: if horizon types load differently on size, value, momentum and liquidity, then same-horizon institutions co-hold by construction. The test that matters (horizon proximity predicting similarity of latent demand after characteristics) is not in the paper or any paper I found.

**Gualdi et al. (full text read).** The BiCM null keeps institution and security degrees fixed on average; "the overlap of two portfolios of very different size and diversification" is compared to random allocation of assets of very different popularity. It uses binary holdings, so it removes degree (number of positions) and stock popularity but not weights, characteristics or common managers. They report validated-network structure by institution type (broker, hedge fund, investment adviser, mutual fund, pension, etc.) but do not relate it to turnover. Relevance: BiCM is the right first null, but passing it only shows excess co-holding beyond degree; it does not rule out characteristic or type channels.

**Borochin-Yang, FEDS 2016-088 (fetched, [[finance-and-economics-discussion-series]]).** Classifies institutions by turnover and concentration and notes "the overlap between firms owned by dedicated, transient, long/short horizon, and focused/diversified institutional investors is imperfect but consistent with expectations." Relevance: horizon-class ownership overlap is documented at the firm level as a descriptive regularity.

**Girardi-Hanley-Nikolova-Pelizzon-Getmansky Sherman, JFE 142 (2021) (search metadata only; full text fetch failed).** Cosine similarity of insurer portfolios predicts similar liquidation behaviour; concentration lowers similarity. Provides the template for a dyadic similarity design and a precedent for cosine as the measure, which is a methodological precedent for D, not a pre-emption. ScienceDirect S1386418120300732 (horizon x concentration, "Institutional investor heterogeneity and market price dynamics") was blocked by Cloudflare; only the search snippet is known: similar-horizon investors often differ in concentration. Reliability: snippet-level.

**Audited absence.** Searches run: "determinants of portfolio similarity ... turnover investment horizon dyadic regression 13F" (cut off once, rerun as an extended search), "investors with similar investment horizons hold similar portfolios overlap turnover similarity", and the Girardi et al. title search. No paper found that regresses pairwise portfolio similarity on pairwise horizon or turnover proximity. This is a thin absence (3 searches, no Google Scholar, no 2025-26 SSRN sweep), so it supports "not found" not "not done".

## Evidence synthesis

The fact is directionally unsurprising. Five independent channels each predict a positive correlation between horizon proximity and cosine similarity, and none is controlled in the CME paper as described.

1. Index-tracking geometry. Long-tau (low-turnover) institutions are the diversified quasi-indexers, whose value-weight portfolios converge on the market portfolio, so their pairwise cosine is near 1. Short-tau institutions run concentrated, idiosyncratic books with low cosine to anyone. Horizon proximity then correlates with cosine mainly because the long-horizon pairs are all index-like. A cosine on raw value weights is dominated by mega-caps and mechanically rises with number of positions.
2. Price-drift contamination, which the CME paper itself documents. If tau is computed from value-weight turnover, institutions holding the same volatile or trending stocks inherit the same spurious "turnover" from price changes. Same holdings then produce same measured tau, a direct mechanical link from holdings to horizon. The paper's own finding in item (3) (r = -0.53 collapsing to -0.06 under share-based turnover) shows this contamination is large for the aggregate series, so item (2) should be re-run on share-based tau before anything else.
3. Characteristic-based demand (Koijen-Yogo) and horizon-type preferences (Yan-Zhang; Gaspar et al.): types load on size, liquidity, momentum, so co-holding follows.
4. Bushee-type clustering and shared managers (Crane et al. type assortativity; Ozdagli-Ryfe common manager). In a top-150 13F filer panel, filers belonging to the same fund family or parent are likely to share both strategy and horizon.
5. Sample and inference artefacts. The panel is the top 150 filers (size-truncated), so degree varies little. NW t = 19 is computed on a quarterly series of cross-sectional correlations; each correlation is over about 11,000 dyads that share 150 nodes, and consecutive quarters are almost the same portfolios, so "positive in 50 of 50 quarters" is closer to one persistent structural fact observed 50 times than 50 independent confirmations. The mean 0.158 is also a modest effect: R-squared about 2.5%.

### Position A: mechanical (not a new fact)
Strongest case: the sum of channels 1-4 predicts a positive coefficient of roughly this size without any horizon-specific mechanism. Crane et al. already show type-assortative co-holding; Chan-Cheng-Hameed already show horizon-sorted behavioural correlation; Borochin-Yang show horizon-class ownership overlap; Koijen-Yogo implies characteristic-driven demand differences. A referee can say D restates "institutions of the same type hold similar stocks". The value-weight tau contamination makes the problem worse for this specific paper.

### Position B: genuine (new, non-mechanical fact)
Strongest case: nobody has measured pairwise horizon proximity against pairwise similarity with controls; the BiCM literature (Gualdi) and cosine-similarity designs (Girardi et al.) show similarity is a meaningful object, and a degree- and size-controlled excess similarity concentrated in horizon-proximate pairs would not be implied by type labels alone, because horizon is continuous and Bushee types are coarse (the in-sample classification uses turnover and concentration but within-type horizon variation remains). If horizon predicts similarity within Bushee type, within family, and after active-weight cosine, the residual is a new fact.

## Committed position

D as currently measured is mostly mechanical and should not carry the paper; it can be rescued only as a conditional fact. The load-bearing reason is that the raw correlation of value-weight cosine with value-weight-turnover horizon is confounded by at least three independent, known channels (index-tracking geometry, price-drift contamination of tau, and characteristic/type demand), and the novelty of the unconditional fact is also eroded by Crane-Koch-Michaely (type-assortative co-holding) and Chan-Cheng-Hameed (horizon-sorted comovement). It becomes a defensible stylised fact only if horizon proximity predicts similarity (i) with share-based tau, (ii) after cosine is computed on active weights relative to the market portfolio (or with the top-N mega-caps removed), (iii) with institution fixed effects (dyadic regression with node FE and two-way clustered or dyadic-robust SE), controlling for log AUM distance, number of positions, same Bushee type, same fund family/parent, and (iv) with positive excess in the BiCM-validated link rate for horizon-proximate pairs, and ideally (v) when similarity is measured on Koijen-Yogo latent-demand residuals. My expectation is that the coefficient shrinks by well over half under (i)-(iii); the t = 19 does not survive dyadic clustering at that magnitude.

- **Position:** The 0.158 correlation is largely a mechanical consequence of indexing, drift-contaminated tau and type/characteristic demand; only a within-type, active-weight, share-based-tau residual would be a new fact, and even then it is a motivating fact for pivot A rather than a standalone contribution.
- **Confidence:** medium (about 65% that the residual falls below one third of the raw coefficient; about 35% that a meaningful residual survives all controls). No test was run; this rests on the structure of the measures and adjacent literature.
- **Boundary conditions:** Applies to the CME panel design (top 150 13F filers, value-weight cosine, tau = 63/turnover). A wider filer universe with real degree variation, or fund-level (not filer-level) data, could change the picture in either direction. The absence audit covers three searches and two fetched papers; it does not exclude a 2025-26 working paper.
- **What would change this position:** (a) a run showing the horizon coefficient on active-weight cosine with share-based tau, Bushee-type and family fixed effects retains at least about 50% of its raw magnitude (e.g. about 0.08 or more) under dyadic-robust inference; (b) BiCM validated-link rates rising monotonically in horizon proximity within the short-tau half of the sample (where index-tracking cannot be the cause); or (c) discovery of a paper that already tests it, which would make it non-novel regardless.
- **Evidence weight:** 4 full-text papers read (Crane et al., Chan-Cheng-Hameed, Koijen-Yogo, Gualdi et al.) plus Ozdagli-Ryfe in vault and Borochin-Yang fetched; 2 support partial pre-emption (Crane, CCH), 1 supplies the null (Gualdi), 1 states the demand channel (KY); no direct test of the claim exists in what I found. Girardi et al. and the ScienceDirect paper are snippet-level only.

## Open questions

- Is there a 2024-26 SSRN/arXiv paper on pairwise turnover or horizon similarity and holdings similarity? Only three searches run; Google Scholar and SSRN keyword sweeps were not possible within budget.
- Does tau (value-weight) correlate with holding composition more strongly than share-based tau? Needs the CME data.
- How many of the top 150 filers share a parent or family?
- Weighted BiCM variants (not binary) were not examined; a weighted or fitness-based null would better match cosine on weights.

## Sources

1. [[institutional-investor-cliques-and-governance]] Crane, Koch, Michaely
2. [[investor-heterogeneity-and-liquidity]] Chan, Cheng, Hameed
3. [[nber-working-paper-series-12]] Koijen-Yogo, A Demand System Approach to Asset Pricing
4. [[statistically-validated-network-of-portfolio-overlaps-and-systemic-risk-pmc]] Gualdi et al.
5. [[working-paper-2515]] Ozdagli-Ryfe, Asset Manager Commonality and Portfolio Similarity
6. [[finance-and-economics-discussion-series]] Borochin-Yang, FEDS 2016-088
