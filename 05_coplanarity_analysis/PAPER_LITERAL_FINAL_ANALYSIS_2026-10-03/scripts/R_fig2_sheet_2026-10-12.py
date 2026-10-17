#!/usr/bin/env python3
"""Fig. 2 summary sheet (2 pages, A4, matplotlib only): paper vs our Fig. 2, values table, equations vs paper, short analysis.
Every number is read or recomputed here from: tables/fig2_r_d_L_paper.csv, FINAL_FIGURES/F34_fig2_v4/F34_fig2_v4_source.csv,
tables/D16_fig2_four_checks.txt, tables/D17_fig2_torque_decomposition.txt, tables/D18_fig2_B0_string_test.txt, tables/D15_fig2_charge_axis_scan.txt.
Output: FIG2_SHEET_2026-10-12.pdf"""
import os, sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
L_ = os.path.abspath(f"{HERE}/.."); T = f"{L_}/tables"; OUT = f"{L_}/FIG2_SHEET_2026-10-12.pdf"; PNG = os.environ.get("SHEET_PNG")
INK, MUTED, RULE, HEAD = "#1b2328", "#5b6770", "#d5dbde", "#eef1f2"
CL, CD = fu.SERIES[0], fu.SERIES[1]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})

def minima(x, y):
    i = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1; res = []
    for k in i:
        x0, x1, x2 = x[k - 1:k + 2]; y0, y1, y2 = y[k - 1:k + 2]; den = (x0 - x1) * (x0 - x2) * (x1 - x2)
        A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den; B = (x2 ** 2 * (y0 - y1) + x1 ** 2 * (y2 - y0) + x0 ** 2 * (y1 - y2)) / den
        C = y1 - A * x1 ** 2 - B * x1; xv = -B / (2 * A) if A > 0 else x1
        res.append((xv, A * xv ** 2 + B * xv + C) if A > 0 else (x1, y1))
    return res
def summary(rL, L, rd, d):
    oL, od = np.argsort(rL), np.argsort(rd); rL, L, rd, d = rL[oL], L[oL], rd[od], d[od]
    s = rd <= 5.0; dm = [m for m in minima(rd[s], d[s]) if 0.05 < m[0] < 5]
    lz = [m for m in minima(rL[rL <= 5.0], L[rL <= 5.0]) if m[1] < 0.05 * L.max() and 0.05 < m[0] < 5]
    lz = [m for i, m in enumerate(lz) if i == 0 or m[0] - lz[i - 1][0] > 0.05]   # one zero per cusp (sampling can split a cusp)
    return dict(dmax=d[s].max(), spacing=np.mean(np.diff([m[0] for m in dm])), Lpk=L[rL <= dm[0][0] + 0.05].max(),
                Lapp=[float(np.interp(r, rL, L)) for r, _ in dm], rapp=[r for r, _ in dm], lz=[r for r, _ in lz])
p = pd.read_csv(f"{T}/fig2_r_d_L_paper.csv"); pd_ = p.dropna(subset=["d_cm"]); pl = p.dropna(subset=["L_1e12_hbar"])
S = {"paper": summary(pl.r_cm.values, pl.L_1e12_hbar.values, pd_.r_cm.values, pd_.d_cm.values)}
src = pd.read_csv(f"{L_}/FINAL_FIGURES/F34_fig2_v4/F34_fig2_v4_source.csv")
for key, ev in (("ours", "constructed"), ("key8", "COL2000 key 8")):
    e = src[src.event == ev]; S[key] = summary(e.r_cm.values, e.L_hbar.values / 1e12, e.r_cm.values, e.d_cm.values)
# signed change of L per half-oscillation (sign flipped at each zero of |L|)
def signed_steps(s, rL, L):
    o = np.argsort(rL); rL, L = rL[o], L[o]; sgn = lambda r: (-1) ** sum(z < r for z in s["lz"])
    v = [0.0] + [sgn(r) * np.interp(r, rL, L) for r in s["rapp"]]; return np.diff(v)
dP = signed_steps(S["paper"], pl.r_cm.values, pl.L_1e12_hbar.values)
e = src[src.event == "constructed"]; dO = [S["ours"]["Lapp"][0]] + [((-1) ** (i + 1)) * S["ours"]["Lapp"][0] for i in range(3)]
txt = lambda f: open(f"{T}/{f}").read()
D17 = txt("D17_fig2_torque_decomposition.txt"); D18 = txt("D18_fig2_B0_string_test.txt")

