# PPT Statistics Sourcebook (v1) — 2026-09-18

Read-only compilation for presentation preparation. No new simulation was
run; no physics code, cuts, or authoritative CSVs were modified. All numbers
independently recomputed by `05_coplanarity_analysis/build_ppt_statistics.py`
from already-authoritative, already-frozen files (EW/colored cutflow CSVs,
the pile-up-only freeze package, the converted-photon-only freeze package).

## 1. Definitions (denominators explicit)

| Term | Definition | Denominator |
|---|---|---|
| Matched event | MLM-matched MadGraph/Pythia8 event (EW: 511; colored: 125, charge-filtered) | generation |
| Trigger-passing event | truth pT(pair)>200GeV | N_matched |
| Geometric fiducial | both quirks cross all 8 layers, \|eta\|<1.8 | N_trigger |
| Timing fiducial (truth_fiducial) | geometric fiducial AND last crossing <25ns | N_trigger |
| Reconstructed candidate | >=1 `seeding_and_iterative_fit` output | N_truth_fiducial (signal) / N_total (background) |
| Selected Sec IIIC plane | `select_reconstructed_plane`: Δw<1cm, smallest Δs | candidates population |
| >=4/8, 8/8 raw-candidate coverage | best RAW candidate's layer count (independent axis from selected plane) | N_total |
| Hit-multiplicity pass | `check_hit_multiplicity` on the SELECTED plane | N_selected_plane |
| Δw pass | structurally guaranteed by plane selection | N_selected_plane |
| Δs pass | selected plane's Δs<0.01cm | N_hit_mult_pass (Sec IV order) |
| Final Sec IV pass | plane found AND hit-mult AND Δs<0.01cm | N_total |
| Conversion-only background | converted e+e- through detector+reconstruction, NO pile-up overlay | 9139 |
| Pile-up-only background | Poisson(mu) minbias overlay, no hard-scatter object | 5000/mu |
| Converted-photon+pile-up | paper's actual prescription (NOT YET IMPLEMENTED) | N/A |

## 2. Authoritative file inventory
`ppt_statistics_v1/authoritative_file_inventory.csv` — 16 files, all status
OK with SHA-256 hashes recorded. No obsolete CSVs used (v1 conversion result
and v2 pile-up sweep coverage-only files explicitly excluded from this
sourcebook's inputs).

## 3–4. EW / Colored complete statistics
`ppt_statistics_v1/ew_complete_statistics.json`,
`colored_complete_statistics.json`. Independently re-verified this turn:

- **EW**: N_matched=511, **N_trigger=89** (explicitly NOT the generated
  sample size), N_geom_fid=41, N_truth_fid=40, N_seed=32, N_plane=32,
  N_mult=16, N_final=6. Final-passing events: **[260, 313, 322, 332, 362,
  438]**. Near-miss events 339 (Δs=0.010211, fails hit-mult) and 386
  (Δs=0.011989, fails hit-mult) — directly confirmed from the CSV.
- **Colored**: N_matched=125, **N_trigger=27** (explicitly NOT total
  generated), N_geom_fid=11, **N_truth_fiducial=7**, N_seed=5, N_plane=5,
  N_mult=3, N_final=1. Full cutflow **125→27→11→7→5→1** confirmed exactly.
  Events 38 and 169: truth_fiducial=True, n_candidates=0 — confirmed zero-seed
  events. Events 208 (Δs=0.010464) and 369 (Δs=0.011863): both just above the
  0.01cm cut, hit-mult PASSES — confirmed genuine Δs near-misses. Event 386:
  Δs=0.009367, hit-mult=True, **the sole final pass** — confirmed.

## 5. Converted-photon-only complete statistics
Reused from the frozen package (`converted_photon_only_statistics_v1/`,
commit 96f0fe0 verified). N_total=9139, N_plane=2982, N(Δs<0.01)=93, N_final=0
— all previously independently verified, re-confirmed present and unchanged
this turn (git status clean, hashes unchanged). **Label: "Converted-photon-only
— no pile-up overlay — not yet the paper-equivalent converted-photon
background."**

## 6. Pile-up-only complete statistics, all mu
Reused from the frozen package (`pileup_only_statistics_v1/`). The
prompt-supplied table (mu: N_raw_candidate/N_plane/N_mult/N_ds/N_final) was
**independently re-verified against the frozen `table9_master_cross_mu.csv`
this turn: CONFIRMED, all 5 mu match exactly** — not blindly copied. mu=50:
Δs median=0.03143, Δw median=0.76399, N(Δs<0.01)=7/172 (frac=0.0407),
multiplicity 0/172 (Wilson 95% UL≈0.0218), final 0/5000 (Wilson 95% UL≈0.000768).
**"Zero observed, not zero probability."**

## 7. Master cutflow table
`ppt_statistics_v1/master_cutflow_table.csv`. EW/Colored/Converted-γ-only/PU
mu=0,5,10,20,50 as columns, N/A used (never 0) where a stage does not apply
(e.g. trigger/geometric-fiducial/timing-fiducial are N/A for background
samples, which have no such truth-level stages).

## 8. Master Δs/Δw table
`ppt_statistics_v1/master_delta_s_delta_w_table.csv`. Explicitly flags
`pile_up_overlay_present` per row: **False** for colored, EW, and
converted-photon-only; **True** for all pile-up-mu rows. Units: cm throughout.

## 9. Paper vs project table
`ppt_statistics_v1/paper_vs_project_table.csv`. Per instruction, final Sec IV
0/5000 is **not** compared to the paper's partial-plane rates (kept as
separate rows A/B vs E), and conversion-only 0/9139 is explicitly marked
**NOT COMPARABLE** to the paper's converted-gamma+pileup result.

