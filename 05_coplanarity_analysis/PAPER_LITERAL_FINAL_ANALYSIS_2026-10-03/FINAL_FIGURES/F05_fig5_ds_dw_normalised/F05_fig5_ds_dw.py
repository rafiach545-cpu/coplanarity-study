#!/usr/bin/env python3
"""Figure 5-style Delta_s / Delta_w distributions, LITERAL configuration, vs the paper's digitised Fig. 5.
Populations ('before the final cut on those variables', paper Sec. IV):
  colored / EW signal : COL2000 / EW2000 events with a Sec. III C plane AND hit multiplicity (cuts 1+2), literal; each sample
                        separately (COL1000/EW1000 are in the source CSV, not pooled); if fewer than 5 such events the
                        plane-only population is ALSO drawn (labelled).
  pile-up             : literal pile-up planes (paper derives pile-up from 1-hit-per-layer planes: all planes shown)
  converted photon    : literal conversion-only planes
  conversion+pile-up  : literal overlay planes (P10; drawn only if available)
Normalised panels: fraction per log bin (10/decade, the paper's own binning), paper histograms normalised the same way.
Absolute panels: raw event counts. Paper normalisation is unknown -> only shapes are compared."""
import os, sys, glob, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
FIG5 = f"{HERE}/../../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"
TR = lambda s: s.astype(str) == "True"
POPS = [("colored", "Colored Quirk"), ("EW", "EW Quirk"), ("pile-up", "Pileup"), ("converted photon", "Converted gamma"), ("conversion + pile-up", None)]


def sources():
    rows = []
    sg = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
    sg = sg[(sg.geom == "B") & (sg.sct == "Z1160") & (sg.wconv == "W1") & TR(sg.fid) & TR(sg.plane)]
    for smp, g in sg.groupby("sample"):
        pop = "colored" if smp.startswith("COL") else "EW"
        for sub, m in [("plane+multiplicity", TR(g.mult)), ("plane only", pd.Series(True, index=g.index))]:
            for _, r in g[m].iterrows():
                rows.append(dict(population=pop, sample=smp, subset=sub, event=int(r.event_id), ds_cm=r.ds, dw_cm=r.dw))
    pu = pd.read_csv(f"{T}/pileup_per_event_literal.csv"); pu = pu[TR(pu.sec3c_plane_found)]
    rows += [dict(population="pile-up", sample="PU50_literal", subset="plane", event=int(r.event_i), ds_cm=r.sec3c_ds, dw_cm=r.sec3c_dw) for _, r in pu.iterrows()]
    cv = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{HERE}/../logs/P9_chunks_LITERAL/chunk_*.csv")))
    cv = cv[(cv.config == "LITERAL") & TR(cv.plane)]
    rows += [dict(population="converted photon", sample="CONV_literal", subset="plane", event=int(r.event), ds_cm=r.ds, dw_cm=r.dw) for _, r in cv.iterrows()]
    ov = sorted(glob.glob(f"{HERE}/../logs/P10_chunks_LITERAL/chunk_*.csv"))
    if ov:
        o = pd.concat(pd.read_csv(f) for f in ov); o = o[(o.config == "LITERAL") & TR(o.plane)]
        rows += [dict(population="conversion + pile-up", sample=f"OVERLAY_literal({len(ov)} chunks)", subset="plane", event=int(r.event), ds_cm=r.ds, dw_cm=r.dw) for _, r in o.iterrows()]
    d = pd.DataFrame(rows)
    fig5 = json.load(open(FIG5))
    for var in ("delta_s_cm", "delta_w_cm"):
        for pop, lab in POPS:
            if lab is None: continue
            h = fig5[var]["histograms"][lab]; tot = sum(t["height"] for t in h)
            d = pd.concat([d, pd.DataFrame([dict(population=pop, sample="PAPER_FIG5_DIGITISED", subset=var, event=-1,
                                                 bin_lo=t["lo"], bin_hi=t["hi"], paper_frac=t["height"] / tot) for t in h])])
    return d


EDGES = {"ds_cm": 10 ** np.arange(-4, 0.01, 0.1), "dw_cm": 10 ** np.arange(-3, 1.01, 0.1)}
PVAR = {"ds_cm": "delta_s_cm", "dw_cm": "delta_w_cm"}


