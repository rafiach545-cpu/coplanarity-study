#!/usr/bin/env python3
"""F06: Table I comparison (literal, each sample separately, Wilson 95% + 68%) vs paper central values.
   F07: literal signal cutflow per sample (fraction of trigger-analysed events surviving each stage).
   F08: SCT-z systematic envelope of eps_reco (diagnostic; NOT the literal result except Z1160)."""
import os, sys, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
SAMPLES = ["COL1000", "COL2000", "EW1000", "EW2000"]


def f06():
    c = pd.read_csv(f"{T}/paper_project_comparison.csv")
    st = pd.read_csv(f"{T}/signal_efficiency_statistics.csv")
    st = st[st.config == "LITERAL"].replace({"reconstruction (full Sec. IV SR)": "reconstruction"})
    src = c.merge(st[["sample", "quantity", "wilson68_lo", "wilson68_hi"]], on=["sample", "quantity"])

    def plot(d):
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8), sharey=False)
        for ax, q in zip(axes, ["trigger", "fiducial", "reconstruction"]):
            x = d[d.quantity == q].set_index("sample").loc[SAMPLES].reset_index()
            for i, r in x.iterrows():
                col = fu.SERIES[0] if r["sample"].startswith("COL") else fu.SERIES[1]
                ax.plot([i, i], [r.wilson95_lo, r.wilson95_hi], color=col, lw=1.5)
                ax.plot([i, i], [r.wilson68_lo, r.wilson68_hi], color=col, lw=4, solid_capstyle="round")
                ax.plot(i, r.project_eff, marker=fu.MARKERS[0] if r["sample"].startswith("COL") else fu.MARKERS[1], color=col, ms=8,
                        mec=fu.SURFACE, mew=1.5)
                ax.plot([i - 0.35, i + 0.35], [r.paper_eff] * 2, color=fu.INK, lw=1.5, ls="--")
                ax.annotate(f"{r.project_k}/{r.project_n}", (i, r.wilson95_hi), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=7, color=fu.INK2)
            ax.set_xticks(range(4), SAMPLES, fontsize=8); ax.set_title({"trigger": "ε_trig", "fiducial": "ε_fid", "reconstruction": "ε_reco"}[q], fontsize=10)
            ax.set_ylim(0, 1.0 if q == "reconstruction" else 0.55)
        axes[0].set_ylabel("efficiency")
        from matplotlib.lines import Line2D
        axes[2].legend([Line2D([], [], color=fu.SERIES[0], marker="o"), Line2D([], [], color=fu.SERIES[1], marker="s"),
                        Line2D([], [], color=fu.INK, ls="--")], ["colored (literal)", "EW (literal)", "paper Table I"], fontsize=7, loc="upper left")
        fig.tight_layout(); return fig
    fu.figure("F06_table_I_comparison", src, plot,
              "Table I comparison, LITERAL configuration, each frozen sample separately (no pooling). Point = k/n; thick bar = Wilson 68%; "
              "thin bar = Wilson 95%; dashed line = paper Table I central value (paper publishes no counts or uncertainties). "
              "ε_reco = full Sec. IV signal region / (trigger ∧ fiducial).",
              [f"{T}/paper_project_comparison.csv", f"{T}/signal_efficiency_statistics.csv"], "config == LITERAL; all four samples", S)


def f07():
    c = pd.read_csv(f"{T}/signal_cutflow_with_event_ids.csv")
    c = c[c.config == "LITERAL"][["sample", "step", "stage", "events", "lost_here"]].copy()
    c["frac_of_trigger_analysed"] = c.events / c.groupby("sample").events.transform("first")

    def plot(d):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7.5, 4))
        for j, s in enumerate(SAMPLES):
            x = d[d["sample"] == s].sort_values("step")
            ax.plot(x.step, x.events, ls=fu.STYLES[j], marker=fu.MARKERS[j], color=fu.SERIES[j], label=s, ms=6)
        st = d[d["sample"] == SAMPLES[0]].sort_values("step")
        ax.set_xticks(st.step, st.stage, rotation=25, ha="right", fontsize=8); ax.set_yscale("log"); ax.set_ylabel("events (log)")
        ax.legend(fontsize=8); fig.tight_layout(); return fig
    fu.figure("F07_signal_cutflow_literal", c, plot,
              "Literal signal cutflow (absolute event counts, log scale) from trigger-analysed events to the final Sec. IV signal region, "
              "each sample separately. Lost event IDs per stage: tables/signal_cutflow_with_event_ids.csv.",
              [f"{T}/signal_cutflow_with_event_ids.csv"], "config == LITERAL", S)


def f08():
    st = pd.read_csv(f"{T}/signal_efficiency_statistics.csv")
    st = st[(st.quantity == "reconstruction (full Sec. IV SR)") & (st.dw_convention == "W1")][["sample", "config", "geometry", "sct_z", "N_pass", "N_total", "eff", "wilson95_lo", "wilson95_hi", "paper"]]

    def plot(d):
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
        zs = ["Z1160", "Z580", "Z34", "Z0"]
        for ax, g in zip(axes, ["B", "A"]):
            for j, s in enumerate(SAMPLES):
                x = d[(d["sample"] == s) & (d.geometry == g)].set_index("sct_z").loc[zs].reset_index()
                xs = np.arange(4) + (j - 1.5) * 0.12
                ax.errorbar(xs, x.eff, yerr=[x.eff - x.wilson95_lo, x.wilson95_hi - x.eff], fmt=fu.MARKERS[j], color=fu.SERIES[j], label=s, ms=6, capsize=0)
            ax.axhline(0.72, color=fu.INK, ls="--", lw=1); ax.axhline(0.35, color=fu.INK2, ls=":", lw=1.2)
            ax.text(-0.45, 0.735, "paper EW 0.72", fontsize=7, va="bottom", ha="left", color=fu.INK); ax.text(-0.45, 0.365, "paper colored 0.35", fontsize=7, va="bottom", ha="left", color=fu.INK2)
            ax.set_xticks(range(4), ["1160 µm\n(LITERAL)", "580 µm", "34 µm", "0\n(calibrated)"], fontsize=8)
            ax.set_title("geometry B: finite barrel (literal)" if g == "B" else "geometry A: η-cone (project; systematic)", fontsize=9)
            ax.set_xlabel("SCT z resolution σ_z")
        axes[0].set_ylabel("ε_reco (Wilson 95%)"); axes[1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.12, 1.0)); fig.tight_layout(); return fig
    fu.figure("F08_diag_sct_z_envelope", st, plot,
              "DIAGNOSTIC: ε_reco vs the SCT z resolution, same events and hits. Only geometry B with σ_z = 1160 µm is the literal result; "
              "the other points are systematic variants. σ_z = 0 is calibrated (not paper-stated). The paper's own Fig. 5 Δs is only "
              "consistent with σ_z ≲ 34 µm (UNRESOLVED_DIFFERENCES.md U2).",
              [f"{T}/signal_efficiency_statistics.csv"], "reconstruction, W1, all geometries and SCT z variants", S)


if __name__ == "__main__":
    f06(); f07(); f08()
