# Figure Captions and Metadata (Phase 5)

## FIGURE_A_fig2_reproduction
**Caption**: Angular momentum L and quirk separation d vs CM radial
distance, representative colored-benchmark event (1800 GeV, Λ=2 keV),
B=2T. Representative approximate reproduction of paper Fig. 2 — the
paper does not publish its exact event initial conditions, so this uses
this project's own representative event, not a bit-identical
reconstruction of the paper's specific plotted event.
**Source**: reused, unmodified, previously-verified
`FIGURE_2_FINAL_source.csv` (no new trajectory generated this phase).

## FIGURE_B_fig3_reproduction
**Caption**: Δφ (plane rotation) vs CM radial distance, two benchmarks:
Colored (1800 GeV, Λ=2 keV) and EW (800 GeV, **Λ=2 keV** — the paper's
own Fig. 3 diagnostic benchmark, confirmed directly from paper text this
session, distinct from the Λ=4 keV Table I benchmark used elsewhere).
Representative approximate reproduction — paper's exact event initial
conditions are not published.
**Source**: reused, unmodified, previously-verified
`FIGURE_3_FINAL_source_colored.csv` / `FIGURE_3_FINAL_source_EW.csv`.
Some visible spikes in the underlying diagnostic data have been
independently classified in prior work
(`FIGURE_3_SPIKE_DIAGNOSTICS.csv`) — **not all spikes are artifacts**;
this classification is preserved, not overwritten by this phase.

## FIGURE_C_fig4_reproduction
**Caption**: Representative reconstructed hit-plane, Colored (left) and
EW (right) benchmarks, each drawn from the CORRECTED fiducial∩plane-
found selection (Colored: 1 of 12; EW: 1 of 75 — not the stale 20/25 or
84/94 populations).
- **Colored panel**: reused, unmodified, previously-verified
  `FIGURE_4_FINAL_hits.csv` (event from the original verified Figure 4
  package).
- **EW panel**: `event_idx=182` (from the fresh 2000-event EW sample's
  corrected fiducial∩plane-found selection of 75), seed
  `2626882725`, replayed once this session from stored truth momenta
  (not new event generation). Δs = 0.0077850 cm, Δw = 0.0808773 cm,
  16 post-merge hits (8 layers × 2 quirks, full coverage) — replay
  reproduces the stored per-event Δs/Δw to >10 significant figures,
  confirming reproducibility.
- Event ID / Δs / Δw / hit multiplicity are recorded here in metadata,
  not embedded in the figure title, per instruction.

## FIGURE_D_delta_s_delta_w_corrected
**Caption**: Δs and Δw distributions for all events in the CORRECTED
fiducial∩plane-found selection (Colored N=12, EW N=75 — the bug-fixed
intersection counts established earlier in this audit, not the stale
20/25 or 84/94 values). Dashed lines mark the Sec. IV signal-region cuts
(Δs<0.01 cm, Δw<1 cm). This is signal only (fresh 2000-event colored/EW
samples) — no converted-photon background or pile-up overlay is included
in this specific figure; those are separate, previously-frozen figures
not regenerated in this phase.
**Source**: `FIGURE_D_delta_s_delta_w_corrected_source.csv`, drawn
directly from `quirk_2000_event_fresh_regeneration_v1/reconstruction/*/per_event_results.csv`
(already-stored data, no replay needed for this figure).

## FIGURE_E_efficiency_comparison
**Caption**: Project (fresh 2000-event sample) vs paper Table I
efficiencies, both benchmarks, with Wilson 95% error bars. Plane-finding
efficiency (ε_reco, Interpretation A) and full Sec. IV pass rate
(Interpretation B) are shown as separate bars — not conflated.
**Source**: `FIGURE_E_efficiency_comparison_source.csv`, drawn directly
from `PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv`.

## FIGURE_F_cutflow_colored_EW
**Caption**: Fresh 2000-event cutflow, Colored and EW, corrected
intersection counts at every stage. Counts agree exactly with the master
table (Phase 4).
**Source**: `FIGURE_F_cutflow_source.csv`.

## Verification note
No 20/25, 84/94, or 4/25 stale conditional values appear anywhere in
this figure set — checked directly against the corrected 12/25 (Colored)
and 75/94 (EW) values throughout Phase 4/5 (see Phase 7 validation).
