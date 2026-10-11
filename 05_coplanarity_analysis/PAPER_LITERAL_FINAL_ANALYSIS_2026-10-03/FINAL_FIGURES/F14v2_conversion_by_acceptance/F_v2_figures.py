#!/usr/bin/env python3
"""v2 figures after the acceptance/longitudinal correction (2026-10-03). PRIMARY = acceptance A (paper-stated |eta|<1.8),
beam spot CV; B (finite barrel, Ref. [27]) shown only as a labelled INFERRED sensitivity. Data: tables written by P4c/P9d/P13."""
import os, sys, json, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
from stats_utils import row
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
SAMPLES = ["COL1000", "COL2000", "EW1000", "EW2000"]; TR = lambda s: s.astype(str) == "True"
SZ = [("Z1160", "SCT z 1160 µm (inferred)"), ("Z580", "SCT z 580 µm (sensitivity)"), ("Z0", "no SCT z smearing (undocumented)")]
PAP = {"COL": {"trigger": .24, "fiducial": .28, "reconstruction": .35}, "EW": {"trigger": .10, "fiducial": .28, "reconstruction": .72}}

# ---- F06v2 Table I comparison (primary A) ----
P = pd.read_csv(f"{T}/v2_primary_table_I.csv")
def f06(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.9))
    for ax, q in zip(axes, ["trigger", "fiducial", "reconstruction"]):
        x = d[d.quantity == q]
        for i, s in enumerate(SAMPLES):
            b = "EW" if s.startswith("EW") else "COL"; xs = x[x["sample"] == s]
            items = [("—", 0, fu.SERIES[0] if b == "COL" else fu.SERIES[1], "o")] if q != "reconstruction" else [(t, (j - 1) * 0.22, fu.SERIES[j + (0 if j < 1 else 1)], fu.MARKERS[j]) for j, (t, _) in enumerate([("SCT z 1160 um (2x580, INFERRED)", 0), ("SCT z 580 um (1x Ref.[27], sensitivity)", 0), ("no SCT z smearing (UNDOCUMENTED)", 0)])]
            for t, off, col, mk in items:
                r = xs[xs.treatment == t].iloc[0]
                ax.plot([i + off] * 2, [r.wilson95_lo, r.wilson95_hi], color=col, lw=1.6)
                ax.plot(i + off, r.frac, marker=mk, color=col, ms=7, mec=fu.SURFACE, mew=1.2, ls="none")
            ax.plot([i - 0.38, i + 0.38], [PAP[b][q]] * 2, color=fu.INK, ls="--", lw=1.4)
        ax.set_xticks(range(4), SAMPLES, fontsize=8); ax.set_title({"trigger": "ε_trig", "fiducial": "ε_fid (|η| < 1.8, paper-stated)", "reconstruction": "ε_reco by SCT z treatment"}[q], fontsize=9)
        ax.set_ylim(0, 1.0 if q == "reconstruction" else 0.65)
    from matplotlib.lines import Line2D
    axes[2].legend([Line2D([], [], color=fu.SERIES[0], marker=fu.MARKERS[0]), Line2D([], [], color=fu.SERIES[2], marker=fu.MARKERS[1]),
                    Line2D([], [], color=fu.SERIES[3], marker=fu.MARKERS[2]), Line2D([], [], color=fu.INK, ls="--")],
                   ["SCT z 1160 µm (inferred)", "SCT z 580 µm", "no SCT z smearing (undoc.)", "paper"], fontsize=6.5, loc="upper left")
    axes[0].set_ylabel("efficiency (Wilson 95%)"); fig.tight_layout(); return fig
fu.figure("F06v2_table_I_primary", P, f06,
          "PRIMARY Table I comparison (v2): paper-stated acceptance (barrel only, |η| < 1.8, no finite-z boundary), 45 mm beam spot as one "
          "common shift per event with the fit from the true vertex, SCT R-φ 34 µm. Reconstruction shown for every SCT z treatment. "
          "Bars: Wilson 95%. Dashed: paper Table I.", [f"{T}/v2_primary_table_I.csv"], "acceptance A, beam spot CV", S)

