#!/usr/bin/env python3
"""paper_project_comparison.csv: every LITERAL signal efficiency (each sample separately) vs paper Table I.
(1) one-sample exact binomial vs the quoted central value (paper value treated as exact; it publishes no counts);
(2) Fisher two-sample test using paper sample sizes INFERRED from Fig. 5 histogram quantisation
    (~1075 EW / ~525 colored reconstructed events; TABLE_I_FINAL_INDEPENDENT_VALIDATION_2026-10-03 report l.54),
    propagated back through the paper's own efficiencies: n_reco = N_fig5/eps_reco, n_fid = n_reco/eps_fid,
    n_trig = n_fid/eps_trig. These n are INFERRED, not published.
Background rows (pile-up, conversion) are appended by P12_background_rows if the background tables exist."""
import os, pandas as pd, numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
s = pd.read_csv(f"{T}/signal_efficiency_statistics.csv")
s = s[(s.config == "LITERAL")].copy(); s["quantity"] = s.quantity.replace({"reconstruction (full Sec. IV SR)": "reconstruction"})
PAPER = {"EW": dict(trigger=0.10, fiducial=0.28, reconstruction=0.72, NF5=1075), "COL": dict(trigger=0.24, fiducial=0.28, reconstruction=0.35, NF5=525)}
rows = []
for _, r in s.iterrows():
    P = PAPER[r.benchmark]; n_reco = P["NF5"] / P["reconstruction"]; n_fid = n_reco / P["fiducial"]; n_trig = n_fid / P["trigger"]
    q = r.quantity if r.quantity in P else None
    if q is None: continue
    n_p = {"reconstruction": n_reco, "fiducial": n_fid, "trigger": n_trig}[q]; k_p = round(P[q] * n_p)
    fisher = stats.fisher_exact([[int(r.N_pass), int(r.N_total - r.N_pass)], [k_p, round(n_p) - k_p]]).pvalue
    rows.append(dict(sample=r["sample"], benchmark=r.benchmark, quantity=q, project_k=int(r.N_pass), project_n=int(r.N_total), project_eff=r.eff,
                     wilson95_lo=r.wilson95_lo, wilson95_hi=r.wilson95_hi, cp95_lo=r.cp95_lo, cp95_hi=r.cp95_hi, paper_eff=P[q],
                     paper_inside_wilson95=r.paper_inside_wilson95, p_exact_one_sample=r.p_exact_vs_paper_quoted,
                     paper_n_INFERRED=round(n_p), paper_k_INFERRED=k_p, p_fisher_vs_inferred_paper=fisher,
                     verdict="compatible" if r.p_exact_vs_paper_quoted > 0.05 else "differs",
                     note="paper publishes no raw counts; paper n inferred from Fig. 5 quantisation"))
o = pd.DataFrame(rows); o.to_csv(f"{T}/paper_project_comparison.csv", index=False)
print(o[["sample", "quantity", "project_k", "project_n", "project_eff", "paper_eff", "p_exact_one_sample", "paper_n_INFERRED", "p_fisher_vs_inferred_paper", "verdict"]].to_string())
