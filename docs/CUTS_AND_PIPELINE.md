# arXiv:1708.02243v2 — "Tracking down Quirks at the Large Hadron Collider"
## Fresh reproduction plan — all cuts, all stages, generation-time cuts enforced wherever possible.

Paper: Knapen, Lou, Papucci, Setford, "Tracking down Quirks at the Large Hadron Collider,"
arXiv:1708.02243v2 [hep-ph], 13 Nov 2017.

This document is derived directly from the paper text + the ATLAS Run-2 Inner Detector
alignment paper (arXiv:2007.07624) for the detector geometry. It does not reuse any code,
numbers, or conventions from any other prior project.

---

## Benchmark points

| Representation | Type | mQ (GeV) | Lambda | Where used in paper |
|---|---|---|---|---|
| (1,1)_1, unit charge | Drell-Yan (EW) | 800 | 1,2,3,4,5 keV | Table I |
| (3,1)_{2/3} | QCD (colored) | 1800 | 1,2,3,5,10 keV | Table I |
| (3,1)_{2/3} colored | QCD | 1800 | 2000 eV | Fig 4, Fig 5 main benchmark |
| (1,1)_1 EW | DY | 800 | 4000 eV | Fig 5 |
| (3,1)_{2/3} colored scan | QCD | 500-2500 | 10 eV - 30000 eV | Fig 6 |
| (1,1)_1 EW scan | DY | 0-1000 | 10 eV - 30000 eV | Fig 6 |

**First milestone target (this build): colored quirk, mQ = 1800 GeV, Lambda = 2 keV** — matches
Fig. 4 (single event display) and the colored-quirk curve in Fig. 5.

**Event counts for this run (per your instruction):**
- Signal (quirk) events: **1000**
- Photon-conversion background events: **10,000**
- Pile-up minimum-bias library: paper uses 125,000 events at <mu>=50 — build toward this,
  scale honestly reported if reduced for compute/time reasons (never silently substitute).

---

## STAGE 0 — Signal generation (MadGraph5_aMC@NLO -> Pythia8)

- Process: `p p > Q Q~ [+ 1 jet]`, MLM-matched, MadGraph5_aMC@NLO -> Pythia8.
- EW quirks: Drell-Yan only, unit electric charge, representation (1,1)_1.
- Colored quirks: QCD pair production only, representation (3,1)_{2/3}.
- Quirk set STABLE in Pythia (`ParticleDecays:limitTau0/limitTau0Max`-style stable flag, or
  `<PDGID>:mayDecay = false`) — it is a heavy stable charged/colored particle, not something
  that hadronizes/decays away.
- Requires a custom UFO model for the vector-like quirk — not a stock MadGraph model. This is
  the first real implementation task in 01_signal_generation/.
- **Generation-level cut**: none of the paper's kinematic cuts (pT_CM>200 GeV etc.) apply at
  the matrix-element level for the signal — that cut is a property of the produced pair's
  system momentum, applied downstream once the pair 4-momenta are known (Stage 3). What IS
  set at generation time is the process definition itself (DY vs QCD, +1 jet matching).
- Output per event: two quirk 4-momenta + ISR jet. Nothing else from MG5/Pythia8 is used
  downstream — the quirks themselves do not shower or hadronize away.

## STAGE 1 — Classical trajectory evolution (custom code, not MadGraph/Pythia)

- Input: the two quirk 4-momenta from Stage 0.
- Integrate Eq. 3 of the paper numerically: Nambu-Goto confining string force
  (string tension = Lambda^2) + external Lorentz force from a **uniform B = 2 T field along z**.
- Validate the integrator against the paper's own sanity plots before trusting it downstream:
  reproduce the qualitative shape of Fig. 2 (angular momentum L and separation d vs radial
  distance r) and Fig. 3 (Delta_phi vs r for mQ=1.8 TeV and mQ=800 GeV, Lambda=2 keV, B=2T).
- No hadronic-material secondary production modeled (paper does not model this either for the
  quirk itself — only affects the pile-up background modeling, Stage 6a).

