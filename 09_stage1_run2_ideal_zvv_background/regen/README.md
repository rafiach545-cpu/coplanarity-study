# Signal regeneration with DOP853 (prepared 2026-11-22, not run)

## Why

The fixed-step RK4 used so far (300 steps per period) is not converged for Λ ≳ 4 keV:
- In the G07 impact test (same events), 0–7 of 20–48 events per point change their signal-region decision between the production step and DOP853.
- k changes, for example:
  - EW 800 GeV, 10 keV, Z1160: 3 → 5;
  - EW 600 GeV, 5 keV: 5 → 3.

Every signal sample is therefore regenerated with the error-controlled DOP853:
- integrator: `03_trajectory_sim/quirk_trajectory_dop853.py`;
- rtol = 1e-10;
- atol = 1 nm for positions and 1e-10 GeV for momenta.

## What changed in the code

All changes are opt-in. Without `QUIRK_INTEGRATOR`, every earlier script and result is unchanged.

- **`03_trajectory_sim/quirk_trajectory_dop853.py`** (new): a numba port of scipy's DOP853.
  - It uses the same coefficients (stored in `quirk_dop853_coefficients.npz`, checked against scipy 1.18.0), the same step control and the same 7th-order dense output.
  - Layer crossings (barrel radii and disk planes) are refined with the dense output: 8 coarse points per step, then 64 fine points in every sub-interval that has a crossing.
- **`04_detector_sim/trajectory_to_hits.py`**:
  - `QUIRK_INTEGRATOR=dop853` makes `simulate_quirk_hits` use DOP853.
  - The 20M-step ceiling of the RK4 path is then not applied.
  - The time range (t_max) is unchanged.
- **`09/g4/G07_dt_impact.py`**: mode `S10` (the production switch) and `--out`.
- **`09/B08_signal_cleaning_scan.py`**: `--hepmc-glob` and `--tag`, so it can run on the 13 TeV Stage 1 HepMC files.
- **`regen/launch07_dop853.py`**: runs 07's `G01_signal_07.py` unchanged, with DOP853 and the 07 geometry's crossing surfaces (8 barrel radii, and for atlas 40 disk planes).

## Checks done on the laptop

| Check | Result |
|---|---|
| G09 (A) exact helix, 20 pairs | max 0.017 µm |
| G09 (B) exact 1D string, 1 and 4 keV | crossing times ≤ 3e-5 ps; turning point −0.001 µm |
| G09 (C) G06 conservation at B = 0, 0.1–4 keV | E_NG ≤ 2e-8 · Q; L_NG ≤ 3e-8; P_NG ≤ 4e-8 |
| G09 (D) 4 events at 4 keV, B = 2 T, 5 ns | ≤ 0.07 µm from scipy DOP853 at rtol 1e-13 (RK4 at dt/64: 3–11 µm) |
| rtol 1e-10 vs 1e-11 on the full G07 subset (9 points × 2 σ_z) | 0 SR flips, 0 fiducial flips |
| Production switch (`S10`) vs the G07 wrapper (`D10`), 16 EW 800 events at 7 and 10 keV | identical to the last digit (fid, final, Δs, Δw, crossings) |
| 07 launcher: DOP853 reaches the forked workers | with a test stop at 0.3 ns, every event has 0 hits |
| Stage 1 13 TeV full-event B08 (EW 800 GeV, 9 events, 4 and 10 keV) | runs; 9 s |

## Setup on the server

1. **Code.** Nothing is committed yet. The new and changed files listed above must be either committed and pulled, or copied with `rsync`:
   - `03_trajectory_sim/quirk_trajectory_dop853.py` and `quirk_dop853_coefficients.npz`;
   - `04_detector_sim/trajectory_to_hits.py`;
   - `09_stage1_run2_ideal_zvv_background/{B08_signal_cleaning_scan.py,g4/G07_dt_impact.py,regen/}`.
