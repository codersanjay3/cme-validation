# Slide Deck Specification: Follow-Up Meeting with Professor Chalmers

**Project:** "Chronotypic Market Ecology" (CME) research paper
**Presenters:** Sumedh Seetharaman and Sanjay Subramanian
**Audience:** Professor John Chalmers (finance professor, not an author, smart but not steeped in our model)
**Deliverable you are building:** one slide deck (PowerPoint or PDF), 17 main slides plus 10 appendix slides, with speaker notes on every slide
**Target talk length:** 18 to 22 minutes of speaking, leaving 10 or more minutes for his questions

Read this whole document before you start. Section 2 is the most important: it records exactly how the professor told us to build presentations, and every slide below is designed to obey it.

---

## 1. What this deck is for

At our last meeting we presented a five-slide progress update to Professor Chalmers. He gave detailed feedback. Since then we did a large amount of work, including work that overturned some of our earlier claims. This deck has four jobs:

1. Show him what we did in response to each of his suggestions.
2. Show him the new changes and findings we made beyond his suggestions, honestly, including the ones that weakened the paper.
3. Ask him for help getting access to a standard finance database (CRSP, reached through a service called WRDS).
4. Ask for his opinion on whether we should change the simulation model, because our data and our model disagree on one important point.

The tone is honest, plain, and collaborative. We are not selling. We are reporting results, including bad news, and asking for guidance. He responded well last time to honesty ("no results are good", "that's fine"), so do not hide weaknesses.

---

## 2. The professor's presentation rules (from the meeting notes). OBEY THESE.

These are paraphrased from his comments at the last meeting. Each rule is followed by what it means for the deck.

**Rule 1. "Every presentation you give, you should start out with what it is you're doing and why you're doing it."**
He said this twice, and also: "no matter when you present this, how many times you present it, to the extent that you're talking to someone other than Sanjay, you probably need to start at the very beginning."
- Slides 2 and 3 exist only for this. They restate the question and the model from scratch in plain English before any result. Do not skip or shrink them.
- Every result slide must open with a one-line "Question this answers" banner so the audience is never lost.

**Rule 2. "Acronyms are usually getting in the way of communication. My favorite acronym is DWAY: don't use acronyms."**
- No acronym appears on a slide unless it is spelled out in the same slide and is a proper name (for example VIX, a published index; see the glossary in Section 3).
- Replace our private jargon with plain English everywhere. TDI becomes "horizon diversity". The clustering estimate becomes "horizon clustering score". Section 3 gives the full mapping.
- Do not put Greek letters or model symbols (tau, kappa, lambda) on main slides. Appendix only, and always next to the plain-English name.

**Rule 3. "It's often really helpful for somebody who's listening to see the data itself. You don't need to show a whole bunch of it, you just show a sample. This is what our data looks like, this is what we're going to do with it."**
- Every result slide that estimates something must be preceded, on that slide or the one before, by a small table of actual sample data (3 to 6 rows) and a plain statement of what we do with it ("we correlate column A with column B across all pairs").
- Slide 5 is the dedicated "what the data looks like" slide with a real worked example.

**Rule 4. "You'll want to actually spell it out for a couple of simple examples. Show me how this works, to make sure they understand what you're doing precisely. That's true with the first box too."**
- The professor could not follow the "co-holding" estimate until two funds were walked through. Slide 5 and slide 7 use a concrete two-institution example with real numbers.
- The bond slide (slide 9) also needs a concrete example of one fund over time.

**Rule 5. "I do still need you to explain what this horizon diversity index is and how you made it... you're going to have to really show me how you created your measures."**
- Slide 6 is entirely about how horizon and horizon diversity are built, step by step, with a toy example whose arithmetic is shown.

**Rule 6. "Make sure your question is clear."**
- Each result slide has the "Question this answers" banner. Phrase it as a real question ending in a question mark.

**Rule 7. "You both talk very fast. Just slow down."**
- Speaker notes must be written for slow delivery: short sentences, one idea per sentence, no more than about 90 words of spoken text per slide. Put a "PAUSE" marker after each key number.
- Never put more than one headline number per slide as the largest element. Supporting numbers go small.

**Rule 8. "You want to make sure people follow exactly what you're doing, and if they aren't, that you have an easy way to get them back into the question you're answering."**
- Add a small persistent "where we are" strip at the bottom of every slide showing the 4 parts of the talk, with the current part highlighted (see Section 4).

**Rule 9 (from his substantive feedback, to be reflected in content):**
- On the number of lags in the Newey-West correction: "Do you have 17 lags? Most of the time people don't use that many. There are tests for how many lags you need." Slide 8 answers this directly.
- On the bond market: "No results are good... compare and contrast... look across bond funds, a treasury bond fund versus a corporate bond fund or a junk fund, they have very different information environments." Slide 9 answers this.
- On the finding that volatility drives the horizon measure: "You need to explore what the mechanism is... people trade more when volatility is high... there's a paper by Harris and Raviv, 'Differences of Opinion Make a Horse Race'." Slide 11 answers this.
- On the data: "People make big mistakes when they don't know their data, for example they think they have no zeros and they have a bunch of zeros and then they take a log." Appendix slide A8 shows our data checks.

---

## 3. Plain-English glossary (use these words on slides)

| Private term in our paper | What to write on slides | One-line explanation to put on first use |
|---|---|---|
| tau (lookback horizon) | **trading horizon** | How long an investor typically holds a position, measured in trading days. |
| TDI (Temporal Diversity Index) | **horizon diversity** | How spread out investors' trading horizons are. High means a healthy mix of short and long holders. |
| kappa-hat (estimated kappa_h) | **horizon clustering score** | Do investors with similar horizons hold similar stocks? Positive means yes. |
| temporal homophily | **horizon clustering** (or "like trades with like") | Investors with similar horizons tend to deal with each other. |
| 13F filings | **quarterly holdings reports** | Reports that large US investment managers must file with the SEC each quarter, listing the stocks they own. |
| N-PORT filings | **bond fund holdings reports** | The equivalent reports for bond funds. |
| CUSIP | **security ID** | A nine-character code that uniquely identifies each stock or bond. |
| VIX | **VIX (the stock market "fear gauge")** | A published index of how much volatility options traders expect in US stocks. Keep the name VIX but always explain it. |
| MOVE | **MOVE (the bond market "fear gauge")** | The same idea for US Treasury bonds. It is a published index from ICE, not something we built. |
| Newey-West / HAC | **a correction for each quarter resembling the last** | Adjusts our uncertainty estimates because quarters are not independent. |
| Granger causality | **does last quarter's X help predict this quarter's Y?** | A standard test of which variable leads the other. It is not proof of cause. |
| VAR | **a model of two series that influence each other over time** | Keep out of main slides if possible. |
| Fama-MacBeth | **estimate each quarter separately, then average** | A standard way to run a regression across many stocks over many quarters. |
| fixed effects | **comparing each stock only to itself over time** | Removes anything permanent about a stock, such as being large. |
| CRSP | **the standard university database of stock prices** | Complete history including companies that later disappeared. |
| WRDS | **the service universities use to access CRSP** | Wharton Research Data Services. |
| FMH | **the Fractal Market Hypothesis** | The idea that markets are stable when investors have many different time horizons. |
| p-value | **how surprising the result would be by luck alone** | Smaller is stronger. Mention only when needed. |

