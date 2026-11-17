# Geometry figures (2026-11-17)

These figures show the inner detector exactly as simulated: Ideal (Knapen et al.) vs ATLAS Run 2 ID. The text, numbers and references are in `../GEOMETRY_COMPARISON.md`.

**Input.** All element positions come from `../tables/X06_geometry_elements.csv`. That table is written by `../compare/X06_geometry_comparison.py` from `sim/detsim07.build()`, the geometry objects the simulation uses. No number is typed by hand.

**ROOT figures** (ROOT 6.40):

```
/home/rafia/miniconda3/envs/root-env/bin/python make_geometry_figures.py
```

| Figure | Content |
|---|---|
| GEO1 | R–z quarter section, Ideal vs ATLAS |
| GEO2 | the pixel region |
| GEO3 | transverse view at z = 0 |

**3D cut-away views** (matplotlib, true scale):

```
/home/rafia/venvs/f6fast/bin/python make_geometry_3d.py
```

| Figure | Content |
|---|---|
| GEO4 | the Ideal geometry, each barrel layer labelled |
| GEO5 | the full ATLAS Run 2 ID model |

The notebook copies the drawing code of `make_geometry_3d.py` unchanged.

**Google Colab version.**

```
/home/rafia/venvs/f6fast/bin/python build_colab_notebook.py
```

This writes `geometry_visualization_colab.ipynb`. Upload the notebook to Colab and choose *Runtime → Run all*. It needs only numpy and matplotlib and draws all five views.
