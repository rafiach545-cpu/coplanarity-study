#!/usr/bin/env python3
"""
Phase 9: converted-photon background (paper Sec. III D), literal reprocessing of the EXISTING raw photon sample
02_backgrounds/photon_conversion/zgamma_photons.csv (9139 Z(nunu)+gamma+j photons with MET > 200 GeV).

VALIDATE: frozen v4 code path (convert_and_analyze_v4_full_diagnostics.analyze_one_event_v4, sequential
          default_rng(99)) on the first N events -> must reproduce the stored v4 rows.
LITERAL : per event i, rng = default_rng(SeedSequence([99, 1708, i])):
            z0 ~ N(0, 45 mm); photon straight from (0,0,z0) to the beam-pipe radius 2.35 cm (frozen
            find_conversion_point); equal energy sharing, collinear e+ e- (paper);
            e+/e- propagated with the PILE-UP detector simulation's exact helix
            ("passed through the same detector simulation as described for the pile-up background"),
            including its per-hit 25 ns time-of-flight cut;
            literal response: finite barrel (ref [27]), pixel-centre quantisation, SCT 34 um / 1160 um,
            neighbouring-pixel merging; plane fit relative to the PRIMARY vertex (0,0,z0)
            (paper Sec. III C: "the primary vertex is identified correctly, and is located at the origin").
          16 standard normals are drawn up front (2 per possible SCT crossing) -> common random numbers for:
            SYS_CONVPT : fit origin = conversion point (frozen project convention)
            SYS_Z0     : SCT z not smeared
            SYS_ETA    : eta-cone acceptance (frozen geometry), PV origin
Output: one CSV per 200-event chunk under ../logs/P9_chunks_<mode>/ (append-only, resumable).
"""
import os, sys, time, multiprocessing as mp
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import literal_detector as ld                                   # noqa: E402
import atlas_geometry as ag                                     # noqa: E402
from helix_propagation import find_helix_layer_crossings         # noqa: E402
from trajectory_to_hits import merge_neighboring_pixel_hits, quantize_pixel   # noqa: E402
from coplanarity_fit import seeding_and_iterative_fit, select_reconstructed_plane, check_hit_multiplicity  # noqa: E402
from convert_and_analyze import find_conversion_point, ELECTRON_MASS_GEV, CONVERSION_PROBABILITY, PER_EVENT_XSEC_PB  # noqa: E402
PC = "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion"
CHUNK = 200
PH = None
IDX = {L["name"]: i for i, L in enumerate(ag.LAYERS, 1)}
CONFIGS = {"LITERAL": ("B", "Z1160", "PV"), "SYS_CONVPT": ("B", "Z1160", "CONV"), "SYS_Z0": ("B", "Z0", "PV"), "SYS_ETA": ("A", "Z1160", "PV")}


def _init():
    global PH
    PH = pd.read_csv(f"{PC}/zgamma_photons.csv")


def analyse(hits, origin):
    hbl = {k: [] for k in range(1, 9)}
    for h in hits:
        hbl[IDX[h["layer"]]].append((h["x"] - origin[0], h["y"] - origin[1], h["z"] - origin[2]))
    cands = seeding_and_iterative_fit(hbl)
    w = select_reconstructed_plane(cands)
    mult = check_hit_multiplicity(w["layers"]) if w else False
    ds = w["fit"]["delta_s"] if w else np.nan; dw = w["fit"]["delta_w"] if w else np.nan
    best = max((len(set(c["layers"])) for c in cands), default=0)
    return dict(n_hits=len(hits), n_candidates=len(cands), best_layers=best, plane=w is not None, ds=ds, dw=dw,
                mult=bool(mult), dw_pass=bool(w is not None and dw < 1.0), ds_pass=bool(w is not None and ds < 0.01),
                final=bool(w is not None and mult and ds < 0.01),
                winner_layers=str(sorted(w["layers"])) if w else "")


