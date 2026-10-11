#!/usr/bin/env python3
"""Meeting figures (2026-10-05), current primary setup only: Ref. [27] barrel lengths, no SCT z smearing for the signal,
45 mm beam spot as one common shift with the fit from the vertex. Background: conversion + mu=50 pile-up with the cited
detector model [34] (bremsstrahlung, Ref. [27] X0), Ref. [27] lengths, fit from the vertex.
G1: the six Table I efficiencies, each sample separately, Wilson 95%, paper line.
G2: conversion + pile-up events in the signal region, SCT z 580 um vs none, with the paper's level.
G3: one SCT z resolution for both: reconstruction efficiency (left) and conversion background (right) vs SCT z."""
import os, sys, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
from stats_utils import row
T = f"{HERE}/../tables"; L = f"{HERE}/../logs"; S = os.path.abspath(__file__)
V = pd.read_csv(f"{T}/v6_primary_table_I.csv"); SAMPLES = ["COL1000", "COL2000", "EW1000", "EW2000"]
TZ = {"Z0": "no SCT z smearing (UNDOCUMENTED in text; best-supported reading for the signal)", "Z580": "SCT z 580 um (1x Ref.[27], sensitivity)", "Z1160": "SCT z 1160 um (2x580, INFERRED)"}
PAPER = {"COL": {"trigger": .24, "fiducial": .28, "reconstruction": .35}, "EW": {"trigger": .10, "fiducial": .28, "reconstruction": .72}}
TRU = lambda s: s.astype(str) == "True"
def ovk(d_):
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L}/{d_}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139
    return int((TRU(o.plane) & TRU(o.mult) & TRU(o.final)).sum())

# G1
g1 = []
for s in SAMPLES:
    for q, t in [("trigger", "—"), ("fiducial", "—"), ("reconstruction", TZ["Z0"])]:
        r = V[(V["sample"] == s) & (V.quantity == q) & (V.treatment == t)].iloc[0]
        g1.append(dict(sample=s, quantity=q, k=int(r.k), n=int(r.n), eff=r.frac, w95_lo=r.wilson95_lo, w95_hi=r.wilson95_hi, paper=PAPER["EW" if s.startswith("EW") else "COL"][q]))
