#!/usr/bin/env python3
"""09 / G12 (2026-11-24): two physics checks on the G11 samples (Athena = Geant4 QuirkPheno_fix maxBoost 0.01; Eq. 3 = DOP853 as G07 D10).
(1) Plane rotation, paper Eq. 8: rotation of the plane spanned by the quirks' velocity vectors, normal n = v1 x v2 (= p1 x p2 / (E1 E2), same direction).
    Delta_phi(r) = angle between n at r and n at the reference (t = 0: the initial momenta; and the first layer, L1).
    Both codes, same estimator: n at a layer from the momenta of the two quirks at their crossings of that layer (Geant4 h_px; Eq. 3 interpolated
    at the crossing). r = layer radius; r = 15 cm by linear interpolation between L4 (12.25 cm) and L5 (29.9 cm).
    For Eq. 3 also the equal-time n(t) vs the transverse radius of the pair centre of mass (the paper's Fig. 3 axis), as a check of the estimator.
    Eq. 3 is re-integrated with the G07 D10 setup (same events, z0, rtol 1e-10, stop 25.05 ns); this is the same calculation, not a new sample.
(2) The events whose fitted plane differs by > 4 deg between the codes (G11, plane of the reco-used crossings through the vertex):
    pair beta*gamma (|P| / M of the pair), the quirk's CM-frame beta*gamma, the number of oscillations before the last-layer crossing
    (local minima of |x1 - x2| on the DOP853 output), the minimum pair separation, and the number of repeated layer crossings (order > 0).
Output: out_G01/G12_rotation.csv (per event and Lambda), out_G01/G12_tilt_events.csv; summaries printed. Run in env g4."""
import os, sys, json, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import G07_dt_impact as G7                                                   # noqa: E402
import uproot                                                                # noqa: E402
OUT = f"{HERE}/out_G01"; NS, CM = 6.582119569e-16, 1.973269804e-14
HALF = {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9}
TAGS = [("colored_1800gev", "2-4-7-10"), ("EW_800gev", "2-4-7-10"), ("EW_600gev", "4-5")]
RL = [3.325, 5.05, 8.85, 12.25, 29.9, 37.1, 44.3, 51.4]


def unit(v): n = np.linalg.norm(v); return v / n if n > 0 else v * np.nan
def ang(a, b): return float(np.arccos(min(1.0, abs(float(a @ b)))))
def at15(d):  # Delta_phi at 15 cm from L4 and L5
    return d[4] + (15.0 - RL[3]) / (RL[4] - RL[3]) * (d[5] - d[4]) if (4 in d and 5 in d) else np.nan


