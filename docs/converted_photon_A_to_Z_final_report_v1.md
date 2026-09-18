# Converted-photon A–Z final report (v1) — 2026-09-18

**STATUS: FINAL.** The v4 full-diagnostics rerun (PID 165371) completed
successfully: 9139/9139 events, wall time 16934.9s (4.704h), exit via
`.DONE` marker. Validated bit-identical to v3 on all 12 pre-existing
columns (0 unequal cells across 9139 rows). The hit-multiplicity cutflow
stage and e±-origin/timing diagnostics below are now complete, not pending.

## NEW RESULT: exact hit-multiplicity cutflow (previously only bounded, now direct)
**N(hit-multiplicity pass, given selected plane) = 4/2982** (previously only
known to be ≤1479 via the necessary-condition bound). Point estimate
w_mult = 0.001341, Wilson 95% CI [0.001237, 0.002728], Clopper-Pearson 95%
[0.000366, 0.003431]. All 4 passing events share the **identical** per-layer
hit pattern `{8:2,7:2,6:2,5:2,4:2,3:2,2:2,1:1}` (events 3578, 5240, 5805,
7723), all positron-dominated (7 positron-origin hits, 0 electron-origin, 1
mixed), Δw≈0.50cm, **Δs∈[0.01907, 0.02646]cm — all above the 0.01cm cut**,
confirming N_final=0 is now traced to its exact cause: every event that
clears hit-multiplicity fails Δs<0.01cm.

Full failure-reason breakdown (9139 total): no candidate=6157 (67.4%),
plane found but hit-multiplicity fails=2978 (32.6%), hit-multiplicity
passes but Δs≥0.01 fails=4 (0.04%), final pass=0. See
`table12_failure_reasons_FINAL.csv`, `fig14_failure_reason_chart.png`.

## Paper methodology (Sec IIID, re-verified this turn)
Z+gamma+j (MadGraph5_aMC@NLO), Z→νν, MET>200GeV, photon pT>0.5GeV, ~1pb
fiducial σ → ~10fb after beampipe conversion probability (PDG figs
33.16/33.17), equal e+/e− energy sharing, same detector sim as pile-up,
**then overlay pile-up hits before reconstruction**.

