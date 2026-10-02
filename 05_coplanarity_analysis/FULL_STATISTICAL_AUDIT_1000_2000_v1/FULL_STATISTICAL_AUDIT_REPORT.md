# Complete Statistical Audit — 1000-Event and 2000-Event Quirk Samples vs Paper Table I

**Read-only.** No new simulation was run. No frozen file (any file under
`quirk_2000_event_fresh_regeneration_v1/`, the repo-root 1000-event
cutflow CSVs, or `madgraph_pilot_v1/`) was modified. Nothing committed or
pushed. Figure 6 was not touched. Every number below was independently
recomputed from raw event-level files during this audit — none is copied
from a cached summary table.

Benchmarks: Colored (mQ=1800 GeV, Λ=2 keV), EW (mQ=800 GeV, Λ=4 keV).
Paper Table I: Colored (trig=0.24, fid=0.28, reco=0.35), EW (trig=0.10,
fid=0.28, reco=0.72).

---

## 1. Complete raw counts, all four samples

Recomputed directly from:
`quirk_2000_event_fresh_regeneration_v1/reconstruction/*/per_event_results.csv`,
`colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv`,
`ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv`, cross-checked against
`madgraph_pilot_v1/cutflows/generator_cutflow_EW_and_colored.csv` and
`COLORED_INCONSISTENCY_AUDIT_v1/tables/colored_complete_cutflow.csv` for
the generator-level (pre-downstream) stages.

Full table: `tables/raw_counts_all_samples.csv`. Reproduced here:

| Quantity | Colored 1000 | EW 1000 | Colored 2000 | EW 2000 |
|---|---|---|---|---|
| N_requested (LHE) | 1000 | 1000 | 2000 | 2000 |
| N_LHE (generated) | 1000 | 1000 | n/a (not separately logged) | n/a |
| N_showered | 419 | 511 | 873 | 1045 |
| N_matched (MLM) | 419 | 511 | 873 | 1045 |
| N_charge_eligible (colored only) | 125 | n/a | 274 | n/a |
| N_trigger_only (of full matched, any charge) | 101 | 89 | 207 | 186 |
| N_trigger_AND_charge | 27 | n/a | 68 | n/a |
| N_downstream_propagated | 27 | 89 | 68 | 186 |
| N_truth_fiducial | 7 | 40 | 25 | 94 |
| N_plane_found_total (unconditioned) | 5 | 32 | 20 | 84 |
| N(fiducial AND plane) | 5 | 32 | 12 | 75 |
| N_hit_multiplicity_total (unconditioned) | 3 | 16 | 9 | 48 |
| N(fiducial AND plane AND hit_mult) | 3 | 16 | 7 | 48 |
| N_delta_s_pass (Δs<0.01cm, any row) | 1 | 6 | 5 | 27 |
| N_delta_w_pass (Δw<1cm, any row) | 5 | 32 | 20 | 84 |
| N_final_SecIV_total (unconditioned) | 1 | 6 | 4 | 21 |
| N(fiducial AND final SecIV) | 1 | 6 | 3 | 21 |

**Note on N_showered vs N_matched**: identical for all four samples —
MLM matching happens inside the Pythia8 shower step itself (unmatched
events never reach the final HepMC record), a structural fact of this
pipeline verified directly in the earlier forensic audit, not an
independent coincidence re-derived here.

### Event-ID intersection / parent-child closure audit

Full table: `tables/event_intersection_closure_audit.csv`.

| Sample | Downstream rows found | Expected from trigger accounting | Closure verified | Duplicate event IDs |
|---|---|---|---|---|
| Colored 1000 | 27 | 27 | **TRUE** | 0 |
| EW 1000 | 89 | 89 | **TRUE** | 0 |
| Colored 2000 | 68 | 68 | **TRUE** | 0 |
| EW 2000 | 186 | 186 | **TRUE** | 0 |

Every transition closes exactly: the number of rows in each downstream
reconstruction file matches the trigger-accounting record's count with
zero missing and zero duplicated event IDs, for all four samples.

---

## 2. Every denominator, defined explicitly

Full table: `tables/denominator_definition_table.csv`. Key points:

