#!/usr/bin/env python3
"""Publication, stage 1 (2026-11-03): sensitivity at 13 TeV, 139 fb^-1 (Run 2), Knapen et al. geometry (arXiv:1708.02243: IBL + 3 pixel + 4 SCT barrel layers,
pixel pitch as resolution, SCT 2x intrinsic), no pile-up on the signal, coplanarity (plane-finding) selection.
Input: the validated reproduction grid PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/fig6/F6_N_grid.csv (13 TeV, 300 fb^-1; MG5 3.7.3 + Pythia8 0+1 jet MLM, Nambu-Goto
integrator, same cuts). N = L sigma eps_trig [f_ch] k/n is linear in L, so every N column (central, Wilson 68% bounds, k = 0 upper limits, bounds of points not
propagated) is scaled by 139/300; points not propagated stay bounds (N_max < 3 at 300 fb^-1 stays < 3). Reach: the F6_04_summary.py algorithm, unchanged
(log10 N interpolated linearly in m at each grid Lambda; only points with k > 0 or bounds). Background (converted photons, sigma_gamma = 0.211 pb, 1% conversion):
scaled the same way. Both SCT z settings are given; the Knapen setting is SCT sigma_z = 1.16 mm (Z1160).
Output (this folder): S1_N_grid_139fb.csv, S1_reach_139fb.csv, S1_background_139fb.csv, S1_fig_reach_139fb.png/.pdf."""
import os, json, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03"
L_REF, L = 300.0, 139.0; S = L / L_REF
G = pd.read_csv(f"{REP}/fig6/F6_N_grid.csv")
NCOL = [c for c in G.columns if c.startswith("N_")] + ["L_sigma_eps_trig"]
G[NCOL] = G[NCOL] * S
G.insert(0, "lumi_fb", L); G.to_csv(f"{HERE}/S1_N_grid_139fb.csv", index=False)

def reach(g, col, thr):                                                      # F6_04_summary.py, unchanged
    best = (np.nan, np.nan)
    for lam, x in g.groupby("lambda_keV"):
        x = x.sort_values("mass_gev"); ok = (x[f"status_{'with_f' if 'with_f' in col else 'without_f'}"] == "bound") | ((x.status_with_f == "computed") & (x.k > 0))
        m, v = x.mass_gev.values, np.where(ok, x[col].values, np.nan)
        for i in range(len(m) - 1):
            a, b = v[i], v[i + 1]
            if np.isfinite(a) and np.isfinite(b) and a >= thr > b:
                mm = m[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (m[i + 1] - m[i])
                if not np.isfinite(best[0]) or mm > best[0]: best = (mm, lam)
    return best
R0 = pd.read_csv(f"{REP}/fig6/F6_reach.csv")
rows = []
for ch in ("colored", "EW"):
    for sct in ("Z1160", "Z0"):
        g = G[(G.channel == ch) & (G.sct == sct)]
        for thr, nm in ((3, "exclusion"), (5, "discovery")):
            c, lo, hi = (reach(g, f"N_with_f{s}", thr) for s in ("", "_lo", "_hi"))
            r300 = R0[(R0.channel == ch) & (R0.sct == sct) & (R0.variant == "charge factor included") & (R0.contour == nm)].iloc[0]
            low_edge = g[g.mass_gev == g.mass_gev.min()]
            rows.append(dict(channel=ch, sct=sct, contour=nm, lumi_fb=L, m_max_GeV=round(c[0]) if np.isfinite(c[0]) else np.nan, at_lambda_keV=c[1],
                             m_max_lo=round(lo[0]) if np.isfinite(lo[0]) else np.nan, m_max_hi=round(hi[0]) if np.isfinite(hi[0]) else np.nan,
                             m_max_300fb=r300.m_max_GeV, N_max_at_lowest_mass=round(float(low_edge.N_with_f.max()), 1)))
R = pd.DataFrame(rows); R.to_csv(f"{HERE}/S1_reach_139fb.csv", index=False)

ul = 1 - 0.05 ** (1 / 9139); sg = 211.2 * 0.01                              # fb after MET > 200 GeV, x 1% conversion
# no pile-up (stage 1): conversion only, tables/conversion_ref34_per_event.csv, geometry B, the same material model as the report's background
# (Z1160: B_Z1160_nomat = P9 LITERAL, the hard part of the report's conv1160; Z0: B_Z0_ref34 = P17, the hard part of the report's conv0);
# mu = 50 (the reproduction report) for reference
REF = pd.read_csv(f"{REP}/tables/conversion_ref34_per_event.csv"); TRUE = lambda s: s.astype(str) == "True"
def k_conv(cfg):
    x = REF[REF.config == cfg]; assert len(x) == 9139; return int((TRUE(x.plane) & TRUE(x.mult) & TRUE(x.final)).sum())
B = pd.DataFrame([dict(pileup="none", sct="Z1160", source="B_Z1160_nomat", pass_=k_conv("B_Z1160_nomat")), dict(pileup="none", sct="Z0", source="B_Z0_ref34", pass_=k_conv("B_Z0_ref34")),
                  dict(pileup="mu 50", sct="Z1160", source="P10_chunks_LITERAL", pass_=0), dict(pileup="mu 50", sct="Z0", source="P10_chunks_B_Z0_REF34", pass_=146)]).rename(columns={"pass_": "pass"})
B["sample"] = 9139; B["N_bkg"] = L * sg * B["pass"] / 9139; B["N_bkg_UL95"] = np.where(B["pass"] == 0, L * sg * ul, np.nan)
def cls_sup(b):                                                              # 95% CLs signal needed, median expectation n_obs = round(b)
    from scipy import optimize
    n = int(round(b)); return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-3, 200)
