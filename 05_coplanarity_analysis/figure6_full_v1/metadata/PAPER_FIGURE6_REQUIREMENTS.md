# Paper Figure 6 Requirements — arXiv:1708.02243v2

Reread sections: Abstract (p.1, string-tension range claim), Sec. II Quirk
Dynamics (p.2, charge-survival probability), Sec. III C (p.6-7, reconstruction
algorithm and Eq. 12 efficiency factorization), Sec. IV Results (p.7-8, signal
region cuts, Table I, Fig. 6 discussion and caption), Appendix A (p.8, not
required for Fig. 6).

Every row below: paper wording, page/line, project implementation, verdict.

## 1. Production channels

**Paper (p.2, verbatim):** "vector-like quirks in the (1,1)₁ and (3,1)₂/₃
representations" — EW (Drell-Yan, hypercharge-1 singlet) and colored (QCD
triplet) benchmarks respectively.
**Project:** `quirk_ew_800gev_4kev` (EW/DY) and `quirk_signal_1800gev_2kev`
(colored/QCD) process directories, reused as templates for all mass points.
**Verdict:** MATCH. Affects: generation.

## 2. Charge-survival probability (colored only)

**Paper (p.2, verbatim):** "the probability for those final states to have
±1 charges is roughly 30% as estimated using Pythia8." "Our analysis is
largely independent on the charges of the quirk-hadrons, as long as both
quirk-hadrons carry non-zero electric charge."
**Project:** `_make_rhadron_charge_lookup()` queries Pythia8's own R-hadron
charge table (not a hand-coded 30% draw) and filters to events where BOTH
quirks are ±1. Measured this project, three separate mass points:
1800 GeV → (existing production), 1500 GeV → 37.2%, 2400 GeV → 33.3%.
**Verdict:** MATCH (methodology identical — uses Pythia8's own hadronization
tables, not an approximation of the paper's 30% figure; measured project
values cluster near the paper's ~30% but are not required to match it
exactly since the paper does not give a per-mass value). Affects: generation/
reconstruction denominator.

## 3. Eq. 12 efficiency factorization

**Paper (p.6, Eq. 12, verbatim):** "ε = ε_trig × ε_fid × ε_reco."
**Project:** total efficiency computed identically as
`ε_charge(colored only) × ε_trig × ε_fid × ε_reco`, i.e. the paper's
factorization plus an explicit additional charge-survival factor for colored
points (the paper folds charge survival into its narrative discussion, p.2,
but Table I's ε_trig/ε_fid/ε_reco numbers are quoted for a fixed benchmark
without re-deriving the ±1 fraction per point).
**Verdict:** MATCH, with the charge-survival factor made an explicit fourth
term for colored points (a PROJECT CLARIFICATION, not a deviation — the
paper's own trigger efficiency for colored quirks is implicitly conditioned
on this population; see item 10 below and the trigger-denominator
correction already made in the consolidated report, commit `cf0e3d2`).
Affects: efficiency/final contour.

## 4. ε_fid definition

**Paper (p.6, verbatim):** "parametrizes the likelihood that each quirk
intersect with each layer at least once, in events passing the trigger. We
also include a 25 ns timing cut, which causes a slight drop in ε_fid for
heavier quirks."
**Project:** `truth_fiducial = geometric_fiducial (16/16 hits pre-merge) AND
timing_ok (max_hit_t_ns < 25.0)`, exactly as coded in
`run_downstream_pipeline.py::analyze_event` and used unchanged throughout
this project.
**Verdict:** MATCH. Affects: reconstruction/efficiency.

## 5. ε_reco / signal-region cuts (Sec. IV, p.7)

**Paper (p.7, verbatim, 3 numbered cuts):**
1. "At least one plane reconstructed under the tracking algorithm"
2. "All but one layer must contain 2 hits, the remaining layer must contain
   at least 1 hit"
3. "Δw < 1.0 cm and Δs < 0.01 cm"

**Project:** `select_reconstructed_plane` (cut 1),
`check_hit_multiplicity` (cut 2), `apply_signal_region_cuts` (cut 3),
all in `coplanarity_fit.py`, unmodified since prior validation.
**Verdict:** MATCH. Affects: final contour.

## 6. Sec. III C seeding / iterative fit

Already verified and corrected in the consolidated report (commit
`cf0e3d2`): Δφ<0.1, Δz<2cm seed pairing (starting from layer 8, then layer
7), xa·n3>0, Δs<0.05cm / Δw<1cm seed cuts, growth-factor-3 iterative-fit
stopping rule — all DIRECT PAPER REQUIREMENT, page 5-6, code-identical in
`coplanarity_fit.py::seeding_and_iterative_fit`, unchanged for this task.
**Verdict:** MATCH (carried over, not re-derived this task). Affects:
reconstruction.

## 7. Table I benchmark efficiencies (p.7)

