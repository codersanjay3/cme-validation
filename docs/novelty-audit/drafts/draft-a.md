# Horizon Contagion: A Novelty Audit and Pivot Plan for "Chronotypic Market Ecology"

**Executive summary.** The single most defensible pivot is Pivot A, recast and tightened: a paper that estimates, for the first time, an identified peer effect in institutional investment horizon through portfolio-overlap networks. Call it "horizon contagion." The estimand is open. Across roughly eighteen search framings and a further adversarial sweep, no paper uses a portfolio-overlap or social network to estimate a peer effect whose outcome is an institution's own turnover, holding period or horizon; institutional peer-effect papers study what is held, bought or flowed, and every paper with trading activity as the peer outcome is about retail investors [1], [2], [3], [4], [5], [6]. The design the current draft proposes (neighbour horizons from non-held stocks plus friends-of-friends instruments on a top-150 sample) is not credible on its own, because turnover carries a strong style-level common component [7], horizon-similar funds receive correlated flows [8], and friends-of-friends instruments built from a sampled network are generically invalid [9], [10]. The paper therefore has to be built on manager-level shocks to neighbours (bereavements, deaths, departures, retirements), with the Liu et al. (2023) bereavement design as the template [11], on the full SEC 13F universe that the free SEC data sets now make available [12], [13], with share-based horizons, style-by-quarter fixed effects and future-neighbour placebos, and with friends-of-friends instruments demoted to robustness [14]. Strategic-complementarity theory gives the paper a signed, falsifiable prediction: because the value of short-horizon information depends on whether others trade on it [15], [16], [17], short horizons should spread between neighbours, and possibly tip.

Every empirical result the current paper headlines is pre-empted, mechanical or a replication, so none can carry the pivot. Holder-horizon dispersion and liquidity is published at JFQA [8], and its appendix already reports that dispersion lowers return volatility net of liquidity [18]; a Chinese 2026 paper links holder-horizon homogeneity to left-tail systemic risk [19]. Price-drift-adjusted turnover has been the standard holdings-based horizon since 2005 [20], [21]. Horizon homophily in co-holding is largely implied by index geometry, drift-contaminated horizons and type-based demand [22], [23]. A network ABM with endogenous horizon adaptation is novel only in a narrow, calibrated form [24], [25]. These pieces become supporting sections: dispersion (B) becomes the consequence test, the ABM (E) becomes a calibrated consequence model whose adaptation rate is the estimated peer coefficient rather than an assumed 0.06, homophily (D) becomes a conditional motivating fact, and drift contamination (C) becomes a footnote plus a data correction.

The paper fits Review of Finance (2024 impact factor 8.4) first, then Management Science (4.9) and JFQA (4.1 in the 2025 release), with Journal of Banking and Finance and Journal of Financial Stability as the next tier [26], [27], [28], [29]. The verdicts are summarised below.

| Pivot | Verdict | Closest papers | What would be novel |
|---|---|---|---|
| A. Horizon contagion | Open as estimand (about 70% confidence) | Pastor-Stambaugh-Taylor turnover commonality; Hong-Kubik-Stein; Pool-Stoffman-Yonker; Blocher; Chen et al. (2021) co-holding peer design; Escobar-Pedraza (retail) | Shock-identified peer effect in institutional horizon on the full 13F universe |
| B. Holder-horizon dispersion | Mostly pre-empted | Chan-Cheng-Hameed (JFQA 2022) and its appendix; Chen-Lu-Qin (2026, China); Greenwood-Thesmar | US crash/fragility horse race and relative absorption in stress, as a section |
| C. Price-drift contamination | Pre-empted | Gaspar-Massa-Matos (2005); Yan-Zhang (2009); Chan-Cheng-Hameed share-based robustness | Footnote plus the 2022Q4 unit-break correction |
| D. Horizon homophily | Mechanical as measured | Crane-Koch-Michaely; Chan-Cheng-Hameed flow comovement; Gualdi et al. null | Conditional residual fact motivating A |
| E. Adaptive-horizon ABM | Novel only in specific form | LeBaron (2001); Oldham (2019); Li-Nishimura-Men; Li-Li-Sun | Adaptation rate estimated from A, tested out of sample, as a section |

## 1. Where the Current CME Paper Stands

### 1.1 The asset worth keeping is the question, not the results

The Chronotypic Market Ecology paper asks a good question badly. Its model assumes that horizons adapt toward network neighbours' horizons at a rate of 0.06 per period, and its central claims (temporal echo chambers, compressed horizon diversity) follow from that assumption. The empirical section never estimates the assumption. That gap is the pivot. If institutions' horizons do move toward those of their portfolio neighbours, the 0.06 parameter is an estimable peer coefficient, and the model's consequences become testable rather than illustrative. The project's own data say there is something to estimate: the within-institution standard deviation of log tau is 0.55 against a total of 0.92, with an AR(1) of 0.75 across 147 institutions and 50 quarters, and after institution and quarter fixed effects 33% of the variance of log tau remains, while quarter fixed effects alone explain only about 2%. That is above the roughly 10% kill threshold an earlier audit set for a peer design [30], and it means the market-wide common component that dominates mutual-fund turnover in Pastor, Stambaugh and Taylor is small in this panel [7]. The remaining threat is style-level commonality, not market-wide commonality, which is precisely what a style-by-quarter fixed effect is built to absorb [14].

The network is also usable. In the project's own data, the top-5 nearest-neighbour overlap network has about 100 institutions per quarter, median pairwise cosine similarity of 0.03 to 0.07, and every node has a median of 32 to 42 friends-of-friends who are not friends. Bramoulle, Djebbari and Fortin show that such intransitive triads are what identify endogenous peer effects in a linear-in-means network model [31], so the structural precondition for network identification holds. What fails is the sampling, not the geometry: a top-150 filer network is a sample of the 13F universe, and Chandrasekhar and Lewis show that two-stage least squares with friends-of-friends instruments on a sampled graph generically violates the exclusion restriction [9]. The pivot therefore inherits a good network shape and must replace a bad network sample.

### 1.2 What does not survive

Four results in the current draft cannot be carried forward as findings.

First, the aggregate horizon-diversity result is not a result. The paper itself reports that the correlation between its diversity index and VIX (r = -0.53) vanishes to r = -0.06 when turnover is computed from share changes, so it was price drift. The project's own data add a second problem: the SEC switched 13F market values from thousands to dollars for filings from January 3, 2023, which produces a 1000x jump at 2022Q4 in the project cache, so the reported 2022Q4 minimum of 1.021 is an artefact (1.918 after rescaling) and the value-weighted correlation with VIX moves from -0.526 to -0.641. The SEC's data documentation confirms the unit rule [13]. Correcting the unit break strengthens a correlation that is already known to be drift; neither number should appear as a finding. The interpretive point matters for referees: a paper that reports a statistic later shown to be contaminated twice over, once by price drift and once by a unit change, will be read as a paper whose data pipeline is untested. The pivot must lead with a rebuilt, share-based, unit-consistent panel.

