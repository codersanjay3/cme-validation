# External data sources and APIs

None of these needs a paid key. SEC EDGAR needs a contact address from you.

| Source | Used by | What for | Setup |
|---|---|---|---|
| **SEC EDGAR** (`data.sec.gov`, `www.sec.gov/Archives`) | `empirical_tdi.py`, `bond_empirical.py`, `bond_discover.py`, `bond_by_type.py` | 13F holdings, N-PORT bond fund reports, filing indexes | The SEC requires a real contact in the User-Agent. Set `export SEC_CONTACT_EMAIL="you@example.com"`. Limit: about 10 requests per second. |
| **OpenFIGI v3** (`api.openfigi.com/v3/mapping`) | `feasibility_stock_level.py`, `map_cusips.py` | CUSIP to ticker | No key. Keyless limit is 10 lookups per request and about 25 requests per minute, so the scripts batch by 10 with a pause. An optional key raises the limits. |
| **Yahoo Finance via `yfinance`** | most empirical scripts | Stock and ETF prices, `^VIX`, `^MOVE` | No key. Survivors only (delisted stocks are missing). It can rate-limit; rerun later. |
| **Cboe** (`cdn.cboe.com`, `VIX_History.csv`) | `empirical_tdi.py` | VIX history | No key. |
| **FRED** (`fred.stlouisfed.org/graph/fredgraph.csv?id=USEPUINDXM`) | `causal_identification.py` | Economic policy uncertainty index | No key. |

Python packages for all of the above are in `requirements.txt`. The data snapshot in the `data-v1` release (see `DATA.md`) means you do not need to re-download SEC filings to reproduce results.

Never put a key or a personal email address in code. Use environment variables.