Style rule that applies to all text, slides and notes: **do not use em dashes (the long dash character) anywhere.** Use commas, periods, colons, or the word "and". Also avoid the words "robust", "leverage", and "novel".

---

## 4. Visual design

- **Match the previous deck.** The earlier deck is `Chalmers Progress Update.pdf` (in Downloads). It uses a dark navy background, off-white headings, a soft purple accent, and thin divider lines. Keep that look for continuity. A clean sans-serif such as Inter is fine.
- **16:9 slides.** Title at top left, one clear idea per slide, generous whitespace.
- **One large number at most per slide**, supporting numbers small.
- **Colour meaning (keep consistent):** purple accent = our main object; green = confirmed or survived; amber = caution or weakened; red = contradicted or reversed. Use amber or red sparingly so it signals something.
- **"Where we are" strip** at the bottom of every main slide: four labelled segments: `1 Background`, `2 What you asked`, `3 New findings`, `4 Our questions for you`. Highlight the current one. Slide numbers at bottom right ("7 / 17").
- **Tables:** at most 7 rows on a main slide, large type. Longer tables go to the appendix.
- **Charts:** label axes in plain words, no acronyms in axis titles. Write the takeaway as the slide title (a sentence), not a topic label.
- **Accessibility:** minimum 20 pt body text on main slides. No text smaller than 14 pt except footnote source lines.
- **Speaker notes:** required on every slide, in the format given in Section 5.

---

## 5. Format of each slide spec below

Every slide has these fields. Build exactly what is listed.

- **Purpose:** why the slide exists.
- **Title (on slide):** the exact title text.
- **Question banner:** the line shown under the title (result slides only).
- **On-slide content:** the elements to place, in reading order.
- **Visual:** chart, table, or diagram, with the data source.
- **Speaker notes:** the words to say, written for slow delivery. Include PAUSE markers.
- **If he asks:** one likely question and a short honest answer, to put in the notes.
- **Time:** target seconds.

Total of main slides is about 20 minutes. If time is short, the slides marked **(compressible)** can be shortened to one sentence each. Never compress slides 10, 14, 15, or 16.

---

## 6. Storyline at a glance

| # | Part | Slide title | Time |
|---|---|---|---|
| 1 | 1 Background | Title | 0:20 |
| 2 | 1 Background | What are we studying, and why? | 1:15 |
| 3 | 1 Background | Our model in one picture | 1:15 |
| 4 | 2 What you asked | What you asked us to do, and what we did | 1:15 |
| 5 | 2 What you asked | What the data actually looks like | 1:30 |
| 6 | 2 What you asked | How we measure trading horizon and horizon diversity | 1:30 |
| 7 | 2 What you asked | Finding 1: investors with similar horizons hold similar stocks | 1:30 |
| 8 | 2 What you asked | Your question on lags: how many corrections do we need? | 1:15 |
| 9 | 2 What you asked | Finding 2: bond funds, split by credit quality | 1:30 |
| 10 | 3 New findings | Finding 3: a correction to our own headline result | 2:00 |
| 11 | 3 New findings | Why would volatility change how investors trade? | 1:15 |
| 12 | 3 New findings | Finding 4: a test on individual stocks | 1:45 |
| 13 | 3 New findings | How this fits with earlier research | 0:45 (compressible) |
| 14 | 3 New findings | The tension: our model and the data disagree | 1:30 |
| 15 | 4 Questions | Should we change the model? Your opinion | 1:30 |
| 16 | 4 Questions | A request: access to the standard stock database | 1:00 |
| 17 | 4 Questions | Where the paper stands, next steps, and questions | 1:00 |
| A1-A10 | Appendix | Reference slides | not presented |

Main parts: Part 1 Background (slides 1 to 3), Part 2 What you asked (4 to 9), Part 3 New findings (10 to 14), Part 4 Our questions for you (15 to 17).

---

## 7. Slide-by-slide specification

### Slide 1. Title

**Purpose:** open and set expectations.
**Title:** Chronotypic Market Ecology: Follow-Up on Your Feedback
**Sub-title:** What we changed because of your suggestions, what we found since, and three questions for you.
**On-slide content:** presenters' names (Sumedh Seetharaman and Sanjay Subramanian), "Meeting with Professor John Chalmers", month and year (October 2026). Below, a row of four small labels matching the four parts of the talk, no numbers yet.
**Visual:** same title style as the previous deck. No data.
**Speaker notes:** "Thank you for your detailed feedback last time. We took every suggestion seriously. PAUSE. Some of what we found supports the paper, and some of it weakens it, and we want to show you both. PAUSE. We finish with three questions where we really need your advice."
**Time:** 20 seconds.

---

### Slide 2. What are we studying, and why?

**Purpose:** Rule 1. Restate the research question from zero.
**Title:** Do investors who think on different time scales keep markets stable?
**On-slide content (three short blocks, left to right):**
1. **The setting:** "Some investors trade in seconds. Others hold for years. We call how long an investor typically holds a position their trading horizon."
2. **The idea (from the Fractal Market Hypothesis):** "Markets may be stable when there is a healthy mix of horizons, because someone is always willing to take the other side of a trade."
3. **Our question:** "What happens to stability when investors with similar horizons mostly trade with each other, and when horizons drift toward each other over time?"
**Visual:** a simple horizontal line labelled "short horizon (days)" to "long horizon (years)" with three small icons at points along it: "high-speed trader", "hedge fund", "pension fund". Illustrative only, no numbers.
**Speaker notes:** "Before any results, a reminder of what we are studying and why. PAUSE. Investors differ a lot in how long they hold things. A pension fund and a day trader live on very different clocks. PAUSE. An older idea, the Fractal Market Hypothesis, says markets are healthiest when there is a mix of those clocks. PAUSE. Our question is: what happens when investors with similar clocks mostly deal with each other, and when their clocks drift together over time? PAUSE."
**If he asks "who proposed this idea?":** "Edgar Peters popularised it in 1994. We cite it. It is a verbal hypothesis, not a proven result, and that matters later."
**Time:** 75 seconds.

---

### Slide 3. Our model in one picture

**Purpose:** Rule 1 continued. Explain the simulation without symbols.
**Title:** Our model: a market of 80 simulated investors with different horizons
**On-slide content:**
- Left: a diagram of a network. Draw about 12 dots arranged left (short horizon) to right (long horizon). Draw many links between dots that are close together and few links between far-apart dots. Caption: "Investors mostly deal with others whose horizons are similar."
- Right, three bullets in plain English:
  - "A dial controls how strongly like trades with like. We call it horizon clustering."
  - "Investors who mostly deal with similar investors slowly copy their neighbours' horizons, so the mix of horizons can shrink over time."
  - "We then measure two things: how volatile prices are, and how fragmented beliefs are across horizon groups."
