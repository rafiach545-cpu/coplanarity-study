#!/usr/bin/env python3
"""
Figure 6 Phase 5 full production driver.

Two sequential stages:
  1. Generation -- 13 distinct mass points (6 EW, 7 colored), 2000 events
     each, strictly sequential, atomic DONE markers, resumable.
  2. Downstream -- 91 (mass, Lambda) grid cells. For each distinct mass
     point, the trigger-passing event set is computed ONCE (Lambda-
     independent) and reused across all 7 Lambda values. Each cell is
     propagated with a 3-worker multiprocessing pool (validated this task:
     bit-identical to serial, deterministic across reruns). Checkpointed
     every CHUNK_SIZE events.

Resumable: rerunning this script skips any mass point/cell already marked
DONE. Safe to kill (SIGTERM/SIGKILL) and restart at any point -- the last
incomplete chunk is simply redone (partial in-progress chunk work is not
separately checkpointed mid-chunk, only whole chunks and whole cells are
atomic).

See PHASE5_LAUNCH_JUSTIFICATION.md and PAPER_FIGURE6_REQUIREMENTS.md.
"""
import sys
import os
import re
import json
import time
import shutil
import subprocess
import multiprocessing as mp
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
FIG6 = f"{BASE}/05_coplanarity_analysis/figure6_full_v1"
HEP_TOOLS_RUNS = "/home/rafia/hep_tools/figure6_full_v1_runs"
TEMPLATE_EW = "/home/rafia/hep_tools/quirk_ew_800gev_4kev"
TEMPLATE_COLORED = "/home/rafia/hep_tools/quirk_signal_1800gev_2kev"

sys.path.insert(0, f"{BASE}/05_coplanarity_analysis/madgraph_pilot_v1")
sys.path.insert(0, f"{BASE}/01_signal_generation")
sys.path.insert(0, f"{BASE}/04_detector_sim")
sys.path.insert(0, f"{BASE}/05_coplanarity_analysis")
sys.path.insert(0, f"{BASE}/03_trajectory_sim")

from extract_pilot_data import parse_hepmc
from extract_quirk_momenta import _make_rhadron_charge_lookup

N_GEN = 2000
LAMBDA_GEV_MAP = {1: 1e-6, 2: 2e-6, 3: 3e-6, 4: 4e-6, 5: 5e-6, 7: 7e-6, 10: 10e-6}
CHUNK_SIZE = 30  # within the 25-50 required range
N_WORKERS = 3
RUNTIME_GUARD_HOURS = 60.0

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}

STATUS_PATH = f"{FIG6}/RUNTIME/status.json"
T_START = time.time()


def atomic_write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


def update_status(**kwargs):
    status = {}
    if os.path.exists(STATUS_PATH):
        try:
            status = json.load(open(STATUS_PATH))
        except Exception:
            status = {}
    status.update(kwargs)
    status["last_update_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_h"] = round((time.time() - T_START) / 3600, 3)
    atomic_write_json(STATUS_PATH, status)
    return status


def load_grid():
    return pd.read_csv(f"{FIG6}/tables/figure6_grid91_full.csv")


def mass_points_from_grid(df):
    mp_df = df.drop_duplicates(subset=["channel", "mass_gev"])[
        ["channel", "mass_gev", "generation_seed"]].sort_values(["channel", "mass_gev"])
    return list(mp_df.itertuples(index=False))


# ---------------------------------------------------------------------
# STAGE 1: GENERATION
# ---------------------------------------------------------------------

def edit_param_card(path, channel, mass_gev):
    with open(path) as f:
        text = f.read()
    if channel == "EW":
        text = re.sub(r"(\n\s*9000011\s+)[0-9.eE+-]+(\s+# mqe)", rf"\g<1>{mass_gev:.6e}\g<2>", text)
    else:
        text = re.sub(r"(\n\s*1000006\s+)[0-9.eE+-]+(\s+# mqc)", rf"\g<1>{mass_gev:.6e}\g<2>", text)
    with open(path, "w") as f:
        f.write(text)


def edit_run_card(path, nevents, seed):
    with open(path) as f:
        lines = f.readlines()
    out = []
    for line in lines:
        if "= nevents" in line:
            out.append(re.sub(r"^\s*\d+", f"  {nevents}", line))
        elif "= iseed" in line:
            out.append(re.sub(r"^\s*\d+", f"  {seed}", line))
        else:
            out.append(line)
    with open(path, "w") as f:
        f.writelines(out)


