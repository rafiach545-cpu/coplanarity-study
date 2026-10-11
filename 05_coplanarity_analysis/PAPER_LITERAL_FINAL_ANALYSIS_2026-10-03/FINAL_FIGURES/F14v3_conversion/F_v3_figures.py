#!/usr/bin/env python3
"""v3 report figures (primary configuration only: |eta|<1.8, common 45 mm beam-spot shift, fit from the vertex).
  F08v3 : reconstruction efficiency vs SCT z treatment (1.16 mm / 0.58 mm / none), each sample, Wilson 95%.
  F13v3 : pile-up per-event rates (|eta|<1.8 + pixel merging) vs the paper's approximate rates.
  F14v3 : converted-photon background cutflow (conversion only x 3 SCT z treatments; conversion + pile-up at 1.16 mm)."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__); SAMPLES = ["COL1000", "COL2000", "EW1000", "EW2000"]
which = sys.argv[1:] or ["F08v3", "F13v3", "F14v3"]
if "F08v3" in which:
    M = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv"); E = M[(M.acceptance == "A") & (M.beamspot == "CV")]
    def f08(d):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7.6, 3.8)); Z = ["Z1160", "Z580", "Z0"]
        for j, s in enumerate(SAMPLES):
            x = d[d["sample"] == s].set_index("sct_z").loc[Z]; xs = np.arange(3) + (j - 1.5) * 0.12
            ax.errorbar(xs, x.eps_reco, yerr=[x.eps_reco - x.reco_w95_lo, x.reco_w95_hi - x.eps_reco], fmt=fu.MARKERS[j], color=fu.SERIES[j], ms=6, label=f"{s} (n = {int(x.fiducial.iloc[0])})")
        ax.axhline(0.72, color=fu.INK, ls="--", lw=1); ax.axhline(0.35, color=fu.INK2, ls=":", lw=1.2)
        ax.text(2.45, 0.735, "paper EW 0.72", fontsize=7, ha="right"); ax.text(2.45, 0.365, "paper colored 0.35", fontsize=7, ha="right", color=fu.INK2)
        ax.set_xticks(range(3), ["1.16 mm\n(2 × 0.58 mm, our reading)", "0.58 mm\n(value in Ref. [27])", "none\n(no source)"], fontsize=8)
        ax.set_xlabel("SCT smearing along the beam (z)"); ax.set_ylabel("ε_reco (Wilson 95%)"); ax.set_ylim(0, 1.05); ax.legend(fontsize=7, loc="upper left"); fig.tight_layout(); return fig
    fu.figure("F08v3_reco_vs_sct_z", E, f08, "Reconstruction efficiency of the same fiducial events for each SCT z treatment (|η| < 1.8 acceptance, common 45 mm "
              "beam-spot shift, fit from the true vertex). Bars: Wilson 95%. Lines: paper Table I.", [f"{T}/acceptance_longitudinal_matrix.csv"], "acceptance A, beam spot CV", S)
if "F13v3" in which:
    P = pd.read_csv(f"{T}/v3_pileup_primary.csv")
    P = P[P.stage.isin(["plane with >=1 hit in >=4 of 8 layers", "plane with >=1 hit in all 8 layers", "Sec. III C plane", "ds < 0.01 cm = signal region"])].copy()
    P["label"] = P.stage.map({"plane with >=1 hit in >=4 of 8 layers": "plane, hits in ≥ 4 of 8 layers", "plane with >=1 hit in all 8 layers": "plane, hits in all 8 layers",
                              "Sec. III C plane": "any reconstructed plane", "ds < 0.01 cm = signal region": "signal region"})
    def f13(d):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7.4, 3.2)); d = d.reset_index(drop=True)
        for i, r in d.iterrows():
            if r.k > 0:
                ax.plot([r.wilson95_lo, r.wilson95_hi], [i, i], color=fu.SERIES[0], lw=2.4); ax.plot(r.frac, i, "o", color=fu.SERIES[0], ms=8, mec=fu.SURFACE, mew=1.4, label="this work, Wilson 95%")
                ax.annotate(f"{int(r.k)}/{int(r.n)}", (r.wilson95_hi, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=fu.INK2)
            else:
                ax.plot([1e-6, r.cp95_upper_one_sided], [i, i], color=fu.SERIES[0], lw=1, ls=":"); ax.plot(r.cp95_upper_one_sided, i, "<", color=fu.SERIES[0], ms=8, label="0 events: 95% upper limit")
                ax.annotate(f"0/{int(r.n)}", (r.cp95_upper_one_sided, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=fu.INK2)
            if not np.isnan(r.paper_approx): ax.plot(r.paper_approx, i, "D", color=fu.INK, ms=7, label="paper (approximate)")
        h, l = ax.get_legend_handles_labels(); u = dict(zip(l, h)); ax.legend(u.values(), u.keys(), fontsize=7, loc="lower right")
        ax.set_yticks(range(len(d)), d.label, fontsize=8.5); ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(2e-5, 0.1); ax.set_xlabel("fraction of pile-up events (μ = 50)")
        fig.tight_layout(); return fig
    fu.figure("F13v3_pileup", P, f13, "Pile-up only (μ = 50, 5000 events; |η| < 1.8, SCT 34 µm / 1.16 mm, pixel merging): per-event rates with Wilson 95% "
              "intervals, or the one-sided 95% upper limit when no event passes. Diamonds: the paper's approximate rates.", [f"{T}/v3_pileup_primary.csv"], "primary", S)
if "F14v3" in which:
    C = pd.read_csv(f"{T}/v3_conversion_primary.csv")
    def f14(d):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7.4, 3.5)); st = ["plane", "hit multiplicity", "signal region"]
        for j, (s, g) in enumerate(d.groupby("setup", sort=False)):
            g = g.set_index("stage").loc[st]; x = np.arange(3) + (j - 1.5) * 0.06
            ax.plot(x, g.frac.where(g.k > 0), marker=fu.MARKERS[j], ls=fu.STYLES[j], color=fu.SERIES[j], label=s, ms=7)
            z = (g.k == 0).values; ax.plot(x[z], g.cp95_upper_one_sided[z], marker="v", ls="none", ms=8, mfc="none", mec=fu.SERIES[j], mew=1.4)
        ax.plot([], [], marker="v", ls="none", mfc="none", mec=fu.INK2, label="0 events: 95% upper limit")
        ax.set_yscale("log"); ax.set_ylim(3e-5, 1); ax.set_xticks(range(3), st); ax.set_ylabel("fraction of 9139 photons"); ax.legend(fontsize=7, loc="lower left"); fig.tight_layout(); return fig
    fu.figure("F14v3_conversion", C, f14, "Converted-photon background, 9139 Z(νν)γ+jet photons, |η| < 1.8, fit from the primary vertex: fraction passing each "
              "cut. Open triangles: one-sided 95% upper limit when no event passes.", [f"{T}/v3_conversion_primary.csv"], "primary", S)
