# 08 · GNN quirk tracking in the real ATLAS geometry

Started 2026-11-18. Goal: run the GNN quirk reconstruction of the collaboration repository on the same events and the same ATLAS Run 2 inner-detector geometry as 07, then compare coplanarity (07) and GNN on equal terms.

## Source

- Repository: `MirxaWaqarBaig/trackml-quickstart-collab` (GitHub), a fork of the Exa.TrkX TrackML quickstart.
- Pipeline: metric-learning embedding → filter → interaction-network GNN edge classifier → track building, followed by Step 6 evaluation.
- The original work ran on the server, in `/home/rafia/trackml-quickstart-collab`, with TrackML inputs in `/home/rafia/trackml_raw`. Neither folder is on the laptop.
- Branches reviewed 2026-11-18 (latest first):

| date | branch | content |
|---|---|---|
| 2026-08-06 | `coplanarity-method` | Waqar: `coplanarity.py`, coplanarity analysis scripts on top of the plane branch |
| 2026-07-18 | `generalization-test-plane-method` | **plane method**: datasets A–E, generalization tests, source-split Step 6 metrics |
| 2026-07-11 | `module-intersection-cylinder-all-masses` | **cylinder method**: all-mass results, `results_notes/` |
| 2026-07-01 | `module-intersection-my-plane`, `quirk-module-intersection-cylinder` | earlier versions of the two methods |
| 2026-06 and earlier | `quirk-module-intersection*`, `quirk-clean-retry`, `quirk-real-detector-sm-bg`, `quirk-modifications`, `quickstart-without-modification` | development history |

## The quirk hit method in the repository (equations)

Files: `Pipelines/TrackML_Example/LightningModules/Processing/utils/quirk_trajectory.py` and `quirk_intersections.py`.

**1. Trajectory (both branches).** The units are mm, ns, GeV and T. Each pair is integrated with fourth-order Runge–Kutta (RK4), 70 000 steps over 80 ns, with these equations:

- string tension: T = Λ² / (ħc), where Λ is in eV and ħc = 1.973 × 10⁻¹³ GeV·mm, so T is in GeV/mm;
- position: dr/dt = v, with v = c p / E and E = √(m² + p²);
- momentum: dp/dt = q (v × B) ± T c ŝ, where ŝ is the unit vector along the Q–Q̄ separation. The string force has constant magnitude T, a simplification of the relativistic string;
- initial state (toy, not MG5):
  - pair transverse momentum p_T and longitudinal momentum p_z, with p_T jitter 5% and φ spread ±π;
  - opening angle 1.2 rad, with jitter 0.35 rad;
  - initial separation 2 mm;
  - origin jitter 40 mm;
- B = 2 T along z.

**2. Lorentz-force factor: the plane and cylinder branches differ.**

- Plane branch: `dpdt_lor = 0.3 · q · (β × B)`.
- Cylinder branch: `dpdt_lor = 0.000299792458 · q · (v[mm/ns] × B)`.

The correct value is dp/dt = 0.2998 GeV/(T·m) × q (v × B), with v in m/ns. For β = 1 and B = 2 T this is 0.18 GeV/ns. The cylinder expression gives exactly this. The plane expression gives 0.60 GeV/ns, so its magnetic bending is about 3.3 times (= 1/0.2998) too strong. Any plane-branch dataset made with this code needs regeneration.

**3a. Plane method (`intersect_track_with_modules`).**

Every detector module is a finite plane with:
- centre C;
- normal n;
- in-plane axes u and v;
- half-widths h_u (`module_maxhu`) and h_v (`module_hv`).

For each trajectory segment A → B:
1. A KD-tree on the module centres selects candidate modules.
2. The crossing parameter is t = n·(C − A) / n·(B − A), skipped when |n·(B − A)| < 10⁻¹⁰.
3. The crossing point is F = A + t (B − A), kept when 0 ≤ t ≤ 1.
4. F is a hit if |(F − C)·u| ≤ h_u and |(F − C)·v| ≤ h_v.
5. Repeat crossings of the same module within 5 steps count once. At most 150 hits are kept per track.

Note: trapezoidal end-cap modules are treated as rectangles of the larger half-width.

**3b. Cylinder method (`intersect_track_with_cylinders_and_modules`).**

1. Solve x² + y² = R² for the 10 TrackML barrel layers.
2. Project the crossing into the local frame of the nearest real module.
3. Apply the same |u| ≤ h_u, |v| ≤ h_v acceptance.

**4. Background.** TrackML SM events with p_T > 0.5 GeV, at most 500 hits per event, mixed with one quirk pair per event. The detector is the TrackML generic detector (`detectors.csv`), not ATLAS.

## Results recorded in the repository (read from the files)

| method | dataset | signal efficiency | fake rate | source |
|---|---|---|---|---|
| plane | AB, `ypid` (Step 6) | 61% (quirk 68%, anti-quirk 54%) | 10.5% | `plane_AB_ypid_step6.log` |
| plane | AB, `ytruth` (Step 6) | not printed; the runs look unfinished | — | `plane_AB_ytruth_*step6*.log` |
| cylinder | AB, trained masses | 90–91% | 5–6% | `results_notes/step6_*` |
| cylinder | C, unseen mass (AB training) | 41% | 32.5% | `results_notes/ABDE_v2_generalization_summary.txt` |
| cylinder | edge filter, 500 events | edge efficiency 96.7%, purity 18.4% | — | `results_notes/gnn_edge_filtering_*` |

The weak point is generalization to unseen (m_Q, Λ). The toy Λ range is 700–1100 eV. The coplanarity reach in 07 lies at Λ ≈ 2–5 keV.

## Plan for 08 (method unchanged, geometry and events from 07)

1. **Geometry.** Replace `detectors.csv` with the 07 ATLAS Run 2 geometry: barrel layers and pixel/SCT disks. The modules will be written as plane-method rows (centre, n, u, v, half-widths) from the 07 element list (`07_atlas_real_geometry/sim/detsim07.py`).
2. **Signal.** Use the 07 quirk trajectories (MG5 + Pythia events, the 07 integrator) instead of the toy simulator. Hits come from the plane intersection of those trajectories with the ATLAS modules. Check: the hits must agree with the 07 station hits for the same events.
3. **Background.** Use the 07 converted photons and minimum-bias pile-up (μ = 0 / 20 / 50) instead of TrackML events, so that the coplanarity and GNN numbers use the same background.
4. **Training and test.** Use several (m_Q, Λ) points per channel near the 07 reach, with held-out points for generalization.
5. **Comparison.** On the same events, report coplanarity and GNN signal efficiency, background and reach (GeV).

## Inputs expected in this folder

`data/` is for the files copied from the server. Expected contents:
- the repository checkout, or the branch to use;
- `trackml_raw/` (`detectors.csv`, `train_all/`);
- the generated datasets (`datasets/plane_*`);
- trained checkpoints (`artifacts/`).

What each item is will be documented here once it is in place.

## Open items

- Which method to carry forward: plane, cylinder, or both. The cylinder branch has the correct Lorentz-force factor.
- GPU: the laptop has an RTX 4050 (6 GB) and a `trackml-quickstart` conda environment. The server GPU status is unknown.
- Whether Waqar's `coplanarity-method` branch is to be used.