Second, the stock-level dispersion slope (-0.011, t = -2.4) replicates an existing appendix table. Chan, Cheng and Hameed's Internet Appendix Table IA1 regresses daily return volatility on lagged cross-holder churn dispersion with liquidity controls and finds coefficients between -0.024 and -0.057 in seven of eight specifications, with one insignificant estimate of -0.012 (t = -0.89), over 1982-2016 and 2000-2016 [18]. The current paper's slope has the same sign, a smaller magnitude and a weaker sample (survivors only, no CRSP) [32].

Third, the simulated friction channel has the wrong sign. The model says more horizon diversity raises volatility through cross-horizon friction. Two independent empirical estimates say the opposite: the appendix table above [18] and the current paper's own stock-level slope. Simulation results with the opposite sign appear in the ABM literature (LeBaron finds mixed short and long horizon populations raise return variability [25]), but FMH-based ABMs find that horizon diversity stabilises [33], [34], and the empirical record sides with stabilisation [8]. The friction channel should be withdrawn or replaced by a calibrated liquidity channel.

Fourth, the homophily coefficient (kappa-hat = 0.158, positive in all 50 quarters, Newey-West t = 19) is mostly mechanical as measured. Value-weight cosine similarity is dominated by mega-caps, long-horizon institutions are diversified quasi-indexers whose portfolios converge on the market, drift-contaminated tau links holdings to measured horizon directly, and characteristic-based demand makes same-type institutions co-hold by construction [22]. The t-statistic overstates information because consecutive quarters observe nearly the same dyads [22].

### 1.3 Committed reading

The CME paper is a question-generating paper, not a result-carrying one. Its value is that it names an unestimated parameter (the horizon adaptation rate), supplies a network on which to estimate it, and comes with a model that can translate the estimate into market consequences. The Fractal Market Hypothesis framing should be demoted from thesis to motivation. The FMH literature that exists is mostly simulation and descriptive time-series work [33], [34], and the journals that clear the user's impact-factor bar reward identified estimands over frameworks [26]. This is an inference from the journals' revealed publication patterns rather than a sourced statement, but it is consistent with every closest paper in this audit being an identified empirical paper.

## 2. Literature Map

### 2.1 Strand (a): horizon heterogeneity, market stability, the FMH and heterogeneous-horizon ABMs

Theory treats horizon heterogeneity as an equilibrium object, not a parameter. Crouzet, Dew-Becker and Nathanson build a noisy rational-expectations model in which investors acquire information and trade at a continuum of frequencies, specialise endogenously, coexist and profit from each other [35]. Parsa's thesis models short-horizon informed traders as imposing a negative informational externality on long-term investors and estimates an institution fixed effect in trading frequency from 13F data [36]. Cespa and Vives show that when traders differ in trading horizons, prices reflect higher-order expectations and the market can sit in a low-liquidity equilibrium in which informed investors do not supply liquidity [17].

The most important theoretical strand for the pivot is the one the current draft does not cite: strategic complementarity among short-horizon traders. Froot, Scharfstein and Stein show that short-horizon speculators may herd on the same information because the value of information to a short-horizon trader depends on whether other traders act on it, producing multiple, informationally inefficient equilibria [15]. Chamley shows a related complementarity in information acquisition with short-term trades, with multiple equilibria and trading frenzies [16]. In all three papers horizon is exogenous [15], [16], [17]. No source makes the next step, but these results jointly imply it: if the payoff to a short horizon rises with the share of short-horizon traders an institution trades alongside, then an institution's best-response horizon should move toward its neighbours' horizons, and the response may be nonlinear because multiple equilibria imply tipping [15], [16]. That is a signed, testable prediction for Pivot A, and it is the theoretical spine the pivot lacks today.

The ABM literature has endogenous horizons but not network adaptation. LeBaron's agents differ in lookback horizon, and wealth-based replacement makes the horizon distribution evolve; mixed populations raise return variability [25]. Li, Nishimura and Men build an FMH ABM in which stability rises as the structure moves from uniformity to diversification, with a caveat that more diversity need not bring more stability when the maximum horizon is finite [33]. Li, Li and Sun find greater horizon divergence makes markets more stable and crashes occur when the divergent structure shrinks [34]. A JEBO 2022 switching model finds longer horizons reduce the fraction adopting the strategy and stabilise [37]. A PLOS ONE paper calibrates two-agent heterogeneous-horizon models to index series and argues horizon heterogeneity is crucial for long memory [38]. Oldham's 2019 ABM, read in full, keeps horizon as a fixed class (memory weight 0.95 for long-term agents, 0.05 lower for short-term) and rewires links on performance toward class-specific "Oracles" [24].

Committed reading: strand (a) supplies the sign prediction for Pivot A (positive peer effect, possibly with tipping) and splits on the sign of diversity's effect on stability, with the FMH ABMs on the stabilising side and LeBaron on the destabilising side. No paper in this strand estimates how horizons adapt.

### 2.2 Strand (b): institutional horizons from 13F turnover and their effects

The canonical horizon measure is Gaspar, Massa and Matos's churn rate, which values share changes at current prices and subtracts the passive price change on prior holdings, so price drift is removed from the numerator; the measure ranges over [0, 2], [20]. Yan and Zhang use the same drift-adjusted numerator with the minimum of buys and sells to strip investor cash flows, and show short-term institutional ownership subsumes the return predictability of total ownership [21]. Cella, Ellul and Giannetti show short-horizon institutions sold almost 21% of their holdings around the Lehman bankruptcy against 7% for long-horizon institutions, with larger price drops and reversals in stocks they held [39]. Glossner, Matos, Ramelli and Wagner find that in the 2020 COVID crash stocks with more institutional ownership did worse, mitigated by long-term, passive and foreign ownership, with retail investors identified as liquidity providers [40]. Parsa finds stocks held by high-frequency institutions have higher volatility, and the lowest-frequency quintile earns about 6 percentage points a year more [36].

On whether horizons move, the evidence divides by moment. Lan, Moneta and Wermers show decile rankings of fund holding horizon remain identical 20 quarters after formation, with the shortest-horizon decile's excess holding period moving from -2.62 to -1.27 years and the longest from 4.30 to 3.85 years [41]. Pastor, Stambaugh and Taylor show average fund turnover fluctuates between 59% and 102% per year from 1979 to 2011, has a 95% correlation with the first principal component of fund turnover, and rises with sentiment, return dispersion and illiquidity [7]. Ranks persist while levels move [30].

Committed reading: strand (b) is entirely about the level of short-horizon ownership as a cause of price outcomes. It treats horizon as a predetermined characteristic of the investor. Nobody in this strand asks what causes an institution's horizon to change, which is the open flank Pivot A attacks.

### 2.3 Strand (c): dispersion of the ownership base

Chan, Cheng and Hameed (JFQA 2022) define STDCR, the cross-holder standard deviation of churn scaled by mean churn, and show that more heterogeneous holder horizons go with more liquidity and lower liquidity volatility, using the 2003 dividend tax reform as an exogenous shock; flow-induced trading has a larger price impact in low-heterogeneity stocks [8]. Their mechanism is correlated liquidity demand: flows of a low-churn fund comove 0.80 with other low-churn funds against 0.12 with funds outside the group, a difference of 0.68 with t = 9.58 [8]. Their appendix reports the volatility result discussed in Section 1.2 [18]. Chen, Lu and Qin (Foreign Economics and Management, 2026) show that stock-level trading-horizon homogeneity among Chinese institutional holders, defined following Chan-Cheng-Hameed, raises left-tail systemic risk through liquidity-shock and order-imbalance channels [19]. Greenwood and Thesmar's fragility measure, the quadratic form of owner weights on the covariance of owners' flow shocks, is the benchmark any dispersion measure must beat [42].

