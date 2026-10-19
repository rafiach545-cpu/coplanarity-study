#!/usr/bin/env python3
"""Export every result needed to redraw the report's tables and Figures 2-7 with ROOT (2026-10-19; EW trigger = matched count, the paper's method) into ROOT_CSV_2026-10-19/.
Rules: one header line, comma separated, missing numbers written as -999, booleans as 0/1, string columns only where unavoidable (labels).
Everything is read from the existing result files (no recomputation, except Figure 6 contour lines, which are traced from fig6/F6_N_grid.csv with the
same interpolation as F6_03_contours.py). A README.txt lists every file, its columns, units and source."""
import os, sys, json, shutil, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/.."); sys.path.insert(0, HERE)
OUT = f"{ROOT}/ROOT_CSV_2026-10-19"; T = f"{ROOT}/tables"; FIG = f"{ROOT}/FINAL_FIGURES"
README = []
def save(df, rel, desc, cols, src):
    p = f"{OUT}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True)
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == bool: df[c] = df[c].astype(int)
        elif df[c].dtype == object:
            low = df[c].astype(str).str.lower()
            if set(low.unique()) <= {"true", "false", "nan", "none", ""}: df[c] = low.map({"true": 1, "false": 0}).fillna(-999).astype(int)
    df = df.fillna(-999); df.to_csv(p, index=False)
    README.append(f"{rel}  ({len(df)} rows)\n  {desc}\n  source: {src}\n" + "".join(f"    {c}: {cols.get(c, '')}\n" for c in df.columns))
    print(f"{rel:60s} {len(df):7d} rows")
if os.path.exists(OUT): shutil.rmtree(OUT)
TR = lambda s: s.astype(str) == "True"
# ------------------------------------------------------------------ Table I
L0 = pd.read_csv(f"{T}/lambda_scan_summary.csv"); L1 = pd.read_csv(f"{T}/lambda_scan_z1160_summary.csv")
LS = pd.concat([L0[L0["sample"].isin(["COL2000", "EW2000"]) & (L0.sct == "Z0")], L1]); LS = LS[LS["mode"] == "FIRST"]
t1 = pd.DataFrame(dict(channel=np.where(LS["sample"] == "COL2000", 1, 2), mass_GeV=np.where(LS["sample"] == "COL2000", 1800, 800), lambda_keV=LS.lambda_keV,
                       sctz_um=np.where(LS.sct == "Z0", 0, 1160), n_fid=LS.n_fid, k_signal_region=LS.k_ge2, eps_reco=LS.k_ge2 / LS.n_fid,
                       sigma_eps=np.sqrt(LS.k_ge2 / LS.n_fid * (1 - LS.k_ge2 / LS.n_fid) / LS.n_fid), paper_eps_reco=LS.paper_reco)).sort_values(["channel", "sctz_um", "lambda_keV"])
save(t1, "TableI/tableI_eps_reco.csv", "Table I reconstruction efficiency per Lambda (production samples, 2000 events, first crossing)",
     dict(channel="1 = colored (m = 1800 GeV), 2 = EW (m = 800 GeV)", mass_GeV="quirk mass", lambda_keV="string tension", sctz_um="SCT z smearing (0 = none, 1160 = 1.16 mm)",
          n_fid="fiducial events (denominator)", k_signal_region="events in the signal region", eps_reco="k / n_fid", sigma_eps="sqrt(eps(1-eps)/n)", paper_eps_reco="paper Table I"),
     "tables/lambda_scan_summary.csv, tables/lambda_scan_z1160_summary.csv")
tc = pd.DataFrame([dict(channel=1, mass_GeV=1800, n_matched=873, n_trigger=207, n_trigger_both_charged=68, n_fid_2keV=22, eps_trig=207 / 873, eps_fid=22 / 68, paper_eps_trig=0.24, paper_eps_fid=0.28),
                   dict(channel=2, mass_GeV=800, n_matched=1045, n_trigger=186, n_trigger_both_charged=186, n_fid_2keV=62, eps_trig=186 / 1045, eps_fid=62 / 186, paper_eps_trig=0.10, paper_eps_fid=0.28)])
save(tc, "TableI/tableI_trigger_fiducial.csv", "Trigger and fiducial efficiency, production samples (fiducial at the benchmark Lambda: colored 2 keV, EW 4 keV)",
     dict(n_trigger="pT(QQ) > 200 GeV", n_trigger_both_charged="colored: both quirk-hadrons charged (EW: = n_trigger)", n_fid_2keV="fiducial events at the benchmark Lambda",
          eps_trig="n_trigger / n_matched", eps_fid="n_fid / n_trigger_both_charged"), "report Table I (R_data_2026_10_15.production)")
