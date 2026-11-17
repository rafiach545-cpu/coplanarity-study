# 07 — ATLAS real geometry, material and backgrounds (started 2026-11-15)

Stage B of the publication plan: replace the 8 infinitely thin barrel layers of the reproduction (Knapen et al., arXiv:1708.02243) with the ATLAS Run 2 Inner Detector. This means end-caps, material, timing, efficiency and field, all taken from published references. The same detector is then used for new background processes. GNN work is not part of this folder.

**Name in the simulation matrix (2026-11-17):** this folder is **Stage 2 · Run 3 · ATLAS** (13.6 TeV, 332 fb⁻¹). Its reference is **Stage 1 · Run 3 · Ideal**: the 2k sample in `06_publication/S2_13p6TeV_run3_knapen_noPU_cop`, called "Stage 2" in older files, and the 10k sample in `signal/runs/large_ideal`. Tags: `S2_Run3_ATLAS`, `S1_Run3_Ideal`, `S1_Run3_Ideal_2k`. The full matrix is in `RESULTS_07_LARGE_SAMPLES.md`.

**Rule:** every number comes from a saved reference. `references/REFERENCES.md` lists each paper, its local file, and which number is taken from which table or section. The CSVs repeat the reference ID on every row and mark the value VERIFIED, DERIVED or CONFLICT.

## Folders

| Folder | Content |
|---|---|
| `references/` | `REFERENCES.md` (R1–R14, MG), `MD5SUMS_pdf.txt`; `pdf/` and `text/` hold local copies of the papers and are not pushed (third-party, `.gitignore`) |
| `geometry/` | `atlas_run2_id_geometry.csv` (barrel layers, pixel disks, SCT rings, beam pipe, field; one row per element with its source), `atlas_run2_id_material.csv` (X/X0 per element with source), `atlas_run2_geometry.py` (reads the CSV; crossings of straight lines and of sampled trajectories) |
| `sim/` | `detsim07.py` (elements, helix propagation through barrel + disks, electron material effects, hit response incl. end-caps, pixel merging, pile-up sampling); `cop07.py` (paper COP on 8 per-hit stations, D1) |
| `tests/` | T01 geometry coverage (R3 space points, module counts); T02 propagation vs Stage 2 helix / electron code and an independent Boris integrator; T03 end-cap hit response, re-smearing, disk merging, station COP on synthetic planes; T04 COP speed-ups give exactly the plain-loop candidates; T05 stage2 configuration reproduces the Stage 2 background event by event. Logs in `logs/` |
| `tables/` | test and step outputs (`T01_coverage_vs_eta.csv`, `M01_conversion_*.csv`) |
| `DECISIONS.md` | D1–D5 with reasons and references |
| `backgrounds/` | `M01_conversion_probability.py` (D2); `BACKGROUND_CANDIDATES.md` (which processes can reach the signal region and why, with numbers); `xsec_mg5/` with the MG5 cross sections of Z(νν̄)+j and W(ℓν)+j at 13.6 TeV (`X01_*`); `logs/` |
| `signal/` | `SIGNAL_REDO.md`: which parts of the signal must be recomputed (no new cross sections or generation; propagation, reconstruction and reach yes) |
| `reach/` | `R01_reach_07.py` (Stage 2 reach method), `R02_results_summary.py` (all numbers in one file), `R00_postprocess.sh` (R01 → plot data → figures → T11, T09 → R02), `R00_wait_final.sh` |
| `FIGURES_ROOT_2026-11-17/` | ROOT figures G01–G10 of the large-sample study, with data and provenance (own README) |
| `RESULTS_07_LARGE_SAMPLES.md` | results of the large-sample study: samples, end-cap gain checks, reach, contour edges, background, reproducibility, open points, tests |
| `compare/` | ideal vs ATLAS (X02), laptop vs server (X01), contour edges (X03), η acceptance (X04), end-cap flags (X05), end-cap plane composition (D01); `X02_SUMMARY.md`; figure X02 |

## Status

| Step | Status |
|---|---|
| References collected and checked (R1–R14) | done |
| Geometry CSV: barrel, pixel disks, SCT rings, all values verified | done |
| Material CSV (beam pipe, IBL, pixel, SCT, disks, PDG X0, 7/9 rule) | done; IBL conflict 1.88% vs 1.5%; Run 2 beam pipe only partly known (DERIVED) |
| Geometry code + test T01 | done, T01_PASS |
| Background candidates + MG5 σ (Z(νν̄)+j 10.8 pb, W(ℓν)+j ≤ 12.2 pb) | done (LO, parton level) |
| Module tilts and gaps, field map, dE/dx in the integrator, SCT 01X timing, hit efficiency and noise | to do |
| Large signal samples (10k generated per point) through the 07 geometry; reach; ROOT figures | **done (2026-11-17), from the server runs** `signal/runs/large_atlas` and `large_ideal` (all Λ 0.1–25 keV): `RESULTS_07_LARGE_SAMPLES.md`, `compare/X02_SUMMARY.md` (ideal vs ATLAS, McNemar, crossings), `tables/R01_*`, `R02_results_summary.md`, `X0*`, `D01_*`, `FIGURES_ROOT_2026-11-17/` (G01–G10), `compare/FIGURES_X02/`; tests T08–T11 PASS. Laptop runs superseded (`signal/runs/atlas_large_laptop_INTERIM_2026-11-17`, kept for the reproducibility check). EW 1200 GeV generated, propagation pending |
| Other backgrounds B02–B04; more C01 events (lower upper limit) | to do |
| Decisions D1 (ATLAS-like stations, R14), D2 (conversion from material), D3 (background order) | done, `DECISIONS.md` |
| M01: conversion probability of the Z+γ photons from the material | done: before the IBL 0.40% (all) / 0.27% (\|η\| < 1.8) vs flat 1%; IBL 2.8% / 2.2%; `tables/M01_*`, `backgrounds/logs/M01_*` |
| Detector simulation + station COP (`sim/`) and tests T01–T07 | done: all PASS (`logs/T0*.log`); T06 SCT settings D4, T06e C01 regression, T07 G01 signal reproduces Stage 2 on 2949 (event, Λ) rows of 6 samples |
| C01: Z+γ conversions through the 07 geometry + material + stations + pile-up (D3 step 1) | done (2026-11-16). SCT z = 0, 332 fb⁻¹: N = 0.34 / 27.0 / 69.2 / 74.6 (± 0.1 / 2.7 / 4.4 / 4.6) at μ = 0 / 20 / 50 / 60, against Stage 2 0.25 / 9.2 / 16.4 / 16.7. The barrel-like part matches Stage 2; the increase comes from the end-caps. SCT z = 1.16 mm: 0 at every μ. SCT A580 (ATLAS intrinsic, D4): 0 / 0.08 ± 0.04 / 0.34 ± 0.24 at μ = 0 / 20 / 50 (μ = 60 not run, user decision). T04 (exact speed-ups) PASS. `backgrounds/BACKGROUND_CANDIDATES.md` E, `tables/S01_*`, `tables/S02_*` |

## Environments

- Python: `/home/rafia/venvs/f6fast/bin/python`
- MG5 3.7.3: `/home/rafia/hep_tools/MG5_aMC_v3_7_3`, with the hep env first in PATH
- Pythia8 8.312 (hep env), with `PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc`
