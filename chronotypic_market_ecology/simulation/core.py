"""
CME Simulation Core — Briefing-Spec Parameters + CME v4 Validated Mechanics
=============================================================================
Parameters match the briefing Section 2 specification:
  N=120, T=700, kh: 30 levels × 20 seeds, d_max=14
  alpha_i ~ U(0.22, 0.38), beta_i ~ U(0.12, 0.28), w_i ~ LN(0, 0.4)

Core mechanics use the CME v4 validated approach (noise amplification for
the friction effect), since the bilateral price formula creates a level
effect rather than a volatility effect. The two approaches are complementary;
noise amplification is the mechanism that produces the paper's published
results and makes gamma sensitivity meaningful for Task 1.

Key validated mechanics (CME v4 Bug fixes):
  Bug 2: conn_w = log(1+lambda_2)/log(2)      smooth spectral-gap blend
  Bug 3: concentration param varies TDI
  Bug 4: momentum uses log returns
  Bug 5: eff_noise = noise_vol*(1 + gamma*mean_td)  friction as noise amplifier
  Bug 6: crash threshold = absolute -2%
  Bug 7: spectral gap = ev[1] (true Fiedler value)
"""

import numpy as np
from scipy import stats

# ── Investor type definitions (briefing Table 1) ──────────────────────────────
INVESTOR_TYPES = {
    'HFT_quant': {
        'color': '#CC3311', 'label': 'HFT / Quant',
        'tau_lognorm': (0.5, 0.6),
        'tau_clip':    (1,   20),
        'weight':       0.15,
    },
    'hedge_fund': {
        'color': '#E69F00', 'label': 'Hedge Fund',
        'tau_lognorm': (2.8, 0.7),
        'tau_clip':    (15,  120),
        'weight':       0.25,
    },
    'mutual_fund': {
        'color': '#0072B2', 'label': 'Mutual Fund',
        'tau_lognorm': (4.2, 0.6),
        'tau_clip':    (60,  400),
        'weight':       0.40,
    },
    'pension_value': {
        'color': '#009E73', 'label': 'Pension / Value',
        'tau_lognorm': (6.0, 0.8),
        'tau_clip':    (400, 2000),
        'weight':       0.20,
    },
}

COMPOSITIONS = {
    '2005': {'HFT_quant':0.020,'hedge_fund':0.055,
             'mutual_fund':0.620,'pension_value':0.305},
    '2010': {'HFT_quant':0.095,'hedge_fund':0.075,
             'mutual_fund':0.555,'pension_value':0.275},
    '2015': {'HFT_quant':0.112,'hedge_fund':0.088,
             'mutual_fund':0.535,'pension_value':0.265},
    '2020': {'HFT_quant':0.130,'hedge_fund':0.092,
             'mutual_fund':0.520,'pension_value':0.258},
    '2023': {'HFT_quant':0.150,'hedge_fund':0.098,
             'mutual_fund':0.500,'pension_value':0.252},
}


def sample_taus(n, composition=None, concentration=1.0, seed=None):
    """
    Sample agent temporal scales (tau values) in trading days.

    concentration > 1 : tighter distribution -> lower TDI
    concentration < 1 : wider distribution  -> higher TDI
    """
    if seed is not None:
        np.random.seed(seed)
    if composition is None:
        composition = {k: v['weight'] for k, v in INVESTOR_TYPES.items()}

    total = sum(composition.values())
    comp  = {k: v / total for k, v in composition.items()}
    taus, labels = [], []

    for itype, frac in comp.items():
        n_i = max(1, int(round(n * frac)))
        mu, sg = INVESTOR_TYPES[itype]['tau_lognorm']
        lo, hi = INVESTOR_TYPES[itype]['tau_clip']
        sg_eff = sg / concentration
        raw = np.exp(np.random.normal(mu, sg_eff, n_i * 8))
        raw = raw[(raw >= lo) & (raw <= hi)]
        while len(raw) < n_i:
            raw = np.concatenate([
                raw, np.exp(np.random.normal(mu, sg_eff, n_i * 4))
            ])
            raw = raw[(raw >= lo) & (raw <= hi)]
        taus.extend(raw[:n_i])
        labels.extend([itype] * n_i)

    return np.array(taus[:n], dtype=float), labels[:n]


