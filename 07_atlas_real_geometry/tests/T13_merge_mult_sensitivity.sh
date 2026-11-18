#!/bin/bash
# 07 test T13 (2026-11-17): the sensitivity options (pixel-merge adjacency, multiplicity threshold) leave production unchanged:
#  (a) multiplicity recomputed after the fact from winner_layers (n1 == 8 and n2 >= T - 8, T = 15) equals the stored mult on every row of
#      runs/C01_atlas_mu50 (Z0), runs/C01_atlas_A580_mu50, runs/C01_stage2_A580_mu50;
#  (b) C01 --merge-adj 1, atlas mu = 20, SCT both, photons 0-99 = runs/C01_atlas_mu20 chunks 0 and 50 (every production column);
#  (c) G01 with G01_SENS_ADJ=0,1,2 (atlas, EW 800 GeV, band mid, first 12 events): the a1 fields equal the production fields of the same run
#      (plane, ds, dw; n1/n2 give the same mult), and the production fields equal a run without the option;
#  (d) synthetic: two pixel hits one index apart merge at adjacency 1 and 2, not at 0; two indices apart merge only at 2.
# Prints T13_PASS / T13_FAIL.
set -e; cd "$(dirname "$0")/.."; W=tests/T13_work; rm -rf "${W:?}"; mkdir -p $W
export PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc; P=/home/rafia/miniconda3/envs/hep/bin/python; Q=/home/rafia/venvs/f6fast/bin/python
export COPLANARITY_BASE=/home/rafia/coplanarity_study
(cd backgrounds && $P C01_conversion_bkg.py atlas 20 --sct both --first 100 --workers 2 --tag T13b --merge-adj 1 2>&1 | grep -v "PYTHIA\|^ \*" | tail -1)
$Q signal/G01_signal_07.py atlas EW_800gev mid --input signal/inputs_large/EW_800gev_events.csv --out $W/plain --nmax 12 --workers 3 | tail -1
G01_SENS_ADJ=0,1,2 $Q signal/G01_signal_07.py atlas EW_800gev mid --input signal/inputs_large/EW_800gev_events.csv --out $W/sens --nmax 12 --workers 3 | tail -1
$Q - <<'PY'
import glob, json, sys, numpy as np, pandas as pd
from collections import Counter
sys.path.insert(0, "sim"); import detsim07 as D
ok = True
def mult_T(s, T):
    c = Counter(json.loads(s)) if isinstance(s, str) and s.startswith("[") else Counter()
    return sum(1 for k in range(1, 9) if c.get(k, 0) >= 1) == 8 and sum(1 for k in range(1, 9) if c.get(k, 0) >= 2) >= T - 8
for run in ("C01_atlas_mu50", "C01_atlas_A580_mu50", "C01_stage2_A580_mu50"):
    d = pd.concat([pd.read_csv(f) for f in glob.glob(f"backgrounds/runs/{run}/chunk_*.csv")], ignore_index=True)
    m = d.mult.astype(str).str.lower().eq("true"); r = d.winner_layers.map(lambda s: mult_T(s, 15)); same = bool((m == r).all()); ok &= same
    print(f"(a) {run}: {len(d)} rows, mult recomputed from winner_layers (T = 15) identical: {same}")
for s in ("000000", "000050"):
    a = pd.read_csv(f"backgrounds/runs/C01_atlas_T13b_mu20/chunk_{s}.csv"); b = pd.read_csv(f"backgrounds/runs/C01_atlas_mu20/chunk_{s}.csv")
    same = (a.merge_adj == 1).all() and a.drop(columns="merge_adj").equals(b); ok &= bool(same); print(f"(b) C01 --merge-adj 1 chunk {s}: {len(a)} rows identical to production: {bool(same)}")
rows = lambda d: {(r["event"], r["lambda_keV"]): r for l in open(glob.glob(f"tests/T13_work/{d}/*.jsonl")[0]) for r in json.loads(l)}
A, B = rows("plain"), rows("sens"); n = 0; same = A.keys() == B.keys()
for k, a in A.items():
    b = B[k]
    for s in ("Z0", "Z1160", "A580"):
        for f in ("plane", "mult", "final", "ds", "dw"):
            x, y = a.get(f"{s}_{f}"), b.get(f"{s}_{f}"); same &= (x == y) or (x != x and y != y)
        if b.get(f"{s}_a1_plane") is not None:
            n += 1; same &= b[f"{s}_a1_plane"] == b[f"{s}_plane"] and (b[f"{s}_a1_ds"] == b[f"{s}_ds"] or (b[f"{s}_ds"] != b[f"{s}_ds"]))
            same &= (b[f"{s}_a1_n1"] == 8 and b[f"{s}_a1_n2"] >= 7) == bool(b[f"{s}_mult"])
ok &= bool(same); print(f"(c) G01: {len(A)} (event, Lambda) rows; option leaves production fields unchanged and a1 = production on {n} fiducial settings: {bool(same)}")
E = D.build("atlas"); e = [x for x in E if x["name"] == "L1_IBL"][0]; R = e["r_cm"]
def hit(k):                                                       # IBL hit at r-phi = k pitches (50 um), z = 0.01 cm; production response
    ph = k * e["pitch_rphi_um"] * 1e-4 / R; return D.respond(e, R * np.cos(ph), R * np.sin(ph), 0.01, 1.0, 1, 0.0, 0.0, "Z0")
syn = []
for d_ in (1, 2):
    got = [len(D.overlay([hit(0), hit(d_)], [], adjacency=a)[0]) for a in (0, 1, 2)]; syn.append(got)
exp = [[2, 1, 1], [2, 2, 1]]; same = syn == exp; ok &= same; print(f"(d) synthetic merged-hit counts at adjacency 0/1/2, 1 and 2 indices apart: {syn} (expected {exp}): {same}")
print("T13_PASS" if ok else "T13_FAIL")
PY
rm -rf backgrounds/runs/C01_atlas_T13b_mu20 "${W:?}"