pe = []
for f, z in ((f"{T}/lambda_scan_per_event.csv", 0), (f"{T}/lambda_scan_z1160_per_event.csv", 1160)):
    x = pd.read_csv(f); x = x[x["sample"].isin(["COL2000", "EW2000"]) & (x["mode"] == "FIRST") & (x.sct == ("Z0" if z == 0 else "Z1160"))]
    for (s, lam), g in x.groupby(["sample", "lambda_keV"]):
        fid = TR(g.fid); pe.append(dict(channel=1 if s == "COL2000" else 2, lambda_keV=lam, sctz_um=z, n_fid=int(fid.sum()), n_plane=int((fid & TR(g.plane)).sum()),
                                        n_hits=int((fid & TR(g.plane) & TR(g.mult)).sum()), n_signal_region=int((fid & TR(g.final)).sum())))
save(pd.DataFrame(pe), "TableI/tableI_cutflow.csv", "Cut-flow after the fiducial requirement, per Lambda (production samples)",
     dict(n_plane="plane found (Dw < 1 cm)", n_hits="+ hit multiplicity", n_signal_region="+ Ds < 0.01 cm"), "tables/lambda_scan_*per_event.csv")
# EW LO samples (D41)
lo = []
for tag, lab in (("mg5_373_lo", 1), ("mg5_373_lo_showered", 2)):
    d = pd.DataFrame([r for l in open(f"{ROOT}/logs/D41_{tag}_events.jsonl") for r in json.loads(l)]); n = d.event.nunique()
    for lam, g in d.groupby("lambda_keV"):
        fid = g.fid.astype(bool); lo.append(dict(sample=lab, lambda_keV=lam, n_events=n, n_fid=int(fid.sum()), k_signal_region=int((fid & g.final.astype(bool)).sum())))
for lam in (1, 2, 3, 4, 5):
    r = t1[(t1.channel == 2) & (t1.sctz_um == 0) & (t1.lambda_keV == lam)].iloc[0]; lo.append(dict(sample=0, lambda_keV=lam, n_events=186, n_fid=r.n_fid, k_signal_region=r.k_signal_region))
LOd = pd.DataFrame(lo); LOd["eps_reco"] = LOd.k_signal_region / LOd.n_fid; LOd["eps_fid"] = LOd.n_fid / LOd.n_events
save(LOd.sort_values(["sample", "lambda_keV"]), "TableI/EW_LO_samples.csv", "EW 800 GeV: production vs leading-order samples (no SCT z smearing, first crossing)",
     dict(sample="0 = production (matched + shower), 1 = LO no shower (3000 events), 2 = LO + Pythia shower (2792 events with pT(QQ) > 200 GeV)", n_events="events in the sample (production: triggered)"),
     "logs/D41_*_events.jsonl, Table I")
# ------------------------------------------------------------------ Figure 2
md = pd.read_csv(f"{T}/fig2_final/fig2_meetings_detail.csv"); md["event_id"] = md.event.map({"paper": 0, "constructed": 1, "key 8": 2})
md["r_L_zero_between_cm"] = pd.to_numeric(md.r_L_zero_between_cm, errors="coerce")
save(md.drop(columns=["event"]), "Fig2/fig2_meetings_numeric.csv", "Figure 2 per meeting, numeric (event_id 0 = paper, 1 = ours with the paper's kinematics, 2 = ours event no. 8)",
     dict(r_L_zero_between_cm="r where |L| = 0 between the meetings (-999 = none)", b_cm="impact parameter |L|/p* (cm)"), "tables/fig2_final/fig2_meetings_detail.csv")
for f in ("fig2_paper_L.csv", "fig2_paper_d.csv", "fig2_ours_constructed.csv", "fig2_ours_key8.csv", "fig2_initial_values.csv", "fig2_meetings_detail.csv"):
    save(pd.read_csv(f"{T}/fig2_final/{f}"), f"Fig2/{f}", "Figure 2 (see tables/fig2_final/README.txt)", dict(r_cm="transverse radius of the CM (cm)", d_cm="quirk separation in the CM frame (cm)",
         L_1e12_hbar="|L| (1e12 hbar)"), f"tables/fig2_final/{f}")
