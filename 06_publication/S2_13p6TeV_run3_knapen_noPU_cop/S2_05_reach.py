#!/usr/bin/env python3
"""Stage 2, step 5: expected signal events N(m_Q, Lambda) at 13.6 TeV and the 3-event (exclusion) / 5-event (discovery) reach, Knapen geometry, no pile-up.
Same definitions as the reproduction (PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts/F6_03_contours.py, grid part, copied without change of method):
N = L sigma eps_trig [f_ch] k / n; colored: n = triggered events with both quirk-hadrons charged, f_ch included; EW: n = triggered events;
Wilson 68% band on k/n; k = 0: 95% upper limit 1 - 0.05^(1/n). Reach: F6_04_summary.py algorithm (as S1_reach_139fb.py).
Luminosity: 300 fb^-1 (main), 332 fb^-1 (ATLAS-like recorded), 355 fb^-1 (CMS-like delivered); N is linear in L. Reference: the 13 TeV grid at 300 fb^-1.
Zero background (no pile-up: stage 1 gives < 0.1 background events for both SCT settings).
Output: S2_N_grid_300fb.csv, S2_reach.csv, S2_fig_reach.png/.pdf."""
import os, json, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03"
LUMI = 300.0; LUMIS = (300.0, 332.0, 355.0)
LAMS = (0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25)
C = pd.read_csv(f"{HERE}/inputs/counts.csv"); TR = lambda s: s.astype(str) == "True"
def load(tag):
    rows, nev = [], {}
    for band in ("low", "mid", "high_a"):
        f = f"{HERE}/logs/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl"
        if os.path.exists(f):
            new = [r for l in open(f) if l.strip() for r in json.loads(l)]; nev[band] = len({r["event"] for r in new}); rows += new
    return pd.DataFrame(rows), nev
recs = []
for r in C.itertuples():
    tag = f"{r.channel}_{r.mass_gev}gev"; ev = pd.read_csv(f"{HERE}/inputs/{tag}_events.csv"); tr = TR(ev.trigger_proxy_pass)
    if r.channel == "colored":
        nch = int((tr & (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)).sum()); et = tr.sum() / len(ev); fch = nch / tr.sum(); n_prop = nch
    else:
        et = tr.sum() / len(ev); fch = 1.0; n_prop = int(tr.sum())
    D, nev = load(tag); pre = LUMI * r.sigma_matched_fb * et
    assert all(v == n_prop for v in nev.values()), f"{tag}: incomplete band(s) {nev}, expected {n_prop}"
    for lam in LAMS:
        x = D[np.isclose(D.lambda_keV.astype(float), lam)] if len(D) else D; done = len(x) == n_prop and len(x) > 0
        for sct in ("Z0", "Z1160"):
            base = dict(sqrt_s_TeV=13.6, lumi_fb=LUMI, channel=r.channel, mass_gev=r.mass_gev, lambda_keV=lam, sct=sct, sigma_fb=r.sigma_matched_fb, eps_trig=et, f_ch=fch,
                        n_prop=n_prop, L_sigma_eps_trig=pre)
            if done:
                n_fid = int(TR(x.fid).sum()); k = int(TR(x[f"{sct}_final"]).sum()); lo, hi = stats.binomtest(k, n_prop).proportion_ci(0.6827, "wilson"); ul = 1 - 0.05 ** (1 / n_prop)
                base.update(status="computed", status_with_f="computed", status_without_f="computed", n_fid=n_fid, k=k, n_integration_fail=int((x.error.astype(str) != "").sum()),
                            eps_fid=n_fid / n_prop, eps_reco=k / n_fid if n_fid else np.nan, N_with_f=pre * fch * k / n_prop, N_with_f_lo=pre * fch * lo, N_with_f_hi=pre * fch * hi,
                            N_with_f_UL95_if_k0=pre * fch * ul if k == 0 else np.nan)
            else:
                base.update(status="not run", status_with_f="bound" if pre * fch < 3 else "missing", status_without_f="bound" if pre < 3 else "missing", N_with_f=pre * fch)
            recs.append(base)
G = pd.DataFrame(recs); G.to_csv(f"{HERE}/S2_N_grid_300fb.csv", index=False)
G13 = pd.read_csv(f"{REP}/fig6/F6_N_grid.csv")

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
R0 = pd.read_csv(f"{REP}/fig6/F6_reach.csv"); rows = []
for ch in ("colored", "EW"):
    for sct in ("Z1160", "Z0"):
        g0 = G[(G.channel == ch) & (G.sct == sct)]
        for L in LUMIS:
            g = g0.copy(); g[["N_with_f", "N_with_f_lo", "N_with_f_hi"]] *= L / LUMI
            for thr, nm in ((3, "exclusion"), (5, "discovery")):
                c, lo, hi = (reach(g, f"N_with_f{s}", thr) for s in ("", "_lo", "_hi"))
                r13 = R0[(R0.channel == ch) & (R0.sct == sct) & (R0.variant == "charge factor included") & (R0.contour == nm)].iloc[0]
                top = g[g.mass_gev == g.mass_gev.max()]
                rows.append(dict(channel=ch, sct=sct, contour=nm, sqrt_s_TeV=13.6, lumi_fb=L, m_max_GeV=round(c[0]) if np.isfinite(c[0]) else np.nan, at_lambda_keV=c[1],
                                 m_max_lo=round(lo[0]) if np.isfinite(lo[0]) else np.nan, m_max_hi=round(hi[0]) if np.isfinite(hi[0]) else np.nan,
                                 m_max_13TeV_300fb=r13.m_max_GeV, N_max_at_highest_mass=round(float(top.N_with_f.max()), 2)))
