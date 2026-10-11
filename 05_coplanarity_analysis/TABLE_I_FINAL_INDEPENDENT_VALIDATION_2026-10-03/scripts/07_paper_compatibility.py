#!/usr/bin/env python3
"""
Task 5: paper-vs-project compatibility for the confirmation results, distinguishing
  (i)  difference from the QUOTED central value (paper value treated as exact; exact binomial p), and
  (ii) a two-sample comparison in which the paper value is itself a measurement with
       binomial uncertainty from its (inferred) sample size plus two-decimal rounding:
         z = (p_ours - p_paper) / sqrt( p_ours(1-p_ours)/n_ours + p_paper(1-p_paper)/n_paper + 0.0029^2 )
       evaluated for the low and high ends of the inferred paper denominators
       (tables/paper_sample_size_inference.json) and for a deliberately small n_paper = 300 (stress test).
The paper states no sample sizes; (ii) is therefore an inference-based sensitivity, not a proof.
"""
import json, math, os
import pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
inf = json.load(open(f"{T}/paper_sample_size_inference.json"))["implied_paper_denominators_range"]
NP = {("EW", "trigger"): inf["EW"]["N_matched"], ("EW", "fiducial"): inf["EW"]["N_trig"], ("EW", "reconstruction"): inf["EW"]["N_fid"],
      ("COL", "trigger"): [round(inf["COL"]["N_trig_charged"][0] / 0.30 / 0.24 * 0.24 / 0.24), round(inf["COL"]["N_trig_charged"][1] / 0.30 / 0.24)],
      ("COL", "fiducial"): inf["COL"]["N_trig_charged"], ("COL", "reconstruction"): inf["COL"]["N_fid"]}
NP[("COL", "trigger")] = [round(inf["COL"]["N_trig_charged"][0] / 0.30 / 0.24), round(inf["COL"]["N_trig_charged"][1] / 0.30 / 0.24)]
c = pd.read_csv(f"{T}/confirmation_efficiencies.csv")
rows = []
for r in c.itertuples():
    for label, npap in (("paper n low", NP[(r.benchmark, r.quantity)][0]), ("paper n high", NP[(r.benchmark, r.quantity)][1]), ("stress n=300", 300)):
        var = r.eff * (1 - r.eff) / r.N_total + r.paper * (1 - r.paper) / npap + 0.0029 ** 2
        z = (r.eff - r.paper) / math.sqrt(var)
        rows.append(dict(benchmark=r.benchmark, geometry=r.geometry, sct_z=r.sct_z, dw_convention=r.dw_convention, quantity=r.quantity,
                         N_pass=r.N_pass, N_total=r.N_total, eff=r.eff, paper=r.paper, p_quoted_value_exact=r.p_exact,
                         paper_n_assumption=label, paper_n=npap, z_two_sample=z, p_two_sample=2 * stats.norm.sf(abs(z))))
o = pd.DataFrame(rows); o.to_csv(f"{T}/confirmation_paper_compatibility.csv", index=False)
pd.set_option("display.width", 250)
x = o[(o.geometry == "B") & (o.dw_convention == "W1") & (o.paper_n_assumption != "stress n=300")]
print(x.pivot_table(index=["benchmark", "quantity", "sct_z"], columns="paper_n_assumption", values="p_two_sample").round(4).to_string())