- Bottom strip with the two headline simulation results, small: "More clustering lowered simulated volatility by a factor of 1.31 and nearly eliminated fragmentation of beliefs across groups (a factor of 14.25). Both held up in a 30-run replication."
**Visual:** hand-drawn style network diagram. Do not use real data. Do not show equations.
**Speaker notes:** "Here is the model in one picture. PAUSE. We simulate eighty investors. Each has a trading horizon. They are linked in a network, and links are more likely between investors with similar horizons. PAUSE. One dial sets how strong that tendency is. PAUSE. Investors also slowly adapt toward their neighbours' horizons. PAUSE. We measure how volatile the simulated price is, and how fragmented beliefs are between horizon groups. The two bottom numbers are the main simulation results. Last time we confirmed them with thirty repeat runs."
**If he asks "why 80 investors?":** "A tractable size. We checked 160 and 320 and the direction held."
**Time:** 75 seconds.

---

### Slide 4. What you asked us to do, and what we did

**Purpose:** show the map from his suggestions to our actions. This is the contents page for Part 2 and Part 3.
**Title:** Your suggestions, and what we did with each
**On-slide content:** a two-column table, left "What you suggested", right "What we did, and where it is in this talk". Six rows exactly:

| What you suggested | What we did | Slide |
|---|---|---|
| Explain the horizon diversity measure and show how it was made | Built a step-by-step explanation with a worked example | 5, 6 |
| Show what the data looks like for two funds | Worked example with three real institutions | 5, 7 |
| Is a correction with 17 lags right? Test how many lags are needed | Ran the correction at 0 to 8 lags, three lag-choice rules, and added two more checks | 8 |
| Look at bond funds by credit quality | Compared 7 bond funds: Treasury, investment-grade corporate, high-yield | 9 |
| Explore why volatility changes the horizon measure (Harris and Raviv) | Read the paper, and tested whether our result was a measurement effect | 10, 11 |
| Be clear and plain, use no jargon | Rewrote the deck and the paper's abstract and introduction | throughout |

Under the table, one amber line: "Along the way we found several of our own earlier claims did not hold. Slide 10 and the appendix list them."
**Visual:** table only, large type.
**Speaker notes:** "This is a map. On the left, what you suggested. On the right, what we did. PAUSE. Almost every suggestion led to a result, and one of them, the price-drift check, led to a correction of our own headline result. PAUSE. We will go through them in order."
**Time:** 75 seconds.

---

### Slide 5. What the data actually looks like

**Purpose:** Rules 3 and 4. A real sample, so he can see the rows.
**Title:** What our data looks like: three real investment managers, one quarter
**Question banner:** "What does one row of our data contain?"
**On-slide content:**
- A table with three rows (label them Institution A, B, C; do not name real firms) and columns: *Positions held* | *Turnover vs last quarter* | *Trading horizon (days)* | *Largest holding share*.
  - A (fast trader): 580 positions | 52.1% | 121 days | 18.1%
  - B (middle): 2,651 positions | 11.5% | 548 days | 2.6%
  - C (slow trader): 223 positions | 4.2% | 1,511 days | 7.1%
- Underneath, three plain sentences: "Each institution reports every stock it owns, with a security ID and a dollar value." / "From two consecutive quarters we measure how much of the portfolio changed. We call that turnover." / "Trading horizon is 63 divided by turnover. Low turnover means a long horizon."
- A small footnote: "Quarter shown: 2019 Q2. Source: SEC quarterly holdings reports for the 150 managers who file most consistently. Turnover here is measured from changes in portfolio weights."
**Visual:** the table, large. Optionally a thin horizontal bar under each institution showing its five largest holdings as coloured blocks (no tickers).
**Data source:** `worked_example.py` output for quarter 2019Q2 (see Section 9). Institutions identified internally by filer ID 1011443, 1535323, 1123778 (do not show IDs).
**Speaker notes:** "This is what one row of our data looks like. PAUSE. Three real managers, one quarter. The first changed over half its portfolio in three months. The last changed about four percent. PAUSE. We turn that into a trading horizon: sixty-three trading days divided by turnover. So the fast manager has a horizon of about 120 days and the slow one about 1,500 days. PAUSE. Everything else in the talk is built from numbers like these."
**If he asks "why 63?":** "Sixty-three is roughly the number of trading days in a quarter, so a manager who turns over their whole portfolio each quarter has a horizon of about one quarter."
**Time:** 90 seconds.

---

### Slide 6. How we measure trading horizon and horizon diversity

**Purpose:** Rule 5. Show how the diversity index is made.
**Title:** From one number per manager to one number per quarter
**Question banner:** "How do we turn the horizons of over 100 managers into a single measure of diversity?"
**On-slide content, four numbered steps left to right with a small picture each:**
1. **Measure each manager's horizon.** (one dot per manager on a line from short to long)
2. **Sort the horizons into 16 equal-width bins on a log scale.** Plain note: "log scale because the gap between 5 days and 10 days matters as much as between 500 and 1,000."
3. **Count the share of managers in each bin.**
4. **Score the spread.** "If everyone is in one bin the score is 0. If managers are spread evenly the score is highest." Formula in words: "the score is the sum, across bins, of (share) times (minus the natural log of share)". Appendix-only: the symbols.
- **Toy example box (clearly labelled "Illustration, not our data"):** five bins with managers split 20%, 30%, 30%, 10%, 10%. Show the calculation: 0.2 x 1.609 = 0.322; 0.3 x 1.204 = 0.361 (twice, 0.722); 0.1 x 2.303 = 0.230 (twice, 0.461). Total = **1.505**. Maximum possible with five bins = 1.609 (everyone spread equally).
- Bottom line: "In our real data the score runs between roughly 1.7 and 2.0. The highest it could ever be with our setup is about 2.57."
**Visual:** the four-step strip plus the toy box. Optionally a small histogram of real horizons for one quarter (use `price_adjusted_tdi_results.csv` is not a histogram, so skip unless the agent can build one from `tau_by_inst_quarter.json`, key `"x"`, quarter 2019Q2).
**Speaker notes:** "Here is exactly how the diversity measure is made. PAUSE. Step one, a horizon for every manager. Step two, sort the horizons into sixteen bins on a log scale. Step three, count the share in each bin. Step four, score the spread. PAUSE. The toy example uses five bins. If the shares are twenty, thirty, thirty, ten, ten, the score is one point five. If everyone sat in a single bin the score would be zero. PAUSE. In our real data the score stays between about one point seven and two."
**If he asks "why entropy?":** "It is the standard measure of how spread out a distribution is, and it is the same formula we use inside the simulation, so the two can be compared."
**Time:** 90 seconds.

---

### Slide 7. Finding 1: investors with similar horizons hold similar stocks

**Purpose:** answer his hardest question from last time (does clustering exist in real data?) using the two-fund example he asked for.
**Title:** Investors with similar horizons do hold more similar stocks
**Question banner:** "Do managers with similar trading horizons own similar portfolios?"
**On-slide content, left to right:**
- **Left: "For one pair of managers":** use the pair table from slide 5 data:

