#!/usr/bin/env python3
"""Figure 6, step 3 (2026-10-17): expected signal events N(m_Q, Lambda) at 300 fb-1 and the 3-event (exclusion) / 5-event (discovery) contours.
Paper (Sec. IV, Fig. 6 caption): N = L sigma eps_trig eps_fid eps_reco, no background; 3 events = exclusion, 5 = discovery.
  colored: sigma = MLM-matched cross section of the point (MG5 3.7.3 + Pythia8, figure6_full_v1 generation); eps_trig = N(pT(QQ) > 200) / N(matched);
           f_ch = N(trigger, both quirk-hadrons charged |q| > 0.5) / N(trigger) (paper Sec. II: ~30%; included in the main line, also shown without);
  EW:      eps_trig = sigma_B / sigma_A (LO, MG5 3.7.3: A = pp -> QQ, B = pp -> QQ + j with pT(j) > 200 GeV, ickkw 0; hep_tools/F6_EW_LO_ratio), as Table I;
  eps_fid * eps_reco = k / n with n = propagated events (trigger [colored: and both charged]), k = events in the signal region (scripts/F6_02_grid.py).
  So N = L sigma eps_trig [f_ch] k / n. Uncertainty: binomial on k/n (Wilson 68% for the band); k = 0: 95% upper limit 1 - 0.05^(1/n).
Points not propagated: N_max = L sigma eps_trig [f_ch] (eps_fid = eps_reco = 1) < 3 -> used as an upper bound (EW 1000; colored 2400; colored 2100 with f_ch).
Contours: log10 N interpolated linearly in m_Q and in the paper's display coordinate of Lambda (log10 below 1 keV, linear above), on the computed grid only
(0.1-10 keV; colored 600-2400 GeV, EW 100-1000 GeV). Grid points with k = 0 have no measured N: no contour is drawn through them; they are marked
(grey x: 95% upper limit on N < 3; red x: upper limit >= 3, not resolved).
Outputs: fig6/F6_N_grid.csv, fig6/F6_ew_lo_ratio.csv, FINAL_FIGURES/F6_fig6/ (png/pdf + source csv)."""
import os, sys, re, json, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; LOG = f"{ROOT}/logs"; OUT = f"{ROOT}/fig6"
LUMI = 300.0
LAMS = (0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 4, 5, 7, 10)
C = pd.read_csv(f"{OUT}/inputs/counts.csv")
# ---- EW LO ratio from the MG5 log (order: for each mass, A then B)
xs = [float(v) for v in re.findall(r"Cross-section :\s+([0-9.eE+-]+) \+-", open("/home/rafia/hep_tools/F6_EW_LO_ratio/mg5_run.log").read())]
dxs = [float(v) for v in re.findall(r"Cross-section :\s+[0-9.eE+-]+ \+- ([0-9.eE+-]+) pb", open("/home/rafia/hep_tools/F6_EW_LO_ratio/mg5_run.log").read())]
assert len(xs) == 12, len(xs)
LO = pd.DataFrame([dict(mass_gev=m, sigma_A_fb=xs[2 * i] * 1e3, sigma_A_err_fb=dxs[2 * i] * 1e3, sigma_B_fb=xs[2 * i + 1] * 1e3, sigma_B_err_fb=dxs[2 * i + 1] * 1e3)
                   for i, m in enumerate((100, 200, 400, 600, 800, 1000))])
LO["ratio"] = LO.sigma_B_fb / LO.sigma_A_fb; LO["ratio_err"] = LO.ratio * np.hypot(LO.sigma_A_err_fb / LO.sigma_A_fb, LO.sigma_B_err_fb / LO.sigma_B_fb)
assert abs(LO.set_index("mass_gev").ratio[800] - 0.0960) < 0.002, "EW 800 LO ratio must reproduce Table I (0.096)"
LO.to_csv(f"{OUT}/F6_ew_lo_ratio.csv", index=False)

def load(tag):
    rows = []
    for band in ("low", "mid"):
        f = f"{LOG}/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl"
        if os.path.exists(f): rows += [r for l in open(f) if l.strip() for r in json.loads(l)]
    return pd.DataFrame(rows)
