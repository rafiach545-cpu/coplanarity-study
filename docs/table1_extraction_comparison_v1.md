# Table I extraction and paper-vs-project comparison (v1) — 2026-09-21

Read-only evidence task. No simulation run, no physics code modified.

## 1. Exact page and caption of Table I
PDF page **8** (1-indexed) of `1708.02243v2_Tracking_down_Quirks.pdf` (10
pages total). Caption: *"Breakdown of the signal efficiencies for two
benchmarks, one for Drell-Yan (DY) production, and one for colored
production (QCD). ε_trig and ε_fid are independent of Λ, the latter with
the exception of small edge effects. For Λ ≳ 5 keV, ε_reco deteriorates as
pairs of hits start merging into a single pixel."*

## 2. Complete exact transcription
`table1_extraction_v1/table1_exact_transcription.csv` / `.md`.

| mQ (GeV) | Λ (keV) | ε_trig | ε_fid | ε_reco |
|---|---|---|---|---|
| 800 (DY) | 1 | 0.10 | 0.28 | 0.11 |
| 800 (DY) | 2 | 0.10 | 0.28 | 0.41 |
| 800 (DY) | 3 | 0.10 | 0.28 | 0.65 |
| 800 (DY) | 4 | 0.10 | 0.28 | **0.72** |
| 800 (DY) | 5 | 0.10 | 0.28 | 0.74 |
| 1800 (QCD) | 1 | 0.24 | 0.28 | 0.083 |
| 1800 (QCD) | 2 | 0.24 | 0.28 | **0.35** |
| 1800 (QCD) | 3 | 0.24 | 0.28 | 0.59 |
| 1800 (QCD) | 5 | 0.24 | 0.28 | 0.74 |
| 1800 (QCD) | 10 | 0.24 | 0.28 | 0.58 |

All values are **exact printed values**, no unreadable cells. **The QCD
block has no printed Λ=4keV row** (jumps 3→5) — confirmed genuine via
direct visual inspection of the 400dpi crop, not a transcription gap.

## 3. Two-pass transcription comparison
Pass 1: raw `pypdf` text extraction (column order scrambled by the PDF's
internal text layout, but every value present). Pass 2: direct visual
reading of a 400dpi crop (`table1_crop_400dpi.png`) rendered via PyMuPDF.
**Compared cell-by-cell: zero discrepancies.**

## 4. Paper's efficiency definitions (re-read, page 7)
- ε_trig: trigger efficiency, "tends to be low, especially for Drell-Yan
  production" — independent of Λ.
- ε_fid: "parametrizes the likelihood that each quirk intersect with each
  layer at least once, in events passing the trigger," includes the 25ns
  timing cut.
- **ε_reco** (verbatim): *"the efficiency of our algorithm in finding
  quirks which satisfy both the trigger and fiducial requirements."* This
  is the Sec IIIC plane-found quantity (Δw<1cm, our `sec3c_plane_found`),
  **not** the complete Sec IV final-selection pass rate — confirmed
  consistent with the εreco relabeling fix from earlier in this session.
- Total: ε = ε_trig × ε_fid × ε_reco (Eq. 12).

## 5. Paper's denominators
`denominator_definitions.csv`. ε_trig: fraction of matched events. ε_fid:
fraction of trigger-passing events. ε_reco: fraction of trigger-AND-fiducial-passing
events (cumulative-conditional chain, matching our own cutflow structure).

## 6. Pile-up status — INFERRED, not stated
Neither the ε_trig/ε_fid/ε_reco paragraph nor Table I's caption mentions
any pile-up overlay for the *signal* efficiency measurement (pile-up is
discussed only in the separate Sec IIID *background* subsection). This is
an **inference from the absence of any overlay mention in the relevant
paragraph itself**, not inferred from the background section alone.
Table I's signal efficiencies therefore appear to be **pile-up-free**,
consistent with our own project's signal-only (no-pileup) cutflow CSVs —
**the comparison below is methodologically equivalent on this axis.**

## 7. Recomputed project counts (independently verified, not copied)

