# 09 · Stage 1 · Run 2 · Ideal — Z(νν̄)+jets background with full events

Started 2026-11-19. This is the first step of the professor's plan of 2026-11-18 ("Quirk searches with an ideal tracker"). It covers:

- the ideal 8-layer tracker, B<sub>z</sub> = 2 T, 13 TeV, no pile-up;
- signal and SM background;
- ordinary-track cleaning;
- a full-sample cut optimisation scored by Z<sub>N</sub>.

Only public tools and public inputs are used. The folder is separate from 05/06/07: nothing there is changed, and the 06 figures are not touched.

## Setup

| Item | Value | Source |
|---|---|---|
| Process | `p p > vl vl~ j` (Z → νν̄ + 1 jet), 4-flavour sm model, LO, no ME/PS matching | MG5_aMC 3.7.3 |
| Shower / hadronisation | Pythia 8.317 via MG5 (MG5's HEPTools install, HepMC 2.06.09), default card. All unstable particles decay, and production vertices are kept. Particle charges in `hepmc_events.py` come from the conda Pythia 8.312 Python module | Pythia 8.317 (`tag_1_pythia8.log`) |
| Energy and generator cuts | √s = 13 TeV, `misset` = 200 GeV (Σ p<sub>T</sub>(ν)), `ptj` = 20 GeV | MG5 run card (each run's banner) |
| Trigger / event cut | Truth MET (all status-1 neutrinos) > 200 GeV. This matches the signal's trigger proxy p<sub>T</sub>(QQ̄) > 200 GeV | as the 05/06 Stage 1 signal |
| Detector | 8-layer barrel of arXiv:1708.02243 Sec. III A (`04_detector_sim/atlas_geometry.py`). Pixel hits are quantised to the pitch; SCT smearing is 34 µm r-φ and 1160 µm z. Hits need \|η<sub>hit</sub>\| < 1.8 and t < 25 ns. No material; uniform 2 T | frozen Stage 1 code |
| Particles | Every status-1 charged particle is propagated as an exact helix from its own production vertex (`pileup_hits.pileup_particle_hits`). The vertex is shifted by the hard-vertex z₀ ~ N(0, 4.5 cm) | frozen Stage 1 code |
| Reconstruction | Pixel merging over the whole event. Hits are taken relative to the true PV. Then the plane finder and the signal-region cuts (Δw < 1 cm, smallest Δs, multiplicity, Δs < 100 µm) | `05_coplanarity_analysis/coplanarity_fit.py`, unchanged |

## Steps

| Script | What it does | Status |
|---|---|---|
| `B01_generate_zvv.py` | MG5 + Pythia8 in chunks; `iseed` = 391000 + chunk | pilot (chunk 0, 1k) and chunks 1–10 (10k each) done |
| `hepmc_events.py` | Streaming HepMC2 reader: charged status-1 particles with their production vertex, plus truth MET | tested |
| `B03_hits_and_planes.py` | Hits and planes for every event, for the "All hits" and "orphan" inputs. Writes one row per event and the candidates for the cut scan | 100k done |
| `track_cleaning.py` (B04) | Ordinary-track cleaning: a PV-constrained helix road search, no truth. Hits on found tracks are removed ("orphan" input). Called inside B03 | done |
| B05 (next) | Signal with the same full-event treatment (quirks + Pythia underlying event), from the existing 13 TeV LHE files | to do |
| B06 (next) | Z<sub>N</sub> scan over the cuts (Δs, Δw, multiplicity, cleaning on/off). σ<sub>B</sub> combines MC statistics with 10/20/30 % normalisation | to do |

## Pilot (chunk 0, 1 000 events, 2026-11-19)

- σ = 9.97 pb at 13 TeV with `misset` > 200 GeV. 903 of the 1 000 events have truth MET > 200 GeV after the shower.
- About 610 hits per event. Each event takes 0.1 s, so the 1 000 events took 13 s wall on 8 workers.
- **Signal region: 0 of 1 000 events pass.** However:
  - 668 events have a selected plane;
  - 179 of those pass the multiplicity cut, and the smallest Δs among them is 105 µm (the cut is 100 µm);
  - 14 have Δs < 100 µm, but these have too few hits. They are mostly 2–3 pions, often from displaced decays at r ≈ 25–45 cm.
- Consequence: the full-multiplicity planes are close to the Δs cut. A large sample, a tail extrapolation and ordinary-track cleaning are therefore needed.
- Normalisation at 139 fb⁻¹: 9.97 pb × 139 000 pb⁻¹ ≈ 1.39 × 10⁶ events, about 1.25 × 10⁶ after MET > 200 GeV. To show B < 0.1 event directly from zero passing MC events would need about 4 × 10⁷ MC events.

## 100k sample (chunks 1–10, 2026-11-19)

- 100 000 events, σ = 10.04 pb (mean of the 10 runs); 90 158 have truth MET > 200 GeV. Weight at 139 fb⁻¹: 13.95 events per MC event.
- Cleaning: 99.25 % of prompt particles with hits on ≥ 6 layers are fully removed. Mean hits per event: about 610 (All), about 79 (orphan).
- Signal region (MET > 200 GeV):

| Input | Multiplicity-OK selected planes | SR pass (MC) | SR pass at 139 fb⁻¹ |
|---|---|---|---|
| All hits | 17 653 | 42 | ≈ 586 |
| Orphan | 459 | 23 | ≈ 321 |

- What passes: almost always 2–4 prompt charged hadrons (π, K, p) from the same jet. Two stiff tracks from the PV lie in one plane through the PV, so they look coplanar. In the orphan input the survivors are mostly pairs with p<sub>T</sub> > 50 GeV, which the cleaning misses (to be understood: likely hit sharing / pixel merging in the jet core).
- The pilot's 0 / 1 000 was a statistical fluctuation of this rate (about 0.4 per 1 000).

## Cleaning v2 (2026-11-19): fix for stiff tracks

- Cause of the orphan passes above (v1): the seed used only two pixel hits (r = 3–12 cm). For tracks with p<sub>T</sub> ≳ 50 GeV the 50 µm pixel pitch over this short lever arm gives a wrong curvature (a 101 GeV K⁺ was fitted as 12 GeV, a 96 GeV π⁻ as 3.8 GeV). The prediction at L5 then missed by 1.3–5 mm (the window is 1 mm), no SCT hit was added, and the track was rejected. Two such tracks from one jet lie in one plane with the PV and pass the SR.
- Fix in `track_cleaning.py`: a second pass with SCT seeds (r = 30–51 cm) and an inward road. v1 code and outputs are kept in `data/v1/`.
- 100k rerun (`run_b03_v2.sh`), MET > 200 GeV:

| | v1 | v2 |
|---|---|---|
| Prompt particles fully removed | 99.25 % | 99.57 % |
| Orphan hits per event | 79.3 | 76.2 |
| Removed hits from displaced particles | 0.52 % | 0.79 % |
| Orphan multiplicity-OK planes | 459 | 9 |
| Smallest Δs of those | 70 µm | 153 µm |
| **Orphan SR pass** | **23** | **0** |
| All-hits SR pass (unchanged input) | 42 | 42 |

- At 139 fb⁻¹ (13.95 events per MC event), 0 MC events means B < 13.95 × 3.00 ≈ 42 events (95 % CL, −ln 0.05 = 3.00; used for every zero-event limit in this folder) from MC statistics alone. A smaller bound needs a larger sample or a tail extrapolation.

## B05: signal as a full event (2026-11-19)

The setup:
- EW quirks, m<sub>Q</sub> = 800 GeV, Λ = 4 keV. The input is the Pythia8 file of the Stage 1 sample (511 events), whose status-1 quirks are exactly the momenta of `ew_quirk_pair_momenta_800gev_4kev.csv`.
- Quirk hits come from `simulate_quirk_hits` (numba RK4, validated in g4/G02–G04). The underlying-event hits are made as in B03. There is one pixel merging over the whole event.
- Three inputs: quirk hits only ("qrk", the Stage 1 treatment), all hits, and orphan hits.

| Triggered (p<sub>T</sub>(QQ̄) > 200 GeV) | Stage 1 fiducial | qrk | all | orphan |
|---|---|---|---|---|
| 89 | 41 | 8 (ε<sub>reco</sub> = 0.195) | 8 (0.195) | **3 (0.073)** |

- Check against Stage 1: the 06 grid has ε<sub>reco</sub> = 7/48 = 0.146 (Z1160) from its own, larger production sample. That is consistent with 8/41 within the binomial error (≈ ±0.06).
- The underlying event does not change the signal: all = qrk = 8.
- **The cleaning costs signal at this point:**
  - 142 of 827 quirk hits are removed (17 %), in 14 of the 41 fiducial events;
  - in 5 of the 8 passing events, 6–16 quirk hits are absorbed into "tracks". At 4 keV the two 800 GeV quirks barely oscillate, so each looks like a stiff prompt helix.
- **Trade-off at 139 fb⁻¹:**
  - cleaning cuts the Z(νν̄)+jets background from 42 MC events (≈ 586) to 0 (< 42 at 95 % CL);
  - it also keeps only 3/8 of the signal here.

## B07–B09: cleaning variants (2026-11-20)

- **B07**: pT-threshold cleaning on the 100k background. Only found tracks with p<sub>T</sub> < 20 / 50 / 100 GeV are removed.

  | Variant | SR pass (MC) | B at 139 fb⁻¹ |
  |---|---|---|
  | c20 | 69 | ≈ 963 |
  | c50 | 92 | ≈ 1283 |
  | c100 | 24 | ≈ 335 |
  | cinf | 0 | < 42 (95 % CL) |

  The soft-track thresholds make the background *larger* than with no cleaning (42 MC events), because the stiff 2–4 track planes are then selected. The 20 and 50 GeV thresholds are dropped.

  The factorised estimate (Δs fraction of the "all" planes) fails its own check: at c100 the direct MC gives ≈ 335 and the factorised value ≈ 4. It is withdrawn. If used again, the Δs fraction must be measured on the planes that survive each cleaning.
- **B08**: signal over (m<sub>Q</sub>, Λ). The input is the 13.6 TeV 10k-generated EW samples of 07; at 13 TeV only the 2k Stage 1 grid samples exist. Variants: c100, cinf, iso and iso20.
  - **iso** removes the tracks that have ≥ 2 other found tracks within ΔR < 0.4.
  - **iso20** does the same and also removes tracks with p<sub>T</sub> < 20 GeV.
  - The first pT-only run is kept in `data/B08_v1_ptcuts/`.
- **B09**: the same variants on the background (same hits and tracks as B07).
- Paths: everything goes through `paths09.py`. Server instructions are in `SERVER.md`.

### B08 + B09 results (2026-11-20)

**Background (B09).** The input is 100k Z(νν̄)+jets events with MET > 200 GeV; the weight is 13.95 per MC event at 139 fb⁻¹. B09's c100 and cinf columns are identical to B07, event by event.

| Variant | SR pass (MC) | B at 139 fb⁻¹ | Multiplicity-OK planes | Smallest Δs of those |
|---|---|---|---|---|
| c100 | 24 | ≈ 335 | 108 | 43 µm |
| cinf | 0 | < 42 (95 % CL) | 8 | 153 µm |
| iso | 0 | < 42 (95 % CL) | 22 | 136 µm |
| **iso20** | **0** | **< 42 (95 % CL)** | 17 | 153 µm |

**Signal (B08).** EW quirks, 13.6 TeV 10k-generated samples; each entry is SR pass / Stage 1 fiducial events. The 25 keV part runs on the server (SERVER.md).

| m<sub>Q</sub> (GeV) | Λ (keV) | Fiducial | qrk | cinf | c100 | **iso20** | iso20 / qrk |
|---|---|---|---|---|---|---|---|
| 100 | 1 | 120 | 0.025 | 0.008 | 0.017 | 0.025 | 1.0 |
| 100 | 4 | 122 | 0.066 | 0.000 | 0.008 | 0.033 | 0.50 |
| 100 | 10 | 123 | 0.041 | 0.000 | 0.008 | 0.024 | 0.60 |
| 400 | 1 | 286 | 0.038 | 0.014 | 0.017 | 0.024 | 0.64 |
| 400 | 4 | 303 | 0.142 | 0.040 | 0.066 | 0.112 | 0.79 |
| 400 | 10 | 298 | 0.067 | 0.013 | 0.023 | 0.044 | 0.65 |
| 800 | 1 | 352 | 0.023 | 0.017 | 0.020 | 0.023 | 1.0 |
| 800 | 4 | 377 | 0.183 | 0.045 | 0.093 | 0.141 | 0.77 |
| 800 | 10 | 382 | 0.115 | 0.034 | 0.071 | 0.081 | 0.70 |
| 1200 | 1 | 377 | 0.021 | 0.011 | 0.016 | 0.013 | 0.63 |
| 1200 | 4 | 400 | 0.135 | 0.035 | 0.068 | 0.110 | 0.81 |
| 1200 | 10 | 391 | 0.092 | 0.010 | 0.038 | 0.069 | 0.75 |

At Λ = 0.1 keV no input passes (0 everywhere). In all passing signal events the SR plane is mostly made of quirk hits.

**Choice: iso20.**
- It gives the same background bound as cinf: 0 MC events, and the closest multiplicity-OK plane is at the same Δs of 153 µm.
- It keeps 50–80 % of the uncleaned signal at Λ ≥ 4 keV, against 0–30 % for cinf.
- iso has the same bound, but it leaves 283 hits per event and has a plane at 136 µm.
- The iso parameters (ΔR < 0.4, ≥ 2 neighbours, p<sub>T</sub> < 20 GeV) were fixed before looking at the results. They are not tuned.
- The background bound is limited by MC statistics (< 42 events). The large server run is needed to go below it.
