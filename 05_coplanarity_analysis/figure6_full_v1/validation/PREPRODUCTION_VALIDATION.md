# Phase 4 — Preproduction validation

## 1. Cache-only validation of the three-point pilot

Rerun of `run_downstream_pipeline.py` after full completion: all 10 events
correctly reported `SKIP (already checkpointed)`, identical validation-gate
results (no NaN/Inf/duplicates) reproduced with zero redundant physics work.
Checkpoint/resume confirmed idempotent.

## 2. Representative points compared, baseline vs. optimized-v2

- EW_200GeV (1 EW point) — three-point pilot, row 1.
- colored_1500GeV (1 low-mass colored point) — three-point pilot, row 0.
- colored_2400GeV (1 high-mass colored point) — three-point pilot, row 1.

## 3. Required checks

| Check | Result |
|---|---|
| Identical final cut flags | PASS (`final_sec_iv_pass` identical, all 3 events) |
| Identical selected-plane membership | PASS (`sec3c_plane_found` identical, all 3) |
| Identical layer counts | PASS (`n_hits_postmerge` identical, all 3) |
| Identical hit-multiplicity verdict | PASS (`hit_multiplicity_pass` identical, all 3) |
| Δs/Δw tolerance | PASS — bit-identical, diff = 0.0 exactly, all 3 (not just within tolerance) |
| No NaN/Inf | PASS (validation gates, three-point pilot + this task's 47-event throughput sample) |
| No duplicate IDs | PASS (`(point,row_index)` uniqueness confirmed, three-point pilot) |
| Deterministic replay | PASS — this task's 47-event parallel run rerun twice, bit-identical both times |
| Successful checkpoint resume | PASS — three-point pilot rerun, all 10 events skipped correctly |

## 4. Extended validation this task (beyond the minimum required 3 events)

A larger, freshly-generated 47-event sample (22 EW_200GeV + 25
colored_2400GeV, real trigger-passing events from n=500/800-requested LHE
generation, not reused pilot events) was additionally run through both
serial and 3-worker-parallel downstream pipelines:

- **Correctness:** parallel output bit-identical to serial for the same
  per-event seed, all 47 events (`all_match_serial: true`).
- **Determinism:** two independent parallel runs bit-identical to each
  other, all 47 events (`all_match_rerun: true`).
- **Measured throughput:** serial 12.33 s/event, parallel (3 workers)
  5.10 s/event average (2.23-2.64x speedup across two parallel runs).

Full data: `metadata/THROUGHPUT_TEST_RESULT.json`.

## 5. Blocker resolution (runtime)

See `metadata/PREFLIGHT_REPORT.md` update block. Revised total projection:
**~24.9h (parallel, 3 workers) to ~42.1h (serial fallback)**, both under the
60h stop-gate. A genuine Pythia8/MadGraph environment version-mismatch bug
(`PYTHIA8DATA` pointing at the wrong Pythia8 install above ~100 events) was
found and fixed (scoped `unset PYTHIA8DATA` around the `generate_events`
subprocess call only) while producing the validation sample.

## Verdict

**Validation PASSED.** Phase 5 (production) may proceed using:
- the 3-worker parallel downstream pipeline,
- the `unset PYTHIA8DATA`-scoped generation fix,
- the corrected 91-point grid (EW mass list capped at 1000 GeV per the
  Phase 0 paper-axis correction).

No physics cuts, tolerances, or grid design were altered to pass validation.
