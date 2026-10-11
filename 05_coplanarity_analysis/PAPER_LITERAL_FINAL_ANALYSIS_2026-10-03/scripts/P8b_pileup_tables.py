#!/usr/bin/env python3
"""Phase 8 tables: literal pile-up-only background (mu = 50) vs the paper's quoted rates and vs the frozen sweep.
Paper Sec. IV: '~1e-3 of background events contain a plane with >= 1 hit in 4 of 8 layers'; '6e-5 with 8/8'.
Inputs : ../logs/P8_chunks_LITERAL/chunk_*.csv (literal), sweep_mu_2026-09-16/pileup_mu50_n5000_sec3c_fullcutflow_v1.csv (frozen).
Outputs: ../tables/pileup_cutflow.csv, ../tables/pileup_per_event_literal.csv, ../tables/pileup_layer_multiplicity.csv"""
import os, sys, glob, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from stats_utils import row
T = f"{HERE}/../tables"
lit = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{HERE}/../logs/P8_chunks_LITERAL/chunk_*.csv"))]).sort_values("event_i")
assert lit.event_i.is_unique
fro = pd.read_csv(f"{HERE}/../../sweep_mu_2026-09-16/pileup_mu50_n5000_sec3c_fullcutflow_v1.csv")
lit.to_csv(f"{T}/pileup_per_event_literal.csv", index=False)
PAPER = {"has_4_of_8_plane": 1e-3, "has_8_of_8_plane": 6e-5}
out = []
for name, d in [("LITERAL (B, SCT 34/1160 um, merging)", lit), ("FROZEN project sweep (eta-cone |eta|<1.8, SCT 34/1160 um, no pixel merging)", fro)]:
    n = len(d); prev = pd.Series(True, index=d.index)
    for st, col, seq in [("plane with >=1 hit in >=4/8 layers (paper 1e-3)", "has_4_of_8_plane", False),
                         ("plane with >=1 hit in 8/8 layers = relaxed control (paper 6e-5)", "has_8_of_8_plane", False),
                         ("Sec. III C plane", "sec3c_plane_found", True), ("hit multiplicity 7x2+1", "hit_multiplicity_pass", True),
                         ("dw < 1 cm", None, True), ("ds < 0.01 cm", "delta_s_pass_0p01", True), ("final Sec. IV", "final_sec_iv_pass", True)]:
        m = (d.sec3c_dw < 1) if col is None else d[col].astype(str) == "True"
        if seq: m = prev & m; prev = m
        r = dict(config=name, stage=st, sequential=seq, **row(int(m.sum()), n, PAPER.get(col)))
        r["event_ids"] = " ".join(map(str, d.event_i[m])) if m.sum() <= 60 else f"({int(m.sum())} events)"
        out.append(r)
o = pd.DataFrame(out); o.to_csv(f"{T}/pileup_cutflow.csv", index=False)
mult = lit[[f"n_hits_L{i}" for i in range(1, 9)] + ["n_hits", "n_pu_interactions"]].describe().T
mult.to_csv(f"{T}/pileup_layer_multiplicity.csv")
print(len(lit), "literal events"); print(o[["config", "stage", "k", "n", "frac", "cp95_upper_one_sided", "p_exact_vs_paper"]].to_string()); print(mult[["mean", "50%"]])
