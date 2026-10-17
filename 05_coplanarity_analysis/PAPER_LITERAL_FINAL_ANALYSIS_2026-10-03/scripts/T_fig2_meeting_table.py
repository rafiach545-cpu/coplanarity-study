#!/usr/bin/env python3
"""Fig. 2 detail tables (2026-10-16): (1) initial values of the two simulated events (constructed event with the paper's kinematics; COL2000 key 8),
with where each value comes from; (2) per meeting and per half-oscillation: r, d, |L|, signed change of L, impact parameter b = |L| / p*, for the paper's
curves and both simulated events. Inputs: tables/fig2_final/*.csv (curves), the COL2000 trigger-passing event file (key 8 momenta).
The paper's signed L is not given; its sign is taken to flip where |L| touches zero between meetings (r = 1.91, 2.67, 4.10 cm).
Output: tables/fig2_final/fig2_initial_values.csv, tables/fig2_final/fig2_meetings_detail.csv (printed)."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); F = f"{HERE}/../tables/fig2_final"
BASE = os.path.abspath(f"{HERE}/../../..")
HBC = 1.973269804e-14                       # hbar c in GeV cm
MQ, LAM, B = 1800.0, 2e-6, 2.0
L0 = MQ / LAM ** 2 * HBC                    # m / Lambda^2 in cm (8.88 cm)

def kin(P1, P2, E1, E2):
    """CM velocity, internal speed v*, gamma*, p* from lab four-momenta"""
    Ptot, Etot = P1 + P2, E1 + E2; b = Ptot / Etot; g = 1 / np.sqrt(1 - b @ b)
    def boost(E, p):
        bp = b @ p; return g * (E - bp), p + ((g - 1) * bp / (b @ b) - g * E) * b
    e1, p1 = boost(E1, P1); vs = np.linalg.norm(p1) / e1; gs = 1 / np.sqrt(1 - vs ** 2)
    return b, vs, gs, np.linalg.norm(p1), p1 / np.linalg.norm(p1)

# ---- constructed event (scripts/D8_fig2_toy_event.py): v* and beta read from the paper's d curve
VS, BETA = 0.556, 0.0975
gs = 1 / np.sqrt(1 - VS ** 2); ps, Es = MQ * gs * VS, MQ * gs; gb = 1 / np.sqrt(1 - BETA ** 2)
n = np.array([0, 0, 1.0])                   # oscillation axis along the beam (along the boost gives the same curve)
def bx(E, p): return gb * (E + BETA * p[0]), np.array([gb * (p[0] + BETA * E), p[1], p[2]])
E1c, P1c = bx(Es, ps * n); E2c, P2c = bx(Es, -ps * n)
pd_ = pd.read_csv(f"{F}/fig2_paper_d.csv")
dmax_paper = pd_.d_cm.max(); gs_from_paper = 1 + dmax_paper / (2 * L0)
# ---- key 8
M = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv").iloc[8]
P1k, P2k = np.array([M.px1, M.py1, M.pz1]), np.array([M.px2, M.py2, M.pz2])
bk, vsk, gsk, psk, nk = kin(P1k, P2k, M.E1, M.E2)
bc, vsc, gsc, psc, nc = kin(P1c, P2c, E1c, E2c)
rows = []
for name, P1, P2, E1, E2, q, b, vs, g_, p_, src in (
        ("constructed (paper's kinematics)", P1c, P2c, E1c, E2c, "+2/3, −2/3", bc, vsc, gsc, psc,
         f"v* from paper's d max {dmax_paper:.3f} cm and spacing via Eq. 4 (γ* = 1 + d_max Λ²/(2m) = {gs_from_paper:.4f} → v* ≈ 0.55; 0.556 used); "
         "β_cm from the r-spacing of the meetings (1.155 cm); axis along the beam; charges: bare quirk ±2/3 (paper does not state)"),
        ("COL2000 key 8 (our sample)", P1k, P2k, M.E1, M.E2, f"{M.charge1:+.0f}, {M.charge2:+.0f}", bk, vsk, gsk, psk,
         "MadGraph 3.7.3 + Pythia 8.317 colored sample (trigger-passing event file, row 8); chosen because its d max and spacing are nearest the paper's; "
         "charges of the final-state R-hadrons")):
    rows.append(dict(event=name, m_GeV=MQ, Lambda_keV=LAM * 1e6, B_T=B, charges=q,
                     p1_lab_GeV=" , ".join(f"{x:.1f}" for x in P1), p2_lab_GeV=" , ".join(f"{x:.1f}" for x in P2), E1_GeV=round(E1, 1), E2_GeV=round(E2, 1),
                     beta_cm=" , ".join(f"{x:.4f}" for x in b), beta_cm_T=round(float(np.hypot(b[0], b[1])), 4), v_star=round(vs, 4), gamma_star=round(g_, 4),
                     p_star_GeV=round(p_, 1), dmax_pred_cm=round(2 * (g_ - 1) * L0, 3), source=src))
IV = pd.DataFrame(rows); IV.to_csv(f"{F}/fig2_initial_values.csv", index=False)

# ---- meetings and half-oscillations
def meet_table(r_L, L, r_d, d, p_star, signed_flip_r=None, name=""):
    o = np.argsort(r_d); r_d, d = r_d[o], d[o]; o = np.argsort(r_L); r_L, L = r_L[o], L[o]
    mi = [i for i in range(1, len(d) - 1) if d[i] <= d[i - 1] and d[i] < d[i + 1] and d[i] < 0.1 * d.max() and 0.2 < r_d[i] < 5]
    rm = [0.0] + [float(r_d[i]) for i in mi]
    Lm = [float(np.interp(x, r_L, L)) for x in rm]
    if signed_flip_r is not None:            # paper: sign flips at each zero of |L| between meetings
        sg = [(-1) ** sum(1 for z in signed_flip_r if z < x) for x in rm]; Ls = [a * s for a, s in zip(Lm, sg)]
    else:
        Ls = Lm                              # ours: L stays on one side (touches 0)
    out = []
    for k in range(1, len(rm)):
        seg = (r_L > rm[k - 1] + 0.05) & (r_L <= rm[k] - 0.05); segw = (r_L > rm[k - 1] + 0.3 * (rm[k] - rm[k - 1])) & (r_L <= rm[k] + 0.3 * (rm[k] - rm[k - 1])); segd = (r_d > rm[k - 1]) & (r_d <= rm[k])
        zr = [float(r_L[i]) for i in range(1, len(L) - 1) if seg[i] and L[i] <= L[i - 1] and L[i] < L[i + 1] and L[i] < 0.05 * L.max()]
        out.append(dict(event=name, meeting=k, r_meeting_cm=round(rm[k], 3), d_at_meeting_cm=round(float(d[mi[k - 1]]), 3),
                        L_abs_at_meeting=round(Lm[k], 3), L_signed_at_meeting=round(Ls[k], 3), dL_this_half=round(Ls[k] - Ls[k - 1], 3),
                        d_max_this_half_cm=round(float(d[segd].max()), 3), 
                        r_L_zero_between_cm=" / ".join(f"{x:.2f}" for x in zr) if zr else "—",
                        b_cm=float(Lm[k] * 1e12 * HBC / p_star), b_over_inv_m=float(Lm[k] * 1e12 * HBC / p_star / (HBC / MQ))))
    return out
pL = pd.read_csv(f"{F}/fig2_paper_L.csv"); oc = pd.read_csv(f"{F}/fig2_ours_constructed.csv"); ok = pd.read_csv(f"{F}/fig2_ours_key8.csv")
oc, ok = oc[oc.r_cm <= 5], ok[ok.r_cm <= 5]
rows = meet_table(pL.r_cm.values, pL.L_1e12_hbar.values, pd_.r_cm.values, pd_.d_cm.values, psc, signed_flip_r=[1.91, 2.67, 4.10], name="paper")
rows += meet_table(oc.r_cm.values, oc.L_1e12_hbar.values, oc.r_cm.values, oc.d_cm.values, psc, name="constructed")
rows += meet_table(ok.r_cm.values, ok.L_1e12_hbar.values, ok.r_cm.values, ok.d_cm.values, psk, name="key 8")
MT = pd.DataFrame(rows); MT.to_csv(f"{F}/fig2_meetings_detail.csv", index=False)
pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 200)
print(IV.T.to_string()); print(); print(MT.to_string(float_format=lambda v: f"{v:.3g}"))
print(f"\nm/Lambda^2 = {L0:.3f} cm; 1/m = {HBC / MQ:.2e} cm")
