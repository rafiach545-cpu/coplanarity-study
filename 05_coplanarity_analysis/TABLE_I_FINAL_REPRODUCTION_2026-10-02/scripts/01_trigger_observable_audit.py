#!/usr/bin/env python3
"""
First-principles EW/colored trigger audit: the paper's trigger observable versus
calorimeter-type alternatives, computed on the SAME showered events (driver v3, frozen
shower settings; EW2000/COL2000 runs are event-identical to the frozen samples).
  T0  paper: pT of quirk/anti-quirk centre-of-mass system > 200 GeV (Sec. III B)
  T1  visible MET > 200 GeV: |sum pT| of final-state particles with |eta|<4.9, quirks/R-hadrons
      and neutrinos treated as invisible (the HLT 'lack of a track' interpretation)
  T2  leading anti-kT R=0.4 jet pT > 200 GeV, |eta|<4.5 (jets from visible particles)
  T3  leading anti-kT R=0.4 jet pT > 200 GeV, |eta|<2.8
  T4  T1 AND T3
Denominator: matched events (all events written by the MLM-matched shower).
T1-T4 are NOT stated in the paper: systematic tests only.
"""
import math, pandas as pd
from scipy import stats
W = "/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/runs/V3OBS"
def wil(k, n, z=1.959964):
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d; h = z/d*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return c-h, c+h
PAPER = {"EW": 0.10, "COL": 0.24}
rows = []
for B, samples in (("EW", ["EW1000", "EW2000", "G0_EW"]), ("COL", ["COL1000", "COL2000", "G0_COL"])):
    d = pd.concat([pd.read_csv(f"{W}/{s}/events.csv").assign(sample=s) for s in samples])
    var = {"T0_paper_pair_pT": d.pair_pt_final > 200, "T1_visible_MET": d.met_vis_eta49 > 200,
           "T2_leadjet_eta4.5": d.lead_jet_pt_eta45 > 200, "T3_leadjet_eta2.8": d.lead_jet_pt_eta28 > 200,
           "T4_MET_and_leadjet2.8": (d.met_vis_eta49 > 200) & (d.lead_jet_pt_eta28 > 200)}
    for name, m in var.items():
        k, n = int(m.sum()), len(d); lo, hi = wil(k, n)
        rows.append(dict(bench=B, variant=name, N_pass=k, N_total=n, eff=k/n, ci95_lo=lo, ci95_hi=hi,
                         paper=PAPER[B], paper_in_ci=lo <= PAPER[B] <= hi, p_exact=stats.binomtest(k, n, PAPER[B]).pvalue))
r = pd.DataFrame(rows); r.to_csv("tables/trigger_observable_audit.csv", index=False)
pd.set_option("display.width", 200); print(r.round(4).to_string(index=False))
p = r.pivot(index="variant", columns="bench", values="eff"); p["EW/COL"] = p.EW / p.COL
print(p.round(3).to_string()); print("paper EW/COL ratio = 0.417")