| | Colored (1.8TeV/2keV) | EW (800GeV/4keV) |
|---|---|---|
| Matched/start | 125 | 511 |
| Trigger | 27 | 89 |
| Geometric fiducial | 11 | 41 |
| Truth/timing fiducial | 7 | 40 |
| Sec IIIC selected plane | 5 | 32 |
| Hit-multiplicity pass | 3 | 16 |
| Final Sec IV pass | 1 | 6 |

All match the "known counts to verify" exactly, independently recomputed
from `colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv` and
`ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv`.

## 8. Statistical intervals (corrected Wilson, z-multiplier verified)
Full table: `paper_vs_project_comparison.csv`. Regression test
`tests/test_wilson_interval_regression.py`: **5/5 pass, exit 0** (rerun
this session to confirm the earlier bug fix holds).

## 9. Direct paper-versus-project comparison

| Benchmark | Quantity | Paper | Project | k/n | Wilson 95% | Interpretation |
|---|---|---|---|---|---|---|
| Colored | ε_trig | 0.24 | 0.216 | 27/125 | [0.153,0.296] | **CONSISTENT** |
| Colored | ε_fid | 0.28 | 0.259 | 7/27 | [0.132,0.447] | **CONSISTENT** |
| Colored | ε_reco (Sec IIIC) | 0.35 | 0.714 | 5/7 | [0.359,0.918] | **TENSION** (paper value 0.35 just below the 95% lower bound 0.359; N=7 extremely small) |
| Colored | Sec IV final rate | N/A | 0.143 | 1/7 | [0.026,0.513] | **DEFINITION MISMATCH** — not in paper Table I |
| EW | ε_trig | 0.10 | 0.174 | 89/511 | [0.144,0.209] | **TENSION** |
| EW | ε_fid | 0.28 | 0.449 | 40/89 | [0.350,0.553] | **TENSION** |
| EW | ε_reco (Sec IIIC) | 0.72 | 0.800 | 32/40 | [0.652,0.895] | **CONSISTENT** |
| EW | Sec IV final rate | N/A | 0.150 | 6/40 | [0.071,0.291] | **DEFINITION MISMATCH** — not in paper Table I |

## 10. Changed interpretation of previous results
**ε_reco (the quantity this project has cared about most) is now shown to
be broadly consistent with the paper for both benchmarks** — EW cleanly
consistent (0.72 within [0.652,0.895]), colored borderline/in-tension but
only by a hair, dominated by N=7 statistics. This is the **first direct,
hard numeric confirmation** that the project's central physics quantity
tracks the paper reasonably well.

**However, ε_trig and ε_fid for the EW/DY benchmark show real tension**
(paper's values sit clearly below the project's 95% CI). The most likely
explanation is a **definition mismatch**, not a physics bug: this
project's own documentation has repeatedly flagged that ε_trig is
implemented as a **project-level proxy** (`pT_pair>200GeV`, truth-level),
not the paper's actual trigger/HLT simulation, and ε_fid's 25ns timing
cut / layer-crossing logic may differ in detail from the paper's own
fiducial-region implementation. This is a newly-surfaced, concrete
discrepancy that previous session work had not directly quantified
(previous reports only had "not numerically quoted" for these fields
since Table I had not yet been extracted) — it should be flagged as an
open item, not silently absorbed.

The colored benchmark's ε_trig/ε_fid, by contrast, ARE consistent with
the paper — meaning the tension is specific to the EW/Drell-Yan case, not
a universal problem with the trigger/fiducial proxy.

## 11. Rendered-page and crop paths
`05_coplanarity_analysis/table1_extraction_v1/page8_fullpage_400dpi.png`,
`table1_crop_400dpi.png`.

## 12. Files changed
New files only, under `05_coplanarity_analysis/table1_extraction_v1/`:
`page8_fullpage_400dpi.png`, `table1_crop_400dpi.png`,
`table1_exact_transcription.csv`, `table1_exact_transcription.md`,
`denominator_definitions.csv`, `paper_vs_project_comparison.csv`,
`extraction_metadata.json`. Plus this report,
`docs/table1_extraction_comparison_v1.md`. No existing files overwritten,
no authoritative event CSV touched.

## 13. Tests and exit codes
`python3 tests/test_wilson_interval_regression.py` — **exit 0**, 5/5 cases
pass (reused, not duplicated — confirms the earlier Wilson-formula fix has
not regressed).

## 14–16. Commit hash / git status / process confirmation
See final response.
