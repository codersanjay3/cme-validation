# Prompt for Claude Design

Copy everything below into Claude Design to generate the deck.

---

Create a clean, academic-style slide deck (5 slides, 16:9) for a 10-15 minute meeting with a finance professor. Two high school researchers are presenting a research project on market microstructure to Professor John Chalmers (Abbott Keller Professor of Finance, University of Oregon), whose own work spans mutual fund trading costs, financial advice, and retirement/target-date fund design. The tone should be confident but genuinely curious — this is a discussion with an expert, not a pitch. Present it as an ongoing research project and open questions, never as a finished paper or submission — don't use the words "paper," "manuscript," or "submission" anywhere in the deck. Use a restrained navy/charcoal/gold palette, generous whitespace, one idea per slide, minimal bullet clutter, and simple custom diagrams (network graphs, line charts) instead of clip art. Include slide numbers and "Sumedh Seetharaman & Sanjay Subramanian" as a footer.

Build these 5 slides with this exact content:

**Slide 1 — Title**
"How Trading Horizons Shape Market Stability"
Subtitle: "A network view of temporal heterogeneity in financial markets"
Sumedh Seetharaman & Sanjay Subramanian — Meeting with Professor John Chalmers

**Slide 2 — The core idea**
Headline: "Every trader has a chronotype"
Content: Markets aggregate wildly different timescales — high-frequency traders react in milliseconds, hedge funds hold for weeks, mutual funds and pension funds rebalance over months or years. We define a trader's chronotype as the lookback window (τ) they use to evaluate price signals, and build an agent-based market (four calibrated investor types, from HFT to pension funds) where traders with similar chronotypes preferentially form trading ties — a behavior we call temporal homophily. Include a simple network-graph diagram: nodes colored/clustered by horizon length, with denser ties among similar-colored nodes.
Framing question at the bottom: "What happens to a market when similar-horizon participants cluster together — and what happens when that clustering erodes over time?"

**Slide 3 — What we found**
Headline: "A stabilizing force that quietly destabilizes itself"
Content, as three compact findings:
— Short-run: clustering by horizon suppresses volatility (~1.3x) and price fragmentation (~14x) by reducing "cross-horizon friction" between short- and long-horizon traders.
— Long-run: when traders adapt toward their neighbors' horizon, overall horizon diversity erodes at every clustering level we tested — a kind of temporal echo chamber.
— A sweet spot: a composite "temporal liquidity" measure peaks at moderate clustering, then falls off at higher levels — too little clustering means friction, too much means fragmented cliques.
Include a simple line chart showing an inverted-U liquidity curve over clustering strength, with the peak marked "Goldilocks zone."
Small footnote line: "A first check against SEC 13F institutional holdings data (2013-2024) shows the same pattern in real markets: quarters with more compressed horizon diversity among institutions tend to be higher-volatility quarters (r = -0.526, p = 0.0002)."

**Slide 4 — Where your work comes in**
Headline: "This is where we'd love your perspective"
Content, written as direct connections rather than citations:
— Your work on mutual fund trading costs shows costs scale with how a fund trades and how often it turns over its portfolio. Our model treats "cross-horizon friction" as a cost-like force — but it's modeled, not measured. Does your trading-cost data suggest institutions actually see higher costs trading against very different-horizon counterparties?
— Your research on financial advisors and target-date fund design deals directly with how retirement investors' horizons get shaped and sometimes homogenized by design choices and advice. Our longest-horizon agents are modeled on pension-type investors — do you see advisor behavior or target-date restructuring as a real-world channel that shifts horizon distributions the way our clustering parameter does?

**Slide 5 — Questions for discussion**
Headline: "Where we'd like to take this"
List as open questions, not statements:
— Does your trading-cost data support treating "cross-horizon friction" as a real, measurable cost rather than just a modeling assumption?
— In your experience with retirement plan design, does simplification (e.g., default target-date funds) measurably narrow the range of investor horizons over time?
— What data source would you trust most for identifying investor "chronotype" directly, rather than inferring it from portfolio turnover the way we do?
— Is the stability/liquidity trade-off we're finding something you'd expect to see in other network-based markets you've studied?
Footer line: "Thank you for considering a conversation with us."

---

Additional formatting notes for Claude Design: keep text per slide under ~70 words outside of slides 4 and 5 (those can run slightly longer since they're discussion-driven); use one clear visual per data-heavy slide (2 and 3) rather than dense tables; avoid academic jargon like "TDI," "TMFI," or Greek letters in slide text — spell concepts out in plain English (e.g., "horizon-diversity index" instead of "TDI").