def force_nb_core_1(path):
    with open(path) as f:
        text = f.read()
    if "nb_core = 1" not in text:
        text = text.replace("# nb_core = None", "nb_core = 1")
    with open(path, "w") as f:
        f.write(text)


def run_generation_one_point(channel, mass_gev, seed, attempt=1):
    mass_gev = int(mass_gev)
    tag = f"{channel}_{mass_gev}gev"
    run_dir = f"{HEP_TOOLS_RUNS}/{tag}"
    template = TEMPLATE_EW if channel == "EW" else TEMPLATE_COLORED
    done_marker = f"{run_dir}/checkpoints_DONE_generation.txt"
    if os.path.exists(done_marker):
        return {"status": "already_done", "tag": tag}

    if not os.path.exists(run_dir):
        os.makedirs(HEP_TOOLS_RUNS, exist_ok=True)
        subprocess.run(["rsync", "-a", "--exclude=Events/run_01", "--exclude=Events/run_fig6",
                         f"{template}/", f"{run_dir}/"], check=True)
        edit_param_card(f"{run_dir}/Cards/param_card.dat", channel, mass_gev)

    edit_run_card(f"{run_dir}/Cards/run_card.dat", N_GEN, seed)
    force_nb_core_1(f"{run_dir}/Cards/me5_configuration.txt")

    run_name = f"run_fig6_attempt{attempt}"
    log_path = f"{run_dir}/gen_{run_name}.log"
    env = os.environ.copy()
    env.pop("PYTHIA8DATA", None)  # scoped fix: MG5's bundled HEPTools/pythia8 must self-resolve its own xmldoc
    t0 = time.time()
    with open(log_path, "w") as logf:
        proc = subprocess.run(["./bin/generate_events", run_name, "-f"], cwd=run_dir,
                               env=env, stdout=logf, stderr=subprocess.STDOUT, timeout=3600)
    wall = time.time() - t0

    events_dir = f"{run_dir}/Events/{run_name}"
    log_text = open(log_path).read()
    success = (proc.returncode == 0) and os.path.exists(f"{events_dir}/tag_1_pythia8_events.hepmc.gz")
    m = re.search(r"Nb of events after matching/merging\s*:\s*(\d+)", log_text)
    n_matched = int(m.group(1)) if m else None
    xm = re.search(r"Matched cross-section\s*:\s*([0-9.eE+-]+)\s*\+-\s*([0-9.eE+-]+)", log_text)
    xsec, xsec_err = (float(xm.group(1)), float(xm.group(2))) if xm else (None, None)

    if success:
        os.rename(events_dir, f"{run_dir}/Events/run_fig6")
        with open(done_marker, "w") as f:
            f.write(f"OK attempt={attempt} wall_s={wall:.1f} n_matched={n_matched}\n")
        stats = {"channel": channel, "mass_gev": mass_gev, "seed": seed, "n_generated": N_GEN,
                  "n_matched": n_matched, "matched_xsec_pb": xsec, "matched_xsec_err_pb": xsec_err,
                  "wall_s": wall, "attempt": attempt, "exit_code": proc.returncode}
        os.makedirs(f"{run_dir}/metadata", exist_ok=True)
        atomic_write_json(f"{run_dir}/metadata/generation_stats.json", stats)
        return {"status": "ok", "tag": tag, "n_matched": n_matched, "wall_s": wall}
    else:
        failed_dir = f"{run_dir}/Events/FAILED_ATTEMPT_NOT_AUTHORITATIVE_{attempt}"
        if os.path.exists(events_dir):
            os.rename(events_dir, failed_dir)
        return {"status": "failed", "tag": tag, "wall_s": wall, "log": log_path}


def stage1_generation(grid):
    points = mass_points_from_grid(grid)
    results = []
    for i, row in enumerate(points):
        channel, mass_gev, seed = row.channel, row.mass_gev, int(row.generation_seed)
        update_status(stage="generation", current_point=f"{channel}_{mass_gev}GeV",
                       generation_progress=f"{i}/{len(points)}")
        r = run_generation_one_point(channel, mass_gev, seed, attempt=1)
        if r["status"] == "failed":
            print(f"RETRY (once, per Phase 7 failure policy): {r['tag']}")
            r = run_generation_one_point(channel, mass_gev, seed, attempt=2)
        results.append(r)
        print(f"[{i+1}/{len(points)}] {channel} {mass_gev}GeV: {r['status']}")
        if r["status"] == "failed":
            print(f"WARNING: {channel} {mass_gev}GeV generation FAILED after retry. "
                  f"Marking point incomplete, continuing to next point (per failure policy).")
    atomic_write_json(f"{FIG6}/metadata/GENERATION_RESULTS.json", results)
    return results


