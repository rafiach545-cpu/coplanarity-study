THIS IS THE ONLY DIRECTORY TO USE FOR THE FINAL PPT.

All figures below are read directly from already-completed, previously
verified project results. No new simulation was run to build this
package; it is a pure organizational/re-packaging pass, with two
exceptions that are purely re-plots of already-frozen numeric data (no
new physics): the FIGURE_5A/5B single-panel splits, and codifying the
FIGURE_5/5C combined-panel plots into a standalone, reproducible script
(they were previously only run via inline Bash heredocs in an earlier
session turn — now saved as `SCRIPTS/plot_figure5_main.py`, verified to
reproduce the existing authoritative images before being trusted).

## Quick reference table

| Paper Figure | Final File | Status | Safe for PPT? |
|---|---|---|---|
| Fig.1 | FIGURE_1_FINAL_Quirk_Schematic.png | FINAL_APPROXIMATE (conceptual schematic) | YES, WITH APPROXIMATE LABEL |
| Fig.2 | FIGURE_2_FINAL_Angular_Momentum_Separation_DIAGNOSTIC.png | DIAGNOSTIC_ONLY (achieved, single event) | YES, WITH APPROXIMATE LABEL |
| Fig.3 | FIGURE_3_FINAL_Plane_Rotation.png | FINAL_APPROXIMATE (achieved this task) | YES, WITH APPROXIMATE LABEL |
| Fig.4 | FIGURE_4_FINAL_Reconstructed_Event_VERTEX_FIXED.png | FINAL_APPROXIMATE | YES, WITH APPROXIMATE LABEL |
| Fig.5 (combined) | FIGURE_5_FINAL_DeltaS_DeltaW_FOUR_COMPONENT.png | FINAL_APPROXIMATE | YES, WITH APPROXIMATE LABEL |
| Fig.5 (Δs panel) | FIGURE_5A_FINAL_DeltaS_FOUR_COMPONENT.png | FINAL_APPROXIMATE | YES, WITH APPROXIMATE LABEL |
| Fig.5 (Δw panel) | FIGURE_5B_FINAL_DeltaW_FOUR_COMPONENT.png | FINAL_APPROXIMATE | YES, WITH APPROXIMATE LABEL |
| Fig.5 (absolute) | FIGURE_5C_FINAL_Absolute_Three_Component_CORRECTED.png | FINAL_APPROXIMATE | YES, WITH APPROXIMATE LABEL |
| Fig.6 | none (blocked) | BLOCKED | NO — BLOCKED |
| Fig.7 | none (blocked) | BLOCKED | NO — BLOCKED |

## Per-figure detail

### FIGURE_1_FINAL_Quirk_Schematic.png
- **Status:** FINAL_APPROXIMATE
- **Shows:** conceptual 3D schematic — quirk pair trajectories (green), ISR jet (blue), 3 tracker-layer cylinders (gray), hits (black dots) all lying exactly on a shaded plane by construction
- **Sample used:** none — pure illustrative matplotlib construction, no simulated data
- **Exact/approximate/diagnostic:** conceptual illustration, not a numerical reproduction
- **Normalization:** N/A
- **Limitation:** illustrative only; does not carry a physics result
- **Source data:** `SOURCE_DATA/FIGURE_1_FINAL_metadata_source.json`
- **Script:** `SCRIPTS/figure1_schematic_v1.py`

### FIGURE_2_FINAL_Angular_Momentum_Separation_DIAGNOSTIC.png
- **Status:** DIAGNOSTIC_ONLY (achieved; kept diagnostic per naming convention since it is a single representative event, not a population result)
- **Shows:** internal angular momentum L and separation d vs radial CM distance r, colored benchmark
- **Sample used:** 1 representative event (deterministic RK4 integration)
- **Exact/approximate/diagnostic:** achieved — L~10¹²ℏ matches the paper's own stated order of magnitude
- **Normalization:** N/A
- **Limitation:** initial orientation is a project assumption, not read from a real ISR-recoil event; d touches 0 at r≈4.2cm, in some tension with the paper's "never vanishes except at origin" claim
- **Source data:** `SOURCE_DATA/FIGURE_2_FINAL_source.csv`
- **Script:** `SCRIPTS/figure2_figure3_reproduction_v1.py`