## 10. Runtime master table
`ppt_statistics_v1/ppt_table10_runtimes.csv`. Photon v3 fully measured
(17057s, PID 95330, exit 0). Pile-up fullcutflow reruns measured per mu
(mu=5:610.24s, mu=10:1377.28s, mu=20:3279.97s, mu=50:16193.40s). Signal
(EW/colored) analysis runtime: **NOT RECORDED** (no per-event timing
instrumentation exists in those scripts) — not fabricated.

## 11. Notable event table
`ppt_statistics_v1/notable_events_table.csv`. Covers EW final passes/near
misses, colored event 386/208/369/38/169, the sole pile-up 8/8 event
(mu=5, event_i=2006, per-layer breakdown `{8:2,7:2,6:1,...}`, fails
hit-multiplicity: "only 2/8 layers have ≥2 hits"), and the converted-photon
minimum-Δs event plus the Δs<0.01 subpopulation.

## 12. Figure/table inventory for PPT
`ppt_statistics_v1/figure_table_inventory_for_ppt.csv` — 12 entries spanning
Fig.5 diagnostic reproduction, pile-up diagnostics, and converted-photon-only
diagnostics, each classified DIAGNOSTIC/PROJECT DIAGNOSTIC/PARTIAL
paper-comparable, with limitations and a recommended slide. **No
converted-photon curve is classified as paper-equivalent.**

## 13. PPT-ready summary tables
All 12 requested `ppt_table01`–`ppt_table12` CSVs generated under
`05_coplanarity_analysis/ppt_statistics_v1/`, each sized for one slide;
detailed appendix versions retained as the full JSON/CSV sidecars in the
same directory and in the two upstream freeze packages.

## 14. Required status classification
See `ppt_table12_status.csv` — reproduced exactly as specified:
EW signal without pile-up: COMPLETED, with reconstruction-efficiency
discrepancy. Colored signal without pile-up: COMPLETED, small-statistics
limitation. Pile-up-only background: COMPLETED AND FROZEN, with documented
limitations. Converted-photon-only: COMPLETED BASELINE, no pile-up overlay.
Converted-photon + pile-up: NOT YET IMPLEMENTED/RUN. EW signal + pile-up:
NOT A FULL AUTHORITATIVE RESULT. Colored signal + pile-up: NOT RUN. Exact
paper Figure 5: NOT YET COMPLETE. Diagnostic Figure 5 shape comparison:
AVAILABLE WITH LABELLED LIMITATIONS.

## 15. Verification performed
Every number above was recomputed directly from source CSVs by
`build_ppt_statistics.py` (not copied from memory or prior text). The
pile-up cross-mu table supplied in the task prompt was independently
cross-checked against the frozen freeze package and found to match exactly.
`git status` confirmed no drift in any upstream frozen file before reading it.

## Remaining gaps (not estimated)
- EW/colored analysis runtime and peak RSS: NOT RECORDED.
- Converted-photon hit-multiplicity flag: NOT RECORDED, requires rerun.
- Colored/pile-up absolute production cross-section: unavailable.
- Table I's exact printed numeric values: not independently re-extracted
  this turn (PDF text extraction renders Table I as non-selectable content).
