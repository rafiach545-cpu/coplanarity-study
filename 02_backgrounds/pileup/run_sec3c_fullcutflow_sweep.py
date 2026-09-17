"""
Analysis-only recovery of Sec IIIC/Sec IV full cutflow quantities for the
existing 5-configuration pile-up sweep (mu=0,5,10,20,50, n=5000, seed=90210777).

Reuses the IDENTICAL deterministic per-event seed convention
(SeedSequence([seed, int(mu), i]).spawn(2) -> (rng_pileup, rng_suppression))
as run_sweep_resumable.py, against the SAME minbias_pool_20000_ANCESTRY_v1.csv
pool -- this reproduces bit-identical hits to the original sweep, it does not
generate any new physics. Only the analysis-stage diagnostics differ (via
run_one_background_event_full_cutflow, which additionally records the Sec
IIIC winning plane and Sec IV hit-multiplicity/Delta_s checks that the
original sweep never recorded).

Checkpointed (append + flush every `checkpoint_every` events, resumable via
<out>.checkpoint) so a crash does not lose completed work and a resumed run
is bit-identical to an uninterrupted one.
"""
import sys
import os
import time
import json
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from run_pileup_fake_background_suppressed import (
    run_one_background_event_full_cutflow, ANCESTRY_POOL_PATH, DETECTOR_MODEL_VERSION)
from pileup_hits_suppressed import build_ancestry_pool_index
from tracking_efficiency import BASELINE_SELECTION
from provenance import build_provenance

SEED = 90210777

RESULT_COLUMNS = [
    "event_i", "n_candidates_raw", "sec3c_plane_found", "sec3c_ds", "sec3c_dw",
    "sec3c_n_hits", "sec3c_n_layers", "hit_multiplicity_pass",
    "delta_s_pass_0p01", "final_sec_iv_pass", "has_4_of_8_plane", "has_8_of_8_plane",
]


def run_resumable_fullcutflow(mu, n_events, out_path, seed=SEED,
                                selection=BASELINE_SELECTION, checkpoint_every=100,
                                overwrite=False):
    ckpt_path = out_path + ".checkpoint"
    done_path = out_path + ".DONE"

    if os.path.exists(done_path) and not overwrite:
        print(f"SKIP: {out_path} already complete (found {done_path}).")
        return out_path

    start_i = 0
    if os.path.exists(ckpt_path) and os.path.exists(out_path):
        with open(ckpt_path) as f:
            start_i = int(f.read().strip())
        print(f"RESUMING {out_path} from event {start_i}/{n_events} (checkpoint found)")
    else:
        if os.path.exists(out_path):
            os.remove(out_path)

    pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))

    t0 = time.time()
    write_header = (start_i == 0)
    buf = []
    for i in range(start_i, n_events):
        ss = np.random.SeedSequence([seed, int(mu), i])
        child_pileup, child_suppression = ss.spawn(2)
        rng_pileup = np.random.default_rng(child_pileup)
        rng_suppression = np.random.default_rng(child_suppression)
        r = run_one_background_event_full_cutflow(
            mu, rng_pileup, rng_suppression, pool_index, selection=selection)
        r["event_i"] = i
        buf.append(r)

        if len(buf) >= checkpoint_every or i == n_events - 1:
            df = pd.DataFrame(buf, columns=RESULT_COLUMNS)
            df.to_csv(out_path, mode="a" if not write_header else "w",
                      header=write_header, index=False)
            write_header = False
            buf = []
            with open(ckpt_path, "w") as f:
                f.write(str(i + 1))
            print(f"  mu={mu}: {i+1}/{n_events} done, {time.time()-t0:.0f}s elapsed", flush=True)

    dt = time.time() - t0
    with open(done_path, "w") as f:
        f.write(f"completed {n_events} events in {dt:.1f}s at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    prov = build_provenance(
        study_type="PILEUP_SEC3C_FULLCUTFLOW_ANALYSIS_ONLY_RERUN", mu=mu,
        n_events_processed=n_events, seed=seed,
        rng_stream_convention="SeedSequence([seed,int(mu),i]).spawn(2) -> (rng_pileup, rng_suppression) -- IDENTICAL to run_sweep_resumable.py",
        detector_model_version=DETECTOR_MODEL_VERSION,
        pool_path=ANCESTRY_POOL_PATH,
        extra={"tracking_efficiency_selection": selection,
               "checkpoint_every": checkpoint_every, "wall_time_s": dt,
               "note": "analysis-only rerun over existing deterministic seeds/pool; no new physics generated"},
    )
    with open(out_path + ".provenance.json", "w") as f:
        json.dump(prov, f, indent=2, default=str)

    print(f"[{out_path}] DONE, wall time {dt:.1f}s")
    return out_path


if __name__ == "__main__":
    n_events = 5000
    out_dir = "/home/rafia/coplanarity_study/05_coplanarity_analysis/sweep_mu_2026-09-16"
    for mu in [0, 5, 10, 20, 50]:
        out_path = f"{out_dir}/pileup_mu{int(mu)}_n5000_sec3c_fullcutflow_v1.csv"
        print(f"=== mu={mu} ===", flush=True)
        run_resumable_fullcutflow(mu, n_events, out_path)
