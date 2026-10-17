# Task: compute the Λ = 15–35 keV part of Figure 6 (arXiv:1708.02243 reproduction)

You are running an existing, validated physics pipeline on a new machine. **Do not change any physics, selection or analysis code.** Your job is to set up the environment, run the validation and the production, check the outputs, and report the results.

## 1. Context

- **What Figure 6 is.** Contours of 3 (exclusion) and 5 (discovery) expected signal events at 300 fb⁻¹ in the plane of quirk mass m_Q vs string tension Λ, for colored and EW quirks.
- **What is done.** Λ = 0.1–10 keV is computed. Those per-event results are in the repo.
- **What is missing.** Λ = 15, 20, 25, 30, 35 keV (the "high band"). It was not run on the original laptop for two reasons: it is slow, and one trajectory at 30–35 keV needs about 2–3 GB of RAM, which killed the 8 GB laptop (OOM).
- **Integrator.** A numba-compiled copy of the production integrator exists: `03_trajectory_sim/quirk_trajectory_numba.py`. It was validated as bitwise identical to the production integrator and is 15–37× faster. It is enabled with the environment variable `FAST=1`.

## 2. Get the code

```bash
git clone https://github.com/rafiach545-cpu/coplanarity-study.git coplanarity_study
cd coplanarity_study
git checkout transfer-2026-10-02          # NOT master
```

Everything needed is tracked on this branch. You do not need any large raw files (event generation, background chunks), and you should not try to recreate them.

## 3. Environment

- Linux, Python ≥ 3.10.
- Install the packages:

  ```bash
  python3 -m venv venv && . venv/bin/activate
  pip install numpy pandas scipy pyyaml matplotlib numba
  python -c "import numba, numpy, pandas, scipy, yaml, matplotlib; print('ok', numba.__version__)"
  ```

- The code finds its files through `COPLANARITY_BASE`, the absolute path of the repo root. The run script sets it. If you call scripts by hand, export it first:

  ```bash
  export COPLANARITY_BASE="$PWD"
  ```

## 4. Choose the number of workers (important)

- Check the free RAM (`free -g`) and CPU cores (`nproc`).
- `NWORKERS = min(nproc − 1, floor(free RAM in GB / 3))`.
- Examples: 32 GB → 8–10; 64 GB → about 20; 16 GB → 4–5.
- If a worker is killed (exit code 137, or "Killed" in the log), lower NWORKERS and rerun. The run resumes; finished events are never recomputed.

## 5. Run

One command does validation, production and figures:

```bash
bash RUN_FIG6_HIGH_BAND.sh <NWORKERS>          # e.g. bash RUN_FIG6_HIGH_BAND.sh 8
```

To use a specific interpreter: `PYTHON=/path/to/python bash RUN_FIG6_HIGH_BAND.sh 8`.

For a long run, start it detached and log to a file:

```bash
nohup bash RUN_FIG6_HIGH_BAND.sh 8 > fig6_high_run.log 2>&1 &
```

What the script does, step by step:

**Step 1. Validation.** It reruns the first 12 events of 5 already-computed points with `FAST=1` and compares every stored value: fiducial flag, plane, hit cut, signal-region flag, Δs and Δw, for both SCT z settings. The script `F6_06_validate_numba.py` must print `VALIDATION PASSED`. The script then exits with code 0.
- **If it prints FAILED, stop. Do not continue, and report the full output.** A failure means the numerics differ on this machine (for example a different numba or LLVM version). In that case, rerun everything without `FAST=1`; it is about 30× slower but uses the reference integrator.

**Step 2. Production.** It runs `F6_02_grid.py` with `BAND=high FAST=1` for 11 mass points: colored 600–2100 GeV, EW 100–800 GeV. EW 1000 and colored 2400 cannot reach 3 events and are skipped on purpose.
- Output: one append-only checkpoint per point, `05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/logs/F6_<point>_high_events.jsonl`, one line per finished event.
- If the run is interrupted, rerun the same command; it continues where it stopped.

**Step 3. Results.** It runs `F6_03_contours.py`, then `F6_04_summary.py`, then `F6_05_sensitivity.py`, then `F6_03_contours.py` again. These rebuild `fig6/F6_N_grid.csv`, `fig6/F6_reach.csv`, `fig6/F6_reach_sensitivity.csv`, `FINAL_FIGURES/F6_fig6/` and `FINAL_FIGURES/F6_kfactor/`. The script picks up the high-band checkpoints automatically.

Expected time: about 900 events, roughly 1–2 CPU-minutes per event for the five Λ values. On 8 cores that is about 2–4 hours.

## 6. Checks before reporting

Let A = `05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03`.

1. **Every checkpoint is complete.** The number of lines in `$A/logs/F6_<point>_high_events.jsonl` must equal the number of propagated events for that point. That number is printed at the start of each point as `events N`. Also, no event may appear twice.
2. **Integration failures.** Count the rows with a non-empty `error` field, per point and Λ. Failures say "cannot reach MIN_STEPS_PER_PERIOD", meaning the step ceiling of 20 million steps was hit. They are counted as not fiducial. Report the counts. If the failures at a given Λ are more than about 10% of the events, report that explicitly, because it would bias the efficiency low.
3. **Grid status.** Every high-band row of `$A/fig6/F6_N_grid.csv` for the 11 points should have `status_with_f = computed`.
4. **Reach.** `$A/fig6/F6_reach.csv` gives the maximum mass reach. The maxima were at Λ = 3–5 keV, so they should hardly change. Report the table.
5. **Figure.** Open `$A/FINAL_FIGURES/F6_fig6/F6_fig6.png`. The hatched "Λ > 10 keV: not computed" band must be gone, and the contours should extend above 10 keV.

## 7. Do not

- Do not edit `P4_literal_signal.py`, `P18_all_crossings.py`, `coplanarity_fit.py`, `trajectory_to_hits.py`, the integrators, or `config/*.yaml`. They define the validated analysis.
- Do not change the Λ values, the seeds, or the event selection in `F6_02_grid.py`.
- Do not delete or rewrite existing checkpoints (`logs/F6_*_events.jsonl`); they are the low- and mid-band results.
- Do not tune anything to match the paper.

## 8. Report back

Return:

1. The full validation output (the `VALIDATION ...` lines).
2. Per point: events, failures per Λ, and wall time.
3. `fig6/F6_reach.csv` and `fig6/F6_reach_sensitivity.csv`.
4. These files, which are tracked by git, so commit and push them to the same branch if you have access, or pack them:
   - `$A/logs/F6_*_high_events.jsonl`
   - `$A/fig6/`
   - `$A/FINAL_FIGURES/F6_fig6/` and `$A/FINAL_FIGURES/F6_kfactor/`

One manual follow-up is left for the project owner: the caption note "Λ > 10 keV: not computed" in `F6_03_contours.py` (variable `NOTES`) must be reworded after this run. Do not change it yourself unless asked.