R = pd.DataFrame(rows); R.to_csv(f"{HERE}/S2_reach.csv", index=False)
pd.set_option("display.width", 220); print(R.to_string(index=False))

# ---- figure: N = 3 / 5 contours at 13.6 TeV, 300 fb^-1, with the 13 TeV 300 fb^-1 contours for reference
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from matplotlib.lines import Line2D
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]; INK, MUTED = "#0b0b0b", "#898781"
def Z(g, lams):
    ms = sorted(g.mass_gev.unique()); z = np.full((len(ms), len(lams)), np.nan)
    for i, m in enumerate(ms):
        for j, lam in enumerate(lams):
            r = g[(g.mass_gev == m) & np.isclose(g.lambda_keV, lam)]
            if len(r) and (r.iloc[0].status_with_f == "bound" or (r.iloc[0].status_with_f == "computed" and r.iloc[0].k > 0)): z[i, j] = np.log10(r.iloc[0].N_with_f)
    return ms, z
def contours(ax, g, color, lw):
    lams = sorted(g.lambda_keV.unique()); ms, z = Z(g, lams); y = np.log10(np.array(lams) * 1e3)
    f = RegularGridInterpolator((ms, y), z, bounds_error=False, fill_value=np.nan)
    mm, yy = np.meshgrid(np.linspace(ms[0], ms[-1], 400), np.linspace(y[0], y[-1], 400), indexing="ij"); zz = f(np.c_[mm.ravel(), yy.ravel()]).reshape(mm.shape)
    for lev, ls in ((3, "--"), (5, "-")): ax.contour(mm, yy, zz, levels=[np.log10(lev)], colors=[color], linestyles=[ls], linewidths=lw)
fig, axs = plt.subplots(2, 2, figsize=(12, 9.5))
for i, ch in enumerate(("colored", "EW")):
    for j, sct in enumerate(("Z1160", "Z0")):
        ax = axs[i, j]; g = G[(G.channel == ch) & (G.sct == sct)]
        contours(ax, G13[(G13.channel == ch) & (G13.sct == sct)], MUTED, 1.0); contours(ax, g, SERIES[0], 2.2)
        for r in g.itertuples():
            yv = np.log10(r.lambda_keV * 1e3)
            if r.status_with_f == "computed": ax.plot(r.mass_gev, yv, "o" if r.k > 0 else "x", ms=2.5 if r.k > 0 else 4, color=INK if r.k > 0 else MUTED)
        q = R[(R.channel == ch) & (R.sct == sct)].set_index(["lumi_fb", "contour"]); t = lambda L, c: f"{q.loc[(L, c), 'm_max_GeV']:.0f}"
        ax.text(0.97, 0.97, f"max reach, 13.6 TeV (±1σ at 300 fb⁻¹):\n 300 fb⁻¹: excl. {t(300.0,'exclusion')} ({q.loc[(300.0,'exclusion'),'m_max_lo']:.0f}–{q.loc[(300.0,'exclusion'),'m_max_hi']:.0f}),"
                f" disc. {t(300.0,'discovery')} GeV\n 332 / 355 fb⁻¹: excl. {t(332.0,'exclusion')} / {t(355.0,'exclusion')} GeV\n"
                f"13 TeV, 300 fb⁻¹: {q.loc[(300.0,'exclusion'),'m_max_13TeV_300fb']:.0f} / {q.loc[(300.0,'discovery'),'m_max_13TeV_300fb']:.0f} GeV",
                transform=ax.transAxes, ha="right", va="top", fontsize=8, bbox=dict(boxstyle="round", fc="white", ec=SERIES[0]))
        ax.set_yticks(np.log10([100, 300, 1000, 3000, 10000, 25000])); ax.set_yticklabels(["100", "300", "1k", "3k", "10k", "25k"])
        ax.set_xlabel("m$_Q$ (GeV)"); ax.set_ylabel("Λ (eV)")
        ax.set_title(f"{'colored (3,1)$_{2/3}$' if ch == 'colored' else 'EW (1,1)$_1$'}, SCT σ$_z$ = {'1.16 mm (Knapen)' if sct == 'Z1160' else '0'}", fontsize=10, loc="left")
fig.legend(handles=[Line2D([], [], color=SERIES[0], ls="--", lw=2.2, label="13.6 TeV, 300 fb⁻¹: 3 events (exclusion)"), Line2D([], [], color=SERIES[0], ls="-", lw=2.2, label="13.6 TeV, 300 fb⁻¹: 5 events (discovery)"),
                    Line2D([], [], color=MUTED, ls="--", lw=1, label="13 TeV, 300 fb⁻¹: 3 events"), Line2D([], [], color=MUTED, ls="-", lw=1, label="13 TeV, 300 fb⁻¹: 5 events"),
                    Line2D([], [], marker="x", ls="", color=MUTED, label="0 events passed")], loc="lower center", ncol=3, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.04))
fig.suptitle("Stage 2: 13.6 TeV (Run 3), Knapen geometry, no pile-up, coplanarity selection; zero background (N = 3 / 5)", fontsize=11)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{HERE}/S2_fig_reach.png", dpi=160, bbox_inches="tight"); fig.savefig(f"{HERE}/S2_fig_reach.pdf", bbox_inches="tight")
print("figure written")
