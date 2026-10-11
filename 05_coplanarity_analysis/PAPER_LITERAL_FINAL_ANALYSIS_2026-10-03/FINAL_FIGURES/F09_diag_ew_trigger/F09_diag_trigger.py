#!/usr/bin/env python3
"""DIAGNOSTIC F09: EW vs colored trigger efficiency for every one-at-a-time generator/trigger variation screened in
PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02 (pre-registered screen; each config run for BOTH benchmarks),
plus the MG5 2.3.3 / Pythia 8.212 version pilot (EW only) from EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02.
None of these is adopted; the literal result is B0_frozenLHE. Paper Table I = (0.24, 0.10)."""
import os, sys, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
B = f"{HERE}/../.."
SCR = f"{B}/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/trigger_screen_results.csv"
PIL = f"{B}/EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/tables/version_pilot_variants.csv"
s = pd.read_csv(SCR); p = pd.read_csv(PIL)
w = s.pivot_table(index="config", columns="bench", values=["eps_trig", "w95_lo", "w95_hi", "N_trigger", "N_matched"], aggfunc="first")
w.columns = [f"{a}_{b}" for a, b in w.columns]; w = w.reset_index(); w["kind"] = "screen (both benchmarks)"
pp = p[["variant", "trig_over_matched", "wilson95_lo", "wilson95_hi", "N_trigger", "N_matched"]].rename(columns={"variant": "config", "trig_over_matched": "eps_trig_EW", "wilson95_lo": "w95_lo_EW", "wilson95_hi": "w95_hi_EW", "N_trigger": "N_trigger_EW", "N_matched": "N_matched_EW"})
pp["kind"] = "version pilot (EW only)"
src = pd.concat([w, pp], ignore_index=True); src["ratio_EW_over_COL"] = src.eps_trig_EW / src.get("eps_trig_COL")


def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1.2, 1]))
    ax = axes[0]; sc = d[d.kind.str.startswith("screen")]
    for _, r in sc.iterrows():
        lit = r.config == "B0_frozenLHE"
        ax.errorbar(r.eps_trig_COL, r.eps_trig_EW, xerr=[[r.eps_trig_COL - r.w95_lo_COL], [r.w95_hi_COL - r.eps_trig_COL]],
                    yerr=[[r.eps_trig_EW - r.w95_lo_EW], [r.w95_hi_EW - r.eps_trig_EW]], fmt="s" if lit else "o",
                    color=fu.SERIES[1] if lit else fu.SERIES[0], ms=8 if lit else 5, lw=1, alpha=1 if lit else 0.7,
                    label="literal (frozen LHE)" if lit else None)
    ax.plot([], [], "o", color=fu.SERIES[0], label="one-at-a-time variation (not adopted)")
    ax.plot(0.24, 0.10, marker="*", ms=16, color=fu.INK, ls="none", label="paper Table I (0.24, 0.10)")
    x = np.linspace(0.1, 0.35, 10); ax.plot(x, 0.42 * x, color=fu.MUTED, ls=":", lw=1, label="paper ratio EW/COL = 0.42")
    ax.set_xlabel("colored ε_trig (Wilson 95%)"); ax.set_ylabel("EW ε_trig (Wilson 95%)"); ax.legend(fontsize=7, loc="upper left"); ax.set_xlim(0.1, 0.35); ax.set_ylim(0.05, 0.25)
    ax2 = axes[1]; pl = d.sort_values("eps_trig_EW").reset_index(drop=True)
    ax2.errorbar(pl.eps_trig_EW, np.arange(len(pl)), xerr=[pl.eps_trig_EW - pl.w95_lo_EW, pl.w95_hi_EW - pl.eps_trig_EW], fmt="o", color=fu.SERIES[1], ms=4, lw=1)
    ax2.axvline(0.10, color=fu.INK, ls="--", lw=1.2); ax2.text(0.102, len(pl) - 1, "paper 0.10", fontsize=7)
    ax2.set_yticks(range(len(pl)), pl.config, fontsize=5); ax2.set_xlabel("EW ε_trig (all variations incl. version pilot)")
    fig.tight_layout(); return fig


fu.figure("F09_diag_ew_trigger", src, plot,
          "DIAGNOSTIC: EW vs colored trigger efficiency (pair pT > 200 GeV / matched) for every pre-registered one-at-a-time generator/trigger "
          "variation (left; both benchmarks) and all EW variations including the MG5 2.3.3 / Pythia 8.212 version pilot (right). Error bars: "
          "Wilson 95%. No variation reaches the paper's EW 0.10 while keeping the colored 0.24; the literal result (frozen LHE) is highlighted. "
          "None of the variations is adopted (UNRESOLVED_DIFFERENCES.md U1).", [SCR, PIL], "all rows of both source tables", os.path.abspath(__file__))
print(src[["config", "kind", "eps_trig_COL", "eps_trig_EW", "ratio_EW_over_COL"]].to_string())
