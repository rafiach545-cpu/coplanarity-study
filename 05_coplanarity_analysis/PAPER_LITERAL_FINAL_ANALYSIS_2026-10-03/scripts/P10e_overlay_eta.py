#!/usr/bin/env python3
"""
P10e (copy of P10_literal_overlay.py, 2026-10-03): identical, except the detector acceptance is the paper-stated
|eta|<1.8 (geometry A) for BOTH the conversion e+e- and the pile-up hits; output logs/P10_chunks_ETA. Same seeds/events.

Original docstring:
Phase 10: converted photon + mu=50 pile-up overlay (paper Sec. III D: "We subsequently overlay pile-up hits and
pass the resulting set of hits through our reconstruction algorithm"), literal detector.

Per event i of zgamma_photons.csv:
  hard part     : identical to P9 LITERAL (SeedSequence([99,1708,i]) -> z0, 16 SCT normals; conversion at the
                  beam pipe; helix e+/e-; finite barrel; SCT 34/1160 um)
  pile-up part  : frozen sampling + track suppression with the literal particle-hit response installed
                  (finite barrel, SCT 34/1160 um); streams SeedSequence([90210777, i]).spawn(2) as in the frozen
                  overlay driver; mu = 50
  combination   : raw conversion hits + raw retained pile-up hits merged ONCE (frozen pileup_hits.overlay_and_merge)
  fit origin    : primary vertex (0,0,z0) [LITERAL]; conversion point [SYS_CONVPT]
Records ancestry of the selected plane's hits (conversion e+/e- vs pile-up) and stores full hit lists for any
event passing the final Sec. IV selection (event displays).
"""
import os, sys, time, json, multiprocessing as mp
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import literal_detector as ld                                    # noqa: E402
import atlas_geometry as ag                                      # noqa: E402
import pileup_hits_suppressed as phs                             # noqa: E402
from pileup_hits import overlay_and_merge                         # noqa: E402
from pileup_hits_suppressed import build_ancestry_pool_index      # noqa: E402
from run_pileup_fake_background_suppressed import ANCESTRY_POOL_PATH   # noqa: E402
from tracking_efficiency import BASELINE_SELECTION                # noqa: E402
from helix_propagation import find_helix_layer_crossings          # noqa: E402
from trajectory_to_hits import quantize_pixel                     # noqa: E402
from coplanarity_fit import seeding_and_iterative_fit, select_reconstructed_plane, check_hit_multiplicity  # noqa: E402
from convert_and_analyze import find_conversion_point, ELECTRON_MASS_GEV, CONVERSION_PROBABILITY, PER_EVENT_XSEC_PB  # noqa: E402
PC = "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion"
MU, PU_SEED, CHUNK = 50, 90210777, 50
IDX = {L["name"]: i for i, L in enumerate(ag.LAYERS, 1)}
PH = POOL = None


def _init():
    global PH, POOL
    ld.install("A", "Z1160")
    PH = pd.read_csv(f"{PC}/zgamma_photons.csv")
    POOL = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))


def conv_hits(r, rng):
    z0 = rng.normal(0.0, 4.5); g = rng.standard_normal(16).reshape(2, 4, 2)
    cp = find_conversion_point(r.px, r.py, r.pz, r.E, z0, ag.BEAMPIPE_RADIUS_CM)
    if cp is None:
        return z0, None, []
    p = np.array([r.px, r.py, r.pz]) / 2.0
    raw = []
    for body, q in ((0, -1.0), (1, 1.0)):
        cr = find_helix_layer_crossings(cp, p, ELECTRON_MASS_GEV, q, 2.0, [L["r_cm"] for L in ag.LAYERS])
        for L in ag.LAYERS:
            res = cr.get(L["r_cm"])
            if res is None or res[1] is None or res[1] > 25.0:
                continue
            (x, y, z), t = res
            if not ld.accepted(L["name"], np.hypot(x, y), z, "A"):
                continue
            rphi = L["r_cm"] * np.arctan2(y, x)
            if L["is_pixel"]:
                rh, zh, ir, iz = quantize_pixel(rphi, z, L["eff_res_rphi_um"], L["eff_res_z_um"])
            else:
                g1, g2 = g[body, IDX[L["name"]] - 5]; rh, zh, ir, iz = rphi + 34e-4 * g1, z + 0.1160 * g2, None, None
            ph_ = rh / L["r_cm"]
            raw.append({"layer": L["name"], "layer_r_cm": L["r_cm"], "quirk_index": f"conv_e{body}", "t_ns": t,
                        "x": L["r_cm"] * np.cos(ph_), "y": L["r_cm"] * np.sin(ph_), "z": zh, "is_pixel": L["is_pixel"],
                        "idx_rphi": ir, "idx_z": iz})
    return z0, cp, raw