TR = lambda s: s.astype(str) == "True"
recs = []
for r in C.itertuples():
    tag = f"{r.channel}_{r.mass_gev}gev"; ev = pd.read_csv(f"{OUT}/inputs/{tag}_events.csv"); tr = TR(ev.trigger_proxy_pass)
    if r.channel == "colored":
        nch = int((tr & (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)).sum()); et = tr.sum() / len(ev); fch = nch / tr.sum(); n_prop = nch
    else:
        et = float(LO.set_index("mass_gev").ratio[r.mass_gev]); fch = 1.0; n_prop = int(tr.sum())
    D = load(tag); pre = LUMI * r.sigma_matched_fb * et
    for lam in LAMS:
        x = D[np.isclose(D.lambda_keV.astype(float), lam)] if len(D) else D
        done = len(x) == n_prop and len(x) > 0
        for sct in ("Z0", "Z1160"):
            base = dict(channel=r.channel, mass_gev=r.mass_gev, lambda_keV=lam, sct=sct, sigma_fb=r.sigma_matched_fb, eps_trig=et, f_ch=fch, n_prop=n_prop,
                        L_sigma_eps_trig=pre)
            if done:
                n_fid = int(TR(x.fid).sum()); k = int(TR(x[f"{sct}_final"]).sum()) if f"{sct}_final" in x else 0
                n_err = int((x.error.astype(str) != "").sum())
                lo, hi = stats.binomtest(k, n_prop).proportion_ci(0.6827, "wilson")
                ul = 1 - 0.05 ** (1 / n_prop)
                base.update(status="computed", status_with_f="computed", status_without_f="computed", n_fid=n_fid, k=k, n_integration_fail=n_err, eps_fid=n_fid / n_prop, eps_reco=k / n_fid if n_fid else np.nan,
                            N_with_f=pre * fch * k / n_prop, N_without_f=pre * k / n_prop, N_with_f_lo=pre * fch * lo, N_with_f_hi=pre * fch * hi,
                            N_without_f_lo=pre * lo, N_without_f_hi=pre * hi, N_with_f_UL95_if_k0=pre * fch * ul if k == 0 else np.nan,
                            N_without_f_UL95_if_k0=pre * ul if k == 0 else np.nan)
            else:
                base.update(status="not run", status_with_f="bound" if pre * fch < 3 else "missing", status_without_f="bound" if pre < 3 else "missing",
                            N_with_f=pre * fch, N_without_f=pre)           # bound = maximum possible N (eps_fid = eps_reco = 1)
            recs.append(base)
G = pd.DataFrame(recs); G.to_csv(f"{OUT}/F6_N_grid.csv", index=False)
print(G.groupby(["channel", "mass_gev"]).status_with_f.agg(lambda s: dict(s.value_counts())).to_string())

# ---------------------------------------------------------------- figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
sys.path.insert(0, HERE); import fig_utils as fu
V = json.load(open(f"{ROOT}/tables/paper_fig6_vector.json"))
cal = V["colored"]["calibration"]                                            # both panels share the y calibration (checked equal in S4)
assert cal == {**cal, "y_log_ticks": V["EW"]["calibration"]["y_log_ticks"], "y_lin_ticks": V["EW"]["calibration"]["y_lin_ticks"]}
_al = np.polyfit([np.log10(v) for v, _ in cal["y_log_ticks"]], [p for _, p in cal["y_log_ticks"]], 1)
_bl = np.polyfit([v for v, _ in cal["y_lin_ticks"]], [p for _, p in cal["y_lin_ticks"]], 1)
def Yd(lam_eV):                                                              # paper's display coordinate (minus page y): log below 1 keV, linear above
    l = np.asarray(lam_eV, float); return -np.where(l <= 1000, np.polyval(_al, np.log10(np.clip(l, 1e-6, None))), np.polyval(_bl, l))
