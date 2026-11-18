"""
Extension: Asset-class heterogeneity sweep.

Tests CME's stability-fragmentation predictions across three market types
with different chronotype compositions, as suggested by Prof. Chalmers:
  - Bond market   : predominantly long-horizon (pension + mutual fund)
  - Equity market : current calibration (mixed)
  - FX/derivatives: predominantly short-horizon (HFT + hedge fund)

Run: python asset_class_sweep.py
"""

import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── re-use core helpers from simulate.py ────────────────────────────────────
from simulate import (
    build_network, fiedler_value, compute_tdi,
    tau_assortativity, community_assignments,
)


# ── Asset-class chronotype configurations ───────────────────────────────────

ASSET_CLASSES = {
    "bond": {
        "label": "Bond market",
        "counts":     [4,  8,  36, 32],   # 5% HFT, 10% hedge, 45% mutual, 40% pension
        "tau_params": [(0.5,0.6),(2.8,0.7),(4.2,0.6),(6.0,0.8)],
        "tau_bounds": [(1,20),(15,120),(60,400),(400,2000)],
        "color": "#2196F3",
    },
    "equity": {
        "label": "Equity market (baseline)",
        "counts":     [12, 20, 32, 16],   # original calibration
        "tau_params": [(0.5,0.6),(2.8,0.7),(4.2,0.6),(6.0,0.8)],
        "tau_bounds": [(1,20),(15,120),(60,400),(400,2000)],
        "color": "#C5A028",
    },
    "fx": {
        "label": "FX / derivatives market",
        "counts":     [32, 28, 12,  8],   # 40% HFT, 35% hedge, 15% mutual, 10% pension
        "tau_params": [(0.5,0.6),(2.8,0.7),(4.2,0.6),(6.0,0.8)],
        "tau_bounds": [(1,20),(15,120),(60,400),(400,2000)],
        "color": "#E05C2A",
    },
}


def sample_tau_asset(cfg: dict, seed: int = 42) -> np.ndarray:
    """Sample tau values according to the given asset-class configuration."""
    rng = np.random.default_rng(seed)
    tau = []
    for count, (mu, sig), (lo, hi) in zip(
        cfg["counts"], cfg["tau_params"], cfg["tau_bounds"]
    ):
        collected = []
        while len(collected) < count:
            batch = np.exp(rng.normal(mu, sig, 400))
            batch = batch[(batch >= lo) & (batch <= hi)]
            collected.extend(batch.tolist())
        tau.extend([int(round(x)) for x in collected[:count]])
    return np.array(tau)


def simulate_one_run_asset(
    cfg: dict,
    n: int = 80,
    T: int = 500,
    kh: float = 0.0,
    seed: int = 42,
    dmax: int = 12,
    gamma: float = 0.20,
    price_impact: float = 0.008,
    sigma_F: float = 0.010,
    sigma0: float = 0.00012,
    alpha_bar: float = 0.30,
    beta_bar: float = 0.20,
) -> dict:
    rng = np.random.default_rng(seed)

    tau  = sample_tau_asset(cfg, seed=seed)
    adj  = build_network(tau, kh, dmax=dmax, rng=rng)
    lam2 = fiedler_value(adj)
    comm = community_assignments(tau)

    W = adj.copy()
    row_s = W.sum(axis=1, keepdims=True)
    W = np.where(row_s > 0, W / row_s, 0.0)

    c_lam = np.log(1.0 + lam2) / np.log(2.0)

    log_tau = np.log(tau + 1)
    d_tau = np.zeros(n)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs):
            d_tau[i] = np.mean(np.abs(log_tau[i] - log_tau[nbrs]))
    sigma_eff = sigma0 * (1.0 + gamma * d_tau)

    max_tau = int(tau.max())
    buf_len = T + max_tau + 10
    p_hist  = np.full(buf_len, 100.0)

    F        = 100.0
    p_global = 100.0
    returns  = []
    tmfi_vals = []
    acf_prices = []

    for t in range(T):
        idx = max_tau + t
        F *= np.exp(rng.normal(0.0, sigma_F))

        noise_obs = rng.normal(0.0, sigma_eff)
        p_j = p_global * (1.0 + noise_obs)
        p_nbr_avg = W @ p_j
        p_obs = c_lam * p_nbr_avg + (1.0 - c_lam) * p_global

        p_bar = np.array([
            p_hist[max(0, idx - int(tau[i])):idx].mean() if idx > 0 else 100.0
            for i in range(n)
        ])
        p_past = np.array([
            p_hist[max(0, idx - int(tau[i]))] for i in range(n)
        ])
        momentum = np.where(p_past > 0, np.log(p_global / p_past), 0.0)

        eps = rng.normal(0.0, sigma_eff)
        demand = (alpha_bar * (F - p_bar) / np.maximum(p_obs, 1e-3)
                  + beta_bar * momentum
                  + eps)

        p_global_new = p_global + price_impact * demand.sum()
        if t > 0:
            returns.append((p_global_new - p_global) / p_global)

        p_hist[idx] = p_global_new
        p_global = p_global_new
        acf_prices.append(p_global_new)

        if t >= T // 2:
            comm_means = [
                p_bar[comm == c].mean() if (comm == c).any() else p_global
                for c in range(4)
            ]
            arr = np.array(comm_means)
            m = arr.mean()
            if m > 1e-6:
                tmfi_vals.append(arr.std(ddof=0) / m)

    returns = np.array(returns)
    vol  = returns.std()
    tmfi = float(np.mean(tmfi_vals)) if tmfi_vals else 0.0

    # Temporal Liquidity: TL = 1 / (σ_r * |ACF_1|)
    if len(returns) > 2:
        acf1 = float(np.corrcoef(returns[:-1], returns[1:])[0, 1])
        tl = 1.0 / (vol * abs(acf1) + 1e-12) if abs(acf1) > 1e-8 else np.nan
    else:
        acf1 = np.nan
        tl   = np.nan

    tdi = compute_tdi(tau, K=20)

    return dict(volatility=vol, tmfi=tmfi, tdi=tdi, lambda2=lam2,
                acf1=acf1, tl=tl)


