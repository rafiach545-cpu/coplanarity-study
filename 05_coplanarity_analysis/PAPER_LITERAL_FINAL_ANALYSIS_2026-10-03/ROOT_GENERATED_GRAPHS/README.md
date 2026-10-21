# ROOT-generated graphs, Figures 3–7

These are the Figures 3–7 of the arXiv:1708.02243 reproduction, drawn with CERN ROOT from the CSV files in `../ROOT_CSV_FIGURES_2026-10-21/`. No other plotting tool was used. Every plotted point is read from those CSVs by the macros in `macros/`. Figure 2 was not touched.

- ROOT 6.40.04 (conda env `/home/rafia/miniconda3/envs/root-env`).
- The macros are compiled with ACLiC (`.C+`) and run in batch mode.
- Created 2026-10-21.

## How to run

```bash
cd ROOT_GENERATED_GRAPHS
./run_all.sh        # activates root-env, runs every macro with "root -l -b -q macros/figN.C+", one log per macro in logs/
```

`macros/common.h` holds three shared pieces:
- a CSV reader that reads every column as `double`;
- one style used by all figures: colored = blue, EW = orange, paper = black;
- `Save()`, which writes `.pdf`, `.png` and a `.root` file holding the canvas.

**Where the folder is.** It sits next to `ROOT_CSV_FIGURES_2026-10-21/`, not inside it. The export script (`scripts/R_export_figures_csv.py`) deletes and rewrites that CSV folder on every run, so outputs inside it would be lost.

## Figures

| Figure | CSV files used | Macro | Output (`.pdf`, `.png`, `.root`) |
|---|---|---|---|
| 3 | `Fig3/fig3_ours_per_event.csv`, `Fig3/fig3_paper.csv` | `macros/fig3.C` | `Fig3/fig3_dphi_vs_r` |
| 4 | `Fig4/fig4_hits_Z0.csv`, `Fig4/fig4_hits_Z1160.csv` | `macros/fig4.C` | `Fig4/fig4_event_display_Z0`, `Fig4/fig4_event_display_Z1160` |
| 5 | `Fig5/fig5_Z0.csv`, `Fig5/fig5_Z1160.csv` | `macros/fig5.C` | `Fig5/fig5_ds_dw_Z0`, `Fig5/fig5_ds_dw_Z1160` |
| 6 | `Fig6/fig6_our_contours.csv`, `fig6_paper_curves.csv`, `fig6_grid.csv`, `F6_reach_numeric.csv` | `macros/fig6.C` | `Fig6/fig6_contours` |
| 6, K-factor sensitivity | `Fig6/fig6_kfactor_lines.csv`, `F6_reach_sensitivity_numeric.csv`, `fig6_paper_curves.csv` | `macros/fig6.C` | `Fig6/fig6_kfactor_sensitivity` |
| 7 | `Fig7/fig7_pixel_hits.csv`, `Fig7/fig7_paper_curves.csv` | `macros/fig7.C` | `Fig7/fig7_dedx_betagamma` |

### Figure 3: rotation Δφ of the velocity plane vs r (B = 2 T, Λ = 2 keV)

**Units**
- Our Δφ is stored in rad; the macro converts it to 10⁻³ rad for panels 1–2.
- The paper's y axis is labelled "Δφ ×10⁻³", so its `dphi_1e-3` column is already in 10⁻³ rad.
- Panel 3 is in rad for both.

**What is drawn**
- **Panels 1–2:** our median over all events at each r (0.1 cm bins), with the 16–84% band, against the paper's curve, which is **one event** (`curve_id` 0 = 1.8 TeV, 1 = 800 GeV).
- **Panel 3:** per event, the median Δφ over r > 14.5 cm, against the paper's event at r = 15 cm.

**Quantiles.** They are computed with `TMath::Quantiles` type 7. A cross-check with pandas gave the same values.

**Result at r = 15 cm**

| Sample | Events | Our median (rad) | Paper's event (rad) |
|---|---|---|---|
| Colored | 22 | 1.89×10⁻⁴ | 0.91×10⁻⁴ |
| EW | 62 | 5.10×10⁻⁴ | 3.53×10⁻⁴ |

