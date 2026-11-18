# Data: what is not in git, and how to get it

The repo holds code, small results and the paper. Large or regenerable data is excluded by `.gitignore`.

| Path | Size | What it is | How to get it |
|---|---|---|---|
| `edgar_cache/` | about 7.3 GB | Raw SEC 13F and N-PORT downloads, plus `holdings_db.json` (436 MB) | Ask Sanjay for the shared-drive link, or rebuild with `empirical_tdi.py` (slow, rate-limited by the SEC) |
| `bond_cache/` | about 12 MB | N-PORT bond fund cache | Rebuild with `bond_discover.py` |
| `stock_prices.pkl` | about 47 MB | Yahoo daily prices, survivors only | Rebuild with `stock_prices.py` |

Put the three paths in the same locations inside your checkout. For a git worktree, symlink them from the main checkout, for example:

```bash
ln -s /path/to/main/cme_validation/edgar_cache edgar_cache
```

Never commit these. Do not put API keys in the repo; use environment variables.
