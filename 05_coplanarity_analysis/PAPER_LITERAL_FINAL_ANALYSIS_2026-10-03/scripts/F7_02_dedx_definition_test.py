#!/usr/bin/env python3
"""Fig. 7 (2026-10-20): which dE/dx definition turns the paper's OWN betagamma histogram (right panel) into its dE/dx histogram (left panel)? No simulation.
Input: tables/paper_fig7_vector.json (S5_fig7_vector_extract.py; step histograms of both panels, EW 800 GeV and colored 1800 GeV, Lambda = 2 keV).
Four definitions of dE/dx(betagamma), silicon (Z/A = 0.49848, I = 173 eV, rho = 2.329 g/cm^3, Sternheimer density effect as F7_dedx.py), unit charge:
  1 PDG most probable value (Eq. 34.12), 250 um, MeV cm^2/g         (what the report uses)
  2 Bethe mean (Eq. 34.5, W_max = 2 m_e b^2 g^2 for a heavy particle), MeV cm^2/g
  3 Bethe mean x rho, MeV/cm
  4 PDG most probable value x rho, MeV/cm
Each betagamma bin is split into 50 log-uniform points carrying its weight. The Bethe formula is not valid at low betagamma (shell corrections, Bragg peak);
bins with betagamma < BGMIN are left out and their fraction is reported (variant BGMIN = 0.1, as in the report, and 0.05).
CRITERION (fixed before the test was run): a definition reproduces the paper if, for BOTH samples, the median of the converted distribution is within 15% of
the median of the paper's dE/dx histogram, and its 10% and 90% quantiles are each within 25% of the paper's (shape and range).
Also written: the fraction of converted hits below the paper histogram's lowest bin edge (18.9), which the paper's histogram does not populate.
Output: tables/F7_dedx_definition_test.csv."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
V = json.load(open(f"{T}/paper_fig7_vector.json"))
K, ZA, ME, I, J, RHO = 0.307075, 0.49848, 0.51099895, 173e-6, 0.200, 2.329
X0, X1, A_, K_, C_, D0 = 0.2015, 2.8716, 0.14921, 3.2546, 4.4355, 0.14
MED_TOL, Q_TOL = 0.15, 0.25
def delta(bg):
    x = np.log10(bg); return np.where(x >= X1, 2 * np.log(10) * x - C_, np.where(x >= X0, 2 * np.log(10) * x - C_ + A_ * (X1 - x) ** K_, D0 * 10 ** (2 * (x - X0))))
def mpv(bg, t=0.025):                                                         # MeV cm^2/g; PDG Eq. 34.12, as F7_dedx.py / the report
    b2 = bg ** 2 / (1 + bg ** 2); xx = t * RHO; xi = 0.5 * K * ZA * xx / b2
    return xi / xx * (np.log(2 * ME * bg ** 2 / I) + np.log(xi / I) + J - b2 - delta(bg))
def mean(bg):                                                                 # MeV cm^2/g; PDG Eq. 34.5, heavy particle: W_max = 2 m_e c^2 b^2 g^2
    b2 = bg ** 2 / (1 + bg ** 2); wmax = 2 * ME * bg ** 2
    return K * ZA / b2 * (0.5 * np.log(2 * ME * bg ** 2 * wmax / I ** 2) - b2 - delta(bg) / 2)
DEFS = {"1 PDG MPV, MeV cm2/g": mpv, "2 Bethe mean, MeV cm2/g": mean, "3 Bethe mean x rho, MeV/cm": lambda b: mean(b) * RHO, "4 PDG MPV x rho, MeV/cm": lambda b: mpv(b) * RHO}
def segs(c, xlog):
    x, y = np.array(c["x"]), np.array(c["y"])
    return [(x[i], x[i + 1], y[i]) for i in range(len(x) - 1) if abs(y[i] - y[i + 1]) < 1e-12 and x[i + 1] > x[i] and y[i] > 1e-6]
def wq(v, w, qs):
    o = np.argsort(v); c = np.cumsum(w[o]) / w.sum(); return [float(v[o][min(np.searchsorted(c, q), len(v) - 1)]) for q in qs]
QS = (0.1, 0.5, 0.9); rows = []
for s in ("EW_800GeV_2keV", "colored_1800GeV_2keV"):
    sd = segs(V["dEdx"]["curves"][s], False)                                  # paper dE/dx: linear x, uniform within a bin
    xs = np.concatenate([np.linspace(lo, hi, 52)[1:-1] for lo, hi, _ in sd]); ws = np.concatenate([np.full(50, h / 50) for *_, h in sd])
    pq = wq(xs, ws, QS)
    sb = segs(V["betagamma"]["curves"][s], True)
    for bgmin in (0.1, 0.05):
        keep = [(lo, hi, h) for lo, hi, h in sb if lo >= bgmin * 0.9999]; fout = 1 - sum(h for *_, h in keep) / sum(h for *_, h in sb)
        bg = np.concatenate([np.logspace(np.log10(lo), np.log10(hi), 52)[1:-1] for lo, hi, _ in keep]); w = np.concatenate([np.full(50, h / 50) for *_, h in keep])
        for name, f in DEFS.items():
            v = f(bg); q = wq(v, w, QS); fb = float(w[v < sd[0][0]].sum() / w.sum())   # fraction below the paper histogram's lowest bin edge
            ok = abs(q[1] / pq[1] - 1) <= MED_TOL and all(abs(q[i] / pq[i] - 1) <= Q_TOL for i in (0, 2))
            rows.append(dict(sample=s, bg_min=bgmin, frac_hits_left_out=round(fout, 3), definition=name, q10=round(q[0], 2), median=round(q[1], 2), q90=round(q[2], 2),
                             frac_below_paper_min=round(fb, 3), paper_min=round(sd[0][0], 1), paper_q10=round(pq[0], 2), paper_median=round(pq[1], 2), paper_q90=round(pq[2], 2), median_ratio=round(q[1] / pq[1], 3), sample_pass=ok))
D = pd.DataFrame(rows)
D["definition_pass"] = D.groupby(["bg_min", "definition"]).sample_pass.transform("all")   # criterion: both samples
D.to_csv(f"{T}/F7_dedx_definition_test.csv", index=False)
pd.set_option("display.width", 250); print(D.drop(columns=["paper_q10", "paper_q90"]).to_string(index=False))
print("paper dE/dx quantiles (10/50/90%):", {s: list(D[D["sample"] == s].iloc[0][["paper_q10", "paper_median", "paper_q90"]]) for s in D["sample"].unique()})
print("definitions passing (both samples):", sorted(set(map(tuple, D[D.definition_pass][["bg_min", "definition"]].values))) or "none")
