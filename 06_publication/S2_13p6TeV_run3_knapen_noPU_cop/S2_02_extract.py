#!/usr/bin/env python3
"""Stage 2, step 2: per mass point, the matched 13.6 TeV events (S2_01_generate.py) -> quirk four-momenta, charges, trigger flag. Same parser, same charge
assignment and same trigger (pT(QQ) > 200 GeV) as the 13 TeV reproduction (PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts/F6_01_extract_events.py);
only the input runs and the output folder differ.
Output: inputs/<tag>_events.csv and inputs/counts.csv (this folder; same columns as fig6/inputs of the reproduction)."""
import os, sys, pandas as pd
os.environ.setdefault("PYTHIA8DATA", "/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc")   # R-hadron charge table (as P22a_minbias_pool.py)
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = "/home/rafia/coplanarity_study"
sys.path.insert(0, f"{BASE}/05_coplanarity_analysis/madgraph_pilot_v1"); sys.path.insert(0, f"{BASE}/01_signal_generation")
from extract_pilot_data import parse_hepmc
from extract_quirk_momenta import _make_rhadron_charge_lookup
RUNS = "/home/rafia/hep_tools/S2_13p6TeV_runs"; OUT = f"{HERE}/inputs"; os.makedirs(OUT, exist_ok=True)
GEN = pd.read_csv(f"{HERE}/generation_statistics_13p6TeV.csv"); assert (GEN.status == "ok").all() and len(GEN) == 13
rows = []
for g in GEN.sort_values(["channel", "mass_gev"]).itertuples():
    tag = f"{g.channel}_{int(g.mass_gev)}gev"; f = f"{OUT}/{tag}_events.csv"
    if not os.path.exists(f):
        h = f"{RUNS}/{tag}/Events/run_s2/tag_1_pythia8_events.hepmc.gz"
        df = parse_hepmc(h, 9000011, g.mass_gev, 5.0, True) if g.channel == "EW" else parse_hepmc(h, 1000006, g.mass_gev, 30.0, False)
        df = df[df["n_quirks_found"] == 2].reset_index(drop=True)
        if g.channel == "colored":
            ch = _make_rhadron_charge_lookup(); df["charge1"] = df.pdg1.map(ch); df["charge2"] = df.pdg2.map(ch)
        else:
            q = {9000011: -1.0, -9000011: 1.0}; df["charge1"] = df.pdg1.map(q); df["charge2"] = df.pdg2.map(q)
        df.to_csv(f, index=False)
    df = pd.read_csv(f); tr = df.trigger_proxy_pass.astype(str) == "True"; chg = (df.charge1.abs() > 0.5) & (df.charge2.abs() > 0.5)
    rows.append(dict(channel=g.channel, mass_gev=int(g.mass_gev), n_generated=int(g.n_generated), n_matched=len(df), sigma_matched_fb=g.matched_xsec_pb * 1e3,
                     sigma_matched_err_fb=g.matched_xsec_err_pb * 1e3, n_trigger=int(tr.sum()), n_trigger_both_charged=int((tr & chg).sum())))
    print(rows[-1], flush=True)
C = pd.DataFrame(rows); C.to_csv(f"{OUT}/counts.csv", index=False); print(C.to_string())