def reco(merged, origin):
    hbl = {k: [] for k in range(1, 9)}; lookup = {}
    for h in merged:
        pt = (h["x"] - origin[0], h["y"] - origin[1], h["z"] - origin[2])
        hbl[IDX[h["layer"]]].append(pt); lookup[pt] = h
    cands = seeding_and_iterative_fit(hbl)
    w = select_reconstructed_plane(cands)
    mult = check_hit_multiplicity(w["layers"]) if w else False
    ds = w["fit"]["delta_s"] if w else np.nan; dw = w["fit"]["delta_w"] if w else np.nan
    anc = {"conv": 0, "pileup": 0, "mixed": 0}
    if w:
        for pt in w["hits"]:
            src = [str(s) for s in lookup[pt].get("source_quirk_indices", [lookup[pt]["quirk_index"]])]
            c = any(s.startswith("conv") for s in src); pu = any(s.startswith("pu") for s in src)
            anc["mixed" if (c and pu) else "conv" if c else "pileup"] += 1
    best = max((len(set(c["layers"])) for c in cands), default=0)
    final = bool(w is not None and mult and ds < 0.01)
    return dict(n_candidates=len(cands), best_layers=best, plane=w is not None, ds=ds, dw=dw, mult=bool(mult),
                dw_pass=bool(w is not None and dw < 1.0), ds_pass=bool(w is not None and ds < 0.01), final=final,
                winner_conv_hits=anc["conv"], winner_pileup_hits=anc["pileup"], winner_mixed_hits=anc["mixed"]), (w, hbl)


def event(i):
    r = PH.iloc[i]
    z0, cp, raw_conv = conv_hits(r, np.random.default_rng(np.random.SeedSequence([99, 1708, i])))
    base = dict(event=i, mu=MU, z0_cm=z0, weight_pb=PER_EVENT_XSEC_PB * CONVERSION_PROBABILITY)
    if cp is None:
        return [dict(base, config=c, status="no_conversion_point") for c in ("LITERAL", "SYS_CONVPT")], []
    c1, c2 = np.random.SeedSequence([PU_SEED, i]).spawn(2)
    pu, st = phs.sample_pileup_hits_suppressed(POOL, MU, np.random.default_rng(c1), np.random.default_rng(c2),
                                               B_tesla=2.0, selection=BASELINE_SELECTION)
    merged, ms = overlay_and_merge(raw_conv, pu)
    rows, displays = [], []
    for name, org in (("LITERAL", (0.0, 0.0, z0)), ("SYS_CONVPT", tuple(cp))):
        res, (w, hbl) = reco(merged, org)
        rows.append(dict(base, config=name, status="ok", n_conv_hits_raw=len(raw_conv), n_pu_interactions=st["n_pu_interactions"],
                         n_pu_hits_raw=len(pu), n_hits_merged=len(merged), **res))
        if res["final"] or (res["plane"] and res["mult"]):
            displays.append(dict(event=i, config=name, origin=list(org), z0_cm=z0, conv_point=list(cp), final=res["final"],
                                 hits=[(h["layer"], h["x"], h["y"], h["z"], [str(s) for s in h.get("source_quirk_indices", [h["quirk_index"]])]) for h in merged
                                       if IDX[h["layer"]] in (1, 2, 3, 4, 5, 6, 7, 8)][:20000],
                                 winner_hits=[list(p) for p in w["hits"]], n1=w["fit"]["n1"].tolist(), n2=w["fit"]["n2"].tolist(),
                                 n3=w["fit"]["n3"].tolist(), ds=res["ds"], dw=res["dw"]))
    return rows, displays


def chunk_job(start):
    rows, disp = [], []
    for i in range(start, min(start + CHUNK, len(PH))):
        r, d = event(i); rows += r; disp += d
    return start, rows, disp


def main():
    outd = f"{HERE}/../logs/P10_chunks_ETA"; os.makedirs(outd, exist_ok=True)
    n = len(pd.read_csv(f"{PC}/zgamma_photons.csv"))
    todo = [s for s in range(0, n, CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
    print(f"P10: {len(todo)} chunks", flush=True); t0 = time.time()
    with mp.Pool(10, initializer=_init) as pool:
        for k, (start, rows, disp) in enumerate(pool.imap_unordered(chunk_job, todo), 1):
            if disp:
                with open(f"{outd}/displays_{start:06d}.jsonl", "w") as f:
                    for d in disp:
                        f.write(json.dumps(d, default=float) + "\n")
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"; pd.DataFrame(rows).to_csv(tmp, index=False)
            os.replace(tmp, f"{outd}/chunk_{start:06d}.csv")
            print(f"  chunk {start} ({k}/{len(todo)}) {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
