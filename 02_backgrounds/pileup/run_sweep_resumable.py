"""
Checkpoint/resume-capable runner for the 5-configuration mu sweep (mu=0,5,
10,20,50 at n=5000 each), Loose selection, track-level suppression enabled.

CHECKPOINTING: writes each event's result to the output CSV immediately
(append mode, flushed) as it completes, and maintains a small
`<out>.checkpoint` file recording the number of events completed so far. On
restart with the same output path, if a checkpoint exists, resumes from
event index = checkpoint count instead of restarting from 0 -- the SAME
per-event SeedSequence([seed, mu, i]) convention is used regardless of
resume point, so a resumed run's later events are bit-identical to what an
uninterrupted run would have produced (verified in test_checkpoint_resume.py).

Never overwrites a COMPLETED (n_events reached) output -- raises if the
target is already complete and overwrite=False.
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
    run_one_background_event_suppressed, ANCESTRY_POOL_PATH, DETECTOR_MODEL_VERSION)
from pileup_hits_suppressed import build_ancestry_pool_index
from tracking_efficiency import BASELINE_SELECTION
from provenance import build_provenance

RESULT_COLUMNS = [
    "event_i", "n_pu_interactions", "n_pu_particles_propagated",
    "n_pu_hits_before_suppression", "n_pu_hits_after_suppression",
    "n_tracks_primary", "n_tracks_primary_removed", "n_tracks_primary_kept",
    "n_tracks_secondary", "n_tracks_ambiguous", "per_layer_hit_counts",
    "n_candidates", "best_candidate_n_layers_with_hit",
    "has_4_of_8_plane", "has_8_of_8_plane",
]


def run_resumable(mu, n_events, out_path, seed=90210777, selection=BASELINE_SELECTION,
                   checkpoint_every=50, overwrite=False):
    ckpt_path = out_path + ".checkpoint"
    done_path = out_path + ".DONE"

    if os.path.exists(done_path) and not overwrite:
        raise FileExistsError(f"{out_path} already complete (found {done_path}). "
                               "Pass overwrite=True or use a new path.")

    start_i = 0
    if os.path.exists(ckpt_path) and os.path.exists(out_path):
        with open(ckpt_path) as f:
            start_i = int(f.read().strip())
        print(f"RESUMING {out_path} from event {start_i}/{n_events} (checkpoint found)")
    else:
        # fresh start: truncate any stale partial output
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
        r = run_one_background_event_suppressed(
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

    dt = time.time() - t0
    with open(done_path, "w") as f:
        f.write(f"completed {n_events} events in {dt:.1f}s at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    prov = build_provenance(
        study_type="PILEUP_FAKE_BACKGROUND", mu=mu, n_events_processed=n_events,
        seed=seed, rng_stream_convention="SeedSequence([seed,int(mu),i]).spawn(2) -> (rng_pileup, rng_suppression)",
        detector_model_version=DETECTOR_MODEL_VERSION,
        pool_path=ANCESTRY_POOL_PATH,  # BUG FIX (audit, 2026-09-17): build_provenance() defaults
        # pool_path to provenance.POOL_PATH (minbias_pool_20000_FINAL.csv), but this driver
        # actually samples from the ANCESTRY pool -- the 5 already-committed sweep provenance
        # JSONs incorrectly recorded the FINAL pool's filename/hash. Fixed here for all future
        # runs; the existing committed JSONs are NOT retroactively edited (see RUN_LOG.md
        # 2026-09-17 errata entry for the correct hash on the record).
        extra={"tracking_efficiency_selection": selection,
               "checkpoint_every": checkpoint_every, "wall_time_s_this_segment": dt},
    )
    with open(out_path + ".provenance.json", "w") as f:
        json.dump(prov, f, indent=2, default=str)

    print(f"[{out_path}] segment wall time {dt:.1f}s, total events now {n_events}")
    return out_path


if __name__ == "__main__":
    mu = float(sys.argv[1])
    n_events = int(sys.argv[2])
    out_path = sys.argv[3]
    run_resumable(mu, n_events, out_path)
