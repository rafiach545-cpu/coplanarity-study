#!/usr/bin/env python3
"""Checks with the analytic results of arXiv:2002.07503 (Li, Li, Pei, Zhang, "The quirk trajectory") and arXiv:1911.02223, applied to our
fiducial events of COL2000 / EW2000 (2026-10-14). Kinematics from the production momenta; uniform B = 2 T (ours, ATLAS) instead of 4 T (CMS).
1. Belt width L (Eq. III.1): L = 2 R / rho * l_c, R = k1 k2 sin(alpha) / sqrt(k1^2 + k2^2 + 2 k1 k2 cos alpha), k_i = |P_i| / m,
   rho = sqrt(((E1 + E2)^2 - (P1 + P2)^2) / (4 m^2) - 1) (Eq. II.10), l_c = (sqrt(1 + rho^2) - 1) m / Lambda^2. Compared with our Delta_w
   (tables/all_crossings_per_event.csv, mode FIRST, SCT z none, plane found).
2. Repeated crossings (Sec. VI, App. D): D = 2 m rho beta_o / (Lambda^2 sqrt(1 - beta_o^2)) (Eq. VI.1), D' = D sin(theta), L' = L cos(phi)
   (theta, phi: Eq. II.22-23). App. D: > 2 hits on a layer of radius R when D' < R < L' (or R >> L'). Prediction for our 8 layers compared with
   the observed max hits per layer > 2 (mode ALL).
3. Truth plane thickness: plane fitted (tensor about the true vertex) to the 16 exact first crossings (no resolution, no quantisation), compared
   with 1911.02223 Eq. III.12, d ~ 1.16 um (m/100 GeV)(keV/Lambda)^4 |q| B_xy/T (B_xy = |B - (B.n) n|, n = fitted normal), and with
   2002.07503 Eq. V.6, d^2 ~ (C1 + 4/15) d_E^2 + 8/45 d_B^2, d_E = 2 m q E_z rho asinh(rho) / Lambda^4 (V.8), d_B = 2 m q B_c (rho - atan rho) / Lambda^4 (V.9),
   E_z, B_c from Eq. II.15-16, C1 = (1/(3 l0)) sum_i (j - [i/2])^2, j = (1/l0) sum_i [i/2], l0 = number of periods in the tracker (Eq. IV.1 with the
   ATLAS barrel: R_max = 51.4 cm, |Z_max| = 74.9 cm) and t_p from Eq. II.8.
Output: tables/D29_li_pei_formulas.csv (per event), printed summary."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
HB, E_NAT, T2G, C = 1.973269804e-14, 0.30282212, 1.9535e-16, 29.9792458
BASE = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events"
SAMP = {"COL2000": ("colored_1800GeV_L2keV", 1800.0, 2e-6), "EW2000": ("EW_800GeV_L4keV", 800.0, 4e-6)}
RAD = [3.325, 5.05, 8.85, 12.25, 29.9, 37.1, 44.3, 51.4]
ac = pd.read_csv(f"{T}/all_crossings_per_event.csv"); TR = lambda s: s.astype(str) == "True"
ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); rows = []
for s, (tag, m, lam) in SAMP.items():
    M = pd.read_csv(f"{BASE}/{tag}/trigger_passing_events.csv")
    first = ac[(ac["sample"] == s) & (ac["mode"] == "FIRST") & (ac.sct == "Z0") & TR(ac.fid)].set_index("key")
    allm = ac[(ac["sample"] == s) & (ac["mode"] == "ALL") & (ac.sct == "Z0") & TR(ac.fid)].set_index("key")
    for k, f in first.iterrows():
        r = M.iloc[int(k)]; P1 = np.array([r.px1, r.py1, r.pz1]); P2 = np.array([r.px2, r.py2, r.pz2]); q = abs(float(r.charge1))
        E1, E2 = np.sqrt(P1 @ P1 + m * m), np.sqrt(P2 @ P2 + m * m); Po = P1 + P2; Eo = E1 + E2
        rho = np.sqrt((Eo ** 2 - Po @ Po) / (4 * m * m) - 1); k1, k2 = np.linalg.norm(P1) / m, np.linalg.norm(P2) / m
        ca = P1 @ P2 / (np.linalg.norm(P1) * np.linalg.norm(P2)); al = np.arccos(np.clip(ca, -1, 1))
        Rf = k1 * k2 * np.sin(al) / np.sqrt(k1 ** 2 + k2 ** 2 + 2 * k1 * k2 * ca); lc = (np.sqrt(1 + rho ** 2) - 1) * m / lam ** 2 * HB
        Lw = 2 * Rf / rho * lc; bo = Po / Eo; b = np.linalg.norm(bo)
        D = 2 * m * rho * b / (lam ** 2 * np.sqrt(1 - b * b)) * HB
        delta = Po[2] / np.linalg.norm(Po); th = np.arccos(delta) if delta >= 0 else np.pi - np.arccos(delta)
        cr = np.cross(P1, P2); cz = np.cross(Po, [0, 0, 1.0]); psi = cr @ cz / (np.linalg.norm(cr) * np.linalg.norm(cz))
        ph = np.pi / 2 - np.arccos(psi) if delta >= 0 else np.arccos(psi) - np.pi / 2
        Lp, Dp = Lw * np.cos(ph), D * np.sin(th)
        pred_multi = any(Dp < R_ < Lp for R_ in RAD)
        # truth plane thickness from the exact first crossings (vertex-relative)
        e = ex[(ex["sample"] == s) & (ex.key == k) & TR(ex.crossed)]
        X = np.column_stack([e.x, e.y, e.z_lab - f.z0_cm]); Tn = X.T @ X / (len(X) - 1); w, v = np.linalg.eigh(Tn); n = v[:, 0]
        ds_truth = np.sqrt(max(w[0], 0)); B = np.array([0, 0, 2.0]); Bxy = np.linalg.norm(B - (B @ n) * n)
        d_1911 = 1.16e-4 * (m / 100) * (1e-6 / lam) ** 4 * q * Bxy                      # cm
        # 2002.07503 Eq. V.6
        ey = bo / b; xp = P1 - (P1 @ ey) * ey; ex_ = xp / np.linalg.norm(xp); Bn = np.array([0, 0, 2.0 * T2G]); qn = q * E_NAT
        Ez = -b * (Bn @ ex_) / np.sqrt(1 - b * b)
        Bc = ((1 - b * b) * (P1 @ ex_) * (Bn @ ey) - (P1 @ ey - b * E1) * (Bn @ ex_)) / (m * rho * (1 - b * b))
        dE = abs(2 * m * qn * Ez * rho * np.arcsinh(rho) / lam ** 4) * HB; dB = abs(2 * m * qn * Bc * (rho - np.arctan(rho)) / lam ** 4) * HB
        # l0 from Eq. IV.1 with t_p from Eq. II.8 (rho1 - rho2 and h from the lab-frame decomposition of Sec. II A)
        exl = P1 / E1 - P2 / E2; exl /= np.linalg.norm(exl); r1, r2 = P1 @ exl / m, P2 @ exl / m
        eyl = P1 - (P1 @ exl) * exl; eyl /= np.linalg.norm(eyl); hh = P1 @ eyl / E1
        tp = 0.0658 * (r1 - r2) / np.sqrt(1 - hh * hh) * (m / 100) * (1e-6 / lam) ** 2       # ns
        bz = abs(bo[2]); bT = np.hypot(bo[0], bo[1]); Rmax_ns, Zmax_ns = 51.4 / C, 74.9 / C
        nT = (min(25, Zmax_ns / bz) if bz / bT >= 74.9 / 51.4 else min(25, Rmax_ns / bT)) / tp; l0 = max(1, int(round(nT)))
        i = np.arange(1, l0 + 1); jl = np.mean(i // 2); C1 = np.sum((jl - i // 2) ** 2) / (3 * l0)
        d_2002 = np.sqrt((C1 + 4 / 15) * dE ** 2 + 8 / 45 * dB ** 2)
        a = allm.loc[k]
        rows.append(dict(sample=s, key=int(k), rho=rho, l_c_cm=lc, L_belt_cm=Lw, D_cm=D, Lprime_cm=Lp, Dprime_cm=Dp, pred_multi=pred_multi,
                         obs_multi=bool(a.max_hits_per_layer > 2), plane=TR(pd.Series([f.plane])).iloc[0], dw_cm=f.dw, ds_meas_cm=f.ds,
                         ds_truth_um=ds_truth * 1e4, d_1911_um=d_1911 * 1e4, d_2002_um=d_2002 * 1e4, nT=nT, l0=l0, dE_um=dE * 1e4, dB_um=dB * 1e4))
d = pd.DataFrame(rows); d.to_csv(f"{T}/D29_li_pei_formulas.csv", index=False)
pd.set_option("display.width", 220)
for s, x in d.groupby("sample"):
    p = x[x.plane]
    print(f"\n== {s}: {len(x)} fiducial events")
    print(f"1. belt width L (III.1): median {x.L_belt_cm.median():.3f} cm [16-84%: {x.L_belt_cm.quantile(.16):.3f}-{x.L_belt_cm.quantile(.84):.3f}]; "
          f"our Delta_w median {p.dw_cm.median():.3f} cm; Delta_w / L median {np.median(p.dw_cm / p.L_belt_cm):.3f}; "
          f"Spearman(Delta_w, L) = {p[['dw_cm', 'L_belt_cm']].corr('spearman').iloc[0, 1]:.2f}; rho median {x.rho.median():.3f}")
    tp_ = (x.pred_multi & x.obs_multi).sum(); fp = (x.pred_multi & ~x.obs_multi).sum(); fn = (~x.pred_multi & x.obs_multi).sum(); tn = (~x.pred_multi & ~x.obs_multi).sum()
    print(f"2. repeated crossings: predicted (D' < R < L' for a layer) {int(x.pred_multi.sum())}, observed {int(x.obs_multi.sum())}; "
          f"both {tp_}, predicted only {fp}, observed only {fn}, neither {tn}; L' median {x.Lprime_cm.median():.2f} cm, D' median {x.Dprime_cm.median():.2f} cm")
    print(f"3. truth plane thickness (exact crossings): median {x.ds_truth_um.median():.2f} um [16-84%: {x.ds_truth_um.quantile(.16):.2f}-{x.ds_truth_um.quantile(.84):.2f}]; "
          f"1911 Eq. III.12: {x.d_1911_um.median():.2f} um; 2002 Eq. V.6: {x.d_2002_um.median():.2f} um (d_E {x.dE_um.median():.2f}, d_B {x.dB_um.median():.2f}, l0 {x.l0.median():.0f}); "
          f"measured Delta_s (pixel centres, SCT r-phi 34 um, no SCT z) median {p.ds_meas_cm.median() * 1e4:.1f} um")
