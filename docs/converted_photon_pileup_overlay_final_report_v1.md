# Converted-photon + pile-up overlay: final report (v1) — 2026-09-20

**STATUS: COMPLETE.** The paper-required converted-photon+pile-up background
(Sec IIID) has been produced for the first time this project. Full
9139-event run, μ=50, exit via `.DONE` marker.

## 1. References reread
paper.txt Sec II/IIIA/IIIB/IIIC/IIID/IV, Fig.5/Fig.6 captions — re-confirmed
against text already directly quoted multiple times this session (not
re-fetched from memory). Sec IIID's overlay sentence re-confirmed verbatim:
*"We subsequently overlay pile-up hits and pass the resulting set of hits
through our reconstruction algorithm."*

## 2. Paper-to-code overlay audit
`docs/converted_photon_overlay_paper_checklist_v1.md` — 14 items, each
labeled DIRECT PAPER REQUIREMENT / CITED-REFERENCE REQUIREMENT / DOCUMENTED
PROJECT ASSUMPTION / PROJECT SIMPLIFICATION / UNRESOLVED.

## 3. Bugs found and fixes
None new. Reused the already-fixed, validated `overlay_and_merge()` (single
raw+raw merge pass) from the prior EW-signal+pileup re-audit (commit
3213219) rather than re-deriving the merge logic, avoiding re-introducing
the previously-found double-merge/provenance-loss bug.

## 4. Test commands and exit codes
- `test_overlay_regression.py`: **19/19 PASS, exit 0.** μ=0 (n=50 prefix):
  9 fields bit-identical to v4. μ=50 (n=50): Poisson/merge-arithmetic/
  mixed-provenance/reproducibility all confirmed.

## 5. Benchmark and projected runtime
100-event μ=50 clean benchmark: 615.78s = 6.158s/event → projected 15.63h
for 9139 events (under the 24h gate). Actual full run: **53240.8s = 14.79h**
(1.853h faster than projected — reasonable variance, no anomaly).

## 6. Full execution history and PID
Historical PID **210143**, launched 2026-09-19 ~10:05, completed
2026-09-20 ~00:46. No process currently active (confirmed via `ps aux`).
Session restart mid-run did not affect the detached `nohup`+`disown`
process; only the monitoring wait-loop was re-armed once, the job itself
never paused.

## 7. Complete converted-photon+μ=50 cutflow
`converted_photon_with_pileup_v1/phase9_full_cutflow.csv`. Headline:

| Stage | N |
|---|---|
| 10000 generated | 10000 |
| 9139 extracted (MET+pT_γ cuts) | 9139 |
| Conversion attempted / valid point | 9139 / 9139 |
| Accepted hits (≥1) | 9139 |
| Raw candidate | 3276 |
| Selected plane | 3276 |
| ≥4/8 layers | 3128 |
| 8/8 layers | 1518 |
| Hit-multiplicity pass | 203 |
| Δs<0.01cm (given mult) | 1 |
| **Final Sec IV pass** | **1** |

Raw unweighted vs 1%-weighted kept strictly separate throughout (weighted
column = raw×0.01, never conflated with `weight_pb`, which already includes
the 1% factor on top of the per-event fiducial cross-section).

**Zero observations elsewhere in the cutflow are reported as "zero
observed, not zero probability" with Wilson/Clopper-Pearson intervals**
(none occurred at the final stage this time — see item 9).

## 8. μ=0 vs μ=50 transitions
`phase10_mu0_vs_mu50_transitions.csv`, using v4 as the μ=0 population
(justified: regression-proven bit-identical to what this overlay driver
itself produces at μ=0, since `rng_photon` is the same single sequential
stream in both). Key findings: **pile-up never destroys an existing
candidate (0 removed at every stage)**, only adds new ones (294 candidates
created, 199 events promoted to hit-multiplicity-pass, 1 event promoted to
final pass). The one final-pass event (2555) was already Δs-good at μ=0
(0.00582cm, well under the cut) but failed hit-multiplicity there; at
μ=50, pile-up hits coincidentally filled the missing per-layer multiplicity
on the *same* pre-existing plane without spoiling Δs enough to fail
(0.00910cm, still under 0.01cm) — a genuine, unforced coincidence, not a
tuned or cherry-picked result.

## 9. Statistical intervals
Final: 1/9139, point estimate 0.0001094, Wilson 95% [0.000166, 0.000473],
Clopper-Pearson 95% [0.0000028, 0.000610]. Since N_final=1 (not 0), the
"zero observed" wording does not apply to this stage; it does apply to
several intermediate zero-transition cells in the transition table (e.g.
0 candidates ever destroyed) and to the pile-up-only/hit-multiplicity
zero-counts documented in the earlier freeze.

