# Figure 2 Extension (0–20 cm) — Provenance

## Source located

The stored trajectory used for the existing paper-range (0–5 cm) Figure 2
was **already integrated to a target radius of r = 20 cm**
(`figure2_figure3_reproduction_v1.py`, line 73: `target_r_cm = 20.0`) — the
original Figure 2 plot simply displayed only `ax1.set_xlim(0, 5)` of this
same underlying data. **No new propagation was required or run.**

- Source CSV: `05_coplanarity_analysis/figure2_figure3_v1/Figure_2_source_v1.csv`
  (15,017 rows, r_cm range confirmed [0.0, 19.99999982])
- Generating script: `03_trajectory_sim/figure2_figure3_reproduction_v1.py`
- Originating commit: `b72fe825c19e15cb8eb5e560e1294ee02414a911`
  ("Figure 2/3 reproduction attempt: Fig.2 achieved (diagnostic), Fig.3
  honestly reported as NOT ACHIEVED.")
- Benchmark parameters (unchanged, matches the paper-range figure exactly):
  mQ = 1800 GeV (1.8 TeV), Λ = 2×10⁻⁶ GeV (2 keV), v_internal = 0.6,
  β_cm = 0.3, B = 2.0 T.

## Exported values

`SOURCE_DATA/FIGURE_2_EXTENDED_0_TO_20CM_VALUES.csv` — 15,017 rows,
columns: `r_cm, L_hbar, L_times_1e12_hbar, d_cm`. Every value copied
verbatim from the source CSV (only a derived `L_times_1e12_hbar = L_hbar/1e12`
column added — pure unit conversion, not a new value). Verified by reading
the exported CSV back and comparing element-wise (`np.allclose`) against the
in-memory source array: exact match.

## Plot

`PNG/FIGURE_2_FINAL_EXTENDED_0_TO_20CM_DIAGNOSTIC.png` /
`PDF/.../..._DIAGNOSTIC.pdf` — two vertically-stacked panels, single y-axis
each (no dual axes), shared x-axis r = 0–20 cm:
- Top: L(ħ)×10¹² vs r, turning points marked (local extrema of the discrete
  derivative).
- Bottom: d (cm) vs r, turning points marked, plus the closest-approach
  point (excluding the trivial r≈0 start, where d=0 by construction):
  **r = 4.189 cm, d = 7.407×10⁻⁴ cm**.
- Title: "Extended Quirk Dynamics: Angular Momentum and Separation"
- Subtitle: "Project diagnostic — extended beyond the paper's 0–5 cm display"

Turning points (r_cm): L = [4.189, 8.378, 12.567, 16.756]; d = [2.094,
4.189, 6.283, 8.378, 10.472, 12.567, 14.662, 16.757, 18.853] — the shared
periodicity (Δr ≈ 4.19 cm between successive L turning points, matching
every other d turning point) reflects the internal oscillation period
mapped through the CM boost, consistent with the same physics already
validated for the 0–5 cm range.

## The existing paper-range Figure 2 was NOT modified

`PNG/FIGURE_2_FINAL_Angular_Momentum_Separation_DIAGNOSTIC.png` and
`figure2_figure3_v1/Figure_2_source_v1.csv` are both unchanged (`git diff`
confirms empty diff / untouched).

## SHA-256 hashes

```
bf3d112fb0b33b63ab2c511bd5e1071fa7cb204e0c87cd5931e7f712eb7a2c72  figure2_figure3_v1/Figure_2_source_v1.csv (source, unmodified)
663c9b8d21881d9fe1b745ce5755baaf32998d96845c0732f15fc482070dc835  03_trajectory_sim/figure2_figure3_reproduction_v1.py (source script, unmodified)
98af82a3824e4c0be30a97b2beded98547546dba7efc0b6b4b8588fae01f0c15  SOURCE_DATA/FIGURE_2_EXTENDED_0_TO_20CM_VALUES.csv
154398dfd6e7c4efe1afbcbf5fb0e83b271cd0de57ca00aa2515bfee3f2a2a71  PNG/FIGURE_2_FINAL_EXTENDED_0_TO_20CM_DIAGNOSTIC.png
46b27eea45ad6c7ebf52755bfc389b0e0cb6f8132001abdb0fbe42bcc72ffed8  PDF/FIGURE_2_FINAL_EXTENDED_0_TO_20CM_DIAGNOSTIC.pdf
```

## Plotting command

`python3 SCRIPTS/export_and_plot_figure2_extended.py` (reads only the
existing source CSV; no `quirk_trajectory` import, no new integration).

## Figure 6 status during this task

Confirmed alive and untouched throughout (PID 33950, 16/91 downstream
cells complete at task start and completion).
