#!/usr/bin/env python3
"""
Fiducial-acceptance replay on EXISTING trigger-passing EW events (no new
generation). Read-only with respect to all project files.

Physics/numerics reused unchanged from the project (imported, never edited):
  04_detector_sim/trajectory_to_hits.py   (simulate_quirk_hits, find_layer_crossing, LAYERS)
  03_trajectory_sim/quirk_trajectory_optimized_v2.py (integrate_trajectory_fast_v2,
                                                      the integrator the 2000-event
                                                      run and Figure 6 use)

Method
------
1. Each event is propagated once with the primary vertex at z0 = 0. The EOM
   (uniform B along z, no z-dependent material) is exactly invariant under a
   z translation, so the true-vertex crossings are the z0=0 crossings shifted
   by z0.
2. For every quirk and layer the FIRST outward crossing (project rule) is
   stored: x, y, z (relative to vertex), t_ns.
3. The project's vertex z0 is recovered exactly:
     EW2000: z0 = default_rng(seed).normal(0, 4.5) with the stored per-event seed.
     EW1000: one sequential default_rng(4242) stream (analyze_ew_quirk.py):
             per event, 1 draw for z0, then 2 draws (r-phi, z) per SCT
             crossing that passes |eta|<1.8; pixel hits draw nothing.
4. Acceptance variants are evaluated on the same crossings:
     A  project baseline : all 16 crossings exist, |eta_origin|<1.8, max t<25 ns
     B  finite barrel    : all 16 crossings exist, |z_lab| < half-length(layer), max t<25 ns
     ...  (see VARIANTS below)
   Variant A must reproduce the project's stored truth_fiducial flag event by
   event; that is the validation of the replay.
"""
import os
import sys
import json
import time
import math
import argparse
import multiprocessing as mp
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
AUD = f"{BASE}/05_coplanarity_analysis/EW_PAPER_REPRODUCTION_AUDIT_2026-10-02"
sys.path.insert(0, f"{BASE}/04_detector_sim")
sys.path.insert(0, f"{BASE}/03_trajectory_sim")

MQ, LAM = 800.0, 4e-6
SAMPLE_PARAMS = {"EW1000": (800.0, 4e-6), "EW2000": (800.0, 4e-6), "COL2000": (1800.0, 2e-6)}
SIGMA_Z_CM = 4.5
ETA_MAX = 1.8
T_CUT = 25.0
PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}


def _init(mq, lam):
    global tth, MQ, LAM
    MQ, LAM = mq, lam
    import trajectory_to_hits as _tth
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _tth.integrate_trajectory = integrate_trajectory_fast_v2
    tth = _tth


def propagate(args):
    key, p1, p2, c1, c2 = args
    t0 = time.perf_counter()
    try:
        _, traj = tth.simulate_quirk_hits(
            p1, p2, mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=c1, charge2=c2,
            rng=np.random.default_rng(0), z0_cm=0.0, max_layer_r_cm=60.0)
        x1 = traj["x1"] * 1.973269804e-14
        x2 = traj["x2"] * 1.973269804e-14
        tg = traj["t_gev_inv"]
        rows = []
        for qi, xt in ((1, x1), (2, x2)):
            for L, layer in enumerate(tth.LAYERS, 1):
                res = tth.find_layer_crossing(xt, tg, layer["r_cm"])
                if res is None:
                    rows.append(dict(key=key, quirk=qi, layer=L, crossed=False))
                else:
                    (x, y, z), t_ns = res
                    rows.append(dict(key=key, quirk=qi, layer=L, crossed=True, x=x, y=y,
                                     z_rel=z, t_ns=t_ns, r=layer["r_cm"],
                                     is_pixel=layer["is_pixel"]))
        return dict(key=key, ok=True, rows=rows, wall=time.perf_counter() - t0)
    except Exception as e:
        return dict(key=key, ok=False, err=f"{type(e).__name__}: {e}", wall=time.perf_counter() - t0)


def eta_of(r, z):
    return -math.log(math.tan(math.atan2(r, z) / 2.0))


