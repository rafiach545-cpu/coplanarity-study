# 20_remaining_work

| item | status | next_action |
|---|---|---|
| Resolve EW trigger/fiducial discrepancy | audited, no bug found, root cause hypothesized (undocumented MC generation settings + DY pT-spectrum merging-scale sensitivity), not proven | reconstruct/archive MadGraph run_cards is now DONE (madgraph_pilot_v1); a controlled re-generation with paper-matched settings would be needed to test the hypothesis, but the papers own settings are unpublished |
| Colored statistics (N=7 fiducial) | feasibility assessed, ~7.2x more matched events needed for N_fiducial~50 | generation-time now measured (~0.68h for the needed sample) -- a larger production run could be launched in a dedicated future task with explicit authorization |
| Figure 6 grid | NOT LAUNCHED -- verified grid plan ready, optimized runtime ~37.9h (was ~437.7h) | launch a bounded 2-3 mass-point pilot before the full 91-point grid, in a dedicated future task with explicit authorization and checkpoint/resume |
| Figure 7 material model | BLOCKED -- standalone Bethe-Bloch formula validated (10/10 tests), material budget/path-length unavailable | digitize PDG MPV-dE/dx-vs-betagamma curve and define an explicit (not invented) per-layer material-budget model before any integration attempt |
| Full 16-run Figure 6 profiling grid | 6/16 completed (time-capped) | not needed -- bottleneck already established with statistical certainty (7/7 including one extra probe) |
| Parallel execution of trajectory integration | not implemented | RK4 integration has no RNG dependency, trivially safe to parallelize across (event,Lambda) grid points -- recommended if the 37.9h estimate is still too slow for the intended use |