2. **Python.** Use the env `g4` (SERVER.md). Steps A and C also need scipy and pyyaml; `cop07` and `analysis_config` import them:
   ```bash
   conda activate g4
   python -m pip install --index-url https://pypi.org/simple scipy==1.18.0 pyyaml
   ```
3. **Inputs.** The A and C event lists are in git. The full-event steps also need HepMC files from the laptop:
   - B: 461 MB;
   - D: 1.6 GB.
   ```bash
   rsync -av laptop:/home/rafia/hep_tools/figure6_full_v1_runs/EW_{100,200,400,600,800,1000}gev/Events/run_fig6 $HEP_TOOLS/figure6_full_v1_runs/...   # B
   rsync -av laptop:/home/rafia/hep_tools/07_large_runs/EW_{100,400,800,1200}gev_c0? $HEP_TOOLS/07_large_runs/                                        # D
   ```
4. **Reproduction check (minutes).** It must agree with the laptop file `g4/out_G01/G07/EW_800gev_L7-10_FS10_n16.jsonl` event by event:
   ```bash
   cd $COPLANARITY_BASE/09_stage1_run2_ideal_zvv_background/g4
   NWORKERS=4 python G07_dt_impact.py EW_800gev 7,10 S10 --nmax 16 --out /tmp/regen_check
   ```

## Commands

```bash
cd $COPLANARITY_BASE/09_stage1_run2_ideal_zvv_background/regen
export HEP_TOOLS=$HOME/hep_tools PYF=$(which python) PYG4=$(which python) NW=8
nohup ./regen_all.sh A > logs/A.out 2>&1 &     # then B, C, D (or "all"); the steps are independent and can run side by side
```

Every job appends and resumes, except B08, which writes one CSV per mass at the end and keeps a `.partial` checkpoint. Running steps in parallel means `NW` workers per running step.

## Cost

The per-event times are DOP853 to t_max, measured on the laptop with `S10`, 5 events per sample at Λ = 0.1 / 1 / 4 / 10 / 25 keV:

| Λ (keV) | Seconds per event |
|---|---|
| 1 | ~0.01 |
| 4 | ~0.2 |
| 10 | ~1.0–1.3 |
| 25 | ~5–7 |

The time grows about as Λ^1.8. Λ = 0.1 keV is up to ~5 s for EW 100 GeV.

| Step | Events (triggered) | Λ values | Core-hours (estimate) | Output |
|---|---|---|---|---|
| A: 13 TeV 8-layer, quirk hits | 1 156 | 17 (0.1–35 keV, including 30 and 35, which had no RK4 result because of the step ceiling) | ~16 | ~40 MB jsonl |
| B: 13 TeV full events, EW | 721 | 17 | ~12 | ~30 MB csv |
| C: 13.6 TeV, stage2 + atlas | 7 209 × 2 | 15 (low, mid, high_a as 07) | ~120 | ~200 MB jsonl |
| D: 13.6 TeV full events, EW | 2 716 | 5 (0.1, 1, 4, 10, 25) | ~9 | ~60 MB csv |
| **Total** | | | **~160; plan for ~250 with margin** | **< 1 GB** (+ 2.1 GB HepMC inputs) |

Notes on the cost:
- At 32 cores this is about 8 hours of wall time.
- Memory is below 1 GB per worker. The DOP853 output keeps only step ends and crossing brackets; the output arrays are allocated lazily, up to 20M points.

## Not covered

- **Colored quirks as full events (B05/B08).** No code exists: B08 reads only EW quirks (PDG 9000011) and has no quirk-hadron handling. Colored 13 TeV is covered by step A only (quirk hits, as in Stage 1).
- **13.6 TeV above 25 keV.** 07's `G01_signal_07.py` accepts only the bands low, mid and high_a.
- **Downstream.** The reach and figure scripts read the old file locations. After the rerun they must be pointed at `regen/out` and the new `B08_*_dop853_*` files. The frozen 06 graphs are not touched.