## 10. Figure 5 status and paths
`converted_photon_with_pileup_v1/figure5_4component_paper_style.png` — the
correct four components (colored N=5, EW N=32, pile-up μ=50 N=172,
**converted-γ+pile-up μ=50 N=3276**, the real overlay result, not the
conversion-only diagnostic). Also
`figure5_conversiononly_vs_overlay_comparison.png` (explicit before/after).
Source histogram CSVs for every curve (`fig5_src_*_ds.csv`, `*_dw.csv`,
raw bin counts included). **Label used, as required:** *"Approximate
unit-area Figure 5 shape reproduction; absolute paper normalization
unavailable."* Pile-up reweighting NOT applied (denominator-population
ambiguity remains unresolved, unchanged from the earlier freeze). Status:
**diagnostic/approximate shape reproduction — not an exact paper figure**,
but for the first time built from the paper-correct four components.

## 11. Figure 6 definition, status and paths
`figure6_requirement_matrix.csv`. Re-read: 95% CL exclusion + discovery
curve over the (mQ,Λ) plane at L=300fb⁻¹, assuming negligible irreducible
backgrounds. **BLOCKED**: requires a production-cross-section × efficiency
scan over a continuous (mQ,Λ) grid; this project has only 2 discrete
benchmark points, no cross-section at all for the colored-quirk benchmark,
and no luminosity-yield calculation implemented. **No plot was produced** —
per instruction, missing cross-sections/efficiencies were not invented.
This project's own background results (pile-up 0/5000 every μ,
converted-γ+pileup 1/9139) are *consistent with* the paper's "negligible
irreducible backgrounds" assumption but were never required as a Fig.6
input by the paper itself, so this does not unblock Fig.6.

## 12. Cache schema and cache-only validation
The compact event-summary CSV (`conversion_with_pileup_mu50_v1.csv`, 26
columns, 9139 rows) is the permanent reusable artifact for this μ=50
result — all Phase 9–11 tables/figures above were computed from it alone,
with zero re-propagation, confirming cache-only reusability at the summary
level. A full raw-hit/candidate-level detailed cache (Parquet/HDF5/NPZ,
Phase 5's richer spec) was **not** built for the full 9139×μ=50 run in this
task (only the earlier n=100 conversion-only prototype exists at that
depth) — building one now would require re-instrumenting and re-running
the ~14.8h propagation a second time, which was not judged justified given
the compact summary already answers every question in Phases 9–11.

## 13. All authoritative paths and hashes
- `conversion_with_pileup_mu50_v1.csv` — sha256=`66f715e107797a9e0c88a9baaedadda7bf2fde51f7872aa3c3e81a4e4a065856`, 1330721 bytes, 9139 rows.
- `analyze_converted_photon_with_pileup_v1.py`, `test_overlay_regression.py` — commit 71e461f.
- `docs/converted_photon_overlay_paper_checklist_v1.md` — commit fc9e671.
- `05_coplanarity_analysis/converted_photon_with_pileup_v1/` — Phase 9–11 tables/figures (this task).

## 14. Runtime/RSS/disk
Wall time 53240.8s (14.79h), ~5.83s/event average. Peak RSS not
instrumented (consistent with all prior runs in this project — never
measured via `/usr/bin/time` for full runs, only for short benchmarks
earlier in the session). Output size 1.3MB; disk headroom unaffected
(947G free before launch).

## 15. Assumptions and limitations
- 20,000-event ancestry pool (paper: 125,000), with replacement.
- Pile-up reweighting denominator-population ambiguity unresolved.
- No absolute cross-section normalization for colored/pileup.
- Figure 6 fundamentally blocked on missing cross-section/efficiency scan.
- Single-run result (N_final=1) — a second independent μ=50 statistics
  batch was not run in this task; this is one realization of a
  small-number process, not a repeated-measurement average.

## 16. Commit hashes
`71e461f` (driver+tests), `fc9e671` (checklist), `3f3f7f7` (RUN_LOG launch
entry), plus this report's own commit and the Phase 9–14 results commit
(see final response for exact hashes).

## 17. Final git status
Clean except pre-existing untracked logs (see final response).

## 18. Confirmation whether any process remains active
**No** — confirmed via `ps aux`, PID 210143 no longer present.

## 19. Exact next recommended action
EW/colored + pile-up overlays remain NOT run (explicitly out of scope this
task). Converted-photon+pile-up is now the authoritative paper-equivalent
background dataset for any future Figure 5/6 refinement. No further action
is required unless you want EW/colored overlays, a repeated μ=50 statistics
batch, or a full detailed hit-level cache for this result — none started
without further authorization.