**Paper:** mQ=800 GeV (DY) at Λ=1,2,3,4,5 keV: ε_trig=0.10, ε_fid=0.28,
ε_reco=0.11/0.41/0.65/0.72/0.74. mQ=1800 GeV (QCD) at Λ=1,2,3,5,10 keV:
ε_trig=0.24, ε_fid=0.28, ε_reco=0.083/0.35/0.59/0.74/0.58.
**Project:** these are the project's own pre-existing frozen benchmark
results (Figures 1-5, frozen per this task's own instruction — NOT rerun).
**Verdict:** REFERENCE ONLY for this task — used as a consistency check on
the grid's two edge points, not regenerated. Affects: none (frozen).

## 8. Mass and Λ ranges for Fig. 6 (p.8-9, Fig. 6 caption + axes)

**Paper:** two panels. Colored panel: mQ axis 500-2500 GeV; Λ axis ~10-30000
eV (log above ~100 eV, linear below, per caption "linear←|→log"). EW panel:
mQ axis 0-1000 GeV, same Λ axis. No explicit list of *generated* mass/Λ grid
points is given in the paper — the smooth contour implies either a fine
generation grid or (more likely, given documented single-CPU-year-scale
compute costs of full LHC MC at the time) a coarser generated grid with
interpolation. The paper does not state its own grid resolution.
**Project:** 91-point proposal (7 colored mass points, 6 EW mass points, 7
Λ values each) drawn from the existing
`figure6_figure7_blockers_v1/Figure_6_future_work_grid_proposal_v1.md`,
spanning the same mQ/Λ ranges as the paper's axes.
**Verdict:** APPROXIMATE — the project's grid resolution is a PROJECT
ASSUMPTION (the paper's own grid density is not published), chosen to be
fine enough to trace the qualitative shape of both contours while remaining
computationally tractable on this project's hardware. Affects: contour
resolution.

## 9. Λ does not require new generation

**Paper:** Λ (string tension) enters only through the Nambu-Goto trajectory
integration (Eq. 3-4) after parton-level production; it does not appear in
the hard-scattering matrix element. Production cross-section and kinematics
depend only on mQ and the production channel.
**Project:** confirmed by code inspection — `Λ_gev` is a keyword argument to
`simulate_quirk_hits`/`integrate_trajectory*`, not a MadGraph run_card/
param_card parameter for these signal processes. One LHE/matched sample per
distinct mass point is reused across all 7 Λ values for that point.
**Verdict:** MATCH. Affects: generation (large cost saving — generation runs
once per the 13 distinct mass points, not per 91 mass-Λ combination).

## 10. Colored trigger efficiency denominator

Already corrected in the consolidated report (commit `cf0e3d2`): the
project's ε_trig for colored points is computed relative to the
charge-filtered subsample (both quirks ±1), not the full matched sample.
This is consistent with item 2/3 above (Eq. 12's ε factorization is
implicitly applied to the population of events that can leave a trigger-
level track, i.e. already charge-filtered).
**Verdict:** MATCH (project convention, internally consistent, documented).
Affects: efficiency/final contour.

## 11. Discovery / exclusion criterion (p.8, Fig. 6 caption, verbatim)

**Paper:** "Contours of having 3 (5) events... for an integrated luminosity
of ∫Ldt = 300 fb⁻¹... The 3 events bound corresponds to 2-σ exclusion given
no background. Discovery is defined by 5 events." Backgrounds are explicitly
assumed negligible ("negligible irreducible backgrounds", p.8) for this
figure specifically — separate from the finite (near-zero, non-negligible in
absolute terms but negligible relative to N_signal thresholds of 3-5) pile-up/
converted-photon background estimates given elsewhere in the paper for the
signal-region cut validation (Fig. 5).
**Project implementation for this task:** N_signal = L(300 fb⁻¹) × σ_matched
× ε_total; exclusion boundary = 3 events, discovery boundary = 5 events, no
background subtraction (consistent with the paper's own stated assumption
for this specific figure).
**Verdict:** MATCH (paper's own stated assumption, not a project
simplification). Affects: final contour.

## 12. Cross-section source

**Paper:** MadGraph5_aMC@NLO matched cross-section (implied by standard
LO/NLO matching workflow described in Sec. III A; exact generator settings
not published).
**Project:** matched cross-section (`sigma_matched` from each point's
generation log / merged_xsecs.txt), as already used for all prior benchmark
results in this project.
**Verdict:** MATCH in methodology; ASSUMPTION that the paper used the same
QCD order/PDF set (unresolved — paper's exact MadGraph settings are not
published; already documented as UNRESOLVED in the consolidated report).
Affects: absolute cross-section normalization, hence absolute mass reach.

## 13. Backgrounds for Fig. 6 specifically

**Paper:** "assuming negligible irreducible backgrounds" (p.8, explicit for
this figure). This project's own pile-up/converted-photon background studies
(frozen, Figures 1-5 scope) found compatible near-zero-but-not-exactly-zero
background yields after the Sec. IV cuts, at a level the paper itself
would also consider "negligible" relative to a 3-5-event threshold.
**Verdict:** MATCH — no background subtraction needed for Fig. 6
specifically, consistent with both the paper's explicit assumption and this
project's own frozen background results. Affects: final contour
(simplification is justified, not applied blindly).

## 14. Interpolation / contour construction

**Paper:** does not document its interpolation method. The published
contours are smooth curves; the paper's own generation grid density is not
stated.
**Verdict:** MISSING (paper does not specify) → PROJECT ASSUMPTION required.
This project will use a documented, disclosed interpolation method (Phase 9)
and will not claim it matches the paper's undocumented method. Affects:
final contour visual only, not underlying efficiency/yield tables.

## Summary of MISSING / ASSUMPTION items requiring explicit disclosure

- Paper's own mass-Λ grid resolution: **MISSING** — project grid is an
  assumption, chosen for computational tractability, documented as such.
- Paper's own interpolation/contour-drawing algorithm: **MISSING** — project
  will use and disclose its own (e.g. linear or cubic interpolation on
  log(N_signal)), not claim equivalence.
- Paper's exact MadGraph/PDF/QCD-order settings: **UNRESOLVED** (documented
  previously, carried over unchanged).
- Λ grid values themselves (which discrete Λ the paper evaluated, if any,
  versus a continuous integration): **MISSING** — project uses a specific
  discrete Λ list (Phase 3), disclosed as project-chosen.

No item above blocks proceeding; all MISSING/ASSUMPTION items are ones the
paper itself does not resolve, and the project's choices are documented so
comparison claims in Phase 10 can be correctly scoped (APPROXIMATE, not
EXACT).
