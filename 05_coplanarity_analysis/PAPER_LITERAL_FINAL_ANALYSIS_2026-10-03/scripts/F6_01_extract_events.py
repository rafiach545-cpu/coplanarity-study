#!/usr/bin/env python3
"""Figure 6, step 1 (2026-10-17): per mass point, the matched events of the existing Figure 6 generation (figure6_full_v1, 13 points, MG5 3.7.3 +
Pythia8 MLM-matched HepMC in /home/rafia/hep_tools/figure6_full_v1_runs/<tag>/Events/run_fig6/) -> quirk four-momenta, charges, trigger flag.
Same parser and charge assignment as the figure6_full_v1 driver (extract_pilot_data.parse_hepmc; colored: Pythia8 R-hadron charge table) and as the
Table I production samples: EW = final-state qe+-, colored = final-state R-hadrons; trigger = pT(QQ) > 200 GeV.
Output: fig6/inputs/<tag>_events.csv (all events with 2 quirks found) and fig6/inputs/counts.csv. Raw HepMC files are read only."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.abspath(f"{HERE}/../../..")
sys.path.insert(0, f"{BASE}/05_coplanarity_analysis/madgraph_pilot_v1"); sys.path.insert(0, f"{BASE}/01_signal_generation")
from extract_pilot_data import parse_hepmc
from extract_quirk_momenta import _make_rhadron_charge_lookup
RUNS = "/home/rafia/hep_tools/figure6_full_v1_runs"; OUT = f"{HERE}/../fig6/inputs"; os.makedirs(OUT, exist_ok=True)
GEN = pd.read_csv(f"{BASE}/05_coplanarity_analysis/figure6_full_v1/TABLES/generation_statistics_13_mass_points.csv")
rows = []
for g in GEN.sort_values(["channel", "mass_gev"]).itertuples():
    tag = f"{g.channel}_{int(g.mass_gev)}gev"; f = f"{OUT}/{tag}_events.csv"
    if not os.path.exists(f):
        h = f"{RUNS}/{tag}/Events/run_fig6/tag_1_pythia8_events.hepmc.gz"
        df = parse_hepmc(h, 9000011, g.mass_gev, 5.0, True) if g.channel == "EW" else parse_hepmc(h, 1000006, g.mass_gev, 30.0, False)
        df = df[df["n_quirks_found"] == 2].reset_index(drop=True)
        if g.channel == "colored":
            ch = _make_rhadron_charge_lookup(); df["charge1"] = df.pdg1.map(ch); df["charge2"] = df.pdg2.map(ch)
        else:
            q = {9000011: -1.0, -9000011: 1.0}; df["charge1"] = df.pdg1.map(q); df["charge2"] = df.pdg2.map(q)
        df.to_csv(f, index=False)
    df = pd.read_csv(f); tr = df.trigger_proxy_pass.astype(str) == "True"; chg = (df.charge1.abs() > 0.5) & (df.charge2.abs() > 0.5)   # as F6_02 and Table I (|q| = 2 hadrons are charged)
    rows.append(dict(channel=g.channel, mass_gev=int(g.mass_gev), n_generated=int(g.n_generated), n_matched=len(df), sigma_matched_fb=g.matched_xsec_pb * 1e3,
                     sigma_matched_err_fb=g.matched_xsec_err_pb * 1e3, n_trigger=int(tr.sum()), n_trigger_both_charged=int((tr & chg).sum())))
    print(rows[-1], flush=True)
C = pd.DataFrame(rows); C.to_csv(f"{OUT}/counts.csv", index=False); print(C.to_string())
