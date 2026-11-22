# N-PORT fund panel

Fund-level (series) holdings and share-based horizons from the free SEC Form N-PORT
Data Sets, 2019Q4 onward. Built for the lame-duck managers design
(`docs/novelty-audit/ideas-round2-2026-11-21.md`, idea 1): own-fund outcomes around
portfolio manager retirement announcements, so there is no 1/k dilution as in Stage 2.

## Steps

Run from the repo root. Data goes to `nport_cache/` and `nport_panel_data/`, both gitignored.

```bash
source ~/.zshrc   # sets SEC_CONTACT_EMAIL (see APIS.md)
python stage2/download_nport.py                    # 28 zips, about 11 GB
python nport_panel/test_build_fund_panel.py        # synthetic fixture, 9 checks
python nport_panel/build_fund_panel.py             # reports, holdings, tau
python nport_panel/validate_turnover.py            # vs prospectus turnover
python nport_panel/event_coverage.py               # event counts only, no outcomes
```

## Rules

The rules are in the docstring of `build_fund_panel.py`. In short:

1. Latest filing per (series, report date); amendments replace originals.
2. Long common equity in shares with a valid CUSIP; rows summed per CUSIP.
3. Turnover between consecutive reports 2 to 4 months apart, at one common price per
   CUSIP and month, scaled to a 3-month gap; tau = 63 / turnover, clipped to [5, 2000].
4. Split rebasing needs both a share ratio near k and a price ratio near 1/k.

## The split rule (differs from the 13F panel)

The 13F rule treats any share ratio near 2, 3, 4, ... (or the inverse) as a split.
Selling exactly half a position then looks like a 1-for-2 reverse split and is
counted as no trade. `scoping/split_rule_check.py` measured this on the 13F panel:
the share-ratio rule fired on 1,385,494 of 63,618,289 continuing positions, and only
44,964 of those had a confirming price move. Unconfirmed firings are 2.1% of positions
and 3.9% of value. This biases 13F tau_split upward (bead cme-d0m). The N-PORT
builder checks the price ratio as well.

## Known limits

- Foreign listings without a CUSIP are dropped (ISIN-only rows). Most US equity funds
  hold few of these; international funds are undercounted.
- Levels differ from the prospectus rate in known directions. The share-based measure
  (average of buys and sells) counts flow-driven trades and sits at 1.08x the reported
  rate for equity funds; `turnover_min` (lesser of buys or sells, the prospectus
  definition) misses round trips inside a quarter and sits at 0.77x. Both rank funds
  well (Spearman 0.79 on 27,866 equity fund-years).
- Fiscal 2024 has no prospectus Risk/Return data set on the SEC page, so those fund
  years are missing from the validation.

## Results

See `results/nport_panel_build.json`, `results/nport_turnover_validation.json` and
`results/nport_event_coverage.json`.
