# 16_runtime_and_resources

| stage | wall_time |
|---|---|
| Colored+EW MadGraph generation (1000 events each, original) | not separately logged (only shower/matching stage timestamped) |
| Colored+EW MadGraph generation (100-event pilot, both benchmarks) | 172.22s (EW) + 39.77s (colored), incl. one-time compile |
| Colored signal full pipeline (27 trigger-passing events) | 818s |
| Pileup sweep (mu=0,5,10,20,50, 5000 events each) | ~24700s total |
| Converted-photon-only (9139 events) | 16934.9s (4.704h) |
| Converted-photon+PU mu=50 (9139 events) | 53240.8s (14.79h) |
| Figure 4 vertex-fixed replay (event 386) | 4115.4s (68.6 min) |
| Figure 6 downstream RK4 profiling (6 events) | 114-1429s per event, baseline |
| Figure 6 downstream optimized (v2 integrator) | 6.43-73.03s per event, 16.87x mean speedup |
| Figure 6 revised total estimate (91-pt grid) | ~37.9h (12.7h generation + 25.2h downstream), down from ~437.7h |
