# From Chronotypic Ecology to Horizon Contagion: A Staged, Falsifiable Pivot Programme

**Executive summary.** The single most defensible pivot is Pivot A, horizon contagion (do institutions' trading horizons move toward those of their portfolio-overlap neighbours?), but only if it is run as a staged programme with pre-stated kill criteria, and only if Pivots B and E are built as modules that can be published on their own when A fails a gate. The two camps that this audit produced are both right about part of the truth. The novelty camp is right that no paper found in roughly 18 search framings estimates a peer effect whose outcome is an institution's own turnover or horizon [1]; institutional peer-effect work targets what is held, bought or flowed [2][3] [4], and the turnover-as-outcome peer literature is retail [1]. The identification camp is right that the design as currently specified (a top-150, 13F-only overlap network, non-held-stock neighbour horizons, friends-of-friends instruments) would not convince a top-field referee, because turnover has a strong common component that is stronger among similar funds [5], same-horizon funds receive correlated flows [6], friends-of-friends instruments from a sampled graph are generically invalid [7], and regressions of an outcome on peers' mean outcome are mechanical without exogenous variation [8]. These two findings do not conflict. The question is open precisely because the obvious design does not identify it.

The reconciliation is procedural, not rhetorical. Step zero rebuilds the panel from the free SEC Form 13F Data Sets on the full filer universe with share-based horizons and a corrected 2022Q4 unit break [9][10]. Step one is a pre-registered variance decomposition and descriptive peer test with style-by-quarter fixed effects and a future-neighbour placebo; the first gate is already passed in the project's own data (33% of the variance of log horizon survives institution and quarter fixed effects, against a 10% kill threshold [11]). Step two is a shock design built on neighbours' manager departures and deaths rather than on fund-family mergers, which recent work shows are timing-confounded and exclusion-violating [12][13] [14]. Pivot B (holder-horizon dispersion and fragility) is mostly pre-empted by Chan, Cheng and Hameed (JFQA 2022) and its Internet Appendix [6][15], and for China by Chen, Lu and Qin (2026) [16]; it survives as a US crash-risk, fragility horse-race and relative-absorption module. Pivot E (a calibrated, horizon-homophilous ABM) is not pre-empted by the nearest model, Oldham (2019), whose horizons are fixed classes [17], but it clears the impact-factor bar only as the final section of an empirical paper, because the ABM-friendly journals sit far below it (JEDC 1.8, JEBO 2.7) [18][19]. Pivot C is pre-empted by the standard churn measure [20][21] and becomes a data appendix; Pivot D is mostly mechanical as measured and becomes a conditional motivating fact [22].

The target for the full programme is Review of Finance (2024 JIF 8.4) or Management Science (4.9), with JFQA as the quality-first alternative despite a volatile JIF (2.8 in 2024, 4.1 in 2025) [23][24]. If A is killed at the shock gate, the descriptive A plus B package fits the Journal of Financial Stability (4.1) or Journal of Banking & Finance (4.0) [25][26]; a US-versus-China version of B fits JIFMIM (6.0) [27]. The current target, Finance Research Letters, already clears the threshold at 7.1 [28], so the binding constraint was never impact factor; it was having a contribution that is not a replication.

## 1. Where the Current CME Paper Stands

### 1.1 What the paper claims and what survives

The current paper bundles a simulation (homophily lowers volatility through a cross-horizon friction channel and lowers belief fragmentation; adaptation compresses horizon diversity) with five empirical exhibits. Taken one at a time, each exhibit is either pre-empted, mechanical, or overturned by the paper's own robustness checks, and this convergence from independent evidence paths is itself the most important finding of the audit.

The aggregate horizon-diversity index illustrates the problem cleanly. Its correlation with VIX (r = -0.53) vanishes to -0.06 under share-based turnover, which the paper itself reports as evidence that the value-weight series was price drift. The project's own data now add a second defect: the SEC switched 13F market values from thousands to dollars for filings from January 3, 2023, which in the project cache creates a 1000x jump at 2022Q4, so the reported 2022Q4 index minimum of 1.021 is an artefact (1.918 after rescaling), and the value-weight correlation with VIX moves from -0.526 to -0.641. The SEC readme states the rule directly: market value is reported to the nearest dollar starting January 3, 2023, and previously in thousands [10]. The correction strengthens the value-weight correlation but does not rescue it, because the share-based series, which is immune to both drift and the unit break, carries no VIX relation. The committed reading: the index result should be withdrawn as a finding and kept only as a cautionary data appendix.

The horizon-homophily fact (kappa-hat 0.158, positive in all 50 quarters, Newey-West t = 19) is the paper's second exhibit. It is directionally unsurprising: index-tracking geometry, drift-contaminated horizons, characteristic-based demand and shared managers each predict a positive correlation of this size without any horizon-specific mechanism [22]. The mean coefficient implies an R-squared of roughly 2.5%, and because each quarter's correlation is computed over about 11,000 dyads sharing 150 nodes with nearly identical portfolios quarter to quarter, the 50-of-50 record is closer to one persistent structural fact observed 50 times than to 50 independent confirmations [22].

The stock-level result (within-stock slope -0.011, t = -2.4: lower ownership-weighted dispersion of holders' log horizon predicts slightly higher next-quarter volatility) is a weaker out-of-sample replication of a table that already exists. Chan, Cheng and Hameed report quarterly Fama-MacBeth coefficients of -0.034 to -0.042 on their dispersion measure over 1982 to 2016, and -0.039 to -0.057 over 2000 to 2016, controlling for size, book-to-market, past returns, number of funds, institutional ownership, illiquidity and liquidity volatility [15]. The survivor-only sample of the current paper, without CRSP delisting returns, cannot improve on that.

### 1.2 What the simulation's sign problem implies

The model's friction channel predicts that more horizon diversity raises volatility. Two independent empirical estimates, the Chan-Cheng-Hameed appendix and the project's own stock-level slope, point the other way [15]. Chan, Cheng and Hameed's headline is that stocks held by institutions with more heterogeneous horizons are more liquid and have lower volatility of liquidity, with a 2003 dividend-tax-reform shock for identification [6]. The theoretical literature is genuinely split: LeBaron's evolving-horizon ABM finds that mixed short- and long-horizon populations raise return variability [29], while Brock-Hommes-type models with horizons find that long-horizon traders stabilise [30]. The reconciler's reading is that both channels exist and that the model's error was to hard-wire one of them. A friction channel (disagreement across horizons) and an absorption channel (long-horizon holders accommodating short-horizon liquidity demand) can coexist, and the net sign is an empirical parameter. This is the opening for Pivot E: a model whose absorption strength is disciplined by Pivot B estimates rather than assumed.

### 1.3 What transfers to the pivot

Four assets transfer. First, the team already has the institution-quarter horizon panel and has shown it has usable within variation: within-institution sd of log tau is 0.55 against 0.92 total, with AR(1) 0.75 across 147 institutions and 50 quarters (the project's own data). The interim analysis translates this into a within-variance share of about 36% and a shock half-life near 2.4 quarters [11]. Second, the overlap network already exists and is structurally suited to network instruments: about 100 institutions per quarter, median pairwise cosine 0.03 to 0.07, and a median of 32 to 42 friends-of-friends per node who are not friends (the project's own data). Third, the code base for the ABM exists and can be re-signed. Fourth, the team's discovery of drift and unit contamination is a credibility asset if it is presented as data hygiene rather than as a contribution. What must be discarded is the FMH microfoundation framing as the paper's headline, the friction-volatility claim, and the VIX correlation.

## 2. Literature Map

### 2.1 Strand (a): horizon heterogeneity, the Fractal Market Hypothesis and heterogeneous-horizon ABMs

The modelling literature has already made horizons endogenous, but never through networks. LeBaron (2001) lets agents differ in the lookback horizon used to evaluate forecasting rules and lets the horizon distribution evolve through wealth-based replacement; mixed populations raise return variability and produce realistic volatility and volume patterns [29]. Nishiwaki (JEBO 2022) inserts horizons into the Brock-Hommes switching model and asks whether long-term traders bring stability [30]. The PLOS ONE calibration study fits two-agent models with heterogeneous horizons, decision processes and lags to index series and argues that horizon heterogeneity is crucial for reproducing long memory [31]. Oldham (2019) is the closest network ABM: an advice network rewires toward class-specific outperforming "Oracles", but horizon is a fixed class with memory weights of 0.95 versus 0.90, the short-term share is set by the user at 0, 25, 50, 75 or 100%, and nothing is calibrated [17]. Oldham's own future-work section asks for empirical calibration and for investors to learn and adjust their approach, which is exactly what the CME model already does [17].

Theory supplies a sign prediction that the empirical literature has never tested. Froot, Scharfstein and Stein (JF 1992) show that short-horizon speculators may herd on the same information, with multiple equilibria; the value of information to a short-horizon trader depends on what others trade on, a strategic complementarity that predicts a positive horizon peer effect and possibly tipping rather than smooth diffusion [32]. Golub and Jackson (QJE 2012) show that with DeGroot averaging, convergence to consensus is slowed by homophily and unaffected by density, and they supply a spectral homophily measure (the second eigenvalue of a group-interaction matrix) that could turn the CME's simulated "temporal echo chamber" into an analytic convergence-time result [33]. The Fractal Market Hypothesis itself has only loose empirical support and no institutional-holdings test in the reviewed record; the equilibrium multi-frequency literature (frequency specialisation, investor fixed effects in trading frequency) does the conceptual work FMH was meant to do and is more credible to finance referees [11].

Committed reading: the ABM space is crowded with heterogeneous-horizon models, but none combines horizon-homophilous link formation, neighbour-driven horizon adaptation and an adaptation rate estimated from holdings data. FMH should be demoted from framing to a sentence of motivation.

### 2.2 Strand (b): 13F-based institutional horizons and their effects

The measurement and level-effect literature is mature. Gaspar, Massa and Matos (JFE 2005) define the churn rate and a firm-level investor-turnover measure as the holding-weighted average of holders' four-quarter churn [20]. Yan and Zhang (RFS 2009) use the minimum of buys and sells to minimise the impact of investor cash flows, sort institutions into tertiles of four-quarter average churn, and find that short-term institutional ownership drives the ownership-return relation with no long-run reversal [21]. Cella, Ellul and Giannetti (RFS 2013) show that around Lehman short-horizon institutions sold almost 21% of their holdings against 7% for long-horizon institutions, and that stocks mostly held by short-horizon investors had cumulative abnormal returns near -12% over five weeks against about -4% [34]. They instrument horizon with the correlation between an investor's past performance and withdrawals, a funding-fragility instrument that captures horizon variation driven by funding structure rather than skill [34]. Glossner, Matos, Ramelli and Wagner (Management Science) show that in the COVID-19 crash high-IO stocks did worse, mitigated by long-term, passive and foreign ownership, with mean long-term ownership of 37% and passive of 16% [35].

Committed reading: every result in this strand is a level effect (the share of short- or long-horizon owners), measured with drift-adjusted churn. Nothing here treats horizon as an outcome that responds to peers.

### 2.3 Strand (c): dispersion of the ownership base

This strand is where pre-emption is heaviest and most recent. Chan, Cheng and Hameed define STDCR as the cross-holder standard deviation of churn divided by its mean, and show that more heterogeneous horizons go with higher liquidity and lower liquidity volatility, that extreme flow-induced trading has more price impact in low-heterogeneity stocks, and that the illiquidity premium concentrates in low-heterogeneity stocks [6]. Their tax-reform design finds illiquidity falling by 9% to 26% among stocks with above-average increases in heterogeneity [6]. Their mechanism is explicitly conjectural at the holder level: they write that long-horizon funds "can provide liquidity to active mutual funds during fire sales" but never observe who buys [6]. Chen, Lu and Qin (Foreign Economics & Management, 2026) take the same coefficient-of-variation measure, flip its sign into a homogeneity index, and find that for A-shares over 2013 to 2024 trading-horizon homogeneity raises left-tail systemic risk through liquidity shocks and order imbalance, robust to difference-in-differences, instrumental variables and Heckman corrections, and stronger when policy uncertainty is high, markets are weak and arbitrage risk is large [16]. Greenwood and Thesmar (JFE 2011) supply the benchmark that any dispersion measure must beat: fragility as an ownership-weighted quadratic form in owners' flow covariance, with a univariate R-squared near 8% for future volatility [36].

Committed reading: "dispersion matters" is published at JFQA for liquidity and volatility, and in China for tail risk. What is open is narrow: US crash and skewness outcomes, a horse race against flow-covariance fragility, and a direct within-stock test of absorption in named stress episodes [37].

### 2.4 Strand (d): common ownership, overlap networks, fire sales and flow-driven fragility

Coval and Stafford document that funds with large outflows cut existing positions, creating price pressure in commonly held stocks that reverses, and that investors trading against constrained funds earn liquidity-provision returns [38]. Gualdi and coauthors build a statistically validated 13F overlap network against a bipartite configuration model null for 1999 to 2013 and find that the proportion of validated links rose before the 2007-2008 crisis and peaked at it [39]. Blocher shows that flows spill over between funds linked by common holdings, with a network externality 32% to 92% as large as lagged own flows and a 1.5% quarterly excess return that reverses [4]. Crane, Koch and Michenaud identify roughly 20 institutional cliques a year and find that clique members are most likely dedicated investors and least likely quasi-indexers [40]. Two papers matter mainly as warnings for shock designs. Lewellen and Lowry (JFE 2021) show that the institutional-merger design used in the common-ownership literature is dominated by the BlackRock-BGI 2009 event and its post-crisis timing; once modified, the effect disappears [12]. Massa, Schumacher and Wang (RFS 2021) show that around the same merger, open-end funds with large exposure to commonly held stocks begin avoiding those stocks, because market participants respond strategically to expected fragility [13].

Committed reading: overlap is a proven transmission channel for flows and prices, and it is also a selection outcome; merger shocks to overlap networks move neighbours' behaviour directly, which is fatal for using them as instruments for a neighbour's horizon.

### 2.5 Strand (e): peer effects, herding and contagion in institutional trading, and identification

The institutional peer-effect literature studies which stocks are held and traded. Hong, Kubik and Stein find that a manager is more likely to hold, buy or sell a stock if other managers in the same city do, and interpret this as an epidemic of word-of-mouth information [2]. Pool, Stoffman and Yonker find that managers living in the same neighbourhood have more similar holdings and trades than same-city managers in different neighbourhoods [3]. The audit of roughly 18 query framings (fund families, manager moves, consultants, China and Europe, hedge-fund strategy contagion, holding-period herding, 2023-2026 working papers) found no paper using a portfolio-overlap or social network to estimate a peer effect whose outcome is institutional turnover or horizon, while trading activity as a peer outcome appears only for retail investors [1]. The closest institutional object is commonality, not contagion: Pastor, Stambaugh and Taylor show that average fund turnover fluctuates between 59% and 102% a year over 1979 to 2011, has a 95% correlation with the first principal component of fund turnover [41], and loads on sentiment, cross-sectional dispersion and market liquidity, with commonality "especially high among funds sharing similar characteristics" [5]. A panel regression of fund turnover on the average of others' turnover with fund fixed effects gives a slope of 0.65 (t = 8.65) [5].

The identification literature is unforgiving. Angrist shows that outcome-on-outcome peer regressions are vacuous, with a coefficient of unity or, with leave-out means, an intraclass correlation, and that with predetermined covariates a peer effect is econometrically a test of whether 2SLS with group dummies differs from OLS [8]. Chandrasekhar and Lewis prove (Proposition 3.4) that 2SLS with friends-of-friends instruments built from a sampled graph generically violates the exclusion restriction, but also that instruments built from the full graph remain valid when the second stage is restricted to the sampled nodes [7]. Canen and Chadha (2026) show that friends-of-friends instruments degenerate in very sparse networks and carry too little first-stage information in denser ones, and recommend Anderson-Rubin inference and row-scaling [42]. Bramoulle, Djebbari and Fortin's intransitive-triad result and Caeyers and Fafchamps's exclusion bias complete the toolkit [43]. The best shock precedent in fund data is Liu, Sulaeman, Shu and Yeung (RoF 2023): parental deaths of 304 mutual-fund managers over 1999 to 2013 push funds toward quasi-indexing, with lower tracking error and active share, more strongly for unexpected deaths and single-manager funds [14].

Committed reading: the estimand is open, the tools are mature, and the specific threat is a style-level common turnover factor that overlap neighbours share by construction.

### 2.6 Strand (f): measuring horizons from holdings and price-drift contamination

The standard churn rate already nets out passive price changes: the Gaspar-Massa-Matos numerator subtracts the prior position times the price change, so it equals share changes valued at current prices, with a range of 0 to 2, following Carhart (1997) and CRSP conventions [20]. Yan and Zhang use the same price-adjusted numerator [21]. Chan, Cheng and Hameed report a share-based turnover robustness (STDTO) with similar effects, for example 0.31% lower illiquidity per standard deviation [6]. Lan, Moneta and Wermers go further and argue that turnover is a flawed and downward-biased proxy for holding horizon, while confirming that horizon ranks are persistent for 20 quarters [11]. On the data side, the SEC's free Form 13F Data Sets cover July 2013 to August 2026, are presented as filed, were refreshed in March 2024 to a common format, and come with a disclaimer that accuracy cannot be guaranteed [9]. Thomson s34 has known omissions (BlackRock is named for 2018), and WRDS's own 13F product starts in June 2013 [10].

Committed reading: drift contamination is the reason the standard measure exists. The CME finding corrects its own non-standard tau = 63/turnover construction. The genuinely useful new item is the January 2023 unit break, which is a data warning, not a research contribution.

### 2.7 Strand (g): homophily in investor networks

Homophily is documented among investors only as type assortativity and as flow comovement. Crane, Koch and Michenaud find that institutions within a clique are more similar to each other than to outsiders, especially on type indicators, and acknowledge that similar behaviour may reflect similar information sets [40]. Chan, Cheng and Hameed find that flows of a low-churn fund comove 0.80 with other low-churn funds and 0.12 with funds outside the group, and 0.98 versus 0.16 for high-churn funds [6]. Gualdi and coauthors supply the bipartite null that removes degree and popularity, though not weights or characteristics [39]. Koijen-Yogo characteristic demand and Ozdagli-Ryfe common asset managers explain co-holding without any horizon mechanism [22]. Golub and Jackson provide the formal consequence of homophily for averaging dynamics [33].

Committed reading: no paper tests pairwise horizon proximity against pairwise portfolio similarity, but the raw version of that fact is predictable from five known channels, so it is a motivating fact, not a contribution.

## 3. Novelty Audit of the Five Candidate Pivots

### 3.1 Summary verdicts

| Pivot | Already done? | Closest papers | Genuinely novel increment | Standalone publishable above IF 4-5? |
|---|---|---|---|---|
| A. Horizon contagion | Not found as an estimand (about 70% confidence after adversarial searches) | Pastor-Stambaugh-Taylor commonality; Hong-Kubik-Stein; Pool-Stoffman-Yonker; Blocher; retail turnover peer papers | Identified peer effect in institutional horizon via neighbour shocks on a full-universe network with style-by-quarter fixed effects; test of the Froot-Scharfstein-Stein complementarity sign | Yes, if it passes the shock gate (RoF, MS, JFQA) |
| B. Holder-horizon dispersion and absorption | Largely done | Chan-Cheng-Hameed (JFQA 2022) and Internet Appendix; Chen-Lu-Qin (2026, China); Greenwood-Thesmar; Cella-Ellul-Giannetti; Glossner et al. | US crash and skewness outcomes; horse race against flow-covariance fragility; relative absorption in 2008, 2020 and 2022 stress quarters | Marginal: JFS, JBF, JIFMIM, or an FRL letter |
| C. Price-drift contamination | Done | Gaspar-Massa-Matos; Yan-Zhang; Chan-Cheng-Hameed STDTO | None as a paper; a data note on the 2023 unit break | No |
| D. Horizon homophily in co-holding | Partly done, mostly mechanical | Crane-Koch-Michenaud; Chan-Cheng-Hameed flow comovement; Gualdi et al. null | Residual after active weights, share-based tau, dyadic fixed effects and BiCM validation | No; motivating fact for A |
| E. Calibrated adaptive-horizon ABM | Not done in this form (about 70% confidence) | Oldham 2019; LeBaron 2001; Nishiwaki 2022; PLOS ONE 2018 | Horizon-homophilous links, neighbour adaptation at an estimated rate, absorption disciplined by B, out-of-sample test | Only below threshold (JEDC, JEBO); above threshold as a section of A |

### 3.2 Pivot A: horizon contagion

**Already done?** No paper found estimates it. Every institutional peer-effect paper reviewed targets holdings, trade direction or flows [2][3] [4], and the closest turnover object, Pastor-Stambaugh-Taylor commonality, is a factor structure with no network, no neighbour exclusion and no instrument [5][1]. Adversarial follow-up searches (the Liang-Wu-Yin Chinese turnover paper at abstract and reference-list level, the Chinese co-holding-network literature, 2023-2026 working papers, manager-mover designs) raised confidence that A is novel as an estimand from about 65% [1] to about 70% in the adversarial round, while confirming that Chinese papers already apply co-holding-network peer designs to other outcomes such as bubble-riding (from this audit's adversarial search; not yet in the cited record). One title-only lead, a 2025 SSRN paper on whether institutions are influenced by other institutions' trades using a quantity-based approach for US 13F holdings, must be read before submission; it most plausibly studies trade direction, the established estimand.

**Why both camps are right.** The novelty is real because the obvious design fails, and the obvious design fails for a specific, nameable reason. The non-held-stock construction removes stock-level channels (a cash-out merger or index deletion in a co-held name) but not the strategy-level opportunity set that moves turnover in every stock [43]. Overlap neighbours are style neighbours by construction, and Pastor-Stambaugh-Taylor show that adding same-category average turnover to the market-wide average raises explanatory power by almost half [5][43]. Chan-Cheng-Hameed's 0.80 versus 0.12 flow comovement within churn terciles is the same problem in flow form [6]. Combining A and B: neighbours are chosen partly because their trading style is alike (the CME's own homophily fact), so selection and influence are observationally equivalent without a shock [43][8].

**The novel, defensible increment.** Three elements together, none of which exists in the record. (i) The estimand: the response of an institution's share-based horizon to an exogenous change in its overlap neighbours' horizons. (ii) The identification: neighbour shocks that originate outside the style factor (manager deaths and departures, following the Liu et al. precedent [14]), estimated on a full-universe network with style-by-quarter fixed effects and future-neighbour placebos. (iii) A theory test: Froot-Scharfstein-Stein complementarity predicts a positive effect that is stronger among short-horizon neighbours and possibly nonlinear [32], while Golub-Jackson predicts slower cross-group convergence under homophily [33]. A paper that delivers (i) and (ii) is a contribution; adding (iii) makes it a paper about why horizons spread.

### 3.3 Pivot B: holder-horizon dispersion and within-stock absorption

**Already done?** Mostly. Chan-Cheng-Hameed publish the measure, a drift-adjusted churn with a share-based robustness, the liquidity outcomes, the flow-comovement mechanism, the flow-induced-trading test and a tax-reform shock [6], and their appendix already shows the volatility sign [15]. Chen-Lu-Qin take the measure to tail risk in China [16]. The level baseline is Cella-Ellul-Giannetti [34].

**Where the two sides meet.** The absorption question pits theory and the stock-level reduced form (dispersion stabilises) against the episode evidence (retail and arbitrageurs absorb; institutions co-trade). Glossner et al. find that retail investors provided liquidity to stocks sold by institutions in 2020Q1 [35]; Cella-Ellul-Giannetti find long-horizon holders sold too, just less [34]; and in distressed liquidations other managers trade in the same direction in a large share of positions, though that figure is unverified [37]. These positions reconcile once absorption is defined as relative rather than absolute: aggregate institutions can net-sell while long-horizon holders within a stock sell less than composition predicts [37]. That relative version is testable in 13F data, and it is new.

**Novel increment.** Three tests: (1) dispersion against next-year crash indicators, NCSKEW and DUVOL in the US, alongside short-horizon ownership level; (2) a horse race against Greenwood-Thesmar fragility, since dispersion may be a cheap proxy for low flow covariance [36][37]; (3) a relative-absorption regression in 2008Q3-Q4, 2020Q1 and 2022, instrumented with Coval-Stafford flow-induced selling [38]. The stated threshold for upgrading B to a standalone short paper is a dispersion-to-crash coefficient with t above 3 surviving fragility, level and liquidity controls in both 1982-2016 and 2013-2026 samples [37]. Committed verdict: a module, publishable alone only in the JFS-JBF-JIFMIM tier.

### 3.4 Pivot C: price-drift contamination

**Already done.** The Gaspar-Massa-Matos churn subtracts the passive price change from the numerator [20]; Yan-Zhang use the same numerator and add the minimum-of-buys-and-sells cash-flow correction [21]; Chan-Cheng-Hameed show share-based robustness [6]. Committed verdict: C is a footnote. The one useful increment is practical. Anyone building value-weighted measures from the SEC flat files must rescale market values for filings before January 3, 2023 [10], and the project's own numbers show that skipping this moves a headline correlation from -0.526 to -0.641. That belongs in a data appendix, and possibly in a short data note, not in a journal article's contribution list.

### 3.5 Pivot D: horizon homophily in co-holding

**Partly done and mostly mechanical.** Type-assortative co-holding is documented by Crane-Koch-Michenaud [40], horizon-sorted flow comovement by Chan-Cheng-Hameed [6], and the right null by Gualdi et al. [39]. The interim assessment expects the coefficient to shrink by well over half once cosine is computed on active weights, tau is share-based, and dyadic regressions carry node fixed effects, same-type and same-family controls [22]. Committed verdict: D survives as Table 1 of the pivot, the motivating fact that horizon-proximate institutions are disproportionately linked, which is precisely why A needs a shock. Reframing D this way turns a weakness into the paper's own argument for its identification strategy.

### 3.6 Pivot E: calibrated adaptive-horizon ABM

**Not done in this form.** LeBaron's horizons evolve by wealth-based selection with no network [29]; Nishiwaki's horizons are fixed in a switching model [30]; the PLOS ONE study calibrates horizons to index series, not holdings [31]; Oldham's horizons are fixed classes, his links follow performance through class-specific Oracle lists, and he calibrates nothing [17]. One caveat on wording: because Oldham's Oracle lists are class-specific, his network is class-assortative as a by-product, so the CME should claim "similarity-based link formation", not "first homophily" [17].

**Novel increment.** The bridge from a reduced-form peer coefficient to a structural adaptation parameter is simple: in DeGroot updating with a row-normalised neighbour matrix, the linear-in-means coefficient on neighbours' average horizon equals the adaptation weight, so the model's assumed 0.06 per quarter becomes directly comparable to an estimated quarterly beta [10]. No reviewed paper ties an estimated network peer coefficient to an ABM adaptation parameter [10]. Committed verdict: E is novel and worth doing, but only as the final section of A, because the journals where it could stand alone sit at JIF 1.8 and 2.7 [18][19].

## 4. Recommended Pivot

### 4.1 The recommendation in one sentence

Pivot to a paper on horizon contagion among institutional investors (working title: "Do Investment Horizons Spread? Peer Effects in Institutional Trading Horizons and Stock Fragility"), executed as a staged programme in which Pivot A is the headline, Pivot B supplies the consequences, Pivot E supplies the discipline, D is the motivating fact and C is the data appendix, with explicit kill criteria that tell the team, before each stage, which product it will publish if the stage fails.

### 4.2 Why a staged programme rather than a single bet

The decisive argument is about expected value under uncertainty. The audit's confidence that A is novel is about 70%, but the identification audit rated even a shock design only about 70% credible [43], and the adversarial round cut that to about 50% once merger shocks were shown to be confounded [12][13]. A team that writes the full A paper first and discovers at the referee stage that its shocks fail pre-trends has nothing. A team that runs the stages in order converts every failure into a smaller paper. This is also the honest response to Angrist's warning that well-identified peer designs have often found little: the programme must be built so that a null is informative and publishable [8].

The ordering is not arbitrary. Each stage is cheaper than the next, each produces an input the next needs, and the fallback products are ordered by the journals they reach. Stage 0 is free with SEC data [9]. Stage 1 uses only own-horizon data and the network. Stage 2 needs manager data from CRSP or Morningstar. Stage 3 needs CRSP returns. Stage 4 needs the Stage 2 coefficient.

### 4.3 The decision tree

| Stage | Test | Pass criterion | If it fails | Fallback product and venue |
|---|---|---|---|---|
| 0. Data rebuild | Full-universe, share-based tau from SEC 13F Data Sets; unit break corrected; CUSIP and amendment cleaning | Horizon ranks and within-variance share stable relative to the top-150 cache | Investigate; nothing proceeds on contaminated data | Corrected CME as an FRL letter or erratum-style revision |
| 1a. Variance gate (pre-registered) | Residual var(log tau) after institution, quarter, style-by-quarter fixed effects and flow controls | At least 10% of total variance remains, residual AR(1) not near zero | Horizon is a trait; kill A | B plus E package (Section 5) |
| 1b. Descriptive peer test (pre-registered) | Own Delta log tau on lagged non-held-stock neighbour horizon, style-by-quarter FE, same-family exclusion | Positive coefficient; future-neighbour placebo near zero | Selection or common factor dominates; kill causal A | Bounded descriptive A plus D plus B at JFS or JBF |
| 2. Shock design | Neighbour manager deaths and departures as shocks to neighbour horizon | At least about 30 usable shocks, no pre-trends, first stage on neighbour horizon | Too few or contaminated shocks | Stage 1b with partial-identification bounds plus B |
| 3. Consequence module (B) | Dispersion against crash risk; horse race with fragility; relative absorption | t above 3 surviving controls in both samples | B becomes a robustness section | Still useful as a section |
| 4. Model module (E) | ABM calibrated to Stage 2 beta and Stage 3 absorption; out-of-sample on later quarters | Beats naive persistence benchmark for horizon-diversity path | Report as illustration only | JEDC or JEBO companion paper (below threshold) |

The 10% variance threshold and the roughly 30-shock threshold come from the interim analyses [11][43]. The first half of gate 1a is already passed in the project's own data: after institution and quarter fixed effects, 33% of var(log tau) remains, and quarter fixed effects alone explain about 2%. That finding is informative in a way neither camp anticipated. The trait camp's strongest evidence was that the common market-wide component dominates (Pastor-Stambaugh-Taylor's 95% first-component correlation [41]); in this 13F panel the market-wide component is small, so the threat is style-level rather than market-wide, which is exactly why style-by-quarter fixed effects are the binding control rather than quarter fixed effects [11][43]. The second half of gate 1a (adding style-by-quarter and flows) has not been run and must be pre-registered before it is.

### 4.4 Pre-registration as a credibility device

The orchestrating analysis ran its variance check outcome-free, on own-horizon data only. The pivot should formalise that discipline. Before estimating any peer coefficient, the team should post (on OSF or as a dated SSRN appendix) the outcome definition (quarterly change in share-based log tau), the network definition (active-weight cosine, top-k or BiCM-validated, formed with a lag), the neighbour-horizon construction (non-held stocks only), the fixed-effect structure, the placebo, and the kill thresholds in the table above. In a literature where Angrist's critique is the first thing a referee reaches for [8], a pre-registered specification is worth more than an extra robustness table, and it costs nothing.

### 4.5 Forward-looking implications

The pivot's relevance grows rather than fades over the next several years. Chen, Lu and Qin motivate their paper with regulatory concern in China about homogeneous institutional behaviour and convergent quantitative trading, and with policy documents in 2022 and 2024 calling for differentiated development of securities and fund institutions [16]. If horizons spread through overlap networks, then the rise of convergent strategies is not merely a composition shift but a feedback process, and the Golub-Jackson result implies that homophily will slow cross-group convergence while accelerating within-group convergence, producing exactly the clustered horizon distribution that Chan-Cheng-Hameed associate with low liquidity [33][6]. Inference, stated with provenance: if A's peer coefficient is positive (the Froot-Scharfstein-Stein prediction [32]) and B's dispersion-fragility link holds [6][16], then shocks that shorten a cluster of neighbours' horizons should predict future fragility in the stocks that cluster holds, a testable early-warning signal that no current fragility measure contains. That is the policy-facing payoff a financial-stability journal will want, and it is also the bridge to the team's N-PORT bond-fund data, where corporate-bond fire sales are a natural second market for the same mechanism.

## 5. Target Journals and Fit

### 5.1 The impact-factor bar is not the binding constraint

Impact factors are volatile and a poor proxy for standing in finance. The Review of Finance report lists 2024 JIFs of 12 for JFE, 9.5 for JF, 8.4 for RoF, 5.4 for RFS, 4.9 for Management Science, 3.8 for JBF, 3.7 for JFI and 2.8 for JFQA [23]. JFQA reports a 2025 JIF of 4.1 [24], and the RFS note records a 2025 JIF of 7.6 from a secondary snippet [44]. Meanwhile, high-volume Elsevier titles sit well above several elite journals: IRFA reports 10.2, FRL 7.1, JCF 6.9 and JIFMIM 6.0 [45][28] [46][27]. An aggregator based on field-normalised citations puts 78.2% of recent RFS work and 53.6% of recent Management Science work in the global top 10% for their field [44][47]. The practitioner's reading is that the team should aim by fit and standing, and use the impact-factor bar only to exclude venues, chiefly JEDC (1.8) and JEBO (2.7) [18][19].

### 5.2 Module-to-journal map

| Product (stage reached) | Primary target | Fit rationale | Alternatives |
|---|---|---|---|
| Full programme: identified A, plus B and E (passes Stage 2) | Review of Finance (8.4) | Broad empirical asset-pricing and institutions scope; accepts a model section alongside empirics; highest 2024 JIF among the core finance journals after JFE and JF [23] | Management Science (4.9) [23]; JFQA (4.1 in 2025) [24]; RFS as a stretch [23] |
| Descriptive A with bounds, plus D and B (fails Stage 2, passes 1b) | Journal of Financial Stability (4.1) | Scope is causes and prevention of crises, including securities markets [25] | JBF (4.0), whose scope lists asset management, networks and liquidity [26]; IRFA (10.2) [45] |
| B alone (A killed at Stage 1) | JFS (4.1) or JBF (4.0) | Fragility and liquidity in stress [25][26] | JIFMIM (6.0) for a US-versus-China comparison against Chen-Lu-Qin [27][16] |
| B as a short transnational test | Finance Research Letters (7.1) | FRL explicitly welcomes transnational applicability and methodological contingency, and excludes single-country replications of well-established results, which a US test of a China finding is not [28] | none needed |
| E alone | JEDC (1.8) or JEBO (2.7) | Natural ABM homes, below the bar [18][19] | Bundle with A instead |
| C alone | Not recommended | Pre-empted [20][21] | Data appendix |

The Journal of Corporate Finance (6.9) is a poor fit unless the paper adds corporate outcomes [46]. FRL deserves one caution: its letters run under 2,500 words [28], so the full programme cannot be compressed into it, but it is a credible venue for the B transnational test or for a corrected and narrowed version of the current paper.

## 6. Identification Strategy and Data Upgrades

### 6.1 Step zero: rebuild the panel

Everything starts from the free SEC Form 13F Data Sets, which provide every filer, share counts, and as-filed XML extracts from mid-2013 [9][10]. Five rebuild rules follow. (1) Use share-based churn in the Gaspar-Massa-Matos form, with the Yan-Zhang minimum-of-buys-and-sells variant as robustness [20][21]. (2) Rescale VALUE for filings before January 3, 2023, by filing date, not report quarter, because the project's 1000x jump at 2022Q4 suggests mixed vintages within the quarter [10]. (3) Clean amendments, notice filings, put and call rows, shares versus principal, and CUSIP errors, which the SEC disclaimer leaves to the user [9]. (4) Build the network on the full universe (about 5,000 or more filers per quarter) and keep the top-150 sample only as an estimation subsample [10]. (5) Add CRSP for returns, delistings and permno mapping, which removes the survivor bias of the current stock-level exhibit.

Rule (4) deserves emphasis because it answers the sampled-network critique for free. Chandrasekhar and Lewis show that instruments constructed from the full graph remain valid even when the second stage is restricted to a sampled subset of nodes [7]. The team can therefore keep its well-understood top filers as the estimation sample, as long as neighbour horizons and friends-of-friends are computed on the full network. The full universe sharpens the Canen-Chadha density problem [42], so the network should be a thresholded top-k or BiCM-validated graph [39], whose sparsity the team can tune and report. The project's own diagnostic (32 to 42 non-friend friends-of-friends per node at top-5) suggests intransitivity will not be the binding problem.

### 6.2 Stage 1: the pre-registered descriptive peer test

The baseline regression is the quarterly change in own share-based log tau on the lagged average log tau of overlap neighbours, where neighbour horizon is computed only from neighbours' trades in stocks the focal institution does not hold. Required controls: institution fixed effects; style-by-quarter fixed effects, where style is Bushee type or an AUM-by-concentration cell; own lagged flows and AUM growth; neighbours' flows; and exclusion of same-parent and same-family neighbours. The Pastor-Stambaugh-Taylor same-category averages enter explicitly, because their regression shows category averages are highly significant over and above the market-wide average [5]. Three placebos: future neighbours (links formed at t+4), matched non-neighbours with the same style and size, and neighbour horizon computed from held stocks (which should be larger if mechanics dominate). With AR(1) near 0.75 and 50 quarters, Nickell bias in a fixed-effect dynamic panel is a concern of the order of a few hundredths in the persistence coefficient; this is an inference from the standard approximate bias formula, not from a source, and it argues for estimating in first differences with lagged-level instruments or reporting bias-corrected estimates. Leave-out neighbour means bias against finding convergence [43], so a positive estimate is conservative on that dimension.

### 6.3 Stage 2: the shock design

The primary shock is a departure or death of a neighbour's portfolio manager. Liu et al. supply the precedent that parental deaths shift a fund's style toward quasi-indexing, with effects strongest for unexpected events and single-manager funds [14]. For Pivot A, the event is a first stage on the neighbour's horizon, and the outcome is the focal institution's horizon in subsequent quarters, in an event-study design with pre-trends and with the same placebos as Stage 1. Two design choices follow from the record. First, filer mergers move to robustness only, pooled and excluding BlackRock-BGI, because Lewellen-Lowry show that merger samples are dominated by that event and its timing [12], and Massa-Schumacher-Wang show that mergers directly change neighbours' holdings through anticipated fragility, which violates the exclusion restriction [13]. Second, the funding-fragility instrument of Cella-Ellul-Giannetti (a neighbour's historical performance-withdrawal correlation) is a valid secondary source of exogenous neighbour horizon, since it captures horizon driven by funding structure [34], provided it is interacted with time variation rather than used as a static characteristic.

The kill rule is about 30 usable shocks with no pre-trends [43]. Liu et al. found 304 events over 15 years in mutual-fund data [14], so the arithmetic suggests the full-universe 13F sample can supply enough manager events once 13F filers are linked to fund-level manager data, but a 13F filer aggregates many funds, which dilutes a single manager's shock. Inference, with provenance: combining Liu et al.'s event count [14] with the dilution implied by filer-level aggregation, the shock design is most powerful for small and single-strategy filers (boutiques, hedge funds), so the team should report effects by filer size and expect identification to come disproportionately from the short-horizon end, which is also where the Froot-Scharfstein-Stein complementarity bites hardest [32].

Friends-of-friends instruments enter only as a robustness check, with first-stage F statistics, Anderson-Rubin confidence sets and row-scaled adjacency, following Canen-Chadha [42].

### 6.4 Stage 3: the B module

Outcomes: next-year crash indicators, NCSKEW and DUVOL, and Greenwood-Thesmar fragility-adjusted volatility [36]. Regressors: ownership-weighted dispersion of holders' share-based log tau, short-horizon ownership level, IO breadth, size and liquidity, with Chan-Cheng-Hameed's own controls (number of funds, IO, illiquidity and liquidity volatility) reproduced [15]. Report the volatility slope next to Chan-Cheng-Hameed's appendix as a replication. The absorption test regresses long-horizon holders' change in shares held on short-horizon net selling, interacted with dispersion, in 2008Q3-Q4, 2020Q1 and 2022, instrumenting short-horizon selling with Coval-Stafford flow-induced trades [38][37]. Quarterly 13F hides intra-quarter round trips, so the claim must be relative absorption, consistent with Glossner et al.'s finding that retail took the other side in aggregate [35].

### 6.5 Stage 4: the E module

Calibrate two parameters from data rather than assumption: the adaptation rate from the Stage 2 beta, via the DeGroot equivalence [10], and the strength of an added absorption channel from the Stage 3 estimates. Replace the hard-wired friction channel with both channels and let the data choose the net sign, which reconciles LeBaron's destabilising mixture [29] with the stabilising empirical sign [15]. Hold out the later part of the sample (for example, calibrate on 2013-2019 and test on 2020-2026), and require the model to beat a naive persistence benchmark for the path of cross-sectional horizon dispersion. Use Golub-Jackson spectral homophily to derive an analytic convergence-time prediction that the simulation can be checked against [33].

### 6.6 What CRSP/WRDS adds

CRSP adds delisting returns and survivor-free prices (removing the current survivors-only restriction), permno mapping, and the CRSP mutual-fund database with manager names and flows, which Stage 2 cannot do without. Thomson s34 adds pre-2013 history for out-of-sample checks against Chan-Cheng-Hameed's 1982-2016 window, but it has known omissions, so it should be a robustness source, not the backbone [10].

## 7. Referee Objections the Pivot Must Survive

Ranked by lethality, with the answer each requires.

**7.1 "This is common shocks, not contagion."** The strongest objection. Fund turnover has a common component tied to sentiment, dispersion and liquidity, and commonality is especially high among similar funds [5]; same-horizon funds receive correlated flows [6]. Answer: style-by-quarter fixed effects, explicit category-average controls, neighbours' flows as controls, the future-neighbour placebo, and the shock design. The project's 2% quarter-FE share is helpful context, because it shows the market-wide component is small in this panel, but it does not answer the style-level version.

**7.2 "Neighbours are selected on horizon, so you have homophily, not influence."** The paper's own Pivot D fact is the referee's argument [43]. Answer: links formed with a lag and held fixed, shocks that originate in a neighbour's personnel rather than strategy [14], and a demonstration that the effect does not appear for future neighbours. Report D as the reason for the design, not as a separate finding.

**7.3 "Outcome-on-mean regressions are mechanical."** Angrist [8]. Answer: the headline estimate comes from manipulated neighbour characteristics (the shock), not from a group-mean regression; the descriptive Stage 1 estimate is labelled as such, and leave-out exclusion bias is discussed as working against the result [43].

**7.4 "Your network is a sample, so your instruments are invalid."** Chandrasekhar-Lewis [7]. Answer: full-universe network construction with a restricted second stage, which their own Proposition 3.4 shows to be valid [7].

**7.5 "Horizon is a fixed trait; there is nothing to transmit."** Persistence in ranks is documented, and Cella-Ellul-Giannetti describe horizon as a permanent characteristic in an untabulated check [11]. Answer: the variance decomposition is the first table of the paper, showing 33% residual variance after institution and quarter fixed effects (the project's own data) and reporting the style-by-quarter and flow-adjusted residual; the paper then argues, as the reconciliation does, that ranks persist while levels move.

**7.6 "Your merger shocks are confounded."** Lewellen-Lowry and Massa-Schumacher-Wang [12][13]. Answer: mergers are robustness only, pooled and excluding BlackRock-BGI; the primary shock is personnel-based.

**7.7 "Turnover from quarterly 13F is a noisy horizon proxy and your earlier work was contaminated."** Answer: share-based churn with standard drift adjustment [20][21], the documented unit-break correction [10], robustness to Lan-Moneta-Wermers-style holding-horizon measures [11], and a candid data appendix. Turning the team's discovery of contamination into visible data hygiene is a credibility gain.

**7.8 "Pivot B is Chan-Cheng-Hameed again, and China already did tail risk."** Answer: cite both prominently [6][16], report the volatility result as a replication of the appendix table [15], and claim only the US crash outcomes, the fragility horse race and the relative-absorption test.

**7.9 "Long-horizon institutions do not absorb anything; retail does."** Glossner et al. [35] and Cella-Ellul-Giannetti [34]. Answer: the claim is relative absorption, defined before estimation, with the Coval-Stafford instrument [38].

**7.10 "The ABM is a black box with assumed parameters."** Answer: both key parameters are estimated, the model is tested out of sample, the friction-only sign is withdrawn, and Oldham is cited as the nearest model with the precise difference stated [17].

**7.11 "Why should finance readers care about the Fractal Market Hypothesis?"** Many will not. Answer: drop FMH from the title and abstract, frame the paper around peer effects, fragility and the Froot-Scharfstein-Stein complementarity [32], and keep FMH as one sentence of intellectual history.

**7.12 "Has someone already done this?"** Answer: cite the commonality literature [5] and the institutional peer-effect literature [2][3] [4] as boundary markers, word the claim narrowly ("first identified peer effect in institutional trading horizons", not "first peer effects among institutions") [1], and read the outstanding 2025 SSRN quantity-based peer-effect title before submission.

**Committed close.** The programme wins on expected value because it never bets the team's time on a single identification argument. The reconciliation the angle promised is concrete: the novelty camp gets its estimand, the identification camp gets its shock design and kill criteria, the trait camp gets the variance decomposition as Table 1, the stabilisation camp gets its sign in the model, and every gate the paper fails still leaves a publishable module.

## Sources

[1] Interim report - pivot-a-near-duplicate-audit. (internal interim research note; no URL)

[2] NBER WORKING PAPER SERIES (Hong, Kubik, Stein, Thy Neighbor's Portfolio, w9711). https://www.nber.org/system/files/working_papers/w9711/w9711.pdf

[3] The People in Your Neighborhood: Social Interactions and Mutual Fund Portfolios (Pool, Stoffman, Yonker, JF 2015). https://ideas.repec.org/a/bla/jfinan/v70y2015i6p2679-2732.html

[4] Network externalities in mutual funds (Blocher, JFM 2016). https://ideas.repec.org/a/eee/finmar/v30y2016icp1-26.html

[5] NBER WORKING PAPER SERIES (Pastor, Stambaugh, Taylor, Do Funds Make More When They Trade More?, w20700). https://www.nber.org/system/files/working_papers/w20700/w20700.pdf

[6] Investor Heterogeneity and Liquidity (Chan, Cheng, Hameed, JFQA 2022). https://web2-bschool.nus.edu.sg/wp-content/uploads/media_rp/publications/vDsxi1613376975.pdf

[7] ECONOMETRICS OF SAMPLED NETWORKS (Chandrasekhar and Lewis). https://stanford.edu/~arungc/CL.pdf

[8] NBER WORKING PAPER SERIES (Angrist, The Perils of Peer Effects, w19774). https://www.nber.org/system/files/working_papers/w19774/w19774.pdf

[9] SEC.gov | Form 13F Data Sets. https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets

[10] Interim report - data-upgrade-and-abm-calibration. (internal interim research note; no URL)

[11] Interim report - horizon-trait-or-time-varying. (internal interim research note; no URL)

[12] Does Common Ownership Really Increase Firm Coordination? (Lewellen and Lowry, JFE 2021). https://corpgov.law.harvard.edu/2021/05/21/does-common-ownership-really-increase-firm-coordination/

[13] EconPapers: Who Is Afraid of BlackRock? (Massa, Schumacher, Wang, RFS 2021). https://econpapers.repec.org/RePEc:oup:rfinst:v:34:y:2021:i:4:p:1987-2044.

[14] Life is Too Short? Bereaved Managers and Investment Decisions - Review of Finance (Liu, Sulaeman, Shu, Yeung, RoF 2023). https://revfin.org/?p=3058

[15] Internet Appendix (Chan, Cheng, Hameed, JFQA 2022, Internet Appendix). https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S0022109022000217/resource/name/S0022109022000217sup001.pdf

[16] DOI: 10.16538/j.cnki.fem.20260118.204 (Chen, Lu, Qin, Institutional investor trading homogeneity and left-tail systemic risk, Foreign Economics & Management 48(5), 2026). https://qks.sufe.edu.cn/J/PDFFull/TxMBou5H-3rV2-xA64-7Pf5-V5uQq9LSBWGd.pdf

[17] Oldham 2019 Complexity full text (Wayback PDF): short-termism and dynamic investor network ABM (Oldham, Complexity 2019). https://web.archive.org/web/20220726165036if_/https://downloads.hindawi.com/journals/complexity/2019/1715624.pdf

[18] Journal of Economic Dynamics and Control | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-economic-dynamics-and-control

[19] Journal of Economic Behavior & Organization | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-economic-behavior-and-organization

[20] Journal of Financial Economics 76 (2005) 135-165 (Gaspar, Massa, Matos, Shareholder investment horizons and the market for corporate control). https://www.darden.virginia.edu/sites/default/files/inline-files/gasparmassamatoshorizonsmajfeapr05.pdf

[21] Institutional Investors and Equity Returns: (Yan and Zhang, RFS 2009). https://www.lehigh.edu/~xuy219/research/horizon_RFS.pdf

[22] Interim report - horizon-homophily-fact-or-mechanical. (internal interim research note; no URL)

[23] Review of Finance (Review of Finance, Report from the Managing Editor, 2025). https://revfin.org/wp-content/uploads/2025/08/RF-Report-2025_FINALv2-1.pdf

[24] Journal of Financial and Quantitative Analysis | Cambridge Core. https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis

[25] Journal of Financial Stability | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-financial-stability

[26] Journal of Banking & Finance | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-banking-and-finance

[27] Journal of International Financial Markets, Institutions and Money | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-international-financial-markets-institutions-and-money

[28] Finance Research Letters | Journal | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/finance-research-letters

[29] EconPapers: EVOLUTION AND TIME HORIZONS IN AN AGENT-BASED STOCK MARKET (LeBaron, Macroeconomic Dynamics 2001). https://econpapers.repec.org/RePEc:cup:macdyn:v:5:y:2001:i:02:p:225-254_01

[30] Impact of different investment horizons in heterogeneous agent models: Do long-term traders bring market stability? (Nishiwaki, JEBO 2022). https://ideas.repec.org/a/eee/jeborg/v196y2022icp393-401.html

[31] Calibrating emergent phenomena in stock markets with agent based models - PMC (PLOS ONE 2018). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5834198/

[32] Herd on the Street: Informational Inefficiencies in a Market with Short-Term Speculation | NBER (Froot, Scharfstein, Stein, JF 1992). https://www.nber.org/papers/w3250

[33] How Homophily Aﬀects the Speed of (Golub and Jackson, QJE 2012). https://web.stanford.edu/~jacksonm/homophily.pdf

[34] ISSN 0956-8549-717 (Cella, Ellul, Giannetti, Investors' Horizons and the Amplification of Market Shocks, RFS 2013). https://eprints.lse.ac.uk/119037/1/DP717.pdf

[35] Do Institutional Investors Stabilize (Glossner, Matos, Ramelli, Wagner, Do Institutional Investors Stabilize Equity Markets in Crisis Periods? Evidence from COVID-19). https://www.ecgi.global/sites/default/files/2026-10/fin-688-2020_do_institutional_investors_stabilize_equity_markets_in_crisi.pdf

[36] Stock price fragility (Greenwood and Thesmar, JFE 2011). https://tevgeniou.github.io/EquityRiskFactors/bibliography/Fragility.pdf

[37] Interim report - dispersion-and-absorption-beyond-chan-cheng-hameed. (internal interim research note; no URL)

[38] NBER WORKING PAPER SERIES (Coval and Stafford, Asset Fire Sales (and Purchases) in Equity Markets, w11357). https://www.nber.org/system/files/working_papers/w11357/w11357.pdf

[39] Statistically validated network of portfolio overlaps and systemic risk - PMC (Gualdi, Cimini, Primicerio, Di Clemente, Challet, Scientific Reports 2016). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5175158/

[40] Institutional Investor Cliques and Governance (Crane, Koch, Michenaud). https://www.lebow.drexel.edu/sites/default/files/1488309013-crane-kochmichenaudinstitutional-investor-cliques.pdf

[41] NBER WORKING PAPER SERIES (Pastor, Stambaugh, Taylor, w20700 earlier revision). https://www.nber.org/system/files/working_papers/w20700/revisions/w20700.rev0.pdf

[42] Empirical Challenges with Peers-of-Peers Instruments (Canen and Chadha, 2026). https://arxiv.org/pdf/2602.24215

[43] Interim report - correlated-turnover-vs-horizon-contagion-identification. (internal interim research note; no URL)

[44] Review of Financial Studies: Journal Quartile & Metrics Score 2026. https://www.journalmetrics.org/journal/review-of-financial-studies

[45] International Review of Financial Analysis | Journal | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/international-review-of-financial-analysis

[46] Journal of Corporate Finance | ScienceDirect.com by Elsevier. https://www.sciencedirect.com/journal/journal-of-corporate-finance

[47] Management Science: Journal Quartile & Metrics Score 2026. https://www.journalmetrics.org/journal/management-science
