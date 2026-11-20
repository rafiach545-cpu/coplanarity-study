#!/usr/bin/env python3
"""09 step B01 (2026-11-19): Z(nunu)+jet background events at 13 TeV for Stage 1 · Run 2 · Ideal.
MG5 3.7.3 (sm model, 4-flavour p/j as in the Zgamma background): generate p p > vl vl~ j, showered and hadronised by Pythia8 through MG5
(default Pythia8 card: all unstable particles decay, production vertices are written to the HepMC). No ME/PS matching (one hard jet), as
the Zgamma background and the ATLAS low-mu slides. Run card: ebeam 6500 GeV, misset = 200 GeV (sum of neutrino pT; equals the signal's
trigger proxy pT(QQbar) > 200 GeV at LO), ptj = 20 GeV, all other values MG5 defaults (recorded in each run's banner).
Chunks: each chunk is an independent MG5 run in its own copy of the process directory, iseed = 391000 + chunk.
Usage: B01_generate_zvv.py <n_chunks> [first_chunk] [--nev N] [--sample zvv|wlnu] [--cores K]   pilot: B01_generate_zvv.py 1 0 --nev 1000
  --sample wlnu (2026-11-20): W(lnu)+jet, same cuts (paths09.SAMPLES), iseed = 392000 + chunk, data/B01_wlnu_chunks.csv.
  --cores K: MG5/Pythia cores per chunk (run_mode 2, nb_core K), to run several chunks side by side on a server.
Output: $ZVV_RUNS/chunk_<cc>/Events/run_b01/tag_1_pythia8_events.hepmc.gz and data/B01_chunks.csv (chunk, seed, n_generated, sigma_pb)."""
import os, re, sys, argparse, subprocess, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paths09 as P                                                              # noqa: E402
MG5 = P.MG5
HEP_BIN = os.environ.get("HEP_BIN", os.path.dirname(sys.executable))         # bin of the running conda env (laptop: envs/hep/bin)
SAMPLE = "zvv"; RUNS = TEMPLATE = PROC = SETTINGS = SEED0 = None


def use_sample(name):
    global SAMPLE, RUNS, TEMPLATE, PROC, SETTINGS, SEED0
    S = P.SAMPLES[name]; SAMPLE, RUNS, PROC, SETTINGS, SEED0 = name, S["runs"], S["proc"], S["settings"], S["seed0"]; TEMPLATE = f"{RUNS}/template"


use_sample("zvv")


def env():
    e = os.environ.copy(); e.pop("PYTHIA8DATA", None); e["PATH"] = f"{HEP_BIN}:{e['PATH']}"; return e


def make_template():
    if os.path.exists(f"{TEMPLATE}/bin/generate_events"): return
    os.makedirs(RUNS, exist_ok=True); cmd = f"{RUNS}/proc_b01.mg5"; open(cmd, "w").write(PROC.format(out=TEMPLATE))
    with open(f"{RUNS}/proc_b01.log", "w") as f: subprocess.run([MG5, cmd], cwd=RUNS, env=env(), stdout=f, stderr=subprocess.STDOUT, check=True)
    c = f"{TEMPLATE}/Cards"; subprocess.run(["cp", f"{c}/pythia8_card_default.dat", f"{c}/pythia8_card.dat"], check=True)
    for x in ("delphes_card.dat", "madspin_card.dat"):                     # shower only; no Delphes, no MadSpin
        if os.path.exists(f"{c}/{x}"): os.remove(f"{c}/{x}")


def run_card(nev, seed):
    card = open(f"{TEMPLATE}/Cards/run_card_default.dat").read()
    for k, v in {**SETTINGS, "nevents": str(nev), "iseed": str(seed)}.items():
        card, n = re.subn(rf"^\s*\S+(\s*=\s*{k}\b)", rf" {v}\1", card, flags=re.M); assert n == 1, (k, n)
    return card


def chunk(c, nev, cores=None):
    d = f"{RUNS}/chunk_{c:02d}"; hep = f"{d}/Events/run_b01/tag_1_pythia8_events.hepmc.gz"; seed = SEED0 + c
    if not os.path.exists(hep):
        subprocess.run(["rsync", "-a", "--exclude=Events/*", "--exclude=*.log", f"{TEMPLATE}/", f"{d}/"], check=True)
        open(f"{d}/Cards/run_card.dat", "w").write(run_card(nev, seed))
        if cores:
            mc = f"{d}/Cards/me5_configuration.txt"; t = open(mc).read()
            t = re.sub(r"^#?\s*run_mode\s*=.*$", "run_mode = 2", t, flags=re.M); t = re.sub(r"^#?\s*nb_core\s*=.*$", f"nb_core = {cores}", t, flags=re.M)
            open(mc, "w").write(t)
        with open(f"{d}/gen_run_b01.log", "w") as f:
            p = subprocess.run(["./bin/generate_events", "run_b01", "-f"], cwd=d, env=env(), stdout=f, stderr=subprocess.STDOUT, timeout=6 * 3600)
        assert p.returncode == 0 and os.path.exists(hep), f"chunk {c} failed, see {d}/gen_run_b01.log"
    ban = open(f"{d}/Events/run_b01/run_b01_tag_1_banner.txt").read()
    x = float(re.search(r"Integrated weight \(pb\)\s*:\s*([0-9.eE+-]+)", ban).group(1))
    n = int(re.search(r"^\s*(\d+)\s*=\s*nevents", ban, re.M).group(1))
    for k, v in SETTINGS.items(): assert re.search(rf"^\s*{re.escape(v)}\s*=\s*{k}\b", ban, re.M), f"banner {k} != {v}"
    return dict(chunk=c, seed=seed, n_generated=n, sigma_pb=x, hepmc=hep)


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("n", type=int); a.add_argument("first", type=int, nargs="?", default=0)
    a.add_argument("--nev", type=int, default=10000); a.add_argument("--sample", default="zvv", choices=sorted(P.SAMPLES))
    a.add_argument("--cores", type=int, default=None); A = a.parse_args(); use_sample(A.sample)
    make_template(); out = f"{HERE}/data/{P.SAMPLES[A.sample]['chunks']}"; os.makedirs(f"{HERE}/data", exist_ok=True)
    rows = [chunk(c, A.nev, A.cores) for c in range(A.first, A.first + A.n)]
    for r in rows: print("B01 chunk", r, flush=True)
    import fcntl                                                                  # several B01 jobs side by side (server): lock the table
    with open(out + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        old = pd.read_csv(out) if os.path.exists(out) else pd.DataFrame(columns=["chunk"])
        C = pd.concat([old[~old.chunk.isin([r["chunk"] for r in rows])], pd.DataFrame(rows)]).sort_values("chunk"); C.to_csv(out, index=False)
    print("B01_EXIT=0")
