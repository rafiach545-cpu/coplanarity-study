# Signal figures in the style of the paper, Stage 2 · Run 3 · ATLAS vs Stage 1 · Run 3 · Ideal (ROOT, 2026-11-18)

These figures need no background input. Both geometries use the same 10k-generated events at 13.6 TeV.

| Figure | Content | Paper analogue |
|---|---|---|
| S01_table_I_cutflow | step efficiencies at the Table I benchmarks (colored 1800 GeV / 2 keV, EW 800 GeV / 4 keV), three SCT settings; `Table_I.md` | Table I |
| S02 / S03 / S04_fig5_ds_dw_{A580, Z1160, Z0} | Δs and Δw of the reconstructed plane, benchmarks | Fig. 5 |
| S05_merge_multiplicity_sensitivity | signal vs pixel-merge adjacency (0 / 1 / 2) and multiplicity threshold (14 / 15 / 16) | — (RESULTS §7.1) |

Not redrawn:
- Figs. 2–3 (quirk dynamics) do not depend on the detector geometry; they are the 05 / 06 figures.
- The reach contours without background are G05 in `FIGURES_ROOT_2026-11-17`.
- The background figures (G06–G09) wait for the 100k Zγ runs.

How to make them:
1. `/home/rafia/miniconda3/envs/hep/bin/python prepare_signal_data.py` → `data/*.csv` and `data/sources.json` (sha256 of the inputs).
2. `/home/rafia/miniconda3/envs/root-env/bin/python make_signal_figures.py` → `Sxx_*/` (pdf, png, root, C, caption.md, provenance.json).
