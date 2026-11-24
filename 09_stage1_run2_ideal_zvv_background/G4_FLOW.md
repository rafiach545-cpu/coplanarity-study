# 09 · Stage 1 · Run 2 · Ideal with Geant4: flow, status, next steps

Written 2026-11-21.

## Decision

From Stage 1 on, the detector simulation is done with Geant4, using QuirkPheno quirkcore, which is derived from the public ATLAS athena Quirks code.

- The geometry is the ideal 8-layer barrel, with no material and a uniform 2 T field.
- The old integrator (`simulate_quirk_hits` with the exact-helix SM transport) is kept as the reference that Geant4 is checked against.

There are two reasons for the switch:
- Stage 1 (ideal) and Stage 2 (material, real geometry) must run in one code. Only then is every difference between the stages a detector effect and not a code effect.
- Without material, Geant4 and the old integrator must agree. The work done so far therefore becomes the validation of Geant4.

## Flow

```
 MG5 + Pythia8 (HepMC2)                         unchanged; generation does not depend on the transport
   ├─ signal: 13 TeV Stage 1 grid (2k), 13.6 TeV 10k (07), EW 800 GeV 4 keV (B05)
   └─ background: Z(νν̄)+j 100k (09/B01), later W(ℓν)+j, tt̄, diboson
          │
          ▼
 [G-A] Geant4 full-event application ("qsim_full")         ← NEW CODE NEEDED
        HepMC2 in → every status-1 particle → Geant4 transport (quirks: quirkcore; SM: standard G4 field propagator)
        → layer crossings of EVERY charged particle → hits CSV with the B03 columns
          │
          ▼
 [G-B] the same reconstruction as now (no change)
        pixel quantisation / SCT smearing → pixel merging → track_cleaning (iso20) → coplanarity_fit → SR
          │
          ▼
 B06  Z_N scan (Δs, Δw, multiplicity, cleaning)  →  (m_Q, Λ) sensitivity contour
```

The old integrator runs next to step G-A on the same events. It is the reference: the hits, the planes and the SR decisions must match.

## Status

| # | Step | Status | Where |
|---|---|---|---|
| 1 | Geant4 11.4.1 + QuirkPheno d91cb27 built (env `g4`) | ✅ laptop | `hep_tools/g4_setup`, `hep_tools/QuirkPheno/build` |
| 2 | Ideal 8-layer card, no material | ✅ | `g4/ideal8_vacuum.card` |
| 3 | Quirk-only comparison G01–G04 | ✅ done | `g4/README.md` |
| 3a | Old integrator vs exact references (helix, B = 0 plane, 1D string) | ✅ all pass (< 0.01 µm) | G02, G03, G04 |
| 3b | Geant4 (QuirkPheno) vs the exact helix | ❌ 10–45 µm r-φ error on the SCT layers; grows with the number of geometry-limited steps | G02, G03 |
| 3c | Geant4 vs old at B = 2 T, Λ = 4 keV | ❌ mm–cm differences. Part is the 3b step error; part is that Eq. 3 and the Athena string-vector model differ when v⊥ ≠ 0 | G01 |
| 4 | Locate and fix the per-step error in `QuirkHyperbolaStep` | ❌ to do (laptop, code work) | fix kept as a patch in our repository; QuirkPheno itself unchanged |
| 5 | SM charged particles in Geant4 vs the exact helix (π, K, p, e, μ; p<sub>T</sub> 0.5–500 GeV) | ❌ to do. quirksim records hits only for quirks (`Actions.cc`, `SteppingAction`). Field accuracy (`DeltaChord`, `DeltaIntersection`, ε<sub>max</sub>) to be tuned until < 1 µm | new test G05 |
| 6 | Full-event Geant4 app: HepMC2 input (`HepMC3::ReaderAsciiHepMC2`; quirksim reads HepMC3 only), hits for all charged particles, B03-format output | ❌ to do | new `g4/qsim_full/` |
| 7 | Equivalence test, Geant4 vs old on the same events: 1k Z(νν̄) (HepMC chunk 01 is kept) and 1k signal. Compare hits, SR planes and pass/fail per event | ❌ to do | new test G06 |
| 8 | Physics difference Eq. 3 vs Athena string model (3c): decide which is the nominal model; the other becomes a systematic | ❌ to do (needs a decision, possibly the professor's) | — |
| 9 | Z(νν̄)+j background through Geant4 (100k, then more) | ❌ after 7 | B03 old outputs = reference |
| 10 | Signal through Geant4: B05, then the B08 grid | ❌ after 7 | |
| 11 | W(τν), W(μν/eν)+j | generation ready (`paths09.SAMPLES["wlnu"]`, `server_chunk.sh`); ❌ no lepton veto exists in B03 yet | |
| 12 | tt̄ + single top | ❌ not defined in `paths09.py` yet | |
| 13 | B06 Z_N scan and the (m_Q, Λ) contour | ❌ last | |
| — | Old-integrator results (B03, B05, B07–B09, cleaning choice iso20) | ✅ kept as the reference | README.md |

## Backgrounds

The shares are the published monojet signal-region composition.

| Process | Share of the monojet SR | Role here | Status |
|---|---|---|---|
| Z → νν̄ + jets | 61–66 % | the largest | ✅ 100k (old transport); Geant4 rerun after step 7 |
| W → τν + jets | 16–18 % | most important new sample | ❌ (generation ready, no lepton veto yet) |
| W → μν / eν + jets | 4–8 % each | lepton missed or not vetoed | ❌ same |
| tt̄ + single top | 2–4 % | displaced tracks in b-jets | ❌ second priority |
| Diboson | 2–3 % | small | optional |
| Multijet (fake MET) | < 1 % after the Δφ cut | removed by Δφ(jet, MET) | cite the paper |
| Non-collision | < 0.1 % | hard to simulate | cite the paper |
| Z → νν̄ + γ (conversion) | — | Knapen's background | ✅ 100k at 13.6 TeV (07); 13 TeV only from 05 Stage 1 |

The W samples need a lepton veto before they mean anything. The current chain cuts only on truth MET > 200 GeV.

The proposal is a truth-level veto that mimics the monojet analyses:
- no e or μ with p<sub>T</sub> > 7 GeV and |η| < 2.5;
- no hadronic τ with p<sub>T</sub> > 20 GeV and |η| < 2.5.

These values must be checked against the analysis that is cited for the shares.

## What can run on the server now

| Job | Ready? | Why |
|---|---|---|
| B08 at 25 keV (old transport) | ✅ | SERVER.md (b) |
| W(ℓν)+j and more Z(νν̄)+j **generation** with `KEEP_HEPMC=1` | ✅ | The generation is the same for both transports. The kept HepMC goes to Geant4 later, so it does not need to be generated again |
| Anything through Geant4 | ❌ | Steps 4–7 are code and validation work. They are light and done on the laptop first |

Disk: about 0.8 GB of HepMC per 10k events, so 1M events ≈ 80 GB.
