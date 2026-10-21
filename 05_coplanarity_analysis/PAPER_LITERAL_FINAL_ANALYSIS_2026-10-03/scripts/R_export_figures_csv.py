#!/usr/bin/env python3
"""Export the data of every final Figure 2-7 of the report (TABLE_I_REPRODUCTION_REPORT_2026-10-19.pdf) for ROOT (2026-10-21) into ROOT_CSV_FIGURES_2026-10-21/.
One folder per figure, one CSV per plotted figure: exactly the numbers drawn in the report (the *_source.csv of FINAL_FIGURES/<name>/), plus the paper's
curves and our traced contour lines where the figure shows them. Every file is numeric so that TTree::ReadFile reads it: text columns are replaced by
integer ids (the meaning of each id is written in README.txt), booleans are 0/1, missing values are -999. Every file is checked to read back with the same
number of rows."""
import os, shutil, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/.."); FIG = f"{ROOT}/FINAL_FIGURES"; OLD = f"{ROOT}/ROOT_CSV_2026-10-19"
OUT = f"{ROOT}/ROOT_CSV_FIGURES_2026-10-21"
if os.path.exists(OUT): shutil.rmtree(OUT)
README = []
FIXED = {"channel": ("channel_id", {"colored": 1, "EW": 2}), "sample": ("sample_id", {"COL2000": 1, "EW2000": 2, "colored_1800GeV_2keV": 1, "EW_800GeV_2keV": 2}),
         "sct": ("sctz_um", {"Z0": 0, "Z1160": 1160})}                    # same ids in every file: 1 = colored, 2 = EW; SCT z in um
def save(df, rel, desc, notes=None, src=""):
    df = df.copy(); maps = {}
    for c, (new, m) in FIXED.items():
        if c in df.columns and df[c].dtype == object:
            assert set(df[c].dropna()) <= set(m), (rel, c, set(df[c].dropna()) - set(m))
            present = set(df[c].dropna()); df[new] = df[c].map(m); df = df.drop(columns=[c]); maps[new] = {k: v for k, v in m.items() if k in present}
    for c in df.columns:
        if df[c].dtype == bool: df[c] = df[c].astype(int)
        elif df[c].dtype == object:
            low = df[c].astype(str).str.lower()
            if set(low.unique()) <= {"true", "false", "nan", "none", ""}: df[c] = low.map({"true": 1, "false": 0}).fillna(-999).astype(int); continue
            num = pd.to_numeric(df[c], errors="coerce")
            if num.notna().sum() == df[c].notna().sum(): df[c] = num; continue
            cats = list(dict.fromkeys(df[c].dropna().astype(str))); ids = {v: i + 1 for i, v in enumerate(cats)}
            df[c + "_id"] = df[c].map(lambda v: ids.get(str(v), -999) if pd.notna(v) else -999); df = df.drop(columns=[c]); maps[c + "_id"] = ids
    df = df.fillna(-999).replace([np.inf, -np.inf], -999)
    p = f"{OUT}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True); df.to_csv(p, index=False)
    assert len(pd.read_csv(p)) == len(df) and all(pd.api.types.is_numeric_dtype(t) for t in pd.read_csv(p).dtypes), rel
    README.append(f"{rel}  ({len(df)} rows)\n  {desc}\n  source: {src}\n  columns: {', '.join(df.columns)}")
    for c, ids in maps.items(): README.append(f"    {c}: " + "; ".join(f"{i} = {v}" for v, i in ids.items()))
    for c, t in (notes or {}).items(): README.append(f"    {c}: {t}")
    README.append(""); print(f"{rel:60s} {len(df):7d} rows")
def src(name): return pd.read_csv(f"{FIG}/{name}/{name}_source.csv", low_memory=False)

# Figure 2
save(src("F39_fig2_combined"), "Fig2/fig2_report_figure.csv", "Report Fig. 2 (3 events x |L| and d vs r): draw each (panel_id, curve_id) as a TGraph of y vs r_cm",
     dict(y="curve L: |L| (hbar); curve d: quirk separation in the CM frame (cm)", r_cm="transverse radius of the CM (cm)"), "FINAL_FIGURES/F39_fig2_combined")
save(src("F42_fig2_log_scale"), "Fig2/fig2_log_scale_four_step_sizes.csv", "Report Fig. 2 on a log scale at 4 integration step sizes (Section 3.1)",
     dict(steps_per_period="integration steps per oscillation period (-999 for the paper curve)", L_signed_hbar="signed L (hbar)"), "FINAL_FIGURES/F42_fig2_log_scale")
save(src("F41_appendixA_diagram"), "Fig2/appendixA_d_L_vs_g.csv", "Appendix-A diagram: d and |L| along the trajectory parameter g", {}, "FINAL_FIGURES/F41_appendixA_diagram")
for f in ("fig2_initial_values_numeric.csv", "fig2_meetings_numeric.csv"):
    save(pd.read_csv(f"{OLD}/Fig2/{f}"), f"Fig2/{f}", "Fig. 2 events: initial values / every meeting (event_id: 0 = paper, 1 = ours with the paper's kinematics, 2 = ours event no. 8)", {}, f"ROOT_CSV_2026-10-19/Fig2/{f}")