def build_network(taus, kappa_h=2.0, max_deg=14, seed=None):
    """
    Build directed tau-proximity network.

    P(i->j) ∝ exp(-kappa_h * |log(tau_i+1) - log(tau_j+1)|)
    Max out-degree = max_deg = 14 (briefing spec, Section 2.5).
    Returns adj (N×N) raw weight matrix.
    """
    if seed is not None:
        np.random.seed(seed)
    n  = len(taus)
    lt = np.log(taus + 1)

    dist   = np.abs(lt[:, None] - lt[None, :])
    prob   = np.exp(-kappa_h * dist)
    np.fill_diagonal(prob, 0)
    rs     = prob.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1
    prob_n = prob / rs

    adj = np.zeros((n, n))
    for i in range(n):
        p = prob_n[i].copy()
        n_elig = int((p > 1e-4).sum())
        d = min(max_deg, n_elig)
        if d == 0:
            continue
        p_sum = p.sum()
        if p_sum < 1e-12:
            continue
        chosen = np.random.choice(n, size=d, replace=False, p=p / p_sum)
        for j in chosen:
            adj[i, j] = prob[i, j]

    return adj


def tdi(taus, n_bins=15):
    """
    Temporal Diversity Index: Shannon entropy of log(tau+1) histogram.
    (briefing Section 7.7)
    """
    lt = np.log(np.array(taus) + 1)
    h, _ = np.histogram(lt, bins=n_bins)
    h = h[h > 0].astype(float)
    h /= h.sum()
    return float(-np.sum(h * np.log(h)))


def spectral_gap(adj):
    """
    Fiedler value λ₂ of the normalised Laplacian.
    Returns ev[1] — the true second-smallest eigenvalue.
    (Bug 7 fix: ev[1] not min(ev[ev>1e-10]))
    """
    n = adj.shape[0]
    if n < 3:
        return 0.0
    deg     = adj.sum(axis=1)
    d_inv_s = np.diag(1.0 / (np.sqrt(deg) + 1e-10))
    L       = np.eye(n) - d_inv_s @ adj @ d_inv_s
    try:
        ev = np.sort(np.real(np.linalg.eigvalsh(L)))
        return float(np.clip(ev[1], 0.0, 2.0)) if len(ev) >= 2 else 0.0
    except Exception:
        return 0.0


def assortativity(G_adj, taus):
    """
    Tau-assortativity: Pearson r between log(tau_i) and log(mean tau of neighbours).
    """
    n = len(taus)
    tau_self, tau_nbr_mean = [], []
    for i in range(n):
        nbrs = np.where(G_adj[i] > 0)[0]
        if len(nbrs) > 0:
            tau_self.append(taus[i])
            tau_nbr_mean.append(np.mean(taus[nbrs]))
    if len(tau_self) < 5:
        return 0.0, 1.0
    r, p = stats.pearsonr(np.log(np.array(tau_self) + 1e-10),
                          np.log(np.array(tau_nbr_mean) + 1e-10))
    return float(r), float(p)


def tmfi(lp_series, taus, n_communities=4):
    """
    Temporal Market Fragmentation Index (briefing Section 2.9 / 7.6).

    Partition agents into C=4 log-tau quartile communities.
    TMFI(t) = std(community_mean_prices) / mean(community_mean_prices)
    Returns (mean_tmfi_over_run, full_tmfi_timeseries).
    """
    lt  = np.log(np.array(taus) + 1)
    qs  = np.percentile(lt, np.linspace(0, 100, n_communities + 1))
    comms = [
        np.where((lt >= qs[k]) & (lt < qs[k + 1]))[0]
        for k in range(n_communities)
    ]
    comms = [c for c in comms if len(c) > 0]

    T = lp_series.shape[0]
    tmfi_ts = np.zeros(T)
    for t in range(T):
        cp = np.array([lp_series[t, c].mean() for c in comms])
        if len(cp) > 1 and cp.mean() > 1e-10:
            tmfi_ts[t] = cp.std() / cp.mean()

    return float(tmfi_ts.mean()), tmfi_ts


