# Figure 6 Phase 5 Production — PAUSED for urgent colored-quirk audit

**Pause timestamp:** 2026-09-24T09:52:03Z (state recorded) — processes
terminated shortly after (driver via SIGTERM, then SIGKILL after 3s;
2 orphaned worker children required an additional SIGTERM/SIGKILL pass
since SIGKILL of the parent does not clean up `multiprocessing.Pool`
workers). Confirmed via `pgrep`: zero `run_phase5` processes remain.

## Process tree at pause

- Driver PID 33950 (parent 14), running 23h09m49s total since last resume.
- 3 worker children (89129, 89130, 89131), 5h03m52s into the active cell's
  `multiprocessing.Pool`.

## Completed work (safe, will NOT be recomputed on resume)

- **All 13 generation points**: complete, validated, `checkpoints_DONE_generation.txt`
  present for each (untouched by this pause).
- **20 of 91 downstream grid cells**: complete, `DONE.txt` present for each
  (full list in the pre-pause state log, captured immediately before
  termination). Resume logic (`if os.path.exists(done_marker): return
  already_done`) skips all 20 unconditionally.
- **60 of 135 events in the active (21st) cell** (`EW_400GeV_L10keV`):
  checkpointed to `checkpoints/progress.json`
  (SHA-256 `aa59eaa418c8339f1b9dcb408ab1310e27df7dfd6dc76011c5129d52ff2a0c2b`
  at pause time). Resume logic skips any event index already present as a
  key in this file.

## Work that will be recomputed on resume (disclosed, bounded loss)

- The **in-flight, third chunk** of `EW_400GeV_L10keV` (events 61-90 of
  135) — up to 30 events. None of these had been written to
  `progress.json` yet (chunk-level atomic write only happens after the
  full `pool.map()` call for that chunk returns), so this is not
  "completed work" being discarded — it was never checkpointed as
  complete. This chunk was unusually slow (Λ=10keV is the most
  computationally expensive value in the grid; the pool's cumulative
  runtime, 5h03m, spans all 3 chunks processed so far in this cell, not
  just the in-flight one).

## Resume command

```
cd /home/rafia/coplanarity_study
source /home/rafia/miniforge3/etc/profile.d/conda.sh && conda activate hep
LOG=05_coplanarity_analysis/figure6_full_v1/LOGS/phase5_production.log
PYTHONUNBUFFERED=1 nohup python3 05_coplanarity_analysis/figure6_full_v1/run_phase5_production.py > "$LOG" 2>&1 < /dev/null &
disown
echo $! > 05_coplanarity_analysis/figure6_full_v1/RUNTIME/production.pid
```

This will: skip all 13 generation points (`already_done`), skip all 20
completed downstream cells, resume `EW_400GeV_L10keV` from event 61
(30 events already-checkpointed events in that cell are also skipped),
then continue through the remaining 71 grid cells.

## Explicit confirmation

**Not resumed automatically. Awaiting authorization**, per the audit
instruction. No new generation, detector simulation, trajectory
propagation, or Figure 7 work has been started during this pause.
