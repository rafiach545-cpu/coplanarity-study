#!/usr/bin/env python3
"""07 signal figures (ROOT, 2026-11-18), step 2 of 2: paper-style signal figures from data/*.csv (prepare_signal_data.py). Nothing is computed here
beyond histogram filling and ratios of CSV columns. Style and helpers: 06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py, its code before the
first figure, executed unchanged (as make_figures_07.py); save() writes this script's name into provenance.json.
Run with /home/rafia/miniconda3/envs/root-env/bin/python. Output per figure: Sxx_<name>/Sxx_<name>.{pdf,png,root,C}, caption.md, provenance.json."""
import os
_src = open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/../../06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py")).read()
exec(_src[:_src.index("# ---------- contour figures")])
SC = {"Z0": C("#6250d6"), "A580": C("#2a78d6"), "Z1160": C("#1baf7a")}       # identity: SCT setting, as in 07 G figures
SCTL = {"Z0": "#sigma_{long}^{SCT} = 0 (best case)", "A580": "SCT 17 #mum / 580 #mum (ATLAS)", "Z1160": "SCT 34 #mum / 1.16 mm (Knapen)"}
SCTT = {"Z0": "σ_long = 0 (best case)", "A580": "the ATLAS intrinsic SCT resolution 17 µm / 580 µm (A580, headline)", "Z1160": "Knapen's SCT 34 µm / 1.16 mm (Z1160)"}
GEO = {"S2_Run3_ATLAS": "Stage 2 #upoint Run 3 #upoint ATLAS", "S1_Run3_Ideal": "Stage 1 #upoint Run 3 #upoint Ideal"}
BEN = {"colored": "colored (3,1)_{2/3}, m_{Q} = 1800 GeV, #Lambda = 2 keV", "EW": "EW (1,1)_{1}, m_{Q} = 800 GeV, #Lambda = 4 keV"}


def save(c, name, caption, inputs):
    d = f"{HERE}/{name}"; os.makedirs(d, exist_ok=True)
    st.SetPaperSize(c.GetWw() / 100.0, c.GetWh() / 100.0); c.Print(f"{d}/{name}.pdf", "pdf Portrait")
    for ext in ("root", "C"): c.SaveAs(f"{d}/{name}.{ext}")
    subprocess.run([PDFTOPPM, "-png", "-r", "250", "-cropbox", "-singlefile", f"{d}/{name}.pdf", f"{d}/{name}"], check=True)
    open(f"{d}/caption.md", "w").write(caption.strip() + "\n")
    json.dump(dict(figure=name, script="make_signal_figures.py (ROOT %s)" % ROOT.gROOT.GetVersion(), data={i: sha(f"{D}/{i}") for i in inputs},
                   data_prepared_by="prepare_signal_data.py", upstream_sources=json.load(open(f"{D}/sources.json"))), open(f"{d}/provenance.json", "w"), indent=1)
    KEEP.clear()


def two(name, w=1700, h=820):
    c = ROOT.TCanvas(name, name, w, h); hd = ROOT.TPad("hd", "", 0, 0.92, 1, 1); top = ROOT.TPad("top", "", 0, 0.14, 1, 0.92); bot = ROOT.TPad("bot", "", 0, 0, 1, 0.14)
    for q in (hd, top, bot): q.Draw()
    KEEP.extend([c, hd, top, bot]); top.Divide(2, 1, 0.002, 0.002); return c, hd, top, bot