| Pair | Stocks both hold | Portfolio similarity (0 to 1) | Horizon closeness (0 to 1) |
|---|---|---|---|
| A and B (fast, middle) | 346 | 0.079 | 0.222 |
| A and C (fast, slow) | 43 | 0.001 | 0.081 |
| B and C (middle, slow) | 195 | 0.132 | 0.363 |

  Below: "Portfolio similarity: 1 means identical dollar weights, 0 means no stock in common. Horizon closeness: 1 means identical horizons, near 0 means very different." (Plain definitions only; the formula goes to the appendix.)
- **Middle: "Then repeat for every pair, every quarter":** "Each quarter we have about 5,000 pairs. We correlate the two columns. A positive correlation means managers with closer horizons hold more similar stocks."
- **Right: the result:** big number **+0.158** with caption "average correlation across 50 quarters". Under it three small supporting lines: "Positive in all 50 quarters." / "Statistically significant in 48 of 50 under a test that does not assume pairs are independent." / "95% range for the average: 0.145 to 0.175."
**Visual:** a line chart of the 50 quarterly correlations, 2013 Q3 to 2026 Q1, y axis "correlation between horizon closeness and portfolio similarity", a dashed zero line, and a dotted line at the average 0.158. Data: `kappa_empirical_results.csv`, column `kappa_hat`.
**Speaker notes:** "You asked what the data looks like for two funds. PAUSE. Take managers A and B. They hold 346 stocks in common, their portfolios are a little similar, and their horizons are moderately close. PAUSE. Now do that for every pair of managers, about five thousand pairs per quarter, and ask whether closer horizons go with more similar portfolios. PAUSE. The answer is yes. The average correlation is about 0.16 across fifty quarters. It is a modest effect but it is consistent. PAUSE. This is the first direct evidence that like-horizon investors cluster in real data, which is the main assumption of our model."
**If he asks "is 0.16 big?":** "No, it is modest. The direction is the point. Its value is that it shows the mechanism exists at all."
**If he asks "why not ask whether they buy the same stocks?":** "We measure holdings, not purchases. A purchases version needs trade data, and is a good next step."
**Time:** 90 seconds.

---

### Slide 8. Your question on lags: how many corrections do we need?

**Purpose:** answer his Newey-West question directly and honestly.
**Title:** The correction we used had no fixed lag count, so we tested it properly
**Question banner:** "How many lags does the uncertainty correction need, and does our result survive it?"
**On-slide content:**
- A short honest line first, amber: "Our earlier figure of 17 was not a lag count. It came from an approximation of the effective sample size, and we had not run the correction itself. We have now."
- **Table, "t-statistic for the average clustering score" by number of lags:**

| Lags | 0 | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|---|
| t-statistic | 25.7 | 22.1 | 20.2 | **19.0** | 18.2 | 17.1 | 16.3 |

  Mark 3 lags as "chosen by two standard rules" and 4 as "chosen by a third rule". Caption: "Any t-statistic above about 2 is significant. Ours stays above 16 at every lag count."
- **Right box, "How we decided on lags":** "Two standard formulas (Schwert, and Newey and West 1994) both give 3. A third formula that uses the data's own persistence gives 4. We also report 8 as a deliberately generous choice."
- **Below, "Do quarters really resemble the last one?":** "Yes, mildly. Correlation of one quarter with the next is 0.35. A standard test of this (Ljung-Box) rejects 'no pattern' at 1, 2 and 4 lags and does not at 8."
- **Two extra checks:** "Block bootstrap (resampling blocks of 4 quarters): the average lies between 0.145 and 0.175." / "Permutation test (shuffling horizons across managers within a quarter, which does not treat pairs as independent): significant at the 5% level in 48 of 50 quarters."
**Visual:** the table as a clean row, plus a tiny bar chart of the t-statistic by lag (bars decreasing from 25.7 to 16.3, with a horizontal line at 2).
**Data source:** `kappa_hac_results.json`; ACF values 0.346, 0.247, 0.146, 0.093, 0.051, 0.164, 0.058, 0.028 for lags 1 to 8; Ljung-Box p-values 0.012 (1 lag), 0.008 (2), 0.023 (4), 0.102 (8).
**Speaker notes:** "You asked whether we used seventeen lags. PAUSE. We did not. That number came from an approximation, and we had not actually run the correction. We have now. PAUSE. Standard rules say three lags. With three lags the t-statistic is nineteen, and with a generous eight lags it is still sixteen. PAUSE. Two other checks agree. So the result is solid, even though the exact seventeen was wrong."
**If he asks "why would the t fall as lags rise?":** "More lags make the correction more cautious about autocorrelation. It falls but stays far above the threshold."
**Time:** 75 seconds.

---

### Slide 9. Finding 2: bond funds, split by credit quality

**Purpose:** respond to his bond suggestion; show a concrete example; state the corrected MOVE description.
**Title:** Bond funds that trade on different information environments
**Question banner:** "Do bond funds differ in how often they trade, and does it relate to bond-market volatility?"
**On-slide content:**
- A note, first, in plain words: "Last time, bond funds' average maturity showed no link to the bond market's fear gauge (correlation minus 0.21, only 12 points). You pointed out average maturity is about how a fund is built, not how often it trades. So we measured how much each fund actually changes its holdings."
- **Data sample (3 rows) of one fund:** use "Vanguard Intermediate-Term Treasury Fund, four quarters": show these four real rows (from `bond_by_type_results.json`, `Treasury` list, fund name "VANGUARD INTERMEDIATE-TERM TREASURY FUND"; fields are quarter, average maturity in years, trading horizon in days, MOVE value, fund name):

| Quarter | Avg maturity (yrs) | Trading horizon (days) | MOVE index |
|---|---|---|---|
| 2020 Q1 | 9.15 | 199 | 88.8 |
| 2020 Q2 | 8.98 | 180 | 53.1 |
| 2020 Q3 | 7.94 | 151 | 42.7 |
| 2020 Q4 | 7.61 | 191 | 50.6 |

  Note for the presenter: these rows show a fund whose trading horizon moved between 151 and 199 days while the bond fear gauge fell from 89 to about 43 to 51.
- **Result table (seven funds):**

| Fund type | Typical trading horizon | Link to bond fear gauge |
|---|---|---|
| Treasury (short, intermediate, long) | 218 days | **+0.38** |
| Investment-grade corporate (short, intermediate, long) | 454 days | **+0.33** |
| High-yield corporate (junk) | 667 days | **+0.36** |

  Caption: "Link = how a fund's trading horizon moves with the MOVE index, quarter by quarter, within each fund. Positive means funds trade less often when bond volatility is high."
- **Takeaways (three bullets):** "Funds with more uncertain information trade less often: 218, 454, 667 days." / "In bonds, horizons lengthen when volatility is high, the opposite sign to what we saw in stocks." / "Each fund has only 27 quarters, so this is descriptive, not a formal test."
- **Footnote (important correction):** "MOVE is the ICE Bank of America index of expected Treasury volatility, computed from option prices. It is a published index. We said last time that we built it. That was wrong."
**Visual:** the 3-row summary table (large) plus a small dot chart of the seven funds' typical horizons grouped by type. Full seven-fund table goes to appendix A4.
**Data source:** `bond_by_type.log`/`bond_by_type_results.json`. Full per-fund numbers are in Section 9.
**Speaker notes:** "You suggested comparing bond funds with different information environments. PAUSE. We took seven Vanguard funds: Treasury, investment-grade corporate, and high yield. PAUSE. Instead of average maturity, we measured how much each fund changes its holdings. PAUSE. Treasury funds turn over fastest, about 220 days. Junk bond funds trade least often, about 670 days. PAUSE. In all three types, trading slows when bond volatility is high. This is only twenty-seven quarters per fund, so we treat it as descriptive. PAUSE. One correction: the MOVE index is a published ICE index. We told you we built it. We did not."
**If he asks "why would junk funds trade less?":** "Possibly because credit bonds are less liquid, so turning them over is costlier. We have not tested that."
**Time:** 90 seconds.