st = pd.read_csv(f"{T}/fig2_final/fig2_ours_constructed_steps.csv")
save(st, "Fig2/fig2_logscale_four_step_sizes.csv", "Figure 2 on a log scale: event with the paper's kinematics at 4 integration step sizes",
     dict(steps_per_period="RK4 steps per oscillation", L_signed_hbar="L projected on its maximum direction (hbar); plot |L|"), "tables/fig2_final/fig2_ours_constructed_steps.csv")
save(pd.read_csv(f"{FIG}/F41_appendixA_diagram/F41_appendixA_diagram_source.csv"), "Fig2/appendixA_d_L_vs_g.csv", "d and |L| vs g (half-oscillations) for the Appendix A diagram",
     dict(g="time in half-oscillations (= r / meeting spacing)"), "FINAL_FIGURES/F41_appendixA_diagram")
# ------------------------------------------------------------------ Figure 3
f3 = pd.read_csv(f"{FIG}/F30_fig3/F30_fig3_source.csv"); f3["channel"] = np.where(f3["sample"] == "COL2000", 1, 2)
save(f3[["channel", "key", "r_cm", "dphi_rad"]], "Fig3/fig3_ours_per_event.csv", "Figure 3: rotation Dphi of the plane of the two velocity vectors vs r, every fiducial event, Lambda = 2 keV",
     dict(channel="1 = colored 1800 GeV, 2 = EW 800 GeV", key="event id"), "FINAL_FIGURES/F30_fig3")
p3 = pd.read_csv(f"{T}/paper_fig3_curves.csv"); n3 = sorted(p3.curve.unique()); p3["curve_id"] = p3.curve.map({n: i for i, n in enumerate(n3)})
save(p3.drop(columns=["curve"]), "Fig3/fig3_paper.csv", "Figure 3 paper curves (vector extraction): " + ", ".join(f"curve_id {i} = {n}" for i, n in enumerate(n3)), dict(curve_id="see description"), "tables/paper_fig3_curves.csv")
# ------------------------------------------------------------------ Figure 4
for z in ("Z0", "Z1160"):
    d = pd.read_csv(f"{FIG}/F29_fig4_{z}/F29_fig4_{z}_source.csv"); d["channel"] = np.where(d["sample"] == "COL2000", 1, 2); d["is_layer_ellipse"] = d.ellipse.astype(str) == "True"
    save(d.drop(columns=["sample", "sct", "ellipse"]), f"Fig4/fig4_hits_{z}.csv", f"Figure 4: hits of the median-Ds signal event projected on (n3, n2); SCT z {'none' if z == 'Z0' else '1.16 mm'}",
         dict(n2_cm="coordinate along n2 (cm)", n3_cm="coordinate along n3 (cm)", is_layer_ellipse="1 = point of a detector-layer ellipse, 0 = hit"), f"FINAL_FIGURES/F29_fig4_{z}")
# ------------------------------------------------------------------ Figure 5
for z in ("Z0", "Z1160"):
    d = pd.read_csv(f"{FIG}/F40_fig5_{z}/F40_fig5_{z}_source.csv"); pop = {"colored": 1, "EW": 2, "converted γ + pile-up": 3, "pile-up": 4}
    d["population_id"] = d.population.map(pop)
    ours = d[d.ds.notna()][["population_id", "ds", "dw"]].rename(columns={"ds": "ds_cm", "dw": "dw_cm"})
    pap = d[d.paper_var.notna()][["population_id", "paper_var", "lo", "hi", "paper_frac"]]; pap["var_id"] = np.where(pap.paper_var == "ds", 1, 2)
    save(ours, f"Fig5/fig5_ours_{z}.csv", f"Figure 5: Ds and Dw of every plane after the plane and hit cuts (before the Ds cut); signal and background SCT z {'none' if z == 'Z0' else '1.16 mm'}",
         dict(population_id="1 colored signal, 2 EW signal, 3 converted photon + pile-up, 4 pile-up only"), f"FINAL_FIGURES/F40_fig5_{z}")
    if z == "Z0": save(pap.drop(columns=["paper_var"]), "Fig5/fig5_paper_histograms.csv", "Figure 5 paper histograms (unit area)", dict(var_id="1 = Ds, 2 = Dw", lo="bin low edge (cm)", hi="bin high edge (cm)",
                       paper_frac="fraction per bin"), "tables/paper_fig5_vector.json")