# ---------- S01: Table I analogue, step efficiencies
CF = read("cutflow.csv"); STEPS = ["fiducial", "plane", "multiplicity", "delta_s", "eps_reco"]
SL = {"fiducial": "#varepsilon_{fid}", "plane": "plane", "multiplicity": "mult.", "delta_s": "#Deltas cut", "eps_reco": "#varepsilon_{reco}"}
c, hd, top, bot = two("S01")
header(hd, "Signal selection at the Table I benchmarks, 13.6 TeV, 10k events: ATLAS (filled) vs Ideal (open)")
leg = []
for k, ch in enumerate(("colored", "EW"), 1):
    p = top.cd(k); p.SetBottomMargin(0.2); h = frame(p, -0.5, 0, 4.5, 1.25, "", "fraction of the previous step")
    ax = h.GetXaxis(); ax.SetNdivisions(5, False); ax.SetLabelSize(0)
    for i, s in enumerate(STEPS): text(i, -0.04, SL[s], 0.05, 23, INK2, ndc=False)
    text(0.17, 0.86, BEN[ch], 0.045)
    for j, s in enumerate(("A580", "Z1160", "Z0")):
        for g_, (setup, mk_) in enumerate((("S2_Run3_ATLAS", 20), ("S1_Run3_Ideal", 24))):
            rr = {r["step"]: r for r in CF if r["channel"] == ch and r["sct"] == s and r["setup"] == setup}
            xs = [i + (j - 1) * 0.2 + (g_ - 0.5) * 0.08 for i in range(len(STEPS))]; ys = [fl(rr[t]["frac_of_prev"]) for t in STEPS]
            g = gerr(xs, ys, [y - fl(rr[t]["frac_lo"]) for y, t in zip(ys, STEPS)], [fl(rr[t]["frac_hi"]) - y for y, t in zip(ys, STEPS)], SC[s], mk_, size=1.4); g.Draw("P same")
            if k == 1: leg.append((g, f"{SCTL[s]}, {'ATLAS' if g_ == 0 else 'Ideal'}", "p"))
    l = ROOT.TLine(3.5, 0, 3.5, 1.25); l.SetLineColor(GRID); l.SetLineStyle(2); l.Draw(); KEEP.append(l)
bot.cd(); legend(0.03, 0.05, 0.97, 0.95, leg, ncol=3, size=0.2)
cap = ["**S01.** Signal selection at the benchmark points of the paper's Table I (colored 1800 GeV at Λ = 2 keV, left; EW 800 GeV at Λ = 4 keV, right), "
       "√s = 13.6 TeV, the same 10 000-generated-event samples in both geometries. Filled: Stage 2 · Run 3 · ATLAS (barrel and end-caps, 8 ATLAS-like stations); "
       "open: Stage 1 · Run 3 · Ideal (the 8 barrel layers of Knapen et al.). Each point is the fraction of the previous step: ε_fid = fiducial / propagated "
       "(triggered; colored: both quirk-hadrons charged); then plane found (Δw < 1 cm), hit multiplicity (all 8 stations hit, ≥ 7 with two hits), Δs < 0.01 cm; "
       "right of the dashed line ε_reco = final / fiducial. Colours: SCT setting. Wilson 68% errors. No pile-up on the signal. Table: Table_I.md. Source: data/cutflow.csv."]
