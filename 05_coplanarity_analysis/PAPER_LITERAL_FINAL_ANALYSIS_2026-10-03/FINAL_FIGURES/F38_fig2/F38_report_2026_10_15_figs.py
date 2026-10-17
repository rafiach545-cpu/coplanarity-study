#!/usr/bin/env python3
"""Figures for the 2026-10-15 report (data from R_data_2026_10_15; simple binomial sigma, no Wilson intervals).
F38_table_I : eps_trig, eps_fid, eps_reco (SCT z none / 580 um / 1.16 mm) of the production samples, EW LO sample B (D41), paper.
F38_lambda  : eps_reco vs Lambda: production (SCT z none, 1.16 mm; first crossing), EW LO sample B (D41, SCT z none), paper.
F38_fig2    : Fig. 2: paper | constructed event (paper kinematics, charges +-2/3) | simulated COL2000 key 8; |L| and d vs r; closest approaches marked."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu, R_data_2026_10_15 as R
S_ = os.path.abspath(__file__); T = R.T
C = R.production(); LT = R.lo_trigger(); D = R.d41()
rows = []
for s, v in R.SAM.items():
    c = C[s]; rows.append(dict(sample=s, item="ε_trig", setting="production (MLM + shower)", k=c["trig"], n=c["matched"], paper=v["paper"]["trig"]))
    rows.append(dict(sample=s, item="ε_fid", setting="production", k=c["fid"], n=c["charged"], paper=v["paper"]["fid"]))
    for z, lab in (("Z0", "SCT z none"), ("Z580", "SCT z 580 µm"), ("Z1160", "SCT z 1.16 mm")):
        rows.append(dict(sample=s, item="ε_reco", setting=lab, k=c[("FIRST", z)]["sr"], n=c["fid"], paper=v["paper"]["reco"]))
r = LT[("3.7.3", "EW")]; rows.append(dict(sample="EW2000", item="ε_trig", setting="LO ratio σ(QQj, pT>200)/σ(QQ)", k=np.nan, n=np.nan, eps=r["r"], sig=r["dr"], paper=0.10))
r = LT[("3.7.3", "COL")]; rows.append(dict(sample="COL2000", item="ε_trig", setting="LO ratio σ(QQj, pT>200)/σ(QQ)", k=np.nan, n=np.nan, eps=r["r"], sig=r["dr"], paper=0.24))
if D:
    rows.append(dict(sample="EW2000", item="ε_fid", setting=f"LO sample B ({D['n']} events)", k=D[4]["fid"], n=D["n"], paper=0.28))
    rows.append(dict(sample="EW2000", item="ε_reco", setting=f"LO sample B, SCT z none", k=D[4]["sr"], n=D[4]["fid"], paper=0.72))
src = pd.DataFrame(rows)
m = src.k.notna(); src.loc[m, "eps"] = src.k[m] / src.n[m]; src.loc[m, "sig"] = np.sqrt(src.eps[m] * (1 - src.eps[m]) / src.n[m])
def p1(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for ax, s, t in zip(axs, ("COL2000", "EW2000"), ("colored 1.8 TeV, Λ = 2 keV", "EW 800 GeV, Λ = 4 keV")):
        x = d[d["sample"] == s].reset_index(drop=True)
        for i, r in x.iterrows():
            lo = "LO" in r.setting; col = fu.SERIES[2] if lo else (fu.SERIES[0] if "1.16" in r.setting else fu.SERIES[3] if "580" in r.setting else fu.SERIES[1] if "none" in r.setting else fu.INK2)
            ax.errorbar(i, r.eps, yerr=r.sig, fmt="s" if lo else "o", color=col, ms=7, capsize=4, lw=1.6)
            ax.hlines(r.paper, i - 0.32, i + 0.32, color=fu.INK, lw=2, linestyles="--")
            ax.annotate(f"{int(r.k)}/{int(r.n)}" if r.k == r.k else f"{r.eps:.3f}", (i, -0.09), ha="center", fontsize=6.5, color=fu.INK2)
        ax.set_xticks(range(len(x))); ax.set_xticklabels([f"{a}\n{b}" for a, b in zip(x.item, x.setting)], fontsize=6.3, rotation=30, ha="right")
        ax.set_ylim(-0.13, 1.0); ax.set_title(t, fontsize=9)
    axs[0].set_ylabel("efficiency ± simple binomial σ"); axs[0].plot([], [], "k--", label="paper"); axs[0].legend(fontsize=7, loc="upper right")
    fig.tight_layout(); return fig
fu.figure("F38_table_I", src, p1, "Table I efficiencies with simple binomial uncertainties σ = √(ε(1−ε)/n): circles = production samples (2000 events generated, "
          "MLM-matched + Pythia 8), squares = EW LO sample B (D41) and LO cross-section ratios, dashes = paper. Numbers below the points: k/n.",
          [f"{T}/all_crossings_per_event.csv", f"{R.IN}/mg5_373_run.log", f"{R.LOG}/D41_mg5_373_lo_events.jsonl"], "2000-event production samples; D41 contiguous finished events", S_)
LS = R.lambda_scan(); rows = []
for _, r in LS[LS["mode"] == "FIRST"].iterrows():
    rows.append(dict(sample=r["sample"], lam=r.lambda_keV, setting=("production, SCT z 1.16 mm" if r.sct == "Z1160" else "production, SCT z none"), k=r.k_ge2, n=r.n_fid, paper=r.paper_reco))
if D:
    for lam in (1, 2, 3, 4, 5): rows.append(dict(sample="EW2000", lam=lam, setting=f"LO sample B ({D['n']} events), SCT z none", k=D[lam]["sr"], n=D[lam]["fid"], paper=R.PAPER_L["EW2000"][lam]))
L = pd.DataFrame(rows); L["eps"] = L.k / L.n; L["sig"] = np.sqrt(L.eps * (1 - L.eps) / L.n)
def p2(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
    for ax, s, t in zip(axs, ("COL2000", "EW2000"), ("colored 1.8 TeV", "EW 800 GeV")):
        x = d[d["sample"] == s]; p = x.drop_duplicates("lam").sort_values("lam"); ax.plot(p.lam, p.paper, "s-", color=fu.INK, ms=6, lw=1.2, label="paper (Table I)")
        for st, c, mk, off in (("production, SCT z none", fu.SERIES[1], "o", -0.08), ("production, SCT z 1.16 mm", fu.SERIES[0], "o", 0.0)):
            y = x[x.setting == st].sort_values("lam"); ax.errorbar(y.lam + off, y.eps, yerr=y.sig, fmt=mk + "-", color=c, ms=6, capsize=3, lw=1.4, label=st)
        y = x[x.setting.str.startswith("LO sample B")].sort_values("lam")
        if len(y): ax.errorbar(y.lam + 0.08, y.eps, yerr=y.sig, fmt="s--", color=fu.SERIES[2], ms=6, capsize=3, lw=1.4, label=y.setting.iloc[0])
        ax.set_xlabel("Λ (keV)"); ax.set_title(t, fontsize=9); ax.set_xticks(sorted(p.lam)); ax.set_ylim(0, 1)
    axs[0].set_ylabel("ε_reco ± simple binomial σ"); h, l = axs[1].get_legend_handles_labels(); fig.legend(h, l, fontsize=7, loc="lower center", ncol=4, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1)); return fig
fu.figure("F38_lambda", L, p2, "ε_reco vs the string tension Λ (the Λ column of Table I), first crossing, with simple binomial σ. Orange: production, no SCT z smearing; "
          "blue: production, SCT z 1.16 mm; green squares: EW LO sample B (D41), no SCT z smearing; black: paper.",
          [f"{T}/lambda_scan_summary.csv", f"{T}/lambda_scan_z1160_summary.csv", f"{R.LOG}/D41_mg5_373_lo_events.jsonl"], "2000-event samples; D41", S_)
S, pl, pdd, ours = R.fig2(); rows = []
rows += [dict(panel="paper", curve="L", r_cm=a, y=b) for a, b in zip(pl.r_cm, pl.L_1e12_hbar)] + [dict(panel="paper", curve="d", r_cm=a, y=b) for a, b in zip(pdd.r_cm, pdd.d_cm)]
for k, x in ours.items():
    x = x.iloc[::4]; rows += [dict(panel=k, curve="L", r_cm=a, y=b) for a, b in zip(x.r_cm, x.L_1e12_hbar)] + [dict(panel=k, curve="d", r_cm=a, y=b) for a, b in zip(x.r_cm, x.d_cm)]
for k in ("paper", "constructed", "key8"): rows += [dict(panel=k, curve="approach", r_cm=a, y=b) for a, b in zip(S[k]["rapp"], S[k]["Lapp"])]
F2 = pd.DataFrame(rows)
TIT = {"paper": "PAPER (Fig. 2, from its vector figure)", "constructed": "THIS WORK: paper's kinematics\n(v* = 0.556, β_cm = 0.0975, charges ±2/3)", "key8": "THIS WORK: simulated event COL2000 key 8\n(charges ±1)"}
def p3(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 3, figsize=(13, 5.6), sharex=True)
    for j, k in enumerate(("paper", "constructed", "key8")):
        x = d[d.panel == k]; L_ = x[x.curve == "L"].sort_values("r_cm"); d_ = x[x.curve == "d"].sort_values("r_cm"); a = x[x.curve == "approach"]
        ax[0, j].plot(L_.r_cm, L_.y, color=fu.SERIES[0], lw=1.8); ax[1, j].plot(d_.r_cm, d_.y, color=fu.SERIES[1], lw=1.6)
        for r_ in a.r_cm: ax[0, j].axvline(r_, color="#c9c8c3", lw=0.8, zorder=0); ax[1, j].axvline(r_, color="#c9c8c3", lw=0.8, zorder=0)
        ax[0, j].plot(a.r_cm, a.y, "o", color=fu.SERIES[0], mec="white", ms=6)
        for r_, y_ in zip(a.r_cm, a.y): ax[0, j].annotate(f"{y_:.2f}", (r_, y_), xytext=(3, 5), textcoords="offset points", fontsize=7)
        ax[0, j].set_title(TIT[k], fontsize=8.5, loc="left"); ax[0, j].set_ylim(0, 1.0); ax[1, j].set_ylim(0, 4.5); ax[1, j].set_xlim(0, 5); ax[1, j].set_xlabel("r (cm)")
    ax[0, 0].set_ylabel("|L| (10¹² ħ)"); ax[1, 0].set_ylabel("d (cm)"); fig.tight_layout(); return fig
fu.figure("F38_fig2", F2, p3, "Fig. 2: |L| (top) and quirk separation d (bottom) vs the transverse radius r of the centre of mass, m_Q = 1.8 TeV, Λ = 2 keV, B = 2 T. "
          "Grey lines: closest approaches (minima of d); numbers: |L| there. Our curves: initial CM frame, equal CM time, 3000 RK4 steps per period.",
          [f"{T}/fig2_final"], "paper event; constructed event; COL2000 key 8", S_)
print(src.round(3).to_string()); print(L.round(3).to_string())
