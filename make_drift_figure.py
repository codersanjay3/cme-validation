"""Figure: value-weight vs share-based TDI against VIX."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

R = "/Users/sanjaysubramania/cme_validation/"
o = pd.read_csv(R + "empirical_tdi_results.csv"); o = o[o.n_institutions >= 50]
o["quarter"] = o.year.astype(str) + "Q" + o.quarter.astype(str)
n = pd.read_csv(R + "price_adjusted_tdi_results.csv")
d = n.merge(o[["quarter", "VIX_avg"]], on="quarter")
d = d[(d.quarter >= "2013Q3") & (d.quarter <= "2024Q3")].reset_index(drop=True)
z = lambda x: (x - x.mean()) / x.std()

fig, ax = plt.subplots(1, 3, figsize=(13, 3.8), gridspec_kw={"width_ratios": [1.5, 1, 1]})
x = np.arange(len(d))
ax[0].plot(x, z(d.tdi_w), color="#1f5fa8", lw=1.6, label="TDI, value-weight turnover")
ax[0].plot(x, z(d.tdi_s), color="#2a8f5a", lw=1.6, label="TDI, share-based turnover")
ax[0].plot(x, z(d.VIX_avg), color="#c0392b", lw=1.2, ls="--", label="VIX")
ticks = [i for i, q in enumerate(d.quarter) if q.endswith("Q1") and int(q[:4]) % 2 == 1]
ax[0].set_xticks(ticks); ax[0].set_xticklabels([d.quarter[i][:4] for i in ticks])
ax[0].set_ylabel("standardised"); ax[0].legend(fontsize=7.5, frameon=False, loc="lower left")
ax[0].set_title("(a) Series", fontsize=10)
for a_, col, c, t in ((ax[1], "tdi_w", "#1f5fa8", "(b) Value-weight turnover"),
                      (ax[2], "tdi_s", "#2a8f5a", "(c) Share-based turnover")):
    r, p = stats.pearsonr(d[col], d.VIX_avg)
    a_.scatter(d[col], d.VIX_avg, s=18, color=c, alpha=.85)
    k = np.polyfit(d[col], d.VIX_avg, 1); xs = np.linspace(d[col].min(), d[col].max(), 20)
    a_.plot(xs, np.polyval(k, xs), color="k", lw=1)
    a_.set_xlabel("TDI"); a_.set_ylabel("VIX (quarterly mean)")
    a_.set_title(f"{t}\n$r$ = {r:+.2f}", fontsize=10)
for a_ in ax: a_.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(R + "figures/drift_check.png", dpi=200)
print(len(d), "quarters saved")