### FIGURE_3_FINAL_Plane_Rotation.png
- **Status:** FINAL_APPROXIMATE — see `METADATA/FIGURE_3_STATUS.txt` for the full correction history
- **Shows:** Δφ (plane-normal rotation of the quirks' velocity vectors) vs radial CM distance, both benchmarks
- **Sample used:** 2 representative events (colored 1.8TeV/2keV, EW-mass 800GeV/2keV)
- **Exact/approximate/diagnostic:** approximate — correct definition, correct order of magnitude (max ~4.6×10⁻⁴/6.1×10⁻⁴ rad vs paper's 0–4×10⁻⁴ rad range), correct qualitative shape
- **Normalization:** N/A (Δφ in units of 10⁻³ rad)
- **Limitation:** residual angle-unwrapping spike artifacts at a few isolated r values (documented, not hidden); initial orientation is a project assumption
- **Source data:** `SOURCE_DATA/FIGURE_3_FINAL_source_colored.csv`, `FIGURE_3_FINAL_source_EW.csv`, `FIGURE_3_FINAL_scan_table.csv`
- **Script:** `SCRIPTS/figure3_diagnostic_v2.py`

### FIGURE_4_FINAL_Reconstructed_Event_VERTEX_FIXED.png
- **Status:** FINAL_APPROXIMATE
- **Shows:** hits for event 386 (colored benchmark) projected onto the reconstructed (n3, n2) plane, quirk-1/quirk-2 hits distinguished, Δs/Δw annotated
- **Sample used:** event 386 (substituted for the unlocatable "event 12"; closest Δs match to paper's reference, sole Sec IV final-pass event)
- **Exact/approximate/diagnostic:** approximate — Δs=0.009367cm (1.13× paper's 0.0083cm, close); Δw=0.242530cm (3.28× paper's 0.074cm, root-caused to genuine trajectory-level kinematic variation for this specific event, not a detector-modeling bug)
- **Normalization:** N/A (hit coordinates in cm)
- **Limitation:** single-event result; paper does not publish which event/momenta correspond to its own Fig.4
- **Source data:** `SOURCE_DATA/FIGURE_4_FINAL_hits.csv`, `FIGURE_4_FINAL_plane.csv`
- **Script:** `SCRIPTS/replay_figure4_event.py` (replay), `SCRIPTS/plot_figure4.py` (plot)

### FIGURE_5_FINAL_DeltaS_DeltaW_FOUR_COMPONENT.png (+ 5A/5B single panels)
- **Status:** FINAL_APPROXIMATE
- **Shows:** unit-area Δs (left/5A) and Δw (right/5B) shape distributions, 4 components
- **Sample used:** colored N=5; EW N=32; pileup_mu50 N=172 (full Sec IIIC population); converted-γ+pileup_mu50 N=3276 (full μ=50 overlay)
- **Exact/approximate/diagnostic:** "Approximate unit-area Figure 5 shape reproduction; absolute paper normalization unavailable."
- **Normalization:** unit-area (density=True) for all 4 curves
- **Limitation:** pile-up reweighting ambiguity (paper's 1-hit-per-layer denominator population) not applied to any curve
- **Source data:** `SOURCE_DATA/FIGURE_5_FINAL_four_component_source.csv` (also used for 5A/5B)
- **Script:** `SCRIPTS/plot_figure5_main.py` (combined), `SCRIPTS/plot_figure5_single_panels.py` (5A/5B splits)

### FIGURE_5C_FINAL_Absolute_Three_Component_CORRECTED.png
- **Status:** FINAL_APPROXIMATE
- **Shows:** absolute dσ/dlog(Δs) (fb/bin), 3 components (pile-up excluded — no cross-section concept)
- **Sample used:** colored N=5 (419 matched); EW N=32 (511 matched); converted-γ+PU N=3276
- **Exact/approximate/diagnostic:** corrected absolute normalization — colored weight 7.5036×10⁻⁴ fb/event (N=419 denominator, NOT the old wrong N=125/2.5152×10⁻³ value), EW 4.5738×10⁻⁴ fb/event, converted-γ+PU 2.3105×10⁻⁴ fb/event (1% conversion factor applied exactly once)
- **Normalization:** absolute fb/bin (log10-Δs bins)
- **Limitation:** pile-up structurally excluded, no paper-supported cross-section concept for a per-bunch-crossing overlay process
- **Source data:** `SOURCE_DATA/FIGURE_5C_FINAL_absolute_source.csv`
- **Script:** `SCRIPTS/plot_figure5_main.py`

### Figures 6 and 7 — BLOCKED
No image exists for either. See `METADATA/FIGURE_6_STATUS.txt` and
`METADATA/FIGURE_7_STATUS.txt` for the full reasons. Do not present a
Figure 6 or Figure 7 result in the PPT.

## Folder contents
- `PNG/` — every approved final figure, PNG format
- `PDF/` — same figures, vector PDF (where available; Figure 2 has no PDF in the source directory)
- `SOURCE_DATA/` — exact numerical source CSVs/JSON behind every final figure
- `SCRIPTS/` — exact generating script for every final figure (verified reproducible)
- `METADATA/` — provenance, status text files for achieved/blocked figures, SHA-256 hash list
- `ARCHIVE_OBSOLETE/` — copies (not the only copies — originals remain in their source directories) of superseded/obsolete/duplicate figures, with `ARCHIVE_REASONS.csv` explaining each
- `FINAL_FIGURE_MANIFEST.csv` — full classification of every figure found across the entire repository

## Verification performed before finalizing this package
1. Every final PNG opened and visually inspected (titles, axes, units, legends all confirmed correct, no clipping)
2. Figure 5 combined confirmed to show all 4 curves with the correct populations
3. Converted-photon curve confirmed N=3276 (not the conversion-only N=2982)
4. Pile-up curve confirmed N=172 (not the old biased N=59)
5. Confirmed the old wrong weight 2.5152×10⁻³ fb/event does NOT appear in any FINAL file (only in ARCHIVE_OBSOLETE, clearly labeled)
6. Confirmed Figure 4 is the vertex-fixed pipeline result (event 386, current pipeline)
7. Confirmed Figure 3 is only labeled FINAL because it was scientifically achieved this task (not before)
8. SHA-256 computed for every final PNG/PDF — see `METADATA/FINAL_FILES_SHA256.txt`
9. Confirmed no simulation process was running at package-build time
