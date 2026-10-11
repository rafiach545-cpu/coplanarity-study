#!/usr/bin/env python3
"""Report figures on the paper's axes, with the paper's own curves from the vector source figures (tables/paper_fig23_vector.json,
tables/paper_fig5_vector.json) overlaid.
F30_fig2 : |L| and quirk separation d vs r (exact CM frame), colored 1.8 TeV, 2 keV: the COL2000 fiducial event with the median |L|max; paper event overlaid.
F30_fig3 : Delta_phi of the plane of the velocity vectors vs r (paper definition), colored and EW at 2 keV: median over fiducial events with 16-84% band,
           paper curves overlaid; right: Delta_phi at r = 15 cm for every event.
F30_fig5_<sct> : Delta_s and Delta_w after plane + hit cut (before the Delta_s cut), one hit per quirk per layer; signal SCT z 1.16 mm or none;
           backgrounds with the cited detector model [34] (SCT z 580 um) for both; unit area on the paper's bins, paper histograms overlaid."""
import os, sys, glob, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; L_ = f"{HERE}/../logs"; S = os.path.abspath(__file__); TR = lambda s: s.astype(str) == "True"
V23 = json.load(open(f"{T}/paper_fig23_vector.json")); V5 = json.load(open(f"{T}/paper_fig5_vector.json"))
# ---------- Fig. 2
f2 = pd.read_csv(f"{HERE}/../FINAL_FIGURES/F23_fig2_v2/F23_fig2_v2_source.csv"); f2 = f2[f2.r_cm <= 5.0][["r_cm", "L_hbar", "d_cm", "selection"]]
pc = V23["fig2"]["curves"]
src2 = pd.concat([f2.assign(curve="this work"), pd.DataFrame(dict(r_cm=pc["L_1e12_hbar"]["x"], L_hbar=np.array(pc["L_1e12_hbar"]["y"]) * 1e12, curve="paper L")),
                  pd.DataFrame(dict(r_cm=pc["d_cm"]["x"], d_cm=pc["d_cm"]["y"], curve="paper d"))])
def p2(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
    for ax, (lab, Lc, dc) in zip(axs, [("paper (Fig. 2, representative event)", d[d.curve == "paper L"], d[d.curve == "paper d"]),
                                      ("this work (COL2000 event with the median |L|max)", d[d.curve == "this work"], d[d.curve == "this work"])]):
        ax.plot(Lc.r_cm, Lc.L_hbar / 1e12, color=fu.SERIES[0], lw=1.8, label="|L|"); ax.set_ylim(0, 1.0); ax.set_xlim(0, 5); ax.set_xlabel("r (cm)")
        bx = ax.twinx(); bx.plot(dc.r_cm, dc.d_cm, color=fu.SERIES[2], lw=1.6, ls="--", label="d"); bx.set_ylim(0, 5); bx.set_ylabel("d (cm)")
        ax.set_title(lab, fontsize=9); ax.legend(loc="upper left", fontsize=7); bx.legend(loc="upper right", fontsize=7)
    axs[0].set_ylabel("|L| (×10¹² ħ)"); fig.suptitle("m_Q = 1.8 TeV, Λ = 2 keV, B = 2 T", fontsize=10); fig.tight_layout(); return fig
fu.figure("F30_fig2", src2, p2, "Figure 2 on the paper's axes. |L| (solid, left axis) and quirk separation d (dashed, right axis) in the exact centre-of-mass frame vs the "
          "transverse radius r of the centre of mass. Left: the paper's curves read from its vector source figure. Right: COL2000 fiducial event with the median |L|max.",
          [f"{HERE}/../FINAL_FIGURES/F23_fig2_v2/F23_fig2_v2_source.csv", f"{T}/paper_fig23_vector.json"], "median |L|max event", S)
# ---------- Fig. 3
c3 = pd.read_csv(f"{T}/fig3_velocity_plane_curves.csv"); PV = {"COL2000": V23["fig3"]["curves"]["colored_1800GeV_2keV"], "EW2000": V23["fig3"]["curves"]["EW_800GeV_2keV"]}
LB = {"COL2000": "colored 1.8 TeV, 2 keV", "EW2000": "EW 800 GeV, 2 keV"}; CL = {"COL2000": fu.SERIES[4], "EW2000": fu.SERIES[1]}
def p3(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9), gridspec_kw=dict(width_ratios=[1, 1, 1.05]))
    for ax, s in zip(axs[:2], ["COL2000", "EW2000"]):
        x = d[d["sample"] == s]; q = x.groupby("r_cm").dphi_rad.quantile([.16, .5, .84]).unstack()
        ax.fill_between(q.index, q[.16] * 1e3, q[.84] * 1e3, color=CL[s], alpha=0.18, lw=0, label="this work, 16–84% of events")
        ax.plot(q.index, q[.5] * 1e3, color=CL[s], lw=2, label=f"this work, median ({x.key.nunique()} events)")
        px = np.array(PV[s]["x"]); py = np.array(PV[s]["y"]); k = px <= 15.0; ax.plot(px[k], py[k], color=fu.INK, lw=1.4, ls=":", label="paper (one event)")
        ax.set_xlim(0, 15); ax.set_ylim(0, 1.2); ax.set_xlabel("r (cm)"); ax.set_ylabel("Δφ (×10⁻³ rad)"); ax.set_title(LB[s], fontsize=9); ax.legend(fontsize=7, loc="upper left")
    ax = axs[2]; e = d[d.r_cm > 14.5].groupby(["sample", "key"]).dphi_rad.median(); edges = 10 ** np.arange(-5, -1.49, 0.25)
    for s in ["COL2000", "EW2000"]:
        v = e.loc[s].values; ax.hist(np.clip(v, edges[0], edges[-1]), bins=edges, histtype="step", lw=2, color=CL[s], label=f"{LB[s]}: median {np.median(v)*1e3:.2f}×10⁻³")
        ax.axvline(PV[s]["y"][int(np.argmin(np.abs(np.array(PV[s]["x"]) - 15)))] * 1e-3, color=CL[s], ls=":", lw=1.4)
    ax.set_xscale("log"); ax.set_xlabel("Δφ at r = 15 cm (rad)"); ax.set_ylabel("events"); ax.set_title("every fiducial event (dotted: paper)", fontsize=9); ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False)
    fig.tight_layout(); return fig
