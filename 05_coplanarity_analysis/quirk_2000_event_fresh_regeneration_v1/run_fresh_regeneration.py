#!/usr/bin/env python3
"""
Fresh, independent 2000+2000 event quirk regeneration driver.
See PAPER_REQUIREMENTS.md and CONFIGURATION_FROZEN.json. No prior numerical
results are read anywhere in this script -- only frozen process-card
templates (proc_card structure) and validated physics code (imports) are
reused, per the explicit, logged exceptions in PAPER_REQUIREMENTS.md.
"""
import sys, os, re, json, time, math, hashlib, subprocess
import multiprocessing as mp
import numpy as np
import pandas as pd
from scipy import stats as sps

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1"
HEP_RUNS = "/home/rafia/hep_tools/quirk_2000_fresh_regen_runs"

sys.path.insert(0, f"{BASE}/05_coplanarity_analysis/madgraph_pilot_v1")
sys.path.insert(0, f"{BASE}/01_signal_generation")
sys.path.insert(0, f"{BASE}/04_detector_sim")
sys.path.insert(0, f"{BASE}/05_coplanarity_analysis")
sys.path.insert(0, f"{BASE}/03_trajectory_sim")

from extract_pilot_data import parse_hepmc
from extract_quirk_momenta import _make_rhadron_charge_lookup

CONFIG = json.load(open(f"{OUT}/CONFIGURATION_FROZEN.json"))
LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}
CHUNK_SIZE = 30
N_WORKERS = 3
STATUS_PATH = f"{OUT}/STATUS.json"
T_START = time.time()


def atomic_write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


