#!/usr/bin/env python3
"""F41_appendixA_diagram: how L builds up and returns (Appendix A of arXiv:2002.07503), drawn for the event with the paper's kinematics.
Top: sketch in the pair's rest (CM) frame at g = 0, 0.5, 1, 1.5, 2: quirk positions, separation d, field E* = gamma v_cm x B, force qE* on each quirk, sign of the
torque q d x E*. Middle: d(g). Bottom: L(g). d and L from tables/fig2_final/fig2_ours_constructed.csv; g = r / (r-spacing of the closest approaches), so g = 1, 2, 3, 4
are the meetings (minima of d)."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables/fig2_final"; S = os.path.abspath(__file__)
d0 = pd.read_csv(f"{T}/fig2_ours_constructed.csv")
r, dd = d0.r_cm.values, d0.d_cm.values
mins = [r[i] for i in range(1, len(dd) - 1) if dd[i] < dd[i - 1] and dd[i] <= dd[i + 1] and dd[i] < 0.05 * dd.max()]
sp = float(np.mean(np.diff([0.0] + mins)))
src = pd.DataFrame(dict(g=r / sp, d_cm=dd, L_1e12_hbar=d0.L_1e12_hbar.values))

def plot(d):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Arc
    Q1, Q2, EC, LC = fu.SERIES[0], fu.SERIES[1], fu.SERIES[6], fu.INK
    fig = plt.figure(figsize=(11, 9.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.35, 0.8, 1.0], hspace=0.32)
    # ---- top: sketch
    ax = fig.add_subplot(gs[0]); ax.set_xlim(-0.6, 10.6); ax.set_ylim(-1.75, 1.75); ax.axis("off")
    snaps = [(0, "g = 0 (n = 0): production\nz₁ = −z₂ = 0,  v₁ = −v₂\nhead-on, L = 0  (Eq. A.5)"), (0.5, "g = 0.5\nlargest d"),
             (1, "g = 1: 1st meeting\nquirks pass each other\noff-centre, |L| largest\n(not covered by A.5)"),
             (1.5, "g = 1.5\nlargest d"), (2, "g = 2 (n = 1): 2nd meeting\nz₁ = −z₂ = 0,  v₁ = −v₂\nhead-on again, L = 0  (Eq. A.5)")]
    for j, (g, lab) in enumerate(snaps):
        cx = 1.0 + 2.1 * j; half = 0.75 * abs(np.sin(np.pi * g))           # sketch: separation grows and shrinks each half-oscillation
        s1 = 1 if (g % 2) <= 1 else -1                                       # quirk 1 right in 0<g<1, left in 1<g<2 (they pass through each other)
        x1, x2 = cx + s1 * half, cx - s1 * half
        ax.plot([cx - 0.95, cx + 0.95], [0, 0], color=fu.MUTED, lw=0.8, ls=":")
        if half > 0.01:
            ax.add_patch(FancyArrowPatch((x2, -0.22), (x1, -0.22), arrowstyle="<->", mutation_scale=9, color=fu.INK2, lw=1))
            ax.text(cx, -0.42, "d", ha="center", va="top", fontsize=9, color=fu.INK2, style="italic")
            for x, sgn, col in ((x1, 1, Q1), (x2, -1, Q2)):                  # force qE*: up on +q, down on -q
                ax.add_patch(FancyArrowPatch((x, 0.12 * sgn), (x, 0.62 * sgn), arrowstyle="-|>", mutation_scale=10, color=col, lw=1.6))
            tpos = (g % 2) < 1
            ax.add_patch(Arc((cx, 0), 1.2, 1.0, theta1=25, theta2=155, color=LC, lw=1.1))          # upper arc; arrowhead gives the sense of rotation
            a_end = np.deg2rad(155 if tpos else 25); a_pre = np.deg2rad(140 if tpos else 40)
            ax.annotate("", xy=(cx + 0.6 * np.cos(a_end), 0.5 * np.sin(a_end)), xytext=(cx + 0.6 * np.cos(a_pre), 0.5 * np.sin(a_pre)),
                        arrowprops=dict(arrowstyle="-|>", color=LC, lw=1.1, mutation_scale=11))
            ax.text(cx, 0.75, "τ > 0\nL rises" if tpos else "τ < 0\nL falls", ha="center", va="bottom", fontsize=8.5, color=LC)
        if half <= 0.01:                                                      # meeting: both quirks at the same point, drawn side by side
            x1, x2 = cx + 0.09, cx - 0.09
            v1 = 1 if (g % 2) == 0 else -1                                    # quirk 1 moves right at g = 0, 2 (as at production), left at g = 1
            for x, sg, col in ((x1, v1, Q1), (x2, -v1, Q2)):                  # opposite velocities: v1 = -v2
                ax.add_patch(FancyArrowPatch((x, 0.16 if col == Q1 else -0.16), (x + 0.55 * sg, 0.16 if col == Q1 else -0.16), arrowstyle="-|>",
                                             mutation_scale=9, color=col, lw=1.3, ls="--"))
            ax.text(cx, 0.3, "v₁" + ("→" if v1 > 0 else "←") + "   " + ("←" if v1 > 0 else "→") + "v₂", ha="center", va="bottom", fontsize=8.5, color=fu.INK2)
        ax.plot([x1], [0], "o", ms=10, color=Q1, mec=fu.SURFACE, mew=1.5, zorder=5); ax.plot([x2], [0], "s", ms=9, color=Q2, mec=fu.SURFACE, mew=1.5, zorder=5)
        ax.text(cx, -0.85, lab, ha="center", va="top", fontsize=8.5, color=fu.INK)
    ax.add_patch(FancyArrowPatch((10.35, -0.5), (10.35, 0.5), arrowstyle="-|>", mutation_scale=12, color=EC, lw=2))
    ax.text(10.35, 0.62, "E* = γ v$_{cm}$ × B\n(constant)", ha="center", va="bottom", fontsize=8.5, color=fu.INK)
    ax.plot([], [], "o", color=Q1, ms=8, label="quirk 1 (+q)"); ax.plot([], [], "s", color=Q2, ms=8, label="quirk 2 (−q)")
    ax.legend(loc="upper left", fontsize=8.5, frameon=False, ncol=2, bbox_to_anchor=(0.0, 1.08))
    ax.set_title("(a) Conceptual sketch, not to scale (EM torque only): pair's rest (CM) frame, force qE* and torque τ = q d × E*\n     dashed arrows: velocities at the meetings",
                 fontsize=10, loc="left", pad=14)
    # ---- middle: d(g)
    a2 = fig.add_subplot(gs[1]); a2.plot(d.g, d.d_cm, color=fu.INK2, lw=1.8)
    a2.set_ylabel("d (cm)"); a2.set_xlim(0, 4.3); a2.set_ylim(0, 4.2); a2.tick_params(labelbottom=False)
    a2.set_title("(b) Numerical simulation: separation d, zero at every meeting g = 1, 2, 3, 4", fontsize=10, loc="left")
    # ---- bottom: L(g)
    a3 = fig.add_subplot(gs[2], sharex=a2); a3.plot(d.g, d.L_1e12_hbar, color=LC, lw=2)
    for k in range(4):
        a3.axvspan(k, k + 1, color=fu.SERIES[0] if k % 2 == 0 else fu.SERIES[1], alpha=0.07, lw=0)
        a3.text(k + 0.5, 0.80, "τ > 0: L rises" if k % 2 == 0 else "τ < 0: L falls", ha="center", fontsize=8.5, color=fu.INK2)
    for ax_ in (a2, a3):
        for k in range(1, 5): ax_.axvline(k, color=fu.MUTED, lw=0.8, ls="--")
    Lm = d.groupby(d.g.round(2)).L_1e12_hbar.mean()
    for k in range(5):
        v = float(np.interp(k, d.g, d.L_1e12_hbar)); a3.plot(k, v, "o", ms=8, color=fu.SERIES[2] if k % 2 == 0 else fu.SERIES[3], mec=fu.SURFACE, mew=1.5, zorder=5)
        a3.annotate(f"|L| = {v:.2f}", (k, v), xytext=(-62, 2) if k % 2 else (6, -16), textcoords="offset points", fontsize=8.5, color=fu.INK)
    a3.set_ylim(-0.24, 0.9); a3.set_xlabel("g = time in units of half an oscillation  (g = Λ²t / (2mρ), Eq. II.11)")
    a3.set_ylabel("|L| (10¹² ħ)"); a3.set_xticks([0, 1, 2, 3, 4]); a3.set_xticklabels(["0\n(n = 0)", "1", "2\n(n = 1)", "3", "4\n(n = 2)"])
    a3.set_title("(c) Numerical simulation: L rises by 0.64 in each odd half, falls by 0.64 in each even half;\nat every g = 2n it is back to its production value (invariant, Eq. A.4 → A.5)", fontsize=10, loc="left")
    return fig

fu.figure("F41_appendixA_diagram", src, plot,
          "How the angular momentum L of the quirk pair builds up and returns, compared with Appendix A of arXiv:2002.07503. "
          "(a) CONCEPTUAL SKETCH, not to scale and not simulation output: pair's rest frame, magnetic field acting as a constant field E* = γ v_cm × B, which pushes +q up "
          "and −q down. For 0 < g < 1 quirk 1 is on one side and the torque q d × E* is positive; after the quirks pass at g = 1, d points the other way and the torque "
          "has the same size and opposite sign. The sketch shows only this EM torque; the string term of Eq. 3 adds a smaller part (±0.09 of ±0.64 ×10¹² ħ) with the "
          "same sign pattern. At g = 0 and g = 2 the sketch shows the relation of Eq. A.5: z₁(2n) = −z₂(2n) = 0 with opposite velocities (head-on, as at production). "
          "Eq. A.5 says nothing about the odd meetings; there the quirks pass off-centre with the largest |L|. "
          "(b), (c) NUMERICAL SIMULATION of Eq. 3 with the Lorentz force for the event with the paper's kinematics (v* = 0.556, β_cm = 0.0975, charges ±2/3, 3000 RK4 steps "
          f"per period): d and |L| in the pair's rest frame vs g = r / {sp:.3f} cm (the spacing of the meetings). The simulated |L| is 0.64 ×10¹² ħ at g = 1, 3 and "
          "consistent with zero at g = 2, 4 (below 10⁻⁵ of the peak; the remaining value depends on the time step). The agreement of (c) with Eq. A.4–A.5 is the "
          "numerical result; the sketch in (a) only illustrates it.",
          [f"{T}/fig2_ours_constructed.csv"], "event with the paper's kinematics", S)
print("spacing", round(sp, 4), "meetings r", [round(m, 3) for m in mins])
