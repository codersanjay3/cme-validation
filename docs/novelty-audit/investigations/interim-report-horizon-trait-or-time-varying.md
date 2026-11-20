---
title: Interim report — horizon-trait-or-time-varying
id: interim-report-horizon-trait-or-time-varying
tags:
- investor-horizon-novelty-audit-45a8e3
- locus-horizon-trait-or-time-varying
created: '2026-11-19T01:24:34.571121Z'
status: draft
type: interim
deprecated: false
summary: Horizon ranks are persistent but within-institution turnover has a large
  common (sentiment/dispersion/liquidity) component; peer-effect work needs quarter
  FE and flow controls and a residual-variance check
---

# Interim report: horizon-trait-or-time-varying

**Locus question:** Is an institution's horizon a near-fixed trait (Parsa; Duarte-Parsa; Crouzet et al.) or does it have a meaningful time-varying part, and what drives it?
**Flavor:** dialectical

## What the corpus already said

Trait side: Parsa defines "intrinsic trading frequency" as a 13F institution fixed effect [[investors-horizon-and-stock-prices]], [[institutional-investors-intrinsic-trading-frequency-and-the]]. Crouzet-Dew-Becker-Nathanson derive equilibrium specialisation by frequency [[a-model-of-multi-frequency-trade]]. Cella-Ellul-Giannetti state: "the churn ratio is very stable for institutions across time, giving us comfort that the trading horizon should be considered as a permanent characteristic" (untabulated) [[investors-horizons-and-the-amplification-of-market-shocks]]. Time-varying side: Chinco-Ye find a stock's short-run volume tilt churns fast (only a 32% chance a top-quintile stock stays in the quintile next month) [[nber-working-paper-series-9]], but that is a stock-level measure, not an institution horizon. Chan-Cheng-Hameed show flows are more correlated among similar-churn funds [[investor-heterogeneity-and-liquidity]], a correlated-shock channel.

Orchestrator data fact (project panel, not a vault source): top-150 13F, share-based horizons, within-institution sd of log tau 0.55 vs 0.92 total, AR(1) 0.75, 147 institutions, 50 quarters.

## What the new sources say

**Pastor-Stambaugh-Taylor, "Do Funds Make More When They Trade More?" (JF 2017; NBER 20700)** [[nber-working-paper-series-16]]. Fund turnover has a large within-fund component that predicts performance: "With fund fixed effects, identification comes from within-fund time variation in turnover... If we drop fund fixed effects, the positive turnover-performance relation weakens to marginally significant." Average turnover across funds fluctuates between 59% and 102% per year (1979-2011), has a 95% correlation with the first principal component of fund turnover, and is significantly related to sentiment, cross-sectional return dispersion and market liquidity ("Funds trade more when sentiment or dispersion is high or liquidity is low"). Turnover sd is 0.438 for all funds, 0.547 for small high-fee funds, 0.379 for large low-fee funds; larger funds have more persistent turnover. Implication: a strong common time component exists and is driven by market conditions, and it is exactly what a peer-effect regression would pick up as spurious convergence. Caveat: this is annual reported fund turnover (CRSP), not 13F-derived.

**Lan-Moneta-Wermers, "Holding Horizon" (JFQA 2024; CFR 15-06)** [[cfr-working-paper-no-15-06]]. Holding-horizon and turnover "are both persistent over time" (own lag explains most variation); the sorted-decile persistence is strong: deciles' deviations from style average move from -2.62 to -1.27 years (bottom) and 4.30 to 3.85 years (top) after 20 quarters. They also say turnover is "a flawed and downward biased proxy" for holding horizon and that turnover captures within-fund time-varying opportunity detection (citing PST). So the cross-sectional rank is highly persistent while turnover has a time-varying skill/opportunity component.

**Clare-Sapuric-Todorovic, manager changes (UK)** [[the-impact-of-manager-changes-on-fund]] and a Bessler-et al.-type persistence piece [[why-is-persistent-mutual-fund-performance-so-difficult-to-achieve]]: manager turnover is documented as a material event that changes holdings and performance. These are weak, indirect evidence for manager change as a driver; I found no paper that quantifies manager change's effect on fund turnover or horizon (see open questions). Tagged as lower authority (conference / working paper, UK sample).

Searches that returned nothing relevant: a variance decomposition of 13F institution turnover into fixed, common-time and idiosyncratic parts; Bushee classification migration statistics (Bushee provides a "permanent" modal classification, which implies migration is common enough to need smoothing; no transition matrix located); post-2022 work on determinants of institutional horizon change. I count this as an audited absence, with moderate confidence that it is real rather than missed.

## Evidence synthesis

The "trait" literature is a statement about levels and ranks: persistent cross-sectional ordering (Parsa fixed effects; LMW decile persistence; Cella et al. stability). None of it says within-institution variation is small or unimportant; Parsa's fixed effect is estimated after controlling for market and portfolio characteristics, which presupposes variation to net out. The "time-varying" literature (PST) shows within-fund turnover is large, volatile, and mostly driven by a common market component (sentiment, dispersion, liquidity). The project's own numbers fit both: within sd 0.55 vs total 0.92 implies within variance share about 36% (0.55^2/0.92^2 = 0.357) and fixed-effect-plus-persistent share about 64%; AR(1) 0.75 means shocks have a half-life near 2.4 quarters.