Our medians are about 1.4× (EW) and 2.1× (colored) the paper's event. The paper's curve lies inside our 16–84% band at 85% (colored) and 89% (EW) of the r values. At r = 15 cm the colored paper event (0.091×10⁻³) is just below the band's lower edge (0.099×10⁻³).

### Figure 4: event displays in the plane frame (n₃, n₂)

For each sample, the figure shows the event with the median Δs among those passing the full signal region:
- the layers are drawn in grey;
- the right panel zooms in and shows the ±Δw band.

The left panel uses nearly equal x and y scales, as the paper does. The paper's Fig. 4 has no numeric data, so there is no overlay.

| SCT z | Sample | Event | Rank (of N) | Δs | Δw |
|---|---|---|---|---|---|
| None | Colored | 212 | 5 of 8 | 38 µm | 0.352 cm |
| None | EW | 270 | 26 of 50 | 45 µm | 0.100 cm |
| 1.16 mm | Colored | 201 | 1 of 1 | 52 µm | 0.470 cm |
| 1.16 mm | EW | 301 | 6 of 10 | 73 µm | 0.079 cm |

The EW sample is at Λ = 4 keV, as in the report.

### Figure 5: Δs and Δw of signal and backgrounds

**Paper-layout version (2026-10-21):** `Fig5/paper_style_4plots/` holds four plots (Δs and Δw, each without and with smearing, all samples on one plot), made by `macros/fig5_paper_style.C`. Details and differences from the paper are in that folder's README. The panels described below are unchanged.

**Selection.** Events after the plane and hit-multiplicity cuts, before the Δs cut.

**Normalisation.** Ours is a histogram of the events, normalised to unit sum. Values outside the range go into the first or last bin, as in the report.

**Bins.** The paper's histograms each sum to 1 and use 0.1-decade bins. The macro checked that **every paper bin lies on our 0.1-decade grid**, so "fraction per bin" can be compared directly. Where the paper's histogram has gaps, the paper left out its empty bins.

The vertical lines are the cuts Δs < 0.01 cm and Δw < 1 cm. Pile-up only was not simulated without SCT z smearing, so that column is missing from the Z0 figure.

**Below the Δs cut:**

| Sample | SCT z none | SCT z 1.16 mm |
|---|---|---|
| Colored | 8/8 | 1/4 |
| EW | 50/50 | 10/24 |
| Converted γ + pile-up | 146/285 | 0/48 |
| Pile-up only | (not simulated) | 8/109 |

### Figure 6: 3- and 5-event contours at 300 fb⁻¹, no background

**Main figure (`fig6_contours`)**
- Ours: our contours, plus colored without the charge factor (thin orange).
- From the paper: its contours, the HSCP and monojet limits, and the d_cm lines.
- Grid points: dot = ≥ 1 event in the signal region; grey ✕ = 0 events with the 95% UL on N < 3; red ✕ = 0 events, not resolved; open circle = not propagated.
- Hatched: not computed.
- Under each panel title: the maximum reach.

**Check of the lines.** For each line, the macro compares its largest mass with `F6_reach_numeric.csv`. They agree to within 1 GeV for all 12 main lines and all 18 K-factor lines (see `logs/fig6.log`).