fu.figure("F30_fig3", c3, p3, "Figure 3 on the paper's axes: rotation Δφ of the plane spanned by the two quirks' velocity vectors (the paper's definition) vs the transverse radius r of "
          "the centre of mass, B = 2 T, both benchmarks at Λ = 2 keV as in the paper. Line: median over all fiducial events (0.1 cm bins); band: 16–84% of events; dotted: the paper's "
          "event from its vector source figure. Right: Δφ at r = 15 cm for every event.", [f"{T}/fig3_velocity_plane_curves.csv", f"{T}/paper_fig23_vector.json"], "all fiducial events", S)
# ---------- Fig. 5
A = pd.read_csv(f"{T}/all_crossings_per_event.csv")
o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L_}/P10_chunks_B_Z580_REF34/chunk_*.csv")); o = o[(o.config == "LITERAL") & TR(o.plane) & TR(o.mult)]
pu = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L_}/P21_chunks_REF34_Z580/chunk_*.csv")); pu = pu[TR(pu.sec3c_plane_found) & (pu.sec3c_dw < 1)]
PL = {"colored": "Colored Quirk", "EW": "EW Quirk", "converted γ + pile-up": "Converted gamma", "pile-up": "Pileup"}
POPS = list(PL); EDG = {"ds": 10 ** np.arange(-4, -0.99, 0.1), "dw": 10 ** np.arange(-3, 1.01, 0.1)}; PVAR = {"ds": "delta_s_cm", "dw": "delta_w_cm"}
for sct, lab in (("Z1160", "signal SCT z 1.16 mm"), ("Z0", "signal without SCT z smearing")):
    rows = []
    for pop, smp in (("colored", "COL2000"), ("EW", "EW2000")):
        x = A[(A["sample"] == smp) & (A["mode"] == "FIRST") & (A.sct == sct) & TR(A.fid) & TR(A.plane) & TR(A.mult)]; rows += [dict(population=pop, ds=a, dw=b) for a, b in zip(x.ds, x.dw)]
    rows += [dict(population="converted γ + pile-up", ds=a, dw=b) for a, b in zip(o.ds, o.dw)] + [dict(population="pile-up", ds=a, dw=b) for a, b in zip(pu.sec3c_ds, pu.sec3c_dw)]
    for pop, pl in PL.items():
        for v in ("ds", "dw"):
            h = V5[PVAR[v]]["histograms"][pl]; t = sum(b["height"] for b in h); rows += [dict(population=pop, paper_var=v, lo=b["lo"], hi=b["hi"], paper_frac=b["height"] / t) for b in h]
    src = pd.DataFrame(rows)
    def p5(d, lab=lab):
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(2, 4, figsize=(13, 5.4))
        for i, v in enumerate(("ds", "dw")):
            for j, pop in enumerate(POPS):
                ax = axs[i, j]; e = EDG[v]; x = d[(d.population == pop) & d[v].notna()][v]
                hh = np.histogram(np.clip(x, e[0] * 1.0001, e[-1] * 0.9999), bins=e)[0].astype(float)
                ax.stairs(hh / max(hh.sum(), 1), e, color=fu.SERIES[j], lw=2, label=f"this work (N = {len(x)})")
                pp = d[(d.population == pop) & (d.paper_var == v)]; ax.stairs(pp.paper_frac.values, np.r_[pp.lo.values, pp.hi.values[-1]], color=fu.INK, lw=1.3, ls=":", label="paper")
                ax.axvline(0.01 if v == "ds" else 1.0, color=fu.MUTED, lw=1); ax.set_xscale("log"); ax.tick_params(labelsize=7)
                ax.set_xlabel("Δs (cm)" if v == "ds" else "Δw (cm)", fontsize=8)
                if i == 0: ax.set_title(pop, fontsize=9)
                if j == 0: ax.set_ylabel("fraction per bin", fontsize=8)
                ax.legend(fontsize=6.5, loc="upper left")
        fig.suptitle(lab + "; backgrounds: cited detector model [34], SCT z 580 µm", fontsize=9.5); fig.tight_layout(); return fig
    fu.figure(f"F30_fig5_{sct}", src, p5, f"Figure 5 on the paper's bins, {lab}. Signal: COL2000 / EW2000 events after the plane and hit cuts, before the Δs cut (Δw < 1 cm is part of the "
              "plane search), one hit per quirk per layer. Converted γ + pile-up (9139 photons) and pile-up only (5000 events, selected planes): cited detector model [34], SCT z 580 µm. "
              "Unit area; dotted: the paper's histograms from its vector source figures. Vertical lines: signal-region cuts.",
              [f"{T}/all_crossings_per_event.csv", f"{L_}/P10_chunks_B_Z580_REF34", f"{L_}/P21_chunks_REF34_Z580", f"{T}/paper_fig5_vector.json"], "see caption", S)
    print(sct, src.dropna(subset=["ds"]).groupby("population").agg(N=("ds", "size"), ds_med_um=("ds", lambda s: s.median() * 1e4), dw_med=("dw", "median"), frac_ds_lt_cut=("ds", lambda s: (s < 0.01).mean())).round(3).to_string())