# ---- F08v2 SCT z envelope, A primary vs B sensitivity ----
M = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv"); E = M[M.beamspot == "CV"].copy()
def f08(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, acc, title in zip(axes, ["A", "B"], ["A: paper-stated |η| < 1.8 (PRIMARY)", "B: finite barrel, Ref. [27] (INFERRED sensitivity)"]):
        for j, s in enumerate(SAMPLES):
            for k, (sz, _) in enumerate(SZ):
                r = d[(d["sample"] == s) & (d.acceptance == acc) & (d.sct_z == sz)].iloc[0]; x = k + (j - 1.5) * 0.12
                ax.errorbar(x, r.eps_reco, yerr=[[r.eps_reco - r.reco_w95_lo], [r.reco_w95_hi - r.eps_reco]], fmt=fu.MARKERS[j], color=fu.SERIES[j], ms=6, label=s if k == 0 else None)
        ax.axhline(0.72, color=fu.INK, ls="--", lw=1); ax.axhline(0.35, color=fu.INK2, ls=":", lw=1.2)
        ax.text(-0.45, 0.735, "paper EW 0.72", fontsize=7); ax.text(-0.45, 0.365, "paper colored 0.35", fontsize=7, color=fu.INK2)
        ax.set_xticks(range(3), ["1160 µm\n(2×580, inferred)", "580 µm\n(sensitivity)", "0\n(undocumented)"], fontsize=8); ax.set_title(title, fontsize=9); ax.set_xlabel("SCT z measurement smearing")
    axes[0].set_ylabel("ε_reco (Wilson 95%)"); axes[1].legend(fontsize=7, loc="upper left"); fig.tight_layout(); return fig
fu.figure("F08v2_sct_z_envelope", E, f08,
          "ε_reco of the same events for each SCT z treatment; left: paper-stated |η| < 1.8 acceptance (primary), right: finite barrel of Ref. [27] "
          "(inferred sensitivity). Beam spot: one common 45 mm shift per event, fit from the true vertex.", [f"{T}/acceptance_longitudinal_matrix.csv"], "beamspot CV", S)

# ---- F12v2 fiducial A vs B ----
F = M[(M.sct_z == "Z1160") & (M.beamspot == "CV")][["sample", "acceptance", "fiducial", "trigger_analysed", "eps_fid", "fid_w95_lo", "fid_w95_hi", "p_fid"]]
def f12(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for j, (acc, lab) in enumerate([("A", "|η| < 1.8, paper-stated (PRIMARY)"), ("B", "finite barrel, Ref. [27] (INFERRED)")]):
        x = d[d.acceptance == acc].set_index("sample").loc[SAMPLES].reset_index(); xs = np.arange(4) + (j - 0.5) * 0.22
        ax.errorbar(xs, x.eps_fid, yerr=[x.eps_fid - x.fid_w95_lo, x.fid_w95_hi - x.eps_fid], fmt=fu.MARKERS[j], color=fu.SERIES[j], ms=7, label=lab)
        for xx, r in zip(xs, x.itertuples()): ax.annotate(f"{r.fiducial}/{r.trigger_analysed}", (xx, r.fid_w95_hi), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=6.5, color=fu.INK2)
    ax.axhline(0.28, color=fu.INK, ls="--", lw=1.2, label="paper 0.28"); ax.set_xticks(range(4), SAMPLES); ax.set_ylim(0, 0.7)
    ax.set_ylabel("ε_fid (Wilson 95%)"); ax.legend(fontsize=7, loc="upper left"); fig.tight_layout(); return fig
fu.figure("F12v2_fiducial_acceptance", F, f12,
          "Fiducial efficiency under the paper-stated |η| < 1.8 acceptance (primary) and under the finite barrel lengths of Ref. [27] (inferred "
          "sensitivity), each sample separately. The paper's 0.28 is reproduced only by the inferred finite barrel for EW.", [f"{T}/acceptance_longitudinal_matrix.csv"], "SCT z 1160, beam spot CV (fiducial does not depend on SCT z)", S)

# ---- F15v2 signal Delta_s vs paper (A) ----
FIG5 = f"{HERE}/../../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"
pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); rows = []
for smp, lab in [("EW2000", "EW Quirk"), ("COL2000", "Colored Quirk")]:
    for sz, nm in [("Z1160", "SCT z 1160 µm (inferred)"), ("Z0", "no SCT z smearing (undocumented)")]:
        x = pe[(pe["sample"] == smp) & (pe.geom == "A") & (pe.sct == sz) & (pe.bs == "CV") & TR(pe.fid) & TR(pe.plane) & TR(pe.mult)]
        rows += [dict(sample=smp, series=nm, ds_cm=v) for v in x.ds]
    h = json.load(open(FIG5))["delta_s_cm"]["histograms"][lab]; tot = sum(t["height"] for t in h)
    rows += [dict(sample=smp, series="paper Fig. 5", bin_lo=t["lo"], bin_hi=t["hi"], frac=t["height"] / tot) for t in h]
D = pd.DataFrame(rows); EB = 10 ** np.arange(-4, -0.99, 0.1)
def f15(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.4), sharey=True)
    for ax, smp, title in zip(axes, ["EW2000", "COL2000"], ["EW 800 GeV, Λ = 4 keV (EW2000)", "colored 1800 GeV, Λ = 2 keV (COL2000)"]):
        g = d[d["sample"] == smp]; p = g[g.series == "paper Fig. 5"]
        ax.stairs(p.frac.values, np.r_[p.bin_lo.values, p.bin_hi.values[-1]], color=fu.INK, lw=1.6, ls=":", label="paper Fig. 5")
        for nm, col, ls in [("SCT z 1160 µm (inferred)", fu.SERIES[1], "-"), ("no SCT z smearing (undocumented)", fu.SERIES[0], "--")]:
            v = g[g.series == nm].ds_cm.dropna(); hh = np.histogram(v, bins=EB)[0].astype(float)
            ax.stairs(hh / max(hh.sum(), 1), EB, color=col, lw=2, ls=ls, label=f"{nm}: N = {len(v)}, median {np.median(v)*1e4:.0f} µm")
        ax.axvline(0.01, color=fu.MUTED, lw=1); ax.set_xscale("log"); ax.set_xlabel("Δs (cm); signal-region cut at 0.01 cm"); ax.set_title(title, fontsize=9); ax.legend(fontsize=6.6, loc="upper left")
    axes[0].set_ylabel("fraction of events per bin"); fig.tight_layout(); return fig