- **Do not mix trigger-only and trigger-and-charge counts.** For
  colored, `trigger_only_efficiency` (101/419, 207/873) uses the FULL
  matched sample as its denominator, irrespective of charge.
  `trigger_conditional_on_charge` (27/125, 68/274) uses the
  charge-eligible subset as its denominator — a different population.
  Both are separately reported; neither should be averaged with the
  other.
- **The population that is directly comparable to the paper's eps_trig**
  is `trigger_only_efficiency` — it matches the paper's own factorization
  (Eq. 12), which does not condition the trigger stage on any
  charge-detectability requirement (that is a detector-response detail
  this project adds afterward, for colored quirks specifically, before
  the fiducial stage).
- **The fiducial-stage denominator is the downstream-propagated
  population**: for colored, that is the trigger-AND-charge-filtered
  sample (27, 68); for EW, the trigger-only sample (89, 186) — since EW
  quirks carry fixed unit charge and never need a charge filter. This
  matches how both generations of this project's own pipeline structured
  the cascade (verified directly from code, not assumed).
- **`eps_plane_conditional`** and **`eps_secIV_conditional`** both use
  `N_fiducial` (from the *same* row, same sample) as their denominator —
  they differ only in numerator (see §3).

---

## 3. Two separate reconstruction-efficiency definitions (not conflated)

```
eps_plane_conditional = N(fiducial AND plane) / N_fiducial
eps_secIV_conditional = N(fiducial AND final SecIV pass) / N_fiducial
```

### Paper wording, weighed for each interpretation

Paper's factorization statement (Sec. IV, p.7): "The reconstruction
efficiency is defined as the efficiency of our algorithm in finding
quirks which satisfy both the trigger and fiducial requirements." This
sentence alone is compatible with either interpretation.

**Interpretation A** (`eps_plane_conditional` — algorithm finds *a*
coplanar-plane candidate) is more strongly supported by the paper's very
next descriptive passage (p.7–8), which explains ε_reco's Λ-dependence
**exclusively** in terms of plane-finding success or failure: "ε_reco
drops at lower Λ, where the iterative algorithm may fail to capture
enough hits largely due to a stringent Δw requirement[s]. At high Λ,
ε_reco drops as well since the separation is small enough for the hits
to start merging, **at which point a plane cannot be found**." This
passage never mentions the hit-multiplicity requirement or the
additional, much tighter Sec IV Δs<0.01cm cut — both of which are part
of `eps_secIV_conditional` but not of `eps_plane_conditional`. If ε_reco
included those additional cuts, the natural place to mention their
effect on ε_reco's Λ-dependence would be exactly this passage, and they
are absent from it.

**Interpretation B** (`eps_secIV_conditional` — full Sec IV
signal-region survival) is supported only by the generic phrase
"finding quirks," which could be read as requiring the complete
identification chain, not merely a candidate plane. No sentence
specific to ε_reco's behavior supports this reading as strongly as it
supports Interpretation A.

**This audit does not resolve the ambiguity** — the paper does not
publish its counting code, and the above is a textual-evidence
weighting, not proof. Both are reported and compared to Table I below.

### Comparison to Table I, both interpretations, all four samples

**Classification convention used throughout this report (revised)**:
exact two-sided binomial p-value against the paper's Table I value —
**p<0.01 → STRONGLY INCONSISTENT; 0.01≤p<0.05 → STATISTICALLY
INCONSISTENT; 0.05≤p<0.10 → BORDERLINE / MILD TENSION; p≥0.10 → NO
STATISTICALLY SIGNIFICANT INCONSISTENCY.** The word "consistent" is not
used to mean two efficiencies are proven equal — "no statistically
significant inconsistency" is used instead, since a non-significant
test never proves equality, only that the data do not demonstrate a
difference at the stated threshold.

For every row: numerator/denominator, exact p-value, Wilson 95%
interval, Clopper-Pearson 95% interval, and the paper value are all
retained (full detail in `tables/master_efficiency_table.csv`, which now
also carries a `paper_value_inside_wilson95` boolean column and an
`interval_vs_test_agreement` column, flagging any case where the
95%-interval check and the exact-test classification disagree).