G1 = pd.DataFrame(g1)
def p1(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
    for ax, q, ttl in zip(axes, ["trigger", "fiducial", "reconstruction"], ["ε_trig", "ε_fid", "ε_reco"]):
        x = d[d.quantity == q].set_index("sample").loc[SAMPLES].reset_index()
        for i, r in x.iterrows():
            col = fu.SERIES[0] if r["sample"].startswith("COL") else fu.SERIES[1]
            ax.plot([i, i], [r.w95_lo, r.w95_hi], color=col, lw=2.2, solid_capstyle="round")
            ax.plot(i, r.eff, "o" if r["sample"].startswith("COL") else "s", color=col, ms=8, mec=fu.SURFACE, mew=1.4)
            ax.plot([i - .35, i + .35], [r.paper] * 2, color=fu.INK, ls="--", lw=1.5)
            ax.annotate(f"{r.k}/{r.n}", (i, r.w95_hi), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=7.5, color=fu.INK2)
        ax.set_xticks(range(4), SAMPLES, fontsize=8); ax.set_title(ttl, fontsize=11); ax.set_ylim(0, 1.05 if q == "reconstruction" else 0.55)
    from matplotlib.lines import Line2D
    axes[0].set_ylabel("efficiency (Wilson 95%)")
    axes[2].legend([Line2D([], [], color=fu.SERIES[0], marker="o"), Line2D([], [], color=fu.SERIES[1], marker="s"), Line2D([], [], color=fu.INK, ls="--")],
                   ["colored", "EW", "paper"], fontsize=7.5, loc="lower right")
    fig.tight_layout(); return fig
fu.figure("G1_table_I_current", G1, p1, "Table I efficiencies, current setup (Ref. [27] barrel lengths; no SCT z smearing for ε_reco), each sample separately. "
          "Bars: Wilson 95%; dashed: paper.", [f"{T}/v6_primary_table_I.csv"], "current primary", S)

# G2
k0, k5 = ovk("P10_chunks_B_Z0_REF34"), ovk("P10_chunks_B_Z580_REF34")
g2 = []
for lab, k in [("SCT z 580 µm", k5), ("no SCT z smearing", k0)]:
    r = row(k, 9139); g2.append(dict(setup=lab, k=k, n=9139, frac=r["frac"], w95_lo=r["wilson95_lo"], w95_hi=r["wilson95_hi"], ul95=r["cp95_upper_one_sided"],
                                     events_300_paper_sigma=1000 * 0.01 * (r["frac"] if k else r["cp95_upper_one_sided"]) * 300, events_300_lo=1000 * 0.01 * r["wilson95_lo"] * 300,
                                     events_300_hi=1000 * 0.01 * r["wilson95_hi"] * 300))
G2 = pd.DataFrame(g2); PAPER_EV = 0.0024 * 300
def p2(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    for i, r in d.reset_index(drop=True).iterrows():
        if r.k > 0:
            ax.plot([r.events_300_lo, r.events_300_hi], [i, i], color=fu.SERIES[1], lw=2.4); ax.plot(r.events_300_paper_sigma, i, "s", color=fu.SERIES[1], ms=9)
            ax.annotate(f"{r.k}/9139", (r.events_300_hi, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=fu.INK2)
        else:
            ax.plot([0.01, r.events_300_paper_sigma], [i, i], color=fu.SERIES[0], lw=1.2, ls=":"); ax.plot(r.events_300_paper_sigma, i, "<", color=fu.SERIES[0], ms=9)
            ax.annotate(f"0/9139 (95% upper limit)", (r.events_300_paper_sigma, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=fu.INK2)
    ax.axvline(PAPER_EV, color=fu.INK, ls="--", lw=1.4); ax.text(PAPER_EV * 1.1, 1.35, "paper ≈ 0.7", fontsize=8)
    ax.set_yticks(range(len(d)), d.setup, fontsize=9); ax.set_ylim(-0.6, 1.6); ax.set_xscale("log"); ax.set_xlim(0.1, 200)
    ax.set_xlabel("conversion + pile-up events in the signal region at 300 fb⁻¹ (σ = 1 pb, 1% conversion)"); fig.tight_layout(); return fig
fu.figure("G2_conversion_background", G2, p2, "Converted-photon + μ = 50 pile-up background in the signal region (9139 photons, cited detector model [34], Ref. [27] lengths), "
          "scaled to 300 fb⁻¹ with the paper's σ ≈ 1 pb and 1% conversion probability. Square + bar: Wilson 95%; arrow: one-sided 95% upper limit for 0 events. "
          "Dashed: the paper's Fig. 5 level (≈ 0.0024 fb).", [f"{L}/P10_chunks_B_Z0_REF34", f"{L}/P10_chunks_B_Z580_REF34"], "cited model", S)

# G3
g3 = []
for s in SAMPLES:
    for z in ["Z0", "Z580", "Z1160"]:
        r = V[(V["sample"] == s) & (V.quantity == "reconstruction") & (V.treatment == TZ[z])].iloc[0]
        g3.append(dict(panel="signal", sample=s, sct_z=z, k=int(r.k), n=int(r.n), eff=r.frac, w95_lo=r.wilson95_lo, w95_hi=r.wilson95_hi))
for z, k in [("Z0", k0), ("Z580", k5)]:
    r = row(k, 9139); g3.append(dict(panel="background", sample="conversion + pile-up", sct_z=z, k=k, n=9139, eff=r["frac"], w95_lo=r["wilson95_lo"], w95_hi=r["wilson95_hi"]))
G3 = pd.DataFrame(g3)
def p3(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6)); Z = ["Z0", "Z580", "Z1160"]; XL = ["none", "580 µm", "1160 µm"]
    ax = axes[0]; sg = d[d.panel == "signal"]
    for j, s in enumerate(SAMPLES):
        x = sg[sg["sample"] == s].set_index("sct_z").loc[Z]; xs = np.arange(3) + (j - 1.5) * 0.1
        ax.errorbar(xs, x.eff, yerr=[x.eff - x.w95_lo, x.w95_hi - x.eff], fmt=fu.MARKERS[j], color=fu.SERIES[j], ms=6, label=s, capsize=0)
    ax.axhline(0.72, color=fu.INK, ls="--", lw=1); ax.axhline(0.35, color=fu.INK2, ls=":", lw=1.2)
    ax.text(2.45, 0.735, "paper EW", fontsize=7, ha="right"); ax.text(2.45, 0.365, "paper colored", fontsize=7, ha="right", color=fu.INK2)
    ax.set_xticks(range(3), XL); ax.set_xlabel("SCT z smearing"); ax.set_ylabel("ε_reco (Wilson 95%)"); ax.set_ylim(0, 1.05); ax.legend(fontsize=7, loc="upper right"); ax.set_title("signal: needs no smearing", fontsize=10)
    bx = axes[1]; bg = d[d.panel == "background"].set_index("sct_z")
    for i, z in enumerate(["Z0", "Z580"]):
        r = bg.loc[z]; ev = lambda f: 1000 * 0.01 * f * 300
        if r.k > 0:
            bx.plot([i, i], [ev(r.w95_lo), ev(r.w95_hi)], color=fu.SERIES[1], lw=2.4); bx.plot(i, ev(r.eff), "s", color=fu.SERIES[1], ms=9)
            bx.annotate(f"{int(r.k)}/9139", (i, ev(r.w95_hi)), xytext=(6, 0), textcoords="offset points", fontsize=8, color=fu.INK2)
        else:
            from scipy import stats
            u = ev(stats.beta.ppf(0.95, 1, 9139)); bx.plot([i, i], [0.1, u], color=fu.SERIES[0], lw=1.2, ls=":"); bx.plot(i, u, "v", color=fu.SERIES[0], ms=9)
            bx.annotate("0/9139 (95% UL)", (i, u), xytext=(6, 0), textcoords="offset points", fontsize=8, color=fu.INK2)
    bx.axhline(0.72, color=fu.INK, ls="--", lw=1.2); bx.text(-0.45, 0.8, "paper ≈ 0.7", fontsize=8)
    bx.set_yscale("log"); bx.set_ylim(0.1, 200); bx.set_xlim(-0.5, 1.8); bx.set_xticks([0, 1], ["none", "580 µm"]); bx.set_xlabel("SCT z smearing")
    bx.set_ylabel("conversion events at 300 fb⁻¹"); bx.set_title("background: needs smearing", fontsize=10)
    fig.tight_layout(); return fig
fu.figure("G3_one_resolution_for_both", G3, p3, "One SCT z resolution cannot give both: the signal efficiency matches the paper only without SCT z smearing (left); the conversion "
          "background matches the paper only with 580 µm (right). Left: Ref. [27] lengths, Wilson 95%. Right: conversion + μ = 50 pile-up, cited detector model, "
          "300 fb⁻¹ with the paper's σ.", [f"{T}/v6_primary_table_I.csv", f"{L}/P10_chunks_B_Z0_REF34", f"{L}/P10_chunks_B_Z580_REF34"], "current primary", S)
print(G1.round(3).to_string()); print(G2.round(4).to_string())
