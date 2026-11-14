#!/usr/bin/env python3
"""Stage 2, step 12: expected exclusion bands ("Brazil band"), 13.6 TeV, 332 fb^-1. Background-only experiments: n_obs ~ Poisson(b); for each n_obs the
CLs 95% signal s95(n_obs, b) (same formula as S2_09 / S2_11, there with n_obs = round(b)); the reach at that threshold with the central signal grid
(F6_04 algorithm, functions of S2_11). Band = reach at the n_obs quantiles of Poisson(b) for the probabilities of -2, -1, 0, +1, +2 sigma (2.28, 15.87, 50,
84.13, 97.72 %); a larger n_obs gives a weaker limit, i.e. the +sigma quantile of n_obs gives the lower reach. Poisson only: the MC uncertainty of b and of
the signal (S2_11) is not in this band. Rows: sigma_z = 0 with b of S2_09 (mu = 0 / 20 / 50 / 60); SCT 1.16 mm with b = 0 (as the main result) and with the
95% upper bound b_UL of the k = 0 background count (illustration, conservative). Output: S2_expected_bands.csv. Run with /home/rafia/venvs/f6fast/bin/python."""
import os, numpy as np, pandas as pd
from scipy import stats, optimize
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/S2_11_uncertainties.py").read(); exec(src[:src.index("S = {(E, ch)")])  # imports, sample(), reach(), grid(), SG, BK of S2_11 (no toys run)
P = stats.norm.cdf([-2, -1, 0, 1, 2])
def s95n(n, b):
    if b == 0: return -np.log(0.05) if n == 0 else np.nan                     # b = 0: n_obs = 0 always, s95 = 3.0
    return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-4, 500)
BKall = pd.read_csv(f"{HERE}/S2_background_13p6TeV.csv"); BKall = BKall[BKall.process == "conversion + pile-up"]
rows = []
for ch in ("colored", "EW"):
    A = sample("13.6", ch)
    for sct in ("Z1160", "Z0"):
        G = grid(A, sct, 332.0)
        cases = [(r.mu, f"S2_09 count {int(r.sr)}/{int(r.n)}", 332.0 * SG * r.sr / r.n) for r in BKall[BKall.sct == "Z0"].itertuples()] if sct == "Z0" else \
                [(-1, "b = 0 (main result)", 0.0)] + [(r.mu, f"95% UL of {int(r.sr)}/{int(r.n)}", r.b_used_332fb) for r in BKall[BKall.sct == "Z1160"].itertuples()]
        for mu, how, b in cases:
            nq = [0] * 5 if b == 0 else [int(stats.poisson.ppf(p, b)) for p in P]   # n_obs quantiles at -2..+2 sigma
            thr = [s95n(n, b) for n in nq]; R = [reach(*G, t) for t in thr]
            r = dict(channel=ch, sct=sct, mu=mu, b_source=how, b=b, nominal_n_obs=int(round(b)), nominal_s95=s95n(int(round(b)), b), nominal_reach=reach(*G, s95n(int(round(b)), b)))
            for lab, n, t, x in zip(("m2", "m1", "med", "p1", "p2"), nq, thr, R): r.update({f"n_obs_{lab}": n, f"s95_{lab}": t, f"reach_{lab}": x})
            r.update({"P_n_obs_0": stats.poisson.pmf(0, b)}); rows.append(r)
            print(ch, sct, mu, f"b={b:.3f}", "n_obs", nq, "reach", [round(x) for x in R], "nominal", round(r["nominal_reach"]), flush=True)
pd.DataFrame(rows).to_csv(f"{HERE}/S2_expected_bands.csv", index=False)
print("S2_12_EXIT=0")