Committed reading: the dispersion-to-liquidity and dispersion-to-volatility links are published in the US, and the dispersion-to-tail-risk link is published for China. What is left is a US crash and fragility horse race against Greenwood-Thesmar and a within-stock absorption test [32]. That is a section.

### 2.4 Strand (d): common ownership, overlap networks, connected stocks, fire sales

Coval and Stafford show that funds in large outflows cut existing positions, creating price pressure in commonly held stocks that reverses, and that investors trading against constrained funds earn liquidity-provision returns [43]. Anton and Polk show shared active mutual fund ownership forecasts excess return correlation, with the 2003 fund scandal giving exogenous variation [44]. Greenwood and Thesmar show fragility from correlated owner flows predicts volatility [42]. Gualdi and coauthors build a statistically validated 13F overlap network against a bipartite configuration model null for 1999-2013 and find the share of validated links rose before the 2007-08 crisis and peaked during it [45]. Blocher shows flows spill over across funds linked by common holdings, with a network externality 32% to 92% as large as lagged own flows [4]. Georg, Pierret and Steffen show money market funds avoid issuers whose other investors hold similar portfolios, identified with other funds' idiosyncratic redemptions [46]. Massa, Schumacher and Wang show funds with large exposure to stocks held by a merging asset manager avoid those stocks after the announcement [47], and Lewellen and Lowry show merger-based common-ownership designs are dominated by the BlackRock-BGI event [48].

Committed reading: overlap networks are an established object for transmitting flows, prices and fire sales. They have never been used to transmit a behavioural trait such as horizon. Strand (d) also hands Pivot A its main methodological warnings: merger shocks change neighbours' trading directly [47] and are timing-confounded [48].

### 2.5 Strand (e): peer effects, herding and contagion in institutional trading

Institutional peer effects are well documented in what institutions hold and trade. Hong, Kubik and Stein find a fund's holding of a stock rises about 0.22 percentage points when same-city, other-family managers raise theirs by one point (differential 0.2172, t = 12.07) [2]. Pool, Stoffman and Yonker find neighbourhood-connected managers hold and trade more similar portfolios [3]. Gerritzen, Jackwerth and Plazzi find hedge fund managers with a shared prior employer invest more similarly, with the joint effect accounting for up to two thirds of the difference in investing behaviour [49]. Chen Guojin and coauthors (China Industrial Economics 2021) use Louvain communities in the institutional holdings network to estimate a peer effect in bubble-riding [50].

Turnover-as-outcome peer effects exist only for retail investors. Escobar and Pedraza use quasi-random classroom assignment to show exposure to successful peers raises new investors' trading frequency [5]. Heimer links sociability to active household trading in survey data [51]. Gelman, Hirshleifer, Levi and Reiter-Gavish use 131,003 Israeli retail accounts and soccer-driven social interaction to show interaction raises trading-volume sensitivity to past trades [6]. Liang, Wu and Yin list herding among the drivers of Chinese fund turnover, but in the trade-direction sense, without a peer-turnover regression [52].

The method literature is the referee's checklist. Bramoulle, Djebbari and Fortin give network identification through intransitivity [31]; their 2020 survey classifies responses to correlated effects into random peers, random shocks, structural endogeneity and panel data, and warns that friends-of-friends instruments fail when the network is mismeasured or sampled [10]. Angrist shows outcome-on-group-mean regressions are vacuous and only manipulated peer characteristics are credible [53]. Canen and Chadha show friends-of-friends instruments degenerate in sparse networks and are weak in dense ones, and recommend Anderson-Rubin inference [54]. Leary and Roberts instrument peers' policies with peers' idiosyncratic return shocks and find a one-standard-deviation change in peer leverage moves own leverage about 11% [55]. Liu, Sulaeman, Shu and Yeung use 304 fund-manager parental deaths to show bereaved managers behave like quasi-indexers [11].

Committed reading: strand (e) is the clearest evidence that Pivot A is open. The ingredients (institutional network peer effects, peer effects in trading frequency, network IV methods, manager-level shocks) all exist; the combination does not [1].

### 2.6 Strand (f): measuring horizons from holdings, and contamination

Drift adjustment is standard. The Gaspar-Massa-Matos numerator equals the absolute share change valued at the current price, so passive drift survives only in the value-weighted denominator [20]. Yan and Zhang adopt it [21]. Chan, Cheng and Hameed use it and also report a price-free share-based turnover robustness [32]. Lan, Moneta and Wermers argue that inverse turnover is "a flawed and downward biased proxy" for holding horizon, and that holding horizon and turnover are both persistent yet have at most marginal explanatory power for each other [41]. On data integrity, the SEC 13F data sets cover July 2013 to August 2026 as filed, without accuracy guarantees [12], and the market-value field moved from thousands to dollars on January 3, 2023 [13].

Committed reading: the current paper's contamination finding corrects its own non-standard measure (tau = 63 / value-weight turnover). It is not a contribution, but the unit break is a live hazard for anyone using the free SEC files, and the pivot must use both a churn-based and a holding-period-based horizon because Lan-Moneta-Wermers show they are different objects [41].

### 2.7 Strand (g): homophily in investor networks

Golub and Jackson show that under averaging (DeGroot) updating, homophily slows convergence to consensus while density does not, whereas shortest-path diffusion speeds with density and ignores homophily [56]. Crane, Koch and Michaely find institutions in co-holding cliques are most likely Bushee-dedicated and least likely quasi-indexers [23]. Gualdi and coauthors supply the configuration-model null that controls for portfolio size and stock popularity [45]. The Bramoulle-Djebbari-Fortin survey notes structural approaches that model network formation with observed and unobserved homophily jointly with outcomes [10].

Committed reading: homophily in co-holding is partly documented by type [23], and it is the core identification problem for Pivot A rather than a standalone fact: if links form on horizon similarity, selection mimics influence [14]. Golub-Jackson is the formal bridge from homophily to the CME "echo chamber" claim, and it gives the ABM an analytic convergence-speed result instead of a purely simulated one [56].

## 3. Novelty Audit of the Five Candidate Pivots

### 3.1 Pivot A: horizon contagion

**Has it been done?** Not as an estimand. A search across about eighteen framings (fund families, manager moves, consultants, China and Europe, hedge-fund strategy contagion, holding-period herding, 2023-2026 SSRN and arXiv, overlap-network by horizon) found no paper regressing an institution's own turnover or horizon on its network neighbours' horizons with an exclusion restriction [1]. The follow-up sweep of the Liang-Wu-Yin abstract, the Chinese network-peer literature and manager-mover designs found nothing that overturns this, raising confidence to about 70% [52], [50].

