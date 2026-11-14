#!/usr/bin/env python3
"""Stage 2, step 6: converted-photon background sample at sqrt(s) = 13.6 TeV. The 13 TeV photons (02_backgrounds/photon_conversion/zgamma_photons.csv)
come from /home/rafia/hep_tools/zgamma_background_test, run_02: p p > z a j, z > vl vl~ (MG5 3.7.3 + Pythia8), 10000 events, iseed 27, MET > 200 GeV,
pT(gamma) > 0.5 GeV. Here: the process directory is copied, the run card is taken from the run_02 banner (the card in Cards/ was edited after run_02:
nevents 300, iseed 0, draj 0.1), and only ebeam1 = ebeam2 is changed. The hep env is put first in PATH (as S2_01_generate.py).
Photons extracted with the unchanged extract_zgamma_photons.build_dataframe (hardest photon, post-shower MET > 200 GeV).
Usage: S2_06_zgamma_generate.py <label> <ebeam GeV>   (13TeV_check 6500: validation, must reproduce zgamma_photons.csv; 13p6TeV 6800: production)
Output: /home/rafia/hep_tools/S2_zgamma_runs/<label>/, inputs/zgamma_photons_<label>.csv, inputs/zgamma_xsec_<label>.txt"""
import os, re, sys, subprocess, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = "/home/rafia/coplanarity_study"
SRC = "/home/rafia/hep_tools/zgamma_background_test"; BANNER = f"{SRC}/Events/run_02/run_02_tag_1_banner.txt"
HEP_BIN = "/home/rafia/miniconda3/envs/hep/bin"
sys.path.insert(0, f"{BASE}/02_backgrounds/photon_conversion")
from extract_zgamma_photons import build_dataframe

label, ebeam = sys.argv[1], float(sys.argv[2]); d = f"/home/rafia/hep_tools/S2_zgamma_runs/{label}"; os.makedirs(f"{HERE}/inputs", exist_ok=True)
hep = f"{d}/Events/run_s2/tag_1_pythia8_events.hepmc.gz"
if not os.path.exists(hep):
    if not os.path.exists(d):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        subprocess.run(["rsync", "-a", "--exclude=Events/*", "--exclude=*.log", f"{SRC}/", f"{d}/"], check=True)
    card = re.search(r"<MGRunCard>\s*<!\[CDATA\[\n(.*?)\]\]>\s*</MGRunCard>", open(BANNER).read(), re.S).group(1)
    card = re.sub(r"^\s*[0-9.]+(\s*= ebeam[12])", rf"     {ebeam}\1", card, flags=re.M)
    assert len(re.findall(rf"^\s*{ebeam}\s*= ebeam[12]", card, re.M)) == 2 and re.search(r"^\s*10000 = nevents", card, re.M) and re.search(r"^\s*27 = iseed", card, re.M)
    open(f"{d}/Cards/run_card.dat", "w").write(card)
    env = os.environ.copy(); env.pop("PYTHIA8DATA", None); env["PATH"] = f"{HEP_BIN}:{env['PATH']}"
    with open(f"{d}/gen_run_s2.log", "w") as f:
        p = subprocess.run(["./bin/generate_events", "run_s2", "-f"], cwd=d, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=4 * 3600)
    assert p.returncode == 0 and os.path.exists(hep), f"generation failed, see {d}/gen_run_s2.log"
x = float(re.search(r"Integrated weight \(pb\)\s*:\s*([0-9.eE+-]+)", open(f"{d}/Events/run_s2/run_s2_tag_1_banner.txt").read()).group(1))
df = build_dataframe(hep); df.to_csv(f"{HERE}/inputs/zgamma_photons_{label}.csv", index=False)
open(f"{HERE}/inputs/zgamma_xsec_{label}.txt", "w").write(f"ebeam_GeV {ebeam}\nsigma_generated_pb {x}\nn_events_after_MET {len(df)}\nsigma_after_MET_pb {x * len(df) / 10000}\n")
print(label, "sigma (pb)", x, "photons after MET > 200 GeV", len(df), "sigma after MET (pb)", x * len(df) / 10000, flush=True); print("ZGAMMA_EXIT=0")
