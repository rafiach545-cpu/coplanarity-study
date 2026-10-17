#!/usr/bin/env python3
"""F40_fig5_<sct>: Figure 5 as F30, but the backgrounds use the same SCT z smearing as the signal (no 580 um).
Z1160: converted gamma + pile-up from P10_chunks_LITERAL, pile-up only from P8_chunks_LITERAL. Z0: converted gamma + pile-up from P10_chunks_B_Z0_REF34;
pile-up only was not simulated without SCT z smearing, so that panel is left out. Selection as F30 (plane + hit cut, before the Delta_s cut)."""
import os, sys, glob, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; L_ = f"{HERE}/../logs"; S = os.path.abspath(__file__); TR = lambda s: s.astype(str) == "True"
V5 = json.load(open(f"{T}/paper_fig5_vector.json")); A = pd.read_csv(f"{T}/all_crossings_per_event.csv")
PL = {"colored": "Colored Quirk", "EW": "EW Quirk", "converted γ + pile-up": "Converted gamma", "pile-up": "Pileup"}
EDG = {"ds": 10 ** np.arange(-4, -0.99, 0.1), "dw": 10 ** np.arange(-3, 1.01, 0.1)}; PVAR = {"ds": "delta_s_cm", "dw": "delta_w_cm"}
def conv(d):
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L_}/{d}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139
    return o[TR(o.plane) & TR(o.mult)]
def pile(d):
    p = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L_}/{d}/chunk_*.csv")); assert p.event_i.nunique() == 5000
    return p[TR(p.sec3c_plane_found) & (p.sec3c_dw < 1)]
for sct, lab, cdir, pdir in (("Z1160", "SCT z 1.16 mm (signal and backgrounds)", "P10_chunks_LITERAL", "P8_chunks_LITERAL"),
                             ("Z0", "no SCT z smearing (signal and backgrounds)", "P10_chunks_B_Z0_REF34", None)):
    rows = []
    for pop, smp in (("colored", "COL2000"), ("EW", "EW2000")):
        x = A[(A["sample"] == smp) & (A["mode"] == "FIRST") & (A.sct == sct) & TR(A.fid) & TR(A.plane) & TR(A.mult)]; rows += [dict(population=pop, ds=a, dw=b) for a, b in zip(x.ds, x.dw)]
    o = conv(cdir); rows += [dict(population="converted γ + pile-up", ds=a, dw=b) for a, b in zip(o.ds, o.dw)]
    if pdir: pu = pile(pdir); rows += [dict(population="pile-up", ds=a, dw=b) for a, b in zip(pu.sec3c_ds, pu.sec3c_dw)]
    pops = list(PL) if pdir else list(PL)[:3]
    for pop in pops:
        for v in ("ds", "dw"):
            h = V5[PVAR[v]]["histograms"][PL[pop]]; t = sum(b["height"] for b in h); rows += [dict(population=pop, paper_var=v, lo=b["lo"], hi=b["hi"], paper_frac=b["height"] / t) for b in h]
    src = pd.DataFrame(rows)
    def p5(d, lab=lab, pops=pops):
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(2, len(pops), figsize=(3.25 * len(pops), 5.4))
        for i, v in enumerate(("ds", "dw")):
            for j, pop in enumerate(pops):
                ax = axs[i, j]; e = EDG[v]; x = d[(d.population == pop) & d[v].notna()][v]
                hh = np.histogram(np.clip(x, e[0] * 1.0001, e[-1] * 0.9999), bins=e)[0].astype(float)
                ax.stairs(hh / max(hh.sum(), 1), e, color=fu.SERIES[j], lw=2, label=f"this work (N = {len(x)})")
                pp = d[(d.population == pop) & (d.paper_var == v)]; ax.stairs(pp.paper_frac.values, np.r_[pp.lo.values, pp.hi.values[-1]], color=fu.INK, lw=1.3, ls=":", label="paper")
                ax.axvline(0.01 if v == "ds" else 1.0, color=fu.MUTED, lw=1); ax.set_xscale("log"); ax.tick_params(labelsize=7)
                ax.set_xlabel("Δs (cm)" if v == "ds" else "Δw (cm)", fontsize=8)
                if i == 0: ax.set_title(pop, fontsize=9)
                if j == 0: ax.set_ylabel("fraction per bin", fontsize=8)
                ax.legend(fontsize=6.5, loc="upper left")
        fig.suptitle(lab, fontsize=9.5); fig.tight_layout(); return fig
    fu.figure(f"F40_fig5_{sct}", src, p5, f"Figure 5 on the paper's bins, {lab}. Signal: COL2000 / EW2000 after the plane and hit cuts, before the Δs cut; converted γ + pile-up "
              f"(9139 photons, {cdir})" + (f"; pile-up only (5000 events, {pdir})" if pdir else "; pile-up only not simulated without SCT z smearing") +
              ". Unit area; dotted: the paper's histograms. Vertical lines: signal-region cuts.",
              [f"{T}/all_crossings_per_event.csv", f"{L_}/{cdir}"] + ([f"{L_}/{pdir}"] if pdir else []) + [f"{T}/paper_fig5_vector.json"], "see caption", S)
    print(sct, src.dropna(subset=["ds"]).groupby("population").agg(N=("ds", "size"), ds_med_um=("ds", lambda s: s.median() * 1e4), dw_med=("dw", "median"),
                                                                     k_lt_cut=("ds", lambda s: int((s < 0.01).sum()))).round(4).to_string())
