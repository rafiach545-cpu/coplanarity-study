#!/usr/bin/env python3
"""Figure 7 of arXiv:1708.02243 (Appendix A, 2026-10-18): distributions of beta*gamma and dE/dx for the hits in the ATLAS pixel detector, for the two
benchmark masses at Lambda = 2 keV (paper caption: "two signal benchmark points with Lambda = 2 keV": m_Q = 800 GeV EW and 1800 GeV colored).
Paper text: dE/dx = "most probable value as a function of beta*gamma [PDG]"; hits with beta*gamma < 0.1 omitted in the dE/dx panel.
Paper does not state: the silicon thickness (we use ATLAS: IBL 200 um, other pixel layers 250 um), the event set and which hits (we use: the trigger-
passing [colored: both charged] events of the Figure 6 samples at these masses, fiducial at 2 keV, first crossing of each pixel layer by each quirk, as in
the reconstruction). Variant also written: all triggered events, every pixel-layer crossing within 25 ns and inside the barrel.
Trajectory: production integrator (numba copy, bitwise identical), same z0 draws as F6_02_grid.py. beta*gamma = |p|/m at the crossing (p interpolated
linearly between the two integration steps, like the position). dE/dx: PDG Eq. 34.12 (Landau-Vavilov-Bichsel most probable value),
Delta_p/x = (xi/x) [ln(2 m c^2 bg^2 / I) + ln(xi / I) + j - beta^2 - delta(bg)], xi = (K/2)(Z/A) z^2 x / beta^2, j = 0.200, silicon: Z/A = 0.49848,
I = 173 eV, rho = 2.329 g/cm^3, Sternheimer density-effect parameters (PDG table): x0 = 0.2015, x1 = 2.8716, a = 0.14921, k = 3.2546, C = 4.4355, delta0 = 0.14.
|z| = 1 (EW unit charge; colored events with both quirk-hadrons charged have |q| = 1 here, checked).
Output: tables/F7_pixel_hits.csv (one row per hit), FINAL_FIGURES/F7_fig7/ (figure + source CSV with our and the paper's histograms)."""
import os, sys, json, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
p4._init(); sys.path.insert(0, f"{p4.BASE}/03_trajectory_sim")
from quirk_trajectory_numba import integrate_trajectory_numba
p4.tth.integrate_trajectory = integrate_trajectory_numba
import fig_utils as fu
NS, CM = p18.NS, p18.CM
K, ZA, ME, I, J, RHO = 0.307075, 0.49848, 0.51099895, 173e-6, 0.200, 2.329
X0, X1, A_, K_, C_, D0 = 0.2015, 2.8716, 0.14921, 3.2546, 4.4355, 0.14
THICK_CM = {1: 0.0200, 2: 0.0250, 3: 0.0250, 4: 0.0250}                      # IBL 200 um, B-layer / L1 / L2 250 um
def delta(bg):
    x = np.log10(bg)
    return np.where(x >= X1, 2 * np.log(10) * x - C_, np.where(x >= X0, 2 * np.log(10) * x - C_ + A_ * (X1 - x) ** K_, D0 * 10 ** (2 * (x - X0))))
def dedx_mpv(bg, t_cm):
    """most probable energy loss per unit mass thickness, MeV cm^2/g (PDG Eq. 34.12), unit charge"""
    bg = np.asarray(bg, float); b2 = bg ** 2 / (1 + bg ** 2); x = t_cm * RHO; xi = 0.5 * K * ZA * x / b2
    return xi / x * (np.log(2 * ME * bg ** 2 / I) + np.log(xi / I) + J - b2 - delta(bg))
def crossings_with_p(tr, mq):
    t = np.asarray(tr["t_gev_inv"]) * NS; out = []
    for qi, (x, p) in enumerate(((tr["x1"], tr["p1"]), (tr["x2"], tr["p2"])), 1):
        x = np.asarray(x) * CM; r = np.hypot(x[:, 0], x[:, 1])
        for L, lay in enumerate(p4.tth.LAYERS, 1):
            R = lay["r_cm"]; d = np.sign(r - R); idx = np.where(d[1:] != d[:-1])[0]
            for k, i in enumerate(idx):
                f = (R - r[i]) / (r[i + 1] - r[i]); pos = x[i] + f * (x[i + 1] - x[i]); tt = t[i] + f * (t[i + 1] - t[i]); pp = p[i] + f * (p[i + 1] - p[i])
                out.append(dict(quirk=qi, layer=L, order=k, x=pos[0], y=pos[1], z_lab=pos[2], t_ns=tt, r=R, bg=float(np.linalg.norm(pp) / mq)))
    return out