# Eq. 6 estimate for the constructed event (natural units)
e_, B_, m_, lam_, v_, vcm = 0.30282212, 2 * 1.9535e-16, 1800.0, 2e-6, 0.556, 0.0975
g_, gcm = 1 / np.sqrt(1 - v_ ** 2), 1 / np.sqrt(1 - vcm ** 2)
L6 = e_ * vcm * gcm * v_ * g_ * (g_ - 1) * m_ ** 2 * B_ / lam_ ** 4 / 1e12

def table(ax, rows, widths, fs=7.2, head=1, h=0.062):
    ax.axis("off"); t = ax.table(cellText=rows, colWidths=widths, loc="upper left", cellLoc="left")
    t.auto_set_font_size(False); t.set_fontsize(fs)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(RULE); cell.set_linewidth(0.5); cell.set_height(h); cell.PAD = 0.03
        if r < head: cell.set_facecolor(HEAD); cell.set_text_props(weight="bold", color=INK)
        else: cell.get_text().set_color(INK)
    return t
f2 = lambda xs: " / ".join(f"{x:.2f}" for x in xs)

with PdfPages(OUT) as pdf:
    # ---------- page 1: figure + values ----------
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor("white")
    fig.text(0.07, 0.965, "Fig. 2 of arXiv:1708.02243: paper vs this work", fontsize=14, weight="bold", color=INK)
    fig.text(0.07, 0.948, "Colored quirk, m_Q = 1.8 TeV, Λ = 2 keV, B = 2 T.  |L| and quirk separation d vs r (transverse radius of the CM).", fontsize=8, color=MUTED)
    gsp = fig.add_gridspec(2, 2, left=0.09, right=0.97, top=0.92, bottom=0.60, hspace=0.12, wspace=0.12)
    panels = [("PAPER (Fig. 2, digitised)", pl.r_cm, pl.L_1e12_hbar, pd_.r_cm, pd_.d_cm),
              ("THIS WORK (same kinematics as the paper's event)", e.r_cm, e.L_hbar / 1e12, e.r_cm, e.d_cm)]
    for j, (ttl, rl, Lv, rd, dv) in enumerate(panels):
        a1 = fig.add_subplot(gsp[0, j]); a2 = fig.add_subplot(gsp[1, j], sharex=a1)
        o = np.argsort(np.asarray(rl)); a1.plot(np.asarray(rl)[o], np.asarray(Lv)[o], color=CL, lw=1.8)
        o = np.argsort(np.asarray(rd)); a2.plot(np.asarray(rd)[o], np.asarray(dv)[o], color=CD, lw=1.6)
        key = "paper" if j == 0 else "ours"
        for r in S[key]["rapp"]:
            a1.axvline(r, color=RULE, lw=0.8, zorder=0); a2.axvline(r, color=RULE, lw=0.8, zorder=0)
        a1.plot(S[key]["rapp"], S[key]["Lapp"], "o", ms=5, color=CL, mec="white", mew=1.2, zorder=3)
        for r, v in zip(S[key]["rapp"], S[key]["Lapp"]): a1.annotate(f"{v:.2f}", (r, v), xytext=(3, 5), textcoords="offset points", fontsize=7, color=INK)
        a1.set_title(ttl, fontsize=8.5, color=INK, loc="left", weight="bold"); a1.set_ylim(0, 1.0); a2.set_ylim(0, 4.2); a1.set_xlim(0, 5)
        a1.tick_params(labelbottom=False); a2.set_xlabel("r (cm)")
        if j == 0: a1.set_ylabel("|L|  (10¹² ħ)"); a2.set_ylabel("d  (cm)")
        a1.grid(axis="y", color=RULE, lw=0.4); a2.grid(axis="y", color=RULE, lw=0.4)
    fig.text(0.09, 0.565, "Grey lines and dots: closest approaches (minima of d). Our curve: v* = 0.556, β_cm = 0.0975, charges ±2/3, 3000 RK4 steps per period.\n"
             "The paper does not give the event's initial conditions; v* and β_cm are read from its d curve (d max and spacing).", fontsize=7, color=MUTED, va="top")
    fig.text(0.07, 0.52, "Values", fontsize=11, weight="bold", color=INK)
    P_, O_, K_ = S["paper"], S["ours"], S["key8"]
    rows = [["Quantity", "Paper", "This work\n(same kinematics)", "This work\n(simulated event, key 8)"],
            ["d max (cm)", f"{P_['dmax']:.2f}", f"{O_['dmax']:.2f}", f"{K_['dmax']:.2f}"],
            ["Spacing of closest approaches in r (cm)", f"{P_['spacing']:.3f}", f"{O_['spacing']:.3f}", f"{K_['spacing']:.3f}"],
            ["First |L| peak (10¹² ħ)", f"{P_['Lpk']:.3f}", f"{O_['Lpk']:.3f}", f"{K_['Lpk']:.3f}"],
            ["|L| at closest approaches 1-4 (10¹² ħ)", f2(P_["Lapp"][:4]), f2(O_["Lapp"][:4]), f2(K_["Lapp"][:4])],
            ["r of closest approaches (cm)", f2(P_["rapp"][:4]), f2(O_["rapp"][:4]), f2(K_["rapp"][:4])],
            ["r where |L| = 0 (cm)", f2(P_["lz"]), f2(O_["lz"]), f2(K_["lz"])],
            ["Change of L per half-oscillation\n(signed, 10¹² ħ)", " / ".join(f"{x:+.2f}" for x in dP[:4]), " / ".join(f"{x:+.2f}" for x in dO), "±0.86 (all equal)"],
            ["Charges", "not stated", "±2/3", "±1"]]
    table(fig.add_axes([0.07, 0.17, 0.88, 0.335]), rows, [0.34, 0.22, 0.22, 0.22], fs=7.4, h=0.105)
    fig.text(0.07, 0.178, "Columns: same kinematics = event built from the paper's d curve (v* = 0.556, β_cm = 0.0975), charges ±2/3;\n"
             "simulated key 8 = event from our MadGraph + Pythia sample with the nearest kinematics, charges ±1.", fontsize=6.8, color=MUTED, va="top")
    fig.text(0.07, 0.140, "Matches: d max, spacing (both by construction for the middle column) and the first peak.\n"
             "Differs: after the first peak our |L| returns to 0 at every second closest approach; the paper's does not (0.19, 0.29).\n"
             "In the paper the half-oscillations of L are unequal (+0.65 / −0.84 / +0.71 / −0.80); in ours they are equal (±0.64).",
             fontsize=8, color=INK, va="top", linespacing=1.5)
    fig.text(0.07, 0.03, "Sources: tables/fig2_r_d_L_*.csv, FINAL_FIGURES/F34_fig2_v4; script scripts/R_fig2_sheet_2026-10-12.py", fontsize=6.5, color=MUTED)
    pdf.savefig(fig)
    if PNG: fig.savefig(f"{PNG}/page1.png", dpi=110)
    plt.close(fig)

    # ---------- page 2: equations + checks ----------
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor("white")
    fig.text(0.07, 0.965, "Equations used vs the paper", fontsize=14, weight="bold", color=INK)
    eq = [["Paper", "What", "In our code", "Same as paper?"],
          ["Eq. 3", r"$\frac{d}{dt}(m\gamma\mathbf{v}) = -\Lambda^2\left(\frac{\sqrt{1-v_\perp^2}}{v_\parallel}\mathbf{v}_\parallel + \frac{v_\parallel}{\sqrt{1-v_\perp^2}}\mathbf{v}_\perp\right) + \mathbf{F}_{\rm ext}$",
           "Same expression, term by term (RK4).\nv∥ = v·ŝ (signed, ŝ along the string),\nso v∥(vector)/v∥ = ŝ", "Yes"],
          ["Eq. 3, F_ext", "Lorentz force (+ material, Sec. II)", "q v × B, B = 2 T along z; no material", "Lorentz: yes. Material: neglected\nin the paper (Sec. II); none used"],
          ["Eq. 4", "d_cm(t): one quirk's distance from the CM\n(max (γ−1) m_Q/Λ²)", f"d = full separation = 2 d_cm\nd max {O_['dmax']:.3f} cm vs 2(γ−1)m_Q/Λ² = 3.607", "Yes"],
          ["Eq. 1", "Amplitude ~2 cm (γ−1)(m_Q/100 GeV)(keV/Λ)²", "1.80 cm per quirk (constructed event)", "Yes"],
          ["Eq. 5", "Torque τ ~ 2d × eE_cm,\nE_cm = γ_cm v_cm × B", "Exact CM-frame EM torque = q d × E_cm\nper half-oscillation (±0.556)", "Yes"],
          ["Eq. 6", "L ~ e v_cm γ_cm vγ(γ−1) m_Q² B/Λ⁴", f"Estimate {L6:.2f}×10¹² ħ; trajectory {O_['Lpk']:.2f}×10¹² ħ", "Same order\n(Eq. 6 is an estimate)"],
          ["Fig. 2", "L, d vs r of the CM", "L = d* × (p1* − p2*)/2 in the CM frame at\nequal CM time; d = |x1* − x2*|; r = CM radius", "Frame of L: paper does\nnot state; we used CM"],
          ["—", "Integrator, step size", "RK4, 3000 steps per oscillation period", "Paper does not state"]]
    table(fig.add_axes([0.06, 0.50, 0.88, 0.44]), eq, [0.08, 0.43, 0.29, 0.20], fs=6.6, h=0.105)
    fig.text(0.07, 0.47, "Checks done on our Fig. 2", fontsize=11, weight="bold", color=INK)
    checks = [
        "L definition: CM frame and three lab-frame definitions give the same |L| at closest approaches (0.64 / 0 / 0.64 / 0).",
        "Charges and oscillation axis: 7 charge sets × 5 axes. In every case |L| = 0 at every second closest approach.",
        "Code: the integrator's magnetic force is q v × B (checked numerically); CM momenta balance to 1e-16;",
        "     d max agrees with energy conservation.",
        "Signed L: L stays on one axis and touches 0; it never changes sign, so |L| is not hiding a sign flip.",
        "Torque per half-oscillation: change of L ±0.643 = EM torque ±0.556 + string torque ±0.087; residual < 1e-4.",
        "String torque at B = 0 (no EM torque): the quirks' L drops to 0.831 = 1/γ* at turning points and returns",
        "     to 1 at closest approaches, for v_cm = 0, 0.0975 and 0.3. It comes from the v∥v⊥ term of Eq. 3",
        "     (the string carries part of L): the same 0.643 when integrated directly in the CM frame.",
        "Scan: 7 definitions of L, 60 random charge / momentum configurations, 8 equation-of-motion variants: |L(2nd)|/|L(1st)| <= 0.012",
        "     (paper 0.30), except forward Euler (0.11 at 300 steps), which does not conserve energy (d max grows 3.6 -> 4.2 cm).",
    ]
    fig.text(0.07, 0.445, "\n".join(("•  " if not c.startswith("     ") else "   ") + c.strip() for c in checks), fontsize=7.8, color=INK, va="top", linespacing=1.65)
    fig.text(0.07, 0.235, "Result", fontsize=11, weight="bold", color=INK)
    res = ["With the paper's Eq. 3 and the Lorentz force, the torque in one half-oscillation is cancelled exactly in the next.",
           "No frame, charge set or axis we tried gives the paper's unequal half-oscillations (|L| 0.19 and 0.29 at the 2nd and 4th approach).",
           "The difference is not explained by anything stated in the paper.",
           "Annihilation: at every second closest approach our |L| is < 1e-5 of its peak (< 6e6 ħ at 100000 steps per period, not converged),",
           "i.e. L ≈ 0 where d ≈ 0. The paper states that |L| = 0 only at large separation, which suppresses annihilation. Neither the paper",
           "nor this work simulates annihilation.",
           "",
           "Questions for the authors:",
           "1. In Fig. 2, in which frame and about which point is L computed; does L include the string's share?",
           "2. What were the event's charges and initial momenta?",
           "3. Did the equation of motion contain anything besides Eq. 3 and the Lorentz force? (The paper and the thesis of J. Setford,\n    Sussex 2018, Ch. 5, state that material effects were neglected; the thesis repeats Fig. 2 without further detail.)"]
    fig.text(0.07, 0.21, "\n".join(res), fontsize=8.2, color=INK, va="top", linespacing=1.6)
    fig.text(0.07, 0.018, "Details: DECISIONS_LOG entries D17-D29; scripts D8, D15-D22 (tables/D15-D22_*.txt).", fontsize=6.5, color=MUTED)
    pdf.savefig(fig)
    if PNG: fig.savefig(f"{PNG}/page2.png", dpi=110)
    plt.close(fig)
print(OUT)
for k, v in S.items(): print(k, {kk: (np.round(vv, 3) if not isinstance(vv, list) else [round(x, 3) for x in vv]) for kk, vv in v.items()})
print("signed paper", np.round(dP, 3), "Eq6", round(L6, 3))
