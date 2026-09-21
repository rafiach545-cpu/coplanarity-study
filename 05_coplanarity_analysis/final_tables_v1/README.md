# Final tables package (v1) — 2026-09-21

Versioned compilation of all cutflow/statistics/status tables for this
project's paper reproduction. Every number in every table states its
denominator explicitly (either in the column headers, or in a `notes`/
description column where the table itself is a summary).

All files are copies of already-verified, already-authoritative source
CSVs/JSONs (re-verified against their live values this task — see
`docs/RUN_LOG.md` 2026-09-21 entries) or newly-synthesized summary tables
built directly from those same verified sources. No new simulation was
run to produce any file in this package.

| # | File | Source |
|---|---|---|
| 1 | `01_colored_complete_cutflow.csv` | `colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv` |
| 2 | `02_EW_complete_cutflow.csv` | `ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv` |
| 3 | `03_paper_table1_comparison.csv` | `table1_extraction_v1/paper_vs_project_comparison.csv` |
| 4 | `04_pileup_and_master_cutflow_all_mu.csv` | `final_freeze_v1/master_cutflow_table.csv` |
| 5 | `05_tracking_suppression_statistics.csv` | `pileup_only_statistics_v1/table3_ancestry_suppression.csv` |
| 6 | `06_converted_photon_only_cutflow.csv` | `02_backgrounds/photon_conversion/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv` |
| 7 | `07_converted_photon_plus_pileup_mu50_cutflow.csv` | `02_backgrounds/photon_conversion/conversion_with_pileup_mu50_v1.csv` |
| 8 | `08_event_2555_per_layer/` | `event_2555_forensic_v1/*.json` |
| 9 | `09_statistical_intervals/` | `ppt_statistics_v1/{colored,ew}_complete_statistics.json` + Wilson regression reference |
| 10 | `10_cross_sections_and_weights.csv` | synthesized this task from verified weight/integral values |
| 11 | `11_figure_source_population_table.csv` | synthesized this task from `FINAL_FIGURES_FOR_PPT/` |
| 12 | `12_paper_requirement_vs_implementation_matrix.csv` | synthesized this task from the full paper reread (Phase 1) |
| 13 | `13_assumptions_and_limitations.csv` | synthesized this task |
| 14 | `14_authoritative_vs_obsolete_file_inventory.csv` | `final_freeze_v1/authoritative_obsolete_file_inventory.csv` |
| 15 | `15_final_figure_1_to_7_completion_matrix.csv` | synthesized this task |

## Verification performed
All values in items 1-9 were independently re-derived from their live
source CSVs this task (Phase 2 of the FINAL PAPER COMPLETION AUDIT) and
confirmed to match exactly — see `docs/RUN_LOG.md` and
`docs/FINAL_PAPER_REPRODUCTION_REPORT_v1.md` for the full verification
record.