## Implementation status
Full paper-to-code table: `converted_photon_ppt_statistics_v1/table02_paper_vs_implementation.csv`.
Every requirement MATCHES except: (a) conversion probability is an
ASSUMPTION not independently re-derived from PDG figures this session (it
matches the paper's implied ~1% order of magnitude); (b) **pile-up overlay
is NOT IMPLEMENTED** — confirmed absent by direct source inspection (zero
"pileup"/"overlay" occurrences in `convert_and_analyze.py`).

**"The existing 9139-event sample is converted-photon-only. The paper
overlays pile-up hits on the converted e+e− hits; that paper-required
combined result has not yet been produced."**

## Complete event chain
Documented stage-by-stage in `table03_generation_extraction_cutflow.csv`
(generation→extraction, 10000→9139, all counts direct except the raw
10000 generated count, which is a hardcoded constant — the underlying
run_card/proc_card files are not present in the repo) and
`table04_conversion_model.csv` (conversion mechanics: every photon
converted, 1% applied as an end-weight not a stochastic filter, exact
2.35cm conversion radius verified constant, exact 50/50 energy split).

## All cuts and counts
- N_total=9139, N_ok=9139 (0 failed conversions).
- N(any detector hit)=7811 (85.47%).
- N(raw candidate)=2982 (38.18% of hit-having events).
- N(selected Sec IIIC plane)=2982 (coincides with raw-candidate count in
  this dataset, confirmed a dataset-specific observation, not a general
  algorithm guarantee).
- N(≥4/8 layers)=2957/2982 (99.16%); N(8/8 layers)=1479/2982 (49.60%).
- N(hit-multiplicity pass, given selected plane)=**4/2982** (w_mult=0.001341,
  Wilson 95% CI [0.001237, 0.002728]) — see NEW RESULT section above.
- N(Δs<0.01 among plane-found, unweighted by multiplicity)=93 (3.12%).
- N(final Sec IV pass)=0/9139 (this final number is unaffected by v4 — it
  was already computed correctly in v3, since `apply_signal_region_cuts`
  internally calls `check_hit_multiplicity`; v4 only recovers the
  *standalone* diagnostic flag, not a new final-pass value).

## Δs/Δw statistics (independently re-verified, unchanged from prior freeze)
Δs (N=2982): median=0.02116, p16=0.01489, p84=0.02723, min=0.00089,
max=0.04816, N(<0.01cm)=93 (3.12%). Δw: median=0.17767, p16=0.06663,
p84=0.38705, min=0.01512, max=0.76062. Full percentile/threshold detail:
`table10_delta_s_statistics.csv`, `table11_delta_w_statistics.csv`.

## Failure analysis (FINAL, complete via v4)
`table12_failure_reasons_FINAL.csv`: no-candidate=6157 (67.38%),
plane-found-but-hit-multiplicity-fails=2978 (32.58%),
hit-multiplicity-passes-but-Δs≥0.01-fails=4 (0.04%), final pass=0. The
4 near-miss events (3578, 5240, 5805, 7723) all share the identical
per-layer pattern `{8:2,7:2,6:2,5:2,4:2,3:2,2:2,1:1}`, all positron-
dominated hits, Δs∈[0.01907,0.02646]cm — genuinely above the 0.01cm cut,
not a rounding-level near-miss.

## Notable events
`table13_notable_events.csv`: minimum/maximum Δs and Δw events, and the
93-event Δs<0.01 subpopulation's range.

## Weights / cross-section
Per-event weight = 2.310512e-07 pb (constant, = fiducial-σ-after-MET ×
0.01 conversion probability), never used as a selection cut. Kept strictly
separate from the unweighted reconstruction-rate statistics throughout.

## Statistical intervals
Final 0/9139: Wilson 95% CI [0, 0.000420], Clopper-Pearson 95% consistent.
**"Zero observed, not zero probability."** This is explicitly not the
paper's final converted-photon-background limit (pile-up overlay absent).

## Runtimes
`table14_runtime.csv`. v3 (authoritative, complete): PID 95330, 17057s
(4.738h), 1.8672 s/event, 1928.85 events/hour, exit 0 — all re-verified
this turn. v4 (COMPLETE): PID 165371, actual wall time **16934.9s (4.704h)**,
1.853 s/event, exit via `.DONE` marker — close to the 1.94 s/event
50-event benchmark projection (~4.93h), slightly faster in the full run.
All 12 pre-existing columns confirmed bit-identical to v3 (0 unequal cells
across 9139 rows) — no physics perturbed by the additive diagnostics.

## Paper comparison
`table15_paper_comparison.csv` (reused from the frozen package, still
valid: process/MET/pT_gamma/detector model MATCH; pile-up overlay NOT
IMPLEMENTED; final rate NOT COMPARABLE to any paper-quoted number).

## Limitations
`table16_limitations.csv`.

## Exact overlay status
NOT IMPLEMENTED. Not started in this task, per explicit instruction.

## Authoritative files and hashes
- `conversion_scan_results_v3_SEC3C_DS_DW.csv` — authoritative baseline, unchanged, commit 96f0fe0.
- `conversion_scan_results_v4_FULL_DIAGNOSTICS.csv` — COMPLETE, sha256=`fab40924cf24c16466b77d8085227c9ae676fe2515e503611575bcd86edc3ad2`, 9139 rows, never overwrites v3.
- `convert_and_analyze_v4_full_diagnostics.py`, `test_v4_regression.py` — commit e999fc0.
- `cache_prototype_v1/` (n=100 event/hit/candidate cache prototype, NOT full statistics) — commits 04ce39d, 4411c6d.

## Commits (this task)
e999fc0 (v4 driver+tests), 6f5eece (figure regen script), 9bc278c (17 PPT
tables, interim), 2257274 (PPT figures, interim), 04ce39d/4411c6d (cache
prototype), cbd37da (RUN_LOG), plus the final v4-results commit and this
report's finalization commit (see final response for exact hashes).

## Next action
**Complete.** Converted-photon-only analysis is now final at full statistics
with documented limitations. **Converted-photon + pile-up overlay and the
PPT itself remain NOT started, per explicit instruction — awaiting separate
authorization.**

**"The converted-photon-only analysis is complete at full statistics with
documented limitations. It is a validated mu=0/no-pile-up baseline and is
not the paper-required converted-photon plus pile-up background."**
