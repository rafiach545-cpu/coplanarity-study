#!/usr/bin/env python3
"""F11: background cutflows (pile-up, converted photon, conversion + pile-up; LITERAL vs FROZEN project, sequential stages,
fraction of events with CP95 one-sided upper limit when zero) and weighted yields at 300 fb^-1 (A: project sigma,
B: paper ~1 pb alternative; C = 0.01 conversion probability; D from this analysis; CP95 upper limits for k = 0)."""
import os, sys, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
STAGES = ["Sec. III C plane", "hit multiplicity 7x2+1", "dw < 1 cm", "final"]
def norm_stage(s):
    for k in STAGES[:-1]:
        if s.startswith(k): return k
    return "final" if ("final" in s or s.startswith("ds < 0.01")) else None
rows = []
for bg, f, keep in [("pile-up μ=50", "pileup_cutflow.csv", None), ("converted photon", "converted_photon_cutflow.csv", None), ("conversion + pile-up", "overlay_cutflow.csv", None)]:
    d = pd.read_csv(f"{T}/{f}"); d = d[~d.stage.str.contains("non-sequential|generated|4/8|8/8")]
    if "sequential" in d: d = d[d.sequential.astype(str) == "True"]
    d["stage_n"] = d.stage.map(norm_stage); d = d.dropna(subset=["stage_n"]).drop_duplicates(["config", "stage_n"], keep="last")
    d = d[~d.config.str.contains("same events")]
    for _, r in d.iterrows():
        rows.append(dict(background=bg, config=r.config, stage=r.stage_n, k=r.k, n=r.n, frac=r.frac, cp95_upper=r.cp95_upper_one_sided))
cf = pd.DataFrame(rows)
y = pd.concat([pd.read_csv(f"{T}/weighted_yields_conversion.csv"), pd.read_csv(f"{T}/weighted_yields_overlay.csv")])
y = y[["background", "config", "sigma_choice", "eff_D_k", "eff_D_n", "N_300fb-1", "N_300fb-1_cp95_upper"]]
src = pd.concat([cf.assign(table="cutflow"), y.assign(table="yield300")], ignore_index=True)


def plot(d):
    import matplotlib.pyplot as plt
    c = d[d.table == "cutflow"]; yy = d[d.table == "yield300"]
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))
    for ax, bg in zip(axes[:3], ["pile-up μ=50", "converted photon", "conversion + pile-up"]):
        g = c[c.background == bg]
        for j, (cfg, gg) in enumerate(g.groupby("config", sort=False)):
            gg = gg.set_index("stage").reindex(STAGES)
            v = gg.frac.where(gg.k > 0, np.nan); ul = gg.cp95_upper.where(gg.k == 0, np.nan)
            ax.plot(range(4), v, marker=fu.MARKERS[j], ls=fu.STYLES[j], color=fu.SERIES[j], label=cfg[:48], ms=6)
            ax.plot(range(4), ul, marker="v", ls="none", color=fu.SERIES[j], ms=7, mfc="none")
        ax.set_yscale("log"); ax.set_ylim(1e-5, 1); ax.set_xticks(range(4), ["plane", "mult.", "Δw<1", "final (Δs)"], fontsize=8)
        ax.set_title(bg + "  (▽ = CP95 UL when 0)", fontsize=9); ax.legend(fontsize=5.5, loc="lower left")
    axes[0].set_ylabel("fraction of events")
    ax = axes[3]; yy = yy.reset_index(drop=True)
    lab = [f"{'conv+PU' if r.background.startswith('converted photon +') else 'conv only'} | {r.config.split(' (')[0]} | σ {'A' if r.sigma_choice.startswith('A') else 'B'}" for _, r in yy.iterrows()]
    for i, r in yy.iterrows():
        colr = fu.SERIES[0] if r.sigma_choice.startswith("A") else fu.SERIES[1]
        if r.eff_D_k > 0: ax.plot(r["N_300fb-1"], i, "o", color=colr)
        ax.plot([0, r["N_300fb-1_cp95_upper"]], [i, i], color=colr, lw=1.5)
    ax.set_yticks(range(len(yy)), lab, fontsize=6.5); ax.set_xscale("symlog", linthresh=0.1); ax.set_xlim(0, 30); ax.set_xlabel("expected events at 300 fb⁻¹ (bar = 0 … CP95 UL; ● = central)")
    ax.set_title("weighted yields (A: project σ, B: paper 1 pb)", fontsize=9)
    fig.tight_layout(); return fig


fu.figure("F11_background_cutflow_and_yields", src, plot,
          "Background cutflows (sequential, fraction of events; open triangles = one-sided Clopper–Pearson 95% upper limit when no event survives) "
          "for pile-up only (μ = 50, 5000 events), converted photon only (9139) and converted photon + pile-up overlay, LITERAL vs systematic/frozen "
          "configurations. Right: expected events at 300 fb⁻¹ = σ × 0.01 × D × L with σ = A (project, 0.211 pb after MET) or B (paper ~1 pb, alternative "
          "only). Pile-up alone has no absolute yield (needs the triggered-event rate, not stated in the paper).",
          [f"{T}/pileup_cutflow.csv", f"{T}/converted_photon_cutflow.csv", f"{T}/overlay_cutflow.csv", f"{T}/weighted_yields_conversion.csv", f"{T}/weighted_yields_overlay.csv"],
          "all configurations in the source tables", S)
print(cf.to_string())