fu.figure("F15v2_signal_ds_vs_paper", D, f15,
          "Signal Δs before the last cut (plane + hit multiplicity), paper-stated |η| < 1.8 acceptance, unit area on the paper's log bins, "
          "for the inferred SCT z 1160 µm and the undocumented no-smearing treatment, vs the paper's digitised Fig. 5.", [f"{T}/acceptance_longitudinal_per_event.csv", FIG5], "acceptance A, beam spot CV, EW2000 and COL2000", S)
for (s, n), g in D.dropna(subset=["ds_cm"]).groupby(["sample", "series"]): print(s, n, len(g), round(g.ds_cm.median() * 1e4), "um")

# ---- F14v2 background flows by acceptance ----
cvA = pd.read_csv(f"{T}/conversion_acceptance_A_cutflow.csv"); cvB = pd.read_csv(f"{T}/converted_photon_cutflow.csv"); ov = pd.read_csv(f"{T}/overlay_cutflow.csv")
rr = []
def add(name, d, cfg, keys):
    for st, key in zip(["plane", "hit multiplicity", "signal region"], keys):
        r = d[d.config.str.startswith(cfg) & d.stage.str.startswith(key)].iloc[0]; rr.append(dict(series=name, stage=st, k=int(r.k), n=int(r.n), frac=r.frac, cp95_upper=r.cp95_upper_one_sided))
add("conversion, |η|<1.8, SCT z 1160 µm (primary)", cvA, "A_Z1160_PV", ["Sec. III C", "hit mult", "final"])
add("conversion, |η|<1.8, no SCT z smearing (undoc.)", cvA, "A_Z0_PV", ["Sec. III C", "hit mult", "final"])
add("conversion + pile-up, |η|<1.8, SCT 1160, conv.-point origin (old run)", ov, "FROZEN overlay v1 (all", ["Sec. III C", "hit mult", "ds <"])
add("conversion + pile-up, finite barrel, SCT 1160, PV origin (sensitivity)", ov, "LITERAL", ["Sec. III C", "hit mult", "ds <"])
B2 = pd.DataFrame(rr)
def f14(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.4, 3.6)); st = ["plane", "hit multiplicity", "signal region"]
    for j, (s, g) in enumerate(d.groupby("series", sort=False)):
        g = g.set_index("stage").loc[st]; x = np.arange(3) + (j - 1.5) * 0.06
        ax.plot(x, g.frac.where(g.k > 0), marker=fu.MARKERS[j], ls=fu.STYLES[j], color=fu.SERIES[j], label=s, ms=7)
        z = (g.k == 0).values; ax.plot(x[z], g.cp95_upper[z], marker="v", ls="none", ms=8, mfc="none", mec=fu.SERIES[j], mew=1.4)
    ax.plot([], [], marker="v", ls="none", mfc="none", mec=fu.INK2, label="0 events: 95% upper limit")
    ax.set_yscale("log"); ax.set_ylim(3e-5, 1); ax.set_xticks(range(3), st); ax.set_ylabel("fraction of 9139 photons"); ax.legend(fontsize=6.6, loc="lower left"); fig.tight_layout(); return fig
fu.figure("F14v2_conversion_by_acceptance", B2, f14,
          "Converted-photon background (9139 photons): fraction surviving each cut, by acceptance and SCT z treatment. Open triangles: one-sided 95% "
          "upper limit when no event survives.", [f"{T}/conversion_acceptance_A_cutflow.csv", f"{T}/overlay_cutflow.csv"], "as labelled", S)
print(B2.to_string())