def ours(d, pop):
    x = d[(d.population == pop) & (d["sample"] != "PAPER_FIG5_DIGITISED")]
    if pop in ("colored", "EW"):
        smp = "COL2000" if pop == "colored" else "EW2000"
        x = x[x["sample"] == smp]; pm = x[x.subset == "plane+multiplicity"]
        return [(f"{smp} plane+mult (N={len(pm)})", pm, 0), (f"{smp} plane only (N={(x.subset == 'plane only').sum()})", x[x.subset == "plane only"], 1)]
    return [(f"literal planes (N={len(x)})", x, 0)] if len(x) else []


def plot_factory(norm):
    def plot(d):
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 5, figsize=(15, 5.6))
        for i, var in enumerate(("ds_cm", "dw_cm")):
            for j, (pop, lab) in enumerate(POPS):
                ax = axes[i, j]; e = EDGES[var]
                for k, (lbl, x, s) in enumerate(ours(d, pop)):
                    v = x[var].dropna(); h = np.histogram(v, bins=e)[0].astype(float)
                    if norm and h.sum(): h = h / h.sum()
                    ax.stairs(h, e, color=fu.SERIES[j], ls=fu.STYLES[s], lw=2 if s == 0 else 1.2, label=lbl)
                if norm and lab is not None:
                    p = d[(d.population == pop) & (d["sample"] == "PAPER_FIG5_DIGITISED") & (d.subset == PVAR[var])]
                    ax.stairs(p.paper_frac.values, np.r_[p.bin_lo.values, p.bin_hi.values[-1]], color=fu.INK, lw=1.2, ls=":", label="paper Fig. 5 (digitised)")
                cut = 0.01 if var == "ds_cm" else 1.0
                ax.axvline(cut, color=fu.MUTED, lw=1); ax.set_xscale("log")
                if not norm: ax.set_yscale("symlog", linthresh=1)
                if i == 0: ax.set_title(pop, fontsize=9)
                ax.set_xlabel("Δs (cm)" if var == "ds_cm" else "Δw (cm, √λ₂)", fontsize=8)
                if j == 0: ax.set_ylabel("fraction per bin" if norm else "events per bin", fontsize=8)
                ax.legend(fontsize=6, loc="upper left"); ax.tick_params(labelsize=7)
                if pop == "conversion + pile-up" and not len(ours(d, pop)): ax.text(0.5, 0.5, "P10 overlay\nnot yet available", transform=ax.transAxes, ha="center", fontsize=8, color=fu.MUTED)
        fig.tight_layout(); return fig
    return plot


if __name__ == "__main__":
    src = sources()
    common = ("LITERAL configuration (finite barrel, SCT 34/1160 µm, literal Sec. III C). Signal: COL2000 / EW2000 separately (no pooling); "
              "solid = plane + hit multiplicity (paper: 'before the final cut on those variables'), thin dashed = plane only. Backgrounds: all literal "
              "Sec. III C planes. Vertical line = signal-region cut. Δw = √λ₂ (Eq. 11); the paper's plotted Δw appears to be ½√λ₂ "
              "(UNRESOLVED_DIFFERENCES.md U3), so the paper's Δw shapes are expected to sit a factor 2 lower.")
    fu.figure("F05_fig5_ds_dw_normalised", src, plot_factory(True), "NORMALISED (unit area, paper's 10-per-decade log bins). " + common +
              " Dotted = paper Fig. 5 digitised and normalised the same way (paper normalisation unknown: shape comparison only).",
              [f"{T}/signal_per_event_all_configs.csv", f"{T}/pileup_per_event_literal.csv", FIG5, f"{HERE}/../logs/P9_chunks_LITERAL", f"{HERE}/../logs/P10_chunks_LITERAL"],
              "literal configuration; populations as stated", S)
    fu.figure("F05_fig5_ds_dw_absolute", src, plot_factory(False), "ABSOLUTE event counts per bin (symlog y). " + common,
              [f"{T}/signal_per_event_all_configs.csv", f"{T}/pileup_per_event_literal.csv", f"{HERE}/../logs/P9_chunks_LITERAL", f"{HERE}/../logs/P10_chunks_LITERAL"],
              "literal configuration; populations as stated", S)
    print(src.groupby(["population", "sample", "subset"]).size())
