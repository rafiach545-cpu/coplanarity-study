#!/usr/bin/env python3
"""P22 (2026-10-08, pre-registered in DECISIONS_LOG D11): pile-up only, mu = 50, identical to P21 REF34_Z580 ([34] material model,
SCT z 580 um, same 5000 events and seeds SeedSequence([90210777, 50, i])) except the minimum-bias pool:
  MB_INEL_MONASH : SoftQCD:inelastic, Monash      (02_backgrounds/pileup/minbias_pool_20000_MB_INEL_MONASH_v1.csv)
  MB_ND_A2       : SoftQCD:nonDiffractive, A2     (02_backgrounds/pileup/minbias_pool_20000_MB_ND_A2_v1.csv)
  CHECK_BASELINE : the P21 pool, events 0-99 only -> must reproduce logs/P21_chunks_REF34_Z580/chunk_000000.csv.
Output: logs/P22_chunks_<variant>/chunk_*.csv (append-only, resumable)."""
import os, sys, time, importlib.util, multiprocessing as mp, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
_s = importlib.util.spec_from_file_location("p21", f"{HERE}/P21_pileup_ref34.py"); p21 = importlib.util.module_from_spec(_s); _s.loader.exec_module(p21)
POOLS = {"MB_INEL_MONASH": "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_MB_INEL_MONASH_v1.csv",
         "MB_ND_A2": "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_MB_ND_A2_v1.csv",
         "CHECK_BASELINE": p21.p8.ANCESTRY_POOL_PATH}
def _init(v):
    p21.p8.ANCESTRY_POOL_PATH = POOLS[v]; p21._init("REF34_Z580")
def chunk_job(a):   # defined here: functions of a spec-loaded module cannot be pickled for the pool
    return p21.chunk_job(a)
def main():
    v, n = sys.argv[1], int(sys.argv[2]); outd = f"{HERE}/../logs/P22_chunks_{v}"; os.makedirs(outd, exist_ok=True)
    todo = [("REF34_Z580", s, min(s + p21.p8.CHUNK, n)) for s in range(0, n, p21.p8.CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
    print(f"{v}: pool {POOLS[v]}, {len(todo)} chunks to run", flush=True); t0 = time.time()
    with mp.Pool(10, initializer=_init, initargs=(v,)) as pool:
        for k, (start, rows) in enumerate(pool.imap_unordered(chunk_job, todo), 1):
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"; pd.DataFrame(rows).to_csv(tmp, index=False); os.replace(tmp, f"{outd}/chunk_{start:06d}.csv")
            print(f"  chunk {start} done ({k}/{len(todo)}), {time.time()-t0:.0f}s", flush=True)
if __name__ == "__main__":
    main()