---

### Slide 10. Finding 3: a correction to our own headline result

**Purpose:** the most important honesty slide. Never compress.
**Title:** Our headline link between horizon diversity and volatility was mostly a measurement artifact
**Question banner:** "Is the link between horizon diversity and the VIX real, or is it caused by how we measure trading?"
**On-slide content:**
- **Two-sentence setup in plain English:** "We measured how much a manager trades from changes in portfolio weights. But weights also change when prices move, even if the manager does nothing. In volatile quarters prices move a lot, so weight-based turnover rises and horizons look shorter for everyone."
- **Three-panel chart (use the existing figure `figures/drift_check.png`, or rebuild it with the same data).** Panels: (a) horizon diversity over time under two methods plus VIX, standardised; (b) scatter with VIX using weight-based turnover; (c) scatter using share-based turnover.
- **Result table beside the chart:**

| How turnover is measured | Correlation with VIX | 95% range |
|---|---|---|
| Changes in portfolio weights (our earlier method) | **-0.59** (our paper reported -0.53) | -0.80 to -0.24 |
| Changes in share counts (price moves cannot count as trades) | **-0.06** | -0.43 to +0.25 |
| Share counts, with stock splits adjusted | **-0.10** | -0.49 to +0.27 |

  One line below, amber: "The difference between the first two rows is statistically significant (95% range -0.92 to -0.13)."
- **Closing line:** "What this means: the correlation we reported as our main empirical result is mostly price drift, not a change in how investors trade."
- **Smaller second note:** "The earlier finding that VIX leads horizon diversity (not the reverse) came from our original numbers. It does not reproduce on the share-based version, so we treat it as suggestive only."
**Visual:** three-panel figure plus the table. Keep the figure large.
**Data source:** `price_adjusted_tdi_results.csv`, `empirical_tdi_results.csv` (column `VIX_avg`), figure `figures/drift_check.png`. 45 quarters, 2013 Q3 to 2024 Q3.
**Speaker notes:** "This is the slide we most want to discuss. PAUSE. After your question about mechanism, we asked whether our headline correlation could be a measurement effect. PAUSE. Here is the issue. We measure trading from changes in portfolio weights. But weights change when prices change, even with no trading. In volatile quarters prices move a lot, so it looks as though everyone is trading faster. PAUSE. When we measure trading only from changes in share counts, the correlation with VIX goes from minus point five nine to minus point oh six. PAUSE. So most of our headline empirical result was price drift. We have rewritten the paper's abstract and conclusion to say so."
**If he asks "so is the paper dead?":** "No. The simulation is unaffected, and the clustering result on slide 7 stands. But the claim that horizon diversity lines up with VIX is not supported, and we say so."
**Time:** 120 seconds. Do not shorten.

---

### Slide 11. Why would volatility change how investors trade?

**Purpose:** answer his mechanism question and cite Harris and Raviv.
**Title:** Two possible reasons volatility and trading speed move together
**Question banner:** "Is it a real change in behaviour, or an accounting effect?"
**On-slide content:** two columns.
- **Left, "Real behaviour" (cites Harris and Raviv, 1993):** "When volatility is high, investors disagree more about value, and disagreement produces more trading. Differences of opinion make a horse race. More trading shortens horizons for many investors at once. This is a genuine economic reason."
- **Right, "Accounting effect":** "Prices move, so portfolio weights move, so measured turnover rises with no trading. This is what slide 10 tested."
- **Bottom, "What we found":** "The accounting effect explains most of our measured link. Real behaviour may still be present but is not visible in our data."
- **Footer line:** "Reference: Harris, M. and Raviv, A. (1993), Review of Financial Studies 6(3), 473 to 506." (Flag in notes: you mentioned it was in the Journal of Finance; it is in the Review of Financial Studies.)
**Visual:** two-column comparison, no chart.
**Speaker notes:** "You asked what the mechanism could be, and recommended Harris and Raviv. PAUSE. We read it. Their idea is that when people disagree more, they trade more. Volatile periods are periods of disagreement. PAUSE. That is a real reason horizons could shorten when volatility rises. PAUSE. But there is also the measurement effect from the last slide. We can show the measurement effect explains most of what we saw. We cannot yet show the behavioural effect. PAUSE."
**If he asks "how would you separate them?":** "With trade-level data instead of quarterly snapshots, or an event where disagreement changes but prices do not."
**Time:** 75 seconds.

---

### Slide 12. Finding 4: a test on individual stocks

**Purpose:** present the stock-level test (new empirical contribution) honestly.
**Title:** Stocks held by like-minded horizons are slightly more volatile, but the effect is small
**Question banner:** "Within a single stock, does it matter whether its owners have similar or very different horizons?"
**On-slide content:**
- **Plain design (three bullets):** "For each stock and quarter, we look at the managers who hold it and measure how spread out their trading horizons are, weighting by how much each holds." / "We then ask whether stocks with less spread (more like-minded owners) have higher volatility the next quarter." / "We fixed this prediction in advance, so we could not choose the result after looking. It comes from the Fractal Market Hypothesis."
- **Data sample (4 rows, illustrative column layout; agent should leave placeholders if no real rows):** columns: *Stock | Quarter | Number of holders | Spread of holders' horizons | Volatility next quarter*. State: "63,261 stock-quarters, 1,699 stocks, 48 quarters, 2013 to 2025." Optionally draw rows from a real sample if the agent can regenerate with `stock_level_test.py`; otherwise show a blank-labelled example row with "e.g." values clearly marked as illustrative.
- **Result table** (standard deviations of next-quarter volatility per one standard deviation change in spread; more negative means more like-minded owners lead to more volatility):

| Method | Effect | Strength |
|---|---|---|
| Average across stocks, quarter by quarter | **-0.046** | very strong (t = -6.2) |
| Comparing each stock only to itself over time | **-0.011** | significant (t = -2.4, p = 0.016) |
| Same, using weight-based turnover | -0.005 | not significant (p = 0.26) |
| Shuffled horizons (placebo) | 0.000 | none |

