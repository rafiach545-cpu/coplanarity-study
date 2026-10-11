#!/usr/bin/env python3
"""Report graphs for Table I (2000-event samples only, one hit per quirk per layer, Ref. [27] lengths).
F31_table_I : eps_trig, eps_fid, eps_reco with Wilson 95% intervals vs the paper; eps_reco for SCT z 1.16 mm and no smearing.
F31_lambda  : eps_reco vs Lambda (paper Table I column) for SCT z 1.16 mm and no smearing; all-crossings (>= 2 hits) as open markers."""
import os, sys, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__); TR = lambda s: s.astype(str) == "True"
W = lambda k, n: stats.binomtest(int(k), int(n)).proportion_ci(0.95, "wilson")
A = pd.read_csv(f"{T}/all_crossings_per_event.csv")
TRIG = {"COL2000": (207, 873), "EW2000": (186, 1045)}; PAP = {"COL2000": dict(trig=.24, fid=.28, reco=.35), "EW2000": dict(trig=.10, fid=.28, reco=.72)}
rows = []
for s in ("COL2000", "EW2000"):
    rows.append(dict(sample=s, quantity="ε_trig", setting="", k=TRIG[s][0], n=TRIG[s][1], paper=PAP[s]["trig"]))
    f = A[(A["sample"] == s) & (A["mode"] == "FIRST") & (A.sct == "Z0")]; NFD = {"COL2000": 68, "EW2000": 186}   # triggered (colored: both charged); 3 events with a
    rows.append(dict(sample=s, quantity="ε_fid", setting="", k=int(TR(f.fid).sum()), n=NFD[s], paper=PAP[s]["fid"]))  # technical integration failure count as not fiducial
    for sct, lab in (("Z1160", "SCT z 1.16 mm"), ("Z0", "no SCT z smearing")):
        x = A[(A["sample"] == s) & (A["mode"] == "FIRST") & (A.sct == sct) & TR(A.fid)]
        rows.append(dict(sample=s, quantity="ε_reco", setting=lab, k=int(TR(x.final).sum()), n=len(x), paper=PAP[s]["reco"]))
src = pd.DataFrame(rows); src[["lo", "hi"]] = [W(k, n) for k, n in zip(src.k, src.n)]; src["eps"] = src.k / src.n
def p1(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
    for ax, s, t in zip(axs, ("COL2000", "EW2000"), ("colored 1.8 TeV, Λ = 2 keV", "EW 800 GeV, Λ = 4 keV")):
        x = d[d["sample"] == s].reset_index(drop=True); x["setting"] = x.setting.fillna(""); lab = [q if not st else f"{q}\n{st}" for q, st in zip(x.quantity, x.setting)]
        for i, r in x.iterrows():
            c = fu.SERIES[0] if r.setting == "SCT z 1.16 mm" else (fu.SERIES[1] if r.setting else fu.INK2)
            ax.errorbar(i, r.eps, yerr=[[r.eps - r.lo], [r.hi - r.eps]], fmt="o", color=c, ms=7, capsize=4, lw=1.6)
            ax.hlines(r.paper, i - 0.3, i + 0.3, color=fu.INK, lw=2, linestyles="--"); ax.annotate(f"{r.k}/{r.n}", (i, -0.08), ha="center", fontsize=7, color=fu.INK2)
        ax.set_xticks(range(len(x))); ax.set_xticklabels(lab, fontsize=7.5); ax.set_ylim(-0.12, 1.0); ax.set_title(t, fontsize=9)
    axs[0].set_ylabel("efficiency (Wilson 95%)"); axs[0].plot([], [], "k--", label="paper"); axs[0].legend(fontsize=7, loc="upper right")
    fig.tight_layout(); return fig
fu.figure("F31_table_I", src, p1, "Table I efficiencies, 2000-event samples: points = this work with Wilson 95% intervals, dashes = paper. ε_reco for SCT z 1.16 mm (blue) and "
          "without SCT z smearing (orange). Numbers below the points: k/n.", [f"{T}/all_crossings_per_event.csv"], "2000-event samples", S)
L0 = pd.read_csv(f"{T}/lambda_scan_summary.csv"); L1 = pd.read_csv(f"{T}/lambda_scan_z1160_summary.csv")
L = pd.concat([L0[L0["sample"].isin(["COL2000", "EW2000"]) & (L0.sct == "Z0")], L1]); L["eps"] = L.k_ge2 / L.n_fid; L[["lo", "hi"]] = [W(k, n) for k, n in zip(L.k_ge2, L.n_fid)]
def p2(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.7), sharey=True)
    for ax, s, t in zip(axs, ("COL2000", "EW2000"), ("colored 1.8 TeV", "EW 800 GeV")):
        x = d[d["sample"] == s]; p = x.drop_duplicates("lambda_keV").sort_values("lambda_keV")
        ax.plot(p.lambda_keV, p.paper_reco, "s-", color=fu.INK, ms=6, lw=1.2, label="paper (Table I)")
        for sct, c, lab, off in (("Z1160", fu.SERIES[0], "SCT z 1.16 mm", -0.07), ("Z0", fu.SERIES[1], "no SCT z smearing", 0.07)):
            y = x[(x.sct == sct) & (x["mode"] == "FIRST")].sort_values("lambda_keV")
            ax.errorbar(y.lambda_keV + off, y.eps, yerr=[y.eps - y.lo, y.hi - y.eps], fmt="o-", color=c, ms=6, capsize=3, lw=1.4, label=f"{lab}, one hit per layer")
            a = x[(x.sct == sct) & (x["mode"] == "ALL")].sort_values("lambda_keV")
            ax.plot(a.lambda_keV + off, a.eps, "o", mfc="none", color=c, ms=6, label=f"{lab}, every crossing (≥ 2 hits)")
        ax.set_xlabel("Λ (keV)"); ax.set_title(t, fontsize=9); ax.set_xticks(sorted(p.lambda_keV)); ax.set_ylim(0, 1)
    axs[0].set_ylabel("ε_reco (Wilson 95%)"); h, l = axs[1].get_legend_handles_labels(); fig.legend(h, l, fontsize=7, loc="lower center", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1)); return fig
fu.figure("F31_lambda", L, p2, "ε_reco vs the string tension Λ, the Λ column of the paper's Table I (2000-event samples). Filled: one hit per quirk per layer, with Wilson 95% intervals; "
          "open: every layer crossing within 25 ns, ≥ 2 hits per layer. Blue: SCT z 1.16 mm; orange: no SCT z smearing; black squares: paper.",
          [f"{T}/lambda_scan_summary.csv", f"{T}/lambda_scan_z1160_summary.csv"], "2000-event samples", S)
print(src.round(3).to_string()); print(L[["sample", "lambda_keV", "mode", "sct", "k_ge2", "n_fid", "eps", "paper_reco"]].sort_values(["sample", "sct", "mode", "lambda_keV"]).round(3).to_string())
