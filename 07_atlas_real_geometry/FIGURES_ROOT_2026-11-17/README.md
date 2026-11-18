# 07 ROOT figures (2026-11-17)

These figures are new. Existing figures in 06 are not changed. All are drawn with ROOT 6.40, using the style and helpers of `06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py`, executed unchanged.

## Naming

The figures use the simulation-matrix names (2026-11-17):

- **S2 · Run 3 · ATLAS** = Stage 2 · Run 3 · ATLAS: this folder, 10k samples.
- **S1 · Run 3 · Ideal (2k)** = Stage 1 · Run 3 · Ideal with 2000 events: 06 S2, called "Stage 2" in older figures.

Data tags in `data/`: `S2_Run3_ATLAS_*` and `S1_Run3_Ideal_2k*`.

## Rebuilding

```
bash ../reach/R00_postprocess.sh <tag>
```

This runs R01 reach, then `prepare_data_07.py` (writes `data/`), `make_figures_07.py` (ROOT), tests T11 and T09, and the R02 summary.

- Python: `/home/rafia/venvs/f6fast/bin/python`
- ROOT: `/home/rafia/miniconda3/envs/root-env/bin/python`
- The PNG is rendered from the PDF with `pdftoppm` at 250 dpi.

## Files per figure

| File | Content |
|---|---|
| `<name>.pdf` | the figure |
| `<name>.png` | the figure, rendered from the PDF |
| `<name>.root` | the ROOT canvas |
| `<name>.C` | the ROOT macro |
| `caption.md` | the caption |
| `provenance.json` | sha256 of the plotted data files and of every upstream input (`data/sources.json`) |

## Figures

| Figure | Content | Data |
|---|---|---|
| G01 | σ, trigger efficiency, f_ch vs m_Q: Stage 2 · Run 3 · ATLAS 10k vs Stage 1 · Run 3 · Ideal 2k | `xsec_and_trigger.csv` |
| G02 | quirk velocity β = \|p\|/E and β_T = p_T/E | `beta_summary.csv`, `beta_hist.csv` |
| G03 | fiducial efficiency vs Λ: 07 rule, barrel rule on Stage 2 · Run 3 · ATLAS trajectories, Stage 1 · Run 3 · Ideal (2k) | `efficiency_vs_lambda.csv` |
| G04 | selection efficiency k/n vs Λ for Z0 / A580 / Z1160, and Stage 1 · Run 3 · Ideal (2k) | `efficiency_vs_lambda.csv` |
| G05 | reach contours, zero background, 332 fb⁻¹, 3 SCT settings × 2 channels, with Stage 1 · Run 3 · Ideal (2k) | `contours.csv`, `grid_points.csv` |
| G06 | reach with the converted-photon background vs μ, A580 | `contours.csv`, `background_thresholds.csv` |
| G07 | the same for Z0 (σ_long = 0) | `contours.csv`, `background_thresholds.csv` |
| G08 | converted-photon background vs μ (barrel-like / end-cap parts, upper limits, Stage 1 · Run 3 · Ideal) | `background_vs_mu.csv` |
| G09 | maximum reach summary | `reach_summary.csv` |
| G10 | conversion probability vs \|η\| from the material (M01), with variants | `material_conversion_vs_eta.csv` |

## Checks

- **T10:** the contour code reproduces the 06 contour lines exactly.
- **T09:** the reach code reproduces the Stage 1 · Run 3 · Ideal (2k, 06 S2) tables exactly.
- **T11:** the grid is recounted independently from the raw files.

## Layout note

The canvas width is at most 1800 px. Wider canvases (above 21 cm at 100 px/cm) are cut on the right by the ROOT PDF page.
