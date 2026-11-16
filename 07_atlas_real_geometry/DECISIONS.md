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