# ------------------------------------------------------------------ Figure 6
G = pd.read_csv(f"{ROOT}/fig6/F6_N_grid.csv"); G["channel_id"] = np.where(G.channel == "colored", 1, 2); G["sctz_um"] = np.where(G.sct == "Z0", 0, 1160)
st_map = {"computed": 1, "bound": 2, "missing": 0, "not run": 0}
for c in ("status_with_f", "status_without_f"): G[c] = G[c].map(st_map)
keep = ["channel_id", "mass_gev", "lambda_keV", "sctz_um", "sigma_fb", "eps_trig", "eps_trig_LO", "f_ch", "n_prop", "n_fid", "k", "n_integration_fail", "eps_fid", "eps_reco", "N_with_f", "N_with_f_lo",
        "N_with_f_hi", "N_without_f", "N_without_f_lo", "N_without_f_hi", "N_with_f_UL95_if_k0", "N_without_f_UL95_if_k0", "status_with_f", "status_without_f"]
save(G[keep], "Fig6/fig6_grid.csv", "Figure 6 grid: expected signal events at 300 fb-1 for every (mass, Lambda, SCT z)",
     dict(channel_id="1 colored, 2 EW", sigma_fb="matched cross section (fb)", eps_trig="count N(pT(QQ) > 200) / N(matched) of the matched + shower sample (both channels)", eps_trig_LO="EW: LO ratio sigma(QQ+j, pT > 200) / sigma(QQ) (alternative); colored: = eps_trig", f_ch="colored: fraction with both quirk-hadrons charged (EW 1)",
          n_prop="propagated events", k="events in the signal region", N_with_f="300 fb-1 x sigma x eps_trig x f_ch x k/n", N_with_f_lo="N at the Wilson 68% lower bound of k/n",
          N_without_f="colored without f_ch", N_with_f_UL95_if_k0="95% upper limit on N when k = 0", status_with_f="1 computed, 2 bound (max possible N < 3, not propagated), 0 not available"),
     "fig6/F6_N_grid.csv")
# our contour lines (same interpolation as F6_03_contours.py)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
V = json.load(open(f"{T}/paper_fig6_vector.json")); cal = V["colored"]["calibration"]
_al = np.polyfit([np.log10(v) for v, _ in cal["y_log_ticks"]], [p for _, p in cal["y_log_ticks"]], 1); _bl = np.polyfit([v for v, _ in cal["y_lin_ticks"]], [p for _, p in cal["y_lin_ticks"]], 1)
Yd = lambda l: -np.where(np.asarray(l, float) <= 1000, np.polyval(_al, np.log10(np.clip(np.asarray(l, float), 1e-6, None))), np.polyval(_bl, np.asarray(l, float)))
ylog = np.linspace(Yd(10), Yd(1000), 2000); yl = np.linspace(Yd(1000), Yd(40000), 4000)
inv_y = lambda y: np.where(y <= Yd(1000), 10 ** np.interp(y, Yd(10 ** np.linspace(1, 3, 2000)), np.linspace(1, 3, 2000)), np.interp(y, Yd(np.linspace(1000, 40000, 4000)), np.linspace(1000, 40000, 4000)))
LAMS = sorted(G.lambda_keV.unique()); rows = []
for ch in ("colored", "EW"):
    for z in ("Z0", "Z1160"):
        for col in (("N_with_f", "N_without_f") if ch == "colored" else ("N_with_f",)):
            g = G[(G.channel == ch) & (G.sct == z)]; ms = sorted(g.mass_gev.unique()); ys = Yd(np.array(LAMS) * 1e3); Z = np.full((len(ms), len(LAMS)), np.nan)
            for i, m in enumerate(ms):
                for j, lam in enumerate(LAMS):
                    r = g[(g.mass_gev == m) & np.isclose(g.lambda_keV, lam)].iloc[0]; s = r[f"status_{col[2:]}"]
                    if (s == 2 and r[col] < 3) or (s == 1 and r.k > 0): Z[i, j] = np.log10(r[col])
            f = RegularGridInterpolator((ms, ys), Z, bounds_error=False, fill_value=np.nan)
            mm, yy = np.meshgrid(np.linspace(ms[0], ms[-1], 400), np.linspace(ys[0], ys[-1], 400), indexing="ij")
            cs = plt.contour(mm, yy, f(np.column_stack([mm.ravel(), yy.ravel()])).reshape(mm.shape), levels=[np.log10(3), np.log10(5)]); plt.close("all")
            for lev, segs in zip((3, 5), cs.allsegs):
                for sid, seg in enumerate(segs):
                    for k, (x, y) in enumerate(seg): rows.append(dict(channel_id=1 if ch == "colored" else 2, sctz_um=0 if z == "Z0" else 1160, charge_factor=int(col == "N_with_f"),
                                                                     n_events=lev, segment=sid, point=k, mass_GeV=x, lambda_eV=float(inv_y(np.array(y)))))
