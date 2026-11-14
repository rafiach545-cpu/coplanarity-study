#!/usr/bin/env python3
"""Stage 2 (2026-11-03): signal generation at sqrt(s) = 13.6 TeV (LHC Run 3, 6.8 TeV per beam), the 13 Figure 6 mass points.
Everything as the validated 13 TeV generation (figure6_full_v1, run_phase5_production.run_generation_one_point): MG5 3.7.3 process directories copied from
/home/rafia/hep_tools/figure6_full_v1_runs/<tag> (same proc/param/pythia8 cards: 0 + 1 jet, MLM xqcut 30, nn23lo1, R-hadrons on), 2000 events, the same seed
per point, nb_core 1, the hep env first in PATH (its conda-forge gfortran 16.2 built the 13 TeV objects). Only change: ebeam1 = ebeam2 = 6800 GeV (was 6500).
Usage: S2_01_generate.py [n_parallel, default 4]. Output: /home/rafia/hep_tools/S2_13p6TeV_runs/<tag>/Events/run_s2/tag_1_pythia8_events.hepmc.gz,
generation_statistics_13p6TeV.csv (this folder). Validation only: env S2_RUNS (folder), S2_EBEAM, S2_ONLY (comma-separated tags). Resumable: points with checkpoints_DONE_generation.txt are skipped."""
import os, re, sys, time, subprocess, multiprocessing as mp, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = "/home/rafia/coplanarity_study"
SRC = "/home/rafia/hep_tools/figure6_full_v1_runs"; RUNS = os.environ.get("S2_RUNS", "/home/rafia/hep_tools/S2_13p6TeV_runs"); EBEAM = float(os.environ.get("S2_EBEAM", 6800.0)); N_GEN = 2000
HEP_BIN = "/home/rafia/miniconda3/envs/hep/bin"   # the 13 TeV objects were built with its gfortran; Ubuntu gfortran 13.3 objects linked to them segfault
GEN13 = pd.read_csv(f"{BASE}/05_coplanarity_analysis/figure6_full_v1/TABLES/generation_statistics_13_mass_points.csv")

def edit_run_card(path, seed):
    out = []
    for line in open(path):
        if "= nevents" in line: line = re.sub(r"^\s*\d+", f"  {N_GEN}", line)
        elif "= iseed" in line: line = re.sub(r"^\s*\d+", f"  {seed}", line)
        elif "= ebeam1" in line or "= ebeam2" in line: line = re.sub(r"^\s*[0-9.]+", f"  {EBEAM}", line)
        out.append(line)
    open(path, "w").writelines(out)
    txt = open(path).read(); assert len(re.findall(rf"^\s*{EBEAM}\s*= ebeam[12]", txt, re.M)) == 2 and re.search(rf"^\s*{seed}\s*= iseed", txt, re.M), path

def gen(row):
    row = pd.Series(row)
    tag = f"{row.channel}_{int(row.mass_gev)}gev"; d = f"{RUNS}/{tag}"; done = f"{d}/checkpoints_DONE_generation.txt"
    if os.path.exists(done): return dict(tag=tag, status="already_done")
    if not os.path.exists(d):
        os.makedirs(RUNS, exist_ok=True)
        subprocess.run(["rsync", "-a", "--exclude=Events/*", "--exclude=checkpoints_DONE_generation.txt", "--exclude=metadata", "--exclude=gen_*.log",
                        f"{SRC}/{tag}/", f"{d}/"], check=True)
    edit_run_card(f"{d}/Cards/run_card.dat", int(row.seed))
    env = os.environ.copy(); env.pop("PYTHIA8DATA", None); env["PATH"] = f"{HEP_BIN}:{env['PATH']}"   # conda-forge gfortran 16.2 (as the 13 TeV build)
    t0 = time.time(); log = f"{d}/gen_run_s2.log"
    with open(log, "w") as f:
        p = subprocess.run(["./bin/generate_events", "run_s2", "-f"], cwd=d, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=7200)
    txt = open(log).read(); ok = p.returncode == 0 and os.path.exists(f"{d}/Events/run_s2/tag_1_pythia8_events.hepmc.gz")
    m = re.search(r"Nb of events after matching/merging\s*:\s*(\d+)", txt); x = re.search(r"Matched cross-section\s*:\s*([0-9.eE+-]+)\s*\+-\s*([0-9.eE+-]+)", txt)
    r = dict(tag=tag, channel=row.channel, mass_gev=int(row.mass_gev), seed=int(row.seed), ebeam_gev=EBEAM, n_generated=N_GEN, n_matched=int(m.group(1)) if m else None,
             matched_xsec_pb=float(x.group(1)) if x else None, matched_xsec_err_pb=float(x.group(2)) if x else None, wall_s=round(time.time() - t0, 1),
             status="ok" if ok else "failed", exit_code=p.returncode)
    if ok: open(done, "w").write(f"{r}\n")
    print(r, flush=True); return r

if __name__ == "__main__":
    rows = GEN13[GEN13.apply(lambda r: f"{r.channel}_{r.mass_gev}gev", axis=1).isin(os.environ["S2_ONLY"].split(","))] if os.environ.get("S2_ONLY") else GEN13
    rows = rows.sort_values("wall_s", ascending=False).to_dict("records")   # longest first (dicts: picklable)
    with mp.Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as pool: res = pool.map(gen, rows, chunksize=1)
    S = []
    for row in GEN13.itertuples():
        f = f"{RUNS}/{row.channel}_{int(row.mass_gev)}gev/checkpoints_DONE_generation.txt"
        if os.path.exists(f): S.append(eval(open(f).read()))
    if os.environ.get("S2_ONLY"): sys.exit(0)                                # validation run: no summary table
    S = pd.DataFrame(S, columns=["tag", "channel", "mass_gev", "seed", "ebeam_gev", "n_generated", "n_matched", "matched_xsec_pb", "matched_xsec_err_pb", "wall_s", "status", "exit_code"]).sort_values(["channel", "mass_gev"]); S.to_csv(f"{HERE}/generation_statistics_13p6TeV.csv", index=False); print(S.to_string(index=False))
    print("GEN_EXIT=0" if (S.status == "ok").sum() == 13 else "GEN_INCOMPLETE")
