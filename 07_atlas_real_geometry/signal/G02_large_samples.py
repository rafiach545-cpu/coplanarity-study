#!/usr/bin/env python3
"""07 signal step G02 (2026-11-16): large signal samples (default 10 000 generated events per mass point) through the ATLAS geometry.
Mass points: the 13 points of Stage 2 (06_publication/S2_.../inputs/counts.csv): EW 100, 200, 400, 600, 800, 1000 GeV; colored 600-2400 GeV every 300.
Steps (each resumes from its checkpoints):
  gen  - 06_publication/S2b_13p6TeV_large_samples/L01_generate.py gen() unchanged: chunks of 2000 events, every chunk an independent MG5 run
         (template process dir of Stage 2, only quirk mass, nevents, iseed changed; seed 700000 + 100000 (EW) + 40 mass + chunk, never a Stage 2 seed);
         run dirs in $S2B_RUNS (default here /home/rafia/hep_tools/07_large_runs);
  ext  - L02_extract.py unchanged (Stage 2 parser, charges, trigger pT(QQ) > 200 GeV; event_id = 100000 + index) -> signal/inputs_large/;
  prop - G01_signal_07.py atlas <tag> <band> --input inputs_large/<tag>_events.csv --out runs/atlas_large, bands mid, low, high_a
         (band order: mid of all points first, then low, then high_a; high_a uses up to 1.8 GB per worker).
Usage: G02_large_samples.py <steps gen,ext,prop> [--nev 10000] [--cores 8] [--workers 4] [--workers-high 3] [--points EW:100,colored:600,...]
Logs: logs/G02_large_samples.log (stdout), logs/G02_<step>_<tag>[_<band>].log."""
import os, sys, time, argparse, subprocess, importlib.util, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/..")
BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study"); L = f"{BASE}/06_publication/S2b_13p6TeV_large_samples"
os.environ.setdefault("S2B_RUNS", "/home/rafia/hep_tools/07_large_runs")
PY = os.environ.get("PY", "/home/rafia/venvs/f6fast/bin/python"); PYHEP = os.environ.get("PYHEP", "/home/rafia/miniconda3/envs/hep/bin/python")
POINTS = [("EW", m) for m in (100, 200, 400, 600, 800, 1000)] + [("colored", m) for m in range(600, 2401, 300)]
ap = argparse.ArgumentParser(); ap.add_argument("steps"); ap.add_argument("--nev", type=int, default=10000); ap.add_argument("--cores", type=int, default=8)
ap.add_argument("--workers", type=int, default=4); ap.add_argument("--workers-high", type=int, default=3); ap.add_argument("--points", default="")
A = ap.parse_args(); STEPS = A.steps.split(",")
if A.points: POINTS = [(p.split(":")[0], int(p.split(":")[1])) for p in A.points.split(",")]
INP = f"{HERE}/inputs_large"; OUT = f"{HERE}/runs/atlas_large"; LOGD = f"{ROOT}/logs"; CH = 2000
os.makedirs(INP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
spec = importlib.util.spec_from_file_location("L01", f"{L}/L01_generate.py"); L01 = importlib.util.module_from_spec(spec); sys.modules["L01"] = L01; spec.loader.exec_module(L01)
assert L01.RUNS == os.environ["S2B_RUNS"]
t0 = time.time(); say = lambda *a: print(f"[{time.time() - t0:7.0f}s]", *a, flush=True)
if __name__ == "__main__":
    say("G02 steps", STEPS, "points", POINTS, "nev", A.nev, "runs", L01.RUNS)
    if "gen" in STEPS:
        nch = -(-A.nev // CH); assert nch <= 40
        jobs = sorted([(ch, m, c, CH) for ch, m in POINTS for c in range(nch)], key=lambda j: j[0] != "EW")   # EW chunks take longer: first
        with mp.Pool(A.cores) as pool:
            res = []
            for r in pool.imap_unordered(L01.gen, jobs):
                res.append(r); say(f"gen {len(res)}/{len(jobs)} {r['tag']} {r['status']} matched {r['n_matched']} {r['wall_s']}s")
        import pandas as pd; pd.DataFrame(res).sort_values("tag").to_csv(f"{LOGD}/G02_generation.csv", index=False)
        bad = [r["tag"] for r in res if r["status"] != "ok"]; say("generation done, failed:", bad)
        if bad: sys.exit("G02_GEN_INCOMPLETE")
    if "ext" in STEPS:
        env = dict(os.environ, L02_OUT=INP)
        for ch, m in POINTS:
            with open(f"{LOGD}/G02_ext_{ch}_{m}gev.log", "w") as fh:
                subprocess.run([PYHEP if ch == "colored" else PY, f"{L}/L02_extract.py", ch, str(m)], check=True, env=env, stdout=fh, stderr=subprocess.STDOUT)
            say("extracted", ch, m, open(f"{LOGD}/G02_ext_{ch}_{m}gev.log").read().strip().splitlines()[-2][:200])
    if "prop" in STEPS:
        for band in ("mid", "low", "high_a"):
            for ch, m in POINTS:
                tag = f"{ch}_{m}gev"; w = A.workers_high if band == "high_a" else A.workers
                with open(f"{LOGD}/G02_prop_{tag}_{band}.log", "a") as fh:
                    p = subprocess.run([PY, f"{HERE}/G01_signal_07.py", "atlas", tag, band, "--input", f"{INP}/{tag}_events.csv", "--out", OUT, "--workers", str(w)],
                                       stdout=fh, stderr=subprocess.STDOUT)
                say("propagated", tag, band, "exit", p.returncode)
                if p.returncode: sys.exit("G02_PROP_FAILED")
    say("G02_EXIT=0")
