# Figure 6, high band (Λ = 15–35 keV): how to run

This bundle runs the missing upper part of Figure 6 (arXiv:1708.02243) on another machine. Λ = 0.1–10 keV is already done; those results are included.

## Requirements

- Linux, Python ≥ 3.10.
- Packages: `numpy pandas scipy pyyaml matplotlib numba`.
  - Install with `pip install numpy pandas scipy pyyaml matplotlib numba`, or use conda.
- RAM: at 30–35 keV one trajectory can need about 2–3 GB. Use NWORKERS ≤ (free RAM in GB) / 3. Examples: a 32 GB machine → 8–10 workers; a 64 GB server → about 20.

## Run

```bash
tar xzf FIG6_HIGH_BAND_BUNDLE_2026-10-17.tar.gz
cd coplanarity_study
bash RUN_FIG6_HIGH_BAND.sh 8          # 8 = number of workers
```

The script does three things:

1. **Validation.** It reruns 12 events of 5 points with the fast (numba) integrator and compares every value with the stored results. It must print `VALIDATION PASSED`; otherwise it stops.
2. **High band.** It runs 11 mass points at Λ = 15, 20, 25, 30, 35 keV. Each event is written to `.../logs/F6_<point>_high_events.jsonl` as soon as it finishes. If the run stops, rerun the same command and it continues where it stopped.
3. **Results.** It rebuilds the grid (`fig6/F6_N_grid.csv`), the reach table (`fig6/F6_reach.csv`) and the figures (`FINAL_FIGURES/F6_fig6`, `F6_kfactor`).

Time: with numba, about 1–2 minutes per event per core for the five high-Λ values. That is about 900 events in total, so roughly 2–4 hours on 8 cores.

To use a specific Python, run `PYTHON=/path/to/python bash RUN_FIG6_HIGH_BAND.sh 8`.

## Send back

- `05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/logs/F6_*_high_events.jsonl`
- `05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/fig6/`
- `05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/FINAL_FIGURES/F6_fig6/` and `.../F6_kfactor/`

## Notes

- **Paths.** The code reads `COPLANARITY_BASE`, which the run script sets to the unpacked folder, so the code runs from any directory.
- **Fast integrator.** `03_trajectory_sim/quirk_trajectory_numba.py` is a compiled copy of the production integrator. On this laptop it was checked to be bitwise identical: trajectories, and 396 pipeline rows with 0 differences. It was 15–37× faster.
- **Figure caption.** After the run, the note "Λ > 10 keV: not computed" in the figure caption must be updated by hand. The hatch disappears automatically.
