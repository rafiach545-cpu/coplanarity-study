# Fresh Independent 2000+2000 Event Quirk Regeneration

Strictly independent regeneration (colored 1800GeV/2keV, EW 800GeV/4keV,
2000 requested events each) — see `PAPER_REQUIREMENTS.md`,
`CONFIGURATION_FROZEN.json`, `FINAL_FRESH_2000_EVENT_REPORT.md`.

## Directory structure
- `generation/<sample>/` — generation stats, logs
- `events/<sample>/` — matched event tables, trigger-passing tables
- `reconstruction/<sample>/` — per-event downstream results (full detail)
- `cutflows/` — charge/trigger accounting JSON
- `statistics/` — cutflow statistics with Wilson/CP intervals, paper comparison
- `checkpoints/` — atomic per-chunk downstream progress
- `metadata/`, `logs/`, `plots/`, `hits/`, `trajectories/` — reserved/populated as applicable

## Reproduce
```
cd /home/rafia/coplanarity_study
source /home/rafia/miniforge3/etc/profile.d/conda.sh && conda activate hep
python3 05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/run_fresh_regeneration.py
```
Resumable: already-checkpointed events/cells are skipped automatically.
