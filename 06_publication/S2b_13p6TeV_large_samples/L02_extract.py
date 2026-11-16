#!/usr/bin/env python3
"""Stage 2b, step 2: matched events of every generated chunk -> quirk four-momenta, charges, trigger flag. Same parser, charge assignment and trigger
(pT(QQ) > 200 GeV) as S2_02_extract.py. Events of all chunks of a mass point are concatenated; event_id = 100000 + running index (the per-event seeds of the
propagation, SeedSequence([6, mass, event_id]), then never coincide with those of the Stage 2 samples, which use 0, 1, 2, ...).
Usage: L02_extract.py <channel> <mass>. Output: inputs/<channel>_<mass>gev_events.csv, inputs/counts.csv (one row per mass point, rewritten). Env (2026-11-16): COPLANARITY_BASE, S2B_RUNS, L02_OUT (output dir), PYTHIA8DATA."""
import os, sys, glob, ast, pandas as pd, numpy as np
os.environ.setdefault("PYTHIA8DATA", "/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc")
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study"); RUNS = os.environ.get("S2B_RUNS", "/home/rafia/hep_tools/S2b_large_runs")
sys.path.insert(0, f"{BASE}/05_coplanarity_analysis/madgraph_pilot_v1"); sys.path.insert(0, f"{BASE}/01_signal_generation")
from extract_pilot_data import parse_hepmc
from extract_quirk_momenta import _make_rhadron_charge_lookup
OUT = os.environ.get("L02_OUT", f"{HERE}/inputs"); os.makedirs(OUT, exist_ok=True); OFFSET = 100000
ch, m = sys.argv[1], int(sys.argv[2]); tag = f"{ch}_{m}gev"; parts = []; gen = []
for d in sorted(glob.glob(f"{RUNS}/{tag}_c[0-9][0-9]")):
    done = f"{d}/checkpoints_DONE_generation.txt"
    if not os.path.exists(done): print("not generated:", d); continue
    g = ast.literal_eval(open(done).read()); gen.append(g); h = f"{d}/Events/run_l/tag_1_pythia8_events.hepmc.gz"
    df = parse_hepmc(h, 9000011, m, 5.0, True) if ch == "EW" else parse_hepmc(h, 1000006, m, 30.0, False)
    df = df[df["n_quirks_found"] == 2].reset_index(drop=True); assert len(df) == g["n_matched"], (d, len(df), g["n_matched"])
    df.insert(0, "chunk", g["chunk"]); parts.append(df)
ev = pd.concat(parts, ignore_index=True); ev.insert(0, "event_id", OFFSET + np.arange(len(ev)))
if ch == "colored":
    q = _make_rhadron_charge_lookup(); ev["charge1"] = ev.pdg1.map(q); ev["charge2"] = ev.pdg2.map(q)
else:
    q = {9000011: -1.0, -9000011: 1.0}; ev["charge1"] = ev.pdg1.map(q); ev["charge2"] = ev.pdg2.map(q)
ev.to_csv(f"{OUT}/{tag}_events.csv", index=False)
G = pd.DataFrame(gen); w = G.n_generated                                                   # sigma: generated-event weighted mean of the chunks, error combined
sig = (G.matched_xsec_pb * w).sum() / w.sum() * 1e3; err = np.sqrt(((G.matched_xsec_err_pb * w) ** 2).sum()) / w.sum() * 1e3
tr = ev.trigger_proxy_pass.astype(str) == "True"; chg = (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
row = dict(channel=ch, mass_gev=m, n_chunks=len(G), n_generated=int(w.sum()), n_matched=len(ev), sigma_matched_fb=sig, sigma_matched_err_fb=err, n_trigger=int(tr.sum()),
           n_trigger_both_charged=int((tr & chg).sum()))
f = f"{OUT}/counts.csv"; C = pd.read_csv(f) if os.path.exists(f) else pd.DataFrame()
C = pd.concat([C[~((C.channel == ch) & (C.mass_gev == m))] if len(C) else C, pd.DataFrame([row])]).sort_values(["channel", "mass_gev"]); C.to_csv(f, index=False)
print(row); print("L02_EXIT=0")
