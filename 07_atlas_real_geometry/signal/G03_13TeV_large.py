#!/usr/bin/env python3
"""07 signal step G03 (2026-11-17): 10k-generated signal samples at sqrt(s) = 13 TeV for Stage 0 · Paper · Ideal, Stage 1 · Run 2 · Ideal and
Stage 2 · Run 2 · ATLAS (the three 13 TeV stages share the signal; they differ in luminosity, pile-up and geometry).
Generation: the method of 06 S2b L01_generate.gen (chunks of 2000 events, every chunk an independent MG5 run) with the validated 13 TeV process
directories of the reproduction (/home/rafia/hep_tools/figure6_full_v1_runs/<template>; same cards as the 13.6 TeV Stage 1 templates except
ebeam 6500 GeV, checked by diff 2026-11-17). Only the quirk mass, nevents and iseed change. Seed: 2 000 000 + 100 000 (EW) + 40 * mass + chunk,
disjoint from the 13.6 TeV large samples (700 000-896 039) and from the reproduction seeds.
Extraction: 06 S2b L02_extract.py unchanged (same parser, charges, trigger pT(QQ) > 200 GeV, event_id = 100000 + index) with
S2B_RUNS = the G03 run folder and L02_OUT = signal/inputs_large_13TeV.
Points: the 13 points of the 13 TeV grid (06 S1 N grid: EW 100-1000, colored 600-2400) + EW 1200 GeV (as at 13.6 TeV) = 14 x 5 chunks.
Usage: G03_13TeV_large.py <gen|ext|gen,ext> [--cores N]. Resumable (chunks with checkpoints_DONE_generation.txt are skipped).
Output: /home/rafia/hep_tools/07_large_runs_13TeV/<tag>_c<chunk>/, logs/G03_generation.csv, signal/inputs_large_13TeV/<tag>_events.csv + counts.csv."""
import os, re, sys, time, argparse, subprocess, multiprocessing as mp, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study")
SRC = os.environ.get("G03_TEMPLATES", "/home/rafia/hep_tools/figure6_full_v1_runs"); RUNS = os.environ.get("G03_RUNS", "/home/rafia/hep_tools/07_large_runs_13TeV")
HEP_BIN = os.environ.get("HEP_BIN", "/home/rafia/miniconda3/envs/hep/bin"); TEMPLATE = {"colored": "colored_1200gev", "EW": "EW_400gev"}; PDG = {"colored": "1000006", "EW": "9000011"}
POINTS = [("EW", m) for m in (100, 200, 400, 600, 800, 1000, 1200)] + [("colored", m) for m in (600, 900, 1200, 1500, 1800, 2100, 2400)]
NCH, NEV = 5, 2000; INP = f"{HERE}/inputs_large_13TeV"; LOGD = f"{R}/logs"


def seed(ch, m, c): return 2000000 + 100000 * (ch == "EW") + 40 * m + c


def edit(path, pat):
    txt = open(path).read()
    for key, val in pat:
        txt, n = re.subn(key, val, txt, flags=re.M); assert n == 1, (path, key)
    open(path, "w").write(txt)


def gen(a):
    ch, m, c = a; tag = f"{ch}_{m}gev_c{c:02d}"; d = f"{RUNS}/{tag}"; done = f"{d}/checkpoints_DONE_generation.txt"
    if os.path.exists(done): return eval(open(done).read())
    os.makedirs(RUNS, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude=Events/*", "--exclude=checkpoints_DONE_generation.txt", "--exclude=gen_*.log", f"{SRC}/{TEMPLATE[ch]}/", f"{d}/"], check=True)
    s = seed(ch, m, c)
    edit(f"{d}/Cards/run_card.dat", [(r"^\s*\d+\s*= nevents", f"  {NEV}\t= nevents"), (r"^\s*\d+\s*= iseed", f"  {s}\t= iseed")])
    edit(f"{d}/Cards/param_card.dat", [(rf"^(\s*{PDG[ch]}\s+)[0-9.eE+-]+", rf"\g<1>{float(m):.6e}")])
    txt = open(f"{d}/Cards/run_card.dat").read(); assert re.search(r"^\s*6500\.?0*\s*= ebeam1", txt, re.M) and re.search(r"^\s*6500\.?0*\s*= ebeam2", txt, re.M)
    env = os.environ.copy(); env.pop("PYTHIA8DATA", None); env["PATH"] = f"{HEP_BIN}:{env['PATH']}"
    t0 = time.time(); log = f"{d}/gen_run.log"
    with open(log, "w") as f: p = subprocess.run(["./bin/generate_events", "run_l", "-f"], cwd=d, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=14400)
    txt = open(log).read(); ok = p.returncode == 0 and os.path.exists(f"{d}/Events/run_l/tag_1_pythia8_events.hepmc.gz")
    mm = re.search(r"Nb of events after matching/merging\s*:\s*(\d+)", txt); x = re.search(r"Matched cross-section\s*:\s*([0-9.eE+-]+)\s*\+-\s*([0-9.eE+-]+)", txt)
    r = dict(tag=tag, channel=ch, mass_gev=m, chunk=c, seed=s, n_generated=NEV, n_matched=int(mm.group(1)) if mm else None, matched_xsec_pb=float(x.group(1)) if x else None,
             matched_xsec_err_pb=float(x.group(2)) if x else None, wall_s=round(time.time() - t0, 1), status="ok" if ok else "failed", exit_code=p.returncode)
    if ok: open(done, "w").write(f"{r}\n")
    print(r, flush=True); return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("steps"); ap.add_argument("--cores", type=int, default=8); A = ap.parse_args(); S = A.steps.split(",")
    if "gen" in S:
        jobs = [(ch, m, c) for ch, m in POINTS for c in range(NCH)]
        with mp.Pool(A.cores) as pool: res = list(pool.imap_unordered(gen, jobs))
        pd.DataFrame(res).sort_values("tag").to_csv(f"{LOGD}/G03_generation.csv", index=False)
        bad = [r["tag"] for r in res if r["status"] != "ok"]; print("G03 generation done, failed:", bad, flush=True)
        if bad: sys.exit(1)
    if "ext" in S:
        env = dict(os.environ, S2B_RUNS=RUNS, L02_OUT=INP, COPLANARITY_BASE=BASE, PYTHIA8DATA=f"{os.path.dirname(HEP_BIN)}/share/Pythia8/xmldoc")
        for ch, m in POINTS:
            with open(f"{LOGD}/G03_ext_{ch}_{m}gev.log", "w") as fh:
                p = subprocess.run([f"{HEP_BIN}/python", f"{BASE}/06_publication/S2b_13p6TeV_large_samples/L02_extract.py", ch, str(m)], env=env, stdout=fh, stderr=subprocess.STDOUT)
            print("extracted", ch, m, "exit", p.returncode, flush=True)
            if p.returncode: sys.exit(1)
    print("G03_EXIT=0")
