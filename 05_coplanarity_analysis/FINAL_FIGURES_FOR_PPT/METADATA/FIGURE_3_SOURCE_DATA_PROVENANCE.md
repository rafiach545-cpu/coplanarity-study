# Figure 3 (Plane Rotation) — Source-Data Provenance

## 1. Source identification

- **Plotting/generation script:** `03_trajectory_sim/figure3_diagnostic_v2.py`
  (byte-identical copy at `05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SCRIPTS/figure3_diagnostic_v2.py`)
- **Input data:** two per-config CSVs, produced by the same script (no external
  input files — the script builds physically-consistent lab-frame 4-momenta
  internally, then calls `quirk_trajectory.py::integrate_trajectory`, the
  same, unmodified integrator used project-wide):
  - `05_coplanarity_analysis/figure3_diagnostic_v2/figure3_source_J_colored_natural_config_v2.csv` (colored)
  - `05_coplanarity_analysis/figure3_diagnostic_v2/figure3_source_K_ew_natural_config_v2.csv` (EW)
- **Git commits:**
  - `67cbbe2a2b0634d31481cb85bdf0c21a571535ba` — "Figure 3 diagnostic (v2): correct measurement bug, achieve reproduction" (originating commit for script + both CSVs + PNG/PDF)
  - `83a4ab997799c88433cdde6e5e0e4f628d9c4a70` — "Create single organized FINAL_FIGURES_FOR_PPT package for all figures" (packaging commit; copies verified byte-identical to the originating commit's files, confirmed via SHA-256 match)
- **Colored benchmark parameters:** mQ = 1800 GeV (1.8 TeV), Λ = 2×10⁻⁶ GeV (2 keV) — **CONFIRMED**, `configs` list, `figure3_diagnostic_v2.py` line 238.
- **EW benchmark parameters:** mQ = 800 GeV, Λ = 2×10⁻⁶ GeV (2 keV) — **CONFIRMED**, line 242, explicitly commented "Fig.3's second curve, paper's own second benchmark point, Lambda=2keV" — **not** the separate Table I EW benchmark (800 GeV, 4 keV) used elsewhere in this project for Table I comparisons.
- **Magnetic field:** B = 2.0 Tesla, along lab z-axis (line 242, `B_tesla=2.0`), identical treatment to the rest of the project.
- **Plane-normal definition:** n_v(t) = v1(t) × v2(t), normalized, where v1,v2 are the two quirks' instantaneous **lab-frame velocity vectors** (p/E). This is a different quantity from `coplanarity_fit.py`'s fitted-hit-plane normal n3 (used for Figures 4/5) — Figure 3 measures the true underlying kinematic plane, not a detector-hit fit.
- **Angle definition/"unwrapping" method:** for each valid sample k, `dphi[k] = arccos(clip(dot(n_v_hat[k], ref), -1, 1))`, where `ref = n_v_hat[idxs[0]]` is the **first valid sample in the entire array**, with a hemisphere flip (`if dot<0: h=-h`) to resolve the plane-normal sign ambiguity. **Important correction to prior documentation:** this is a single fixed-reference angular-distance metric, computed independently at each sample — it is **not** a running/cumulative unwrap, and there is **no per-segment reference re-anchoring** anywhere in the code, despite `figure3_diagnostic_metadata_v2.json`'s existing `caveat_residual_spike_artifacts` text claiming "the reference direction is re-anchored to the first sample of each new segment." That claim does not match the code as written (verified by direct read, lines 159–169) and should be corrected in that file — flagged here, not silently fixed (per the read-only/no-file-modification instruction for this audit... wait, this file itself IS a new file, not an edit to the existing metadata; the existing `figure3_diagnostic_metadata_v2.json` was left untouched).
- **Degeneracy/validity threshold:** `valid = nv_mag > 0.1 * median(nv_mag[nv_mag > 0])` (line 154-155) — a percentile-based exclusion of near-antiparallel v1≈−v2 crossings where |v1×v2|→0 and its direction becomes numerically ill-conditioned.

## 2. Exported CSVs

- `SOURCE_DATA/FIGURE_3_FINAL_Plane_Rotation_VALUES.csv` — combined, 24,403 rows
- `SOURCE_DATA/FIGURE_3_COLORED_VALUES.csv` — 7,509 rows
- `SOURCE_DATA/FIGURE_3_EW_VALUES.csv` — 16,894 rows

Every row is copied verbatim (`r_cm`, `dphi_rad`, `valid`) from the original,
already-committed per-config CSV — no interpolation, smoothing, or
recalculation. One column, `velocity_cross_product_norm`, is marked
**UNAVAILABLE** in every row: `nv_mag = |v1×v2|` is computed in-memory by
the original script but was never written to its output CSV, and recovering
it would require re-running the trajectory integration — explicitly
forbidden for this audit. `angle_unwrapped` is populated as identical to
`delta_phi_rad`, since the stored quantity already *is* the (non-cumulative,
fixed-reference) unwrapped angle described above.

## 3. Spike diagnostics

`SOURCE_DATA/FIGURE_3_SPIKE_DIAGNOSTICS.csv` — 8 candidate jumps found
(threshold: |Δ(delta_phi) between consecutive plotted points| ≥ 5×10⁻⁵ rad):

| Classification | Count | Basis |
|---|---|---|
| NEAR_DEGENERACY_ARTIFACT | 4 | Plotted point sits adjacent (in raw sample index) to ≥1 excluded near-degenerate sample |
| PHYSICAL_TREND | 4 | No adjacent excluded sample; consistent with ordinary oscillatory accumulation |
| UNRESOLVED | 0 | none found at this threshold |

No point was deleted, smoothed, or altered to produce this classification.

## 4. Independent validation

| | Colored | EW |
|---|---|---|
| Row count | 7,509 | 16,894 |
| r_cm range | [0.0, 19.999999986] cm | [0.0, 19.999999921] cm |
| delta_phi_rad range | [0.0, 4.610×10⁻⁴] | [0.0, 6.075×10⁻⁴] |
| Finite count | 7,509 / 7,509 | 16,894 / 16,894 |
| NaN/Inf count | 0 | 0 |
| Duplicate (r_cm, delta_phi_rad) rows | 0 | 0 |

Agreement between exported CSV and original plotted arrays: max absolute
difference 3.55×10⁻¹⁵ cm (r_cm), 3.39×10⁻²¹ rad (delta_phi) — floating-point
CSV round-trip noise only, not a real discrepancy. All `valid` flags
preserved exactly.

## 5. Cache-only reproduction

`SCRIPTS/plot_figure3_final_from_csv.py` reads only
`FIGURE_3_FINAL_Plane_Rotation_VALUES.csv` (imports only pandas/matplotlib —
no `quirk_trajectory`, no simulation). Produces
`PNG/FIGURE_3_FINAL_Plane_Rotation_FROM_CSV.png` and the matching PDF.
Points plotted: colored 7,159 / 7,509 (valid only), EW 16,088 / 16,894
(valid only) — matches the original script's `cv = c[c["valid"]]` filter
exactly.

## 6. Numerical comparison, original vs. cache-only reproduction

- Underlying data: **exact** (see §4 above — differences at floating-point
  noise level only).
- Every plotted point preserved: **yes**.
- Image SHA-256: **differs** (`63225ac2…` original vs `473005b8…` cache-only)
  — expected, since the cache-only version adds the required caption text
  box and was rendered in a separate matplotlib session (font-cache/metadata
  differences), not because any data value changed.
- **Confirmed: no physics value changed.**

## 7. Units, limitations, why approximate

- Units: r in cm, Δφ in radians (plotted ×10⁻³ to match the paper's own
  y-axis convention).
- **Why approximate, not exact:** (a) the paper does not publish its own
  exact initial orientation (boost direction relative to internal-motion
  tilt) for its representative Fig. 2/3 events — this script uses the same
  simple, unperturbed orientation already validated for this project's
  Figure 2 reproduction, a disclosed project assumption, not a value read
  from a specific real signal event; (b) ISR recoil is not modeled; (c) the
  angle metric itself (fixed-reference arccos distance, not a true
  continuous unwrap) is a diagnostic approximation of the paper's own
  (unspecified) angle-accumulation method.
- Residual spikes are a genuine, documented feature of this specific
  angle-measurement method, not evidence the underlying physics is wrong —
  see §3.

## 8. Verification exit codes

All three scripts (`export_figure3_source_values.py`,
`figure3_spike_diagnostics.py`, `plot_figure3_final_from_csv.py`) ran to
completion, exit code 0, no exceptions.

## SHA-256 hashes

```
222990868b308d5c987e88aae211d0e474828e7894ee316ddc8adf29afc16b93  figure3_diagnostic_v2/figure3_source_J_colored_natural_config_v2.csv
f563d88b422c5875edccbe4ed3caed6e7daebd7ddf6f9a2ea2ad3e0a155ac9da  figure3_diagnostic_v2/figure3_source_K_ew_natural_config_v2.csv
028efb5277a43fe68d73c3b9bf96a25b8f6c83fc0665ccff8b115f95ceb102f8  03_trajectory_sim/figure3_diagnostic_v2.py
63225ac2a368d1f49bb5891cdf32406c201e2ed5c5d1567b58d073d9b10d0dd1  FINAL_FIGURES_FOR_PPT/PNG/FIGURE_3_FINAL_Plane_Rotation.png (original, unmodified)
473005b8a53af0472e4073d5faf79cc027be076121f3036b6117e92f19d4395b  FINAL_FIGURES_FOR_PPT/PNG/FIGURE_3_FINAL_Plane_Rotation_FROM_CSV.png (new, cache-only)
8db5b4abfc244293129a1b8e233fc4d2409c7dbe86bef29dd981bf662ef288a2  FINAL_FIGURES_FOR_PPT/PDF/FIGURE_3_FINAL_Plane_Rotation_FROM_CSV.pdf
846180fcd824451e92f06f8ec03e21f8a042c6b6749c11ec833ffcae221e99f0  SOURCE_DATA/FIGURE_3_FINAL_Plane_Rotation_VALUES.csv
82b8c5f2c757b0549459696949dce8d4758ec66aa4ea4490ecac6bdbd6910737  SOURCE_DATA/FIGURE_3_COLORED_VALUES.csv
2b975eb5d9925a0eb2046e8fb23b474c156517f5191fcd62363437917653e190  SOURCE_DATA/FIGURE_3_EW_VALUES.csv
02212e3e98a960983e1300c9c96d31472892b01dd2fef3b2d722a0a177e462d8  SOURCE_DATA/FIGURE_3_SPIKE_DIAGNOSTICS.csv
c4e38dbaec20a24d4a009f0496e6f24aaeb9cd43f3eede79e7560423deb6800c  SCRIPTS/export_figure3_source_values.py
3de280b6070ed4132324443e0e86d2c3b0bbea24604f6b1207125df209752820  SCRIPTS/figure3_spike_diagnostics.py
f2258ef031a36e0684cc697aaee6d9a1c4da28316bef0144acc6e3ca7ca26b4d  SCRIPTS/plot_figure3_final_from_csv.py
```

## Note: the existing authoritative Figure 3 was NOT altered

`PNG/FIGURE_3_FINAL_Plane_Rotation.png` and its PDF counterpart are
untouched (hash-confirmed identical to before this audit). Only new files
were added.
