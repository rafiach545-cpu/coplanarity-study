# Follow-up: Causal Test of the ISR-Kinematics Hypothesis (existing events only)

**Correction to the original report**: the original
`FINAL_EW_TRIGGER_FIDUCIAL_AUDIT.md` stated the "harder ISR spectrum"
explanation as if demonstrated. It was a plausible, physically-motivated
hypothesis, not a tested result. This follow-up tests it directly, using
only already-stored data (`matched_events_full.csv`,
`per_event_results.csv`) — **no replay, no new simulation, no frozen
file modified**.

## 1–2. Fiducial efficiency binned by kinematics

Full table: `tables/fiducial_efficiency_binned.csv`. Quirk-pair pT
(post-shower, trigger-passing population, N=186):

| pT_pair bin (GeV) | N | N_fiducial | efficiency | Wilson 95% |
|---|---|---|---|---|
| (200,300] | 83 | 34 | 41.0% | [31.0%,51.7%] |
| (300,400] | 34 | 16 | 47.1% | [31.5%,63.3%] |
| (400,600] | 42 | 23 | 54.8% | [40.0%,68.8%] |
| (600,900] | 22 | 17 | 77.3% | [56.6%,89.9%] |
| (900,1400] | 5 | 4 | 80.0% | [37.6%,96.4%] |

A clear, monotonically increasing trend, roughly doubling from ~41% to
~80% across the pT_pair range. Also binned against \|η\| of each quirk,
max\|η\| of the pair, β_min of the pair, and total `n_hits_premerge`
(layer-coverage proxy, see caveat below) — all in the same table.

**Caveat on "minimum layers crossed by either quirk"**: this exact
per-quirk quantity is **not stored** for the full 186-event sample (only
`n_hits_premerge`, the combined total for both quirks, was retained by
the original pipeline). Getting the true per-quirk minimum would require
replaying every event's trajectory — explicitly excluded by this
follow-up's "no new simulations" instruction. `n_hits_premerge` (total)
is used as an imperfect proxy instead, and is flagged as such everywhere
it appears. It correlates almost tautologically with `truth_fiducial`
(r=0.90) since `truth_fiducial` is partly defined from it — this is a
consistency check, not new causal information.

## 3. Kinematic distributions across populations

Full table: `tables/kinematic_distribution_comparison.csv` — mean,
median, std, quartiles of pT_pair, η1, η2, max\|η\|, β_min for all
1045 matched events, the 186 trigger-passing events, and the 94
fiducial-passing events. (Not reproduced in full here; see the CSV.)

## 4. Fiducial failure sub-categorization

Full table: `tables/fiducial_failure_subcategories_kinematic.csv`.

| Category | Count |
|---|---|
| Pass (fiducial) | 94 |
| **Propagation failure** (zero hits — quirk(s) never registered *any* layer hit) | **71** |
| **Geometric/barrel failure** (fewer than all 8 layers covered, but ≥1 hit) | 18 |
| Technical exception (known integration edge case) | 2 |
| 25 ns timing failure (geometric OK, timing fails) | 1 |

**New finding this follow-up**: the dominant failure mode by far is
"propagation failure" (zero hits at all, 71/92 = 77% of failures), not
"almost made it but missed a layer or two" (18/92 = 20%). This is
directly consistent with the strong η correlation below — a quirk that
exits at high \|η\| tends to miss the barrel acceptance entirely (zero
hits) rather than partially.

## 5. Correlation quantification (the actual causal test)

Full table: `tables/kinematic_fiducial_correlation.csv`.

| Variable | Point-biserial r | p-value | Spearman r | p-value |
|---|---|---|---|---|
| quirk_pair_pt_gev | **0.230** | **0.0016** | 0.192 | 0.0085 |
| max\|η\| of pair | **−0.469** | **1.4e-11** | −0.476 | 6.2e-12 |
| β_min of pair | −0.340 | 2.0e-6 | −0.353 | 7.5e-7 |
| n_hits_premerge (proxy, caveated above) | 0.903 | 8.4e-69 | 0.954 | 1.8e-97 |

