#!/usr/bin/env python3
"""07 X10 (2026-11-17): how converted photons pass with pile-up. For each setting, the mu = 0 run gives the "near-misses"
(winning plane with dw < 1 cm and ds < 0.01 cm that fails only the hit-multiplicity cut). The same photon-region rows at mu = 20 / 50
(same photons, seeds, conversion points; only pile-up added) are classified as: passing that were near-misses at mu = 0, passing that
already passed at mu = 0, other passing; and the winning plane's pile-up hit count. Completion probability = (passing near-misses) / (near-misses).
Writes tables/X10_pileup_completion.csv and tables/X10_passing_rows_A580.csv."""
import os, glob, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"
SETS = [("S2_Run3_ATLAS", "A580", "C01_atlas_A580_mu{}"), ("S2_Run3_ATLAS", "Z0", "C01_atlas_mu{}"), ("S1_Run3_Ideal", "A580", "C01_stage2_A580_mu{}"),
        ("S2_Run3_ATLAS", "A580", "C01_atlas_A580_100k_mu{}"), ("S1_Run3_Ideal", "A580", "C01_stage2_A580_100k_mu{}")]   # 100k: 90 980 photons (Z01), server pool 94e81e1f


def load(run, sct):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{R}/backgrounds/runs/{run}/chunk_*.csv"))], ignore_index=True)
    d = d[d.sct == sct].copy()
    for c in ("plane", "mult", "ds_pass", "dw_pass", "final"): d[c] = d[c].astype(str).str.lower().eq("true")
    return d.set_index(["event", "region"]).sort_index()


rows, pas = [], []
for setup, sct, pat in SETS:
    D0 = load(pat.format(0), sct); nm = D0.plane & D0.dw_pass & D0.ds_pass & ~D0.mult
    for mu in (20, 50):
        D = load(pat.format(mu), sct); assert D.index.equals(D0.index); f = D.final
        rows.append(dict(setup=setup, sct=sct, sample="100k" if "100k" in pat else "9130", mu=mu, rows=len(D0), final_mu0=int(D0.final.sum()), near_miss_mu0=int(nm.sum()), final=int(f.sum()),
                         final_photons=D[f].index.get_level_values(0).nunique(), final_from_near_miss=int((f & nm).sum()), final_already_mu0=int((f & D0.final).sum()),
                         final_other=int((f & ~nm & ~D0.final).sum()), final_with_pileup_hit=int((D.winner_pileup_hits[f] > 0).sum()),
                         completion_prob=(f & nm).sum() / max(nm.sum(), 1)))
        if sct == "A580":
            p = D[f][["region_element", "p_conv", "ds", "dw", "winner_conv_hits", "winner_pileup_hits", "winner_layers"]].copy()
            p["mu0_ds"], p["mu0_dw"], p["mu0_mult"], p["mu0_winner_hits"] = D0.ds[f], D0.dw[f], D0.mult[f], D0.winner_conv_hits[f]
            pas.append(p.reset_index().assign(setup=setup, sample="100k" if "100k" in pat else "9130", mu=mu))
X = pd.DataFrame(rows); X.to_csv(f"{T}/X10_pileup_completion.csv", index=False)
P = pd.concat(pas, ignore_index=True); P.to_csv(f"{T}/X10_passing_rows_A580.csv", index=False)
pd.set_option("display.width", 250); print(X.round(4).to_string(index=False)); print(); print(P.round(4).to_string(index=False)); print("X10_EXIT=0")
