#!/usr/bin/env python3
"""EW 800 GeV Table I numbers from the Fig. 6 sample (user's decision 2026-10-22: eps_trig = 0.148 everywhere, all EW efficiencies from that one sample).
Reads the stored Fig. 6 checkpoints (logs/F6_EW_800gev*_events.jsonl, same Table I pipeline, first crossing) - no new simulation - and writes
  tables/EW800_fig6_sample_lambda_scan.csv: per Lambda (1-5 keV) and SCT z setting: matched, triggered, fiducial, plane, + multiplicity, signal region, failures;
  FINAL_FIGURES/F43_lambda: eps_reco vs Lambda as F38_lambda, with the EW production points from the Fig. 6 sample (colored: Table I sample, unchanged)."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu, R_data_2026_10_15 as R
ROOT = f"{HERE}/.."; TR = lambda s: s.astype(str) == "True"
ev = pd.read_csv(f"{ROOT}/fig6/inputs/EW_800gev_events.csv"); trig = TR(ev.trigger_proxy_pass)
cnt = pd.read_csv(f"{ROOT}/fig6/inputs/counts.csv").set_index(["channel", "mass_gev"]).loc[("EW", 800)]
rows = []
for band in ("low", "mid", "high", "high_a"):
    f = f"{ROOT}/logs/F6_EW_800gev{'' if band == 'mid' else '_' + band}_events.jsonl"
    if os.path.exists(f): rows += [r for l in open(f) if l.strip() for r in json.loads(l)]
d = pd.DataFrame(rows); d = d[d.lambda_keV.isin([1, 2, 3, 4, 5])]
out = []
for lam, x in d.groupby("lambda_keV"):
    assert x.event.nunique() == len(x) == int(trig.sum()), (lam, len(x))                # every triggered event exactly once
    f = x[TR(x.fid)]
    for z in ("Z1160", "Z0"):
        out.append(dict(lambda_keV=int(lam), sct=z, matched=len(ev), triggered=int(trig.sum()), sigma_matched_fb=float(cnt.sigma_matched_fb), fid=len(f),
                        plane=int(TR(f[f"{z}_plane"]).sum()), mult=int((TR(f[f"{z}_plane"]) & TR(f[f"{z}_mult"])).sum()), sr=int(TR(f[f"{z}_final"]).sum()),
                        n_integration_fail=int((x.error.astype(str) != "").sum()), paper_reco=R.PAPER_L["EW2000"][int(lam)]))
O = pd.DataFrame(out); O.to_csv(f"{ROOT}/tables/EW800_fig6_sample_lambda_scan.csv", index=False)
G = pd.read_csv(f"{ROOT}/fig6/F6_N_grid.csv"); G = G[(G.channel == "EW") & (G.mass_gev == 800)]
for r in O.itertuples():                                                         # same numbers as the Fig. 6 grid
    q = G[(G.lambda_keV == r.lambda_keV) & (G.sct == r.sct)].iloc[0]; assert (int(q.n_fid), int(q.k)) == (r.fid, r.sr), r
print(O.to_string(index=False))

LS = R.lambda_scan(); D = R.d41(); rows = []
for _, r in LS[(LS["mode"] == "FIRST") & (LS["sample"] == "COL2000")].iterrows():
    rows.append(dict(sample="COL2000", lam=r.lambda_keV, setting=("SCT z 1.16 mm" if r.sct == "Z1160" else "no SCT z smearing"), k=r.k_ge2, n=r.n_fid, paper=r.paper_reco))
for r in O.itertuples(): rows.append(dict(sample="EW2000", lam=r.lambda_keV, setting=("SCT z 1.16 mm" if r.sct == "Z1160" else "no SCT z smearing"), k=r.sr, n=r.fid, paper=r.paper_reco))
for lam in (1, 2, 3, 4, 5): rows.append(dict(sample="EW2000", lam=lam, setting=f"EW LO sample ({D['n']} events), no SCT z smearing", k=D[lam]["sr"], n=D[lam]["fid"], paper=R.PAPER_L["EW2000"][lam]))
L = pd.DataFrame(rows); L["eps"] = L.k / L.n; L["sig"] = np.sqrt(L.eps * (1 - L.eps) / L.n)
def plot(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
    for ax, s, t in zip(axs, ("COL2000", "EW2000"), ("colored 1.8 TeV", "EW 800 GeV")):
        x = d[d["sample"] == s]; p = x.drop_duplicates("lam").sort_values("lam"); ax.plot(p.lam, p.paper, "s-", color=fu.INK, ms=6, lw=1.2, label="paper (Table I)")
        for st, c, off in (("no SCT z smearing", fu.SERIES[1], -0.08), ("SCT z 1.16 mm", fu.SERIES[0], 0.0)):
            y = x[x.setting == st].sort_values("lam"); ax.errorbar(y.lam + off, y.eps, yerr=y.sig, fmt="o-", color=c, ms=6, capsize=3, lw=1.4, label=f"this work, {st}")
        y = x[x.setting.str.startswith("EW LO sample")].sort_values("lam")
        if len(y): ax.errorbar(y.lam + 0.08, y.eps, yerr=y.sig, fmt="s--", color=fu.SERIES[2], ms=6, capsize=3, lw=1.4, label=y.setting.iloc[0])
        ax.set_xlabel("Λ (keV)"); ax.set_title(t, fontsize=9); ax.set_xticks(sorted(p.lam)); ax.set_ylim(0, 1)
    axs[0].set_ylabel("ε_reco ± simple binomial σ"); h, l = axs[1].get_legend_handles_labels(); fig.legend(h, l, fontsize=7, loc="lower center", ncol=4, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1)); return fig
fu.figure("F43_lambda", L, plot, "ε_reco vs Λ, first crossing, simple binomial σ: paper (black), this work without SCT z smearing and with SCT z 1.16 mm, EW leading-order sample (no SCT z "
          "smearing). Colored: Table I production sample; EW: the Fig. 6 sample at 800 GeV (ε_trig = 152/1024).",
          [f"{ROOT}/tables/EW800_fig6_sample_lambda_scan.csv", f"{R.T}/lambda_scan_summary.csv", f"{R.T}/lambda_scan_z1160_summary.csv"], "first crossing", os.path.abspath(__file__))
print("written F43_lambda")
