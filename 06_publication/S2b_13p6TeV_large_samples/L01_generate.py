#!/usr/bin/env python3
"""Stage 2b, step 1: large signal samples near the contours at sqrt(s) = 13.6 TeV. Generation in chunks: every chunk is an independent MG5 run (own process
directory and seed) so that the chunks can run on many cores at once. Process directory copied from the validated 13.6 TeV run of Stage 2
(/home/rafia/hep_tools/S2_13p6TeV_runs/<template>, same cards, ebeam 6800, hep env first in PATH as S2_01); only the quirk mass (param_card: mqc for
colored, mqe for EW), nevents and iseed change. Seed of a chunk: 700000 + 1000 * (0 colored / 1 EW) ... see seed() (never equal to a Stage 2 seed).
Usage: L01_generate.py <channel> <mass> <n_chunks> <events_per_chunk> [n_parallel] [first_chunk]. Output: /home/rafia/hep_tools/S2b_large_runs/<tag>_c<chunk>/,
logs/L01_generation.csv (one row per chunk, appended). Env (2026-11-16, other machines): S2_TEMPLATES (process dirs), HEP_BIN, S2B_RUNS. Resumable: chunks with checkpoints_DONE_generation.txt are skipped."""
import os, re, sys, time, subprocess, multiprocessing as mp, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.environ.get("S2_TEMPLATES", "/home/rafia/hep_tools/S2_13p6TeV_runs"); RUNS = os.environ.get("S2B_RUNS", "/home/rafia/hep_tools/S2b_large_runs")
HEP_BIN = os.environ.get("HEP_BIN", "/home/rafia/miniconda3/envs/hep/bin"); TEMPLATE = {"colored": "colored_1200gev", "EW": "EW_400gev"}; PDG = {"colored": "1000006", "EW": "9000011"}
def seed(ch, m, c): return 700000 + 100000 * (ch == "EW") + 40 * m + c        # c < 40; unique per (channel, mass, chunk)
def edit(path, pat):
    txt = open(path).read()
    for key, val in pat:
        txt, n = re.subn(key, val, txt, flags=re.M); assert n == 1, (path, key)
    open(path, "w").write(txt)
def gen(a):
    ch, m, c, nev = a; tag = f"{ch}_{m}gev_c{c:02d}"; d = f"{RUNS}/{tag}"; done = f"{d}/checkpoints_DONE_generation.txt"
    if os.path.exists(done): return eval(open(done).read())
    os.makedirs(RUNS, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude=Events/*", "--exclude=checkpoints_DONE_generation.txt", "--exclude=gen_*.log", f"{SRC}/{TEMPLATE[ch]}/", f"{d}/"], check=True)
    s = seed(ch, m, c)
    edit(f"{d}/Cards/run_card.dat", [(r"^\s*\d+\s*= nevents", f"  {nev}\t= nevents"), (r"^\s*\d+\s*= iseed", f"  {s}\t= iseed")])
    edit(f"{d}/Cards/param_card.dat", [(rf"^(\s*{PDG[ch]}\s+)[0-9.eE+-]+", rf"\g<1>{float(m):.6e}")])
    txt = open(f"{d}/Cards/run_card.dat").read(); assert re.search(r"^\s*6800\.?0*\s*= ebeam1", txt, re.M) and re.search(r"^\s*6800\.?0*\s*= ebeam2", txt, re.M)
    env = os.environ.copy(); env.pop("PYTHIA8DATA", None); env["PATH"] = f"{HEP_BIN}:{env['PATH']}"
    t0 = time.time(); log = f"{d}/gen_run.log"
    with open(log, "w") as f: p = subprocess.run(["./bin/generate_events", "run_l", "-f"], cwd=d, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=14400)
    txt = open(log).read(); ok = p.returncode == 0 and os.path.exists(f"{d}/Events/run_l/tag_1_pythia8_events.hepmc.gz")
    mm = re.search(r"Nb of events after matching/merging\s*:\s*(\d+)", txt); x = re.search(r"Matched cross-section\s*:\s*([0-9.eE+-]+)\s*\+-\s*([0-9.eE+-]+)", txt)
    r = dict(tag=tag, channel=ch, mass_gev=m, chunk=c, seed=s, n_generated=nev, n_matched=int(mm.group(1)) if mm else None, matched_xsec_pb=float(x.group(1)) if x else None,
             matched_xsec_err_pb=float(x.group(2)) if x else None, wall_s=round(time.time() - t0, 1), status="ok" if ok else "failed", exit_code=p.returncode)
    if ok:
        open(done, "w").write(f"{r}\n")
        for junk in ("Events/run_l/unweighted_events.lhe.gz",): pass                 # LHE kept (small)
    print(r, flush=True); return r
if __name__ == "__main__":
    ch, m, nch, nev = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); npar = int(sys.argv[5]) if len(sys.argv) > 5 else 4; c0 = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    assert ch in TEMPLATE and nch + c0 <= 40
    with mp.Pool(npar) as pool: res = pool.map(gen, [(ch, m, c, nev) for c in range(c0, c0 + nch)], chunksize=1)
    f = f"{HERE}/logs/L01_generation.csv"; pd.DataFrame(res).to_csv(f, mode="a", header=not os.path.exists(f), index=False)
    print("L01_EXIT=0" if all(r["status"] == "ok" for r in res) else "L01_INCOMPLETE")