- **Honest limits (amber box):** "Effect is tiny: one standard deviation change in spread moves volatility by about 1% of a standard deviation within a stock." / "Two other outcomes (worst daily return and skew) were not consistent." / "Sample includes only stocks that still exist, because free price data drops delisted companies. This is a reason we want the standard database (slide 16)."
**Visual:** results table. Optionally a bar chart of the three effect sizes with 95% bars.
**Data source:** `stock_level_results.json`, `stock_level_test.log`, `stock_level_test_v2.log`.
**Speaker notes:** "To get more than forty-five data points, we moved to individual stocks. PAUSE. For each stock and quarter we measure how similar its owners' horizons are, and ask about next quarter's volatility. We fixed the prediction in advance. PAUSE. Stocks with more like-minded owners are more volatile. Across stocks the effect is strong. But when we compare each stock only to itself, it shrinks to about one percent of a standard deviation. PAUSE. It is statistically detectable but economically small. And the sample only contains survivors, which is one reason we would like better data."
**If he asks "is it just size?":** "We control for the amount held and the number of holders, and the stock-only-to-itself version removes anything permanent. But we lack true market cap. That is another reason for the standard database."
**Time:** 105 seconds.

---

### Slide 13. How this fits with earlier research (compressible)

**Purpose:** show we know related work and differ honestly.
**Title:** Related work, and how we differ
**On-slide content:** a four-row table.

| Earlier paper | What it showed | How ours differs |
|---|---|---|
| Cella, Ellul and Giannetti (2013, Review of Financial Studies) | Stocks held by short-horizon investors fall more and rebound more in market turmoil, using the same kind of holdings data | They study how many short-horizon owners. We study how similar owners' horizons are, holding the average fixed, inside a network model |
| Bushee (1998, The Accounting Review) and Gaspar, Massa and Matos (2005, Journal of Financial Economics) | Classify investors by turnover and link them to managers' short-termism and to takeovers | Different outcomes. We study price volatility and market structure |
| Li, Nishimura and Men (2014, Physica A) | Simulation: liquidity comes from mixed horizons, and with a finite maximum horizon more diversity need not add stability | Close to our simulation idea. We add a network that forms by horizon similarity and horizons that adapt |
| Kristoufek (2012, Advances in Complex Systems) | Tests the Fractal Market Hypothesis around the 2008 crisis | Different data and method |

- Footer: "The first row is the closest overlap. A referee would likely raise it, so we cite it directly."
**Visual:** table only.
**Speaker notes:** "A quick note on related work. The closest paper is Cella, Ellul and Giannetti, which uses the same holdings data to show that short-horizon owners amplify market shocks. PAUSE. Their focus is how much short-horizon ownership a stock has. Ours is how similar owners' horizons are. We now cite all of these in the paper."
**Time:** 45 seconds.

---

### Slide 14. The tension: our model and the data disagree

**Purpose:** set up the question for him. Never compress.
**Title:** In our model, mixed horizons raise volatility. In the data, similar horizons do.
**Question banner:** "Does our model predict the same direction we see in the data?"
**On-slide content:**
- **Two boxes side by side.**
  - **Left, "What the model says":** "When investors' horizons are compressed (less mixed), simulated volatility goes down: 0.00084 versus 0.00095, comparing the most compressed horizons with the widest (statistically significant at the lowest clustering setting). Across 125 simulation runs at that setting, higher horizon diversity goes with higher volatility (correlation +0.21)." Plain reason: "Investors whose horizons differ add friction to trading, which raises noise."
  - **Right, "What the data say":** "Stocks whose owners have similar horizons are more volatile, not less (slide 12)."
- **Between them, a red "opposite directions" marker.**
- **Below, a line in amber:** "We also found that a sentence in our earlier paper claiming the model produced the data's direction was not supported: the sweep behind it never fed the compressed horizons into the simulation. We have corrected the paper."
- **Closing line:** "Our model contains the 'friction' channel but not the 'fragility' channel that the Fractal Market Hypothesis describes."
**Visual:** a small bar chart on the left box: volatility by horizon-compression level (five bars, conc 0.5, 1, 1.5, 2, 3) at the lowest clustering setting: 0.00095, 0.00094, 0.00095, 0.00092, 0.00084 (values in 10^-3 units: 0.95, 0.94, 0.95, 0.92, 0.84). On the right, a single arrow pointing the other way.
**Data source:** `sim_concentration_results.json`, `sim_concentration_check.log`. Second clustering setting gives 0.00086, 0.00088, 0.00079, 0.00080, 0.00080 (not significant).
**Speaker notes:** "Here is the uncomfortable part. PAUSE. In our model, when investors' horizons are compressed, volatility goes down, because mixed horizons add friction. PAUSE. In the data, stocks whose owners have similar horizons are more volatile. These point in opposite directions. PAUSE. We also found that an earlier sentence in the paper claimed the model produced the data's direction. It did not. That sweep had never fed the compressed horizons into the simulation. We have corrected it. PAUSE. So our model has the friction channel, but it does not have the fragility channel that the Fractal Market Hypothesis is about."
**If he asks "which one is wrong, model or data?":** "We do not know. The data effect is small and from a survivor-only sample. The model is missing a mechanism. Both are why we want your view."
**Time:** 90 seconds. Do not shorten.

---

### Slide 15. Should we change the model? We want your opinion

**Purpose:** ask the question. This is the most important slide for his input.
**Title:** Three options for the model, and which would you pick?
**On-slide content:** three option cards, each with Idea, What we would change, Pro, Con.
- **Option A, "Add a stabiliser that depends on horizon mix."** Idea: "Make the force that pulls prices back to fundamental value weaker when horizons are concentrated." Change: "A small modification to the demand rule." Pro: "Directly produces the fragility the hypothesis describes, so model and data could agree." Con: "We would have to re-verify every simulation result, and it risks looking like we built the answer we wanted."
- **Option B, "Make liquidity depend on horizon mix."** Idea: "Market makers or long-horizon investors provide liquidity, and their willingness shrinks when horizons concentrate." Change: "Add a liquidity-provision agent type." Pro: "Closer to Harris and Raviv and to the real mechanism." Con: "Larger redesign."
- **Option C, "Keep the model, report the disagreement."** Idea: "Say plainly that the model captures the friction channel only and that the data point to a channel we do not model." Change: "None; wording only." Pro: "Simple, honest." Con: "Weaker contribution; the model does not explain the data."
- **Bottom, "Questions for you":** (1) "Which option would a referee find most convincing?" (2) "Is it acceptable to change the model after seeing the data, if we say so openly?" (3) "Should the data and the model be shown to agree, or is it fine to report a disagreement?"
**Visual:** three cards. No chart.
**Speaker notes:** "This is where we need your judgement. PAUSE. Option A: add a stabilising force that weakens when horizons are concentrated. PAUSE. Option B: make liquidity depend on horizon mix, closer to the idea in Harris and Raviv. PAUSE. Option C: keep the model and report the disagreement. PAUSE. Two worries. Changing the model after seeing the data can look like fitting the answer, and any change means re-checking all our simulation results. PAUSE. Which would you choose, and is changing the model after seeing data acceptable if we say so openly?"
**Time:** 90 seconds. Leave at least two minutes of silence for his reply. Do not shorten.

---

### Slide 16. A request: access to the standard stock database