def load_inputs(sample):
    if sample == "COL2000":
        # cross-check sample only: project's charge-filtered trigger set + stored seeds
        d = f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1"
        trig = pd.read_csv(f"{d}/events/colored_1800GeV_L2keV/trigger_passing_events.csv")
        res = pd.read_csv(f"{d}/reconstruction/colored_1800GeV_L2keV/per_event_results.csv")
        trig["row_index"] = np.arange(len(trig))
        trig = trig.merge(res[["row_index", "seed", "truth_fiducial", "geometric_fiducial",
                               "sec3c_plane_found", "final_sec_iv_pass", "n_hits_premerge"]],
                          on="row_index", how="left", validate="1:1")
        trig["event_id"] = trig["hepmc_event_idx"].astype(int)
        assert (trig["quirk_pair_pt_gev"] > 200).all()
        return trig, float("nan")
    raw = pd.read_csv(f"{AUD}/tables/{sample}_hepmc_events.csv")
    if sample == "EW2000":
        d = f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1"
        trig = pd.read_csv(f"{d}/events/EW_800GeV_L4keV/trigger_passing_events.csv")
        res = pd.read_csv(f"{d}/reconstruction/EW_800GeV_L4keV/per_event_results.csv")
        trig["row_index"] = np.arange(len(trig))
        trig = trig.merge(res[["row_index", "seed", "truth_fiducial", "geometric_fiducial",
                               "sec3c_plane_found", "final_sec_iv_pass", "n_hits_premerge"]],
                          on="row_index", how="left", validate="1:1")
        trig["event_id"] = trig["hepmc_event_idx"].astype(int)
    else:
        src = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")
        trig = src[src["pT_pair"] > 200].reset_index(drop=True)
        trig["row_index"] = np.arange(len(trig))
        res = pd.read_csv(f"{BASE}/05_coplanarity_analysis/ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv")
        trig = trig.merge(res[["event", "truth_fiducial", "geometric_fiducial", "seed_found",
                               "passes_signal_region", "n_hits_premerge"]],
                          on="event", how="left", validate="1:1")
        trig["event_id"] = trig["event"].astype(int)
        trig["charge1"] = trig["pdg1"].map(PDG_TO_CHARGE)
        trig["charge2"] = trig["pdg2"].map(PDG_TO_CHARGE)
    # cross-check momenta against the independent raw HepMC parse
    m = trig.merge(raw, left_on="event_id", right_on="hepmc_seq", suffixes=("", "_raw"))
    assert len(m) == len(trig), f"{sample}: not all trigger rows found in raw HepMC table"
    # quirk order may differ between project CSV and raw parse: compare both orderings
    same = np.maximum.reduce([np.abs(m[f"{c}{i}"] - m[f"{c}{i}_raw"]).to_numpy() for c in ("px", "py", "pz") for i in (1, 2)])
    swap = np.maximum.reduce([np.abs(m[f"{c}{i}"] - m[f"{c}{3 - i}_raw"]).to_numpy() for c in ("px", "py", "pz") for i in (1, 2)])
    dmax = float(np.max(np.minimum(same, swap)))
    assert dmax < 1e-6, f"{sample}: project momenta differ from raw HepMC (max {dmax})"
    assert (m["trigger_strict_gt200_final"]).all(), f"{sample}: a project trigger row fails raw trigger"
    return trig, dmax


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True, choices=["EW1000", "EW2000", "COL2000"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()

    trig, dmax = load_inputs(a.sample)
    if a.limit:
        trig = trig.iloc[:a.limit]
    out_cross = f"{AUD}/tables/{a.sample}_layer_crossings_vertex_relative.csv"
    done = {}
    if os.path.exists(out_cross):
        prev = pd.read_csv(out_cross)
        for k, g in prev.groupby("key"):
            done[int(k)] = g.to_dict("records")
    jobs = [(int(r.row_index), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2),
             float(r.charge1), float(r.charge2)) for r in trig.itertuples() if int(r.row_index) not in done]
    print(f"{a.sample}: {len(trig)} trigger events, momenta vs raw max|diff|={dmax:.2e}, "
          f"{len(done)} already propagated, {len(jobs)} to run", flush=True)
    walls, errs = [], []
    if jobs:
        with mp.Pool(a.workers, initializer=_init, initargs=SAMPLE_PARAMS[a.sample]) as pool:
            for i, r in enumerate(pool.imap_unordered(propagate, jobs), 1):
                if r["ok"]:
                    done[r["key"]] = r["rows"]
                    walls.append(r["wall"])
                    pd.DataFrame([x for k in sorted(done) for x in done[k]
                                  if "technical_error" not in x]).to_csv(out_cross, index=False)
                else:
                    errs.append(r)
                print(f"  {i}/{len(jobs)} key={r['key']} ok={r['ok']} wall={r['wall']:.0f}s", flush=True)
    # Technical exceptions are kept in the denominator and counted as
    # non-fiducial in every variant -- exactly how the project's own driver
    # records them (first_failure_reason = technical_exception).
    for e in errs:
        done[e["key"]] = [dict(key=e["key"], quirk=q, layer=L, crossed=False, technical_error=e["err"])
                          for q in (1, 2) for L in range(1, 9)]
    if errs:
        json.dump(errs, open(f"{AUD}/tables/{a.sample}_technical_exceptions.json", "w"), indent=2)

    # --- recover the project's vertex z0 per event --------------------------------
    cross = {k: pd.DataFrame(v) for k, v in done.items()}
    z0 = {}
    if a.sample in ("EW2000", "COL2000"):
        for r in trig.itertuples():
            z0[int(r.row_index)] = np.random.default_rng(int(r.seed)).normal(0.0, SIGMA_Z_CM)
    else:
        rng = np.random.default_rng(4242)
        for r in trig.itertuples():
            k = int(r.row_index)
            z = rng.normal(0.0, SIGMA_Z_CM)
            z0[k] = z
            c = cross[k]
            for row in c.sort_values(["quirk", "layer"]).itertuples():
                if not row.crossed or "technical_error" in c.columns:
                    continue
                if abs(eta_of(row.r, row.z_rel + z)) > ETA_MAX:
                    continue
                if not row.is_pixel:
                    rng.normal(0.0, 1.0)
                    rng.normal(0.0, 1.0)

    HALF = {  # cm; see report for provenance of each number
        "nominal": {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9},
        "sct80":   {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 80.0, 6: 80.0, 7: 80.0, 8: 80.0},
    }
    out = []
    for r in trig.itertuples():
        k = int(r.row_index)
        c = cross[k].sort_values(["quirk", "layer"])
        all16 = bool(c["crossed"].all()) and len(c) == 16
        zc = c["z_rel"].to_numpy(dtype=float) + z0[k] if all16 else None
        rr = c["r"].to_numpy(dtype=float) if all16 else None
        tmax = float(c["t_ns"].max()) if all16 else float("nan")
        t_ok = all16 and tmax < T_CUT
        etas = np.array([eta_of(a_, b_) for a_, b_ in zip(rr, zc)]) if all16 else None
        etas_nov = np.array([eta_of(a_, b_) for a_, b_ in zip(rr, c["z_rel"].to_numpy(float))]) if all16 else None
        lay = c["layer"].to_numpy() if all16 else None

        def finite(h, zz):
            return all16 and all(abs(z_) < h[int(l)] for z_, l in zip(zz, lay))
        P = np.array([r.px1 + r.px2, r.py1 + r.py2, r.pz1 + r.pz2])
        eta_pair = math.asinh(P[2] / math.hypot(P[0], P[1]))
        out.append(dict(
            sample=a.sample, row_index=k, event_id=int(r.event_id), z0_cm=z0[k],
            project_truth_fiducial=bool(r.truth_fiducial), project_n_hits_premerge=r.n_hits_premerge,
            technical_exception=bool("technical_error" in c.columns),
            all_16_crossings_exist=all16, max_t_ns=tmax, timing_ok=bool(t_ok),
            max_abs_eta_crossing=float(np.max(np.abs(etas))) if all16 else float("nan"),
            max_abs_z_crossing_cm=float(np.max(np.abs(zc))) if all16 else float("nan"),
            eta1_prod=float(r.eta1) if hasattr(r, "eta1") else math.asinh(r.pz1 / math.hypot(r.px1, r.py1)),
            eta2_prod=float(r.eta2) if hasattr(r, "eta2") else math.asinh(r.pz2 / math.hypot(r.px2, r.py2)),
            eta_pair=eta_pair,
            A_project_baseline=bool(t_ok and np.all(np.abs(etas) < ETA_MAX)),
            A0_baseline_no_vertex_smear=bool(t_ok and np.all(np.abs(etas_nov) < ETA_MAX)),
            B_finite_barrel_nominal=bool(t_ok and finite(HALF["nominal"], zc)),
            B2_finite_barrel_sct80=bool(t_ok and finite(HALF["sct80"], zc)),
            B0_finite_barrel_nominal_no_vertex_smear=bool(t_ok and finite(HALF["nominal"], c["z_rel"].to_numpy(float) if all16 else None)),
            C_eta1p8_and_finite_barrel=bool(t_ok and np.all(np.abs(etas) < ETA_MAX) and finite(HALF["nominal"], zc)),
            D_eta1p5_crossing=bool(t_ok and np.all(np.abs(etas) < 1.5)),
            E_geometric_only_no_timing_eta1p8=bool(all16 and np.all(np.abs(etas) < ETA_MAX)),
        ))
    df = pd.DataFrame(out)
    df.to_csv(f"{AUD}/tables/{a.sample}_fiducial_variants_per_event.csv", index=False)
    agree = int((df["A_project_baseline"] == df["project_truth_fiducial"]).sum())
    summ = {c: int(df[c].sum()) for c in df.columns if c[:2] in ("A_", "A0", "B_", "B2", "B0", "C_", "D_", "E_")}
    summ.update(N_trigger=len(df), baseline_agreement=f"{agree}/{len(df)}",
                project_truth_fiducial=int(df["project_truth_fiducial"].sum()),
                technical_exceptions=int(df["technical_exception"].sum()),
                mean_wall_s=float(np.mean(walls)) if walls else None)
    json.dump(summ, open(f"{AUD}/tables/{a.sample}_fiducial_variants_summary.json", "w"), indent=2)
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