save(pd.DataFrame(rows), "Fig6/fig6_our_contours.csv", "Our Figure 6 contour lines (3 = exclusion, 5 = discovery); draw each (channel, sctz, charge_factor, n_events, segment) as a TGraph",
     dict(charge_factor="colored: 1 with the both-charged factor, 0 without (EW: 1)", n_events="3 or 5", segment="separate line pieces", lambda_eV="string tension (eV)"), "traced from fig6/F6_N_grid.csv")
pc = pd.read_csv(f"{T}/paper_fig6_curves.csv"); pc["channel_id"] = np.where(pc.panel == "colored", 1, 2)
names = sorted(pc.curve.unique()); pc["curve_id"] = pc.curve.map({n: i for i, n in enumerate(names)})
save(pc[["channel_id", "curve_id", "point", "m_GeV", "lambda_eV"]], "Fig6/fig6_paper_curves.csv", "Paper Figure 6 curves (vector extraction): " + ", ".join(f"{i} = {n}" for i, n in enumerate(names)),
     dict(curve_id="see description"), "tables/paper_fig6_curves.csv")
for f, d in (("F6_reach.csv", "maximum mass reach (main variants)"), ("F6_reach_sensitivity.csv", "maximum mass reach for the normalisation-sensitivity variants"), ("F6_ew_lo_ratio.csv", "EW LO cross sections and trigger ratio")):
    save(pd.read_csv(f"{ROOT}/fig6/{f}"), f"Fig6/{f}", d, {}, f"fig6/{f}")
# ------------------------------------------------------------------ Figure 7
H = pd.read_csv(f"{T}/F7_pixel_hits.csv"); H["channel_id"] = np.where(H["sample"].str.startswith("colored"), 1, 2)
save(H.drop(columns=["sample"]), "Fig7/fig7_pixel_hits.csv", "Figure 7: every quirk hit on the 4 pixel layers, Lambda = 2 keV (EW 800 GeV, colored 1800 GeV)",
     dict(channel_id="1 colored 1800 GeV, 2 EW 800 GeV", triggered="1 = pT(QQ) > 200 GeV event", fiducial_event="1 = fiducial at 2 keV", in_25ns="1 = hit time < 25 ns",
          order="0 = first crossing of that layer", betagamma="|p|/m at the crossing", dEdx_MPV_MeVcm2g="PDG most probable value (MeV cm2/g), only for betagamma >= 0.1"),
     "tables/F7_pixel_hits.csv (main selection of the figure: triggered, fiducial_event, order 0, in_25ns)")
p7 = pd.read_csv(f"{T}/paper_fig7_curves.csv"); p7["channel_id"] = np.where(p7["sample"].str.startswith("colored"), 1, 2); p7["var_id"] = np.where(p7.panel == "dEdx", 1, 2)
save(p7[["var_id", "channel_id", "point", "x", "y"]], "Fig7/fig7_paper_curves.csv", "Paper Figure 7 step histograms (vector extraction)", dict(var_id="1 = dE/dx (MeV cm2/g), 2 = betagamma"), "tables/paper_fig7_curves.csv")
# ------------------------------------------------------------------ backgrounds
bg = pd.DataFrame([dict(sample=1, sctz_um=1160, n_events=9139, n_signal_region=0), dict(sample=1, sctz_um=0, n_events=9139, n_signal_region=146), dict(sample=2, sctz_um=1160, n_events=5000, n_signal_region=0)])
save(bg, "Backgrounds/backgrounds_signal_region.csv", "Backgrounds in the signal region", dict(sample="1 = converted photon + pile-up (mu = 50), 2 = pile-up only"), "report Section 7")
open(f"{OUT}/README.txt", "w").write(
    "CSV files to redraw the Table I reproduction of arXiv:1708.02243 with ROOT (2026-10-19). One header line, comma separated, missing values = -999, booleans 0/1.\n"
    "ROOT: auto df = ROOT::RDF::FromCSV(\"Fig6/fig6_grid.csv\");  or  TTree t; t.ReadFile(\"file.csv\", \"\", ',');  (the header line gives the branch names)\n"
    "TGraph from two columns: TGraph g(\"file.csv\", \"%*lg,%lg,%lg\", \",\")  -- skip columns with %*lg.\n\n" + "\n".join(README))
shutil.copy(f"{HERE}/ROOT_plot_examples.C", f"{OUT}/plot_examples.C")              # example macro (tested with ROOT)
print("written", OUT)