**Purpose:** ask for WRDS and CRSP access with a concrete plan.
**Title:** Could we get access to the standard stock database?
**Question banner:** "What would better data let us do, and could you help us get it?"
**On-slide content:**
- **Left, "What we used":** "Free price data from Yahoo Finance. It drops companies that were delisted or acquired, covers about 60% of the stocks we tried to match, and has no market capitalisation or trading-volume history. Our stock sample is therefore survivors only."
- **Right, "What the standard database gives":** "CRSP (via WRDS): every US stock back to 1926 including delisted ones, with market capitalisation, volume, and the adjusted returns referees expect. WRDS also has a full holdings database, so we could use all managers, not our 150."
- **Middle, "What we would do with it" (four bullets):** "Repeat the stock-level test on the full universe." / "Control for firm size properly." / "Test more outcomes: crash risk, co-movement, and trading liquidity." / "Use all managers' holdings, not 150."
- **Bottom, "The ask":** "Does the university or your research group have a WRDS subscription we could be added to, or could you point us to the right person? If not, is there a cheaper route you would suggest?"
**Visual:** two-column comparison. No chart.
**Speaker notes:** "A practical request. PAUSE. Our stock-level test uses free price data, which drops delisted companies. That biases the sample, and we cannot control for size properly. PAUSE. The standard database is CRSP, accessed through a service called WRDS. It includes delisted stocks and the full holdings database. PAUSE. Do you or the university have a subscription we could be added to, or can you point us to the right person? PAUSE."
**If he asks "what would you do first?":** "Rerun the stock-level test and see whether the small effect survives with better data. That tells us if it is real."
**Time:** 60 seconds.

---

### Slide 17. Where the paper stands, next steps, and questions

**Purpose:** close with a summary and an explicit list of asks.
**Title:** Where we are, and what we need from you
**On-slide content, three columns:**
- **"What holds up":** green: "Like-horizon investors hold similar stocks (average +0.158)." / "Simulation results confirmed over 30 runs." / "A small, within-stock link between clustered owners and volatility."
- **"What we corrected":** amber: "Horizon diversity and VIX link was mostly price drift." / "The number of lags was never 17; real correction gives t about 19." / "Our model does not produce the data's direction, and the paper now says so." / "MOVE is a published index; the Temporal Liquidity validation partly mechanical (details in appendix)."
- **"Next steps and asks":** "1. Your view on changing the model (slide 15)." / "2. Access to WRDS (slide 16)." / "3. Rebuild the main horizon diversity measure from share counts." / "4. Upload the replication code and finalise the paper for Finance Research Letters or a complexity-economics journal."
- **Bottom line:** "Thank you for pushing us to test this carefully."
**Visual:** three columns with coloured top borders (green, amber, purple).
**Speaker notes:** "To close. PAUSE. What holds up: like-horizon investors hold similar stocks, the simulation replicates, and a small stock-level link in the direction of the hypothesis. PAUSE. What we corrected: the headline link with VIX was mostly price drift; the lag count was not seventeen; and the model does not produce the data's direction. PAUSE. What we need: your view on the model, and help with data access. Thank you for pushing us to test this carefully."
**Time:** 60 seconds.

---

## 8. Appendix slides (not presented; keep for questions)

**A1. Glossary.** Reproduce the table in Section 3 (private terms mapped to plain English). Title: "Plain-English glossary".

**A2. The clustering score every quarter.** Full line chart of the 50 quarterly values with the shaded bootstrap range, plus a small table of the three quarters that fail the strict permutation threshold: 2013 Q3 (permutation p = 0.10), 2013 Q4 (p = 0.06), 2016 Q4 (p = 0.03). Data: `kappa_empirical_results.csv`, `kappa_hac_results.json`. Note: these were the earliest quarters, when fewer managers reported.

**A3. All the numbers behind slide 8.** Full table: lags 0 to 8 with standard error and t-statistic (lags 0: se 0.0061, t 25.69; 1: 0.0071, 22.14; 2: 0.0078, 20.15; 3: 0.0083, 18.95; 4: 0.0087, 18.15; 5: 0.0090, 17.60; 6: 0.0093, 17.06; 7: 0.0095, 16.63; 8: 0.0097, 16.30). Autocorrelation at lags 1 to 8: 0.346, 0.247, 0.146, 0.093, 0.051, 0.164, 0.058, 0.028. Ljung-Box tests. Effective sample size about 24 (formula: number of quarters times (1 minus r) over (1 plus r) with r = 0.346). Block-bootstrap range 0.145 to 0.175 (5,000 resamples, block length 4).

**A4. Seven bond funds, full table.**

| Fund | Reports used | Avg maturity (yrs) | Median trading horizon (days) | Link of maturity to MOVE | Link of trading horizon to MOVE |
|---|---|---|---|---|---|
| Short-term Treasury | 27 | 3.75 | 146 | -0.30 (p 0.13) | +0.45 (p 0.02) |
| Intermediate-term Treasury | 27 | 6.63 | 211 | -0.54 (p 0.00) | +0.44 (p 0.02) |
| Long-term Treasury | 27 | 21.97 | 400 | -0.40 (p 0.04) | +0.30 (p 0.13) |
| Short-term investment-grade | 27 | 4.29 | 437 | -0.64 (p 0.00) | +0.47 (p 0.01) |
| Intermediate-term investment-grade | 27 | 8.40 | 363 | -0.41 (p 0.03) | +0.73 (p 0.00) |
| Long-term investment-grade | 27 | 22.84 | 765 | -0.28 (p 0.16) | +0.01 (p 0.95) |
| High-yield corporate | 27 | 5.52 | 667 | -0.31 (p 0.12) | +0.36 (p 0.07) |

Method note: trading horizon uses changes in the amount of each bond held (par amount), valued at one price per bond so price moves cannot create turnover; bonds that matured are not counted as trades. Caveat: pooled p-values treat fund-quarters as independent although all funds in a quarter share one MOVE value, so do not present them as formal tests.

**A5. Horizon diversity series, three versions.** Table or chart of quarterly values for: our earlier method (weights), share-based, share-based with splits adjusted. Mean values about 1.88 to 1.94; standard deviations 0.051, 0.046, 0.052. Data: `price_adjusted_tdi_results.csv`. Also note our rebuilt series correlates only 0.50 with the series used in the original paper, because the set of institutions and some processing differ. Suggested wording: "The comparison is valid between the two turnover methods inside our rebuilt data, not as an exact copy of the paper's numbers."

**A6. Full stock-level regression table.**

| Outcome | Method | Share-based horizons | Weight-based horizons |
|---|---|---|---|
| Next-quarter volatility (log) | Average across quarters | -0.0459 (t = -6.20) | -0.0440 (t = -8.04) |
| | Pooled with quarter fixed effects | -0.0169 (t = -4.13) | -0.0089 (t = -2.33) |
| | Stock plus quarter fixed effects | **-0.0106 (t = -2.42, p = 0.016)** | -0.0047 (t = -1.13, p = 0.26) |
| Next-quarter worst daily return | Average across quarters | +0.0417 (t = 4.47) | +0.0416 (t = 4.73) |
| | Pooled with quarter fixed effects | -0.0038 (t = -0.58) | -0.0064 (t = -1.07) |
| Next-quarter skew | Average across quarters | -0.0006 (t = -0.09) | +0.0025 (t = +0.38) |
| | Pooled with quarter fixed effects | -0.0053 (t = -0.68) | +0.0009 (t = +0.13) |
| Placebo (horizons shuffled) | Average across quarters | 0.0000 (t = 0.01) | not run |