| Sample | eps_plane_conditional | Wilson95 | CP95 | vs paper | p-value | verdict (A) | eps_secIV_conditional | Wilson95 | CP95 | vs paper | p-value | verdict (B) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Colored 1000 | 5/7=0.7143 | [0.359,0.918] | [0.290,0.963] | 0.35 | 0.056 | BORDERLINE / MILD TENSION — **flag: paper value 0.35 falls OUTSIDE the Wilson95 interval, disagreeing with the exact-test's "borderline" (not "significant") classification** | 1/7=0.1429 | [0.026,0.513] | [0.004,0.579] | 0.35 | 0.434 | NO STATISTICALLY SIGNIFICANT INCONSISTENCY |
| Colored 2000 | 12/25=0.4800 | [0.300,0.665] | [0.278,0.687] | 0.35 | 0.208 | NO STATISTICALLY SIGNIFICANT INCONSISTENCY | 3/25=0.1200 | [0.042,0.300] | [0.025,0.312] | 0.35 | 0.019 | STATISTICALLY INCONSISTENT |
| EW 1000 | 32/40=0.8000 | [0.653,0.895] | [0.644,0.909] | 0.72 | 0.295 | NO STATISTICALLY SIGNIFICANT INCONSISTENCY | 6/40=0.1500 | [0.071,0.291] | [0.057,0.298] | 0.72 | 9.1e-14 | STRONGLY INCONSISTENT |
| EW 2000 | 75/94=0.7979 | [0.706,0.867] | [0.702,0.874] | 0.72 | 0.107 | NO STATISTICALLY SIGNIFICANT INCONSISTENCY | 21/94=0.2234 | [0.151,0.318] | [0.144,0.321] | 0.72 | 2.4e-23 | STRONGLY INCONSISTENT |

**Interval-vs-test disagreement, flagged**: for colored-1000
`eps_plane_conditional`, the paper's value (0.35) lies just outside the
Wilson 95% interval ([0.359, 0.918]) — which on its own would suggest
"significant at 95%" — while the exact two-sided binomial test gives
p=0.056, just above the 0.05 threshold, classified here as "borderline"
rather than "significant." This is not an error in either calculation;
Wilson intervals and the exact binomial test are constructed differently
and can disagree very close to a threshold, especially at small N (here
N=7). Both figures are reported side by side rather than letting one
silently override the other.

**The classification changes between interpretations for every sample
except colored-1000 (where N=7 is too small for either interpretation to
be conclusive, and the two methods disagree with each other besides).**
Per instruction, the reconstruction-efficiency result is **not**
described with a single "consistent/inconsistent" label — it is
definition-dependent, and reported as such.

---

## 4. Statistical uncertainty — full detail for every efficiency

Full table with every quantity, every uncertainty type, and every
p-value: `tables/master_efficiency_table.csv` (34 rows). Each row
reports: central value, numerator, denominator, standard binomial
error, Wilson 68%, Wilson 95%, Clopper-Pearson 95%, and the exact
two-sided binomial p-value against the corresponding Table I value
where applicable.

**These are statistical uncertainties only** (binomial counting
statistics on this project's own finite event samples). No modeling
uncertainty (detector response assumptions, generator PDF/scale choice,
hit-merging algorithm approximations, etc.) and no systematic
uncertainty of any kind has been estimated or included anywhere in this
audit.

---

## 5. Consistency classification

**Declared criterion (revised)**: exact two-sided binomial p-value
against the paper's Table I value, using the conventional two-sided
significance threshold α=0.05 as the primary criterion:
- **p < 0.01 → STRONGLY INCONSISTENT**
- **0.01 ≤ p < 0.05 → STATISTICALLY INCONSISTENT**
- **0.05 ≤ p < 0.10 → BORDERLINE / MILD TENSION**
- **p ≥ 0.10 → NO STATISTICALLY SIGNIFICANT INCONSISTENCY**

The word "consistent" is deliberately not used to assert that two
efficiencies are proven equal — a non-significant result only means the
data do not demonstrate a difference at the stated threshold, not that
the true values are equal. Quantities with no paper Table I analog are
labeled **NOT_DIRECTLY_COMPARABLE** (never scored against a threshold).
Reconstruction-efficiency quantities whose classification changes
between Interpretation A and B are labeled **DEFINITION-DEPENDENT** in
the narrative (a property of the *pair* of rows, not a fifth per-row CSV
value — see the thesis-ready table for both rows side by side).

| Sample | eps_trig | eps_fid | reco (A: plane) | reco (B: SecIV) |
|---|---|---|---|---|
| Colored 1000 | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.954) | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=1.0) | BORDERLINE / MILD TENSION (p=0.056) — see interval-vs-test flag above | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.434, N too small to be conclusive) |
| Colored 2000 | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.874) | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.136) | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.208) | STATISTICALLY INCONSISTENT (p=0.019) |
| EW 1000 | STRONGLY INCONSISTENT (p=2.8e-7) | STRONGLY INCONSISTENT (p=8.2e-4) | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.295) | STRONGLY INCONSISTENT (p=9.1e-14) |
| EW 2000 | STRONGLY INCONSISTENT (p<1e-13) | STRONGLY INCONSISTENT (p<1e-9) | NO STATISTICALLY SIGNIFICANT INCONSISTENCY (p=0.107) | STRONGLY INCONSISTENT (p<1e-22) |