**Maximum reach (GeV; paper's figure in brackets)**

| Signal SCT z | Colored excl. / disc. | EW excl. / disc. |
|---|---|---|
| None | 1702 / 1591 (1793 / 1707) | 792 / 701 (762 / 688) |
| 1.16 mm | 1497 / 1424 | 524 / 473 |

**K-factor figure (`fig6_kfactor_sensitivity`)**
- Ours with σ × K, plus the EW LO-ratio trigger (dotted grey), against the paper.
- The legends carry the reach of each line.

### Figure 7: dE/dx and βγ of the pixel hits (Λ = 2 keV)

**Selections**
- **Main:** triggered, fiducial events, first crossing of each layer, t < 25 ns. The same as the report: 376 EW and 160 colored hits.
- **Dashed:** all events, all crossings, t < 25 ns (8558 / 2626 hits).
- **dE/dx:** only hits with βγ ≥ 0.1, as the paper says for its left panel (colored 158 of 160 hits).

**Normalisation**
- **dE/dx panel:** fraction **per unit dE/dx**. The paper's bins are 0.586 MeV cm²/g wide and ours are 2, so fractions per bin cannot be compared.
- **βγ panel:** fraction per 0.1 decade for both, since the bins are the same.

**Medians.** The paper's values are weighted medians of its histograms, as in the report (Section 9.1). `logs/fig7.log` prints the centre of the median bin instead (dE/dx 22.7 / 20.9).

| | Ours, main (colored / EW) | Paper (colored / EW) |
|---|---|---|
| βγ | 0.418 / 0.658 | 0.224 / 0.355 |
| dE/dx (MeV cm²/g) | 6.16 / 3.06 | 22.4 / 20.7 |

## Validation

| Check | Result |
|---|---|
| ROOT works | `root-config --version` = 6.40.04; `root -l -b -q` exits 0 |
| Every macro in batch mode | `./run_all.sh`: fig3–fig7 exit 0 (`logs/run_all.log`) |
| Errors or warnings in the logs | none (`grep -i "error\|warning" logs/fig*.log` is empty) |
| Output files | 24 files (8 figures × pdf/png/root), all non-empty (14–119 kB) |
| ROOT files complete | Fig. 5: 6 / 8 pads, 12 / 16 histograms, each normalised to 1 |
| Data from the CSVs | every macro prints the rows read and the derived numbers. Fig. 3 quantiles cross-checked with pandas (same). Fig. 4 events, Fig. 5 counts (e.g. 146 converted photons below the Δs cut without smearing, as in the report), Fig. 6 reach and Fig. 7 hit counts and medians all agree with the report |
| Units | Fig. 3: ours rad → 10⁻³ rad, paper already 10⁻³ rad; Fig. 5: cm for both; Fig. 6: eV and GeV for both; Fig. 7: MeV cm²/g and βγ for both |
| Bin compatibility | Fig. 5: every paper bin on our grid; Fig. 7: dE/dx bin widths differ (0.586 vs 2), handled by plotting per unit dE/dx |
| Original files | `ROOT_CSV_FIGURES_2026-10-21/`, `ROOT_CSV_2026-10-19/` and `FINAL_FIGURES/` unchanged (git status clean) |

## Open issues (not hidden)

1. **Fig. 3 compares one paper event with our distribution.** The paper shows one representative event per benchmark and does not say how it was chosen. Its caption says "Δθ" while its axis says "Δφ"; we use the axis label. Our medians at r = 15 cm are 1.4× (EW) and 2.1× (colored) the paper's event. The paper's curve lies inside our 16–84% band at 85% / 89% of the r values; the colored event at r = 15 cm is just below the band.
2. **Fig. 5 signal samples are small:** with SCT z 1.16 mm there are 4 colored and 24 EW events; without smearing, 8 and 50. Converted photons (Δs):

   | | Below the cut (Δs < 0.01 cm) | Median Δs |
   |---|---|---|
   | Paper | 6.9% | ≈ 0.031 cm |
   | Ours, no smearing | 51% (146 of 285) | 0.0097 cm |
   | Ours, 1.16 mm | 0% | 0.022 cm |

   Without smearing on the background, ours lies far below the paper's. With 1.16 mm it is close to the paper's but slightly lower and narrower.
3. **Fig. 6 y axis:** the paper uses a mixed axis (log below 1 keV, linear above); here it is log throughout. The curves are in eV in both, so only the look differs.
4. **Fig. 6 variant ids differ between two CSVs.** `fig6_kfactor_lines.csv` uses 1 = K1, 2 = K1.5, 3 = K1.8, 4 = K2, 5 = K0.9, 6 = K1.4, 7 = LO-ratio trigger. `F6_reach_sensitivity_numeric.csv` uses its own ids (9 = LO-ratio trigger). The macro matches the two by the `K` column, and uses id 9 for the LO-ratio line. The line maxima agree with the table (point 4 of the Fig. 6 check).
5. **Fig. 6 colored maxima** are 5–7% below the paper's figure; EW is 2–4% above (see the report, Section 8).
6. **Fig. 7 disagrees with the paper.** Our hits are faster: median βγ about 1.9× the paper's. The paper's low-βγ tail (βγ < 0.1) is not reproduced. Its dE/dx histogram (narrow, starting at 18.9 MeV cm²/g) cannot be obtained from its own βγ histogram with any of four standard dE/dx definitions (report, Section 9.1). The paper does not say what normalisation its y axis uses; we take it as fraction per bin because each of its histograms sums to 1.
