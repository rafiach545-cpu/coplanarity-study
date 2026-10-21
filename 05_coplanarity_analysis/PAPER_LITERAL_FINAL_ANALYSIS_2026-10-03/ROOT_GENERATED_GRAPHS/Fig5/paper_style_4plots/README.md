# Figure 5 in the paper's layout: four plots

Four plots, made with ROOT 6.40.04 from the existing CSVs (2026-10-21):
- Δs and Δw;
- each without and with SCT z smearing;
- every sample of one case on one plot, as in the paper.

The earlier 6- and 8-panel versions (`../fig5_ds_dw_Z0.*`, `../fig5_ds_dw_Z1160.*`, made by `macros/fig5.C`) are kept unchanged. No other figure, CSV or source file was modified.

| Plot | Files (`.pdf`, `.png`, `.root`) |
|---|---|
| Δs without smearing | `fig5_ds_without_smearing` |
| Δw without smearing | `fig5_dw_without_smearing` |
| Δs with smearing (SCT z 1.16 mm) | `fig5_ds_with_smearing` |
| Δw with smearing (SCT z 1.16 mm) | `fig5_dw_with_smearing` |

- **Macro:** `fig5_paper_style.C`, a copy of `../../macros/fig5_paper_style.C`. It uses `../../macros/common.h`.
- **Log:** `fig5_paper_style.log`.
- **Run, from `ROOT_GENERATED_GRAPHS/`:** `root -l -b -q "macros/fig5_paper_style.C+"`

## What the paper's Figure 5 shows (figures/Deltat.pdf and Deltaw.pdf of arXiv:1708.02243 v2, read before plotting)

The paper has two plots, Δs (left) and Δw (right), each with four samples:

| Sample | Paper's style |
|---|---|
| Colored quirk (m_Q = 1.8 TeV, Λ = 2 keV) | purple, solid |
| EW quirk (800 GeV, Λ = 4 keV) | red, solid |
| Pile-up | green, dashed |
| Converted γ | blue, dashed |

**Axes**
- Bins are 0.1 decade wide on a log x axis; the y axis is log.
- Δs runs from 10⁻³ to 10⁻¹ cm, and the cut Δs < 0.01 cm is marked with an arrow.
- Δw runs from 5×10⁻³ to 1 cm.

**y axis**
- Δs: dσ/d log Δs in **fb/bin**, an absolute cross section.
- Δw: (1/σ) dσ/d log Δw, unit area.

The paper uses one smearing setting and does not say which. We show both of ours.

## What is plotted here

**Samples (ours, from `../../../ROOT_CSV_FIGURES_2026-10-21/Fig5/fig5_Z0.csv` and `fig5_Z1160.csv`)**
- **Selection,** unchanged from the report: after the plane and hit-multiplicity cuts, before the Δs cut.
- **Without smearing:** no SCT z smearing on signal or backgrounds.
- **With smearing:** SCT z 1.16 mm on signal and backgrounds.
- **Converted γ** is simulated with pile-up (μ = 50) overlaid; the legend says so.
- **Pile-up only** was not simulated without smearing, so it is absent from those two plots; the legend says so.

**Normalisation:** both observables are drawn as a fraction of the events per 0.1-decade bin, (1/N) dN/d log Δ, normalised over all events.
- For Δw this is the paper's own normalisation.
- For Δs the paper's axis is absolute (fb/bin), but the CSVs contain no cross section for any sample at this selection stage. Drawing ours in fb would require cross sections that we do not have here, so Δs is also shown with unit area.
- For reference, the paper's Δs histograms total 0.0041 fb (colored), 0.0076 fb (EW), 2.65 fb (pile-up) and 0.067 fb (converted γ) (`tables/paper_fig5_vector.json`).

**Binning**
- Our bins are the paper's 0.1-decade grid over a wide range (Δs 10⁻⁵ to 10 cm, Δw 10⁻⁴ to 10 cm), and no value is moved into an edge bin.
- 1 event lies outside the drawn axis range: one pile-up Δs at 0.0009 cm in the with-smearing plot. The log reports it.
- Every paper bin lies on the same grid (checked earlier in `macros/fig5.C`).