### Position A: horizon is essentially a fixed trait
Best case: LMW's 20-quarter decile persistence, Cella et al.'s stability, Parsa's fixed effect and the Crouzet et al. specialisation equilibrium all imply the movable component is small relative to the investor-type component, and sorting plus clienteles (flow-driven, fee-driven) pins it. Also, 0.36 within-variance share is partly mechanical measurement noise from quarterly 13F turnover.

### Position B: horizon has a meaningful time-varying part
Best case: PST show within-fund variation is where the economic content lies, is large (average turnover swings 59%-102%) and is explained by observable market conditions; LMW concede turnover's time-varying component; Chinco-Ye show rapid churn at the stock level. AR(1) 0.75 with 36% within variance is not noise-dominated: pure noise would give AR near 0 for the within component.

The dispute is largely definitional. Both sides are right about different moments: ranks are persistent, levels move. What matters for a peer-effect design is the part of within variation that is (i) not common to all institutions (absorbed by quarter fixed effects), (ii) not flow-driven, (iii) not a filer or manager event, (iv) not measurement noise. No source quantifies that residual.

## Committed position

A peer-effect study is worthwhile only as a within-institution, quarter-fixed-effect design, and the movable component is real but probably much smaller than the headline 36% within variance: most of that is a common market factor (PST: sentiment, dispersion, liquidity), flows and measurement noise. The load-bearing reason is that the only quantified time variation in the literature (PST) is dominated by a common component, which would produce mechanical "convergence" with no social transmission, so identification must come from idiosyncratic, peer-specific deviations after removing quarter effects. The trait literature does not refute Pivot A, because it is silent on idiosyncratic within-institution variance; but no source shows that this residual is large, so the paper must report its size first.

- **Position:** Horizon has a sizable but mostly common/flow-driven time-varying component; peer-effect work is worthwhile only if the idiosyncratic residual after quarter fixed effects, flows and filer events is shown to be economically large.
- **Confidence:** medium (about 60%) that a usable idiosyncratic residual exists; high (about 85%) that quarter fixed effects are mandatory.
- **Boundary conditions:** applies to 13F quarterly turnover for large filers; the evidence base is mutual-fund and annual-turnover (PST) plus ranks (LMW), not 13F quarterly within-filer variance decompositions. Outside large US filers, no evidence.
- **What would change this position:** a variance decomposition of the project panel with institution FE, quarter FE and flow/AUM controls leaving under about 10% of total variance of log tau (or residual AR(1) near 0) would flip it toward trait and make Pivot A not worth pursuing; residual sd of log tau above about 0.3 with AR near 0.5 would raise confidence. Evidence that manager changes or filer mergers explain most large jumps would shift the paper to an organisational-event design.
- **Evidence weight:** 2 empirical papers on fund-level time variation/persistence (PST, LMW), 2 weak trait statements (Cella et al. untabulated; Parsa FE), 1 equilibrium model, 2 low-authority manager-change papers; zero direct 13F variance decomposition.

Concrete controls: institution FE; quarter FE (and ideally quarter x institution-type FE, e.g. Bushee type or AUM tercile); lagged own tau; net flows and AUM growth (flow-induced turnover), lagged performance; filer-reorganisation flags (CIK merger, AUM jumps above about 50%, entry/exit of managers' holdings in the 13F); share-based not value-weighted tau (Gaspar-Massa-Matos churn removes the price term N*dP; the project's value-weight contamination finding is consistent); winsorise log tau; drop quarters with filer events.

## Open questions

- No located variance decomposition of 13F institution turnover into FE / common time / idiosyncratic parts; the project's own data can supply it.
- No located paper quantifying manager-change effects on turnover or horizon; Bushee classification migration rates not found.
- Chan-Cheng-Hameed already define holder churn dispersion (STDCR) and link it to liquidity and volatility of liquidity: relevant to the locus B novelty audit, flagged for that investigator.
- SSRN abstract pages failed to fetch; Cremers-Pareek persistence not read directly. Source budget used: 4 new fetches of 7 (PST, LMW, Clare et al., Bessler-type), remaining budget unspent because further searches found no direct hit.

## Sources

1. [[nber-working-paper-series-16]] Pastor, Stambaugh, Taylor, Do Funds Make More When They Trade More?
2. [[cfr-working-paper-no-15-06]] Lan, Moneta, Wermers, Holding Horizon
3. [[the-impact-of-manager-changes-on-fund]] Clare, Sapuric, Todorovic
4. [[why-is-persistent-mutual-fund-performance-so-difficult-to-achieve]]
5. Corpus: [[investors-horizon-and-stock-prices]], [[institutional-investors-intrinsic-trading-frequency-and-the]], [[a-model-of-multi-frequency-trade]], [[investors-horizons-and-the-amplification-of-market-shocks]], [[nber-working-paper-series-9]], [[investor-heterogeneity-and-liquidity]]
