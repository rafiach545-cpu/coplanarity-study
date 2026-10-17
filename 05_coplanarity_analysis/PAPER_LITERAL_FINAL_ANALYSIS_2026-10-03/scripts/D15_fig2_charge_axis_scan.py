#!/usr/bin/env python3
"""Fig. 2 constructed event (D20 kinematics): charge assignments x oscillation axes, CM-frame |L| at closest approaches and |L| zeros (2026-10-12).
Output printed; saved in tables/D15_fig2_charge_axis_scan.txt."""
import sys, numpy as np
S = "/home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"; sys.path.insert(0, S)
import F22_dynamics_v2 as f22
HB, MQ = f22.HB, 1800.0; f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
VS, BETA = 0.556, 0.0975
def boost_x(E, p, b):
    g = 1/np.sqrt(1-b*b); return g*(E+b*p[0]), np.array([g*(p[0]+b*E), p[1], p[2]])
def run(n, q1, q2):
    n = np.array(n, float); n /= np.linalg.norm(n); gs = 1/np.sqrt(1-VS**2); ps = MQ*gs*VS; Es = MQ*gs
    E1, P1 = boost_x(Es, ps*n, BETA); E2, P2 = boost_x(Es, -ps*n, BETA)
    _, tr = f22.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=q1, charge2=q2, rng=np.random.default_rng(0),
                                        z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((p1**2).sum(1)+MQ*MQ); e2 = np.sqrt((p2**2).sum(1)+MQ*MQ); b = (p1[0]+p2[0])/(e1[0]+e2[0])
    t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); k2i = np.column_stack([np.interp(t1[ok], t2, k2[:, k]) for k in range(3)])
    dv = y1[ok]-y2i; L = np.linalg.norm(np.cross(dv, (k1[ok]-k2i)/2), axis=1)/1e12; d = np.linalg.norm(dv, axis=1)*HB
    gg = 1/np.sqrt(1-b@b); tl = gg*(t1[ok]+((y1[ok]+y2i)/2)@b); xc = (x1+x2)/2
    r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1]))*HB; s = r <= 5
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0]+1; mn = mn[(r[mn] > 0.05) & (r[mn] < 5)]
    Lz = np.where((L[1:-1] < L[:-2]) & (L[1:-1] <= L[2:]))[0]+1; Lz = Lz[(r[Lz] > 0.05) & (r[Lz] < 5) & (L[Lz] < 0.05*L[s].max())]
    return " / ".join(f"{L[i]:.2f}" for i in mn), " / ".join(f"{r[i]:.2f}" for i in Lz), d[s].max()
for nm, n in (("x", [1,0,0]), ("z", [0,0,1]), ("y", [0,1,0]), ("xz45", [1,0,1]), ("yz45", [0,1,1])):
    for q1, q2 in ((2/3, -2/3), (1, -1), (1, 0), (0, -1), (1, -1/3), (2/3, -1/3), (1/3, -1/3)):
        a, z, dm = run(n, q1, q2); print(f"axis {nm:5s} q=({q1:+.2f},{q2:+.2f}) dmax={dm:.2f}  L@approach={a}  L-zeros r={z}", flush=True)
print("paper: L@approach 0.65 / 0.19 / 0.52 / 0.29 ; zeros r = 1.91 / 2.67 / 4.10")