# Figure 3
save(src("F30_fig3"), "Fig3/fig3_ours_per_event.csv", "Report Fig. 3: Δφ of the quirk pair vs r, every event (our samples)", dict(dphi_rad="Δφ (rad)"), "FINAL_FIGURES/F30_fig3")
save(pd.read_csv(f"{OLD}/Fig3/fig3_paper.csv"), "Fig3/fig3_paper.csv", "Paper Fig. 3 curves (vector extraction)", {}, "ROOT_CSV_2026-10-19/Fig3/fig3_paper.csv")
# Figure 4
for z, lab in (("Z0", "no SCT z smearing"), ("Z1160", "SCT z 1.16 mm")):
    save(src(f"F29_fig4_{z}"), f"Fig4/fig4_hits_{z}.csv", f"Report Fig. 4 ({lab}): hits of the displayed events in the plane frame (n2, n3), with Δs, Δw",
         dict(rank="event shown (median events)", ellipse="1 if the hit is inside the signal-region ellipse"), f"FINAL_FIGURES/F29_fig4_{z}")
# Figure 5
for z, lab in (("Z0", "no SCT z smearing"), ("Z1160", "SCT z 1.16 mm")):
    save(src(f"F40_fig5_{z}"), f"Fig5/fig5_{z}.csv", f"Report Fig. 5 ({lab}): our Δs, Δw per event (ds, dw in cm) and the paper's histograms (lo, hi, paper_frac)",
         dict(ds="Δs (cm), our events", dw="Δw (cm), our events", lo="paper bin low edge (cm)", hi="paper bin high edge (cm)", paper_frac="paper fraction in the bin"), f"FINAL_FIGURES/F40_fig5_{z}")
# Figure 6
save(src("F6_fig6"), "Fig6/fig6_grid.csv", "Report Fig. 6 grid: N at 300 fb-1 for every (mass, Lambda, SCT z); status: computed / bound / missing",
     dict(eps_trig="matched + shower count (both channels)", eps_trig_LO="EW: LO ratio (alternative)", N_with_f="300 fb-1 x sigma x eps_trig x f_ch x k/n"), "FINAL_FIGURES/F6_fig6")
for f, d in (("fig6_our_contours.csv", "Our Fig. 6 contour lines: draw each (channel_id, sctz_um, charge_factor, n_events, segment) as a TGraph of lambda_eV vs mass_GeV"),
             ("fig6_paper_curves.csv", "Paper Fig. 6 curves (vector extraction); curve ids in ROOT_CSV_2026-10-19/README.txt (5 = discovery, 6 = exclusion)"),
             ("F6_reach_numeric.csv", "Maximum mass reach (main contours)"), ("F6_reach_sensitivity_numeric.csv", "Maximum mass reach of the sensitivity variants")):
    save(pd.read_csv(f"{OLD}/Fig6/{f}"), f"Fig6/{f}", d, {}, f"ROOT_CSV_2026-10-19/Fig6/{f}")
kl = pd.read_csv(f"{ROOT}/fig6/F6_kfactor_lines.csv"); kl.insert(0, "channel_id", kl.pop("channel").map({"colored": 1, "EW": 2}))
kl.insert(1, "K", kl.variant.map(lambda v: float(v[1:]) if v.startswith("K") else -999))
save(kl, "Fig6/fig6_kfactor_lines.csv", "Report F6_kfactor: contour lines with sigma x K and the EW LO-ratio trigger (no SCT z smearing, charge factor included); draw each "
     "(channel_id, variant_id, n_events, segment) as a TGraph of lambda_eV vs mass_GeV", dict(n_events="3 exclusion, 5 discovery"), "fig6/F6_kfactor_lines.csv (F6_05_sensitivity.py)")
# Figure 7
save(src("F7_fig7"), "Fig7/fig7_report_histograms.csv", "Report Fig. 7 histograms: our three selections and the paper (selection_id), dE/dx (MeV cm2/g) and betagamma (var_id); one row per bin (lo, hi, frac)",
     dict(frac="fraction of hits in the bin", n_hits="hits in the selection", x="paper step-path vertex x", y="paper step-path vertex y"), "FINAL_FIGURES/F7_fig7")
for f, d in (("fig7_pixel_hits.csv", "every quirk hit on the 4 pixel layers (unbinned; for your own histograms)"),
             ("fig7_paper_curves.csv", "paper Fig. 7 step histograms (vector extraction)"), ("fig7_dedx_definition_test.csv", "report Section 9.1: the paper's betagamma histogram converted with four dE/dx definitions")):
    save(pd.read_csv(f"{OLD}/Fig7/{f}"), f"Fig7/{f}", d, {}, f"ROOT_CSV_2026-10-19/Fig7/{f}")
shutil.copy(f"{OLD}/plot_examples.C", f"{OUT}/plot_examples.C")
open(f"{OUT}/README.txt", "w").write(
    "Data of the final Figures 2-7 of TABLE_I_REPRODUCTION_REPORT_2026-10-19.pdf (arXiv:1708.02243 reproduction), for ROOT. Written 2026-10-21 by scripts/R_export_figures_csv.py.\n"
    "Every file: one header line, comma separated, numeric only (text replaced by *_id columns, explained below), booleans 0/1, missing = -999.\n"
    "ROOT: TTree t; t.ReadFile(\"Fig6/fig6_kfactor_lines.csv\", \"\", ',');  (branches are Float_t)   or   auto df = ROOT::RDF::FromCSV(\"Fig6/fig6_grid.csv\");\n"
    "Lines (Fig. 2, Fig. 6): draw one TGraph per group of the id columns listed in the file description, ordered by the point column.\n"
    "Table I and background data: ROOT_CSV_2026-10-19/.\n\n" + "\n".join(README))
print("written", OUT)