save(c, "S01_table_I_cutflow", cap[0], ["cutflow.csv"])
rows = ["| geometry | benchmark | SCT | matched | triggered | propagated | ε_trig | ε_fid | plane | multiplicity | Δs | ε_reco |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for setup in GEO:
    for ch in ("colored", "EW"):
        for s in ("A580", "Z1160", "Z0"):
            rr = {r["step"]: r for r in CF if r["channel"] == ch and r["sct"] == s and r["setup"] == setup}
            f = lambda t: f"{fl(rr[t]['frac_of_prev']):.3f}"
            rows.append(f"| {setup.replace('_', ' · ')} | {ch} {rr['matched']['mass_gev']} GeV, {rr['matched']['lambda_keV']} keV | {s} | {rr['matched']['n']} | {rr['triggered']['n']} | "
                        f"{rr['propagated']['n']} | {f('triggered')} | {f('fiducial')} ({rr['fiducial']['n']}) | {f('plane')} | {f('multiplicity')} | {f('delta_s')} | {f('eps_reco')} ({rr['eps_reco']['n']}) |")
open(f"{HERE}/S01_table_I_cutflow/Table_I.md", "w").write("Signal efficiencies at the Table I benchmarks (data/cutflow.csv). Each column after ε_fid is the fraction of the previous step. "
                                                         "Colored: 'propagated' = triggered with both quirk-hadrons charged.\n\n" + "\n".join(rows) + "\n")

# ---------- S02-S04: paper Fig. 5 analogue, Delta_s and Delta_w distributions
DS = read("ds_dw.csv")
for n_, s in enumerate(("A580", "Z1160", "Z0"), 2):
    c, hd, top, bot = layout(f"S0{n_}", w=1600, h=1450)
    header(hd, f"Signal #Deltas and #Deltaw, {SCTL[s]}, 13.6 TeV, same 10k events")
    leg = []
    for k, (ch, var, lo, hi) in enumerate([("colored", "ds_cm", 1e-4, 0.1), ("colored", "dw_cm", 1e-3, 1.0), ("EW", "ds_cm", 1e-4, 0.1), ("EW", "dw_cm", 1e-3, 1.0)], 1):
        p = top.cd(k); nb = 30; edges = array.array("d", [lo * (hi / lo) ** (i / nb) for i in range(nb + 1)]); hs = []
        for setup, col, sty in (("S2_Run3_ATLAS", SC["A580"] if s == "A580" else SC[s], 1), ("S1_Run3_Ideal", MUTED, 2)):
            rr = [r for r in DS if r["setup"] == setup and r["channel"] == ch and r["sct"] == s]
            hh = ROOT.TH1D(f"h{k}{setup}{s}", "", nb, edges); KEEP.append(hh)
            for r in rr: hh.Fill(min(max(fl(r[var]), lo * 1.0001), hi * 0.9999))
            nf = fl(rr[0]["n_fid"]) if rr else 1.0; hh.Scale(1.0 / nf if nf else 1.0)
            hh.SetLineColor(col); hh.SetLineWidth(3); hh.SetLineStyle(sty); hs.append(hh)
            if k == 1: leg.append((hh, GEO[setup], "l"))
        ymax = max(h_.GetMaximum() for h_ in hs) * 1.35 or 1
        frame(p, lo, 0, hi, ymax, "#Deltas [cm]" if var == "ds_cm" else "#Deltaw [cm]", "fraction of fiducial events", logx=True)
        for h_ in hs: h_.Draw("hist same")
        cut = 0.01 if var == "ds_cm" else 1.0
        if cut < hi * 0.999:
            l = ROOT.TLine(cut, 0, cut, ymax * 0.78); l.SetLineColor(INK2); l.SetLineStyle(7); l.Draw(); KEEP.append(l); text(cut * 1.1, ymax * 0.6, "cut", 0.04, 11, INK2, ndc=False)
        text(0.17, 0.86, BEN[ch], 0.042)
    bot.cd(); legend(0.15, 0.15, 0.85, 0.85, leg, ncol=2, size=0.3)
    save(c, f"S0{n_}_fig5_ds_dw_{s}", f"""**S0{n_}.** Analogue of the paper's Fig. 5: Δs (left) and Δw (right) of the reconstructed plane for signal events at the Table I benchmarks
(top: colored 1800 GeV, Λ = 2 keV; bottom: EW 800 GeV, Λ = 4 keV), √s = 13.6 TeV, {SCTT[s]}. Every fiducial event in which a plane is found (Δw < 1 cm is part of
the plane selection, so Δw ends at 1 cm). Normalised to the number of fiducial events, so a histogram's integral is the plane fraction. Blue solid: Stage 2 · Run 3 · ATLAS;
grey dashed: Stage 1 · Run 3 · Ideal; the same 10 000-generated-event samples. Dashed vertical line: the Δs < 0.01 cm cut. Values outside the axis range (Δs up to 0.1 cm shown) are put in the
first or last bin. No pile-up on the signal. Source: data/ds_dw.csv.""", ["ds_dw.csv"])

# ---------- S05: sensitivity of the signal selection to pixel merging and to the multiplicity threshold
if os.path.exists(f"{D}/sensitivity.csv"):
    SN = [r for r in read("sensitivity.csv") if r["lambda_keV"] == "all"]
    VAR = [(a, t) for a in ("0", "1", "2") for t in ("14", "15", "16")]
    c, hd, top, bot = two("S05")
    header(hd, "Signal vs merge adjacency a and multiplicity threshold T, relative to production (a = 1, T = 15), #Lambda = 1-10 keV")
    leg = []
    for k, (smp, lab) in enumerate((("colored_1800gev", "colored, m_{Q} = 1800 GeV"), ("EW_800gev", "EW, m_{Q} = 800 GeV")), 1):
        p = top.cd(k); p.SetBottomMargin(0.24); h = frame(p, -0.5, 0.3, 8.5, 1.7, "", "k / k(a = 1, T = 15)"); h.GetXaxis().SetLabelSize(0); h.GetXaxis().SetNdivisions(9, False)
        for i, (a, t) in enumerate(VAR): text(i, 0.28, f"T={t}", 0.04, 23, INK2, ndc=False)
        for g0, a in enumerate(("0", "1", "2")): text(3 * g0 + 1, 0.205, f"a = {a}" + (" (production)" if a == "1" else ""), 0.045, 23, INK, ndc=False)
        for xg in (2.5, 5.5):
            lg = ROOT.TLine(xg, 0.3, xg, 1.7); lg.SetLineColor(GRID); lg.SetLineStyle(2); lg.Draw(); KEEP.append(lg)
        one = ROOT.TLine(-0.5, 1, 8.5, 1); one.SetLineColor(GRID); one.Draw(); KEEP.append(one)
        text(0.17, 0.86, lab, 0.045)
        for j, s in enumerate(("A580", "Z0")):
            for g_, (setup, mk_) in enumerate((("S2_Run3_ATLAS", 20), ("S1_Run3_Ideal", 24))):
                rr = {(r["merge_adj"], r["threshold"]): r for r in SN if r["sample"] == smp and r["sct"] == s and r["setup"] == setup}
                if not rr: continue
                ref = fl(rr[("1", "15")]["k"]); xs, ys, el, eh = [], [], [], []
                for i, v in enumerate(VAR):
                    kk = fl(rr[v]["k"]); xs.append(i + (j - 0.5) * 0.25 + (g_ - 0.5) * 0.1); ys.append(kk / ref if ref else float("nan"))
                    e = ys[-1] * math.sqrt(1 / max(kk, 1) + 1 / max(ref, 1)) if ref else 0; el.append(e); eh.append(e)   # Poisson, uncorrelated (conservative: the samples share events)
                g = gerr(xs, ys, el, eh, SC[s], mk_, size=1.4); g.Draw("P same")
                if k == 1: leg.append((g, f"{SCTL[s]}, {'ATLAS' if g_ == 0 else 'Ideal'}", "p"))
    bot.cd(); legend(0.03, 0.05, 0.97, 0.95, leg, ncol=2, size=0.2)
    save(c, "S05_merge_multiplicity_sensitivity", """**S05.** Signal events passing the selection for variants of the pixel merging (adjacency a in pixel-index units: a = 0 merges only hits in the same
pixel, which is also what a −50% merge distance gives; a = 1 = production, identical to +50%; a = 2 = +100%) and of the multiplicity threshold T (total hits on the 8 stations:
T = 15 = the paper's rule, production; T = 14 one hit looser; T = 16 all stations with two hits), relative to production, summed over Λ = 1–10 keV (mid band),
√s = 13.6 TeV, the same 10k samples. Filled: Stage 2 · Run 3 · ATLAS; open: Stage 1 · Run 3 · Ideal. Errors: Poisson on both counts, treated as independent (conservative,
since the variants use the same events). The threshold is applied after the fact to the same winning plane (test T13). Source: data/sensitivity.csv (tables/X11_signal_sensitivity.csv).""",
         ["sensitivity.csv"])

# ---------- S06: mass dependence of the A580 signal ratio (2026-11-18): two masses per channel, merge a = 0 / 2 and threshold T = 14 / 16
    MS = {"colored": (1500, 1800), "EW": (600, 800)}
    if all(any(r["sample"] == f"{ch}_{m}gev" for r in SN) for ch in MS for m in MS[ch]):
        V6 = [("0", "15", "a = 0", C("#2a78d6"), 20), ("2", "15", "a = 2", C("#2a78d6"), 21), ("1", "14", "T = 14", C("#e0662e"), 22), ("1", "16", "T = 16", C("#e0662e"), 23)]
        c, hd, top, bot = two("S06")
        header(hd, "SCT 17 #mum / 580 #mum (A580): signal ratio to production (a = 1, T = 15) vs quirk mass, #Lambda = 1-10 keV")
        leg = []
        for k, ch in enumerate(("colored", "EW"), 1):
            m1, m2 = MS[ch]; dm = m2 - m1
            p = top.cd(k); p.SetBottomMargin(0.16); frame(p, m1 - 0.6 * dm, 0.55, m2 + 0.6 * dm, 1.45, "m_{Q} [GeV]", "k / k(a = 1, T = 15)")
            one = ROOT.TLine(m1 - 0.6 * dm, 1, m2 + 0.6 * dm, 1); one.SetLineColor(GRID); one.Draw(); KEEP.append(one)
            text(0.17, 0.86, "colored (3,1)_{2/3}" if ch == "colored" else "EW (1,1)_{1}", 0.045)
            for i, (a, t, lab, col, mk_) in enumerate(V6):
                for g_, (setup, mo) in enumerate((("S2_Run3_ATLAS", 0), ("S1_Run3_Ideal", 4))):
                    rr = {int(r["sample"].split("_")[1][:-3]): r for r in SN if r["sct"] == "A580" and r["setup"] == setup and r["merge_adj"] == a and r["threshold"] == t
                          and r["sample"].startswith(ch + "_")}
                    ms = [m for m in (m1, m2) if m in rr]
                    if not ms: continue
                    xs = [m + (i - 1.5) * 0.05 * dm + (g_ - 0.5) * 0.02 * dm for m in ms]; ys = [fl(rr[m]["ratio_to_reference"]) for m in ms]; e = [fl(rr[m]["ratio_err_paired"]) for m in ms]
                    g = gerr(xs, ys, e, e, col, {20: 24, 21: 25, 22: 26, 23: 32}[mk_] if mo else mk_, size=1.4); g.SetLineStyle(1 if g_ == 0 else 2); g.Draw("PL same")
                    if k == 1: leg.append((g, f"{lab}, {'ATLAS' if g_ == 0 else 'Ideal'}", "pl"))
        bot.cd(); legend(0.03, 0.05, 0.97, 0.95, leg, ncol=4, size=0.2)
        save(c, "S06_merge_ratio_vs_mass", """**S06.** Mass dependence of the A580 signal ratio to production (a = 1, T = 15) for the merge variants a = 0 and a = 2 (blue) and the threshold
variants T = 14 and T = 16 (orange), at two masses per channel near the A580 reach (colored 1500 and 1800 GeV, EW 600 and 800 GeV), summed over Λ = 1–10 keV (mid band),
√s = 13.6 TeV, the same 10k samples. Filled, solid: Stage 2 · Run 3 · ATLAS; open, dashed: Stage 1 · Run 3 · Ideal. Errors: paired, from the events that pass only in the variant
or only in production (√(gained + lost) / k_production). Source: data/sensitivity.csv (tables/X11_signal_sensitivity.csv).""", ["sensitivity.csv"])
print("SIGNAL_FIGS_EXIT=0")
