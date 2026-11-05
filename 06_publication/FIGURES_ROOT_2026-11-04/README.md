# Paper figures (ROOT), 2026-11-04

These are new figures for stage 1 (13 TeV) and stage 2 (13.6 TeV). The figures of the reproduction (FINAL_FIGURES, frozen since 2026-10-22) are not touched.

## Run

1. `/home/rafia/venvs/f6fast/bin/python prepare_data.py`
   - Reads the stage CSVs and the background chunk files and writes the plot-ready CSVs in `data/`.
   - `data/sources.json` holds the sha256 of every input.
   - Contour lines use the method of `S2_05_reach.py`. Their mass extent agrees with the reach tables to within 2 GeV.
2. `/home/rafia/miniconda3/envs/root-env/bin/python make_figures_root.py`
   - ROOT 6.40 draws every figure from `data/`.
   - Per figure: `.pdf` (vector), `.png` (250 dpi, rendered from the PDF), `.root` (canvas), `.C` (macro), `caption.md`, `provenance.json`.

## Figures

| Figure | Content | Data |
|---|---|---|
| F01_cross_sections | σ(m_Q) at 13 and 13.6 TeV, both channels, ratio | xsec_and_trigger.csv |
| F02_trigger_and_charge | ε_trig and f_ch, 13 vs 13.6 TeV | xsec_and_trigger.csv |
| F03_reach_13TeV_139fb | stage 1 reach contours, N = 3 / 5, ±1σ | contours.csv, grid_points.csv |
| F04_reach_13p6TeV_332fb | 13.6 TeV, 332 fb⁻¹ against 13 TeV, 139 fb⁻¹ | contours.csv, grid_points.csv |
| F05_reach_13p6TeV_pileup | σ_z = 0 contours with background at μ = 0 / 20 / 50 / 60 | contours.csv, background_13p6TeV_thresholds.csv |
| F06_background_vs_pileup | signal-region fraction vs μ (13 and 13.6 TeV); N_bkg and required signal at 332 fb⁻¹ | background_vs_mu.csv, background_13p6TeV_thresholds.csv |
| F07_mix_test_mu50 | photons × pile-up mixed test, σ_z = 0, μ = 50 | mix_test_mu50.csv |
| F08_reach_summary | maximum reach for every scenario | reach_summary.csv |
| F09_bootstrap_13_vs_13p6 | Δ reach (13.6 TeV − expected) with bootstrap σ | bootstrap.csv |
| F10_selection_efficiency_colored | k/n colored, 13 vs 13.6 TeV, Λ = 2 / 4 / 5 keV | kn_13_vs_13p6.csv |
| F11_expected_events | expected signal events N at the best Λ of every mass point, 13 TeV 139 fb⁻¹ vs 13.6 TeV 332 fb⁻¹, with N = 3 / 5 and the μ = 50 σ_z = 0 requirement | expected_events.csv |
| F12_pulls_13_vs_13p6 | permutation-test pulls of the selection efficiency per mass point, χ² and mean pull per channel | unc_consistency_mass.csv, unc_consistency.csv |
| F13_reach_uncertainty | maximum reach with k/n-only and total statistical 16–84% bands, 13 vs 13.6 TeV | unc_reach.csv |

## Colours

- 13 TeV is orange and 13.6 TeV is blue.
- μ is shown with one blue ramp, from light to dark.
- The SCT setting is green (1.16 mm, Knapen) or violet (σ_z = 0).
- Line styles: exclusion is dashed, discovery is solid, and the ±1σ band is dotted.

The report built from these figures is `../REPORT_2026-11-04/QUIRK_13_13p6TeV_REPORT_2026-11-04.pdf` (`make_report.py`).
