# Manual Verification Guide — Figure 2 Root Audit

Everything in this directory can be checked by hand with a few simple
commands. This is a read-mostly audit — running the commands below does not
modify anything. All paths are relative to this directory unless noted.

Python used throughout: `/home/rafia/miniforge3/envs/hep/bin/python3.11`
(the conda env `hep` — has pandas/numpy/matplotlib; the system `/usr/bin/python3`
does NOT have these installed).

## 1. Verify file integrity (hashing)

```bash
cd 05_coplanarity_analysis/FIGURE2_ROOT_AUDIT_2026-09-30
sha256sum -c SHA256_MANIFEST.txt
```
All lines should print `OK`.

## 2. Row counts

```bash
wc -l EVENT65_FULL_TIMESERIES.csv EVENT65_ROOT_RECOMPUTED_VALUES.csv
wc -l ../FINAL_FIGURES_2000_EVENT_2026-09-30/SOURCE_DATA/FIGURE_2_2000event_colored_event65_source.csv
```
`EVENT65_ROOT_RECOMPUTED_VALUES.csv` and the original source CSV should both
have 2,519 lines (2,518 data rows + 1 header).

## 3. head/tail sanity check

```bash
head -3 EVENT65_ORIGINAL_INPUT_ROW.csv
head -3 EVENT65_INITIAL_KINEMATICS.csv
head -5 EVENT65_FULL_TIMESERIES.csv
tail -5 EVENT65_FULL_TIMESERIES.csv
```

## 4. Event-identity check (seed, event_idx)

```bash
PY=/home/rafia/miniforge3/envs/hep/bin/python3.11
$PY -c "
import pandas as pd
BASE='/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1'
recon = pd.read_csv(f'{BASE}/reconstruction/colored_1800GeV_L2keV/per_event_results.csv')
trig  = pd.read_csv(f'{BASE}/events/colored_1800GeV_L2keV/trigger_passing_events.csv')
print(recon[recon.event_idx==65][['event_idx','seed','wall_time_s']])
print(trig.iloc[65][['px1','py1','pz1','E1','px2','py2','pz2','E2']])
"
```
Expect `seed=2123515583`, `wall_time_s≈12.817`.

## 5. Max/min L and d (quick recompute check)

```bash
PY=/home/rafia/miniforge3/envs/hep/bin/python3.11
$PY -c "
import pandas as pd
df = pd.read_csv('EVENT65_ROOT_RECOMPUTED_VALUES.csv')
print('max L_hbar:', df.L_hbar.max())
print('min/max d_cm:', df.d_cm.min(), df.d_cm.max())
print('r_cm range:', df.r_cm.min(), df.r_cm.max())
"
```
Expect `max L_hbar ≈ 5.22e13`, `d_cm` ranging roughly 0.0006–1.627 cm,
`r_cm` ranging roughly 2.36–22.0 cm.

## 6. Compare against the ORIGINAL Figure 2 source CSV (point-by-point)

```bash
PY=/home/rafia/miniforge3/envs/hep/bin/python3.11
$PY -c "
import pandas as pd, numpy as np
orig = pd.read_csv('../FINAL_FIGURES_2000_EVENT_2026-09-30/SOURCE_DATA/FIGURE_2_2000event_colored_event65_source.csv')
new  = pd.read_csv('EVENT65_ROOT_RECOMPUTED_VALUES.csv')
for col in ['r_cm','L_hbar','d_cm']:
    diff = np.abs(orig[col].values - new[col].values)
    print(col, 'max abs diff:', diff.max())
"
```
Expect all max-abs-diffs to be at the floating-point-noise level
(~1e-15 to ~1e-2 out of values ~1e13 for L_hbar — i.e. relative ~1e-16),
NOT zero (RK4 floating-point summation order differs slightly between the
two Python invocations) but also not meaningfully different.

## 7. Reproduce the cache-only plot yourself

```bash
PY=/home/rafia/miniforge3/envs/hep/bin/python3.11
nice -n 19 $PY plot_figure2_cache_only.py
```
This regenerates `FIGURE2_EVENT65_ROOT_VERIFIED.{png,pdf,svg}` from
`EVENT65_ROOT_RECOMPUTED_VALUES.csv` alone — no simulation code is imported
by this script (open it and check the import list yourself: only `pandas`
and `matplotlib`).

## 8. Re-run the full audit computation from scratch

```bash
PY=/home/rafia/miniforge3/envs/hep/bin/python3.11
nice -n 19 $PY generate_audit_csvs.py
```
This is the exact script that produced every `EVENT65_*.csv` file in this
directory. It is single-process (no multiprocessing pool) and runs at low
priority (`nice -n 19`) so it does not compete with the Figure 6 production
workers. It does NOT touch `05_coplanarity_analysis/figure6_full_v1/` or any
existing Figure 2 file.

## 9. Confirm Figure 6 was never touched

```bash
tmux ls   # should show "figure6_resume" session still present
ps -p 14845 -o pid,cmd   # driver process, should still be running
```

## Files in this directory

| File | What it is |
|---|---|
| `SOURCE_FILE_PROVENANCE.csv/.md` | Hashes/sizes/mtimes of all 11 authoritative input files |
| `EVENT65_ORIGINAL_INPUT_ROW.csv` | Unaltered original row 65 of `trigger_passing_events.csv` |
| `EVENT65_INITIAL_KINEMATICS.csv` | Full initial-state kinematics (E, p, masses, boosts) |
| `EVENT65_FULL_TIMESERIES.csv` | Every accepted RK4 step (r≤22cm), positions/momenta/L/d |
| `EVENT65_L_ZERO_AND_EXTREMA_TABLE.csv` | Every signed-L zero-crossing and L/d local extremum |
| `EVENT65_PAPER_EQ6_EQ7_COMPARISON.csv` | Event-specific evaluation of paper Eq. 6/7 vs. numeric max L |
| `EVENT65_ROOT_RECOMPUTED_VALUES.csv` | Independently regenerated (r_cm, L_hbar, d_cm), for Phase 8/9 |
| `generate_audit_csvs.py` | The script that produced all `EVENT65_*.csv` files above |
| `plot_figure2_cache_only.py` | Independent, cache-only replot (no simulation imports) |
| `FIGURE2_EVENT65_ROOT_VERIFIED.png/.pdf/.svg` | Output of the cache-only replot |
| `FIGURE2_ROOT_AUDIT_REPORT.md` | Full phase-by-phase findings and final verdict |
| `SHA256_MANIFEST.txt` | Hashes of every file in this directory |
