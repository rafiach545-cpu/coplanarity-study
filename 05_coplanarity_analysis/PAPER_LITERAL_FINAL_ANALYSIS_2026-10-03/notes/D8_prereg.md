## D8. Pre-registered test: pile-up 4-of-8 rate with the cited detector model [34] (written BEFORE the run, 2026-10-08)
- **Question:** our pile-up rate of planes with >= 1 hit in >= 4 of 8 layers is 31/5000 = 6.2e-3 (selected Sec. III C plane, Delta_w < 1) and
  33/5000 = 6.6e-3 (any candidate), against the paper's "~1e-3" (Sec. IV). Changing the definition does not remove the gap; hit density
  (490-1670 per layer, paper "O(1000)"), 45 mm vertex spread and mu = 50 are as in the paper.
- **Run:** `scripts/P21_pileup_ref34.py REF34_Z580 5000`: same 5000 events and seeds as P8 (SeedSequence([90210777, 50, i])),
  two changes only: (1) every pile-up particle propagated with the [34] model (bremsstrahlung for electrons, most-probable ionisation
  with 1/beta^2 scaling, no multiple scattering, stop below 10% kinetic/mass, X0 from Ref. [27] Fig. 3); (2) SCT z 580 um.
  Unchanged: Ref. [27] lengths, pixel merging, track suppression, plane finding.
- **Validation done before the run:** material off + SCT z 1160 on events 0-199 reproduces logs/P8_chunks_LITERAL: plane / multiplicity /
  final identical for 200/200; hits per layer identical except 2 events (one layer-4 hit); Delta_s differs by <= 5.5 um in 7 events.
  Cause: gyroradius constant 333.564 vs 333.569 cm per GeV/T (1.5e-5) between the two helix solvers.
- **Primary statistic:** fraction of the 5000 events whose selected plane (Sec. III C, Delta_w < 1 cm) has >= 1 hit in >= 4 layers.
- **Outcomes, fixed now:**
  - rate <= 2e-3: the gap is explained by the missing material model.
  - 2e-3 < rate < 4e-3: partly explained.
  - rate >= 4e-3 (around 6e-3): unresolved; bug hunt on pile-up stops here.
