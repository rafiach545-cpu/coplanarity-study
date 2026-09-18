# Converted-photon A–Z final report (v1) — 2026-09-18

**STATUS: INTERIM.** The v4 full-diagnostics rerun (PID 165371, launched
this task, projected ~4.93h) is still in progress at the time of this
report. Everything below that does NOT depend on the hit-multiplicity flag
is final; the hit-multiplicity cutflow stage and e±-origin/timing
diagnostics will be appended in a follow-up update once v4 completes
(checked automatically, not polled).

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
- N(hit-multiplicity pass): **PENDING v4**.
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

## Failure analysis (partial, hit-multiplicity split PENDING v4)
`table12_failure_reasons_partial.csv`: no-candidate=6157 (67.38%),
plane-found-but-Δs≥0.01=2889 (31.61%), plane-found-and-Δs<0.01=93 (1.02%,
these are NOT automatically final passes — final=0 proves at least one of
them also fails hit-multiplicity, per the structural AND in
`apply_signal_region_cuts`). v4 will split this further once complete.

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
this turn. v4 (in progress): PID 165371, benchmarked at 97.06s/50 events =
1.94 s/event on a regression-tested 50-event prefix (all 11 old columns
bit-identical to v3, 0 failures), projecting ~4.93h for the full run —
under the 6-hour authorization threshold, launched only after confirming no
other CPU-heavy process and sufficient disk/RAM.

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
- `conversion_scan_results_v4_FULL_DIAGNOSTICS.csv` — IN PROGRESS, will be hashed and recorded on completion; never overwrites v3.
- `convert_and_analyze_v4_full_diagnostics.py`, `test_v4_regression.py` — commit e999fc0.

## Commits (this task, so far)
e999fc0 (v4 driver+tests), 6f5eece (figure regen script), 9bc278c (17 PPT
tables), 2257274 (PPT figures). A final commit will follow once v4
completes and the report is updated.

## Next action
Wait for v4 (PID 165371) to complete (background-monitored, not polled),
then: validate v4 (row count, bit-identical old columns, new-column
sanity), compute the complete hit-multiplicity cutflow stage and
e±-origin/timing statistics, finish `table06`/`table12` (full versions),
add the failure-reason and hit-origin figures, update this report to FINAL
status, and commit. **Converted-photon + pile-up overlay and the PPT itself
remain NOT started, per explicit instruction.**