def eq3_one(a):
    tag, i, lam = a; g = G7.G; p4 = g.p4
    ev = EV[tag].iloc[i]; P1 = (ev.px1, ev.py1, ev.pz1, ev.E1); P2 = (ev.px2, ev.py2, ev.pz2, ev.E2)
    rng = np.random.default_rng(np.random.SeedSequence([6, int(g.MQ), i])); z0 = rng.normal(0.0, p4.R["beamspot_cm"])
    _, tr = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=g.MQ, Lambda_gev=lam * 1e-6, B_tesla=p4.R["B_tesla"], charge1=float(ev.charge1), charge2=float(ev.charge2),
                                       rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=p4.R["max_layer_r_cm"])
    t = tr["t_gev_inv"] * NS; X1, X2 = tr["x1"] * CM, tr["x2"] * CM; Pa, Pb = tr["p1"], tr["p2"]
    n0 = unit(np.cross(Pa[0], Pb[0]))
    # momenta of each quirk at its first crossing of each layer
    pc, tc, nrep = {}, {}, 0
    for q, X, P in ((1, X1, Pa), (2, X2, Pb)):
        r = np.hypot(X[:, 0], X[:, 1])
        for L, R in enumerate(RL, 1):
            w = np.nonzero(np.sign(r[1:] - R) != np.sign(r[:-1] - R))[0]
            if len(w) == 0: continue
            nrep += len(w) - 1; j = w[0]; f = (R - r[j]) / (r[j + 1] - r[j])
            pc[(q, L)] = P[j] + f * (P[j + 1] - P[j]); tc[(q, L)] = t[j] + f * (t[j + 1] - t[j])
    nl = {L: unit(np.cross(pc[(1, L)], pc[(2, L)])) for L in range(1, 9) if (1, L) in pc and (2, L) in pc}
    d0 = {L: ang(n, n0) for L, n in nl.items()}; d1 = {L: ang(n, nl[1]) for L, n in nl.items()} if 1 in nl else {}
    # equal-time estimator vs r of the pair CM (transverse)
    rc = np.hypot(0.5 * (X1[:, 0] + X2[:, 0]), 0.5 * (X1[:, 1] + X2[:, 1])); nt = np.cross(Pa, Pb); nt /= np.linalg.norm(nt, axis=1)[:, None]
    dt = np.arccos(np.minimum(1.0, np.abs(nt @ n0))); k = np.nonzero(rc >= 15.0)[0]
    eqt15 = float(dt[k[0]]) if len(k) else np.nan
    # oscillations, separation, before the last-layer crossing
    tL = max([tc[k_] for k_ in tc if k_[1] == 8], default=np.nan); m = t <= tL if tL == tL else np.ones(len(t), bool)
    sep = np.linalg.norm(X1 - X2, axis=1)[m]; lm = (sep[1:-1] < sep[:-2]) & (sep[1:-1] <= sep[2:]); nosc = int(np.sum(lm)) if len(sep) > 2 else 0
    mins = sep[1:-1][lm]                                                   # separation at the local minima (t = 0, both at the vertex, excluded)
    E = P1[3] + P2[3]; Pv = np.array(P1[:3]) + np.array(P2[:3]); M = np.sqrt(max(E * E - Pv @ Pv, 0))
    bg_pair = np.linalg.norm(Pv) / M; bg_int = np.sqrt(max((M / (2 * g.MQ)) ** 2 - 1, 0))     # CM-frame quirk beta*gamma at production
    return dict(sample=tag, event=i, lambda_keV=lam, eq3_d0_L4=d0.get(4), eq3_d0_L5=d0.get(5), eq3_d0_15=at15(d0), eq3_d1_15=at15(d1), eq3_eqtime_15=eqt15,
                bg_pair=bg_pair, bg_int=bg_int, n_osc=nosc, min_sep_um=1e4 * float(mins.min()) if len(mins) else np.nan, med_min_sep_um=1e4 * float(np.median(mins)) if len(mins) else np.nan,
                max_sep_um=1e4 * float(sep.max()) if len(sep) else np.nan, n_repeat_cross=nrep, t_L8_ns=tL)


def g4_dphi(tag, i, lam):
    T = uproot.open(f"{OUT}/G11/runs/F6_{tag}_e{i:04d}_L{lam:g}_mb0.01.root")["events"].arrays(library="np")
    p0 = {int(T["q_pdg"][0][j] < 0): np.array([T["q_px0"][0][j], T["q_py0"][0][j], T["q_pz0"][0][j]]) for j in range(2)}   # q 0 = positive PDG
    n0 = unit(np.cross(p0[0], p0[1])); pc = {}
    for j in np.argsort(T["h_t0"][0]):
        q, l = int(T["h_q"][0][j]), int(T["h_layer"][0][j])
        if (q, l) not in pc: pc[(q, l)] = np.array([T["h_px"][0][j], T["h_py"][0][j], T["h_pz"][0][j]])
    nl = {L: unit(np.cross(pc[(0, L)], pc[(1, L)])) for L in range(1, 9) if (0, L) in pc and (1, L) in pc}
    d0 = {L: ang(n, n0) for L, n in nl.items()}; d1 = {L: ang(n, nl[1]) for L, n in nl.items()} if 1 in nl else {}
    return dict(g4_d0_L4=d0.get(4), g4_d0_L5=d0.get(5), g4_d0_15=at15(d0), g4_d1_15=at15(d1))


EV = {}


def _init(tag, lams):
    G7._init(tag, lams, "D10")