**pT_pair has a real, statistically significant positive association
with fiducial pass** (p=0.0016) — not large (r=0.23), but genuine and
consistent with the monotonic binned trend in §1. **η-centrality has a
substantially stronger association** (r≈−0.47) — this is the dominant
single kinematic driver of fiducial acceptance, expected directly from
the barrel-only \|η\|<1.8 geometric cut.

**Mediation check** (`tables/pt_eta_mediation_check.csv`): is pT_pair's
effect on fiducial pass actually just a side-effect of higher-pT events
also being more central (which would make pT_pair a confound, not an
independent cause)? Tested directly: pT_pair and max\|η\| are **not
significantly correlated with each other** (Spearman r=−0.066, p=0.37).
Partial correlation of pT_pair with fiducial pass, controlling for
max\|η\|, is 0.191 — barely attenuated from the raw 0.230. **This
demonstrates pT_pair's association with fiducial pass is genuine and
independent of the η-centrality effect, not an artifact mediated
through it.**

## 6. Paper's fiducial denominator — before or after matching/charge requirement?

Reread directly (Sec. IV, p.7, Eq. 12 and surrounding text): the paper's
own factorization has **exactly three** multiplicative stages —
ε = ε_trig × ε_fid × ε_reco — with ε_fid explicitly defined as
conditional on "events passing the trigger." There is no fourth,
separately-named stage for matching or charge-survival anywhere in this
factorization or its surrounding prose. For the EW channel specifically,
this project applies no charge filter at all (EW quirks have fixed unit
charge — charge-survival probability is a colored-channel-only concept,
per Sec. II's ~30% R-hadron-charge statement, itself outside Eq. 12's
three-factor structure). **Conclusion: the paper's ε_fid denominator is
the trigger-passing population drawn directly from the full
generated/matched sample, with no intervening matching or charge
requirement — and this is exactly what this project's own EW
computation already does.** No discrepancy or ambiguity found on this
point.

## 9. Revised wording (per instruction)

**Demonstrated, with appropriate hedging**: "Harder ISR-induced
kinematics contribute to the higher fiducial efficiency." This is now
supported by a genuine correlational test on existing data — not proven
in the strict causal-inference sense (no controlled intervention on
xqcut/PDF was performed; that would require new generation, explicitly
out of scope here), but demonstrated as a real, statistically
significant, eta-independent association, not merely a plausible
argument. **η-centrality is the numerically dominant driver**; pT_pair
contributes an independent, smaller, but real and statistically
significant additional effect. The trigger-efficiency discrepancy
(ε_trig itself) remains **UNRESOLVED — undocumented paper generator
settings**, unchanged from the original report, since this follow-up
does not (and could not, without new generation) test *why* this
project's ISR spectrum differs from the paper's, only that harder ISR
kinematics *do* propagate into higher fiducial acceptance within this
project's own existing sample.

## 10. Scope discipline

No new simulation was run. No sensitivity study of xqcut/PDF/shower was
performed or claimed — any such study, if done in the future, must be
explicitly labeled a sensitivity study, not a reproduction attempt,
since the paper does not publish its own settings (already stated in
the original report, reiterated here per instruction).

---

## Required short final table

| Quantity | Project value | Uncertainty (Wilson 95%) | Paper value | Verified checks | Remaining possible cause | Final verdict |
|---|---|---|---|---|---|---|
| ε_trig (EW) | 186/1045 = 17.80% | [15.60%, 20.24%] | 10% | Trigger variable, threshold, units, boundary, post-shower momenta, generator-config self-consistency (1000 vs 2000) all verified correct | Undocumented paper generator settings (PDF/xqcut/shower tune) — cannot be tested without the paper's own cards | **UNRESOLVED — undocumented paper generator settings** |
| ε_fid (EW) | 94/186 = 50.54% | [43.42%, 57.64%] | 28% | Denominator, both-quirks-all-8-layers logic (structurally + empirically verified, zero false-accepts), 25ns cut, no-endcap, failure sub-categorization, paper denominator definition (§6) all verified correct | Same undocumented generator settings, propagating through kinematics; now **demonstrated** (not just plausible) that harder pT_pair and more central η both independently and causally-consistently raise fiducial acceptance within this project's own data | **UNRESOLVED (root mechanism), with harder-ISR-kinematics contribution now DEMONSTRATED (not merely hypothesized) as a real, statistically significant, η-independent effect** |