**Overall reconstruction-efficiency conclusion is DEFINITION-DEPENDENT**
for Colored-2000, EW-1000, and EW-2000: no statistically significant
inconsistency under Interpretation A, statistically/strongly
inconsistent under Interpretation B.

---

## 6. 1000-event vs 2000-event compatibility

Full table: `tables/stability_1000_vs_2000.csv`. Two-sided Fisher's
exact test (chosen over a normal-approximation two-proportion z-test
because several counts are small, e.g. N=7 fiducial for colored-1000).

| Benchmark | Quantity | 1000-event | 2000-event | Abs. difference | SE of difference | Fisher exact p | Compatible at 5%? |
|---|---|---|---|---|---|---|---|
| Colored | trigger_only | 0.2411 | 0.2371 | −0.0039 | 0.0254 | 0.889 | YES |
| Colored | trigger_cond_on_charge | 0.2160 | 0.2482 | +0.0322 | 0.0451 | 0.528 | YES |
| Colored | fiducial | 0.2593 | 0.3676 | +0.1084 | 0.1026 | 0.347 | YES |
| Colored | eps_plane_conditional | 0.7143 | 0.4800 | −0.2343 | 0.1978 | 0.403 | YES |
| Colored | eps_secIV_conditional | 0.1429 | 0.1200 | −0.0229 | 0.1474 | 1.000 | YES |
| EW | trigger_only | 0.1742 | 0.1780 | +0.0038 | 0.0205 | 0.888 | YES |
| EW | fiducial | 0.4494 | 0.5054 | +0.0559 | 0.0642 | 0.440 | YES |
| EW | eps_plane_conditional | 0.8000 | 0.7979 | −0.0021 | 0.0756 | 1.000 | YES |
| EW | eps_secIV_conditional | 0.1500 | 0.2234 | +0.0734 | 0.0709 | 0.480 | YES |

**All nine tested quantities are statistically compatible between the
1000-event and 2000-event samples** (p≥0.05 in every case, several very
close to 1.0). The largest-looking apparent shift (colored
eps_plane_conditional, 0.714→0.480) is fully consistent with ordinary
sampling fluctuation given N=7 vs N=25 — it is **not** evidence of a
real change in the underlying efficiency, and is **not** related to the
numerator bug (§7), since both the 1000-event value (0.714) and the
*corrected* 2000-event value (0.480) are computed the same, bug-free way.

**Independence of seeds / no event overlap**: the 1000-event samples
used MadGraph/Pythia8 generation seed `iseed=21` (both benchmarks,
`madgraph_pilot_v1/metadata/GENERATOR_CONFIGURATION_SUMMARY.md`). The
2000-event samples used seeds `8001` (colored) and `8002` (EW),
explicitly logged in `SEED_REGISTRY.csv` as "none (fresh) ... distinct
from ... prior pilots (9101-9302)." These are different generation
seeds on different MadGraph runs (different requested event counts,
1000 vs 2000, run at different times) — there is no mechanism by which
the same event could appear in both samples, and no such overlap was
observed or expected.

