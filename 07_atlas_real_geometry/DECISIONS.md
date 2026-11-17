# 07 decisions log

## D1 (2026-11-15): hit counting and fiducial rule with end-caps follow ATLAS

**Question:** with end-cap disks, which "8 layers" does COP require?

**What ATLAS does** (R14 = arXiv:2605.07585, Table 1 and Sec. 4):

- ATLAS counts silicon measurements N_Si = Pixel + SCT clusters on any measurement surface, barrel layer or end-cap disk alike. An SCT module gives one cluster per side.
- A **hole** is a missing expected cluster on a measurement surface between the innermost and outermost measurements of the track.
- Track quality, Loose working point: \|η\| < 2.5, N_Si ≥ 8, ≤ 1 pixel hole, ≤ 2 silicon holes.
- Track quality, Tight Primary: N_Si ≥ 9 (\|η\| ≤ 1.65) or ≥ 11, 0 pixel holes.
- R14 places the IBL at r = 33.5 mm, the same as R2. R1 gives 33.25 mm.

**Decision** (as first written; item 2 refined below):

1. **Element crossings:** a quirk's crossings are taken in time order over all silicon elements (barrel layers, pixel disks, SCT rings), using `geometry/atlas_run2_geometry.py`.
2. **Stations:** the COP "layers" become 8 **stations** per quirk: pixel stations 1–4 are the first four distinct pixel elements crossed, and SCT stations 5–8 are the first four distinct SCT elements crossed. With the barrel only, the stations are exactly the 8 barrel layers. **Stages 1–2 are therefore reproduced unchanged as a special case**, and this must be checked as a test.
3. **Fiducial:** both quirks have all 8 stations, \|η\| < 2.5 (R14 acceptance), and t < 25 ns (the timing rule will be refined with R5 01X).
4. **Signal region:** unchanged in form (R10). Hits from both quirks are counted per station: 2 hits in all but one station, ≥ 1 in the remaining one, Δs < 0.01 cm, Δw < 1.0 cm.
5. **Later (not now):** a Loose-like hole count (≤ 1 pixel, ≤ 2 silicon holes per quirk) once efficiency and dead modules are added.

**Refinement of item 2 (2026-11-15, implemented in `sim/cop07.py`):**

- **Problem:** with one station list per plane, no plane was found in the barrel / end-cap transition (T03 (e), \|η\| = 1.4 and 1.9). The reason is that the two tracks of a pair cross different elements as their k-th measurement.
- **New rule: each hit gets its own station** from the straight line PV → hit. The number of pixel (SCT) elements this line crosses before the hit, + 1, is the pixel station 1–4 (SCT station 5–8). This is "the k-th measurement along the track".
- **Seed-pair longitudinal cut:** \|Δz\| < 2 cm for two barrel hits (the paper), \|Δr\| < 2 cm for two disk hits, both for a barrel–disk pair. Everything else is the paper's algorithm unchanged.
- **Checks:**
  - With the barrel only, every hit's station is its layer: T05 reproduces Stage 2 event by event at μ = 0 and 50.
  - Synthetic pairs crossing the same 8 elements are always found (T03 (e): 38/38).
  - Pairs whose two tracks cross different elements at a boundary pass only partly (5/11). This is an acceptance effect, to be measured on the signal.

## D2 (2026-11-15, decided by the user): conversion probability from the material

