#!/usr/bin/env python3
"""Fig. 2 constructed event (2026-10-11): kinematics read from the paper's Fig. 2: internal speed v* = 0.556 (d max 3.6 cm), CM transverse speed
beta = 0.0975 along x (spacing 1.16 cm); 1800 GeV, 2 keV, B = 2 T along z, production at the origin. The oscillation axis is not given by the paper:
three directions are tried (along the boost x, transverse to it y, along the beam z). Charges +-1 (final-state R-hadrons) and +-2/3 (bare quirk).
L computed (a) in the exact CM frame, d* x (p1* - p2*)/2 at equal CM time (our standard, F22); (b) about the lab centre of energy,
sum (x_i - X_E) x p_i with X_E = sum E_i x_i / sum E_i, at equal lab time. Output: tables/D8_fig2_toy.csv (+ curves)."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T, MQ = f22.HB, f22.T, 1800.0; f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
VS, BETA = 0.556, 0.0975
def boost_x(E, p, b):
    g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
rows, curves = [], []
for axis_name, n in (("x (along boost)", [1, 0, 0]), ("y (transverse)", [0, 1, 0]), ("z (beam)", [0, 0, 1])):
    for q in (1.0, 2 / 3):
        n = np.array(n, float); gs = 1 / np.sqrt(1 - VS ** 2); ps = MQ * gs * VS; Es = MQ * gs
        E1, P1 = boost_x(Es, ps * n, BETA); E2, P2 = boost_x(Es, -ps * n, BETA)
        _, tr = f22.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=q, charge2=-q, rng=np.random.default_rng(0),
                                            z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
        t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
        e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
        t1, y1, _, q1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, q2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
        y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(t1[ok], t2, q2[:, k]) for k in range(3)])
        dv = y1[ok] - y2i; Lcm = np.linalg.norm(np.cross(dv, (q1[ok] - q2i) / 2), axis=1); d = np.linalg.norm(dv, axis=1) * HB
        gg = 1 / np.sqrt(1 - b @ b); tl = gg * (t1[ok] + ((y1[ok] + y2i) / 2) @ b); xc = (x1 + x2) / 2
        r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB   # lab CM radius at the lab time matching the CM-frame time (D12)
        XE = (e1[:, None] * x1 + e2[:, None] * x2) / (e1 + e2)[:, None]; Lce = np.linalg.norm(np.cross(x1 - XE, p1) + np.cross(x2 - XE, p2), axis=1)
        rl = np.hypot(*((x1 + x2)[:, :2] / 2 * HB).T); s = r <= 5.0; sl = rl <= 5.0
        mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1; mn = mn[(r[mn] > 0.05) & (r[mn] < 5)]
        Lz = np.where((Lcm[1:-1] < Lcm[:-2]) & (Lcm[1:-1] <= Lcm[2:]))[0] + 1; Lz = Lz[(r[Lz] > 0.05) & (r[Lz] < 5) & (Lcm[Lz] < 0.05 * Lcm[s].max())]
        rows.append(dict(axis=axis_name, charge=q, d_max=d[s].max(), spacing=np.diff(r[mn]).mean(), L_at_approaches=" / ".join(f"{Lcm[i]/1e12:.2f}" for i in mn),
                         L_zero_r=" / ".join(f"{r[i]:.2f}" for i in Lz), d_at_L_zero=" / ".join(f"{d[i]:.2f}" for i in Lz),
                         max_rel_diff_CoE_vs_CM=float(np.abs(np.interp(r[s], rl[sl][np.argsort(rl[sl])], Lce[sl][np.argsort(rl[sl])]) - Lcm[s]).max() / Lcm[s].max())))
        curves.append(pd.DataFrame(dict(axis=axis_name, charge=q, r_cm=r[s], L_cm_hbar=Lcm[s], d_cm=d[s])))
out = pd.DataFrame(rows); out.to_csv(f"{T}/D8_fig2_toy.csv", index=False); pd.concat(curves).to_csv(f"{T}/D8_fig2_toy_curves.csv", index=False)
pd.set_option("display.width", 250); print(out.to_string(float_format=lambda v: f"{v:.3g}"))
print("paper: d max 3.56, spacing 1.155, L at approaches 0.65 / 0.19 / 0.52 / 0.29, L zeros r = 1.91 / 2.67 / 4.10 at d = 3.2 / 3.1 / 3.5")
