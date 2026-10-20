#!/usr/bin/env python3
"""Figure 6 normalisation sensitivity (2026-10-17), no new simulation: every grid N from fig6/F6_N_grid.csv is rescaled and the contours redrawn.
This is a sensitivity study, not a fit: it shows which overall factor on the signal would move our contours onto the paper's.
Variants (applied to N with the charge factor; colored and EW):
  K-factor on sigma: colored x1.5, x1.8; EW x0.8, x0.9 (with the matched trigger EW is above the paper at K = 1), x1.2, x1.4; x2 for both = an N_Q = 2 reading of the paper's panel titles ("N_Q = 2 Quirks"), not applied in
  the main figure;
  EW trigger: matched + shower count N(pT(QQ) > 200)/N(matched) of each sample instead of the LO ratio sigma_B/sigma_A;
  annihilation, worst case (not simulated in the paper or here): N x survival from tables/D27_annihilation_B.txt (alpha = 0.05, c_sigma = 1, benchmark masses
  1800 / 800 GeV, linear in Lambda; Lambda < 1 keV uses the 1 keV value; EW above 5 keV uses the 5 keV value), applied to all masses (approximation).
Output: fig6/F6_reach_sensitivity.csv, FINAL_FIGURES/F6_kfactor/ (signal without SCT z smearing, the setting that reproduces Table I)."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, HERE)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
import fig_utils as fu
G = pd.read_csv(f"{ROOT}/fig6/F6_N_grid.csv"); V = json.load(open(f"{ROOT}/tables/paper_fig6_vector.json"))
C = pd.read_csv(f"{ROOT}/fig6/inputs/counts.csv"); LO = pd.read_csv(f"{ROOT}/fig6/F6_ew_lo_ratio.csv").set_index("mass_gev")
# EW LO-ratio trigger / matched-count trigger, per mass (alternative to the main matched-count trigger)
EWLO = {r.mass_gev: LO.ratio[r.mass_gev] / (r.n_trigger / r.n_matched) for r in C[C.channel == "EW"].itertuples()}   # LO-ratio trigger / matched-count trigger
# EW efficiency from the LO sample (D41, 800 GeV, 3000 events, no shower) instead of the matched sample: per-Lambda ratio of k/n at 800 GeV (1-5 keV;
# 1 elsewhere), applied to all EW masses (approximation)
_d41 = pd.DataFrame([r for l in open(f"{ROOT}/logs/D41_mg5_373_lo_events.jsonl") for r in json.loads(l)]); _n41 = _d41.event.nunique()
_g8 = G[(G.channel == "EW") & (G.mass_gev == 800) & (G.sct == "Z0")].set_index("lambda_keV")
LORAT = {lam: (int((_d41[_d41.lambda_keV == lam].fid.astype(bool) & _d41[_d41.lambda_keV == lam].final.astype(bool)).sum()) / _n41) / (_g8.loc[lam, "k"] / _g8.loc[lam, "n_prop"])
         for lam in (1, 2, 3, 4, 5)}
# annihilation survival (worst case alpha = 0.05)
S = {}
for l in open(f"{ROOT}/tables/D27_annihilation_B.txt"):
    p = l.split()
    if len(p) > 7 and "c_sigma=1" in l and p[3] == "0.05": S.setdefault("colored" if p[0] == "COL2000" else "EW", {})[float(p[1]) / 1e3] = float(p[-2])
def surv(ch, lam):
    t = S[ch]; xs = np.array(sorted(t)); ys = np.array([t[x] for x in xs]); return float(np.interp(lam, xs, ys, left=ys[0], right=ys[-1]))
def scaled(g, ch, var):
    g = g.copy(); f = np.ones(len(g))
    if var.startswith("K"): f[:] = float(var[1:])
    elif var == "EW LO-ratio trigger": f = g.mass_gev.map(EWLO).values
    elif var == "annihilation worst": f = np.array([surv(ch, l) for l in g.lambda_keV])
    elif var == "EW fully LO": f = g.mass_gev.map(EWLO).values * np.array([LORAT.get(float(l), 1.0) for l in g.lambda_keV])   # LO trigger and LO efficiencies (800 GeV ratio)
    for c in ("N_with_f", "N_with_f_lo", "N_with_f_hi"): g[c] = g[c] * f
    return g
def reach(g, col, thr):
    """max over Lambda of the mass where N crosses thr (log-linear between computed masses). If at some Lambda N >= thr at the last computed mass and the next
    mass is only a bound that is no longer below thr, the crossing lies beyond that mass and is not determined: returned as (-mass, Lambda)."""
    best, beyond = (np.nan, np.nan), None
    for lam, x in g.groupby("lambda_keV"):
        x = x.sort_values("mass_gev"); m = x.mass_gev.values; val = x[col].values; st = x.status_with_f.values; k = x.k.values
        meas = (st == "computed") & (k > 0); okb = (st == "bound") & (val < thr)
        v = np.where(meas | okb, val, np.nan)
        for i in range(len(m) - 1):
            a, b = v[i], v[i + 1]
            if np.isfinite(a) and a >= thr:
                if np.isfinite(b) and b < thr:
                    mm = m[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (m[i + 1] - m[i])
                    if not np.isfinite(best[0]) or mm > best[0]: best = (mm, lam)
                elif st[i + 1] == "bound" and not okb[i + 1]:
                    if beyond is None or m[i] > beyond[0]: beyond = (m[i], lam)
    return (-beyond[0], beyond[1]) if beyond is not None else best
fmt = lambda v: (round(v) if v > 0 else f"> {int(-v)}") if np.isfinite(v) else np.nan
PLOTK = {"colored": ["K1", "K1.5", "K1.8", "K2"], "EW": ["K1", "K0.9", "K1.4", "K2"]}   # K values drawn (4 colours); all K values are in the csv
VARS = {"colored": ["K1", "K1.5", "K1.8", "K2", "annihilation worst"], "EW": ["K1", "K0.8", "K0.9", "K1.2", "K1.4", "K2", "EW LO-ratio trigger", "EW fully LO", "annihilation worst"]}
rows = []
for ch in ("colored", "EW"):
    for sct in ("Z0", "Z1160"):
        base = G[(G.channel == ch) & (G.sct == sct)]
        for var in VARS[ch]:
            if var == "EW fully LO" and sct != "Z0": continue          # D41 was run without SCT z smearing only
            g = scaled(base, ch, var)
            for thr, nm in ((3, "exclusion"), (5, "discovery")):
                c, lo, hi = reach(g, "N_with_f", thr), reach(g, "N_with_f_lo", thr), reach(g, "N_with_f_hi", thr)
                pc = V[ch]["curves"][nm]; rows.append(dict(channel=ch, sct=sct, variant=var, contour=nm, m_max=round(c[0]) if c[0] > 0 else f"> {int(-c[0])} (not determined)", lam_keV=c[1],
                                                           lo=fmt(lo[0]), hi=fmt(hi[0]), paper=round(max(pc["m_GeV"]))))
R = pd.DataFrame(rows); R.to_csv(f"{ROOT}/fig6/F6_reach_sensitivity.csv", index=False); pd.set_option("display.width", 200); print(R.to_string(index=False))
print("EW LO/matched k/n ratio at 800 GeV:", {k: round(v, 3) for k, v in LORAT.items()})
print("EW LO-ratio / matched-count trigger factor per mass:", {k: round(v, 2) for k, v in EWLO.items()})
# ---------------------------------------------------------------- figure (signal without SCT z smearing)
cal = V["colored"]["calibration"]
_al = np.polyfit([np.log10(v) for v, _ in cal["y_log_ticks"]], [p for _, p in cal["y_log_ticks"]], 1); _bl = np.polyfit([v for v, _ in cal["y_lin_ticks"]], [p for _, p in cal["y_lin_ticks"]], 1)
Yd = lambda l: -np.where(np.asarray(l, float) <= 1000, np.polyval(_al, np.log10(np.clip(np.asarray(l, float), 1e-6, None))), np.polyval(_bl, np.asarray(l, float)))
LAMS = sorted(G.lambda_keV.unique())
def surface(g):
    ms = sorted(g.mass_gev.unique()); ys = Yd(np.array(LAMS) * 1e3); Z = np.full((len(ms), len(LAMS)), np.nan)
    for i, m in enumerate(ms):
        for j, lam in enumerate(LAMS):
            r = g[(g.mass_gev == m) & np.isclose(g.lambda_keV, lam)].iloc[0]
            if (r.status_with_f == "bound" and r.N_with_f < 3) or (r.status_with_f == "computed" and r.k > 0): Z[i, j] = np.log10(r.N_with_f)
    f = RegularGridInterpolator((ms, ys), Z, bounds_error=False, fill_value=np.nan)
    mm, yy = np.meshgrid(np.linspace(ms[0], ms[-1], 400), np.linspace(ys[0], ys[-1], 400), indexing="ij"); return mm, yy, f(np.column_stack([mm.ravel(), yy.ravel()])).reshape(mm.shape)
SRC = []
def plot(_):
    fig, axs = plt.subplots(2, 2, figsize=(12.5, 10.5)); cols = [fu.SERIES[0], fu.SERIES[1], fu.SERIES[3], fu.SERIES[6]]
    for i, ch in enumerate(("colored", "EW")):
        base = G[(G.channel == ch) & (G.sct == "Z0")]; x0, x1 = (500, 2500) if ch == "colored" else (0, 1200)
        for j, (thr, nm, ls) in enumerate(((3, "exclusion", "--"), (5, "discovery", "-"))):
            ax = axs[i, j]; P = V[ch]["curves"][nm]; ax.plot(P["m_GeV"], Yd(P["lambda_eV"]), color=fu.INK, ls=ls, lw=1.8, label=f"paper {nm}")
            for k, var in enumerate(PLOTK[ch]):
                mm, yy, zz = surface(scaled(base, ch, var)); ax.contour(mm, yy, zz, levels=[np.log10(thr)], colors=[cols[k]], linestyles=[ls], linewidths=2.2 if var == "K1" else 1.4)
                r = R[(R.channel == ch) & (R.sct == "Z0") & (R.variant == var) & (R.contour == nm)].iloc[0]
                ax.plot([], [], color=cols[k], ls=ls, lw=2.2 if var == "K1" else 1.4,
                        label=f"this work, σ × {var[1:]}{' (N_Q = 2 reading)' if var == 'K2' else ''}: " + (f"{r.m_max} ({r.lo}–{r.hi}) GeV" if str(r.m_max).isdigit() else f"{r.m_max} GeV"))
            if ch == "EW":                                                   # the alternative EW trigger (LO ratio, not stated in the paper)
                mm, yy, zz = surface(scaled(base, ch, "EW LO-ratio trigger")); ax.contour(mm, yy, zz, levels=[np.log10(thr)], colors=[fu.MUTED], linestyles=[":"], linewidths=1.6)
                r = R[(R.channel == ch) & (R.sct == "Z0") & (R.variant == "EW LO-ratio trigger") & (R.contour == nm)].iloc[0]
                ax.plot([], [], color=fu.MUTED, ls=":", lw=1.6, label=f"alternative: LO-ratio trigger, σ × 1: {r.m_max} ({r.lo}–{r.hi}) GeV")
            lmax = max(float(l) for l in base.lambda_keV.unique()) * 1e3
            ax.fill_between([x0, x1], Yd(lmax), Yd(35e3), color="#ededed", lw=0, zorder=0, label=f"Λ > {lmax / 1e3:.0f} keV: not computed")
            ax.set_xlim(x0, x1); ax.set_ylim(Yd(50), Yd(35000)); tv = [100, 1000, 10000, 20000, 30000]; ax.set_yticks(Yd(tv)); ax.set_yticklabels(["10²", "10³", "10000", "20000", "30000"])
            ax.axhline(Yd(1000), color=fu.MUTED, lw=0.6); ax.set_xlabel("m$_Q$ (GeV)"); ax.set_ylabel("Λ (eV)"); ax.legend(fontsize=7.3, loc="upper right", frameon=True, framealpha=0.92)
            ax.set_title(f"{'colored' if ch == 'colored' else 'EW'}: {nm} ({thr} events), signal without SCT z smearing; paper max {int(max(P['m_GeV']))} GeV", fontsize=9.3, loc="left")
    fig.suptitle("Sensitivity of Fig. 6 to the signal normalisation (σ × K; not a fit). Numbers: maximum mass reach, brackets: ±1σ statistics", fontsize=10.5)
    fig.tight_layout(); return fig
fu.figure("F6_kfactor", R, plot,
          "Figure 6 contours (signal without SCT z smearing, charge factor included) with the expected number of events multiplied by a common factor K: colored K = 1.5, 1.8, "
          "EW K = 0.9, 1.4 (0.8 and 1.2 in the csv), and K = 2 for both; EW also the alternative trigger (LO ratio σ(QQ̄ + j, pT > 200)/σ(QQ̄) instead of the matched count, dotted grey) (the N_Q = 2 of the paper's panel titles read as a factor 2 on σ; not applied in the main figure). K = 1: our LO "
          "cross sections. This is a sensitivity study, not a fit. Grid N from fig6/F6_N_grid.csv; no new simulation.", [f"{ROOT}/fig6/F6_N_grid.csv"], "all grid points", os.path.abspath(__file__))
