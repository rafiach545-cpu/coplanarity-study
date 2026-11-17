# Z(νν̄)+jets background for the coplanarity search: plan (2026-11-17, not started)

## Why

Only Z(νν̄)γ+j conversions have been simulated. Z(νν̄)+jets passes the same MET > 200 GeV trigger and has a 47 times larger cross section: 10.8 pb at LO from MG5, about 3.6 × 10⁶ events at 332 fb⁻¹ (`xsec_mg5/X01_xsec_13p6TeV.csv`). W(ℓν)+jets is similar (≤ 12.2 pb).

Their jets contain particles that can make a thin two-track plane (`BACKGROUND_CANDIDATES.md` B1–B4):
- photons from π⁰ and η decays that convert in the material;
- Dalitz e⁺e⁻ pairs;
- K_S and Λ decays;
- 3-prong τ decays (from W).

The claim "A580 background below one event" holds today only for the Zγ process.

## Code needed

| Step | Script | What it does | New or reused |
|---|---|---|---|
| B01 | `B01_zjets_generate.py` | MG5 `p p > vl vl~ j` (+ an optional second jet with MLM matching), MET > 200 GeV, 13.6 TeV; Pythia8 with π⁰, η, K_S and Λ decaying (default) | chunked like Z01 / L01 |
| B02 | `B02_extract_objects.py` | For every event, the "plane candidates" from the HepMC: (i) photons with their production vertex (π⁰/η → γγ); (ii) Dalitz e⁺e⁻ pairs; (iii) K_S → π⁺π⁻ and Λ → pπ with the decay vertex; (iv) τ 3-prongs. Momenta and vertices are written per object | new; based on the existing HepMC readers |
| B03a | C01 with `--photons` | **Cheap first step:** the jet photons (i) are fed straight into the existing C01, which accepts any photon list. This gives the π⁰/η conversion background with no new detector code. A vertex column (photon not from the PV) must be added. | small extension of C01 |
| B03b | `B03_two_track_bkg.py` | Like C01, but the two charged tracks start at a given vertex with given momenta: Dalitz pairs, K_S, Λ (`detsim07.propagate` already takes any mass and charge) | about 150 lines, generalising C01 |
| B04 | `B04_summary.py` | Pass probability per object type, times the number of such objects per event, times L σ. An upper limit is given when nothing passes, as in S01 | new, short |
| Tests | — | B03b with a single photon reproduces C01 row by row; B02 object counts are checked against the Pythia decay tables (R8 BRs) | — |

## Cost

**Generation.** About 30 min per 10⁵ events in 10 chunks, as for Zγ (5 min per 10k). With a second matched jet it is about 2–3 times slower. Events with MET > 200 GeV are kept.

**Objects.** About 10–20 π⁰ per event (so 20–40 photons), about 1 K_S and a few Dalitz pairs. Most are soft. A cut on the object momentum (for example p > 1 GeV, enough to cross 8 layers) leaves only a few per event.

**Detector time.** This scales with the number of objects:
- μ = 0 is about 10 times cheaper than μ = 50.
- Plan: first μ = 0 for all objects, to see which kinds can pass the selection at all. Then μ = 50 only for those kinds.
- Example: 10⁵ events × about 5 hard photons at μ = 50, ATLAS A580, 40 workers: about 5 × 7.5 h ≈ 40 h on the server. μ = 0 takes a few hours.

**Coding.** About 2–3 days: B02 and B03b, the tests, and the normalisation. Plus 1–3 days of server time.

**Order of the work if required:** B01 → B02 → B03a (jet photons, cheapest, closest to the existing result) → B03b (Dalitz, K_S) → τ from W+jets.

## Open questions for the decision

- Is the per-object factorisation (pass probability × objects per event) acceptable, instead of full events at 3.6 × 10⁶ × pile-up?
- Is W(ℓν)+jets needed as well, or only Z(νν̄)+jets?
- Hadronic interactions in the material (B5) need Geant4 or a parametrisation. They are not in this plan.