**Closest papers.** (1) Pastor, Stambaugh and Taylor: a regression of fund turnover on the leave-one-out average of other funds' turnover has slope 0.65, and adding same-category averages keeps the sum of slopes at 0.65 while raising R-squared by almost half [7]. This is commonality, not influence; it uses no network, no exclusion rule and no instrument, and the authors exclude the focal fund "to exclude any mechanical correlation" [7]. It is the single most important alternative explanation. (2) Hong-Kubik-Stein, Pool-Stoffman-Yonker, Blocher and Gerritzen et al., which share the network-peer architecture but have holdings, trades, flows or returns as the outcome [2], [3], [4], [49]. (3) Chen et al. (2021), which applies a co-holding-community peer design to bubble-riding in China [50]. (4) Escobar-Pedraza, the cleanest identification precedent for a peer effect in trading frequency, but for retail investors [5]. (5) Liang-Wu-Yin, which studies Chinese fund turnover drivers including herding, at abstract level only [52].

**Residual risk.** One unread lead remains: a 2025 SSRN paper by MacDonald (5692342) on whether investors are influenced by the trades of other investors in US institutional holdings, flagged by the adversarial sweep from its title alone. Its title suggests trade-direction peer effects, the established estimand, but it must be read before any novelty claim is submitted. Chinese-language fund-turnover work is only partly searched [1].

**Novel and defensible increment.** The increment has three parts, and all three are needed. The outcome is new: institutional horizon, not holdings or flows. The identification is new for this outcome: exogenous manager-level shocks to a neighbour's horizon, on a full-universe network, with style-by-quarter effects, rather than outcome-on-mean regressions [14], [53]. The theory is new in application: strategic complementarity in short horizons [15], [16] predicts a positive peer coefficient and possible tipping, so the paper tests a model rather than reporting a correlation. The paper should be framed as "a known network-peer design applied to a new estimand, identified with a new shock," not as "the first peer effects among institutions" [1].

**Verdict:** open; the defensible lead.

### 3.2 Pivot B: holder-horizon dispersion, fragility and absorption

**Has it been done?** Largely. Chan, Cheng and Hameed publish the dispersion measure, the drift-adjusted churn, the liquidity outcomes, the flow-comovement mechanism, the flow-induced trading test and the tax-reform identification [8], and the appendix gives the volatility sign [18]. Chen, Lu and Qin pre-empt the tail-risk outcome for Chinese A-shares [19].

**Closest papers.** Chan-Cheng-Hameed [8], [18]; Chen-Lu-Qin [19]; Cella-Ellul-Giannetti for the level baseline [39]; Greenwood-Thesmar for flow-covariance fragility [42]; Glossner et al. for the stress-episode setting [40].

**What evidence says about absorption.** The strong version (long-horizon holders buy what short-horizon holders sell within the same stock) is not supported. In 2020Q1 retail investors provided liquidity while institutions net-sold [40]; long-horizon institutions also sold around Lehman, just less (7% against 21%) [39]. Chan-Cheng-Hameed conjecture that "long-horizon funds can provide liquidity to active mutual funds during fire sales" but never observe who buys [8]. The defensible claim is relative absorption: long-horizon holders sell less than composition predicts in stocks with heavy short-horizon selling [32].

**Novel and defensible increment.** A US horse race of dispersion against Greenwood-Thesmar fragility for crash risk and negative skewness, plus a relative-absorption test in 2008Q3-Q4 and 2020Q1 instrumented with Coval-Stafford flow-induced trading [32], [43], [42]. **Verdict:** a section, not a paper (about 80% confidence after the Chinese pre-emption [19]).

### 3.3 Pivot C: price-drift contamination of turnover

**Has it been done?** Yes, by construction of the standard measure. The Gaspar-Massa-Matos churn rate subtracts the passive price change from the numerator [20]; Yan-Zhang use it [21]; Chan-Cheng-Hameed add a share-based robustness [32]; Lan-Moneta-Wermers go further and argue turnover is a biased proxy for holding horizon regardless [41].

**Novel and defensible increment.** None at journal level. The CME finding demonstrates why the standard measure exists. The one genuinely useful by-product is the SEC unit break at January 3, 2023 [13], which matters for any researcher using the free data sets [12], but this is a data note. **Verdict:** pre-empted; footnote plus correction.

### 3.4 Pivot D: horizon homophily in co-holding

**Has it been done?** No paper regresses pairwise portfolio similarity on pairwise horizon proximity, but the fact is mostly implied by known channels [22]. Crane, Koch and Michaely show type-assortative co-holding in cliques [23]; Chan-Cheng-Hameed show horizon-sorted flow comovement [8]; Pool-Stoffman-Yonker supply the pairwise similarity design run in the other direction (ties to similarity) [3]; Gualdi et al. supply the null that the raw cosine fails to address [45].

**Novel and defensible increment.** A residual fact: horizon proximity predicts similarity on active weights relative to the market, with share-based horizons, dyadic fixed effects, same-family and same-type controls, and excess configuration-model-validated links among horizon-proximate pairs, ideally within the short-horizon half of the sample where index geometry cannot drive it [22], [45]. **Verdict:** mechanical as measured; a motivating fact for A at best. Its more important role is negative: it documents the selection channel that Pivot A's shock design must defeat.

### 3.5 Pivot E: ABM with endogenous horizon adaptation

**Has it been done?** Endogenous horizons have: LeBaron's horizons evolve through wealth-based selection [25], and Crouzet et al.'s through information specialisation [35]. Network ABMs with horizon classes have: Oldham's horizons are fixed and links rewire on performance [24]. FMH ABMs with horizon diversity have [33], [34]. Calibration of heterogeneous-horizon ABMs to index series has [38]. What has not been found is an ABM in which links form on horizon similarity, horizons adapt toward neighbours, and the adaptation rate is set to an estimated peer coefficient and tested out of sample [13], [24].

**Novel and defensible increment.** The bridge is simple. Under DeGroot updating, x(t+1) = (1 - a) x(t) + a W x(t) with row-normalised W, the linear-in-means coefficient on neighbours' average horizon equals the adaptation weight a [13], [56]. Pivot A's estimate replaces the assumed 0.06. The model then needs a liquidity or absorption channel whose strength is disciplined by the Pivot B estimates, because the current friction channel is contradicted by data [18], [8]. The out-of-sample test is whether the calibrated model, fed the network and horizons to 2019Q4, predicts the cross-section of holder-horizon dispersion and fragility in 2020 and 2022. **Verdict:** novel only in this specific form (about 70% confidence [24]), and publishable alone only in ABM journals that fall below the impact-factor threshold [57], [58]. It belongs in the paper as the consequence model.

### 3.6 Cross-pivot reading

The audit's most important pattern is that three independent lines of evidence (dispersion, homophily, measurement) converge on the same conclusion: every result the current paper headlines is pre-empted, mechanical or a replication [32], [22], [20]. Independent convergence is itself a finding. It means the pivot cannot be an incremental rewrite; it needs a new estimand, and A is the only candidate whose estimand is open.

## 4. Recommended Pivot

### 4.1 The paper

**Working title:** "Horizon Contagion: Peer Effects in Institutional Investment Horizons." **One-sentence contribution:** institutions' trading horizons move toward the horizons of their portfolio-overlap neighbours, identified from manager-level shocks to those neighbours, and this contagion compresses the horizon diversity of stocks' ownership bases, raising fragility.

The paper has four empirical parts and one model part.

