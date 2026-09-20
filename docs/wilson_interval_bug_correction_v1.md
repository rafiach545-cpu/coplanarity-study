# Wilson-interval bug: audit and correction (v1) — 2026-09-21

Read-only statistical audit, triggered by a user-caught inconsistency: the
reported Wilson 95% CI for k=1, n=9139 did not contain the point estimate.
**No authoritative event CSV was modified or rerun.**

## 1. Exact cause
`05_coplanarity_analysis/build_ppt_statistics.py`'s `wilson(k, n, z)`
function (and an inline, unsaved copy of the identical pattern used ad hoc
in the converted-photon+pile-up overlay task's "Phase 9" cutflow script)
omitted the leading `z` multiplier on the margin term:

```python
# BUGGY
h = np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
# CORRECT
h = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
```

This makes the interval systematically too narrow. For most k, n this
merely understates uncertainty without visibly breaking containment; for
small k (k=1, n=9139) the true margin is large enough relative to the
undersized one that the interval shifts entirely above the point estimate.

Three OTHER Wilson implementations in this repo were independently checked
and are **confirmed correct** (already include the `z` multiplier):
`02_backgrounds/pileup/run_pileup_fake_background.py::wilson_interval`,
`02_backgrounds/pileup/build_pileup_only_statistics.py::wilson_interval`,
`02_backgrounds/photon_conversion/build_converted_photon_only_statistics.py::wilson_interval`.
None of the pile-up-only or converted-photon-only freeze outputs are
affected.

## 2. Old value vs corrected value (k=1, n=9139)

| | Old (buggy) | Corrected |
|---|---|---|
| Point estimate | 0.000109421 | 0.000109421 (unchanged) |
| Wilson 95% | [0.000166, 0.000473] — **does not contain phat** | [0.0000193, 0.000620] — contains phat |
| Wilson 68% | not previously reported | [0.0000418, 0.000286] |
| Clopper-Pearson 95% | [0.0000028, 0.000610] (already correct — scipy.stats.beta was used directly, unaffected) | unchanged |
| Clopper-Pearson 68% | not previously reported | [0.0000191, 0.000360] |

## 3. Which numerator/denominator were used
Confirmed: k=1 (the exact `final_sec_iv_pass` count from
`conversion_with_pileup_mu50_v1.csv`), n=9139 (exact `N_total`). No mixing
with the 0.01 conversion weight occurred in the interval computation
itself — the bug was purely the missing `z` multiplier, not a
numerator/denominator mixup. The Clopper-Pearson interval was already
correct throughout (computed directly via `scipy.stats.beta.ppf`, which
has no such bug surface).

## 4. Terminology verification (as requested)
- Raw final probability: 1/9139 = 0.000109421.
- 1%-conversion-weighted equivalent: (1×0.01)/9139 = 1.0942×10⁻⁶.
- The 0.01 conversion probability is a **physical per-event weight**
  (`weight_pb = PER_EVENT_XSEC_PB × 0.01`), applied multiplicatively to a
  rate/cross-section — confirmed it was **never** treated as a binomial
  success count (`k` or `n`) anywhere in the affected code; the bug was
  isolated to the Wilson margin formula only.
- This result should be described as a **"paper-matched overlay
  implementation with documented simplifications,"** not an exact
  paper-equivalent reproduction.

## 5. Cross-checks performed
- Explicit Wilson formula (manual independent re-derivation): matches
  `wilson_correct()`.
- `scipy.stats.beta` for Clopper-Pearson: matches.
- `statsmodels.stats.proportion.proportion_confint`: **NOT AVAILABLE** in
  this environment (`ModuleNotFoundError`) — not installed, not a source
  of the bug. Cross-checked instead via the independent manual
  re-derivation above, which agrees with `wilson_correct()` to all
  reported digits.

## 6. Regression test
`tests/test_wilson_interval_regression.py` — 5 cases (k=0,n=5000;
k=1,n=9139; k=4,n=2982; k=n=172,172; k=0,n=172), each checked for Wilson
68%/95% and Clopper-Pearson 68%/95% containment. **5/5 pass, exit 0.**

## 7. Files changed
- `05_coplanarity_analysis/build_ppt_statistics.py` — fixed `wilson()`.
- `05_coplanarity_analysis/ppt_statistics_v1/ew_complete_statistics.json` — regenerated.
- `05_coplanarity_analysis/ppt_statistics_v1/colored_complete_statistics.json` — regenerated.
- `05_coplanarity_analysis/converted_photon_with_pileup_v1/phase9_full_cutflow.csv` — corrected Wilson/CP columns.
- `05_coplanarity_analysis/converted_photon_with_pileup_v1/phase9_final_pass_statistics.json` — corrected, with an explicit `correction_note`.
- `docs/converted_photon_pileup_overlay_final_report_v1.md` — corrected §9, terminology added.
- `tests/test_wilson_interval_regression.py` — new regression test.
- `docs/RUN_LOG.md` — new append-only correction entry (old entry left untouched, per project convention).

**No authoritative event CSV** (`conversion_with_pileup_mu50_v1.csv`,
`conversion_scan_results_v3/v4*.csv`, any pile-up sweep CSV) was modified.
**No simulation was rerun.**

## 8. Audit scope confirmation
Every Wilson-interval-bearing file in the repository was located via
`grep -rl "wilson68\|wilson95\|wilson_lo\|wilson_hi"` and individually
checked; the 4 affected outputs listed above are the complete blast
radius. Figure annotations and plot-embedded error bars (pile-up-only
freeze figures) use the confirmed-correct `build_pileup_only_statistics.py`
implementation and required no changes.
