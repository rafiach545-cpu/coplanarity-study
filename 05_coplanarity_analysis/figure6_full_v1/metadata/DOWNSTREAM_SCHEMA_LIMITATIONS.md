# Downstream data-schema: what the active run captures vs. what was requested

The Phase 5 driver (PID 23769) was already running generation when the
expanded data-capture requirements (Sections H-L of the continue-uninterrupted
instruction) arrived. Editing `run_phase5_production.py` on disk does **not**
change the behavior of the already-running process (Python does not hot-reload
a running interpreter's function definitions) — the driver will use the
`process_one_cell`/`analyze_event` code as it existed at launch when it
reaches the downstream stage.

Per the explicit instruction to protect the healthy run ("do not restart it,
do not change worker count, do not overwrite completed output"), the driver
was **not** killed and relaunched to pick up a richer schema. This section
documents exactly what is and is not captured as a result, so no claim is
made about data that does not exist.

## Captured by the active run (per event, in `checkpoints/progress.json` and
`summary.csv` per grid cell)

`n_hits_premerge`, `n_hits_postmerge`, `geometric_fiducial`, `truth_fiducial`,
`n_candidates` (count of surviving grown candidates, not raw seed count),
`sec3c_plane_found`, `sec3c_ds_cm`, `sec3c_dw_cm`, `hit_multiplicity_pass`,
`final_sec_iv_pass`, `first_failure_reason`, `wall_time_s`, `seed`,
`nan_ds`, `inf_ds`.

Per grid cell, in `checkpoints/cell_stats.json`: N_generated (=2000),
N_matched, N_charge_filtered, N_trigger, N_fiducial, N_plane, N_multiplicity,
N_final, ε_trigger, ε_fiducial, ε_reconstruction, ε_total, Wilson 95% on
N_final, NaN/Inf counts, downstream wall time, a `low_statistics` flag.

Also saved: `cache/detailed_cache.npz` per cell (compressed, per-event
row_index/n_hits_postmerge/ds/dw/final_pass/seed arrays).

## Requested but NOT captured by the active run (Sections H-J)

- **Raw hit-level records** (unique raw-hit ID, per-hit layer/x/y/z/time,
  detector type, pixel/SCT flag, quantization indices, acceptance status,
  per-hit rejection reason) — only aggregate counts (premerge/postmerge)
  are saved, not the individual hits.
- **Merged-hit provenance** (merged-hit ID → source raw-hit IDs) — not saved.
- **All-candidates reconstruction cache** (every seed's hit membership,
  every grown candidate's Δs/Δw/plane normal, not just the winning one) —
  only the winning candidate's Δs/Δw survive; losing candidates are
  discarded in-memory by `seeding_and_iterative_fit` and never serialized.
- **Raw N_seed vs. N_candidate distinction** — `n_candidates` in the saved
  schema is the count of *fully-grown* candidates (post-iterative-fit), not
  the raw seed-pair count before growth; the two are conflated.
- **Per-candidate layer-coverage histogram** (N_ge4_layers, N_8_layers) —
  not separately tracked; only the winning candidate's final layer list
  survives (used for the `hit_multiplicity_pass` check), not a distribution
  across all candidates.
- **Trajectory-level fields** (RK4 step count, timestep statistics, maximum
  radius/time reached, per-event cache hit/miss, retry count, integrator
  warning/error fields) — the integrator runs to completion or raises; step
  counts are not currently returned to the caller.
- **Worker ID per event** — `multiprocessing.Pool.map` does not expose which
  worker handled which job to the caller in the current implementation.

## What IS recoverable post-hoc from saved data (partially closing the gap)

- **N_Delta_s_pass / N_Delta_w_pass** (requested in Section K, item 15-16):
  recoverable by comparing each event's saved `sec3c_ds_cm`/`sec3c_dw_cm`
  against the paper's own thresholds (Δs<0.01cm, Δw<1.0cm) — computed in
  `scripts/build_full_cutflow.py`.
- **N_any_detector_hit**: recoverable from `n_hits_premerge > 0`.
- **N_technical_failure**: inferable (conservatively, likely an
  undercount) from `nan_ds`/`inf_ds` flags; no separate exception/error
  field exists, so a Python exception during `analyze_event` would currently
  propagate as a `multiprocessing.Pool` failure rather than a logged,
  per-event technical-failure record. (No such failure has been observed in
  this project's downstream code across the three-point pilot, the 47-event
  throughput test, or this smoke test — but the absence of a dedicated field
  means one occurring during full production would surface as a pool/chunk
  failure, not a silently-recorded per-event flag.)

## Disposition

This is disclosed as a genuine, accepted limitation of this production run,
not hidden. It does not affect the correctness of any number that IS
reported (all reported quantities trace to real saved data), only the
*granularity* of what can be reconstructed after the fact for deeper
diagnostic work (e.g. "show me every candidate considered for event X," or
"how many RK4 steps did this specific slow event take in production" — the
latter WAS measured in aggregate via the separate cProfile investigation
during Phase 0/4, just not per-event in production). Any future rerun that
requires this level of detail should use an upgraded schema, launched fresh
(not as a hot-patch to a running process).