B["s95_CLs_nobs_eq_b"] = [cls_sup(u if p == 0 else b) for p, b, u in zip(B["pass"], B.N_bkg, B.N_bkg_UL95)]
B.to_csv(f"{HERE}/S1_background_139fb.csv", index=False)
pd.set_option("display.width", 200); print(R.to_string(index=False)); print(); print(B.round(3).to_string(index=False))

# ---- figure: N = 3 / 5 contours at 139 fb^-1 (300 fb^-1 for reference), both channels, both SCT settings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]; INK, MUTED = "#0b0b0b", "#898781"
LAMS = sorted(G.lambda_keV.unique())
def Z(g, col):
    ms = sorted(g.mass_gev.unique()); z = np.full((len(ms), len(LAMS)), np.nan)
    for i, m in enumerate(ms):
        for j, lam in enumerate(LAMS):
            r = g[(g.mass_gev == m) & np.isclose(g.lambda_keV, lam)].iloc[0]
            if r.status_with_f == "bound" or (r.status_with_f == "computed" and r.k > 0): z[i, j] = np.log10(r[col])
    return ms, z
fig, axs = plt.subplots(2, 2, figsize=(12, 9.5))
for i, ch in enumerate(("colored", "EW")):
    for j, sct in enumerate(("Z1160", "Z0")):
        ax = axs[i, j]; g = G[(G.channel == ch) & (G.sct == sct)]; ms, z = Z(g, "N_with_f"); y = np.log10(np.array(LAMS) * 1e3)
        f = RegularGridInterpolator((ms, y), z, bounds_error=False, fill_value=np.nan)
        mm, yy = np.meshgrid(np.linspace(ms[0], ms[-1], 400), np.linspace(y[0], y[-1], 400), indexing="ij"); zz = f(np.c_[mm.ravel(), yy.ravel()]).reshape(mm.shape)
        for lev, ls in ((3, "--"), (5, "-")):
            ax.contour(mm, yy, zz, levels=[np.log10(lev)], colors=[SERIES[0]], linestyles=[ls], linewidths=2.2)
            ax.contour(mm, yy, zz + np.log10(1 / S), levels=[np.log10(lev)], colors=[MUTED], linestyles=[ls], linewidths=1.0)
        for r in g.itertuples():
            yv = np.log10(r.lambda_keV * 1e3)
            if r.status_with_f == "computed": ax.plot(r.mass_gev, yv, "o" if r.k > 0 else "x", ms=2.5 if r.k > 0 else 4, color=INK if r.k > 0 else MUTED)
            else: ax.plot(r.mass_gev, yv, "o", ms=2.5, color=MUTED, mfc="none")
        q = R[(R.channel == ch) & (R.sct == sct)].set_index("contour")
        ax.text(0.97, 0.97, f"max reach, 139 fb⁻¹ (±1σ):\n exclusion {q.loc['exclusion','m_max_GeV']:.0f} ({q.loc['exclusion','m_max_lo']:.0f}–{q.loc['exclusion','m_max_hi']:.0f}) GeV\n"
                f" discovery {q.loc['discovery','m_max_GeV']:.0f} ({q.loc['discovery','m_max_lo']:.0f}–{q.loc['discovery','m_max_hi']:.0f}) GeV\n"
                f"300 fb⁻¹: {q.loc['exclusion','m_max_300fb']:.0f} / {q.loc['discovery','m_max_300fb']:.0f} GeV",
                transform=ax.transAxes, ha="right", va="top", fontsize=8, bbox=dict(boxstyle="round", fc="white", ec=SERIES[0]))
        ax.set_yticks(np.log10([100, 300, 1000, 3000, 10000, 25000])); ax.set_yticklabels(["100", "300", "1k", "3k", "10k", "25k"])
        ax.set_xlabel("m$_Q$ (GeV)"); ax.set_ylabel("Λ (eV)")
        ax.set_title(f"{'colored (3,1)$_{2/3}$' if ch == 'colored' else 'EW (1,1)$_1$'}, SCT σ$_z$ = {'1.16 mm (Knapen)' if sct == 'Z1160' else '0'}", fontsize=10, loc="left")
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], color=SERIES[0], ls="--", lw=2.2, label="139 fb⁻¹: 3 events (exclusion)"), Line2D([], [], color=SERIES[0], ls="-", lw=2.2, label="139 fb⁻¹: 5 events (discovery)"),
                    Line2D([], [], color=MUTED, ls="--", lw=1, label="300 fb⁻¹: 3 events"), Line2D([], [], color=MUTED, ls="-", lw=1, label="300 fb⁻¹: 5 events"),
                    Line2D([], [], marker="x", ls="", color=MUTED, label="0 events passed"), Line2D([], [], marker="o", ls="", color=MUTED, mfc="none", label="not propagated (N_max < 3)")],
           loc="lower center", ncol=3, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.04))
fig.suptitle("Stage 1: 13 TeV, 139 fb⁻¹, Knapen geometry, no pile-up, coplanarity selection; zero background assumed (N = 3 / 5)", fontsize=11)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{HERE}/S1_fig_reach_139fb.png", dpi=160, bbox_inches="tight"); fig.savefig(f"{HERE}/S1_fig_reach_139fb.pdf", bbox_inches="tight")
print("figure written")