**Paper overlay**
- Thin dotted lines in the same colours: the paper's histograms normalised to unit sum. They are the same in all four plots, because the paper's figure does not depend on our smearing.
- They are read from `fig5_Z1160.csv`. Its paper rows are identical to those of `fig5_Z0.csv` (108 rows, checked), and only this file also has the paper's pile-up histogram.

**Style:** ours follows the paper: signal solid, backgrounds long-dashed, thick, semi-transparent.

## Validation

| Check | Result |
|---|---|
| ROOT batch run | `root -l -b -q "macros/fig5_paper_style.C+"`, exit 0 |
| Log | no error or warning lines (`grep -i "error\|warning" fig5_paper_style.log` empty) |
| Output files | 12 files (4 plots × pdf/png/root), all non-empty |
| Histograms in each `.root` canvas | ours: 3 (without smearing) / 4 (with smearing), each with integral 1.000; paper: 4 in each |
| Event counts (same as the report and `macros/fig5.C`) | without smearing: colored 8, EW 50, converted γ 285; with smearing: colored 4, EW 24, converted γ 48, pile-up 109 |

## Results and differences from the paper

**Δs: fraction below the cut (Δs < 0.01 cm) and median Δs**

| Sample | Paper | Ours, no smearing | Ours, SCT z 1.16 mm |
|---|---|---|---|
| Colored | 90%, 0.0035 cm | 8/8 (100%), 0.0038 cm | 1/4 (25%), 0.016 cm |
| EW | 92%, 0.0028 cm | 50/50 (100%), 0.0044 cm | 10/24 (42%), 0.011 cm |
| Converted γ | 6.9%, 0.028 cm | 146/285 (51%), 0.0097 cm | 0/48 (0%), 0.022 cm |
| Pile-up | 0.2%, 0.056 cm | not simulated | 8/109 (7.3%), 0.032 cm |

**Δw: median Δw (all samples satisfy Δw < 1 cm by selection)**

| Sample | Paper | Ours, no smearing | Ours, SCT z 1.16 mm |
|---|---|---|---|
| Colored | 0.089 cm | 0.48 cm | 0.55 cm |
| EW | 0.045 cm | 0.097 cm | 0.092 cm |
| Converted γ | 0.14 cm | 0.44 cm | 0.35 cm |
| Pile-up | 0.56 cm | not simulated | 0.78 cm |

**What smearing does**
- **Without SCT z smearing,** our signal Δs agrees with the paper: the medians are within about 10–60%, and nearly all events are below the cut.
- **With 1.16 mm smearing,** our signal Δs moves above the paper's (median 0.011–0.016 cm), and only 25–42% of the signal passes the cut. This is the same conclusion as the report: only no smearing reproduces the paper's signal.

**Converted photons**
- With 1.16 mm smearing, ours (median 0.022 cm) is close to the paper's (0.028 cm), and none pass the cut (paper: 6.9%).
- Without smearing on the background, ours moves down to a median of 0.0097 cm, and 51% pass the cut.
- So the paper's signal matches our unsmeared case, while the paper's converted-photon distribution matches our smeared case. No single smearing setting reproduces both.

**Δw**
- Our signal Δw is wider than the paper's: EW about 2×, and colored 5–6× (based on only 4–8 events).
- Our converted photons are wider too (0.35–0.44 vs 0.14 cm).
- Pile-up with smearing is shifted up (0.78 vs 0.56 cm). Our pile-up selection includes Δw < 1 cm, so its distribution ends at 1 cm.

**Small samples:** the colored signal has 4 (smeared) and 8 (unsmeared) events, and EW has 24 and 50. The shapes of the colored histograms are therefore only indicative.

**Absolute Δs scale:** this cannot be compared, because the paper's axis is in fb and ours has unit area (see above).