def literal_event(i):
    r = PH.iloc[i]
    rng = np.random.default_rng(np.random.SeedSequence([99, 1708, i]))
    z0 = rng.normal(0.0, 4.5)
    g = rng.standard_normal(16).reshape(2, 4, 2)
    base = dict(event=i, z0_cm=z0, weight_pb=PER_EVENT_XSEC_PB * CONVERSION_PROBABILITY)
    cp = find_conversion_point(r.px, r.py, r.pz, r.E, z0, ag.BEAMPIPE_RADIUS_CM)
    if cp is None:
        return [dict(base, config=c, status="no_conversion_point") for c in CONFIGS]
    p = np.array([r.px, r.py, r.pz]) / 2.0
    cross = []
    for body, q in ((0, -1.0), (1, 1.0)):
        cr = find_helix_layer_crossings(cp, p, ELECTRON_MASS_GEV, q, 2.0, [L["r_cm"] for L in ag.LAYERS])
        for L in ag.LAYERS:
            res = cr.get(L["r_cm"])
            if res is None or res[1] is None or res[1] > 25.0:          # pile-up sim per-hit 25 ns cut
                continue
            (x, y, z), t = res
            cross.append((body, L, x, y, z, t))
    out = []
    for name, (geom, sct, origin) in CONFIGS.items():
        raw = []
        for body, L, x, y, z, t in cross:
            if not ld.accepted(L["name"], np.hypot(x, y), z, geom):
                continue
            rphi = L["r_cm"] * np.arctan2(y, x)
            if L["is_pixel"]:
                rh, zh, ir, iz = quantize_pixel(rphi, z, L["eff_res_rphi_um"], L["eff_res_z_um"])
            else:
                g1, g2 = g[body, IDX[L["name"]] - 5]
                rh, zh, ir, iz = rphi + 34e-4 * g1, z + ld.SCT_Z_SIGMA_CM[sct] * g2, None, None
            ph_ = rh / L["r_cm"]
            raw.append({"layer": L["name"], "layer_r_cm": L["r_cm"], "quirk_index": body, "t_ns": t,
                        "x": L["r_cm"] * np.cos(ph_), "y": L["r_cm"] * np.sin(ph_), "z": zh,
                        "is_pixel": L["is_pixel"], "idx_rphi": ir, "idx_z": iz})
        merged = merge_neighboring_pixel_hits(raw)
        org = (0.0, 0.0, z0) if origin == "PV" else tuple(cp)
        out.append(dict(base, config=name, status="ok", conv_r_cm=float(np.hypot(cp[0], cp[1])), conv_z_cm=float(cp[2]),
                        n_crossings=len(cross), n_raw_hits=len(raw), **analyse(merged, org)))
    return out


def validate_chunk(n):
    sys.path.insert(0, PC)
    from convert_and_analyze_v4_full_diagnostics import analyze_one_event_v4
    ph = pd.read_csv(f"{PC}/zgamma_photons.csv"); rng = np.random.default_rng(99)
    return [dict(event=i, **analyze_one_event_v4(ph.iloc[i], rng)) for i in range(n)]


def chunk_job(start):
    n = len(PH)
    rows = []
    for i in range(start, min(start + CHUNK, n)):
        rows += literal_event(i)
    return start, rows


def main():
    mode = sys.argv[1]
    outd = f"{HERE}/../logs/P9_chunks_{mode}"; os.makedirs(outd, exist_ok=True)
    if mode == "VALIDATE":
        n = int(sys.argv[2]); f = f"{outd}/validate_first_{n}.csv"
        if not os.path.exists(f):
            pd.DataFrame(validate_chunk(n)).to_csv(f, index=False)
        return
    _init(); n = len(PH)
    todo = [s for s in range(0, n, CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
    print(f"LITERAL: {len(todo)} chunks", flush=True); t0 = time.time()
    with mp.Pool(10, initializer=_init) as pool:
        for k, (start, rows) in enumerate(pool.imap_unordered(chunk_job, todo), 1):
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"; pd.DataFrame(rows).to_csv(tmp, index=False)
            os.replace(tmp, f"{outd}/chunk_{start:06d}.csv"); print(f"  chunk {start} ({k}/{len(todo)}) {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