## STAGE 2 — Detector hit simulation (ATLAS Run-2 Inner Detector barrel, 8 layers)

Geometry source: **ATLAS Collaboration, "Alignment of the ATLAS Inner Detector in Run-2,"
arXiv:2007.07624**, Table 1 / Section 2 — as given in your reference image ("Method B").

| Layer | Element | radius r [mm] | pitch (r-phi, z) | resolution sigma(r-phi, z) [um] |
|---|---|---|---|---|
| L1 | IBL | 33.25 | 50 x 250 um | 10, 60 (paper); **use 2x per Knapen prescription for SCT only, IBL/Pixel use pixel PITCH directly per paper Sec IIIA** |
| L2 | Pixel B0 | 50.5 | 50 x 400 um | pixel pitch used directly (Knapen et al. Sec IIIA) |
| L3 | Pixel B1 | 88.5 | 50 x 400 um | pixel pitch used directly |
| L4 | Pixel B2 | 122.5 | 50 x 400 um | pixel pitch used directly |
| L5 | SCT B3 | 299 | 80 um strip pitch | 34 (r-phi), 1160 (z) = 2x intrinsic, per Knapen et al. |
| L6 | SCT B4 | 371 | 80 um strip pitch | 34, 1160 |
| L7 | SCT B5 | 443 | 80 um strip pitch | 34, 1160 |
| L8 | SCT B6 | 514 | 80 um strip pitch | 34, 1160 |

Rule from the paper (Sec III A), applied exactly:
- **Pixel/IBL layers (L1-L4): use the pixel SIZE (pitch) as the effective resolution**, not the
  intrinsic single-hit resolution.
- **SCT layers (L5-L8): use 2x the intrinsic accuracy** (34 um r-phi / 1.16 mm z, i.e. double
  the ATLAS-quoted 17 um / ~580 um figures) — this is the paper's own conservative choice, not
  an ATLAS number.
- Beam pipe (photon-conversion material) inner radius: **r_conv = 23.5 mm** (from the ATLAS
  beam pipe radius used in your reference figure) — this is the radius at which the
  photon-conversion background (Stage 6b) is allowed to convert.
- Hit merging: hits in neighboring pixels merged into a single hit (models ATLAS hit-merging
  procedure) — define adjacency in pixel-index space explicitly and document the exact rule
  used (the paper does not give a numeric adjacency rule, so ours must be stated, not implied).
- Beamspot smearing: uniform Gaussian smearing, **sigma_z = 45 mm**, applied to every hit's
  z-coordinate (paper value, models finite longitudinal beamspot size).
- Fiducial range: **|eta| <~ 1.8** (barrel only — no endcaps, no TRT, no calorimeters).
- Magnetic field (2 T along z) is already folded into the Stage 1 trajectory — do not reapply.

## STAGE 3 — Trigger emulation cut

- **pT(quirk-pair CM system) > 200 GeV** — emulates the Run-2 startup MET trigger threshold.
  Apply this at the parton/truth level on the Stage-0 output (sum of the two quirk 4-momenta's
  transverse momentum), BEFORE running Stage 1/2, to avoid wasting compute on events that would
  fail the trigger anyway. This is a "generation-time" cut in spirit even though it is computed
  post-generation from MG5/Pythia8 output — MadGraph's own generation-level `ptheavy`-style cuts
  are only a loose proxy since MG5 doesn't directly cut on the true post-shower pair-pT; state
  clearly in code comments that this is the EXACT truth-level cut, not a generator-card proxy.

## STAGE 4 — Fiducial cuts