1. **Fact.** A variance decomposition of institutional horizon on the full 13F universe into institution, quarter, style-by-quarter and idiosyncratic components. The project's own data put the residual after institution and quarter effects at 33% on the top-150 panel; the full-universe number is the paper's first table. This answers the trait objection before it is raised [30], [41], [36].
2. **Estimate.** A shock-identified peer coefficient: the response of institution i's horizon to an exogenous horizon shift at an overlap neighbour j, with both sides' horizons computed on mutually non-held stocks (Section 6) [14], [11].
3. **Mechanism.** Tests of the strategic-complementarity predictions: the coefficient is positive, larger when i's neighbourhood is already short-horizon (tipping), and stronger in less liquid stocks where short-horizon information is more valuable [15], [16], [17].
4. **Consequence.** Stocks whose holder bases are exposed to contagion-driven compression show lower horizon dispersion and, net of Greenwood-Thesmar fragility, higher crash risk and weaker relative absorption in stress [8], [42], [32].
5. **Model.** The CME ABM recast with horizon-homophilous links, an adaptation rate set to the estimate in part 2, a liquidity channel disciplined by part 4, and an out-of-sample test [24], [56].

### 4.2 Why A should lead, and not B

The strongest case against this recommendation is that A is novel only because it is hard to identify, while B is identifiable with existing tools. That case deserves a direct answer, and the answer is asymmetric. A novelty problem cannot be fixed by effort: no amount of better data makes Chan-Cheng-Hameed unpublished [8], and no US crash-risk extension will read as more than an extension of a JFQA paper plus a Chinese replication [19]. An identification problem can be fixed by design: the specific threats to A are named (style-level commonality [7], correlated flows [8], homophily-selection [14], sampled networks [9], weak instruments [54]), and each has a known remedy (style-by-quarter fixed effects, flow residualisation, predetermined networks with exogenous shocks, full-universe data, Anderson-Rubin sets). A also absorbs B: B's best surviving pieces become A's consequence section, so choosing A does not waste B's work, while choosing B wastes A's estimand.

The second argument is economic. Strand (b) shows short-horizon ownership amplifies shocks [39] and raises volatility [36], and strand (c) shows homogeneous holder bases are illiquid [8]. No source states that horizon contagion multiplies these effects, but these results jointly imply it: if horizons are contagious, a shock that shortens a few central institutions' horizons propagates through the overlap network, shortening neighbours' horizons and compressing the holder-horizon dispersion of the stocks they co-hold, which is the state Chan-Cheng-Hameed associate with illiquidity [8] and Chen-Lu-Qin with tail risk [19]. That multiplier is a new object for financial-stability work, and it is what makes A matter beyond a coefficient.

### 4.3 What transfers from CME and what is discarded