# ---------------------------------------------------------------------
# STAGE 2: DOWNSTREAM
# ---------------------------------------------------------------------

def _worker_init():
    global trajectory_to_hits, seeding_and_iterative_fit, apply_signal_region_cuts
    global select_reconstructed_plane, check_hit_multiplicity, vertex_relative_hits
    import trajectory_to_hits as tth
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    tth.integrate_trajectory = integrate_trajectory_fast_v2
    trajectory_to_hits = tth
    from coplanarity_fit import (seeding_and_iterative_fit as sif, apply_signal_region_cuts as asrc,
                                  select_reconstructed_plane as srp, check_hit_multiplicity as chm,
                                  vertex_relative_hits as vrh)
    seeding_and_iterative_fit, apply_signal_region_cuts = sif, asrc
    select_reconstructed_plane, check_hit_multiplicity, vertex_relative_hits = srp, chm, vrh


def analyze_event(row, mq_gev, lambda_gev, charge1, charge2, seed):
    rng = np.random.default_rng(seed)
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
    t0 = time.perf_counter()
    hits, traj = trajectory_to_hits.simulate_quirk_hits(
        p1, p2, mass_gev=mq_gev, Lambda_gev=lambda_gev, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0)
    n_premerge = traj["n_hits_premerge"]
    max_t_ns = traj["max_hit_t_ns_premerge"]
    geometric_fiducial = (n_premerge == 16)
    timing_ok = (not np.isnan(max_t_ns)) and (max_t_ns < 25.0)
    truth_fiducial = geometric_fiducial and timing_ok

    merged = trajectory_to_hits.merge_neighboring_pixel_hits(hits, adjacency=1)
    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in merged:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    candidates = seeding_and_iterative_fit(hits_by_layer)
    sec3c_winner = select_reconstructed_plane(candidates)
    secIV_winner = apply_signal_region_cuts(candidates)
    hit_mult_pass = check_hit_multiplicity(sec3c_winner["layers"]) if sec3c_winner else False
    wall = time.perf_counter() - t0

    first_failure = None
    if not truth_fiducial:
        first_failure = "fiducial"
    elif sec3c_winner is None:
        first_failure = "no_plane_reconstructed"
    elif not hit_mult_pass:
        first_failure = "hit_multiplicity"
    elif secIV_winner is None:
        first_failure = "signal_region_cuts"

    return {
        "n_hits_premerge": int(n_premerge), "n_hits_postmerge": len(merged),
        "geometric_fiducial": bool(geometric_fiducial), "truth_fiducial": bool(truth_fiducial),
        "n_candidates": len(candidates), "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds_cm": float(sec3c_winner["fit"]["delta_s"]) if sec3c_winner else None,
        "sec3c_dw_cm": float(sec3c_winner["fit"]["delta_w"]) if sec3c_winner else None,
        "hit_multiplicity_pass": bool(hit_mult_pass),
        "final_sec_iv_pass": secIV_winner is not None,
        "first_failure_reason": first_failure,
        "wall_time_s": wall, "seed": seed,
        "nan_ds": bool(sec3c_winner and np.isnan(sec3c_winner["fit"]["delta_s"])),
        "inf_ds": bool(sec3c_winner and np.isinf(sec3c_winner["fit"]["delta_s"])),
    }


def _worker(args):
    row_dict, mq, lam, c1, c2, seed = args
    try:
        return analyze_event(row_dict, mq, lam, c1, c2, seed)
    except Exception as e:
        # A per-event failure must not crash the pool/cell/run. No physics
        # constant is touched here -- this only prevents one bad event from
        # taking down the entire grid; the event is recorded as a technical
        # failure, not silently dropped or reinterpreted as a physics pass/fail.
        return {
            "n_hits_premerge": None, "n_hits_postmerge": None,
            "geometric_fiducial": None, "truth_fiducial": False,
            "n_candidates": None, "sec3c_plane_found": False,
            "sec3c_ds_cm": None, "sec3c_dw_cm": None,
            "hit_multiplicity_pass": False, "final_sec_iv_pass": False,
            "first_failure_reason": "technical_exception",
            "wall_time_s": None, "seed": seed,
            "nan_ds": False, "inf_ds": False,
            "exception_type": type(e).__name__, "exception_message": str(e),
        }


_TRIGGER_CACHE = {}