def fid_of(cr):
    f = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}
    return all((q, L) in f and abs(f[(q, L)]["z_lab"]) < p4.HALF[L] and f[(q, L)]["t_ns"] < p4.R["timing_ns"] for q in (1, 2) for L in range(1, 9))
if __name__ == "__main__":
    # sanity check of the dE/dx formula: minimum-ionising MPV in 250 um silicon (PDG Fig. 34.8: about 1.1-1.2 MeV cm^2/g for 160-320 um)
    print("MPV/x at bg = 3.5, 250 um:", round(float(dedx_mpv(3.5, 0.025)), 3), "MeV cm^2/g;  bg = 0.1:", round(float(dedx_mpv(0.1, 0.025)), 1))
    rows = []
    for tag, lab in (("EW_800gev", "EW_800GeV_2keV"), ("colored_1800gev", "colored_1800GeV_2keV")):
        ch, mq = tag.split("_")[0], float(tag.split("_")[1][:-3])
        ev0 = pd.read_csv(f"{HERE}/../fig6/inputs/{tag}_events.csv"); chg = (ev0.charge1.abs() > 0.5) & (ev0.charge2.abs() > 0.5)
        trig = ev0.trigger_proxy_pass.astype(str) == "True"
        sel = trig & chg if ch == "colored" else trig
        ev = ev0[sel].reset_index(drop=True); nq = {abs(c) for c in np.r_[ev.charge1.values, ev.charge2.values]}; print(tag, "events", len(ev), "|q| values", nq)
        notrig = ev0[(~trig) & chg].reset_index(drop=True)                 # variant: matched events failing the trigger (both charged), seeds offset by 100000
        for i, r in list(enumerate(ev.itertuples())) + [(100000 + j, rr) for j, rr in enumerate(notrig.itertuples())]:
            rng = np.random.default_rng(np.random.SeedSequence([6, int(mq), i])); z0 = rng.normal(0.0, p4.R["beamspot_cm"])
            try:
                _, tr = p4.tth.simulate_quirk_hits((r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), mass_gev=mq, Lambda_gev=2e-6, B_tesla=p4.R["B_tesla"],
                                                   charge1=float(r.charge1), charge2=float(r.charge2), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=p4.R["max_layer_r_cm"])
            except Exception as e:
                print("  event", i, "failed:", str(e)[:60]); continue
            cr = crossings_with_p(tr, mq); f = fid_of(cr); del tr
            for c in cr:
                if c["layer"] > 4 or abs(c["z_lab"]) >= p4.HALF[c["layer"]]: continue          # timing cut applied below (column in_25ns)
                rows.append(dict(sample=lab, event=i, triggered=i < 100000, fiducial_event=f, in_25ns=c["t_ns"] < p4.R["timing_ns"], quirk=c["quirk"], layer=c["layer"], order=c["order"], t_ns=c["t_ns"], betagamma=c["bg"],
                                 dEdx_MPV_MeVcm2g=float(dedx_mpv(c["bg"], THICK_CM[c["layer"]])) if c["bg"] >= 0.1 else np.nan))
    Hall = pd.DataFrame(rows); Hall.to_csv(f"{T}/F7_pixel_hits.csv", index=False)
    for s, x in Hall.groupby("sample"):
        print(f"{s}: fraction of hits with bg < 0.1 WITHOUT the 25 ns cut -- triggered: {np.mean(x[x.triggered].betagamma < 0.1):.3f}; all events: {np.mean(x.betagamma < 0.1):.3f}; "
              f"hits after 25 ns: {np.mean(~x.in_25ns):.3f}")
    H = Hall[Hall.in_25ns]
    H_trig = H[H.triggered]
    main = H_trig[(H_trig.fiducial_event) & (H_trig.order == 0)]
    for s, x in H.groupby("sample"):
        print(f"{s}: fraction of hits with bg < 0.1 -- triggered, all crossings: {np.mean(x[x.triggered].betagamma < 0.1):.3f}; "
              f"not triggered, all crossings: {np.mean(x[~x.triggered].betagamma < 0.1):.3f}; all events: {np.mean(x.betagamma < 0.1):.3f}")
    for s, x in main.groupby("sample"):
        print(f"{s}: main selection {len(x)} hits from {x.event.nunique()} events; bg median {x.betagamma.median():.3f}, fraction bg<0.1 {np.mean(x.betagamma < 0.1):.3f}; "
              f"dE/dx median {x.dEdx_MPV_MeVcm2g.median():.1f} MeV cm2/g")
    # ---- figure: our histograms (unit area) vs the paper's
    V = json.load(open(f"{T}/paper_fig7_vector.json"))
    EB = {"dEdx": np.linspace(0, 100, 51), "betagamma": np.logspace(-4, 1, 51)}
    src = []
    for sel_name, D in (("main: fiducial events, first crossing", main), ("all triggered events, all crossings", H_trig), ("all matched events (no trigger), all crossings", H)):
        for s, x in D.groupby("sample"):
            for var, col in (("dEdx", "dEdx_MPV_MeVcm2g"), ("betagamma", "betagamma")):
                v = x[col].dropna().values; h, e = np.histogram(np.clip(v, EB[var][0], EB[var][-1] * 0.9999), bins=EB[var])
                src += [dict(selection=sel_name, sample=s, var=var, lo=e[j], hi=e[j + 1], frac=h[j] / max(h.sum(), 1), n_hits=len(v)) for j in range(len(h))]
    for var in ("dEdx", "betagamma"):
        for s, c in V[var]["curves"].items(): src += [dict(selection="paper", sample=s, var=var, x=a, y=b) for a, b in zip(c["x"], c["y"])]
    SRC = pd.DataFrame(src)
    def plot(d):
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8)); col = {"EW_800GeV_2keV": fu.SERIES[1], "colored_1800GeV_2keV": fu.SERIES[6]}
        for ax, var in zip(axs, ("dEdx", "betagamma")):
            for s in ("EW_800GeV_2keV", "colored_1800GeV_2keV"):
                o = d[(d.selection.str.startswith("main")) & (d["sample"] == s) & (d["var"] == var)]
                ax.stairs(o.frac.values, np.r_[o.lo.values, o.hi.values[-1]], color=col[s], lw=2, label=f"this work, {s.replace('_', ' ')} (N = {int(o.n_hits.iloc[0])} hits)")
                p = d[(d.selection == "paper") & (d["sample"] == s) & (d["var"] == var)]
                ax.plot(p.x, p.y, color=col[s], lw=1.2, ls=":", label=f"paper, {s.replace('_', ' ')}")
                a = d[(d.selection.str.startswith("all matched")) & (d["sample"] == s) & (d["var"] == var)]
                ax.stairs(a.frac.values, np.r_[a.lo.values, a.hi.values[-1]], color=col[s], lw=1.0, ls="--", alpha=0.8, label=f"this work, no trigger, all crossings")
            ax.set_yscale("log")
            if var == "betagamma": ax.set_xscale("log"); ax.set_xlabel("βγ"); ax.set_ylim(1e-4, 1)
            else: ax.set_xlabel("dE/dx (MeV cm²/g), most probable value, βγ ≥ 0.1"); ax.set_xlim(0, 100); ax.set_ylim(1e-3, 0.5)
            ax.set_ylabel("fraction of hits per bin"); ax.legend(fontsize=7.2, loc="upper right")
        fig.suptitle("Figure 7 (Appendix A): pixel hits, Λ = 2 keV; our bins are not the paper's (paper bin width not stated), so compare shapes and ranges", fontsize=9.5)
        fig.tight_layout(); return fig
    fu.figure("F7_fig7", SRC, plot,
              "Figure 7 of the paper: βγ and dE/dx (PDG most probable value, Eq. 34.12, silicon 200 µm IBL / 250 µm other layers) of the quirk hits on the 4 pixel layers, Λ = 2 keV, "
              "EW 800 GeV and colored 1800 GeV. Main selection: trigger-passing events (colored: both charged) that are fiducial, first crossing of each pixel layer, t < 25 ns. "
              "dE/dx panel: hits with βγ ≥ 0.1 only, as in the paper. Unit area; dotted: the paper's histograms from its vector figures (its bin widths are not stated).",
              [f"{T}/F7_pixel_hits.csv", f"{T}/paper_fig7_vector.json"], "see caption", os.path.abspath(__file__))
    print("figure written")