XR = {"colored": (500, 2500), "EW": (0, 1200)}; SCT = {"Z1160": "SCT z 1.16 mm (signal and background)", "Z0": "no SCT z smearing (signal only)"}
def contours(ax, g, col, ls_ex, ls_di, lw, label):
    ms = sorted(g.mass_gev.unique()); ys = Yd(np.array(LAMS) * 1e3)
    Z = np.full((len(ms), len(LAMS)), np.nan)
    for i, m in enumerate(ms):
        for j, lam in enumerate(LAMS):
            r = g[(g.mass_gev == m) & np.isclose(g.lambda_keV, lam)]
            if not len(r): continue
            st = r[f"status_{col[2:]}"].iloc[0]; r = r.iloc[0]
            if st == "bound": Z[i, j] = np.log10(r[col])                 # maximum possible N (< 3)
            elif st == "computed":
                Z[i, j] = np.log10(r[col]) if r.k > 0 else np.nan               # k = 0: no measured N -> no contour through this point (marked separately)
    if np.isnan(Z).all(): return
    f = RegularGridInterpolator((ms, ys), Z, bounds_error=False, fill_value=np.nan)
    mm, yy = np.meshgrid(np.linspace(ms[0], ms[-1], 400), np.linspace(ys[0], ys[-1], 400), indexing="ij")
    zz = f(np.column_stack([mm.ravel(), yy.ravel()])).reshape(mm.shape)
    ax.contour(mm, yy, zz, levels=[np.log10(3)], colors=[fu.SERIES[0] if "without" not in label else fu.SERIES[1]], linestyles=[ls_ex], linewidths=lw)
    ax.contour(mm, yy, zz, levels=[np.log10(5)], colors=[fu.SERIES[0] if "without" not in label else fu.SERIES[1]], linestyles=[ls_di], linewidths=lw)
def panel(ax, ch, sct):
    P = V[ch]["curves"]; x0, x1 = XR[ch]
    for k, lab, c, ls in (("hscp_12.9_boundary", "HSCP 12.9 fb⁻¹", "#7fbf7f", "-"), ("hscp_300", "HSCP 300 fb⁻¹", "#7fbf7f", "--"),
                          ("monojet_12.9_boundary", "monojet 12.9 fb⁻¹", "#b5b5b5", "-"), ("monojet_300", "monojet 300 fb⁻¹", "#b5b5b5", "--")):
        ax.plot(P[k]["m_GeV"], Yd(P[k]["lambda_eV"]), color=c, ls=ls, lw=1.2, zorder=1)
    for k in ("dcm_100um", "dcm_1mm", "dcm_1cm", "dcm_1m", "dcm_100m"):
        ax.plot(P[k]["m_GeV"], Yd(P[k]["lambda_eV"]), color="#9cb9d1", ls=":", lw=1.0, zorder=1)
        ax.text(x1 - 0.02 * (x1 - x0), Yd(P[k]["lambda_eV"][-1]) + 3, "d$_{cm}$ = " + {"100um": "100 µm", "1mm": "1 mm", "1cm": "1 cm", "1m": "1 m", "100m": "100 m"}[k[4:]],
                ha="right", fontsize=6.5, color="#5f87a8")
    ax.plot(P["exclusion"]["m_GeV"], Yd(P["exclusion"]["lambda_eV"]), color=fu.INK, ls="--", lw=1.6, zorder=3)
    ax.plot(P["discovery"]["m_GeV"], Yd(P["discovery"]["lambda_eV"]), color=fu.INK, ls="-", lw=1.6, zorder=3)
    g = G[(G.channel == ch) & (G.sct == sct)]
    contours(ax, g, "N_with_f", "--", "-", 2.4, "this work")
    if ch == "colored": contours(ax, g, "N_without_f", "--", "-", 1.3, "without charge factor")
    # grid points: computed (dot), not resolved (x), bound (small grey dot); not computed regions hatched
    for r in g.itertuples():
        y = Yd(r.lambda_keV * 1e3)
        if r.status == "computed":
            if r.k == 0: ax.plot(r.mass_gev, y, "x", ms=4.5, color=fu.SERIES[7] if r.N_with_f_UL95_if_k0 >= 3 else fu.MUTED, zorder=4)
            else: ax.plot(r.mass_gev, y, "o", ms=2.2, color=fu.INK2, zorder=4)
        elif r.status_with_f == "bound": ax.plot(r.mass_gev, y, "o", ms=2.2, color=fu.MUTED, mfc="none", zorder=4)
    mmin, mmax = g.mass_gev.min(), g.mass_gev.max()
    ax.fill_between([x0, x1], Yd(10e3), Yd(35e3), color="#e9e9e9", hatch="//", edgecolor="#c9c9c9", lw=0, zorder=0)
    ax.text((x0 + x1) / 2, Yd(22e3), "Λ > 10 keV: not computed", ha="center", fontsize=8.5, color=fu.INK2, zorder=5)
    if mmin > x0: ax.fill_betweenx([Yd(3), Yd(10e3)], x0, mmin, color="#e9e9e9", hatch="//", edgecolor="#c9c9c9", lw=0, zorder=0)
    ax.fill_between([x0, x1], Yd(3), Yd(100), color="#e9e9e9", hatch="//", edgecolor="#c9c9c9", lw=0, zorder=0)
    ax.text(x1 - 0.02 * (x1 - x0), Yd(5), "Λ < 100 eV: not computed", ha="right", fontsize=8, color=fu.INK2, zorder=5)
    ax.set_xlim(x0, x1); ax.set_ylim(Yd(3), Yd(35000))
    tv = [10, 100, 1000, 10000, 20000, 30000]; ax.set_yticks(Yd(tv)); ax.set_yticklabels(["10", "10²", "10³", "10000", "20000", "30000"])
    ax.axhline(Yd(1000), color=fu.MUTED, lw=0.6, ls="-"); ax.set_xlabel("m$_Q$ (GeV)"); ax.set_ylabel("Λ (eV)")
    ax.set_title(f"{'colored (3,1)$_{2/3}$' if ch == 'colored' else 'EW (1,1)$_1$'}: {SCT[sct]}", fontsize=9.5, loc="left")