- |eta| <~ 1.8 (barrel-only acceptance, Stage 2 geometry).
- 25 ns timing cut: quirk must reach each detector element within 25 ns of the interaction
  (paper's stated timing constraint for the tracker/muon system). Compute exactly from the
  Stage-1 trajectory's time coordinate, not approximated.
- Each quirk must intersect all 8 layers at least once (folded into epsilon_fid).

## STAGE 5 — Plane-finding / coplanarity algorithm

Distance metric: for hit set {x_a}, tensor `T_ij = (1/(N-1)) sum_a x_a_i x_a_j`. Eigen-decompose:
smallest eigenvalue -> Delta_s^2 ("thickness"), eigenvector n1 = plane normal. Second eigenvalue
-> Delta_w^2 ("width"), eigenvector n2. Third eigenvector n3 (largest eigenvalue) ~ flight dir.

**Seeding (layers 8 and 7):**
1. Layer 8: all hit pairs with Delta_phi < 0.1, Delta_z < 2 cm. Same for layer 7.
2. Combine one pair from each -> 4-hit seed. Require: `x_a . n3 > 0` for all hits,
   `Delta_s < 0.05 cm`, `Delta_w < 1 cm`.

**Iterative fitting (layers 6 down to 1), per seed:**
3. At each layer, candidate hits satisfy `(x . n3) > 0`, `|x . n1| < 0.05 cm`, `|x . n2| < 1 cm`.
4. Add hits smallest-`|x.n1|`-first; keep only if Delta_s, Delta_w do not grow by more than 3x.
5. Repeat to layer 1; finalize {x_a}, Delta_s, Delta_w for this seed.

**Event selection (Sec III C step 3 — part of the algorithm itself, runs BEFORE any
signal-region cut below):**
- Gather every candidate from every seed. Keep only those with `Delta_w < 1.0 cm`. If more
  than one survives, keep the single one with the smallest Delta_s. This yields AT MOST ONE
  "reconstructed plane" per event — not a search for whichever candidate happens to separately
  pass every downstream cut (`select_reconstructed_plane()` in `coplanarity_fit.py`).

**Signal-region cuts (Sec IV, applied only to that single reconstructed plane):**
1. At least one reconstructed plane (the step above succeeded).
2. All layers but one have >= 2 hits; the remaining layer has >= 1 hit (>= 15 hits total).
3. **Delta_s < 0.01 cm** (`Delta_w < 1.0 cm` is already guaranteed by the selection step above;
   0.01 cm is tighter than the 0.05 cm seed-stage cut).

Bug history: an earlier version of `apply_signal_region_cuts()` searched across all raw
candidates for one jointly satisfying Delta_w, Delta_s AND hit-multiplicity, instead of first
collapsing to the single Sec-III-C-designated plane. That let an event pass via a candidate the
paper's algorithm never actually selects. Fixed 2026-09-14 — see DEVIATIONS_LOG.md item 5.

Extra variables the paper mentions but does NOT use in the baseline cut-flow (future handles,
not part of the Sec. IV numbers): Delta_phi(MET, n3); dE/dx per hit (Appendix A).

## STAGE 6 — Backgrounds

### 6a. Pile-up / unassociated hits
- <mu> = 50 average pile-up interactions, beamspot sigma_z = 45 mm.
- Library: minimum-bias events from Pythia8, passed through the Stage-2 detector model.
  Paper target: 125,000 events. Build and document the actual library size used; if smaller
  for compute reasons, state the number explicitly everywhere (never silently claim 125k).
- Use ATLAS public tracking-efficiency numbers (paper ref [33]) — eta-dependence neglected
  within the barrel.

### 6b. Photon conversion background — 10,000 events, generation-time cuts, prompt photons only
- Process at generation time: **`p p > Z(-> nu nu) gamma j`**, generated directly with
  MadGraph5_aMC@NLO — Z forced to decay to neutrinos AT THE MATRIX-ELEMENT LEVEL (not inclusive
  Z + post-hoc filtering). This is what makes the photon a **prompt** photon: it comes from the
  hard 2->3 matrix element itself, not from parton-shower/ISR/FSR radiation, not from pile-up,
  not "idhar udhar ka" — exactly the photon produced in the primary collision.
- **Generation-level (run_card) cuts, set BEFORE running MadGraph, not applied post-hoc:**
  - `pta = 0.5` (minimum photon pT = 0.5 GeV, exact paper value)
  - MET/missing-ET proxy: MadGraph cannot cut directly on true post-shower neutrino-pT-sum in
    the run_card with full precision, so use the loose parton-level heavy-system-pT cut
    (`ptheavy` or equivalent) generously below 200 GeV purely as a generation-time PRE-filter to
    avoid wasting phase space on events that can never pass, then apply the EXACT
    **MET > 200 GeV** cut on the true post-shower neutrino-pT vector sum immediately after
    Pythia8 showering — document explicitly in code comments which cut is the generator
    pre-filter (loose, for efficiency) vs which is the exact paper-fiducial cut (MET>200 GeV,
    computed from truth neutrinos post-shower).
- Fiducial cross section with just pT_gamma>0.5 GeV + MET>200 GeV: ~1 pb (paper value, use as
  cross-check on our generation).
- Beampipe conversion: apply the actual PDG photon-conversion probability (PDG Review of
  Particle Physics conversion-probability tables, paper ref [35], Fig 33.16/33.17) at
  r_conv = 23.5 mm — do NOT substitute an arbitrary flat percentage; if the true conversion-
  probability curve isn't available, get the real curve/formula, don't approximate with a
  round number. Paper's resulting fiducial cross section after conversion requirement: ~10 fb.
- e+/e- energy sharing: **equal sharing** between the two conversion electrons (paper's own
  deliberately conservative choice — real unequal sharing would make background easier to
  reject, so equal sharing is the paper's stated worst-case assumption; keep it for a like-for-
  like comparison, and note explicitly in results that this is conservative).
- Pass the converted e+/e- pair through the SAME Stage-2 detector simulation as signal.
- Overlay with pile-up hits (Stage 6a), then run the full Stage-5 algorithm on the combined hit
  set exactly like signal — never apply a different/looser reconstruction to background.
- Target sample size: **10,000 generated events** (after the generation-level pT_gamma>0.5 GeV
  cut), consistent with your instruction — report the surviving fraction after each cut stage
  (pT_gamma cut -> MET cut -> beampipe conversion -> full reconstruction) as an explicit
  cut-flow table, not just a final number.

## STAGE 7 — Efficiency bookkeeping & validation targets

epsilon_total = epsilon_trig x epsilon_fid x epsilon_reco (paper Eq. 12)

Reproduce as validation targets, in order:
1. Fig. 2 / Fig. 3 shape check (trajectory integrator sanity, Stage 1) — do this FIRST, before
   trusting anything downstream.
2. Fig. 4: single-event hit pattern on the (n3, n2) plane, one clean signal event, no pile-up.
3. Table I: epsilon_trig, epsilon_fid, epsilon_reco for the two benchmark points across their
   Lambda scan.
4. Fig. 5: Delta_s and Delta_w distributions — signal (colored + EW benchmarks) vs pile-up vs
   converted-photon background, log-scale, with Delta_s < 0.01 cm cut line marked.
5. (Stretch) Fig. 6: mQ vs Lambda exclusion/discovery contours at 300 fb^-1 — only after 1-4
   are validated; this needs the full Lambda/mQ grid, not just the two benchmark points.

---

## Build order for this session

1. Environment: MadGraph5_aMC@NLO + Pythia8 + custom quirk UFO model, verified to actually run
   a minimal test process before anything else.
2. Stage 1 trajectory integrator, validated against Fig. 2/3 BEFORE it touches real MG5 output.
3. Stage 0 signal generation, 1000 events, colored quirk mQ=1800 GeV/Lambda=2 keV benchmark.
4. Stage 2 detector hit sim on clean signal (no background yet).
5. Stage 5 plane-finding algorithm on clean signal hits -> reproduce Fig. 4 for one event.
6. Stage 6b photon-conversion background, 10,000 events, full generation-time-cut chain as
   specified above -> reproduce the converted-gamma curve in Fig. 5.
7. Stage 6a pile-up overlay -> reproduce Table I epsilon_reco and the pile-up curve in Fig. 5.
8. Remaining benchmark points (full Table I, then Fig. 6 grid) only once 1-7 are validated.

Every number that deviates from the paper (sample size, any approximation) must be logged
explicitly in a running `docs/DEVIATIONS_LOG.md` as it happens — no silent substitutions.