if __name__ == "__main__":
    L = lambda p: {(r["event"], r["lambda_keV"]): r for l in open(p) for r in json.loads(l)}
    rows = []
    for tag, lams in TAGS:
        ev = pd.read_csv(f"{G7.G6}/../fig6/inputs/{tag}_events.csv"); sel = ev.trigger_proxy_pass.astype(str) == "True"
        if tag.startswith("colored"): sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
        EV[tag] = ev[sel].reset_index(drop=True)
        G, D = L(f"{OUT}/G11/{tag}_L{lams}_FG4mb01.jsonl"), L(f"{OUT}/G07/{tag}_L{lams}_FD10.jsonl")
        keys = sorted(k for k in D if D[k]["fid"] and G[k]["fid"])
        lv = [float(x) for x in lams.split("-")]
        with mp.Pool(6, initializer=_init, initargs=(tag, lv)) as P:
            R = P.map(eq3_one, [(tag, k[0], k[1]) for k in keys], chunksize=1)
        for k, r in zip(keys, R):
            r.update(g4_dphi(tag, k[0], k[1]))
            used = {(c[0], c[1]) for c in D[k]["first"] if c[5] < 25 and abs(c[4]) < HALF[c[1]]}
            pl = []
            for X in (G[k], D[k]):
                v = np.array([0, 0, X["z0"]]); A = np.array([np.array(c[2:5]) - v for c in X["first"] if (c[0], c[1]) in used])
                pl.append(np.linalg.svd(A, full_matrices=False)[2][-1])
            r["tilt_deg"] = np.degrees(ang(pl[0], pl[1])); r["Z1160_eq3"] = bool(D[k]["Z1160_final"]); r["Z1160_g4"] = bool(G[k]["Z1160_final"])
            rows.append(r)
        print(tag, "done", flush=True)
    T = pd.DataFrame(rows); T.to_csv(f"{OUT}/G12_rotation.csv", index=False)
    pd.set_option("display.width", 250)
    S = T.groupby(["sample", "lambda_keV"]).agg(n=("event", "size"), eq3_15=("eq3_d0_15", "median"), g4_15=("g4_d0_15", "median"), eq3_15_refL1=("eq3_d1_15", "median"),
                                                 g4_15_refL1=("g4_d1_15", "median"), eq3_eqtime_15=("eq3_eqtime_15", "median")).reset_index()
    for c in S.columns[3:]: S[c] = S[c] * 1e3
    print("\n(1) plane rotation Delta_phi at r = 15 cm, median over events fiducial in both, in mrad (ref t=0 unless noted)"); print(S.round(4).to_string(index=False))
    S.to_csv(f"{OUT}/G12_rotation_summary.csv", index=False)
    ew = T[T["sample"].str.startswith("EW")].copy(); ew["tilted"] = ew.tilt_deg > 4.0
    tl = ew[ew.tilted].sort_values("tilt_deg", ascending=False)
    tl[["sample", "event", "lambda_keV", "tilt_deg", "bg_pair", "bg_int", "n_osc", "min_sep_um", "med_min_sep_um", "max_sep_um", "n_repeat_cross", "t_L8_ns", "Z1160_eq3", "Z1160_g4"]].to_csv(f"{OUT}/G12_tilt_events.csv", index=False)
    print(f"\n(2) EW events with plane tilt > 4 deg: {len(tl)} of {len(ew)}"); print(tl[["sample", "event", "lambda_keV", "tilt_deg", "bg_pair", "bg_int", "n_osc", "min_sep_um", "med_min_sep_um", "max_sep_um", "n_repeat_cross", "t_L8_ns", "Z1160_eq3", "Z1160_g4"]].round(3).to_string(index=False))
    print("\nmedians, tilted vs the rest (EW)"); print(ew.groupby("tilted")[["bg_pair", "bg_int", "n_osc", "min_sep_um", "med_min_sep_um", "max_sep_um", "n_repeat_cross", "t_L8_ns"]].median().round(3).to_string())
    print("G12_EXIT=0")