def get_trigger_passing_events(channel, mass_gev):
    key = (channel, mass_gev)
    if key in _TRIGGER_CACHE:
        return _TRIGGER_CACHE[key]
    tag = f"{channel}_{mass_gev}gev"
    hepmc = f"{HEP_TOOLS_RUNS}/{tag}/Events/run_fig6/tag_1_pythia8_events.hepmc.gz"
    if channel == "EW":
        df = parse_hepmc(hepmc, 9000011, mass_gev, 5.0, True)
    else:
        df = parse_hepmc(hepmc, 1000006, mass_gev, 30.0, False)
    df = df[df["n_quirks_found"] == 2].reset_index(drop=True)
    n_matched = len(df)
    if channel == "colored":
        charge_of = _make_rhadron_charge_lookup()
        df["charge1"] = df["pdg1"].map(lambda p: charge_of(p))
        df["charge2"] = df["pdg2"].map(lambda p: charge_of(p))
        df = df[(df["charge1"].abs() == 1) & (df["charge2"].abs() == 1)].reset_index(drop=True)
    else:
        PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
        df["charge1"] = df["pdg1"].map(PDG_TO_CHARGE)
        df["charge2"] = df["pdg2"].map(PDG_TO_CHARGE)
    n_charge_filtered = len(df)
    trig = df[df["trigger_proxy_pass"]].reset_index(drop=True)
    result = {"trig_df": trig, "n_matched": n_matched, "n_charge_filtered": n_charge_filtered,
              "n_trigger": len(trig)}
    _TRIGGER_CACHE[key] = result
    return result


def wilson_interval(k, n, z=1.96):
    if n == 0:
        return None, None
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    hw = (z / denom) * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    return max(0.0, center - hw), min(1.0, center + hw)


def process_one_cell(channel, mass_gev, lambda_kev, downstream_seed_base, cell_idx, n_cells):
    mass_gev = int(mass_gev)
    lambda_kev = int(lambda_kev)
    lambda_gev = LAMBDA_GEV_MAP[lambda_kev]
    cell_dir = f"{FIG6}/generation/{channel}_{mass_gev}GeV/downstream_L{lambda_kev}keV"
    os.makedirs(f"{cell_dir}/checkpoints", exist_ok=True)
    os.makedirs(f"{cell_dir}/cache", exist_ok=True)
    done_marker = f"{cell_dir}/checkpoints/DONE.txt"
    if os.path.exists(done_marker):
        return {"status": "already_done"}

    trig_info = get_trigger_passing_events(channel, mass_gev)
    trig_df = trig_info["trig_df"]
    n_trig = len(trig_df)

    progress_path = f"{cell_dir}/checkpoints/progress.json"
    progress = json.load(open(progress_path)) if os.path.exists(progress_path) else {}

    seed_seq = np.random.SeedSequence(int(downstream_seed_base))
    child_seeds = seed_seq.spawn(n_trig) if n_trig > 0 else []

    pending = [i for i in range(n_trig) if str(i) not in progress]
    t_cell_start = time.time()
    n_done_this_cell = 0

    if pending:
        with mp.Pool(processes=N_WORKERS, initializer=_worker_init) as pool:
            for chunk_start in range(0, len(pending), CHUNK_SIZE):
                chunk = pending[chunk_start:chunk_start + CHUNK_SIZE]
                job_args = []
                for i in chunk:
                    row = trig_df.iloc[i]
                    seed = int(child_seeds[i].generate_state(1)[0])
                    job_args.append((row.to_dict(), mass_gev, lambda_gev,
                                      float(row["charge1"]), float(row["charge2"]), seed))
                chunk_results = pool.map(_worker, job_args)
                for i, res in zip(chunk, chunk_results):
                    progress[str(i)] = res
                atomic_write_json(progress_path, progress)
                n_done_this_cell += len(chunk)
                elapsed = time.time() - T_START
                rate = (time.time() - t_cell_start) / max(n_done_this_cell, 1)
                update_status(stage="downstream", current_cell=f"{channel}_{mass_gev}GeV_L{lambda_kev}keV",
                               cell_progress=f"{cell_idx}/{n_cells}",
                               events_in_cell_done=f"{len(progress)}/{n_trig}",
                               rolling_s_per_event=round(rate, 2))

    df = pd.DataFrame([{"row_index": int(k), **v} for k, v in progress.items()])
    df["channel"] = channel
    df["mass_gev"] = mass_gev
    df["lambda_kev"] = lambda_kev
    summary_path = f"{cell_dir}/summary.csv"
    df.to_csv(summary_path, index=False)

    n_final = int(df["final_sec_iv_pass"].sum()) if len(df) else 0
    n_fid = int(df["truth_fiducial"].sum()) if len(df) else 0
    n_plane = int(df["sec3c_plane_found"].sum()) if len(df) else 0
    n_mult = int(df["hit_multiplicity_pass"].sum()) if len(df) else 0
    lo, hi = wilson_interval(n_final, n_trig) if n_trig else (None, None)

    n_technical_failure = int((df["first_failure_reason"] == "technical_exception").sum()) if len(df) else 0

    cache_npz = f"{cell_dir}/cache/detailed_cache.npz"
    if len(df):
        np.savez_compressed(cache_npz,
                             row_index=df["row_index"].to_numpy(),
                             n_hits_postmerge=pd.to_numeric(df["n_hits_postmerge"], errors="coerce").to_numpy(dtype=float),
                             sec3c_ds_cm=pd.to_numeric(df["sec3c_ds_cm"], errors="coerce").to_numpy(dtype=float),
                             sec3c_dw_cm=pd.to_numeric(df["sec3c_dw_cm"], errors="coerce").to_numpy(dtype=float),
                             final_sec_iv_pass=df["final_sec_iv_pass"].to_numpy(),
                             seed=df["seed"].to_numpy())

    cell_stats = {
        "channel": channel, "mass_gev": mass_gev, "lambda_kev": lambda_kev,
        "n_generated": N_GEN, "n_matched": trig_info["n_matched"],
        "n_charge_filtered": trig_info["n_charge_filtered"], "n_trigger": n_trig,
        "n_fiducial": n_fid, "n_plane": n_plane, "n_multiplicity": n_mult, "n_final": n_final,
        "n_technical_failure": n_technical_failure,
        "eps_trigger": trig_info["n_trigger"] / trig_info["n_charge_filtered"] if trig_info["n_charge_filtered"] else None,
        "eps_fiducial": n_fid / n_trig if n_trig else None,
        "eps_reconstruction": n_final / n_fid if n_fid else None,
        "eps_total": n_final / n_trig if n_trig else None,
        "wilson_95_lo": lo, "wilson_95_hi": hi,
        "nan_count": int(df["nan_ds"].sum()) if len(df) else 0,
        "inf_count": int(df["inf_ds"].sum()) if len(df) else 0,
        "downstream_wall_s": sum(v["wall_time_s"] for v in progress.values() if v.get("wall_time_s") is not None),
        "low_statistics": bool(n_trig < 50 or (n_trig and (hi - lo) / max(n_final / n_trig, 1e-9) > 0.4 if n_trig and n_final else True)),
    }
    atomic_write_json(f"{cell_dir}/checkpoints/cell_stats.json", cell_stats)
    with open(done_marker, "w") as f:
        f.write(f"OK n_trig={n_trig} n_final={n_final}\n")
    return {"status": "ok", **cell_stats}


