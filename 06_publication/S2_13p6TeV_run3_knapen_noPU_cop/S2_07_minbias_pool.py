#!/usr/bin/env python3
"""Stage 2, step 7: minimum-bias pool for the pile-up at sqrt(s) = 13.6 TeV. Same code, events and seed as the 13 TeV pool used by all background runs
(02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv: generate_ancestry_pool.py, 20 000 events, seed 20260916, SoftQCD:nonDiffractive, Monash);
only Beams:eCM = 13600 GeV.
Usage: S2_07_minbias_pool.py <n_events> <ecm GeV> <out.csv> [seed]   (validation: 13000 GeV must reproduce the first events of the 13 TeV pool).
2026-11-17: optional seed (default 20260916, the production pool) for the pool-size / pool-seed test; env COPLANARITY_BASE, PYTHIA8DATA.
Production: S2_07_minbias_pool.py 20000 13600 inputs/minbias_pool_20000_13p6TeV.csv"""
import os, sys, time
os.environ.setdefault("PYTHIA8DATA", "/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc")
sys.path.insert(0, os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study") + "/02_backgrounds/pileup")
import generate_ancestry_pool as gap
n, ecm, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]; seed = int(sys.argv[4]) if len(sys.argv) > 4 else 20260916
if os.path.exists(out): raise FileExistsError(out)
t0 = time.time(); st = gap.generate_ancestry_pool_streaming(n, seed, out, ecm_gev=ecm)
print("eCM", ecm, "seed", seed, "Pythia", st["actual_version"], "n_ok", st["n_ok"], "particles", st["n_particles_total"], f"{time.time()-t0:.0f}s", flush=True); print("POOL_EXIT=0")
