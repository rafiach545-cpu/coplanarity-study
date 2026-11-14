# Stage 1: 13 TeV, 139 fb⁻¹, Knapen geometry, no pile-up, coplanarity

Publication plan (whiteboard, 2026-11-03), step 1. Run: `/home/rafia/venvs/f6fast/bin/python S1_reach_139fb.py`.

- **Setup:** identical to the validated reproduction (`05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03`, Fig. 6 grid): 13 TeV, MG5 3.7.3 + Pythia8 (0 + 1 jet, MLM), Nambu–Goto integrator, B = 2 T, 8-layer barrel of arXiv:1708.02243, trigger pT(QQ̄) > 200 GeV, the paper's plane-finding cuts, no pile-up on the signal.
- **Only change:** L = 139 fb⁻¹ instead of 300 fb⁻¹. N = L σ ε is linear in L, so all N in `F6_N_grid.csv` are scaled by 139/300. No new simulation.
- **SCT z:** σ_z = 1.16 mm is the Knapen setting (main). σ_z = 0 is shown for comparison.
- **Statistics:** zero background, 3 events = exclusion, 5 = discovery (as in the paper). Bands: Wilson 68% on k/n.

| | Exclusion (GeV) | Discovery (GeV) | 300 fb⁻¹ (excl. / disc.) |
|---|---|---|---|
| Colored, σ_z = 1.16 mm | 1388 (1332–1445) | 1316 (1262–1370) | 1497 / 1424 |
| Colored, σ_z = 0 | 1535 (1488–1584) | 1452 (1419–1484) | 1702 / 1591 |
| EW, σ_z = 1.16 mm | 451 (419–487) | 408 (357–441) | 524 / 473 |
| EW, σ_z = 0 | 666 (646–685) | 597 (579–615) | 792 / 701 |

Background at 139 fb⁻¹ (converted photons, σ_γ = 0.211 pb × 1%), **no pile-up** (this stage; conversion only, same hard part and material model as the report's backgrounds): σ_z = 1.16 mm 0/9139 (< 0.096 events, 95% UL); σ_z = 0 1/9139 (0.032 events). Zero background holds for both settings, and 3 events is the 95% CLs level (2.996) in both. For reference, with μ = 50 pile-up (reproduction report): 0/9139 and 146/9139 (4.7 events, 95% CLs needs about 6.5 signal events); the σ_z = 0 background comes almost entirely from pile-up.

Files: `S1_N_grid_139fb.csv`, `S1_reach_139fb.csv`, `S1_background_139fb.csv`, `S1_fig_reach_139fb.png/.pdf`.

## Run 2 pile-up for the backgrounds (2026-11-03, user's request)

The reproduction ran the pile-up part of the backgrounds at μ = 50. For 139 fb⁻¹ shown as Run 2, the backgrounds are rerun with the Run 2 mean ⟨μ⟩ = 33.7 (ATLAS 2015–2018, luminosity-weighted): `S1_pileup_run2.py {P10|P17b|P8}` loads the original scripts unchanged and replaces only MU and the output folder (`logs/<run>_mu33p7/`). Same photons and seeds, so μ = 33.7 and μ = 50 are compared on the same events. Signal efficiencies are unchanged (the signal has no pile-up).
- Check before the runs: the wrapper at μ = 50 must reproduce chunk 0 of the original P10 run row by row.

### Results at μ = 20 and ⟨μ⟩ = 33.7 (`S1_background_run2_summary.py` → `S1_background_run2.csv`)

| Background | μ | plane / multiplicity / SR | N_bkg at 139 fb⁻¹ | 95% CLs signal |
|---|---|---|---|---|
| conversion + PU, σ_z = 1.16 mm | 50 | 1990 / 48 / 0 of 9139 | < 0.096 | 3.0 |
| | 33.7 | 1851 / 30 / 0 of 9139 | < 0.096 | 3.0 |
| | 20 | 1790 / 14 / 0 of 9139 | < 0.096 | 3.0 |
| | 0 | 0 of 9139 (B_Z1160_nomat) | < 0.096 | 3.0 |
| conversion + PU, σ_z = 0 | 50 | 4105 / 285 / 146 of 9139 | 4.69 | 6.50 |
| | 33.7 | 4032 / 241 / 154 of 9139 | 4.95 | 6.36 |
| | 20 | 3998 / 170 / 115 of 9139 | 3.69 | 6.05 |
| | 0 | 1 of 9139 (B_Z0_ref34) | 0.032 | 3.0 |
| pile-up only, σ_z = 1.16 mm | 50 | 109 / 1 / 0 of 5000 | prob. < 6×10⁻⁴ per event | — |
| | 33.7 | 39 / 0 / 0 of 5000 | prob. < 6×10⁻⁴ per event | — |
| | 20 | 10 / 0 / 0 of 5000 | prob. < 6×10⁻⁴ per event | — |

- σ_z = 1.16 mm (Knapen): zero background at every μ (0, 20, 33.7, 50); the reach in the table above stands.
- σ_z = 0: going from μ = 50 to 33.7 does not reduce the background (146 → 154, within statistics). Only 52 events pass at both μ; the others differ, so passing is set by the random pile-up configuration, not by the photon. With about 5 background events, the σ_z = 0 contours need ~6.4 signal events instead of 3, so those contours are optimistic once pile-up is present.
- σ_z = 0 at μ = 20: 115/9139 (3.7 events, ~6 signal events for 95% CLs). The background appears as soon as there is pile-up and depends only weakly on μ (0.03 → 3.7 → 4.9 → 4.7 events for μ = 0 / 20 / 33.7 / 50). Passing events again differ between μ (115 at μ = 20, 26 shared with μ = 50, 11 shared by all three).
- μ = 20 was run twice in parallel by mistake (watcher and manual chain, same seeds, writing to the same folder); every chunk was checked afterwards: same row counts as μ = 33.7, no duplicates, no errors.
