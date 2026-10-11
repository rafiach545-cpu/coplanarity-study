## D11. Pre-registered test: pile-up minimum-bias generator variants (written BEFORE the runs, 2026-10-08)
- **Source search first (done):** the paper's TeX comments (v1, v2 = latest) and the source of ref. [34] (softbombs.tex) contain no
  minimum-bias settings; [34] says only "minimum bias events generated with Pythia 8". Our pool: SoftQCD:nonDiffractive, default tune
  (Monash), 13 TeV, 20 000 events, Pythia 8.312 (paper: 125 000 events).
- **Runs:** `scripts/P22_pileup_minbias_variants.py`, identical to P21 REF34_Z580 except the pool (20 000 events, seed 20260916, `scripts/P22a_minbias_pool.py`):
  V1 = SoftQCD:inelastic, Monash; V2 = SoftQCD:nonDiffractive, Tune:pp = 5 (A2-CTEQ6L1).
  Check: the P22 code with the P21 pool must reproduce P21 chunk 0 (events 0-99).
- **Primary statistic (as D8):** fraction of the 5000 events whose selected Sec. III C plane (Delta_w < 1 cm) has >= 1 hit in >= 4 layers. Baseline (P21): 33/5000 = 6.6e-3.
- **Outcomes, fixed now (per variant):** rate <= 2e-3: explained by the minimum-bias generator setting. Otherwise: not explained, and the
  pile-up investigation stops.
