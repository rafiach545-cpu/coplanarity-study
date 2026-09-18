# Pile-up-only final statistics freeze (v1) — 2026-09-18

Authoritative, independently-verified pile-up-only statistics package built
from the already-completed μ=0,5,10,20,50 sweeps (n=5000 each). No new
simulation was run to produce this package; one tiny deterministic 1-event
replay was used solely to recover a stored-field gap (see §14).

All numbers below are regenerated directly from source CSVs by
`02_backgrounds/pileup/build_pileup_only_statistics.py` (exit code 0, zero
integrity issues found). Full machine-readable tables/figures are in
`05_coplanarity_analysis/pileup_only_statistics_v1/`.

## 1. References reread
- arXiv:1708.02243v2 (paper.txt): Sec IIIC (lines 480–657), Sec IIID (658–702),
  Fig.5 caption (707–737), Sec IV (738–809).
- arXiv:1612.00850 (ref34.txt): pile-up/detector simplified-simulation sections
  (previously reread in this session; re-consulted for Appendix A framing,
  no new extraction performed this turn since no new claim about ref[34]'s
  numerics was needed).
- ATL-PHYS-PUB-2015-051: tracking-efficiency definition (Eq.1/2, primary-particle
  definition, Loose/Tight selections) — re-consulted via `tracking_efficiency.py`'s
  own docstrings/digitized curve, consistent with earlier direct reads this session.

## 2. Exact event definition
One "analysed bunch crossing" = one call to
`sample_pileup_hits_suppressed(pool_index, mu, rng_pileup, rng_suppression, ...)`
under `SeedSequence([90210777, int(mu), event_i])`, `event_i ∈ [0,5000)`. Each
bunch crossing draws `Poisson(mu)` minimum-bias interactions with replacement
from the 20,000-event ancestry pool, propagates every resulting truth particle,
applies ancestry-aware tracking-efficiency suppression, then runs the
unchanged Sec IIIC/Sec IV reconstruction chain. Full per-quantity definition
table (paper source / code field / code function / denominator / direct-vs-derived
/ assumptions) is in-line in `build_pileup_only_statistics.py`'s docstrings and
summarized in §7/§9 below; a standalone table was not separately materialized
as a file, since every definition it would contain is already attached to
each table's own field descriptions (avoiding a duplicate, driftable copy).

