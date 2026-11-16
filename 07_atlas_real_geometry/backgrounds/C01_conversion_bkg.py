#!/usr/bin/env python3
"""07 background step C01 (2026-11-15, decision D3 step 1): Z(nunu)+gamma+j converted photons + pile-up through the 07 detector.

Usage: C01_conversion_bkg.py <geom: stage2|atlas> <mu> [--material on|off] [--sct Z0|Z1160|A580|both] [--first N] [--workers K] [--tag T]
Photons: 06_publication/S2_.../inputs/zgamma_13p6TeV/zgamma_photons.csv (9130, MET > 200 GeV, as Stage 2). Pile-up pool: the 13.6 TeV
minimum-bias pool of Stage 2 (inputs/minbias_pool_20000_13p6TeV.csv, ancestry-labelled, track suppression Loose).
Per photon i (same seeds as Stage 2 P17b_overlay_ref34): rng = SeedSequence([99, 1708, i]) -> z0 ~ N(0, 4.5 cm), then 16 normals (Stage 2 SCT
draws); pile-up streams SeedSequence([90210777, i]).spawn(2). Equal energy sharing, collinear e+ e- (R10).
geom = stage2 (validation): barrel only, conversion at the beam pipe (r = 2.35 cm, find_conversion_point), weight = Stage 2 flat 1%,
  electrons with propagate_stage2 (= Stage 2 track34), pile-up with the Stage 2 helix constant; must reproduce Stage 2 event by event (T05).
geom = atlas (production): barrel + end-caps (detsim07.build('atlas')), conversion on material surface k of the photon's straight path
  (k = 0 beam pipe r = 2.35 cm, k = 1, 2 the first two silicon elements; decision D2) with weight P_k = prod_{j<k} exp(-7 t_j / 9) (1 - exp(-7 t_k / 9)),
  t = (x/X0) / |cos alpha| (07 material table); elements up to and including the conversion surface are not hit by the pair; general propagate()
  (barrel + disks, material after each hit); SCT normals for the pair from SeedSequence([99, 1708, i, 10 + body]); pile-up |eta| < 2.5
  reconstruction acceptance for the track suppression (R14); COP with stations (cop07, D1).
Both SCT settings use common random numbers (detsim07.resmear). Fit origin: the primary vertex (0, 0, z0).
Output: runs/C01_<geom>_<tag>_mu<mu>/chunk_<start>.csv (resumable) with one row per (photon, region, sct)."""
import os, sys, math, time, argparse, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, f"{ROOT}/sim")
import detsim07 as D, cop07                                                        # noqa: E402
from pileup_hits_suppressed import build_ancestry_pool_index                       # noqa: E402
from convert_and_analyze import find_conversion_point, PER_EVENT_XSEC_PB            # noqa: E402
S2 = "/home/rafia/coplanarity_study/06_publication/S2_13p6TeV_run3_knapen_noPU_cop"
PHF, POOLF = f"{S2}/inputs/zgamma_13p6TeV/zgamma_photons.csv", f"{S2}/inputs/minbias_pool_20000_13p6TeV.csv"
PU_SEED, CHUNK = 90210777, 50
A = None; PH = POOL = ELS = None; BP_X0 = None


def _init(args):
    global A, PH, POOL, ELS, BP_X0
    A = args; PH = pd.read_csv(PHF); POOL = build_ancestry_pool_index(pd.read_csv(POOLF)); ELS = D.build(A.geom)
    M = pd.read_csv(f"{ROOT}/geometry/atlas_run2_id_material.csv").set_index("component"); BP_X0 = float(M.loc["beam_pipe_Be_wall", "x_over_X0_normal_incidence"])


def regions_atlas(r, z0):
    """Material surfaces along the photon's straight path from (0,0,z0): [(name, point, t, element or None)], path ordered (beam pipe first)."""
    p = np.array([r.px, r.py, r.pz]); u = p / np.linalg.norm(p); st = math.hypot(u[0], u[1]); out = []
    if st > 1e-9: out.append((0.0 + 2.35 / st, "BP", np.array([0, 0, z0]) + u * 2.35 / st, BP_X0 / st, None))
    for e in ELS:
        if e["kind"] == "barrel":
            if st <= 1e-9: continue
            L = e["r_cm"] / st; pt = np.array([0, 0, z0]) + u * L
            if abs(pt[2]) < e["half_cm"]: out.append((L, e["name"], pt, e["x0"] / st, e))
        else:
            if u[2] == 0: continue
            L = (e["z_cm"] - z0) / u[2]
            if L <= 0: continue
            pt = np.array([0, 0, z0]) + u * L
            if e["rmin_cm"] <= math.hypot(pt[0], pt[1]) <= e["rmax_cm"]: out.append((L, e["name"], pt, e["x0"] / abs(u[2]), e))
    out.sort(key=lambda t: t[0]); res, surv = [], 1.0
    for L, nm, pt, t, e in out:
        pk = surv * (1 - math.exp(-7 * t / 9)); res.append((nm, pt, pk, e, L)); surv *= math.exp(-7 * t / 9)
    return res


