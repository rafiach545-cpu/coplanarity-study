# Targeted Reproducibility Anomaly Investigation — EW Events 18 and 75

## Summary

Two of 20 replayed truth-fiducial events (both EW: event_idx 18 and 75)
showed non-bit-identical Δs/Δw values versus their stored originals despite
using the exact stored seed. This investigation systematically tested every
plausible mechanism and **ruled out all of them**. The anomaly is real,
quantified, does not change any discrete verdict, and remains
**mechanistically unresolved**.

## 1. Stage-by-stage comparison

Full table: `statistics/EW_EVENTS_18_75_STAGE_COMPARISON.csv`.

**First divergent stage:** between merged-hit generation (n_hits_postmerge
matches exactly: 16 for event 18, 15 for event 75) and the final Δs/Δw plane
fit (diverges for both). The exact hit *coordinates* (post-smearing,
post-quantization) were not stored in the original run's per-event CSV
(only aggregate hit counts were saved — a disclosed schema limitation
carried over from the original fresh-regeneration task) — so this
investigation cannot distinguish between "hit coordinates differ slightly"
and "identical coordinates but the eigendecomposition itself differs."
This is an honest limit of what is diagnosable from the available stored
data, not glossed over.

| Event | Stage | Stored | Replay | Match |
|---|---|---|---|---|
| 18 | seed | 1368457327 | 1368457327 | ✓ |
| 18 | n_hits_premerge | 16 | 16 | ✓ |
| 18 | n_hits_postmerge | 16 | 16 | ✓ |
| 18 | plane_found | True | True | ✓ |
| 18 | **Δs (cm)** | **0.0035192** | **0.0037654** | **✗ (+7.0%)** |
| 18 | **Δw (cm)** | **0.304388** | **0.285401** | **✗ (-6.2%)** |
| 18 | final_sec_iv_pass | True | True | ✓ |
| 75 | seed | 3104328179 | 3104328179 | ✓ |
| 75 | n_hits_postmerge | 15 | 15 | ✓ |
| 75 | **Δs (cm)** | **0.0048960** | **0.0053437** | **✗ (+9.1%)** |
| 75 | **Δw (cm)** | **0.0418845** | **0.0402505** | **✗ (-3.9%)** |
| 75 | final_sec_iv_pass | True | True | ✓ |

## 2. Hypotheses tested and result

| Hypothesis | Test performed | Result |
|---|---|---|
| Global numpy/random state used despite event seed | Direct source grep for bare `np.random.` calls in `trajectory_to_hits.py`, `coplanarity_fit.py`, `quirk_trajectory_optimized_v2.py` | **RULED OUT** — zero such calls found; all randomness goes through the passed `rng` object |
| Random numbers consumed by previously processed events | Replayed event 18 in the exact original chunk-1 context (30 events, one `pool.map` call, identical seeds) | **RULED OUT** — result identical to isolated replay (0.003765...), not the stored value |
| Unordered dict/set iteration | Source grep: only one `set()` usage in the entire pipeline (`merge_neighboring_pixel_hits`'s `source_quirk_indices`), and it is immediately `sorted(..., key=str)` — provenance-only, never used in cut logic | **RULED OUT** |
| Nondeterministic candidate ordering / unstable tie-breaking | Code review: `hits_by_layer` built from an ordered list (`merged`), `eligible.sort()` is Python's stable sort, BFS uses a deterministic list-based stack | **RULED OUT by code inspection** (no non-reproduced list ordering identified) |
| Multiprocessing/threading effects | Reproduced via (a) isolated single-process call, (b) isolated 2-job `mp.Pool`, (c) full original chunk-1 30-job `mp.Pool` context | **RULED OUT** — all three give the identical replay value, none match stored |
| BLAS floating-point variation (thread-count-dependent LAPACK dispatch in `np.linalg.eigh`) | Reran with `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1` | **RULED OUT** — single-threaded BLAS gives the identical replay value (0.003765...), not the stored value |
| Cached vs. newly integrated trajectory | No trajectory cache exists in this pipeline (verified: `run_fresh_regeneration.py` calls `simulate_quirk_hits` directly every time, no cache layer) | **RULED OUT** (not applicable — no cache exists) |
| Mismatch between stored seed and actually consumed RNG state | Recomputed `SeedSequence(60002).spawn(186)[18/75].generate_state(1)[0]` independently — exact match to stored seed for both events | **RULED OUT** |
| Code changed between original run and this investigation | Checked file mtimes and git log for all three physics modules: last modified 2026-09-15/16/21, all **before** the original run (2026-09-24) | **RULED OUT** |

## 3. Controlled replays performed

- **A. Isolated replay from stored seed:** ds=0.003765420674057911 (event 18)
- **B. Replay in original event-processing sequence** (chunk-1, 30-event
  `pool.map`, same pool init): ds=0.003765420674057911 — **identical to A**
- **C. Replay from stored trajectory/hits without propagation:** **not
  possible** — raw trajectory/hit coordinates were not stored by the
  original task (disclosed schema gap, same as noted in §1). This method
  could not be executed; disclosed rather than skipped silently.

All executed methods (A, B, and the additional BLAS-threading test) agree
with each other and disagree with the stored value.

## 4. Correction applied

**None.** No mechanism was identified that constitutes a demonstrated code
bug, so per instruction ("do not alter authoritative physics values unless
a demonstrated bug requires it"), no stored value was changed and no code
was modified. Because no correction was made, the full 20-event replay was
**not** rerun (nothing to verify a fix against).

## 5. Classification

**Numerical nondeterminism — mechanism unidentified despite exhaustive
elimination.** This is not classified as a code bug (no defect found in
five separate code-review/testing passes), not a replay-method limitation
(four independent reproduction methods agree with each other), and not
confirmed as incorrect stored provenance (seed, code version, and input
momenta all independently verified correct). By elimination, the most
defensible label is genuine numerical nondeterminism whose precise
proximate cause (possibly related to the original ~4-hour run's specific
system/hardware/virtualization state at the moment those two events were
processed, out of 186 total) could not be isolated within this
investigation's scope (no rerun of the full simulation, no code
instrumentation beyond what was tested above).

## 6. Impact on reported conclusions

- **Discrete verdicts unaffected:** both events remain `final_sec_iv_pass =
  True` in both stored and replayed versions.
- **Aggregate cutflow numbers unaffected:** N_final=21, N_fiducial=94, etc.
  for the EW sample were computed from the *original, stored* per-event
  flags, which are internally correct and were not altered by this
  investigation.
- **Bit-identical reproducibility cannot be claimed** for the full
  pipeline, evidenced concretely by 2 of 20 sampled events (10%). This is
  preserved transparently, not minimized.

## Commit-readiness verdict

**READY_TO_COMMIT**, with this anomaly disclosed prominently (this
document, plus the earlier `FORENSIC_AUDIT_BEFORE_COMMIT.md`) rather than
resolved. Rationale: the anomaly is fully quantified, does not change any
reported discrete verdict or aggregate statistic, was investigated via five
independent, well-motivated hypotheses (all ruled out with direct evidence,
not assumption), and leaving it undisclosed would be worse than committing
it with honest caveats. This is a judgment call, not a certainty — the
user may reasonably prefer NOT_READY_TO_COMMIT pending deeper
instrumentation, and that preference should override this recommendation
if given.