Transfers: the question, the network construction (rebuilt on the full universe), the horizon panel (rebuilt share-based), the ABM (recast), the stock-level dispersion regression (repositioned as a replication of Chan-Cheng-Hameed's appendix inside the consequence section [18]), and N-PORT data as a fund-level validation layer. Discarded: the FMH as the headline frame, the friction-channel volatility claim, the 1.31x volatility and 14x fragmentation simulation numbers as findings, the aggregate diversity-VIX result, and kappa-hat as a headline fact.

### 4.4 Forward-looking implications

If the estimate is positive and survives the shock design, three implications follow, and the paper should say so. First, the stability effects of short-horizon ownership documented in crises [39], [40] have a network multiplier that current fragility measures, built from flow covariances [42] and overlap counts [45], do not see. Second, the growth of passive and quasi-index ownership changes the network itself: Liu et al. show even a personal shock can push an active manager toward quasi-indexing [11], so horizon contagion predicts that shifts toward long horizons also spread, which is a testable implication about the passive transition. Third, the result gives agent-based finance something it has lacked: an adaptation parameter estimated from holdings rather than chosen to match return moments [38], [25]. If the estimate is a precise zero, the paper still settles the trait-versus-time-varying dispute for institutional horizons [30] and tells the ABM literature that horizon adaptation should be modelled as performance-driven selection [25] rather than imitation. A precise null is harder to publish at the top of the target list, which is why the variance decomposition and the consequence section must be strong enough to carry a JBF or JFS submission on their own [28], [29].

## 5. Target Journals and Fit

### 5.1 The impact-factor bar and what it hides

The user's threshold (impact factor above 4 to 5) is met by more journals than it seems, and it is a poor proxy for quality. Finance Research Letters, the current target, has an impact factor of 7.1 [59], and International Review of Financial Analysis has 10.2 [60], yet both rank below JFQA and Management Science in most finance assessments. JFQA's impact factor is volatile: 4.1 in the 2025 release [27] but 2.8 in the 2024 release reported by Review of Finance [26]. Management Science is 4.9 in 2024 [26]. The natural ABM outlets fail the bar: JEDC at 1.8 [57] and JEBO at 2.7 [58]. This pushes the paper toward an empirical-led design, which is what Pivot A is.

### 5.2 Fit by journal

| Journal | Impact factor (source) | Fit for horizon-contagion paper | Comment |
|---|---|---|---|
| Review of Finance | 8.4 (2024) [26] | High | Best balance of reach and fit; empirical asset management with theory-motivated tests |
| Management Science | 4.9 (2024) [26], [61] | High | Values networks and peer-effect identification; published Gerritzen et al. on hedge-fund ties [49] |
| JFQA | 4.1 (2025); 2.8 (2024) [27], [26] | High | Published the closest dispersion paper [8]; the consequence section speaks to it directly |
| Review of Financial Studies | 5.4 (2024) [26]; 7.6 (2025, snippet-level) [62] | Medium | Requires the shock design to be clean and the consequence result large |
| JFE / JF | 12 / 9.5 (2024) [26] | Low to medium | Only if the shock design is airtight and the multiplier is economically large |
| Journal of Banking and Finance | 4.0 (homepage); 3.8 (2024) [28], [26] | High | Scope lists asset management, networks and liquidity [28]; safest strong outlet |
| Journal of Financial Stability | 4.1 [29] | High for consequence framing | Policy angle on fragility multipliers [29] |
| IRFA | 10.2 [60] | Medium | Clears the bar easily; broad and high-volume |
| Journal of Corporate Finance | 6.9 [63] | Low | Needs a corporate-outcome angle |
| JIFMIM | 6.0 [64] | Low to medium | Needs an international angle |
| Finance Research Letters | 7.1 [59] | Low for the pivot | Letters under 2,500 words cannot hold the shock design [59] |
| JEDC / JEBO | 1.8 / 2.7 [57], [58] | High topical fit for the ABM alone | Below the threshold |

### 5.3 Committed submission ladder

Submit first to Review of Finance. If rejected on identification grounds, Management Science or JFQA; if on contribution grounds, Journal of Banking and Finance or Journal of Financial Stability with the consequence section promoted. Do not split the ABM into a separate submission until the empirical paper is accepted, because an uncalibrated model is what the field already has [24], [33].

## 6. Identification Strategy and Data Upgrades

### 6.1 Step zero: rebuild the panel

Every pivot depends on a rebuilt panel; this is a precondition, not a contribution [13]. The SEC Form 13F data sets cover July 2013 to August 2026, extracted from the XML portion of filings for every filer, as filed, with an explicit disclaimer that accuracy is not guaranteed [12]. They include share counts, so a share-based horizon immune to price drift can be built without WRDS; the market-value field must be rescaled for filings before January 3, 2023 [13]. Cleaning falls on the user: amendments, CUSIP errors, 13F-NT notices, shared discretion, shares versus principal, puts and calls [13]. The first quarter of the current sample (2013Q2) is not in the data sets [13].

### 6.2 Outcome and network

**Outcome.** Two horizon measures, because they are different objects [41]: the Gaspar-Massa-Matos churn rate built from share changes valued at current prices [20], and a Lan-Moneta-Wermers-style holding horizon from position ages [41]. Log tau from value-weight turnover is retired.

**Network.** A predetermined, lagged (t - 4) overlap network on the full universe, thresholded to stay sparse because a full universe of thousands of filers sharpens the dense-network weakness of friends-of-friends instruments [13], [54]. Report results on raw cosine, active-weight cosine and configuration-model-validated links [45].

### 6.3 The baseline specification and why it is not enough

The baseline regresses the change in institution i's horizon on the lagged average horizon of its overlap neighbours, with neighbour horizons computed only on stocks i does not hold, plus institution fixed effects, style-by-quarter fixed effects, lagged own horizon, net flows and AUM growth, and filer-event flags [30], [14]. It is reported because referees will ask for it, but it is not the identification. Three reasons: neighbours share a style-level turnover factor that no stock-level exclusion removes [7]; horizon-similar institutions receive correlated flows [8]; and links are formed from holdings, so homophily is the null rather than an alternative [14]. Angrist's critique applies with full force to this regression [53], and with AR(1) of 0.75 in the project's own data, the dynamic panel with fixed effects also carries Nickell-type bias [14].

### 6.4 The identifying design: manager-level shocks to neighbours

The headline design is an event study of neighbours of institutions hit by manager-level shocks: deaths and bereavements of portfolio managers, unexpected departures, and retirements. The template is Liu, Sulaeman, Shu and Yeung, who use 304 parental deaths of mutual fund managers from 1999 to 2013 in a difference-in-differences design and find bereaved managers act like quasi-indexers, with lower tracking error and active share, effects stronger for unexpected deaths and single-manager funds [11]. That paper shows the shock moves the focal fund's style; whether it moves turnover is an inference this paper must establish as its first stage. The design follows the "random shocks" route in the Bramoulle-Djebbari-Fortin classification, which is valid even when the network is endogenous provided the shock does not change the network [10], and it follows Leary-Roberts in using a shock to the peer rather than the peer's chosen outcome [55].

The specification has five features.

1. **First stage.** The shock shifts j's horizon. Measure it with the churn and holding-horizon outcomes and require a sizeable first-stage F.
2. **Double exclusion.** Compute j's horizon shift on stocks i does not hold and i's horizon response on stocks j does not hold. This blocks the channel Massa, Schumacher and Wang document, in which neighbours respond to a shocked institution's trades in co-held names directly [47], and it blocks Coval-Stafford price pressure in shared positions [43]. This double exclusion is a proposed design feature, not something any source has implemented.
3. **Fixed effects.** Institution, style-by-quarter and, where feasible, Bushee-type-by-quarter effects [30], [23].
4. **Placebos.** Future neighbours (institutions that become j's neighbours only after the shock), matched non-neighbours of similar style and size, and pre-trends [14].
5. **Event dependence.** Leave-one-event-out estimates and event-clustered errors, because Lewellen and Lowry show a single dominant event can manufacture a treatment effect [48].

Filer mergers and closures are pooled only as a robustness arm and excluding BlackRock-BGI, because mergers change neighbours' holdings directly [47] and the merger sample is timing-confounded [48].

**Mapping shocks to 13F filers** is the main data cost. Manager identities live at the fund level; 13F filers aggregate many funds. N-PORT, which the team already holds, gives fund-level holdings; the CRSP mutual fund database gives manager names and tenure. The cleanest sample is single-manager funds whose sponsor files a 13F dominated by that fund [11].

### 6.5 Supporting identification arms

**Idiosyncratic flow shocks to neighbours.** Following Georg, Pierret and Steffen, use neighbours' idiosyncratic redemptions as instruments [46], residualised on style-by-quarter flows because flows are style-correlated (0.80 within a churn tercile against 0.12 outside) [8] and mechanically generate turnover [14].

**Friends-of-friends instruments as robustness.** The project's own data show 32 to 42 non-friend friends-of-friends per node, so the Bramoulle-Djebbari-Fortin rank condition is plausible [31]. On the full universe the sampled-network invalidity largely disappears [9], but weak-instrument risk remains [54]; report Anderson-Rubin sets, first-stage F and row-scaled adjacency [54].

**Bounds.** If the shock count is thin, report the baseline coefficient with an Oster-type or partial-identification bound, as the identification audit suggests [14].

### 6.6 Kill criteria and decision points

Three pre-committed decision points protect the team from sinking time into a dead end. (1) If the full-universe variance decomposition leaves less than about 10% of horizon variance after institution, quarter and flow controls, abandon A for the B-led paper [30]. (2) If fewer than about 30 usable manager shocks with measurable first stages exist in 2013-2026, rely on the flow-shock arm and target JBF or JFS rather than Review of Finance [14]. (3) If the MacDonald 2025 SSRN paper or any other paper already estimates a turnover peer effect, reposition A as the shock-identified version of an existing estimand.

### 6.7 Consequence and model sections

**Consequence (B).** Outcomes: next-year crash indicators and negative skewness; regressors: ownership-weighted dispersion of holders' horizons, short-horizon ownership share and Greenwood-Thesmar fragility [42], [32]. Absorption: in stocks in the top decile of short-horizon net selling, regress long-horizon holders' share changes on the interaction of short-horizon selling and dispersion, instrumented with Coval-Stafford flow-induced trading [43], [32]. The 2008 episode needs pre-2013 holdings, which the free data sets do not provide [12]; it requires Thomson/Refinitiv s34 via WRDS or parsing raw EDGAR text [13].

**Model (E).** Set the adaptation weight to the estimated peer coefficient, using the DeGroot mapping [13], and use Golub-Jackson's result that homophily slows cross-group convergence to derive an analytic convergence speed [56]. Replace the friction channel with a liquidity channel calibrated to the consequence estimates, then test the model out of sample on the 2020 and 2022 cross-sections.

### 6.8 Data upgrades, ranked

| Priority | Upgrade | Purpose | Cost |
|---|---|---|---|
| 1 | Full-universe SEC 13F data sets, share-based, unit-corrected [12], [13] | Answers sampled-network critique; removes drift | Free; cleaning effort |
| 2 | CRSP stock file via WRDS | Returns, delistings, crash measures without survivorship bias [32] | Access pending |
| 3 | CRSP mutual fund manager data plus N-PORT | Manager shocks and fund-to-filer mapping [11] | WRDS plus existing N-PORT |
| 4 | Thomson/Refinitiv s34 | Pre-2013 history for 2008 stress tests [13] | WRDS |
| 5 | Fund flow histories | Greenwood-Thesmar fragility and flow residualisation [42] | CRSP mutual fund |

## 7. Referee Objections the Pivot Must Survive

**Objection 1: "This is turnover commonality, not contagion."** The strongest objection. Pastor, Stambaugh and Taylor show turnover loads heavily on a common factor tied to sentiment, dispersion and liquidity, with category-level commonality especially high [7]. **Response:** quarter effects explain only about 2% of horizon variance in the project's own data, so the market-wide factor is small here; style-by-quarter fixed effects absorb the style-level factor; and the shock design moves one neighbour's horizon for reasons unrelated to market conditions [11], [14]. Include PST-style category averages as controls.

**Objection 2: "Overlap neighbours are chosen because they are alike; this is selection."** Links formed from holdings make homophily the null [14], and co-holding is type-assortative [23]. **Response:** the network is lagged and fixed before the shock, the shock does not change the network [10], and future-neighbour placebos test whether selection on trends drives results.

**Objection 3: "Horizon is a fixed trait; there is nothing to transmit."** Parsa treats it as an institution fixed effect [36], Cella et al. call it very stable [30], and holding-horizon ranks persist for 20 quarters [41]. **Response:** ranks persist while levels move [7], [30]; the project's own data leave 33% of variance after institution and quarter effects; the paper's first table reports the decomposition on the full universe.

**Objection 4: "Turnover is not horizon."** Lan, Moneta and Wermers call inverse turnover a flawed proxy [41]. **Response:** report both churn and holding-horizon outcomes and show the peer effect in each.

**Objection 5: "Outcome-on-mean peer regressions are vacuous."** Angrist [53]. **Response:** the headline estimate uses a manipulated peer characteristic (a shock), which is the design Angrist accepts [53].

**Objection 6: "Your instruments are invalid or weak."** Sampled-network invalidity [9], [10] and weak friends-of-friends instruments [54]. **Response:** full universe; friends-of-friends only as robustness with Anderson-Rubin inference [54].

**Objection 7: "The shock is small, fund-level and may hit holdings directly."** The bereavement sample has 304 events at fund level [11]; mergers change neighbours' holdings directly [47]; single events dominate [48]. **Response:** pool deaths, departures and retirements; use single-manager funds; double exclusion of co-held stocks; leave-one-event-out. If shocks are too few, step down the journal ladder per the kill criteria.

**Objection 8: "13F data are noisy."** Quarterly snapshots miss intra-quarter round trips, filers aggregate funds, the SEC does not guarantee accuracy [12], and values changed units in 2023 [13]. **Response:** share-based measures, filer-event flags, N-PORT fund-level validation, documented unit correction.

**Objection 9: "Strategic complementarity predicts herding in information, not horizon."** In Froot-Scharfstein-Stein and Chamley horizon is exogenous [15], [16]. **Response:** concede it openly; the paper extends their logic to endogenous horizon choice and tests the extension's distinctive prediction (tipping in already short-horizon neighbourhoods), which pure common shocks do not produce.

**Objection 10: "So what?"** **Response:** the consequence section links contagion to holder-horizon dispersion, which is tied to liquidity [8] and tail risk [19], and the calibrated model quantifies the multiplier on crisis amplification [39].

**Objection 11: "This has been done."** **Response:** cite PST, Hong-Kubik-Stein, Pool-Stoffman-Yonker, Blocher, Chen et al. and the retail turnover papers as boundary markers [7], [2], [3], [4], [50], [5], [6], word the claim as "first identified peer effect in institutional horizon," and read MacDonald (SSRN 5692342, 2025) and the full Liang-Wu-Yin paper before submission [52], [1].

**Committed reading of the objections.** Objections 1, 2 and 7 decide the paper; the rest are answerable with robustness. The pivot survives only if the manager-shock first stage is real and the double-exclusion reduced form is positive with clean pre-trends. That is a risk worth taking because the alternative pivots carry a risk that cannot be designed away: being second to a published paper [8], [20].

## Sources

[1] Interim research note: pivot-a-near-duplicate-audit. No public URL (internal research note in the project vault).
[2] NBER WORKING PAPER SERIES (Hong, Kubik, Stein, NBER w9711, Thy Neighbor's Portfolio). https://www.nber.org/system/files/working_papers/w9711/w9711.pdf
[3] The People in Your Neighborhood: Social Interactions and Mutual Fund Portfolios (Pool, Stoffman, Yonker, JF 2015). https://ideas.repec.org/a/bla/jfinan/v70y2015i6p2679-2732.html
[4] Network externalities in mutual funds (Blocher, Journal of Financial Markets 2016). https://ideas.repec.org/a/eee/finmar/v30y2016icp1-26.html
[5] Escobar and Pedraza 2023 JFE: Active trading and (poor) performance: the social transmission channel. https://ideas.repec.org/a/eee/jfinec/v150y2023i1p139-165.html
[6] Social Interaction Intensity (Gelman, Hirshleifer, Levi, Reiter-Gavish, NBER w32772). https://cba.lmu.edu/media/lmucollegeofbusinessadministration/departments/finance/Social Interaction Intensity and Investor Behavior.pdf
[7] NBER WORKING PAPER SERIES (Pastor, Stambaugh, Taylor, Do Funds Make More When They Trade More?, NBER w20700). https://www.nber.org/system/files/working_papers/w20700/w20700.pdf
[8] Investor Heterogeneity and Liquidity* (Chan, Cheng, Hameed, JFQA 2022). https://web2-bschool.nus.edu.sg/wp-content/uploads/media_rp/publications/vDsxi1613376975.pdf
[9] ECONOMETRICS OF SAMPLED NETWORKS (Chandrasekhar and Lewis). https://stanford.edu/~arungc/CL.pdf
[10] Peer Effects in Networks: a Survey. https://www.crrep.ca/sites/crrep.ca/files/2020-01.pdf
[11] Life is Too Short? Bereaved Managers and Investment Decisions - Review of Finance (Liu, Sulaeman, Shu, Yeung, RoF 2023). https://revfin.org/?p=3058
[12] SEC.gov | Form 13F Data Sets. https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
[13] Interim research note: data-upgrade-and-abm-calibration. No public URL (internal research note in the project vault).
[14] Interim research note: correlated-turnover-vs-horizon-contagion-identification. No public URL (internal research note in the project vault).
[15] Herd on the Street: Informational Inefficiencies in a Market with Short-Term Speculation | NBER (Froot, Scharfstein, Stein). https://www.nber.org/papers/w3250
[16] PRELIMINARY PROOF (Chamley, Complementarities in information acquisition with short-term trades, Theoretical Economics 2007). https://www.bu.edu/econ/files/2012/11/dp156.pdf
[17] WORKING PAPER NO. 276 (Cespa and Vives, Higher order expectations, illiquidity and short-term trading). https://www.csef.it/WP/wp276.pdf
[18] Internet Appendix (Chan, Cheng, Hameed, Internet Appendix, JFQA 2022). https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S0022109022000217/resource/name/S0022109022000217sup001.pdf
[19] DOI: 10.16538/j.cnki.fem.20260118.204 (Chen, Lu, Qin, Foreign Economics and Management 2026). https://qks.sufe.edu.cn/J/PDFFull/TxMBou5H-3rV2-xA64-7Pf5-V5uQq9LSBWGd.pdf
[20] Journal of Financial Economics 76 (2005) 135-165 (Gaspar, Massa, Matos, Shareholder investment horizons and the market for corporate control). https://www.darden.virginia.edu/sites/default/files/inline-files/gasparmassamatoshorizonsmajfeapr05.pdf
[21] Institutional Investors and Equity Returns: (Yan and Zhang, RFS 2009). https://www.lehigh.edu/~xuy219/research/horizon_RFS.pdf
[22] Interim research note: horizon-homophily-fact-or-mechanical. No public URL (internal research note in the project vault).
[23] Institutional Investor Cliques and Governance (Crane, Koch, Michaely). https://www.lebow.drexel.edu/sites/default/files/1488309013-crane-kochmichenaudinstitutional-investor-cliques.pdf
[24] Oldham 2019 Complexity full text (Wayback PDF): short-termism and dynamic investor network ABM. https://web.archive.org/web/20220726165036if_/https://downloads.hindawi.com/journals/complexity/2019/1715624.pdf
[25] EconPapers: EVOLUTION AND TIME HORIZONS IN AN AGENT-BASED STOCK MARKET (LeBaron, Macroeconomic Dynamics 2001). https://econpapers.repec.org/RePEc:cup:macdyn:v:5:y:2001:i:02:p:225-254_01
[26] Review of Finance. https://revfin.org/wp-content/uploads/2025/08/RF-Report-2025_FINALv2-1.pdf
[27] Journal of Financial and Quantitative Analysis | Cambridge Core. https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis
[28] Journal of Banking & Finance | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-banking-and-finance
[29] Journal of Financial Stability | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-financial-stability
[30] Interim research note: horizon-trait-or-time-varying. No public URL (internal research note in the project vault).
[31] IZA DP No. 2652 (Bramoulle, Djebbari, Fortin, Identification of Peer Effects through Social Networks). https://docs.iza.org/dp2652.pdf
[32] Interim research note: dispersion-and-absorption-beyond-chan-cheng-hameed. No public URL (internal research note in the project vault).
[33] CoMSES Catalog (Li, Nishimura, Men 2014, Physica A). https://catalog.comses.net/publications/774
[34] CoMSES Catalog (Li, Li, Sun 2017, Applied Economics). https://catalog.comses.net/publications/192806
[35] A Model of Multi-Frequency Trade∗ (Crouzet, Dew-Becker, Nathanson). https://pages.stern.nyu.edu/~jh4/SternMicroMtg/Old/SternMicroMtg2017/Papers/MultiFreqTrade.pdf
[36] Investors' horizon and stock prices (Parsa, MIT PhD thesis 2011). http://hdl.handle.net/1721.1/65491
[37] Impact of different investment horizons in heterogeneous agent models: Do long-term traders bring market stability?. https://ideas.repec.org/a/eee/jeborg/v196y2022icp393-401.html
[38] Calibrating emergent phenomena in stock markets with agent based models - PMC. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5834198/
[39] ISSN 0956-8549-717 (Cella, Ellul, Giannetti, Investors' Horizons and the Amplification of Market Shocks, RFS 2013). https://eprints.lse.ac.uk/119037/1/DP717.pdf
[40] Do Institutional Investors Stabilize (Glossner, Matos, Ramelli, Wagner, ECGI WP 688/2020). https://www.ecgi.global/sites/default/files/2026-10/fin-688-2020_do_institutional_investors_stabilize_equity_markets_in_crisi.pdf
[41] CFR Working Paper NO. 15-06 (Lan, Moneta, Wermers, Holding Horizon). https://www.cfr-cologne.de/download/workingpaper/cfr-15-06.pdf
[42] Stock price fragility$ (Greenwood and Thesmar, Stock price fragility, JFE 2011). https://tevgeniou.github.io/EquityRiskFactors/bibliography/Fragility.pdf
[43] NBER WORKING PAPER SERIES (Coval and Stafford, Asset fire sales (and purchases) in equity markets). https://www.nber.org/system/files/working_papers/w11357/w11357.pdf
[44] THE JOURNAL OF FINANCE • VOL. LXIX, NO. 3 • JUNE 2014 (Anton and Polk, Connected Stocks). https://personal.lse.ac.uk/polk/research/ConnectedStocks.pdf
[45] Statistically validated network of portfolio overlaps and systemic risk - PMC (Gualdi et al., Scientific Reports 2016). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5175158/
[46] Similar Investors1 (Georg, Pierret, Steffen, Similar Investors). https://www.fmg.ac.uk/sites/default/files/2020-08/6.PIERRET-Similar-Investors-presentation-LSE.pdf
[47] EconPapers: Who Is Afraid of BlackRock? (Massa, Schumacher, Wang, RFS 2021). https://econpapers.repec.org/RePEc:oup:rfinst:v:34:y:2021:i:4:p:1987-2044.
[48] Does Common Ownership Really Increase Firm Coordination? (Lewellen and Lowry, JFE 2021 (Harvard Law Forum summary)). https://corpgov.law.harvard.edu/2021/05/21/does-common-ownership-really-increase-firm-coordination/
[49] Birds of a Feather: Do Hedge Fund Managers Flock Together? (Gerritzen, Jackwerth, Plazzi, Management Science 2024). https://ideas.repec.org/a/inm/ormnsc/v70y2024i5p2976-2998.html
[50] 机构投资者理性泡沫骑乘及其动因探究 (Chen Guojin et al., China Industrial Economics 2021). http://cfrc.pbcsf.tsinghua.edu.cn/__local/B/20/39/C42717CDED9CC5A121DC2EC233A_2A862632_121624.pdf?e=.pdf
[51] w o r k i n g (Heimer, Friends Do Let Friends Buy Stocks Actively, FRB Cleveland WP 13-14). https://www.clevelandfed.org/-/media/project/clevelandfedtenant/clevelandfedsite/publications/working-papers/2013/wp1314.pdf
[52] Liang-Wu-Yin: High Turnover in Chinese Mutual Funds: Drivers and Effects (SSRN 5048159) - abstract-level only. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5048159
[53] NBER WORKING PAPER SERIES (Angrist, The Perils of Peer Effects, NBER w19774). https://www.nber.org/system/files/working_papers/w19774/w19774.pdf
[54] Empirical Challenges with Peers-of-Peers Instruments (Canen and Chadha, arXiv 2602.24215). https://arxiv.org/pdf/2602.24215
[55] Do Peer Firms Aﬀect Corporate Financial Policy?∗ (Leary and Roberts, JF 2014). https://haas.berkeley.edu/wp-content/uploads/LR_PeerEffects_R4.pdf
[56] How Homophily Aﬀects the Speed of (Golub and Jackson, How Homophily Affects the Speed of Learning and Best-Response Dynamics, QJE 2012). https://web.stanford.edu/~jacksonm/homophily.pdf
[57] Journal of Economic Dynamics and Control | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-economic-dynamics-and-control
[58] Journal of Economic Behavior & Organization | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-economic-behavior-and-organization
[59] Finance Research Letters | Journal | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/finance-research-letters
[60] International Review of Financial Analysis | Journal | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/international-review-of-financial-analysis
[61] Management Science: Journal Quartile & Metrics Score 2026. https://www.journalmetrics.org/journal/management-science
[62] Review of Financial Studies: Journal Quartile & Metrics Score 2026. https://www.journalmetrics.org/journal/review-of-financial-studies
[63] Journal of Corporate Finance | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-corporate-finance
[64] Journal of International Financial Markets, Institutions and Money | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-international-financial-markets-institutions-and-money
