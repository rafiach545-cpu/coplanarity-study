# Figure 5 final freeze package (v1) — 2026-09-21

Two separate, authoritative products. No simulation was run to produce
this package — all populations were already-completed authoritative
results, verified directly before plotting.

## Product A: Four-component unit-area shape reproduction
`Figure_5_four_component_v2_AUTHORITATIVE.{png,pdf}` +
`Figure_5_four_component_source_v2.csv` (bin-level raw counts + density
for every curve, both panels).

**Populations, verified directly before use (not assumed):**
- Colored: `colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv`, `truth_fiducial & ds.notna()`, **N=5**.
- EW: `ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv`, same selection, **N=32**.
- Pile-up: `sweep_mu_2026-09-16/pileup_mu50_n5000_sec3c_fullcutflow_v1.csv`, `sec3c_plane_found`, **N=172** (asserted N_total=5000, N_plane=172 — this is the FULL authoritative population, not the old biased ≥4-layer-only N=59 subsample used in the 2026-09-17 figure).
- Converted-γ+pile-up: `conversion_with_pileup_mu50_v1.csv`, `sec3c_plane_found`, **N=3276** (asserted N_total=9139, N_plane=3276 — this is the REAL μ=50 overlay population, not the conversion-only N=2982 used in the 2026-09-17 figure).

**Label:** *"Approximate unit-area Figure 5 shape reproduction; absolute
paper normalization unavailable."*

**This supersedes** `fig5_reproduction_2026-09-17/fig5_left_panel_ds.png`
(and its sibling files) — that version used the pile-up ≥4-layer-biased
N=59 subsample and had NO converted-photon curve at all (recorded as
`null` in its own source JSON, since the overlay didn't exist yet at that
time). The old files are **not deleted**, marked OBSOLETE below.

## Product B: Corrected three-component absolute normalization
`Figure_5_absolute_three_component_v2_CORRECTED.{png,pdf}` +
`Figure_5_absolute_three_component_source_v2.csv`.

| Component | Weight (fb/event) | Denominator | Selected-plane integral (fb) |
|---|---|---|---|
| Colored | 7.5036×10⁻⁴ | 419 matched (full sample) | 3.7518×10⁻³ |
| EW | 4.5738×10⁻⁴ | 511 matched (full sample) | 1.4636×10⁻² |
| Converted-γ+PU μ=50 | 2.3105×10⁻⁴ (1% conversion factor applied exactly once) | 9139 | 0.756924 |

**Pile-up excluded** — no paper-supported fb/bin normalization exists for
a per-bunch-crossing overlay process (no cross-section concept).

**This supersedes** `fig5_absnorm_audit_v1/figure5_left_panel_ABSOLUTE_3curves.png`
(no `_v2_CORRECTED` suffix) — that version's colored curve used N=125
(a charge-filtered subset) as the cross-section denominator instead of
N=419 (the full matched sample), making it **3.352× too high**. Not
deleted, marked OBSOLETE below.

## Selections and normalization, explained
- Both products use the **Sec IIIC selected-plane** population (Δw<1cm,
  smallest Δs), i.e. the paper's own Fig.5 population ("before the final
  cut on those variables are imposed").
- Δs/Δw are in **cm** throughout, log-x bins (20 log-spaced bins per
  panel, graphically estimated from the paper's own plot — the paper
  does not print exact bin edges anywhere in the text).
- Product A: unit-area (density=True) normalization for all 4 curves.
- Product B: absolute fb/bin = (Σ per-event weight in bin) / (bin width
  in log10 units), using each component's own physical per-event weight.
- Pile-up reweighting ambiguity (paper's "1-hit-per-layer" denominator
  population) remains unresolved — **not applied** to either product;
  both show the raw (unweighted-by-multiplicity) Sec IIIC population.

## Authoritative vs. obsolete files (this figure only)

| File | Status | Reason | Replacement |
|---|---|---|---|
| `figure5_final_freeze_v1/Figure_5_four_component_v2_AUTHORITATIVE.*` | AUTHORITATIVE | correct populations (pileup N=172, converted-γ+PU N=3276) | — |
| `fig5_reproduction_2026-09-17/fig5_left_panel_ds.png` (+siblings) | OBSOLETE | pileup N=59 biased subsample; no converted-photon curve at all | `Figure_5_four_component_v2_AUTHORITATIVE.png` |
| `figure5_final_freeze_v1/Figure_5_absolute_three_component_v2_CORRECTED.*` | AUTHORITATIVE | corrected colored weight (N=419 denominator) | — |
| `fig5_absnorm_audit_v1/figure5_left_panel_ABSOLUTE_3curves.png` (no suffix) | OBSOLETE | colored weight 3.352× too high (wrong N=125 denominator) | `Figure_5_absolute_three_component_v2_CORRECTED.png` |

## Regeneration
Both products are reproducible from already-existing authoritative CSVs
with no new simulation — the exact commands used are recorded in this
session's RUN_LOG (2026-09-21 entries).

## SHA-256 manifest
See `SHA256_MANIFEST.json`.
