#!/usr/bin/env python3
"""Stage 2b, step 4: the whole large-sample run. Points: colored 1200-1800 GeV every 150 GeV, EW 400-700 GeV every 50 GeV (13.6 TeV), N_EV generated events
per point in chunks of 2000 (L01, all chunks of all points in one pool), then extraction (L02, hep env for the R-hadron charges) and propagation at
Lambda = 2-10 keV (L03, NCORES workers per point). Every step resumes from its checkpoints.
Usage: L04_run_all.py <events_per_point> <n_cores>. Log: logs/L04_run_all.log (stdout)."""
import os, sys, time, subprocess, importlib.util, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); PY = "/home/rafia/venvs/f6fast/bin/python"; PYHEP = "/home/rafia/miniconda3/envs/hep/bin/python"
POINTS = [("colored", m) for m in range(1200, 1801, 150)] + [("EW", m) for m in range(400, 701, 50)]
spec = importlib.util.spec_from_file_location("L01", f"{HERE}/L01_generate.py"); L01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(L01)
if __name__ == "__main__":
    nev, nc = int(sys.argv[1]), int(sys.argv[2]); CH = 2000; nch = -(-nev // CH); t0 = time.time()
    jobs = [(ch, m, c, CH) for ch, m in POINTS for c in range(nch)]
    jobs.sort(key=lambda j: j[0] != "EW")                                          # EW chunks take longer: first
    with mp.Pool(nc) as pool: res = pool.map(L01.gen, jobs, chunksize=1)
    import pandas as pd; f = f"{HERE}/logs/L01_generation.csv"; pd.DataFrame(res).to_csv(f, index=False)
    bad = [r["tag"] for r in res if r["status"] != "ok"]; print(f"generation: {len(res)} chunks, failed {bad}, {time.time() - t0:.0f}s", flush=True)
    for ch, m in POINTS:
        subprocess.run([PYHEP if ch == "colored" else PY, f"{HERE}/L02_extract.py", ch, str(m)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"extraction done {time.time() - t0:.0f}s", flush=True)
    for ch, m in POINTS:
        with open(f"{HERE}/logs/L03_{ch}_{m}gev.log", "a") as fh: subprocess.run([PY, f"{HERE}/L03_propagate.py", ch, str(m), str(nc)], check=True, stdout=fh, stderr=subprocess.STDOUT)
        print(f"propagated {ch} {m} {time.time() - t0:.0f}s", flush=True)
    print("L04_EXIT=0" if not bad else "L04_INCOMPLETE", flush=True)
