#!/usr/bin/env python3
"""
Final Table I tables.

PRIMARY RESULT (declared before tabulation): pooled over ALL available samples per benchmark,
  EW  : EW1000 (frozen) + EW2000 (frozen) + G0_EW (independent MG5 seed 9101)
  COL : COL1000 (frozen) + COL2000 (frozen) + G0_COL (independent MG5 seed 9201)
No sample is dropped or selected. Per-sample values are reported alongside.

Final configuration ("B + R2 + A0"): frozen generation settings; trigger = pair pT > 200 GeV over
matched events; colored: both R-hadrons with non-zero charge; fiducial = finite ATLAS barrel (B),
all 16 crossings, max t < 25 ns; detector = pixel quantisation + SCT R-phi-only smearing (R2);
reconstruction = literal Sec. III C algorithm; eps_reco = full Sec. IV signal region / fiducial.

Statistics: Wilson score 95% interval (primary), Clopper-Pearson exact 95% (secondary),
exact two-sided binomial p-value vs the paper value.
"""
import math, json, os
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
PAPER = {"EW": dict(trigger=0.10, fiducial=0.28, reconstruction=0.72), "COL": dict(trigger=0.24, fiducial=0.28, reconstruction=0.35)}
# generation/matching/trigger counts (paper trigger definition) -- frozen samples from raw HepMC
# recount (EW_PAPER_REPRODUCTION_AUDIT_2026-10-02, COLORED raw parse), G0 from the validated driver
GEN = {"EW1000": dict(generated=1000, matched=511, trigger=89), "EW2000": dict(generated=2000, matched=1045, trigger=186),
       "G0_EW": dict(generated=2000, matched=1101, trigger=187),
       "COL1000": dict(generated=1000, matched=419, trigger=101), "COL2000": dict(generated=2000, matched=873, trigger=207),
       "G0_COL": dict(generated=2000, matched=855, trigger=186)}
SAMPLES = {"EW": ["EW1000", "EW2000", "G0_EW"], "COL": ["COL1000", "COL2000", "G0_COL"]}


def ci(k, n):
    z = 1.959964; p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    cp = (0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1), 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k))
    return c - h, c + h, cp


def main():
    pe = pd.read_csv(f"{T}/full_chain_per_event.csv")
    fin = pe[(pe.geom == "B") & (pe.model == "R2")]
    cut, comp = [], []
    for B, ss in SAMPLES.items():
        for label, group in [(s, [s]) for s in ss] + [(f"{B} POOLED (primary)", ss)]:
            g = {k: sum(GEN[s][k] for s in group) for k in ("generated", "matched", "trigger")}
            x = fin[fin.sid.isin(group)]
            n_trig_charged = len(x)
            f = x[x.fid == True]
            stages = [("generated (LHE events)", g["generated"]),
                      ("showered (all LHE events passed to Pythia8)", g["generated"]),
                      ("matched (MLM-accepted)", g["matched"]),
                      ("trigger: pair pT > 200 GeV", g["trigger"])]
            if B == "COL":
                stages.append(("trigger AND both R-hadrons charged (non-zero)", n_trig_charged))
            stages += [("fiducial (finite barrel, 16 crossings, t<25 ns)", len(f)),
                       ("plane found (Sec. III C selection)", int(f.plane.sum())),
                       ("hit multiplicity (SR cut 2)", int((f.plane & f.mult).sum())),
                       ("Delta_w < 1 cm (SR cut 3a)", int((f.plane & f.mult & f.dw_pass).sum())),
                       ("Delta_s < 0.01 cm (SR cut 3b)", int((f.plane & f.mult & f.dw_pass & f.ds_pass).sum())),
                       ("final signal region", int(f.final.sum()))]
            for i, (n, v) in enumerate(stages):
                cut.append(dict(bench=B, sample=label, step=i, stage=n, events=v))
            # efficiencies
            den_trig = g["matched"]
            den_fid = n_trig_charged
            effs = [("trigger", g["trigger"], den_trig, "pair pT>200 / matched" + ("; before charge requirement" if B == "COL" else "")),
                    ("fiducial", len(f), den_fid, "fiducial / trigger" + (" (both R-hadrons charged)" if B == "COL" else "")
                     + "; technical propagation exceptions counted as non-fiducial"),
                    ("reconstruction", int(f.final.sum()), len(f), "full Sec. IV signal region / (trigger AND fiducial)")]
            for q, k, n, note in effs:
                lo, hi, cp = ci(k, n); pv = PAPER[B][q]
                comp.append(dict(benchmark="EW" if B == "EW" else "Colored", sample=label, quantity=q, N_pass=k, N_total=n,
                                 efficiency=k / n, ci95_lo=lo, ci95_hi=hi, cp95_lo=cp[0], cp95_hi=cp[1],
                                 paper=pv, paper_inside_95ci=bool(lo <= pv <= hi),
                                 p_exact_binomial=stats.binomtest(k, n, pv).pvalue, notes=note))
    pd.DataFrame(cut).to_csv(f"{T}/final_cutflows.csv", index=False)
    c = pd.DataFrame(comp); c.to_csv(f"{T}/final_table_I_comparison.csv", index=False)
    # systematics: geometry x resolution, pooled
    sy = []
    for (gm, m), g in pe.groupby(["geom", "model"]):
        for B, ss in SAMPLES.items():
            x = g[g.sid.isin(ss)]; f = x[x.fid == True]
            for q, k, n in (("fiducial", len(f), len(x)), ("reconstruction", int(f.final.sum()), len(f))):
                lo, hi, _ = ci(k, n); pv = PAPER[B][q]
                sy.append(dict(geometry=gm, sct_model=m, benchmark=B, quantity=q, N_pass=k, N_total=n, efficiency=k / n,
                               ci95_lo=lo, ci95_hi=hi, paper=pv, paper_inside_95ci=bool(lo <= pv <= hi)))
    pd.DataFrame(sy).to_csv(f"{T}/final_systematics_geometry_resolution.csv", index=False)
    pd.set_option("display.width", 250, "display.max_colwidth", 70)
    print(c[c["sample"].str.contains("POOLED")].drop(columns=["notes"]).round(4).to_string(index=False))
    print()
    print(c[~c["sample"].str.contains("POOLED")][["sample", "quantity", "N_pass", "N_total", "efficiency", "ci95_lo", "ci95_hi", "paper_inside_95ci"]].round(4).to_string(index=False))
    print()
    cc = pd.DataFrame(cut); print(cc.pivot_table(index=["bench", "step", "stage"], columns="sample", values="events", aggfunc="first").to_string())
    print(); print(pd.DataFrame(sy).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
