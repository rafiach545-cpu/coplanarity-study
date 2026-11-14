#!/usr/bin/env python3
"""Stage 2, step 8: the three background runs of the reproduction at sqrt(s) = 13.6 TeV. As S1_pileup_run2.py: the original scripts are loaded unchanged and
only module constants are replaced: MU, the photon folder PC (13.6 TeV photons from S2_06_zgamma_generate.py) and ANCESTRY_POOL_PATH (13.6 TeV minimum-bias
pool from S2_07_minbias_pool.py). Same per-event seeds as at 13 TeV. mu = 0 gives the conversion-only background (Poisson(0) = no pile-up interaction).
  P10  = conversion + pile-up, SCT z 1.16 mm
  P17b = conversion + pile-up, no SCT z smearing (Ref. [34] material)
  P8   = pile-up only, SCT z 1.16 mm
Usage: S2_08_background.py {P10|P17b|P8} <mu> [13p6TeV (default) | 13TeV: validation with the 13 TeV photons and pool |
       ph13_pu13p6, ph13p6_pu13: mixed test, 13 TeV photons with the 13.6 TeV pool and vice versa].
Check-only env: S2_PU_SEED (other pile-up seed), S2_NCHUNKS (first chunks only); both change the output folder name.
Output: logs/bkg_<sample>/<run>_mu<mu, . -> p>/chunk_*.csv (resumable: existing chunks are skipped)."""
import os, sys, time, json, importlib.util, multiprocessing as mp
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
run, MU, SAMPLE = sys.argv[1], float(sys.argv[2]), (sys.argv[3] if len(sys.argv) > 3 else "13p6TeV")
SRC = {"P10": "P10_literal_overlay", "P17b": "P17b_overlay_ref34", "P8": "P8_literal_pileup"}; name = SRC[run]
spec = importlib.util.spec_from_file_location(name, f"{REP}/{name}.py"); M = importlib.util.module_from_spec(spec); sys.modules[name] = M; spec.loader.exec_module(M)
assert M.MU == 50 and M.ANCESTRY_POOL_PATH.endswith("minbias_pool_20000_ANCESTRY_v1.csv"); M.MU = MU
PH136, PU136 = f"{HERE}/inputs/zgamma_13p6TeV", f"{HERE}/inputs/minbias_pool_20000_13p6TeV.csv"   # 13 TeV: the module defaults
assert SAMPLE in ("13p6TeV", "13TeV", "ph13_pu13p6", "ph13p6_pu13")                  # the last two: mixed test (photons of one energy, pile-up of the other)
if SAMPLE in ("13p6TeV", "ph13_pu13p6"): M.ANCESTRY_POOL_PATH = PU136
if SAMPLE in ("13p6TeV", "ph13p6_pu13") and run != "P8": M.PC = PH136; assert os.path.exists(f"{M.PC}/zgamma_photons.csv")
SEED_TAG = ""
if os.environ.get("S2_PU_SEED"):                                                   # check only: independent pile-up configurations (P10 / P17b)
    assert run != "P8"; M.PU_SEED = int(os.environ["S2_PU_SEED"]); SEED_TAG = f"_seed{M.PU_SEED}"
NMAX = int(os.environ.get("S2_NCHUNKS", 0))                                         # check only: first S2_NCHUNKS chunks
outd = f"{HERE}/logs/bkg_{SAMPLE}/{run}_mu" + f"{MU:g}".replace(".", "p") + SEED_TAG + ("_first%d" % NMAX if NMAX else ""); os.makedirs(outd, exist_ok=True)

def main():
    t0 = time.time()
    if run == "P8":
        n = 5000; todo = [("LITERAL", s, min(s + M.CHUNK, n)) for s in range(0, n, M.CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
        pool = mp.Pool(10, initializer=M._init, initargs=("LITERAL",))
    else:
        n = len(pd.read_csv(f"{M.PC}/zgamma_photons.csv")); todo = [s for s in range(0, n, M.CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
        if NMAX: todo = [s for s in todo if s < NMAX * M.CHUNK]
        pool = mp.Pool(10, initializer=M._init)
    print(f"{run} {SAMPLE} mu = {M.MU}: photons {getattr(M, 'PC', '-')}, pool {M.ANCESTRY_POOL_PATH}, {len(todo)} chunks", flush=True)
    with pool:
        for k, res in enumerate(pool.imap_unordered(M.chunk_job, todo), 1):
            start, rows = res[0], res[1]
            if run != "P8" and res[2]:
                with open(f"{outd}/displays_{start:06d}.jsonl", "w") as f:
                    for d in res[2]: f.write(json.dumps(d, default=float) + "\n")
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"; pd.DataFrame(rows).to_csv(tmp, index=False); os.replace(tmp, f"{outd}/chunk_{start:06d}.csv")
            print(f"  chunk {start} ({k}/{len(todo)}) {time.time()-t0:.0f}s", flush=True)
    print(f"{run}_EXIT=0", flush=True)

if __name__ == "__main__":
    main()