def plot(_):
    fig, axs = plt.subplots(2, 2, figsize=(13, 11))
    for i, ch in enumerate(("colored", "EW")):
        for j, sct in enumerate(("Z1160", "Z0")): panel(axs[i, j], ch, sct)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=fu.INK, ls="--", lw=1.6, label="paper: exclusion (3 events)"), Line2D([], [], color=fu.INK, ls="-", lw=1.6, label="paper: discovery (5 events)"),
         Line2D([], [], color=fu.SERIES[0], ls="--", lw=2.4, label="this work: exclusion (3 events)"), Line2D([], [], color=fu.SERIES[0], ls="-", lw=2.4, label="this work: discovery (5 events)"),
         Line2D([], [], color=fu.SERIES[1], ls="--", lw=1.3, label="this work, colored, without the charged-hadron factor"),
         Line2D([], [], color="#7fbf7f", lw=1.2, label="HSCP 12.9 / 300 fb⁻¹ (from the paper)"), Line2D([], [], color="#b5b5b5", lw=1.2, label="monojet 12.9 / 300 fb⁻¹ (from the paper)"),
         Line2D([], [], color="#9cb9d1", ls=":", lw=1.2, label="d$_{cm}$ (from the paper)"),
         Line2D([], [], marker="o", ls="", color=fu.INK2, ms=4, label="grid point with ≥ 1 event in the signal region"),
         Line2D([], [], marker="x", ls="", color=fu.MUTED, ms=6, label="0 events passed: N < 3 at 95% CL"), Line2D([], [], marker="x", ls="", color=fu.SERIES[7], ms=6, label="0 events passed: not resolved (95% UL on N ≥ 3)"),
         Line2D([], [], marker="o", ls="", color=fu.MUTED, mfc="none", ms=4, label="not propagated: N < 3 even with ε$_{fid}$ = ε$_{reco}$ = 1")]
    fig.legend(handles=h, loc="lower center", ncol=3, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Figure 6 of arXiv:1708.02243: 300 fb⁻¹, no background (left: same SCT z smearing for signal and background; right: signal without SCT z smearing)", fontsize=10.5)
    fig.tight_layout(); return fig
SRC = G.copy()
fu.figure("F6_fig6", SRC, plot,
          "Figure 6: contours of 3 (exclusion) and 5 (discovery) expected signal events at 300 fb⁻¹, no background, as in the paper. N = L σ ε_trig [f_ch] ε_fid ε_reco; colored: "
          "matched σ, ε_trig by event count, f_ch = fraction with both quirk-hadrons charged (main line; thin orange: without it); EW: ε_trig = σ(QQ̄+j, pT > 200)/σ(QQ̄) at LO. "
          "ε_fid ε_reco from the Table I pipeline on the 2000-event samples of each mass (first crossing). Left: SCT z 1.16 mm for signal (and background, which is then 0/9139); right: "
          "signal without SCT z smearing (background with the same setting is not negligible). Contours interpolated in log N on the computed grid (Λ = 0.1–10 keV); not computed above "
          "10 keV and outside the mass range of the samples (hatched). Paper curves, HSCP/monojet limits and d_cm lines extracted from the paper's vector figures.",
          [f"{OUT}/F6_N_grid.csv", f"{ROOT}/tables/paper_fig6_vector.json"], "all computed grid points", os.path.abspath(__file__))
print("figure written")
