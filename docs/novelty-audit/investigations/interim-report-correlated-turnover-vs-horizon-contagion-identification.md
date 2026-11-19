---
title: Interim report — correlated-turnover-vs-horizon-contagion-identification
id: interim-report-correlated-turnover-vs-horizon-contagion-identification
tags:
- investor-horizon-novelty-audit-45a8e3
- locus-correlated-turnover-vs-horizon-contagion-identification
created: '2026-11-19T01:24:31.132099Z'
status: draft
type: interim
deprecated: false
summary: 13F-only horizon peer effect is not identifiable to top-journal standard;
  only shock-based event design on full 13F universe survives; PST common factor and
  style-correlated flows are the decisive confounds.
---

# Interim report: correlated-turnover-vs-horizon-contagion-identification

**Locus question:** Can a horizon peer effect among 13F overlap neighbours be separated from non-peer comovement in turnover (common turnover factor, correlated flows within horizon classes, shared asset managers, corporate events in co-held stocks) and from reflection / exclusion / sampled-network / weak-IV problems, and which design survives?
**Flavor:** dialectical

## What the corpus already said

The corpus holds the full toolkit for both sides but no paper that applies it to institutional trading horizon. Pro-identification: Bramoulle-Djebbari-Fortin [[iza-dp-no-2652]] (intransitivity gives G^2 x instruments, provided correlated unobservables are absent or absorbed by component fixed effects), Georg-Pierret-Steffen [[similar-investors1]] (an IV built from other funds' idiosyncratic redemptions, in money-market funds, with no horizon content). Anti-identification: Angrist [[nber-working-paper-series-4]] (group-mean regressions are mechanical; only manipulated peer characteristics are credible), Caeyers-Fafchamps [[nber-working-paper-series-5]] (exclusion bias, negative, with fixed effects or small pools), Chandrasekhar-Lewis [[econometrics-of-sampled-networks]] (Proposition 3.4: 2SLS with sampled-graph friends-of-friends instruments generically gives E[Zu] != 0), Canen-Chadha [[empirical-challenges-with-peers-of-peers-instruments]] (FoF IVs degenerate in very sparse networks and carry little first-stage information in denser ones; Anderson-Rubin inference and row-scaling adapt). Confound evidence: Chan-Cheng-Hameed [[investor-heterogeneity-and-liquidity]] Table 2: flows of a low-churn fund comove 0.80 with other low-churn funds against 0.12 with funds outside the group (high-churn: 0.98 vs 0.16). Ozdagli-Ryfe [[working-paper-2515]]: shared asset managers raise portfolio and trade similarity, and manager closures give an exogenous drop in commonality.

## What the new sources say

**Pastor-Stambaugh-Taylor, "Do funds make more when they trade more?" (NBER w20700, the JF 2017 paper's working-paper version) [[nber-working-paper-series-15]].** Fetched in full. Turnover has a strong common component: "Average turnover across funds, essentially the first principal component of turnover, is significantly related to three proxies for potential mispricing: investor sentiment, cross-sectional dispersion in individual stock returns, and aggregate stock market liquidity." Category-average turnovers correlate 52-61% across size, value-growth and fee categories (small-cap vs large-cap 59%). A panel regression of fund turnover on the leave-one-out average of other funds' turnover, with fund fixed effects, gives slope 0.65 (t = 8.65). Adding same-category average turnover (stock size, fund size, expense ratio) keeps the sum of slopes at 0.65 and raises R2 "by almost half", so "commonality in turnover is especially high among funds sharing similar characteristics". Two lessons for Pivot A. First, a time fixed effect only removes the average loading on this factor, and the loadings differ by style, so style-neighbours in an overlap network load on it more similarly. Second, PST themselves exclude fund i from its own average "to exclude any mechanical correlation", which is the exclusion-bias point in miniature (leave-out mean) and they have no reflection problem only because they claim no peer causation. Caveat: PST measure turnover from fund-reported mutual-fund turnover (CRSP), not 13F, and the factor reflects funds collectively exploiting mispricing, not imitation.

**Koch-Ruenzi-Starks (RFS 2016, SSRN 1364124).** I could not obtain full text (SSRN returned 403; two other open-copy fetches returned junk or errors). Evidence below is from abstract-level snippets via web search, so treat as weaker provenance. Stocks with high mutual-fund ownership show about twice the liquidity commonality; channels are common ownership and funds' correlated liquidity shocks; stocks held by higher-turnover funds, and funds with own liquidity shocks, show higher commonality; the 2003 fund scandal is used as an exogenous flow shock. Relevance: high-turnover funds trade in a correlated way, and the correlation runs through flows. That is exactly a correlated effect that would load on a turnover-horizon measure and that an overlap neighbour shares.

**Network-IV and shock templates in mutual-fund finance (web-search snippets only; PDFs failed to fetch).** Blocher's "Contagious Capital" (2012; later "Peer Effects in Mutual Funds"; JFM 2016 "Network externalities in mutual funds") uses flows of two-step neighbours as the instrument, with validity needing enough two-step neighbours not connected to the focal fund; it also reports spatial autoregression and a network permutation test. An NBER paper uses 2003 scandal peer-flow shocks, exposure to monetary policy and Morningstar star-threshold RD for fire-sale spillovers. Closest horizon-related search hit: Cella-Ellul-Giannetti (RFS 2013) show short-horizon 13F filers sell more in turmoil, but that is a level-of-horizon response, not horizon convergence. Searches for "horizon peer effect / convergence among 13F neighbours" returned no matching paper (audited absence, two searches plus scholar search; not a proof of absence).

**Fetch hygiene note.** Two vault notes I created by fetch error are irrelevant and should be ignored or removed by the orchestrator: [[nber-working-paper-series-14]] (a migration paper, mis-fetched) and [[the-relevance-of-broker-networks-for-information-diffusion]] with its duplicate "-2". Effective new sources used: one fetched in full (PST), the rest search-level.

## Evidence synthesis

The factual core is that turnover is a heavily common object. PST's first principal component, flow comovement within same-churn terciles (CCH), and KRS's high-turnover-fund correlated trading all say the same thing: funds with similar horizons receive correlated shocks (sentiment, dispersion, liquidity, flows). Overlap neighbours are style neighbours by construction, so the dependent variable (own horizon) and the regressor (neighbour horizon) share a style-specific, time-varying factor. The user's proposed "neighbour horizon from stocks the focal institution does not hold" removes stock-level and event-level channels (a cash-out merger, an index deletion in a co-held name) but not this factor, because the factor is a strategy-level opportunity set and liquidity condition that moves turnover in every stock. Orchestrator data facts (not a vault source): within-institution sd of log tau is 0.55 vs 0.92 total and AR(1) is 0.75. High persistence means the lagged dependent variable and institution fixed effects create Nickell-type bias, and an adaptation rate of 0.06 per quarter is a small coefficient to separate from slow-moving style loadings.

On the network side, the orchestrator's diagnostic (median pairwise cosine 0.03-0.07; top-5 symmetrized network mean degree about 9; 32-42 non-friend friends-of-friends per node, 60-70 at top-10) says intransitivity is abundant, so the Bramoulle rank condition is plausible and the Canen-Chadha dense-network degeneracy is less of a worry than I expected for kNN networks. But that network is a sampled one (top-150 filers, roughly 93-105 per quarter), and Chandrasekhar-Lewis show FoF IVs from sampled graphs are generically invalid. Also the kNN construction is itself a function of holdings, so homophily (Pivot D's own fact: similar horizon implies similar portfolios, mean 0.158) is the link-formation rule: neighbours are chosen partly because their trading style is alike. That makes "influence" and "selection" observationally equivalent without a shock (Angrist: only manipulated peer characteristics are credible).

### Position A: Peer effects in horizon are identifiable
Best case: intransitive triads supply G^2 x instruments [[iza-dp-no-2652]]; peers' idiosyncratic shocks supply exogenous variation (Leary-Roberts template; Georg et al. redemption IV; scandal flows; Ozdagli-Ryfe manager closures, which show that exogenous removal of a link-forming common driver is feasible in institutional data). With quarter and institution fixed effects, factor-by-style interactions, same-manager/same-parent exclusion, and neighbour horizon built from non-held stocks, the residual comovement could be cleanly interpreted. The orchestrator facts on FoF counts make the first stage plausible.

### Position B: With 13F holdings alone the estimate is fragile
Best case: (i) the dependent variable and regressor share the PST/KRS/CCH common-and-style factor, which no stock-level exclusion removes; (ii) overlap links are formed from holdings, so homophily is the null, not an alternative; (iii) leave-out means bias against finding convergence [[nber-working-paper-series-5]], so a null is uninformative and a positive is contaminated; (iv) top-150 sampling invalidates FoF instruments [[econometrics-of-sampled-networks]]; (v) FoF instruments are exactly the kind of lagged style characteristic of neighbours-of-neighbours, which are correlated with the focal's style factor loading (exclusion fails when style clusters are larger than one step). I find (i), (ii) and (iv) decisive for a design without an external shock.

## Committed position

Pivot A, as specified (13F-only overlap network, non-held-stock neighbour horizons, friends-of-friends instruments), is not identifiable to the standard a top finance journal will accept, and I would not build the paper on it. The reason is that the non-held-stock construction cures stock-level mechanical overlap but leaves the strategy-level common turnover factor (PST: sum of slopes 0.65 with category averages adding almost half the R2) and style-correlated flows (CCH 0.80 vs 0.12; KRS), and overlap-network neighbours share style by construction, so correlated effects and homophily-selection fit the data as well as influence. The one design with a chance of surviving is shock-based, not instrument-based: exogenous changes to a neighbour's horizon that are unrelated to style-level conditions, such as the closure/merger/reorganization of a 13F filer or the departure of a PM, studied as an event design with pre-trends, placebo neighbours (future neighbours, non-neighbours matched on style and size) and a style-by-quarter fixed effect. Peers' idiosyncratic flow shocks are second best, because flows mechanically generate turnover and flows are style-correlated, so they must be residualized on style-quarter flows. FoF IV should be reported only as a robustness check with Anderson-Rubin sets, never as the headline. Practical consequence: reposition Pivot A as bounded descriptive evidence (homophily plus an Oster-type or partial-identification bound on the adaptation rate) feeding the ABM calibration (Pivot E), or pair it with a shock design on the full 13F universe (not top-150).

- **Position:** A 13F-only horizon-contagion estimate is not publishable at top-field standard; only a shock/event design on the full 13F universe is credible, and the realistic fallback is descriptive homophily plus bounds.
- **Confidence:** medium (about 70%). Sources fully read: one (PST) plus vault notes; KRS and the mutual-fund network-IV papers are search-snippet level, and I found no existing horizon-peer-effect paper, which is an absence from limited searching.
- **Boundary conditions:** Applies to outcomes defined as institution turnover/horizon with link formation from holdings overlap in US 13F data. If the outcome were a discrete adoption choice (e.g., a policy change) or the network were exogenous (e.g., shared manager assignment), identification would be easier.
- **What would change this position:** (a) A usable exogenous shock count: for example 30 or more filer mergers, closures or PM departures in 2013-2026 with measurable neighbour horizon changes and no pre-trend. (b) Evidence that, after adding style-by-quarter fixed effects and PST-style category averages, the neighbour coefficient survives with sizable first-stage F on a full-universe network. (c) A placebo showing that future or non-held-stock neighbours yield a zero coefficient with the same specification. (d) An existing paper that already does this with credible shocks would flip the novelty verdict, not the identification verdict.
- **Evidence weight:** 1 full-text empirical source (PST) and 6 full-text methodological or related vault notes support the fragility reading; 3 search-snippet sources (KRS, Blocher, scandal-flow paper) support both that shocks exist and that flows are correlated; nothing found that directly demonstrates a horizon peer effect.

## Open questions

- KRS full text (turnover-sorted commonality magnitudes) not retrieved; Blocher / Peer Effects in Mutual Funds details unverified.
- How many 13F filer mergers, closures and PM departures exist among institutions with reliable turnover, and does the full universe change the sampled-network problem (WRDS s34 vs SEC structured 13F data sets since 2013)? Known s34 data-quality problems not researched.
- Whether a PST-style common factor explains most of the observed horizon-proximity/similarity correlation (0.158) is testable with the project's own data and was not run.
- Reflection-with-persistence: dynamic panel (AR 0.75) estimators for a 0.06 adaptation rate were not searched.

## Sources

1. [[nber-working-paper-series-15]] Pastor-Stambaugh-Taylor, Do Funds Make More When They Trade More? (NBER w20700)
2. [[iza-dp-no-2652]] Bramoulle-Djebbari-Fortin
3. [[nber-working-paper-series-4]] Angrist, Perils of Peer Effects
4. [[nber-working-paper-series-5]] Caeyers-Fafchamps, Exclusion Bias
5. [[econometrics-of-sampled-networks]] Chandrasekhar-Lewis
6. [[empirical-challenges-with-peers-of-peers-instruments]] Canen-Chadha
7. [[investor-heterogeneity-and-liquidity]] Chan-Cheng-Hameed
8. [[working-paper-2515]] Ozdagli-Ryfe
9. [[similar-investors1]] Georg-Pierret-Steffen
10. Search-level only (not in vault): Koch-Ruenzi-Starks RFS 2016; Blocher (2012/2016); Cella-Ellul-Giannetti RFS 2013.