def run_market(taus, adj, T=700, lam=0.008, gamma=0.20,
               fund_vol=0.010, noise_vol=0.005, seed=None):
    """
    Market simulation with CME v4 validated mechanics and briefing parameters.

    PRICE FORMATION (CME v4 Bug 2 fix):
      p_obs_i = conn_w * mean(p_neighbours) + (1-conn_w) * p_global
      conn_w = log(1+lambda_2)/log(2)  [smooth spectral-gap blend]

    DEMAND (briefing Section 2.4):
      d_i = alpha_i*(F - p_bar_i)/p_obs_i + beta_i*m_i + epsilon_i
      p_bar_i = mean of last tau_i observations of p_obs (not global price)
      m_i = mean log-return of p_obs over tau_i window (Bug 4 fix)
      epsilon_i ~ N(0, noise_vol^2)

    FRICTION (CME v4 Bug 5 fix — gamma as noise amplifier):
      eff_noise_i = noise_vol * (1 + gamma * mean_tau_dist_to_neighbours)
      High gamma + cross-tau neighbours → amplified noise → more vol at kh=0

    PRICE UPDATE (briefing Section 2.6):
      p_i(t) = p_i(t-1) * exp(lam*[0.6*d_i + 0.4*d_bar_N] + eff_noise_i*z_i)

    GLOBAL PRICE (briefing Section 2.7):
      p(t) = Σ_i w̃_i * p_i(t),  w̃_i = deg_i*w_i / Σ_j deg_j*w_j
      where w_i ~ LN(0, 0.4) is agent wealth

    Returns: global_prices, log_returns, fundamentals, local_prices, lambda2
    """
    if seed is not None:
        np.random.seed(seed)

    n = len(taus)
    lt       = np.log(np.array(taus) + 1)
    tau_arr  = np.clip(np.array(taus, dtype=int), 1, max(T // 3, 10))

    # ── Precompute friction per agent ─────────────────────────────────────────
    tau_dist = np.abs(lt[:, None] - lt[None, :])   # (n, n)
    nb_mask  = (adj > 0).astype(float)              # (n, n) binary edge mask
    nb_count = nb_mask.sum(axis=1)                  # (n,) number of neighbours

    # Mean tau-distance to neighbours; 0 for isolated agents
    mean_td = np.where(
        nb_count > 0,
        (tau_dist * nb_mask).sum(axis=1) / (nb_count + 1e-10),
        0.0
    )
    # Bug 5 fix: friction amplifies effective noise vol per agent
    eff_noise = noise_vol * (1.0 + gamma * mean_td)   # (n,)

    # ── Network matrices ──────────────────────────────────────────────────────
    rs    = adj.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1
    adj_n = adj / rs   # (n, n) row-normalised

    # ── Agent wealth and degree weights (briefing Section 2.3 + 2.7) ─────────
    w_i = np.exp(np.random.normal(0, 0.4, n))   # LN(0, 0.4)
    deg = adj.sum(axis=1)
    dw  = deg * w_i
    if dw.sum() > 1e-10:
        dw /= dw.sum()
    else:
        dw = np.ones(n) / n

    # ── Spectral gap → connectivity weight (Bug 2 fix) ───────────────────────
    lam2   = spectral_gap(adj)
    conn_w = float(np.clip(np.log(1 + lam2) / np.log(2), 0.03, 0.95))

    # ── Agent parameters (briefing Section 2.3) ───────────────────────────────
    alpha = np.random.uniform(0.22, 0.38, n)   # U(0.22, 0.38)
    beta  = np.random.uniform(0.12, 0.28, n)   # U(0.12, 0.28)

    # ── Pre-generate shocks ───────────────────────────────────────────────────
    fund_shocks = np.random.normal(0, fund_vol, T)
    noise_draws = np.random.normal(0, 1.0, (T, n))  # unit normals, scaled by eff_noise

    # ── State arrays ─────────────────────────────────────────────────────────
    lp = np.full((T, n), 100.0)   # local prices (start at 100, as in CME v4)
    gp = np.zeros(T);  gp[0] = 100.0
    fn = np.zeros(T);  fn[0] = 100.0

    # ── Precompute for vectorised inner loop ─────────────────────────────────
    agent_idx = np.arange(n)       # reused for fancy indexing

    # Cumulative-sum history: cs_hist[t, i] = lp[0,i] + ... + lp[t,i]
    cs_hist = np.zeros((T, n))
    cs_hist[0] = lp[0]

    # ── Main simulation loop (fully vectorised over agents) ───────────────────
    for t in range(1, T):
        # Step 1: Fundamental update
        fn[t] = fn[t - 1] * np.exp(fund_shocks[t])

        # Step 2: p_obs — neighbourhood blend with global (Bug 2)
        nbr_avg = adj_n @ lp[t - 1]
        p_obs   = conn_w * nbr_avg + (1.0 - conn_w) * gp[t - 1]
        p_obs[nb_count == 0] = gp[t - 1]

        # Step 3: Vectorised p_bar via cumulative sums
        # cs_hist[t-1, i] = lp[0,i] + ... + lp[t-1,i]
        lo      = np.maximum(0, t - tau_arr)          # (n,) window start
        lo_m1   = lo - 1                               # (n,), possibly -1
        prev_cs = np.where(lo > 0,
                           cs_hist[lo_m1, agent_idx], 0.0)
        p_bar   = (cs_hist[t - 1] - prev_cs) / np.maximum(1, t - lo)

        # Step 4: Vectorised momentum (mean log-return over tau_i window)
        # = (log(lp[t-1]) - log(lp[lo])) / max(1, t-1-lo)   [Bug 4: log returns]
        p_at_lo   = lp[lo, agent_idx]                  # (n,) fancy indexed
        log_diff  = np.log(lp[t - 1] + 1e-10) - np.log(p_at_lo + 1e-10)
        ms_all    = np.where(
            t - 1 > lo,
            beta * log_diff / np.maximum(1, t - 1 - lo),
            0.0
        )

        # Step 5: Demand (vectorised)
        p_obs_safe = np.maximum(p_obs, 1e-6)
        dm = alpha * (fn[t] - p_bar) / p_obs_safe + ms_all

        # Step 6: Neighbourhood average demand (60/40 split)
        d_bar_N = adj_n @ dm

        # Step 7: Price update with noise amplification (Bug 5, vectorised)
        lp[t] = lp[t - 1] * np.exp(
            lam * (0.6 * dm + 0.4 * d_bar_N) + eff_noise * noise_draws[t]
        )
        lp[t] = np.clip(lp[t], 1.0, 1e5)

        # Step 8: Global price (degree × wealth weighted)
        gp[t] = float(np.clip(dw @ lp[t], 1.0, 1e5))

        # Update cumulative sum for next step
        cs_hist[t] = cs_hist[t - 1] + lp[t]

    log_returns = np.diff(np.log(gp + 1e-10))
    return gp, log_returns, fn, lp, lam2


def diagnostics(gp, log_returns, fn, lp, taus):
    """
    Compute all market quality metrics for one simulation run.

    vol      : std of log returns
    kurt     : excess kurtosis (normal = 0)
    misprice : mean |log(price/fundamental)|
    vol_acf  : ACF of |returns| at lag 5 (volatility clustering)
    crash    : fraction of returns < -2% (absolute threshold, Bug 6 fix)
    tdi_v    : Temporal Diversity Index
    tmfi_v   : mean Temporal Market Fragmentation Index
    tl       : Temporal Liquidity = 1/(vol * vol_acf * crash_excess)
    """
    d = {}
    d['vol']      = float(np.std(log_returns))
    d['kurt']     = float(stats.kurtosis(log_returns))
    d['misprice'] = float(np.mean(np.abs(np.log(gp / (fn + 1e-10) + 1e-10))))

    ar  = np.abs(log_returns)
    x   = ar - ar.mean()
    c0  = float(np.dot(x, x))
    lag = min(5, len(x) // 8)
    d['vol_acf'] = float(
        np.dot(x[:-lag], x[lag:]) / c0 if c0 > 1e-12 else 0.001
    )

    d['crash']  = float(np.mean(log_returns < -0.02))
    d['tdi_v']  = tdi(taus)
    tmfi_mean, _ = tmfi(lp, taus)
    d['tmfi_v'] = tmfi_mean

    crash_excess = max(1.0, d['crash'] / 0.05)
    d['tl'] = 1.0 / (d['vol'] * max(0.001, d['vol_acf']) * crash_excess + 1e-8)

    return d