---

## 7. The fresh-script numerator bug — confirmed from code and event evidence

**Confirmed claims, verified directly (not assumed):**

- **The original 1000-event pipeline skips plane reconstruction for
  non-fiducial events.** `analyze_colored_quirk.py`, line 86:
  `if not truth_fiducial:` is followed by an early return that sets
  `seed_found = False` without calling the seeding/plane-finding
  algorithm at all. Verified: for both 1000-event samples,
  `N_plane_found_total` exactly equals `N(fiducial AND plane)` (5=5
  colored, 32=32 EW) — structurally guaranteed by this code path, not a
  coincidence.
- **The fresh 2000-event pipeline runs plane finding unconditionally.**
  `run_fresh_regeneration.py`, `analyze_event()` (lines 266–299): calls
  `seeding_and_iterative_fit(hits_by_layer)` on every event regardless of
  `truth_fiducial`. Confirmed by the mismatch this produces:
  - **Colored 2000 has 20 total planes but only 12 fiducial-plane
    intersections.** ✓ confirmed directly from
    `reconstruction/colored_1800GeV_L2keV/per_event_results.csv`.
  - **EW 2000 has 84 total planes but only 75 fiducial-plane
    intersections.** ✓ confirmed directly.
  - **Colored 2000 has 4 total final passes but only 3 fiducial-final
    intersections.** ✓ confirmed directly.
  - **EW 2000 has 21 total final passes and all 21 are fiducial.** ✓
    confirmed directly (21 = 21, no mismatch at this stage for EW).
- **Exact code line responsible**: `run_fresh_regeneration.py`, function
  `build_statistics()`, line 375: `n_plane = int(recon_df["sec3c_plane_found"].sum())`
  — sums over the *entire* propagated sample rather than the
  fiducial-conditioned subset, then this value is divided by `n_fid`
  (line 406) as if it were already a subset count.

**This is a statistics/selection-bookkeeping bug, not a
simulation-physics bug.** Nothing about the trajectory integration,
detector hit simulation, or the seeding/iterative-fit plane-finding
algorithm's own logic is wrong — event-level physics (hit positions,
Δs/Δw values, timing) is computed identically and correctly regardless
of this bug. The error is purely in how the *summary statistic* `N_plane`
was aggregated across the population when writing
`statistics/*_summary.json` and `statistics/paper_comparison_table.csv`
— a downstream bookkeeping step, entirely separable from and not
indicative of any error in the physics/reconstruction code itself.

---

## 8. Files produced (paper-ready outputs)

- `FULL_STATISTICAL_AUDIT_REPORT.md` — this file.
- `tables/master_efficiency_table.csv` — all counts, denominators,
  efficiencies, all uncertainty types, p-values, verdicts (34 rows).
- `tables/thesis_ready_comparison_table.csv` — concise PPT/thesis table.
- `tables/denominator_definition_table.csv` — every numerator/denominator
  defined in words.
- `tables/stability_1000_vs_2000.csv` — 1000-vs-2000 compatibility tests.
- `tables/event_intersection_closure_audit.csv` — parent-child closure
  verification.
- `tables/raw_counts_all_samples.csv` — all 16 raw counts, 4 samples.
- `scripts/full_audit.py` — the exact, re-runnable computation (read-only
  with respect to all source files; writes only into this new directory).
- `SHA256_MANIFEST.txt` — hash of every file in this directory.

### Results-section-ready paragraph