def pair_hits(cp, p, i, gS2, els_pair, sct):
    """Raw hits of the e+ e- pair from conversion point cp (cm), photon momentum p (GeV), equal sharing."""
    raw = []
    for body, q in ((0, -1.0), (1, 1.0)):
        if A.geom == "stage2":
            cr = D.propagate_stage2(cp, p / 2.0, q, D.ME, els_pair, material=A.material)
            for e, x, y, z, t in cr:
                if abs(z) >= e["half_cm"]: continue                                 # Stage 2 acceptance on the hit (geometry B)
                idx = [k for k, ee in enumerate(ELS) if ee is e][0]
                g1, g2 = (gS2[body, idx - 4] if not e["is_pixel"] else (0.0, 0.0))
                raw.append(D.respond(e, x, y, z, t, f"conv_e{body}", g1, g2, sct))
        else:
            rg = np.random.default_rng(np.random.SeedSequence([99, 1708, i, 10 + body]))
            for e, x, y, z, t in D.propagate(cp, p / 2.0, q, D.ME, els_pair, material=A.material):
                g1, g2 = (rg.standard_normal(2) if not e["is_pixel"] else (0.0, 0.0))
                raw.append(D.respond(e, x, y, z, t, f"conv_e{body}", g1, g2, sct))
    return raw


def event(i):
    r = PH.iloc[i]; rng = np.random.default_rng(np.random.SeedSequence([99, 1708, i])); z0 = rng.normal(0.0, 4.5)
    gS2 = rng.standard_normal(16).reshape(2, 4, 2); p = np.array([r.px, r.py, r.pz]); scts = ("Z0", "Z1160") if A.sct == "both" else (A.sct,)
    base = dict(event=i, mu=A.mu, z0_cm=z0, sigma_evt_pb=PER_EVENT_XSEC_PB)
    if A.geom == "stage2":
        cp = find_conversion_point(r.px, r.py, r.pz, r.E, z0, 2.35)
        regs = [] if cp is None else [("BP", cp, 0.01, None, 0.0)]
    else:
        regs = regions_atlas(r, z0)[:3]
    if not regs: return [dict(base, status="no_conversion_point")]
    c1, c2 = np.random.SeedSequence([PU_SEED, i]).spawn(2)
    pu, st = D.pileup_hits(ELS, POOL, A.mu, np.random.default_rng(c1), np.random.default_rng(c2), scts[0],
                           eta_max_reco=None if A.geom == "stage2" else 2.5, rc=D.RC_STAGE2_PU if A.geom == "stage2" else D.RC_EXACT)
    rows = []
    for k, (nm, cp, pk, e_conv, L) in enumerate(regs):
        if e_conv is None: els_pair = ELS
        else:                                                                         # elements crossed before / at the conversion are not hit
            before = {n for n, *_ in regs[:k + 1]}; els_pair = [e for e in ELS if e["name"] not in before]
        raw = pair_hits(np.array(cp, float), p, i, gS2, els_pair, scts[0])
        merged0, ms = D.overlay(raw, pu)
        for sct in scts:
            merged = merged0 if sct == scts[0] else D.resmear(merged0, sct)
            res, w = cop07.analyse(merged, (0.0, 0.0, z0), ELS)
            anc = {"conv": 0, "pileup": 0, "mixed": 0}
            if w:
                look = {(h["x"], h["y"], h["z"] - z0): h for h in merged}
                for pt in w["hits"]:
                    h = look.get((pt[0], pt[1], pt[2])); src = [str(s) for s in (h.get("source_quirk_indices", [h["quirk_index"]]) if h else [])]
                    c = any(s.startswith("conv") for s in src); u = any(s.startswith("pu") for s in src); anc["mixed" if (c and u) else "conv" if c else "pileup"] += 1
            rows.append(dict(base, status="ok", region=k, region_element=nm, conv_r_cm=float(math.hypot(cp[0], cp[1])), conv_z_cm=float(cp[2]),
                             p_conv=pk, sct=sct, n_conv_hits_raw=len(raw), n_pu_interactions=st["n_pu_interactions"], n_pu_hits_raw=len(pu),
                             n_hits_merged=len(merged), **res, winner_conv_hits=anc["conv"], winner_pileup_hits=anc["pileup"], winner_mixed_hits=anc["mixed"]))
    return rows


def chunk_job(start):
    rows = []
    for i in range(start, min(start + CHUNK, len(PH), A.first or 10 ** 9)): rows += event(i)
    return start, rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("geom", choices=["stage2", "atlas"]); ap.add_argument("mu", type=float)
    ap.add_argument("--material", default="on", choices=["on", "off"]); ap.add_argument("--sct", default="both", choices=["Z0", "Z1160", "A580", "both"])
    ap.add_argument("--first", type=int, default=0); ap.add_argument("--workers", type=int, default=10); ap.add_argument("--tag", default="")
    a = ap.parse_args(); a.material = a.material == "on"
    n = len(pd.read_csv(PHF)); n = min(n, a.first) if a.first else n
    outd = f"{HERE}/runs/C01_{a.geom}{'_' + a.tag if a.tag else ''}_mu{a.mu:g}"; os.makedirs(outd, exist_ok=True)
    todo = [s for s in range(0, n, CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
    print(f"C01 {a.geom} mu={a.mu} material={a.material} sct={a.sct} photons={n} chunks to run {len(todo)} -> {outd}", flush=True); t0 = time.time()
    with mp.Pool(a.workers, initializer=_init, initargs=(a,)) as pool:
        for k, (start, rows) in enumerate(pool.imap_unordered(chunk_job, todo), 1):
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"; pd.DataFrame(rows).to_csv(tmp, index=False); os.replace(tmp, f"{outd}/chunk_{start:06d}.csv")
            print(f"  chunk {start} ({k}/{len(todo)}) {time.time() - t0:.0f}s", flush=True)
    print("C01_EXIT=0", flush=True)


if __name__ == "__main__":
    main()