Controls: owners' average horizon, number of owners, concentration of owners, amount held by our panel, current-quarter volatility. All variables standardised. Standard errors: Newey-West for the average-across-quarters method; clustered by stock for the others. Sample sizes: share-based 63,261 stock-quarters (1,699 stocks, 48 quarters); weight-based 63,239.

**A7. Simulation concentration table.**

Lowest clustering setting (kappa_h = 0.5, 25 runs per row):

| Compression level (1 = baseline, higher = narrower horizons) | 0.5 | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|
| Horizon diversity | 2.52 | 2.44 | 2.29 | 2.17 | 2.01 |
| Simulated volatility (x 10^-3) | 0.95 | 0.94 | 0.95 | 0.92 | 0.84 |

Compression 3.0 versus 0.5: Welch t = -2.72, p = 0.009. Correlation of diversity and volatility across runs +0.21 (p = 0.02).
Higher clustering setting (kappa_h = 2.0): volatility 0.86, 0.88, 0.79, 0.80, 0.80 (x 10^-3); compression 3.0 versus 0.5: t = -1.54, p = 0.13; correlation +0.17 (p = 0.06).
Note: horizon diversity here uses the paper's fixed-range bins from 1 to 2,000 days. An older figure of 1.88 at compression 3 came from data-range bins and was removed.

**A8. How we checked the data (his point on zeros).**
- Holdings: each quarter we keep only positive-value, positive-share positions. Cases that would produce a zero or negative value before taking logs are dropped.
- Turnover below 0.1% is dropped (inactive filers), because it gives an extreme horizon.
- Horizons are limited to the range 5 to 2,000 trading days; the shortest and longest are capped.
- Quarters with fewer than 50 reporting managers are excluded from the diversity series. The clustering series requires at least 8 managers with valid horizons.
- For the stock test: at least 10 owners per stock, ticker matched through a public identifier service (about 60% of securities matched), at least 50 trading days of prices in the quarter.
- Stock splits: share counts near an exact split ratio (2, 3, 4, 5, 6, 8, 10, 20 or reverse) are rebased before measuring trades.

**A9. All the corrections we made to the paper (full list).**
1. Newey-West: previously asserted t about 15 and "17 lags"; now computed (t = 19.0 at 3 lags).
2. "Significant in every quarter with p < 0.001": replaced by 48 of 50 quarters at the 5% level using a permutation test.
3. Horizon diversity vs VIX: reframed as mostly price drift.
4. Granger direction: marked suggestive; does not reproduce on rebuilt series.
5. Temporal Liquidity: sample was reported as 36 quarters but the result was from 45; the correlation with VIX is largely mechanical because volatility sits inside the measure. The claim that return autocorrelation rises with volatility is unsupported (correlation +0.04).
6. MOVE: described correctly as a published index.
7. Concentration claim in simulation: replaced with real result (volatility falls).
8. The stability bound for the uniform price mode: previously asserted a figure of 0.0016 without derivation; now 0.0013 with the derivation shown.
9. Added five related-work references and one mechanism reference (Harris and Raviv).
10. Abstract, highlights, introduction and conclusion rewritten to match.

**A10. Data and code files for reproducing every number in this deck.** List from Section 9.

---

## 9. Source data and files (so every number can be traced)

All paths are under `/Users/sanjaysubramania/cme_validation/` unless noted.

| What | File |
|---|---|
| Worked example (slide 5, 7) | `worked_example.py` (run: `python3 worked_example.py 2019Q2`) |
| Quarterly clustering scores (slide 7, A2) | `kappa_empirical_results.csv` |
| Lag tests, bootstrap, permutation (slide 8, A3) | `kappa_hac_results.json`, script `kappa_hac_tests.py` |
| Bond funds (slide 9, A4) | `bond_by_type_results.json`, log `bond_by_type.log`, script `bond_by_type.py` |
| Price-drift check (slide 10, A5) | `price_adjusted_tdi_results.csv`, figure `figures/drift_check.png`, script `price_adjusted_tdi.py`, figure script `make_drift_figure.py` |
| Original diversity vs VIX series | `empirical_tdi_results.csv` |
| Stock-level test (slide 12, A6) | `stock_level_results.json`, logs `stock_level_test.log`, `stock_level_test_v2.log` |
| Model vs data (slide 14, A7) | `sim_concentration_results.json`, `sim_concentration_check.log` |
| The paper (updated) | `cme_frl_submission.tex`; compiled `cme_frl_submission_updated.pdf` |
| Previous deck for style | `Chalmers Progress Update.pdf` (Downloads) |
| Replication notes | `REPRODUCE.md` |

If a chart needs data not in these files, build it from them. Do not invent numbers.

---

## 10. Accuracy rules: what NOT to say

These are traps. Each corresponds to a claim we already had to retract.

- **Do not say** horizon diversity is correlated with VIX as evidence for the model. It is mostly price drift.
- **Do not say** the clustering score is significant in "all 50 quarters" or "p < 0.001 in every quarter". The accurate statement is 48 of 50 at the 5% level using a permutation test.
- **Do not say** we used 17 lags, or that t is about 15. The accurate figures are 3 lags with t = 19.0, and 16.3 at 8 lags.
- **Do not say** we built the MOVE index. It is a published ICE index.
- **Do not say** the model predicts the stock-level result. It predicts the opposite sign.
- **Do not say** the stock-level effect is large. It is about 1% of a standard deviation within a stock.
- **Do not say** the Granger result "confirms" anything. It is suggestive and does not reproduce on the rebuilt series.
- **Do not describe** the Temporal Liquidity correlation with VIX as validation. It is largely mechanical.
- **Do not name** the three example institutions. Use "Institution A, B, C".
- **Do not present** the three model options as decisions made. They are proposals for his opinion.
- **Do not claim** we already have WRDS or CRSP. We are asking.
- **The reference** is Harris and Raviv (1993), Review of Financial Studies, not the Journal of Finance as he said.

---

## 11. Quality checklist before you hand back the deck

1. Slides 1 to 3 restate the question and model before any result. Yes or no?
2. Every result slide has a "Question this answers" banner ending in a question mark?
3. Every estimate is preceded by a small sample of the data and a plain statement of what is done with it?
4. A worked two-institution example exists (slides 5 and 7)?
5. Horizon diversity construction is shown step by step with arithmetic (slide 6)?
6. No acronym appears without being spelled out, except VIX and MOVE which are explained?
7. No em dashes anywhere in slides or notes?
8. Every slide has speaker notes written for slow delivery with PAUSE markers, at most about 90 words each?
9. Every number on a slide matches Section 7, Section 8, or the files in Section 9?
10. The "where we are" strip and slide numbers appear on every main slide?
11. Slides 10, 14, 15, 16 are not shortened?
12. Total of 17 main slides plus appendix A1 to A10?
13. Colours are used consistently (green confirmed, amber caution, red contradicted, purple our object)?
14. The deck makes the three asks clear: his opinion on the model, WRDS access, and the lag and mechanism feedback follow-ups?

When done, send back the deck file and a list of any number you could not trace to a source in Section 9. Do not guess.
