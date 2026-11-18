"""
Extension: Empirical Temporal Liquidity proxy from public market data.

TL = 1 / (σ_r * |ACF_1|) where:
  σ_r  = quarterly return volatility (rolling 4-quarter window)
  ACF_1 = lag-1 quarterly return autocorrelation (rolling 8-quarter window)

Uses SPY quarterly returns (Yahoo Finance) aligned to the existing
TDI/VIX panel (empirical_tdi_results.csv, 2013Q3-2024Q3).

Run: python empirical_tl.py
Requires: pip install yfinance
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    HAVE_YF = True
except ImportError:
    HAVE_YF = False
    print("yfinance not installed. Run: pip install yfinance")
    print("Falling back to VIX-only proxy for σ_r.")


def fetch_spy_quarterly(start="2011-01-01", end="2025-01-01") -> pd.Series:
    """Download SPY, resample to quarter-end, return quarterly log-returns."""
    ticker = yf.Ticker("SPY")
    hist = ticker.history(start=start, end=end, auto_adjust=True)
    if hist.empty:
        raise RuntimeError("Could not download SPY data from Yahoo Finance.")
    # Quarter-end prices
    qprices = hist["Close"].resample("QE").last()
    qreturns = np.log(qprices / qprices.shift(1)).dropna()
    return qreturns


def quarter_label(ts: pd.Timestamp) -> str:
    """Convert timestamp to 'YYYYQq' label matching the CSV."""
    return f"{ts.year}Q{ts.quarter}"


def compute_empirical_tl(qreturns: pd.Series,
                          vol_window: int = 4,
                          acf_window: int = 8) -> pd.DataFrame:
    """
    Compute rolling quarterly σ_r, ACF_1, and TL.
    Returns a DataFrame indexed by quarter label.
    """
    rows = []
    r = qreturns.values
    labels = [quarter_label(ts) for ts in qreturns.index]

    for i in range(len(r)):
        # Rolling σ_r over vol_window quarters
        if i + 1 >= vol_window:
            window_r = r[i + 1 - vol_window: i + 1]
            sigma_r = float(np.std(window_r, ddof=1))
        else:
            sigma_r = np.nan

        # Rolling ACF_1 over acf_window quarters
        if i + 1 >= acf_window:
            window_r2 = r[i + 1 - acf_window: i + 1]
            if len(window_r2) > 2:
                acf1 = float(np.corrcoef(window_r2[:-1], window_r2[1:])[0, 1])
            else:
                acf1 = np.nan
        else:
            acf1 = np.nan

        if not np.isnan(sigma_r) and not np.isnan(acf1) and abs(acf1) > 1e-8 and sigma_r > 1e-8:
            tl = 1.0 / (sigma_r * abs(acf1))
        else:
            tl = np.nan

        rows.append(dict(label=labels[i], qreturn=float(r[i]),
                         sigma_r=sigma_r, acf1=acf1, tl=tl))

    return pd.DataFrame(rows).set_index("label")


def merge_with_tdi(tl_df: pd.DataFrame, tdi_path: str = "empirical_tdi_results.csv") -> pd.DataFrame:
    tdi = pd.read_csv(tdi_path)
    tdi = tdi[tdi["n_institutions"] >= 50].copy()
    tdi = tdi.set_index("label")

    merged = tdi.join(tl_df[["sigma_r", "acf1", "tl", "qreturn"]], how="inner")
    merged = merged.dropna(subset=["tl", "TDI"])
    return merged


def print_correlations(merged: pd.DataFrame):
    print("\n=== Empirical TL correlations ===")
    for col in ["TDI", "VIX_avg"]:
        if col in merged.columns:
            sub = merged.dropna(subset=["tl", col])
            r, p = stats.pearsonr(sub["tl"], sub[col])
            print(f"  r(TL, {col}) = {r:.3f}  p = {p:.4f}  n = {len(sub)}")

    # TDI predicting next-quarter TL (forward lag)
    merged_sorted = merged.sort_index()
    tdi_vals = merged_sorted["TDI"].values
    tl_vals  = merged_sorted["tl"].values
    if len(tdi_vals) > 2:
        r_fwd, p_fwd = stats.pearsonr(tdi_vals[:-1], tl_vals[1:])
        print(f"  r(TDI[t], TL[t+1]) = {r_fwd:.3f}  p = {p_fwd:.4f}  n = {len(tdi_vals)-1}")


def make_figure(merged: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Empirical Temporal Liquidity vs. TDI and VIX", fontsize=13)

    # TL vs TDI scatter
    ax = axes[0]
    sub = merged.dropna(subset=["tl", "TDI"])
    ax.scatter(sub["TDI"], sub["tl"], color="#C5A028", alpha=0.7, s=50)
    r, p = stats.pearsonr(sub["TDI"], sub["tl"])
    m, b = np.polyfit(sub["TDI"], sub["tl"], 1)
    x_line = np.linspace(sub["TDI"].min(), sub["TDI"].max(), 100)
    ax.plot(x_line, m * x_line + b, "k--", linewidth=1.5)
    ax.set_xlabel("TDI (horizon diversity)")
    ax.set_ylabel("Empirical TL")
    ax.set_title(f"TL vs TDI  (r = {r:.3f}, p = {p:.4f}, n = {len(sub)})")
    ax.grid(True, alpha=0.3)

    # TL time series vs VIX
    ax2 = axes[1]
    merged_sorted = merged.sort_index().reset_index()
    ax2.plot(range(len(merged_sorted)), merged_sorted["tl"],
             color="#C5A028", label="Empirical TL", linewidth=1.5)
    ax2r = ax2.twinx()
    ax2r.plot(range(len(merged_sorted)), merged_sorted["VIX_avg"],
              color="#E05C2A", linestyle="--", label="VIX", linewidth=1.2, alpha=0.8)
    ax2.set_xlabel("Quarter (sorted)")
    ax2.set_ylabel("TL", color="#C5A028")
    ax2r.set_ylabel("VIX", color="#E05C2A")
    ax2.set_title("Empirical TL and VIX over time")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("figures/empirical_tl.png", dpi=150, bbox_inches="tight")
    print("Saved: figures/empirical_tl.png")


def main():
    if not HAVE_YF:
        print("Install yfinance to run this script: pip install yfinance")
        return

    print("Downloading SPY quarterly returns...")
    try:
        qreturns = fetch_spy_quarterly()
    except Exception as e:
        print(f"Download failed: {e}")
        return

    print(f"  Got {len(qreturns)} quarters of SPY data.")

    print("Computing rolling σ_r, ACF_1, TL...")
    tl_df = compute_empirical_tl(qreturns)

    print("Merging with TDI panel...")
    try:
        merged = merge_with_tdi(tl_df)
    except FileNotFoundError:
        print("empirical_tdi_results.csv not found. Run from cme_validation/ directory.")
        return

    print(f"  Merged panel: {len(merged)} quarters.")
    print("\nSample rows:")
    print(merged[["TDI", "VIX_avg", "sigma_r", "acf1", "tl"]].head(10).to_string())

    print_correlations(merged)
    make_figure(merged)

    # Save merged data
    merged.to_csv("empirical_tl_results.csv")
    print("Saved: empirical_tl_results.csv")
    print("\nDone.")


if __name__ == "__main__":
    main()
