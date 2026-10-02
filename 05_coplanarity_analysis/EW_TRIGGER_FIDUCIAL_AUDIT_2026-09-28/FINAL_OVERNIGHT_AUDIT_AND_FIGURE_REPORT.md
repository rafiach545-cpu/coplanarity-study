# Final Overnight Audit and Figure Report — 2026-09-28

## Work completed

**Phase 1 — Zero-hit replay completion**: 30/31 (97%) targeted EW-2000
"moderate truth-η, zero-hit" events fully classified: **eta-drift barrel
loss** — physical, verified via instrumented replay (150s original
budget: 17/31; 600s extended follow-up on the 14 timeouts: 13/14 more).
1 event (idx 165) remains genuinely unresolved (timed out at both
budgets). See `ZERO_HIT_REPLAY/PHASE1_FINAL_CLASSIFICATION.md`.

**Phase 2 — Paper/detector reread**: Sec. III A/B/C, Sec. IV, Table I,
Fig. 2-5 captions reread directly. Confirmed exact source of the
"|η|≲1.8" statement (Sec III A). Confirmed the project applies only a
constant-η cut, no finite-z boundary (code-verified, zero matches for
z-boundary variables). Identified and quantitatively demonstrated (not
proven against paper's own unavailable code) that a constant-η cone and
a literal finite-length barrel cylinder are **geometrically
non-equivalent**, with the barrel model being looser at inner layers —
a disclosed, labeled INFERENCE, not asserted as fact. See
`PHASE2_PAPER_DETECTOR_REREAD.md`.

**Phase 3 — Final EW verdict**: all 7 required explanation items
answered with exact statistics (binomial errors, Wilson 68%/95%, exact
p-values). Overall verdict: **UNRESOLVED**, with specific, demonstrated
sub-findings (ISR/pT effect real but insufficient; rapidity/η-centrality
dominant internal driver; 30/31 zero-hit losses physical; no double-
counting; residual gap attributable only to undocumented paper settings).
See `PHASE3_FINAL_VERDICT.md`.

**Phase 4 — Consolidated master table**: both benchmarks, both sample
sizes (1000/2000), all quantities including the CORRECTED intersection
values (Colored 12/25, EW 75/94 — never the stale 20/25 or 84/94), full
uncertainty suite. See `PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv`.

**Phase 5 — Figures**: 6 figures (A-F) generated in
`05_coplanarity_analysis/FINAL_FIGURES_2026-09-28/` (new, isolated
directory; no previous figure overwritten), each as PNG+PDF+SVG+source
CSV: Fig.2 reproduction (A), Fig.3 reproduction (B, correctly using the
paper's own Λ=2keV EW diagnostic benchmark, not confused with the Λ=4keV
Table I benchmark), Fig.4 reproduction (C, Colored from existing
verified data + EW from one new representative-event replay, event_idx
182, reproducing stored Δs/Δw to >10 significant figures), Δs/Δw
distributions on the corrected 12/75 intersection (D), efficiency
comparison with Wilson 95% error bars (E), and cutflow figures (F).

**Phase 6 — PPT slides**: `PPT_READY_COLORED_TWO_SLIDES.md` (cutflow
counts only on slide 1; efficiencies+uncertainty+verdict on slide 2, no
repeated numbers).

**Phase 7 — Validation**: figure source CSVs directly recomputed from
authoritative event tables; Colored/EW counts in Figure D's source CSV
verified as exactly 12/75; grep-checked for stale 20/25, 84/94, 4/25
values across all new outputs — only found inside explanatory
"CORRECTED, not stale X" labels, never as live data; all PNG/PDF/SVG
files have healthy non-zero file sizes; no process running; both
directories' SHA-256 manifests regenerated.

## Unresolved items (honestly disclosed, not hidden)

- Event_idx 165 (EW-2000 zero-hit population): mechanism genuinely
  unresolved, timed out at both 150s and 600s replay budgets.
- The finite-z-vs-constant-η-cone modeling question (Phase 2): flagged
  as a real, quantitatively-motivated candidate contributor to the
  fiducial-efficiency gap, but **not confirmed** against the paper's own
  code or ref [27]'s exact dimensions (which were not accessible in this
  audit).
- The ultimate root cause of the ε_trig/ε_fid gaps: still attributed
  only to undocumented paper generator/PDF/matching/shower settings —
  not closed by this session's work, and not claimed to be.
- A PDF/xqcut/qcut/Pythia sensitivity scan remains a recommended, but
  not yet executed, next step — and per instruction, any such future
  scan must be labeled a sensitivity study, not a paper-reproduction
  attempt.

## Exact files created (this overnight session)

**`EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/`**:
- `ZERO_HIT_REPLAY/PHASE1_FINAL_CLASSIFICATION.md`
- `ZERO_HIT_REPLAY/tables/FINAL_31_EVENT_CLASSIFICATION.csv`
- `ZERO_HIT_REPLAY/tables/instrumented_replay_summary_EXTENDED_600s.csv`
- `ZERO_HIT_REPLAY/tables/layer_crossing_detail_EXTENDED_600s.csv`
- `ZERO_HIT_REPLAY/scripts/instrumented_replay_extended.py`
- `PHASE2_PAPER_DETECTOR_REREAD.md`
- `PHASE3_FINAL_VERDICT.md`
- `PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv`
- `PHASE4_MASTER_TABLE/figure5_corrected_source_data.csv`
- `PPT_READY_COLORED_TWO_SLIDES.md`
- `FINAL_OVERNIGHT_AUDIT_AND_FIGURE_REPORT.md` (this file)
- `SHA256_MANIFEST.txt` (regenerated, covers all of the above plus all
  earlier-session files in this directory)

**`FINAL_FIGURES_2026-09-28/`** (new, isolated):
- `PNG/`, `PDF/`, `SVG/` — 6 figures each (A-F)
- `SOURCE_DATA/` — one CSV per figure
- `METADATA/FIGURE_captions_and_metadata.md`
- `scripts/make_figures_DEF.py`, `scripts/make_figures_ABC.py`,
  `scripts/replay_ew_event182.py`
- `SHA256_MANIFEST.txt`

## Simulations run: NONE
No MadGraph, Pythia8, LHE, or HepMC generation was performed. Two
existing-event trajectory **replays** were performed (deterministic,
from stored seeds/momenta, using already-validated physics code
unmodified) — the 600s extended zero-hit replay (14 events) and one
Figure-4 EW representative-event replay (event_idx 182) — neither is new
particle-physics event generation.

## Frozen files modified: NONE
No file under `quirk_2000_event_fresh_regeneration_v1/`, any
`FINAL_FIGURES_FOR_PPT/` file, `madgraph_pilot_v1/`, or any repo-root
1000-event cutflow CSV was modified. Existing figures in
`FINAL_FIGURES_FOR_PPT/` and elsewhere were read (to reuse their
verified source data) but never written to.

## Commit/push status: NONE
Nothing was committed or pushed this session.
