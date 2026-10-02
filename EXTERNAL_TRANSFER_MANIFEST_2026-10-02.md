# External Transfer Manifest — 2026-10-02

Files/directories NOT committed to git (too large for GitHub and/or raw
generator output), that must be transferred separately (e.g. rsync/scp)
if needed on the destination machine. Nothing here was deleted or modified.

## 1. Disposable MadGraph/Pythia generation scratch (inside the repo tree, gitignored by exclusion)

- `02_backgrounds/photon_conversion/CROSS_SECTION_AUDIT_v1/generation/` — 651M
  - includes `scan_D_ptgmin05/Events/run_D1/tag_1_pythia8_events.hepmc.gz` (389M)
  - MadGraph build artifacts (`nlo_pilot_attempt/`), multiple scan run directories
  - All deliverables derived FROM this scratch (CSVs, tables, MD reports) are
    already committed; only the raw generation working directory is excluded.

## 2. Pre-existing large data pools (predate 2026-09-24 backup, unrelated to this round)

- `02_backgrounds/pileup/minbias_pool_20000_FINAL.csv` — 223M
- `02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv` — 250M

## 3. External tool/run directory (outside the git repo entirely)

- `/home/rafia/hep_tools/` — 3.7G total, never tracked in git
  - Contains all MadGraph installs (`MG5_aMC_v3_7_3/`), per-benchmark run
    directories (`quirk_signal_1800gev_2kev/`, `quirk_ew_800gev_4kev/`,
    `quirk_2000_fresh_regen_runs/`, `figure6_full_v1_runs/`, `zgamma_background_test/`,
    `test_quirk_qcd/`, `test_pp_jj/`), each with `.lhe.gz`/`.hepmc.gz` event files.
  - `figure6_full_v1_runs/` specifically holds the Figure 6 grid's generation-level
    outputs and DONE markers referenced by the (currently stopped, awaiting
    resume) Figure 6 production pipeline — do not delete or modify this on
    either machine until Figure 6 production is fully complete.

## Recommended transfer command (run manually on this machine, not via git)

```
rsync -avh --progress \
  /home/rafia/coplanarity_study/02_backgrounds/photon_conversion/CROSS_SECTION_AUDIT_v1/generation/ \
  /home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_FINAL.csv \
  /home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv \
  /home/rafia/hep_tools/ \
  <destination>
```
