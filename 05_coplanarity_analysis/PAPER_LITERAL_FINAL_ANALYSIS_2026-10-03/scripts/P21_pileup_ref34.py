#!/usr/bin/env python3
"""
P21 (2026-10-08, pre-registered in DECISIONS_LOG D8): pile-up only, mu = 50, the SAME 5000 events and seeds as P8
(SeedSequence([90210777, 50, i]).spawn(2)), with two changes:
  1. every pile-up particle is propagated with the detector model of paper ref. [34] (arXiv:1612.00850 App. A), as already
     used for the conversions (P17): exact helix between layers; after each hit, bremsstrahlung E -> E exp(-t_eff) for
     electrons, and most-probable ionisation loss for every particle (0.28 MeV per mm silicon-equivalent at minimum
     ionisation, scaled by 1/beta^2 for slow particles); no multiple scattering (not in [34]); stop when the kinetic energy
     falls below 10% of the mass; 25 ns per-hit time-of-flight cut (unchanged). X0 per layer: tables/material_X0_per_layer_ref27.csv.
  2. SCT z resolution 580 um (the resolution of the cited model [34], from the ATLAS TDR = Ref. [27] value).
Unchanged: Ref. [27] barrel lengths (geometry B), pixel-centre quantisation, neighbouring-pixel merging, tracking-efficiency
track suppression, plane finding from the vertex at the origin, SCT random-draw order.
Modes: VALIDATE_NOMAT (material off, SCT z 1160, first 200 events; must reproduce logs/P8_chunks_LITERAL exactly),
       REF34_Z580 (the pre-registered run). Output: logs/P21_chunks_<mode>/chunk_*.csv (append-only, resumable).
"""
import os, sys, math, time, importlib.util, multiprocessing as mp
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import literal_detector as ld                                   # noqa: E402
import atlas_geometry as ag                                     # noqa: E402
import trajectory_to_hits as tth                                # noqa: E402
import pileup_hits as ph                                        # noqa: E402
import pileup_hits_suppressed as phs                            # noqa: E402
_s = importlib.util.spec_from_file_location("p8", f"{HERE}/P8_literal_pileup.py"); p8 = importlib.util.module_from_spec(_s); _s.loader.exec_module(p8)
_s = importlib.util.spec_from_file_location("p16", f"{HERE}/P16_conversion_material.py"); p16 = importlib.util.module_from_spec(_s); _s.loader.exec_module(p16)
MAT = pd.read_csv(f"{HERE}/../tables/material_X0_per_layer_ref27.csv"); X0 = {}
for r in MAT.itertuples():
    for nm in (r.layer_names if isinstance(r.layer_names, str) else "").split(): X0[nm] = float(r.per_layer_X0_normal_incidence)
SI_X0_MM, DEDX_MIP_GEV_PER_MM, CL = 93.7, 0.28e-3, 29.9792458
MATERIAL = {"on": True}

def ref34_particle_hits(px, py, pz, m, charge_e, vertex_cm, particle_tag, rng, B_tesla=2.0):
    """Same signature, hit schema and random-draw order as literal_detector.literal_pileup_particle_hits."""
    x, p, tns, hits = np.asarray(vertex_cm, float).copy(), np.array([px, py, pz], float), 0.0, []
    if math.hypot(p[0], p[1]) <= 0 or charge_e == 0: return hits
    for layer in ag.LAYERS:
        r = p16.next_crossing(x, p, charge_e, layer["r_cm"])
        if r is None: break
        x, p_new, path = r; pm = math.sqrt(p_new @ p_new); E = math.sqrt(pm * pm + m * m); tns += path / (CL * pm / E); p = p_new
        if tns > ph.PILEUP_HIT_TIMING_CUT_NS: break
        if ld.accepted(layer["name"], math.hypot(x[0], x[1]), x[2], ld.CONFIG["geometry"]):
            rphi = layer["r_cm"] * math.atan2(x[1], x[0])
            if layer["is_pixel"]: rh, zh, ir, iz = tth.quantize_pixel(rphi, x[2], layer["eff_res_rphi_um"], layer["eff_res_z_um"])
            else:
                rh = rphi + rng.normal(0.0, layer["eff_res_rphi_um"] * 1e-4); zh = x[2] + rng.normal(0.0, 1.0) * ld.SCT_Z_SIGMA_CM[ld.CONFIG["sct"]]; ir = iz = None
            ph_ = rh / layer["r_cm"]
            hits.append({"layer": layer["name"], "layer_r_cm": layer["r_cm"], "quirk_index": particle_tag, "t_ns": tns,
                         "x": layer["r_cm"] * math.cos(ph_), "y": layer["r_cm"] * math.sin(ph_), "z": zh,
                         "is_pixel": layer["is_pixel"], "idx_rphi": ir, "idx_z": iz})
        if MATERIAL["on"]:   # the particle traverses the layer material whether or not a hit is recorded
            rhat = np.array([x[0], x[1], 0.0]) / math.hypot(x[0], x[1]); te = X0[layer["name"]] / max(abs(p @ rhat) / pm, 1e-3)
            if m < 0.01: E = E * math.exp(-te)                                           # bremsstrahlung (electrons)
            beta2 = (pm / math.sqrt(pm * pm + m * m)) ** 2
            E = E - DEDX_MIP_GEV_PER_MM * te * SI_X0_MM / max(beta2, 1e-6)               # most-probable ionisation
            if E - m < 0.1 * m: break                                                    # [34] stopping condition
            p = p * math.sqrt(max(E * E - m * m, 0.0)) / pm
    return hits

def _init(mode):
    if mode == "VALIDATE_NOMAT": ld.install("B", "Z1160"); MATERIAL["on"] = False
    else: ld.install("B", "Z580"); MATERIAL["on"] = True
    phs.pileup_particle_hits = ref34_particle_hits
    p8.POOL = p8.build_ancestry_pool_index(pd.read_csv(p8.ANCESTRY_POOL_PATH))

def chunk_job(a):
    mode, start, stop = a
    return start, [p8.one_event(i, "LITERAL") for i in range(start, stop)]   # "LITERAL" = merge neighbouring pixels (as P8)

def main():
    mode, n = sys.argv[1], int(sys.argv[2])
    outd = f"{HERE}/../logs/P21_chunks_{mode}"; os.makedirs(outd, exist_ok=True)
    todo = [(mode, s, min(s + p8.CHUNK, n)) for s in range(0, n, p8.CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
    print(f"{mode}: {len(todo)} chunks to run", flush=True); t0 = time.time()
    with mp.Pool(10, initializer=_init, initargs=(mode,)) as pool:
        for k, (start, rows) in enumerate(pool.imap_unordered(chunk_job, todo), 1):
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"; pd.DataFrame(rows).to_csv(tmp, index=False); os.replace(tmp, f"{outd}/chunk_{start:06d}.csv")
            print(f"  chunk {start} done ({k}/{len(todo)}), {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
