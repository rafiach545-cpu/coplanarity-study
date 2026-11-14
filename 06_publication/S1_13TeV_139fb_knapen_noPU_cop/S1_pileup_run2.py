#!/usr/bin/env python3
"""Stage 1 backgrounds with the Run 2 pile-up (2026-11-03): the three background runs of the reproduction report, rerun with <mu> = 33.7 (ATLAS Run 2,
2015-2018, luminosity-weighted mean) instead of mu = 50. Nothing else changes: the original scripts are loaded unchanged, only their module constant MU and
the output folder are replaced; same photons, same seeds (P10/P17b: SeedSequence([90210777, i]) does not depend on mu, so the two mu values are compared on
the same events; P8: SeedSequence([90210777, int(MU), i]) as in the original).
  P10  = conversion + pile-up, SCT z 1.16 mm (report: conv1160, 0/9139 at mu = 50)
  P17b = conversion + pile-up, no SCT z smearing (report: conv0, 146/9139 at mu = 50)
  P8   = pile-up only, SCT z 1.16 mm (report: pu1160, 0/5000 at mu = 50)
Usage: python S1_pileup_run2.py {P10|P17b|P8} [mu, default 33.7; 20 = low pile-up]. Output: logs/<run>_mu<mu, . -> p>/chunk_*.csv (resumable: existing chunks are skipped)."""
import os, sys, time, json, importlib.util, multiprocessing as mp
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
MU_RUN2 = float(sys.argv[2]) if len(sys.argv) > 2 else 33.7
SRC = {"P10": "P10_literal_overlay", "P17b": "P17b_overlay_ref34", "P8": "P8_literal_pileup"}
run = sys.argv[1]; name = SRC[run]
spec = importlib.util.spec_from_file_location(name, f"{REP}/{name}.py"); M = importlib.util.module_from_spec(spec); sys.modules[name] = M; spec.loader.exec_module(M)
assert M.MU == 50; M.MU = MU_RUN2
outd = f"{HERE}/logs/{run}_mu" + f"{MU_RUN2:g}".replace(".", "p"); os.makedirs(outd, exist_ok=True)

def main():
    t0 = time.time()
    if run == "P8":
        n = 5000; todo = [("LITERAL", s, min(s + M.CHUNK, n)) for s in range(0, n, M.CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
        pool = mp.Pool(10, initializer=M._init, initargs=("LITERAL",))
    else:
        n = len(pd.read_csv(f"{M.PC}/zgamma_photons.csv")); todo = [s for s in range(0, n, M.CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
        pool = mp.Pool(10, initializer=M._init)
    print(f"{run} mu = {M.MU}: {len(todo)} chunks", flush=True)
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