**Change:** the flat 1% at the beam pipe (professor's earlier guidance; R10: ~1 pb → ~10 fb) is replaced by a layer-by-layer probability.

- **Formula:** P_i = Π_{j<i} exp(−7 t_j / 9) × [1 − exp(−7 t_i / 9)] (R7 Eq. 34.32).
- **Thickness per crossing:** t = (x/X0)_normal / \|cos α\|, where α is the angle between the photon direction and the normal of the element (barrel: sin θ; disk: \|cos θ\|).
- **Values:** x/X0 from `geometry/atlas_run2_id_material.csv`:
  - IBL nominal: 1.88% (R2); variation 1.5% (R6);
  - pixel barrel: 10.7%/3 per layer (R3);
  - SCT barrel: 2.96% per layer (R3);
  - SCT disk: 3.75% (R3);
  - pixel disk: no published number found, so the pixel barrel value is used (INFERRED);
  - beam pipe: Be wall 0.227% (DERIVED; polyimide tapes not included). The Run 1 pipe (0.45% to r = 36 mm, R3) is kept as a variation.
- **Missing from the model:** passive tubes (IPT, IST, PSF, PST), because no published X/X0 number was found for them (R6 gives only positions and the IPT thickness).

## D3 (2026-11-15): order of the background work

Chosen by expected size and by how much existing code each step reuses:

1. **Z(νν̄)+γ+j with the real material and end-caps.** The existing photons are reused and no generation is needed. This step also validates the new detector simulation against Stage 2.
2. **Z(νν̄)+jets,** the dominant MET background (R9), with all particles: conversions of π⁰/η photons in jets (B1), Dalitz pairs (B2), K_S/Λ (B3).
3. **W(→τν)+jets** (R9), for hadronic τ decays (B4).
4. **Hadronic interactions in the material** (B5): needs a hadronic model.
5. **Cosmic-ray muons** (B6).
6. **tt̄, single top, diboson, multijet:** small in R9; σ estimate only, unless steps 2–3 show a problem.

**Started first:** M01, the conversion probability of the 13.6 TeV Z+γ photons from the material, compared with the flat 1%.

## D4 (2026-11-16): SCT resolution settings; ATLAS intrinsic becomes the main one

**What the references say:**

- **R3 Table 4.1** (intrinsic accuracy, µm):
  - pixel layers 10 (R-φ) / 115 (z); pixel disks 10 (R-φ) / 115 (**R**);
  - SCT barrel 17 (R-φ) / 580 (z); SCT disks 17 (R-φ) / 580 (**R**);
  - TRT 130.
- **R1 Table 1:** IBL 50 × 250 µm, intrinsic 10 × 60 µm, r = 33.25 mm.
- **R10 Sec. III A:** "for the pixel detector we use the pixel size rather than the resolution and for the SCT we conservatively assume a resolution of twice the intrinsic accuracy". This is where 34 µm / 1.16 mm comes from.
- **Not used:** other IBL values (8 × 40 µm in arXiv:1811.08780, 10 × 75 µm in arXiv:2307.03925, both theses) and SCT 16 µm (PoS proceedings). They are secondary; the official R1 and R3 values are kept.

**Decision:** three SCT settings, used for both signal and background.

| Setting | SCT R-φ | SCT long direction (barrel z, disk R) | Role |
|---|---|---|---|
| **A580** | 17 µm | 580 µm | **main: ATLAS intrinsic** (R3, R1) |
| Z1160 | 34 µm | 1160 µm | Knapen 2× (R10), comparison with the paper |
| Z0 | 34 µm | 0 | upper bound (Stage 1–2 "σ_z = 0") |

- **End-caps:** on SCT disks the long direction is R. The code already did this, and T06 (a) checks it: σ is applied to R at fixed φ, with z = the ring's z. "SCT z = 0" (Z0) on the disks therefore means no R smearing.
- **Pixels: unchanged in all settings.** They keep the pitch quantisation, as in R10 and Stages 1–2.
  - This gives pitch/√12 = 14.4 µm (R-φ) and 115.5 µm (z, R) for the pixel layers and disks; the second equals the intrinsic 115 µm.
  - The IBL gets 14.4 / 72 µm against the intrinsic 10 / 60 µm.
  - These are 10–40 times smaller than the SCT long resolution that drives the background, so the pixel model is not changed (Stage 2 stays reproducible).
- **Code:** `sim/detsim07.py` SCT_LONG_CM and SCT_RPHI_FACTOR; resmear() now also re-smears R-φ when the R-φ factor changes.
- **Tests:**
  - T06 (a)–(d): widths 17 / 580 µm, Z0 / Z1160 bit for bit as before, resmear between all settings exact.
  - T06 (e): C01 production rows reproduced exactly.
  - T03 rerun: PASS.
- **Results (2026-11-16):** C01 background with A580: 0 / 0.08 ± 0.04 / 0.34 ± 0.24 events (332 fb⁻¹) at μ = 0 / 20 / 50. μ = 60 was not run for A580 (user decision, 2026-11-16).

## D5 (2026-11-16/17): large signal samples, reach method, background limit, figures

- **Samples (user, 2026-11-16):** 10 000 generated events per mass point for the 13 Stage 2 points (EW 100–1000 GeV, colored 600–2400 GeV), made by `signal/G02_large_samples.py` with the unchanged L01 (5 MG5 runs of 2000, Stage 2 cards, new seeds 700000 + 100000·EW + 40·m + chunk) and L02 (event_id = 100000 + index). All 65 runs ok; cross sections and trigger fractions agree with Stage 2 (largest pull 2.7σ, colored 600 GeV ε_trig).
- **Propagation:** G01 in the atlas configuration, all three SCT settings of D4, bands mid, low and high_a as Stage 2; per-event seeds from event_id (T08 PASS: unchanged results for Stage 2 inputs).
- **Reach:** `reach/R01_reach_07.py` uses the Stage 2 method unchanged (S2_05 grid and reach, S2_09 thresholds). T09 PASS: its functions reproduce S2_N_grid_300fb.csv, S2_reach.csv and S2_reach_with_background.csv exactly.
- **Background limit when no photon passes:** the C01 background has three conversion regions with different photon weights w_i. With 0 passing in every region, the 95% upper limit is b ≤ 3·max_i w_i, i.e. the largest per-region S01 limit (1.29 events at 332 fb⁻¹). Summing the per-region limits (2.1 events) would over-cover and made the μ = 0 reach worse than μ = 20. The reach is also given with b = central value ("central b").
- **β:** read as the quirk velocity β = |p|/E (as in S2_10). Distributions per mass point in G02.
- **Figures:** new folder `FIGURES_ROOT_2026-11-17/`, drawn with ROOT 6.40 (style and helpers of the 06 ROOT figures, unchanged); contour lines with the 06 method (T10 PASS). Existing figures are not changed.
- **Material cross-check (R12):** M01 gives 20% conversion probability for |η| < 1 (R12: "about 20% at low |η|"), but 38% at |η| ≈ 2.3 against R12's "up to about 65%". Forward services and supports are not in the material model. The end-cap part of the background may therefore be underestimated.
- **Grid edge (2026-11-17):** the Stage 2 reach method only finds crossings between grid masses. `R01_reach.csv` therefore has two extra columns: `N_max_at_highest_mass_used` (largest N at the highest mass over the rows the method uses) and `reach_beyond_grid` (True if that N is at or above the threshold, so the true reach is at or above the highest mass and the quoted value is a lower bound). The method itself is unchanged; T09 still PASS. The only interim case is EW Z0 at 355 fb⁻¹ (exclusion).
- **s_req vs μ is not monotonic:** for A580 and Z1160 at μ = 0, no MC photon passes, so b = UL = 1.29 and n_obs = 1, giving s_req = 4.0. For A580 at μ = 20 and 50, b = 0.08 and 0.34, n_obs = 0, giving s_req = 3.0. This follows from the S2_09 rule n_obs = round(b) and is written in the G06/G07 captions.
- **Integration failures:** 0.86% of event–Λ pairs (Stage 2: 1.06% on the same Λ), always "MIN_STEPS_PER_PERIOD not reached". They are counted as not fiducial, as in Stage 2 (`tables/R02_integration_failures.csv`).
- **Server runs are the result (2026-11-17, user):** the large samples were propagated on the server in the atlas and stage2 (ideal) geometries; all 07 tables and figures are built from `signal/runs/large_atlas`. The laptop G02 propagation was stopped. Its rows are not bit-identical to the server rows: 2.6% of rows differ in a discrete field, with no net direction. Each machine reproduces itself exactly, so the cause is floating-point arithmetic, which differs between machines. The difference is taken as a numerical-reproducibility systematic: ≤ 4 GeV on m_max (X01c).
- **EW 1200 GeV added (2026-11-17, user):** for ATLAS Z0, N at the highest EW mass (1000 GeV) is 2.90, just below 3, so the EW reach sits at the grid edge. The same G02 gen/ext was used, with seeds 848000–848004. `R01_reach_07.py` uses a point only when all its band files exist (`with_runs`).

## D6 (2026-11-17, decided by the user): names from the simulation matrix

| Stage | Run | Geometry | √s | L | Where |
|---|---|---|---|---|---|
| 0 | Paper | Ideal | 13 TeV | 300 fb⁻¹ | `05_coplanarity_analysis` |
| 1 | Run 2 | Ideal | 13 TeV | 139 fb⁻¹ | `06_publication/S1_13TeV_139fb_knapen_noPU_cop` |
| 1 | Run 3 | Ideal | 13.6 TeV | 332 fb⁻¹ | `06_publication/S2_13p6TeV_run3_knapen_noPU_cop` (2k); `signal/runs/large_ideal` (10k) |
| 2 | Run 2 | ATLAS | 13 TeV | 139 fb⁻¹ | not done |
| 2 | Run 3 | ATLAS | 13.6 TeV | 332 fb⁻¹ | this folder, `signal/runs/large_atlas` |
| 2 | Run 2 / Run 3 | CMS | 13 / 13.6 TeV | 139 / 332 fb⁻¹ | not done |

- **What changed:** docs, table columns and labels, and the 07 figures (G01–G10, X02) now use these names. Text uses "Stage 2 · Run 3 · ATLAS"; figure legends use "S2 · Run 3 · ATLAS"; tags in tables and files are `S2_Run3_ATLAS`, `S1_Run3_Ideal`, `S1_Run3_Ideal_2k`.
- **What did not change:** folder names and the frozen 06 graphs (user choice).
- **Older entries:** in the entries above (D1–D5), "Stage 2" means Stage 1 · Run 3 · Ideal (2k), and "07" means Stage 2 · Run 3 · ATLAS.
- **Renamed table columns:**
  - `n_fid_stage2` → `n_fid_barrel_rule` (in the raw jsonl files the field is still `fid_stage2`);
  - `m_max_stage2_GeV` → `m_max_S1_Run3_Ideal_2k_GeV`;
  - X02 setups `ideal` / `atlas` / `stage2` → `S1_Run3_Ideal` / `S2_Run3_ATLAS` / `S1_Run3_Ideal_2k`.
- **Background value (2026-11-17, decided by the user):** the reach uses the central MC background, with b = 0 when no MC photon passes. The MC 95% upper limit (1.29 events ATLAS, 0.25 events Ideal) is only a systematic variant. The earlier D5 rule ("b = UL if 0 passed") made the A580 μ = 0 reach lower than the μ = 20 reach, which is unphysical. Implemented in R01 (columns `b_used` / `s_excl` = central, `b_UL` / `s_excl_UL` = variant) and in X08 (variants "central b" and "UL if 0 passed (systematic)").
- **Headline setting (2026-11-17, decided by the user):** A580 (realistic SCT). Z0 is shown only as the best case (perfect SCT z), always with its background. Each geometry is compared with its own background; the Ideal A580 background was run with C01 stage2 at μ = 0/20/50 (`backgrounds/C01_chain_stage2_A580.sh`).