def run_asset_sweep(kh_values=None, n_seeds=10):
    if kh_values is None:
        kh_values = np.linspace(0, 6, 25)

    all_results = {}
    for key, cfg in ASSET_CLASSES.items():
        print(f"\n=== {cfg['label']} ===")
        rows = []
        for kh in kh_values:
            for seed in range(n_seeds):
                r = simulate_one_run_asset(cfg, kh=float(kh), seed=seed)
                r["kh"] = float(kh)
                r["seed"] = seed
                r["asset_class"] = key
                rows.append(r)
            print(f"  kh={kh:.2f} done", flush=True)
        all_results[key] = rows

    return all_results


def summarise(rows, metric):
    khs = sorted(set(r["kh"] for r in rows))
    means, stds = [], []
    for kh in khs:
        vals = [r[metric] for r in rows if r["kh"] == kh and not np.isnan(r[metric])]
        means.append(np.mean(vals))
        stds.append(np.std(vals))
    return np.array(khs), np.array(means), np.array(stds)


def make_figures(all_results):
    kh_values = np.linspace(0, 6, 25)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Asset-Class Chronotype Heterogeneity: Stability-Fragmentation Curves",
                 fontsize=13, y=1.02)

    metrics = [
        ("volatility", "Return volatility (σ_r)", "Volatility"),
        ("tmfi",       "TMFI (cross-community price dispersion)", "TMFI"),
        ("tl",         "Temporal Liquidity (TL)", "TL"),
    ]

    for ax, (metric, ylabel, title) in zip(axes, metrics):
        for key, cfg in ASSET_CLASSES.items():
            rows = all_results[key]
            khs, means, stds = summarise(rows, metric)
            ax.plot(khs, means, label=cfg["label"], color=cfg["color"], linewidth=2)
            ax.fill_between(khs, means - stds, means + stds,
                            alpha=0.15, color=cfg["color"])
        ax.set_xlabel("Homophily κ_h")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("figures/asset_class_comparison.png", dpi=150, bbox_inches="tight")
    print("\nSaved: figures/asset_class_comparison.png")


def print_key_stats(all_results):
    print("\n=== Key Statistics: kh=0 vs kh=6 ===")
    for key, cfg in ASSET_CLASSES.items():
        rows = all_results[key]
        for metric in ["volatility", "tmfi", "tl"]:
            lo = [r[metric] for r in rows if abs(r["kh"]) < 0.01 and not np.isnan(r[metric])]
            hi = [r[metric] for r in rows if abs(r["kh"] - 6.0) < 0.01 and not np.isnan(r[metric])]
            if lo and hi:
                ratio = np.mean(lo) / np.mean(hi) if np.mean(hi) > 0 else np.nan
                t_stat, p_val = stats.ttest_rel(lo[:min(len(lo), len(hi))],
                                                hi[:min(len(lo), len(hi))])
                print(f"  {cfg['label']:35s} {metric:12s}: "
                      f"kh=0 {np.mean(lo):.4f} | kh=6 {np.mean(hi):.4f} | "
                      f"ratio {ratio:.3f}x | t={t_stat:.2f} p={p_val:.4f}")


if __name__ == "__main__":
    print("Running asset-class heterogeneity sweep (3 configs × 25 kh × 10 seeds)...")
    all_results = run_asset_sweep(n_seeds=30)

    # Save raw results
    serialisable = {k: v for k, v in all_results.items()}
    with open("asset_class_results.json", "w") as f:
        json.dump(serialisable, f, indent=2)
    print("Saved: asset_class_results.json")

    print_key_stats(all_results)
    make_figures(all_results)
    print("\nDone.")
