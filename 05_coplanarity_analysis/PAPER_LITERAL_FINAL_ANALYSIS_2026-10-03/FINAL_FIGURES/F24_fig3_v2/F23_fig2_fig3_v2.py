#!/usr/bin/env python3
"""Fig. 2 and Fig. 3 on the paper's axes, from tables/dynamics_v2_trajectories.csv (exact CM treatment, F22_dynamics_v2.py).
Fig. 2: colored 1.8 TeV, 2 keV; |L| (hbar) and d (cm) vs r (cm), r = 0-5 cm. Event = the fiducial COL2000 event with the
        median |L|max (rule fixed in advance; no other selection).
Fig. 3: Delta_phi (plane of relative motion, windowed plane fit) vs r = 0-15 cm for colored 1.8 TeV 2 keV and EW 800 GeV 2 keV.
  (a) for each benchmark the event whose Delta_phi at r ~ 15 cm is closest to the paper's own curve end-point (shape comparison;
      selection rule stated);  (b) the median event;  (c) distribution of Delta_phi at r ~ 15 cm over all fiducial events
      (colored 22, EW 62; EW also at its Table I Lambda = 4 keV) with the paper's single-event values marked.
Paper end-points read from its Fig. 3 at r = 15 cm: colored ~0.09e-3, EW (2 keV) ~0.35e-3."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
D = pd.read_csv(f"{T}/dynamics_v2_trajectories.csv"); SUM = pd.read_csv(f"{T}/dynamics_v2_summary.csv")
PAPER15 = {"COL2000|2keV": 0.09e-3, "EW2000|2keV": 0.35e-3}
c = SUM[(SUM["sample"] == "COL2000") & (SUM.label == "2keV")].sort_values("Lmax").reset_index(drop=True); kmed = int(c.loc[len(c) // 2, "key"])
g2 = D[(D["sample"] == "COL2000") & (D.key == kmed) & (D.r_cm <= 5)].sort_values("r_cm").assign(selection=f"COL2000 event key {kmed}: median |L|max of 22 fiducial events")
def p2(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.2, 4.2)); bx = ax.twinx()
    ax.plot(d.r_cm, d.L_hbar / 1e12, color=fu.SERIES[0], lw=2, label="|L|"); bx.plot(d.r_cm, d.d_cm, color=fu.SERIES[2], lw=2, ls="--", label="d")
    ax.set_xlim(0, 5); ax.set_ylim(0, 1.0); bx.set_ylim(0, 5); ax.set_xlabel("r (cm)"); ax.set_ylabel("|L| (×10¹² ħ)", color=fu.SERIES[0]); bx.set_ylabel("d (cm)", color=fu.SERIES[2])
    ax.set_title("m_Q = 1.8 TeV, Λ = 2 keV", fontsize=10); h1, l1 = ax.get_legend_handles_labels(); h2, l2 = bx.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper right")
    bx.spines["right"].set_visible(True); fig.tight_layout(); return fig
fu.figure("F23_fig2_v2", g2, p2, f"Figure 2 on the paper's axes: magnitude of the internal angular momentum |L| (solid) and quirk separation d (dashed) in the "
          f"centre-of-mass frame at equal CM time, vs the transverse radius r of the centre of mass. Colored 1.8 TeV, Λ = 2 keV, B = 2 T; event = COL2000 key {kmed}, "
          "the fiducial event with the median |L|max. Where |L| ≈ 0, d ≈ 0.02 cm (never 0 except at r = 0), so annihilation stays suppressed.",
          [f"{T}/dynamics_v2_trajectories.csv", f"{T}/dynamics_v2_summary.csv"], "median |L|max fiducial COL2000 event", S)
rows = []
for tag, (smp, lab) in {"COL2000|2keV": ("COL2000", "2keV"), "EW2000|2keV": ("EW2000", "2keV")}.items():
    s = SUM[(SUM["sample"] == smp) & (SUM.label == lab)].copy(); s["dist"] = (s.dphiw_at_15 - PAPER15[tag]).abs()
    kp = int(s.sort_values("dist").key.iloc[0]); km = int(s.sort_values("dphiw_at_15").key.iloc[len(s) // 2])
    for kind, k in (("closest to the paper's end-point", kp), ("median event", km)):
        g = D[(D["sample"] == smp) & (D.key == k) & (D.label == lab)].sort_values("r_cm")
        rows.append(g.assign(curve=f"{'colored 1.8 TeV' if smp == 'COL2000' else 'EW 800 GeV'}, 2 keV ({kind}, key {k})", kind=kind, bench=smp))
src = pd.concat(rows)
dist = SUM[["sample", "key", "label", "dphiw_at_15"]].copy(); dist["curve"] = "distribution"; src = pd.concat([src, dist.rename(columns={"sample": "bench"})], ignore_index=True)
def p3(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.0), gridspec_kw=dict(width_ratios=[1, 1, 1.1]))
    for ax, kind in zip(axes[:2], ["closest to the paper's end-point", "median event"]):
        for j, bench in enumerate(["COL2000", "EW2000"]):
            g = d[(d.kind == kind) & (d.bench == bench) & (d.r_cm >= 0.5)].copy(); g["rb"] = (g.r_cm / 0.1).round() * 0.1
            g = g.groupby("rb").agg(r_cm=("r_cm", "median"), dphi_window_rad=("dphi_window_rad", "median"), curve=("curve", "first")).reset_index()
            ax.plot(g.r_cm, g.dphi_window_rad * 1e3, color=fu.SERIES[4] if bench == "COL2000" else fu.SERIES[1], lw=2, label=g.curve.iloc[0])
        ax.set_xlim(0, 15); ax.set_xlabel("r (cm)"); ax.set_ylabel("Δφ (×10⁻³)"); ax.set_title(kind, fontsize=10); ax.legend(fontsize=6.8, loc="upper left")
    ax = axes[2]; dd = d[d.curve == "distribution"]; E = 10 ** np.arange(-5, -0.9, 0.2)
    for j, (bench, lab, col, nm) in enumerate([("COL2000", "2keV", fu.SERIES[4], "colored 1.8 TeV, 2 keV"), ("EW2000", "2keV", fu.SERIES[1], "EW 800 GeV, 2 keV"), ("EW2000", "4keV", fu.SERIES[0], "EW 800 GeV, 4 keV (Table I)")]):
        v = dd[(dd.bench == bench) & (dd.label == lab)].dphiw_at_15.dropna(); ax.hist(v, bins=E, histtype="step", lw=2, color=col, ls=fu.STYLES[j], label=f"{nm}: median {np.median(v)*1e3:.2f}e-3")
    for tag, col in (("COL2000|2keV", fu.SERIES[4]), ("EW2000|2keV", fu.SERIES[1])): ax.axvline(PAPER15[tag], color=col, lw=1.2, ls=":")
    ax.text(PAPER15["COL2000|2keV"] * 1.05, ax.get_ylim()[1] * 0.92, "paper colored", fontsize=7, rotation=90, va="top"); ax.text(PAPER15["EW2000|2keV"] * 1.05, ax.get_ylim()[1] * 0.92, "paper EW", fontsize=7, rotation=90, va="top")
    ax.set_xscale("log"); ax.set_xlabel("Δφ at r ≈ 15 cm (rad)"); ax.set_ylabel("events"); ax.set_title("all fiducial events", fontsize=10); ax.legend(fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, -0.18), ncol=1, frameon=False)
    fig.tight_layout(); return fig
fu.figure("F24_fig3_v2", src, p3, "Figure 3 on the paper's axes: rotation Δφ of the plane of relative motion (plane fitted to the CM-frame separation over a sliding "
          "window of one oscillation) vs the transverse radius r of the centre of mass, r = 0–15 cm. Left: the event per benchmark whose Δφ at 15 cm is closest "
          "to the paper's own curve (shape comparison). Middle: the median event. Right: Δφ at r ≈ 15 cm for all fiducial events (dotted: paper's two events). "
          "Curves: median in 0.1 cm bins of r, from r = 0.5 cm (where the reference plane is set). The L̂-based estimator gives the same medians within 10%.", [f"{T}/dynamics_v2_trajectories.csv", f"{T}/dynamics_v2_summary.csv"], "rules in caption", S)
for tag in PAPER15:
    smp, lab = tag.split("|"); v = SUM[(SUM["sample"] == smp) & (SUM.label == lab)].dphiw_at_15
    print(tag, "paper value percentile in our distribution: %.0f%%" % (100 * (v < PAPER15[tag]).mean()))
