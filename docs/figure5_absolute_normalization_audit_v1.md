# Figure 5 absolute-normalization audit (v1) — 2026-09-21

Read-only. No detector simulation launched, no events regenerated.

## Fig. 5 rereading (page 7, re-confirmed)
Left panel: `dσ/dlogΔs (fb/bin)` — absolute cross-section. Right panel:
`(1/σ)dσ/dlogΔw` — unit-normalized. Population: Sec IIIC plane-found,
before the final Δs/Δw cuts. Pile-up curve reweighted per the verbatim
text: *"the pileup backgrounds are derived by taking the distribution
from events that are allowed to have 1-hit per layer, weighted by the
overall efficiency of passing the more stringent requirement in point 2
above."*

## 1. Bin edges (graphical estimate, not exact)
`extraction_metadata.json`. The paper gives no numeric bin count/edges
anywhere in the text. Visual step-counting on the Pileup curve (clearest,
most bins visible) is consistent with ~20 log-spaced bins across each
panel's full 2-decade x-axis range — matching what this project already
used. Not pixel-calibrated to sub-bin precision (judged unnecessary: this
audit concerns normalization, not bin placement).

## 2–6. Cross-sections and weights — MAJOR FINDING

**The colored-quirk cross-section was never actually absent — it exists
in the original MadGraph banner file and was simply never read by any
analysis script.** Recovered this task:

| Benchmark | Total σ (pb) | **Matched σ (pb)** | Source |
|---|---|---|---|
| EW (DY, 800GeV/4keV) | 0.00045738380829 | **0.000233723127** | `/home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01/run_01_tag_1_banner.txt`, sha256=`0589530808b3d0710557f7a365366cfe54c5ff3473d376f61de4a17f64c136af` |
| Colored (QCD, 1800GeV/2keV) | 0.00075035994535 | **0.00031440081900** | `/home/rafia/hep_tools/quirk_signal_1800gev_2kev/Events/run_01/run_01_tag_1_banner.txt`, sha256=`d02fc202d118c14bf560d0f617e68c7ea1a043132126d4ab6d6f1fa5e525f144` |

**Phase 4 answer**: the project's existing 0.0002337pb for EW is confirmed
the **matched** (post-MLM) cross-section, matching the banner's
`0.000233723127` to 4 significant figures — appropriate for Fig.5
normalization (matches the population Fig.5 draws from: matched events,
further reduced by trigger/fiducial/reconstruction, exactly as our own
weighted-histogram procedure does).

Both benchmarks: `nevents=1000` requested (pre-matching), MLM matching
(`ickkw=1`, `xqcut=30GeV`). N_matched (post-shower, exactly-2-quirks):
colored=125, EW=511 (both independently re-verified this session).

Per-event weight (fb) = matched_σ_pb × 1000 / N_matched:
- Colored: **2.515207×10⁻³ fb/event**
- EW: **4.573838×10⁻⁴ fb/event**

**Converted-γ (+pile-up μ=50)**: fiducial σ (post-shower MET/pT_γ cuts,
9139/10000) × 1% conversion probability, already established and
unchanged: per-event weight = **2.310512×10⁻⁴ fb/event**, constant,
already includes the 1% factor, applied to N_total=9139 (N_plane=3276
after Sec IIIC selection — this is the real converted-γ+pile-up overlay
result, not the conversion-only diagnostic).

**Pile-up**: no natural cross-section concept exists for a per-bunch-
crossing overlay process (it is not a physical scattering process with a
production rate) — the paper supplies no luminosity/rate conversion for
this curve anywhere in the text I reread. **This is a structural/
conceptual blocker, not a missing-data gap.**

## 7. Pile-up reweighting denominator — still unresolved (both interpretations preserved)
`phase7_pileup_reweighting_ambiguity.json`. Interpretation A (project's
existing assumption): denominator = Sec IIIC Event-Selection winner
population → w_mult = 0/172 (μ=50 control sample), Wilson 95% UL≈0.0218.
Interpretation B: a looser "any candidate, no Δw cut" population, not
distinguishable from the paper text and not available in any stored
dataset. **Not silently chosen** — both stated.

## 8. Absolute-normalization readiness table
`absolute_normalization_readiness_table.csv`:

| Component | Shape | σ available | Weight verified | Reweighting | Fig.5-ready |
|---|---|---|---|---|---|
| Colored Quirk | YES (N=5) | **YES (recovered)** | YES | N/A | **YES** (very sparse) |
| EW Quirk | YES (N=32) | YES (confirmed) | YES | N/A | **YES** (sparse) |
| Converted-γ+PU μ=50 | YES (N=3276) | YES | YES | N/A | **YES** |
| Pile-up | YES (N=172) | **NO** | N/A | AMBIGUOUS | **NO — structurally blocked** |

## 9–10. Generated output
Since 3 of 4 components are fully supported but Pile-up is not, per
instruction: **did not invent** a pile-up cross-section, **preserved**
the existing unit-area 4-curve Fig.5, and generated a **partial absolute
Fig.5 with the 3 supported curves** (`figure5_left_panel_ABSOLUTE_3curves.png`,
source data `figure5_left_panel_ABSOLUTE_source.csv`). Pile-up is
explicitly excluded and labeled, not silently dropped.

**Exact missing input for a complete absolute pile-up curve**: a defined
mapping from "pile-up interactions per bunch crossing" to an equivalent
differential cross-section in fb — e.g. via an assumed total inelastic pp
cross-section and a luminosity/bunch-crossing-rate convention, which the
paper does not provide. Obtaining it would require either finding this
convention in a cited reference not yet reread for this purpose, or an
explicit user-supplied assumption (which would then need to be labeled
DOCUMENTED PROJECT ASSUMPTION, not extracted from the paper).

## Files and hashes
All new files under `05_coplanarity_analysis/fig5_absnorm_audit_v1/`:
`page7_fullpage_400dpi.png`, `fig5_left_panel_crop.png`,
`fig5_right_panel_crop.png`, `extraction_metadata.json`,
`xsec_and_weights_summary.json`, `absolute_normalization_readiness_table.csv`,
`phase7_pileup_reweighting_ambiguity.json`,
`figure5_left_panel_ABSOLUTE_3curves.png`,
`figure5_left_panel_ABSOLUTE_source.csv`. No existing file overwritten.

## Tests
`tests/test_wilson_interval_regression.py` — exit 0 (rerun, unaffected by
this task, confirms no regression).

## Confirmation
No simulation was launched at any point in this task (only PDF rendering,
banner-file inspection, and histogram computation from already-existing
CSVs). No process remains active.