def update_status(**kw):
    st = {}
    if os.path.exists(STATUS_PATH):
        try: st = json.load(open(STATUS_PATH))
        except Exception: st = {}
    st.update(kw)
    st["last_update_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    st["elapsed_h"] = round((time.time() - T_START) / 3600, 3)
    atomic_write_json(STATUS_PATH, st)


def sha256_of(path):
    if not os.path.exists(path): return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()


def log(msg):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    with open(f"{OUT}/RUN_LOG.md", "a") as f:
        f.write(line + "\n")


# ---------------- Stage 1: generation ----------------

def edit_param_card(path, channel, mass_gev):
    text = open(path).read()
    if channel == "EW":
        text = re.sub(r"(\n\s*9000011\s+)[0-9.eE+-]+(\s+# mqe)", rf"\g<1>{mass_gev:.6e}\g<2>", text)
    else:
        text = re.sub(r"(\n\s*1000006\s+)[0-9.eE+-]+(\s+# mqc)", rf"\g<1>{mass_gev:.6e}\g<2>", text)
    open(path, "w").write(text)


def edit_run_card(path, nevents, seed):
    lines = open(path).readlines()
    out = []
    for line in lines:
        if "= nevents" in line:
            out.append(re.sub(r"^\s*\d+", f"  {nevents}", line))
        elif "= iseed" in line:
            out.append(re.sub(r"^\s*\d+", f"  {seed}", line))
        else:
            out.append(line)
    open(path, "w").writelines(out)


def force_nb_core_1(path):
    text = open(path).read()
    if "nb_core = 1" not in text:
        text = text.replace("# nb_core = None", "nb_core = 1")
    open(path, "w").write(text)


def run_generation(sample_key):
    cfg = CONFIG["samples"][sample_key]
    channel = cfg["channel"]
    mass = cfg["mQ_GeV"]
    seed = cfg["generation_seed"]
    n_req = cfg["N_requested"]
    template = cfg["template_process_dir"].split(" (")[0]
    run_dir = f"{HEP_RUNS}/{sample_key}"
    done_marker = f"{run_dir}/checkpoints_DONE_generation.txt"
    gen_out_dir = f"{OUT}/generation/{sample_key}"

    if os.path.exists(done_marker):
        log(f"{sample_key}: generation already_done, skipping")
        return

    if not os.path.exists(run_dir):
        os.makedirs(HEP_RUNS, exist_ok=True)
        subprocess.run(["rsync", "-a", "--exclude=Events/run_01", "--exclude=Events/run_fresh",
                         f"{template}/", f"{run_dir}/"], check=True)
        edit_param_card(f"{run_dir}/Cards/param_card.dat", channel, mass)

    edit_run_card(f"{run_dir}/Cards/run_card.dat", n_req, seed)
    force_nb_core_1(f"{run_dir}/Cards/me5_configuration.txt")

    log_path = f"{gen_out_dir}/generation.log"
    env = os.environ.copy()
    env.pop("PYTHIA8DATA", None)
    t0 = time.time()
    with open(log_path, "w") as logf:
        proc = subprocess.run(["./bin/generate_events", "run_fresh", "-f"], cwd=run_dir,
                               env=env, stdout=logf, stderr=subprocess.STDOUT, timeout=3600)
    wall = time.time() - t0
    events_dir = f"{run_dir}/Events/run_fresh"
    log_text = open(log_path).read()
    success = (proc.returncode == 0) and os.path.exists(f"{events_dir}/tag_1_pythia8_events.hepmc.gz")

    m_lhe = re.search(r"Cross-section\s*:\s*([0-9.eE+-]+)\s*\+-\s*([0-9.eE+-]+)\s*pb", log_text)
    m_matched = re.search(r"Nb of events after matching/merging\s*:\s*(\d+)", log_text)
    m_matched_xsec = re.search(r"Matched cross-section\s*:\s*([0-9.eE+-]+)\s*\+-\s*([0-9.eE+-]+)", log_text)

    if not success:
        failed_dir = f"{run_dir}/Events/FAILED_ATTEMPT_NOT_AUTHORITATIVE_1"
        if os.path.exists(events_dir):
            os.rename(events_dir, failed_dir)
        log(f"{sample_key}: generation FAILED, exit_code={proc.returncode}, log preserved at {log_path}")
        raise RuntimeError(f"{sample_key} generation failed")

    stats = {
        "sample": sample_key, "channel": channel, "mQ_GeV": mass, "seed": seed,
        "N_requested": n_req,
        "parton_xsec_pb": float(m_lhe.group(1)) if m_lhe else None,
        "parton_xsec_err_pb": float(m_lhe.group(2)) if m_lhe else None,
        "N_matched": int(m_matched.group(1)) if m_matched else None,
        "matched_xsec_pb": float(m_matched_xsec.group(1)) if m_matched_xsec else None,
        "matched_xsec_err_pb": float(m_matched_xsec.group(2)) if m_matched_xsec else None,
        "wall_s": wall, "exit_code": proc.returncode,
        "hepmc_sha256": sha256_of(f"{events_dir}/tag_1_pythia8_events.hepmc.gz"),
        "lhe_sha256": sha256_of(f"{events_dir}/unweighted_events.lhe.gz"),
        "run_card_sha256": sha256_of(f"{run_dir}/Cards/run_card.dat"),
        "param_card_sha256": sha256_of(f"{run_dir}/Cards/param_card.dat"),
        "banner_path": f"{events_dir}/run_fresh_tag_1_banner.txt",
    }
    os.makedirs(gen_out_dir, exist_ok=True)
    atomic_write_json(f"{gen_out_dir}/generation_stats.json", stats)
    with open(done_marker, "w") as f:
        f.write(f"OK wall_s={wall:.1f} N_matched={stats['N_matched']}\n")
    log(f"{sample_key}: generation OK, N_matched={stats['N_matched']}, wall={wall:.1f}s")


# ---------------- Stage 2: extraction, charge/trigger accounting ----------------

def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    phat = k / n; denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    hw = (z / denom) * math.sqrt(max(0.0, phat * (1 - phat) / n + z**2 / (4 * n**2)))
    return max(0.0, center - hw), min(1.0, center + hw)


def cp(k, n, alpha=0.05):
    if n == 0: return (None, None)
    lo = sps.beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = sps.beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return lo, hi


def extract_and_account(sample_key):
    cfg = CONFIG["samples"][sample_key]
    channel = cfg["channel"]
    mass = cfg["mQ_GeV"]
    run_dir = f"{HEP_RUNS}/{sample_key}"
    hepmc = f"{run_dir}/Events/run_fresh/tag_1_pythia8_events.hepmc.gz"

    if channel == "EW":
        df = parse_hepmc(hepmc, 9000011, mass, 5.0, True)
    else:
        df = parse_hepmc(hepmc, 1000006, mass, 30.0, False)
    N_showered = len(df)
    df = df[df["n_quirks_found"] == 2].reset_index(drop=True)
    N_matched = len(df)

    accounting = {"sample": sample_key, "N_showered": N_showered, "N_matched": N_matched}

    if channel == "colored":
        charge_of = _make_rhadron_charge_lookup()
        df["charge1"] = df["pdg1"].map(lambda p: charge_of(p))
        df["charge2"] = df["pdg2"].map(lambda p: charge_of(p))
        both_neutral = ((df["charge1"].abs() < 0.5) & (df["charge2"].abs() < 0.5))
        one_charged = (((df["charge1"].abs() >= 0.5) & (df["charge2"].abs() < 0.5)) |
                       ((df["charge1"].abs() < 0.5) & (df["charge2"].abs() >= 0.5)))
        both_charged = ((df["charge1"].abs() >= 0.5) & (df["charge2"].abs() >= 0.5))
        accounting.update({
            "N_both_neutral": int(both_neutral.sum()),
            "N_one_charged": int(one_charged.sum()),
            "N_both_charged": int(both_charged.sum()),
            "N_charge_filtered": int(both_charged.sum()),
        })
        n_trig_matched = int((df["trigger_proxy_pass"] == True).sum())  # noqa: E712
        dfc = df[both_charged].reset_index(drop=True)
        n_trig_charge_filtered = int((dfc["trigger_proxy_pass"] == True).sum())  # noqa: E712
        accounting.update({
            "N_trigger_of_full_matched": n_trig_matched,
            "eps_trig_of_full_matched": n_trig_matched / N_matched if N_matched else None,
            "N_trigger_AND_charge_filtered": n_trig_charge_filtered,
            "N_trigger_of_charge_filtered": n_trig_charge_filtered,
            "eps_trig_of_charge_filtered": n_trig_charge_filtered / len(dfc) if len(dfc) else None,
            "joint_trigger_and_charge_survival_prob": n_trig_charge_filtered / N_matched if N_matched else None,
        })
        propagate_df = dfc[dfc["trigger_proxy_pass"] == True].reset_index(drop=True)  # noqa: E712
    else:
        PDG_TO_CHARGE = {9000011: -1.0, -9000011: 1.0}
        df["charge1"] = df["pdg1"].map(PDG_TO_CHARGE)
        df["charge2"] = df["pdg2"].map(PDG_TO_CHARGE)
        n_trig = int((df["trigger_proxy_pass"] == True).sum())  # noqa: E712
        accounting.update({
            "N_trigger_of_full_matched": n_trig,
            "eps_trig_of_full_matched": n_trig / N_matched if N_matched else None,
        })
        propagate_df = df[df["trigger_proxy_pass"] == True].reset_index(drop=True)  # noqa: E712

    accounting["N_to_propagate"] = len(propagate_df)
    os.makedirs(f"{OUT}/events/{sample_key}", exist_ok=True)
    df.to_csv(f"{OUT}/events/{sample_key}/matched_events_full.csv", index=False)
    propagate_df.to_csv(f"{OUT}/events/{sample_key}/trigger_passing_events.csv", index=False)
    atomic_write_json(f"{OUT}/cutflows/{sample_key}_charge_trigger_accounting.json", accounting)
    log(f"{sample_key}: N_matched={N_matched}, N_to_propagate={len(propagate_df)}")
    return propagate_df, accounting


# ---------------- Stage 3: downstream (trajectory, detector, reconstruction) ----------------

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


def analyze_event(row, mq_gev, lambda_gev, charge1, charge2, seed, event_idx):
    t0 = time.perf_counter()
    try:
        rng = np.random.default_rng(seed)
        p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
        p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
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
        per_layer_raw = {k: 0 for k in range(1, 9)}
        for h in hits:
            per_layer_raw[LAYER_NAME_TO_IDX[h["layer"]]] += 1
        per_layer_merged = {k: 0 for k in range(1, 9)}
        for h in merged:
            hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
            hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
            per_layer_merged[LAYER_NAME_TO_IDX[h["layer"]]] += 1

        candidates = seeding_and_iterative_fit(hits_by_layer)
        sec3c_winner = select_reconstructed_plane(candidates)
        secIV_winner = apply_signal_region_cuts(candidates)
        hit_mult_pass = check_hit_multiplicity(sec3c_winner["layers"]) if sec3c_winner else False
        wall = time.perf_counter() - t0

        first_failure = None
        if not truth_fiducial: first_failure = "fiducial"
        elif sec3c_winner is None: first_failure = "no_plane_reconstructed"
        elif not hit_mult_pass: first_failure = "hit_multiplicity"
        elif secIV_winner is None: first_failure = "signal_region_cuts"

        return {
            "event_idx": event_idx, "seed": seed,
            "n_hits_premerge": int(n_premerge), "n_hits_postmerge": len(merged),
            "per_layer_raw": per_layer_raw, "per_layer_merged": per_layer_merged,
            "geometric_fiducial": bool(geometric_fiducial), "truth_fiducial": bool(truth_fiducial),
            "n_candidates": len(candidates), "sec3c_plane_found": sec3c_winner is not None,
            "sec3c_ds_cm": float(sec3c_winner["fit"]["delta_s"]) if sec3c_winner else None,
            "sec3c_dw_cm": float(sec3c_winner["fit"]["delta_w"]) if sec3c_winner else None,
            "hit_multiplicity_pass": bool(hit_mult_pass),
            "final_sec_iv_pass": secIV_winner is not None,
            "first_failure_reason": first_failure, "wall_time_s": wall,
            "nan_ds": bool(sec3c_winner and np.isnan(sec3c_winner["fit"]["delta_s"])),
            "inf_ds": bool(sec3c_winner and np.isinf(sec3c_winner["fit"]["delta_s"])),
            "status": "ok", "error": None,
        }
    except Exception as e:
        return {"event_idx": event_idx, "seed": seed, "status": "error", "error": f"{type(e).__name__}: {e}",
                "first_failure_reason": "technical_exception", "wall_time_s": time.perf_counter() - t0,
                "truth_fiducial": False, "sec3c_plane_found": False, "final_sec_iv_pass": False,
                "n_hits_premerge": None, "n_hits_postmerge": None, "n_candidates": None,
                "sec3c_ds_cm": None, "sec3c_dw_cm": None, "hit_multiplicity_pass": False,
                "nan_ds": False, "inf_ds": False}


def _worker(args):
    row_dict, mq, lam, c1, c2, seed, idx = args
    return analyze_event(row_dict, mq, lam, c1, c2, seed, idx)


def run_downstream(sample_key, propagate_df):
    cfg = CONFIG["samples"][sample_key]
    lambda_gev = cfg["Lambda_GeV"]
    mass = cfg["mQ_GeV"]
    seed_base = cfg["downstream_seed_base"]
    n_total = len(propagate_df)

    ckpt_path = f"{OUT}/checkpoints/{sample_key}_progress.json"
    progress = json.load(open(ckpt_path)) if os.path.exists(ckpt_path) else {}
    seed_seq = np.random.SeedSequence(seed_base)
    child_seeds = seed_seq.spawn(n_total)
    pending = [i for i in range(n_total) if str(i) not in progress]

    if pending:
        with mp.Pool(processes=N_WORKERS, initializer=_worker_init) as pool:
            for chunk_start in range(0, len(pending), CHUNK_SIZE):
                chunk = pending[chunk_start:chunk_start + CHUNK_SIZE]
                job_args = []
                for i in chunk:
                    row = propagate_df.iloc[i]
                    seed = int(child_seeds[i].generate_state(1)[0])
                    job_args.append((row.to_dict(), mass, lambda_gev,
                                      float(row["charge1"]), float(row["charge2"]), seed, i))
                results = pool.map(_worker, job_args)
                for r in results:
                    progress[str(r["event_idx"])] = r
                atomic_write_json(ckpt_path, progress)
                update_status(sample=sample_key, stage="downstream",
                               events_done=f"{len(progress)}/{n_total}")
                log(f"{sample_key}: downstream {len(progress)}/{n_total} checkpointed")

    df = pd.DataFrame([{"row_index": int(k), **v} for k, v in progress.items()]).sort_values("row_index")
    os.makedirs(f"{OUT}/reconstruction/{sample_key}", exist_ok=True)
    df.to_csv(f"{OUT}/reconstruction/{sample_key}/per_event_results.csv", index=False)
    return df


# ---------------- Stage 4: statistics ----------------

def build_statistics(sample_key, accounting, recon_df):
    n_fid = int(recon_df["truth_fiducial"].sum())
    n_plane = int(recon_df["sec3c_plane_found"].sum())
    n_mult = int(recon_df["hit_multiplicity_pass"].sum())
    n_final = int(recon_df["final_sec_iv_pass"].sum())
    n_trig = accounting["N_to_propagate"]

    transitions = [
        ("trigger_to_fiducial", n_fid, n_trig),
        ("fiducial_to_plane_SecIIIC", n_plane, n_fid),
        ("plane_to_multiplicity", n_mult, n_plane),
        ("fiducial_to_final_SecIV", n_final, n_fid),
    ]
    rows = []
    for name, k, n in transitions:
        w95 = wilson(k, n, 1.96); w68 = wilson(k, n, 1.0); c95 = cp(k, n, 0.05)
        rows.append({"transition": name, "numerator": k, "denominator": n,
                     "conditional_eff": k / n if n else None,
                     "wilson68_lo": w68[0], "wilson68_hi": w68[1],
                     "wilson95_lo": w95[0], "wilson95_hi": w95[1],
                     "cp95_lo": c95[0], "cp95_hi": c95[1]})
    stats_df = pd.DataFrame(rows)
    os.makedirs(f"{OUT}/statistics", exist_ok=True)
    stats_df.to_csv(f"{OUT}/statistics/{sample_key}_cutflow_statistics.csv", index=False)

    failure_counts = recon_df["first_failure_reason"].fillna("final_pass").value_counts().to_dict()
    n_nan = int(recon_df["nan_ds"].sum())
    n_inf = int(recon_df["inf_ds"].sum())
    n_dup = int(recon_df["event_idx"].duplicated().sum())

    summary = {
        "sample": sample_key, "N_fiducial": n_fid, "N_plane_SecIIIC": n_plane,
        "N_hit_multiplicity": n_mult, "N_final_SecIV": n_final,
        "eps_reco_paper_defined_N_plane_over_N_fid": n_plane / n_fid if n_fid else None,
        "sec_iv_final_pass_rate_N_final_over_N_fid": n_final / n_fid if n_fid else None,
        "failure_reason_counts": failure_counts,
        "nan_count": n_nan, "inf_count": n_inf, "duplicate_event_count": n_dup,
        "total_downstream_wall_s": float(recon_df["wall_time_s"].sum()),
    }
    atomic_write_json(f"{OUT}/statistics/{sample_key}_summary.json", summary)
    log(f"{sample_key}: N_fid={n_fid} N_plane={n_plane} N_mult={n_mult} N_final={n_final}")
    return summary


# ---------------- Main ----------------

if __name__ == "__main__":
    os.makedirs(f"{OUT}/checkpoints", exist_ok=True)
    update_status(stage="starting", pid=os.getpid())
    order = ["colored_1800GeV_L2keV", "EW_800GeV_L4keV"]
    for sample_key in order:
        update_status(stage="generation", sample=sample_key)
        run_generation(sample_key)
        update_status(stage="extraction", sample=sample_key)
        propagate_df, accounting = extract_and_account(sample_key)
        update_status(stage="downstream", sample=sample_key, total_events=len(propagate_df))
        recon_df = run_downstream(sample_key, propagate_df)
        build_statistics(sample_key, accounting, recon_df)
        log(f"=== {sample_key} COMPLETE ===")
    update_status(stage="COMPLETE")
    log("=== FRESH REGENERATION COMPLETE (both samples) ===")