def stage2_downstream(grid):
    grid = grid.sort_values(["channel", "mass_gev", "lambda_kev"]).reset_index(drop=True)
    n_cells = len(grid)
    all_results = []
    for idx, row in grid.iterrows():
        # runtime guard
        elapsed_h = (time.time() - T_START) / 3600
        if elapsed_h > RUNTIME_GUARD_HOURS:
            update_status(stage="STOPPED_RUNTIME_GUARD", elapsed_h=elapsed_h)
            print(f"RUNTIME GUARD TRIGGERED at {elapsed_h:.1f}h. Stopping before cell {idx}/{n_cells}.")
            break
        r = process_one_cell(row["channel"], row["mass_gev"], row["lambda_kev"],
                              row["downstream_seed_base"], idx, n_cells)
        all_results.append({**r, "channel": row["channel"], "mass_gev": row["mass_gev"],
                             "lambda_kev": row["lambda_kev"]})
        print(f"[{idx+1}/{n_cells}] {row['channel']} {row['mass_gev']}GeV L{row['lambda_kev']}keV: {r['status']}")
    pd.DataFrame(all_results).to_csv(f"{FIG6}/metadata/ALL_CELL_RESULTS.csv", index=False)
    return all_results


if __name__ == "__main__":
    os.makedirs(f"{FIG6}/RUNTIME", exist_ok=True)
    os.makedirs(f"{FIG6}/metadata", exist_ok=True)
    update_status(stage="starting", pid=os.getpid())
    grid = load_grid()
    print("=== STAGE 1: GENERATION (13 distinct mass points, sequential) ===")
    stage1_generation(grid)
    print("=== STAGE 2: DOWNSTREAM (91 grid cells, 3-worker parallel per cell) ===")
    stage2_downstream(grid)
    update_status(stage="COMPLETE")
    print("=== PHASE 5 PRODUCTION COMPLETE ===")
