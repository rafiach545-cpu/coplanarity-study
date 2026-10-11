#!/usr/bin/env python3
"""F09v3: EW trigger efficiency under generator variations.
(a) EW vs colored eps_trig for every configuration run on BOTH benchmarks (one-at-a-time screen + pre-registered combinations), labelled.
(b) EW/colored ratio per configuration (paper 0.42).
(c) all EW values incl. the MG5/Pythia version pilot (EW only); marker = kind, filled/open = sample size.
Sources: forensics trigger_screen_results.csv, followup version_pilot_variants.csv, tables/trigger_combinations.csv."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
B = f"{HERE}/../.."; T = f"{HERE}/../tables"
SCR = f"{B}/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/trigger_screen_results.csv"
PIL = f"{B}/EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/tables/version_pilot_variants.csv"; CMB = f"{T}/trigger_combinations.csv"
s = pd.read_csv(SCR).rename(columns={"bench": "bench"}); s["kind"] = np.where(s.config.str.startswith("B0"), "baseline", np.where(s.config.str.startswith("D"), "one-at-a-time (contradicts paper)", "one-at-a-time"))
c = pd.read_csv(CMB).rename(columns={}); c["kind"] = np.where(c.config.isin(["C5", "C6"]), "combination (contradicts paper)", "combination")
cols = ["config", "bench", "kind", "N_matched", "N_trigger", "eps_trig", "w95_lo", "w95_hi"]
both = pd.concat([s[cols], c[cols]])
w = both.pivot_table(index=["config", "kind"], columns="bench", values=["eps_trig", "w95_lo", "w95_hi", "N_matched"], aggfunc="first")
w.columns = [f"{a}_{b}" for a, b in w.columns]; w = w.reset_index(); w["ratio"] = w.eps_trig_EW / w.eps_trig_COL; w["panel"] = "both"
p = pd.read_csv(PIL); p = p.assign(config=p.variant.str.replace("SHOWER_", "").str.replace("_mg5_", " MG").str.replace("_py", " Py"), kind="version pilot (EW only)",
                                   eps_trig_EW=p.trig_over_matched, w95_lo_EW=p.wilson95_lo, w95_hi_EW=p.wilson95_hi, N_matched_EW=p.N_matched, panel="EW only")
src = pd.concat([w, p[["config", "kind", "eps_trig_EW", "w95_lo_EW", "w95_hi_EW", "N_matched_EW", "panel"]]], ignore_index=True)
src["n_generated"] = src.config.map(lambda x: 500 if "PILOT500" in x else (1000 if "EW1000" in x else 2000))
STY = {"baseline": (fu.SERIES[1], "s"), "one-at-a-time": (fu.SERIES[0], "o"), "one-at-a-time (contradicts paper)": (fu.MUTED, "o"),
       "combination": (fu.SERIES[2], "D"), "combination (contradicts paper)": (fu.MUTED, "D"), "version pilot (EW only)": (fu.SERIES[4], "^")}
def short(x): return x.split("_")[0]

def plot(d):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12.5, 8.6)); gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 1])
    ax = fig.add_subplot(gs[0, 0]); bx = fig.add_subplot(gs[1, 0]); cx = fig.add_subplot(gs[:, 1])
    b = d[d.panel == "both"]
    for _, r in b.iterrows():
        col, mk = STY[r.kind]
        ax.errorbar(r.eps_trig_COL, r.eps_trig_EW, xerr=[[r.eps_trig_COL - r.w95_lo_COL], [r.w95_hi_COL - r.eps_trig_COL]], yerr=[[r.eps_trig_EW - r.w95_lo_EW], [r.w95_hi_EW - r.eps_trig_EW]],
                    fmt=mk, color=col, ms=6, lw=0.8, alpha=0.9, label=r.kind)
        ax.annotate(short(r.config), (r.eps_trig_COL, r.eps_trig_EW), xytext=(4, 3), textcoords="offset points", fontsize=6.5, color=fu.INK2)
    ax.plot(0.24, 0.10, "*", ms=16, color=fu.INK, label="paper (0.24, 0.10)"); x = np.linspace(0.1, 0.35, 5); ax.plot(x, 0.42 * x, ":", color=fu.MUTED, lw=1, label="paper ratio 0.42")
    h, l = ax.get_legend_handles_labels(); u = dict(zip(l, h)); ax.legend(u.values(), u.keys(), fontsize=6.5, loc="lower left")
    ax.set_xlim(0.12, 0.32); ax.set_ylim(0.07, 0.22); ax.set_xlabel("colored ε_trig (Wilson 95%)"); ax.set_ylabel("EW ε_trig (Wilson 95%)"); ax.set_title("(a) both benchmarks, every configuration", fontsize=9)
    bb = b.sort_values("ratio").reset_index(drop=True)
    for i, r in bb.iterrows():
        col, mk = STY[r.kind]; bx.plot(i, r.ratio, mk, color=col, ms=6)
    bx.axhline(0.42, color=fu.INK, ls="--", lw=1.2); bx.text(0.2, 0.44, "paper 0.10 / 0.24 = 0.42", fontsize=7)
    bx.set_xticks(range(len(bb)), [short(c) for c in bb.config], fontsize=6.5, rotation=90); bx.set_ylim(0.3, 1.0); bx.set_ylabel("EW / colored ε_trig"); bx.set_title("(b) the ratio stays at 0.6–0.85 in every configuration", fontsize=9)
    e = d.sort_values("eps_trig_EW").reset_index(drop=True)
    for i, r in e.iterrows():
        col, mk = STY[r.kind]; filled = r.n_generated == 2000
        cx.plot([r.w95_lo_EW, r.w95_hi_EW], [i, i], color=col, lw=1.2)
        cx.plot(r.eps_trig_EW, i, mk, color=col, ms=6 if filled else 7, mfc=col if filled else "white", mew=1.3)
    cx.axvline(0.10, color=fu.INK, ls="--", lw=1.2); cx.text(0.101, len(e) - 0.5, "paper 0.10", fontsize=7)
    cx.set_yticks(range(len(e)), e.config, fontsize=5.6); cx.set_xlabel("EW ε_trig (Wilson 95%)"); cx.set_title("(c) all EW values; open marker = 500 or 1000 generated events", fontsize=9)
    fig.tight_layout(); return fig

fu.figure("F09v3_trigger_variations", src, plot,
          "EW trigger efficiency under generator variations. (a) EW vs colored ε_trig for every configuration run on both benchmarks: the one-at-a-time screen "
          "(blue; grey = settings that contradict the paper's 'up to 1 jet, matched'), the frozen baseline B0 (orange square) and the pre-registered combinations "
          "C1–C6 (green diamonds; grey = contradicts the paper). Bars: Wilson 95%. Star: paper. (b) EW/colored ratio per configuration vs the paper's 0.42. "
          "(c) All EW values including the MG5/Pythia version pilot (pink triangles, EW only); open markers = 500- or 1000-event samples.",
          [SCR, PIL, CMB], "all configurations", os.path.abspath(__file__))
print(src.groupby("kind").size())
