#!/usr/bin/env python3
"""07 background step Z01 (2026-11-17): a larger Z(nunu)+gamma+j photon sample at 13.6 TeV for C01 (laptop: MG5 is installed here).
Same process and cards as the production sample (06_publication/S2_.../S2_06_zgamma_generate.py, label 13p6TeV: p p > z a j, z > vl vl~, MG5 3.7.3 + Pythia8,
ebeam 6800 GeV, run card from that run's banner), in chunks of 10 000 events; per chunk only iseed is changed (271000 + chunk, never the production seed 27).
Each chunk is an independent MG5 run in its own copy of the process directory. Photons are extracted with the unchanged
02_backgrounds/photon_conversion/extract_zgamma_photons.build_dataframe (hardest photon, post-shower MET > 200 GeV).
Usage: Z01_zgamma_large.py <n_chunks> [first_chunk]      (100k photons: n_chunks = 10). Resumable: finished chunks are skipped.
Output: /home/rafia/hep_tools/07_zgamma_runs/chunk_<c>/ (MG5 runs), backgrounds/inputs_zgamma_large/zgamma_photons_large.csv (column event = 0..N-1, chunk),
        backgrounds/inputs_zgamma_large/zgamma_xsec_large.txt (sigma_generated_pb = event-weighted mean over chunks, n_generated, n_events_after_MET,
        sigma_after_MET_pb), backgrounds/inputs_zgamma_large/chunks.csv. Env: COPLANARITY_BASE, ZG_RUNS (run folder), HEP_BIN."""
import os, re, sys, subprocess, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study")
TEMPLATE = "/home/rafia/hep_tools/S2_zgamma_runs/13p6TeV"; RUNS = os.environ.get("ZG_RUNS", "/home/rafia/hep_tools/07_zgamma_runs")
HEP_BIN = os.environ.get("HEP_BIN", "/home/rafia/miniconda3/envs/hep/bin"); OUT = f"{HERE}/inputs_zgamma_large"; NEV = 10000
sys.path.insert(0, f"{BASE}/02_backgrounds/photon_conversion")
from extract_zgamma_photons import build_dataframe
card0 = re.search(r"<MGRunCard>\s*<!\[CDATA\[\n(.*?)\]\]>\s*</MGRunCard>", open(f"{TEMPLATE}/Events/run_s2/run_s2_tag_1_banner.txt").read(), re.S).group(1)
assert re.search(r"^\s*6800\.0\s*= ebeam1", card0, re.M) and re.search(r"^\s*10000\s*= nevents", card0, re.M) and re.search(r"^\s*27\s*= iseed", card0, re.M)


def chunk(c):
    d = f"{RUNS}/chunk_{c:02d}"; hep = f"{d}/Events/run_z01/tag_1_pythia8_events.hepmc.gz"; seed = 271000 + c
    if not os.path.exists(hep):
        os.makedirs(RUNS, exist_ok=True)
        subprocess.run(["rsync", "-a", "--exclude=Events/*", "--exclude=*.log", f"{TEMPLATE}/", f"{d}/"], check=True)
        card = re.sub(r"^\s*27\s*= iseed", f" {seed} = iseed", card0, flags=re.M); assert re.search(rf"^\s*{seed} = iseed", card, re.M)
        open(f"{d}/Cards/run_card.dat", "w").write(card)
        env = os.environ.copy(); env.pop("PYTHIA8DATA", None); env["PATH"] = f"{HEP_BIN}:{env['PATH']}"
        with open(f"{d}/gen_run_z01.log", "w") as f:
            p = subprocess.run(["./bin/generate_events", "run_z01", "-f"], cwd=d, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=4 * 3600)
        assert p.returncode == 0 and os.path.exists(hep), f"chunk {c} failed, see {d}/gen_run_z01.log"
    x = float(re.search(r"Integrated weight \(pb\)\s*:\s*([0-9.eE+-]+)", open(f"{d}/Events/run_z01/run_z01_tag_1_banner.txt").read()).group(1))
    pc = f"{OUT}/chunk_{c:02d}_photons.csv"
    if not os.path.exists(pc): build_dataframe(hep).to_csv(pc, index=False)
    return dict(chunk=c, seed=seed, n_generated=NEV, sigma_generated_pb=x, n_after_MET=len(pd.read_csv(pc)))


if __name__ == "__main__":
    n, first = int(sys.argv[1]), (int(sys.argv[2]) if len(sys.argv) > 2 else 0); os.makedirs(OUT, exist_ok=True); rows = []
    for c in range(first, first + n):
        r = chunk(c); rows.append(r); print("Z01 chunk", r, flush=True)
    done = sorted(int(f[6:8]) for f in os.listdir(OUT) if f.startswith("chunk_") and f.endswith("_photons.csv"))
    C = pd.DataFrame([chunk(c) for c in done]); C.to_csv(f"{OUT}/chunks.csv", index=False)
    P = pd.concat([pd.read_csv(f"{OUT}/chunk_{c:02d}_photons.csv").assign(chunk=c) for c in done], ignore_index=True)
    P["source_event"] = P["event"]; P["event"] = range(len(P)); P.to_csv(f"{OUT}/zgamma_photons_large.csv", index=False)
    ng = int(C.n_generated.sum()); sig = float((C.sigma_generated_pb * C.n_generated).sum() / ng)
    open(f"{OUT}/zgamma_xsec_large.txt", "w").write(f"ebeam_GeV 6800.0\nsigma_generated_pb {sig}\nn_generated {ng}\nn_events_after_MET {len(P)}\nsigma_after_MET_pb {sig * len(P) / ng}\n")
    print(f"Z01: chunks {done}, generated {ng}, photons after MET {len(P)}, sigma {sig:.5g} pb (production 0.25205 pb)"); print("Z01_EXIT=0")