## 3. Input files and hashes
See `pileup_only_statistics_v1/table1_input_inventory.csv` (10 rows: 2 file
families × 5 μ). All 10 files: exactly 5000 rows, 5000 unique `event_i`, 0
duplicates, 0 missing IDs, `.DONE` marker present. **Known metadata caveat**:
the 5 *original-sweep* provenance sidecars record `pool_sha256=e03cf9a6...`
(the FINAL pool's hash — a previously-documented bug, RUN_LOG 2026-09-17),
while the actual sampling used the ANCESTRY pool
(`a8f9149c07b9967332cfd7eba49960dd137bbc927c4be7309b92df6979b172ad`) — the 5
*new fullcutflow* provenance sidecars record this correct hash. mu=0's
fullcutflow provenance sidecar is **absent** (the resumable driver skips
`build_provenance()` entirely when a `.DONE` marker already exists — a minor
gap, data itself unaffected and independently verified below).

## 4. Detector/suppression model
`atlas_geometry.py` Sec-IIIA barrel 8-layer model (no ref[34] endcap/TRT/ECAL/
Bethe-Bloch), Loose tracking-efficiency selection, ancestry-aware Bernoulli
per-primary-track suppression (`track_suppression.py`) — confirmed by direct
code inspection this turn: one independent Bernoulli draw per ref[33]-primary
truth particle, all-or-none correlated hit retention, secondaries/ambiguous
particles never drawn on, suppression RNG stream independent of the pile-up/
vertex stream (separate `SeedSequence` child via `.spawn(2)`).

## 5–13. Statistics
Full numeric content in `pileup_only_statistics_v1/table{2,3,4,5,6,7}*.csv`.
Headline cross-mu numbers (from `table9_master_cross_mu.csv`):

| mu | Poisson mean | N_raw_cand | N_plane | N_>=4/8 | N_8/8 | N_mult | N_final |
|---|---|---|---|---|---|---|---|
| 0 | 0.0000 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 4.9674 | 3 | 3 | 2 | 1 | 0 | 0 |
| 10 | 10.0530 | 6 | 6 | 1 | 0 | 0 | 0 |
| 20 | 20.0428 | 22 | 22 | 5 | 0 | 0 | 0 |
| 50 | 49.9572 | 172 | 172 | 59 | 0 | 0 | 0 |

Poisson means/variances at every mu are consistent with the expected
`Poisson(mu)` mean=variance=mu within finite-sample fluctuation (e.g. mu=50:
mean=49.957, variance=49.722; mu=10: mean=10.053, variance=9.774).

## 14. Rare-event evidence
The single `has_8_of_8_plane=True` event in the entire 25,000-crossing sweep
(mu=5, event_i=2006) was recovered via a **tiny deterministic 1-event
replay** (justified: the paper's exact per-layer hit-count breakdown for this
candidate was never persisted to any CSV, only its aggregate `n_layers`/
`ds`/`dw` were). Result (`table10_rare_event_evidence.csv`), bit-identical to
the prior independent audit reproduction:
`per_layer_hit_counts={8:2,7:2,6:1,5:1,4:1,3:1,2:1,1:1}`, `delta_s=0.03691`,
`delta_w=0.57769`, `multiplicity_pass=False`, **failure reason: only 2/8
layers have ≥2 hits (need ≥7)**.

## 15. Statistical intervals/upper limits
Every zero-count row in `table5_cutflow.csv`/`table9_master_cross_mu.csv`
carries Wilson 68%/95%, Clopper-Pearson 95%, and the naive 3/N rule. Example
(final Sec IV, n=5000, k=0 at every mu): Wilson 95% UL≈0.000768,
Clopper-Pearson 95% UL≈0.000738, 3/N=0.0006.

## 16. Paper comparison
`table8_paper_comparison.csv`. Key correction from prior turns: the paper's
quoted ~10⁻³ / ~6×10⁻⁵ values correspond to the ≥4/8 and 8/8 *raw best-candidate
coverage* diagnostics (rows A/B; our closest matches: 59/5000=0.0118 and
0/5000=0.0000 at mu=50 for A/B respectively, comparability **PARTIAL** —
different suppression model/pool from the paper), **not** the final Sec IV
rate (row E, comparability **NO** — must never be compared directly to those
two numbers, since they are earlier-stage coverage diagnostics).

## 17. Reweighting ambiguity
`w_mult_reassessment.json`: `w_mult = N_hit_mult_pass/N_sec3c_plane_found =
0/172 = 0.0` (point estimate), **Wilson 95% CL upper bound ≈0.0218**
(Clopper-Pearson consistent, 3/N≈0.0174). The denominator population match to
the paper's "events allowed to have 1-hit per layer" phrase is an
**UNRESOLVED / ASSUMPTION** — the paper text does not disambiguate whether
this means our Δw<1cm-filtered Sec IIIC winner population or a looser,
non-Δw-filtered population. **The zero point estimate must not be treated as
an exact physical weight** — any Fig.5 pile-up reweighting built on this
factor must carry the upper-bound uncertainty explicitly.

## 18. Limitations and assumptions
- Pool-reuse statistics (unique pool events touched, reuse histogram, maximum
  reuse) are **NOT AVAILABLE FROM STORED FIELDS** — `sampled_pool_event_ids`
  is computed in-memory by `sample_pileup_hits_suppressed` but never persisted
  by either CSV family. Recovering it for all 25,000 crossings would require
  a further, non-trivial analysis-only rerun (not "tiny") — not performed here.
- Per-class hit-removal breakdown (`n_hits_removed`, `n_hits_kept_primary_failed`,
  etc.), postmerge hit counts, and timing-rejected hit counts are similarly
  **NOT AVAILABLE FROM STORED FIELDS**.
- The full raw-candidate layer-coverage histogram (1/8 through 7/8, across
  *all* candidates, not just the best one) is **NOT AVAILABLE** — only the
  best raw candidate's coverage (`has_4_of_8_plane`/`has_8_of_8_plane`) and
  the Sec IIIC winner's `sec3c_n_layers` were persisted.
- 20,000-event pool (with replacement) is a documented project decision, not
  a paper requirement (paper uses 125,000 events) — results have reduced
  statistical independence relative to the paper's own sample.
- Transition tables (`table12_transitions_bookkeeping_only.csv`) are
  explicitly labeled **BOOKKEEPING COMPARISON ONLY — NOT A PHYSICAL
  EVENT-BY-EVENT TRANSITION**, since each mu uses a distinct
  `SeedSequence([seed, mu, event_i])` stream; the same `event_i` at different
  mu is not the same physical draw.

## 19. Authoritative tables and plots
All under `05_coplanarity_analysis/pileup_only_statistics_v1/`: 10 tables
(`table1`–`table10`, plus `table12` transitions and the master
`pileup_only_complete_statistics_v1.{csv,md}`), 12 figures (`fig1`–`fig12`),
5 per-layer raw CSVs, `w_mult_reassessment.json`, `integrity_check_report.json`.
Regeneration script: `02_backgrounds/pileup/build_pileup_only_statistics.py`
(single committed script, exit code 0 on this run).

## 20. Exact status of pile-up-only reproduction
Signal-region-adjacent diagnostics (≥4/8, 8/8 coverage) are approximately
comparable to the paper's own quoted rates, with documented model differences.
The Sec IIIC selected-plane population and its Δs/Δw shapes are directly
computed, not inferred. The pile-up reweighting factor for Fig.5 is
correctly *formulated* per the paper's description but has an unresolved
denominator-population ambiguity and a statistically-limited (not proven
exactly zero) point estimate.

**The pile-up-only study is frozen as an authoritative project result with
documented limitations. Zero final Sec. IV events were observed in each
5000-crossing sample; this is not a claim that the underlying probability is
exactly zero.**