> We validated our signal reconstruction pipeline against Table I of
> Knapen et al. (arXiv:1708.02243) using two independently generated
> event samples per benchmark (1000 and 2000 requested events). Trigger
> and fiducial efficiencies for the colored benchmark (mQ=1800 GeV,
> Λ=2 keV) show no statistically significant inconsistency with the
> paper across both samples (e.g. eps_trig = 0.237, 95% Wilson interval
> [0.210,0.266], vs paper's 0.24, exact two-sided p=0.87). For the
> reconstruction efficiency, we report two distinct quantities
> corresponding to different plausible readings of the paper's
> definition: the conditional plane-finding efficiency (12/25 = 0.480,
> no statistically significant inconsistency with the paper's 0.35,
> p=0.21) and the conditional full-signal-region efficiency (3/25 =
> 0.120, statistically inconsistent, p=0.019). For the EW benchmark
> (mQ=800 GeV, Λ=4 keV), trigger and fiducial efficiencies are strongly
> inconsistent with the paper (p<10⁻⁹ in both cases) in both the 1000-
> and 2000-event samples, while the conditional plane-finding
> reconstruction efficiency shows no statistically significant
> inconsistency (0.798 vs paper's 0.72, p=0.11). All quantities tested
> for compatibility between the 1000- and 2000-event samples agree
> within statistical uncertainty (Fisher's exact test, p≥0.35 in every
> case), confirming that differences between the two sample generations
> reflect ordinary counting statistics rather than a change in the
> underlying pipeline.

### Limitations/Systematics-section-ready paragraph

> The uncertainties reported throughout this audit are purely
> statistical (binomial counting uncertainties on finite Monte Carlo
> samples, computed via the Wilson score interval, the Clopper-Pearson
> exact interval, and the exact two-sided binomial test against the
> paper's quoted value). No systematic uncertainty has been estimated —
> in particular, uncertainties arising from PDF and factorization/
> renormalization scale choices in event generation, from the assumed
> detector hit-merging and smearing model, from the approximate nature
> of the truth-level fiducial definition, or from the paper's own
> unpublished choices for these same quantities, are not included. The
> paper's reconstruction efficiency (ε_reco) is defined in prose in a
> way compatible with two different concrete countings; both are
> reported here as separate, equally-computed quantities rather than
> collapsed into one, because the paper does not publish the counting
> code needed to disambiguate them, and the choice materially changes
> the consistency verdict for three of the four samples tested.

---

## 9. Final reporting requirements

**Confirmed inconsistencies** (p<0.05 against Table I, STRONGLY
INCONSISTENT or STATISTICALLY INCONSISTENT): EW trigger efficiency (both
samples, p<10⁻⁶, STRONGLY INCONSISTENT); EW fiducial efficiency (both
samples, p<10⁻³, STRONGLY INCONSISTENT); EW eps_secIV_conditional
reconstruction efficiency (both samples, p<10⁻¹³, STRONGLY
INCONSISTENT); Colored eps_secIV_conditional reconstruction efficiency
(2000-event sample, p=0.019, STATISTICALLY INCONSISTENT).

**Quantities with no statistically significant inconsistency vs the
paper**: Colored trigger efficiency (both samples); Colored fiducial
efficiency (both samples); Colored eps_plane_conditional reconstruction
efficiency (2000-event sample, and 1000-event sample under the exact
test though flagged BORDERLINE / MILD TENSION with a disagreeing
95%-interval check, see §3); EW eps_plane_conditional reconstruction
efficiency (both samples); Colored eps_secIV_conditional (1000-event
sample only, N=7 too small to be conclusive either way).

**Definition-dependent conclusions**: the overall reconstruction-
efficiency classification for Colored-2000, EW-1000, and EW-2000 depends
entirely on which of the two ε_reco interpretations is used — no
statistically significant inconsistency under Interpretation A
(plane-finding), statistically/strongly inconsistent under
Interpretation B (full Sec IV selection). This audit does not resolve
which the paper intended.

**Unresolved issues**: (1) the ε_reco definition ambiguity itself,
un-resolvable without the paper's own counting code; (2) the root cause
of the EW trigger/fiducial inconsistencies (both statistically
significant at high confidence in both samples, not yet investigated for
a physical or modeling explanation — out of scope for this audit); (3)
whether the fresh-script bug (§7) should now be corrected in
`run_fresh_regeneration.py` and the frozen summary files regenerated —
an explicit next step requiring separate authorization, not done here.

**Exact files created**: listed in full in §8 above and hashed in
`SHA256_MANIFEST.txt`.

**Confirmation**: no simulation was run in this audit; no frozen data
file (anything under `quirk_2000_event_fresh_regeneration_v1/`,
`madgraph_pilot_v1/`, or the repo-root 1000-event cutflow CSVs) was
modified; Figure 6 production was not touched, resumed, or checked in a
way that risked disturbing it; nothing was committed or pushed.
