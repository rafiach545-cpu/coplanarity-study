#!/usr/bin/env python3
"""F15 (2026-11-09): production channel (gg, qqbar, qg) and pT of the quirk pair per mass point, 13 and 13.6 TeV. Separate from make_figures_root.py so that
F01-F13 are not redrawn; style and helpers taken from it unchanged. Data: data/production_channels.csv, data/pair_pt.csv (S2_13). Run with root-env python."""
import os
HERE = os.path.dirname(os.path.abspath(__file__)); src = open(f"{HERE}/make_figures_root.py").read(); exec(src[:src.index("# ---------- contour figures")])
PC, PT = read("production_channels.csv"), read("pair_pt.csv")
PR = {"gg": (C("#6250d6"), 20, 24, "gg"), "qqbar": (C("#1baf7a"), 21, 25, "q#bar{q}"), "qg": (C("#e87ba4"), 22, 26, "qg"), "all": (INK, 33, 27, "all")}  # colour, filled (13.6), open (13)
EN = (("13", -1, "13 TeV (open)"), ("13.6", 1, "13.6 TeV (filled)"))
c, hd, top, bot = layout("F15", 1600, 1450); header(hd, "Production channel and p_{T}(Q#bar{Q}) per mass point (matched events of the analysis)"); LE = {}
def pts(rows, key, lo=None, hi=None, prod="all", E="13.6", dx=0):
    col, mf, mo, _ = PR[prod]; xs = [fl(r["mass_gev"]) + dx for r in rows]; v = [fl(r[key]) for r in rows]
    if lo and not hi: el = eh = [fl(r[lo]) for r in rows]                       # symmetric error column
    else: el = [a - fl(r[lo]) for a, r in zip(v, rows)] if lo else [0] * len(v); eh = [fl(r[hi]) - a for a, r in zip(v, rows)] if hi else [0] * len(v)
    g = gerr(xs, v, el, eh, col, mf if E == "13.6" else mo, size=1.3); g.Draw("PL" if E == "13.6" else "P"); return g
for j, ch in enumerate(("colored", "EW")):                                         # (a), (b): fraction of matched events per production channel
    p = top.cd(j + 1); p.SetLeftMargin(0.14); frame(p, XR[ch][0] - 100 * (j == 0) - 50 * j, 0, XR[ch][1] + 100 * (j == 0) + 50 * j, 1.0, "m_{Q} [GeV]", "fraction of matched events")
    for prod in ("gg", "qqbar", "qg"):
        for E, s, _ in EN:
            rows = sorted([r for r in PC if r["channel"] == ch and r["sqrt_s_TeV"] in (E, E + ".0")], key=lambda r: fl(r["mass_gev"]))
            if all(fl(r[f"matched_frac_{prod}"]) == 0 for r in rows): continue
            LE[(prod, E)] = pts(rows, f"matched_frac_{prod}", f"matched_frac_{prod}_lo", f"matched_frac_{prod}_hi", prod, E, s * 12 * (1 + (j == 0)))
    text(0.17, 0.86, f"#bf{{{CH[ch].split()[0]}}}", 0.055)
for j, (key, yt, yr) in enumerate((("pt_median", "median p_{T}(Q#bar{Q}) [GeV]", (0, 300)), ("eps_trig", "#varepsilon_{trig} = P(p_{T}(Q#bar{Q}) > 200 GeV)", (0, 0.75)))):   # (c), (d): colored per channel + EW
    p = top.cd(j + 3); p.SetLeftMargin(0.14); frame(p, 0, yr[0], 2550, yr[1], "m_{Q} [GeV]", yt)
    for ch in ("colored", "EW"):
        for prod in (("gg", "qqbar", "qg", "all") if ch == "colored" else ("all",)):
            for E, s, _ in EN:
                rows = sorted([r for r in PT if r["channel"] == ch and r["production"] == prod and r["sqrt_s_TeV"] in (E, E + ".0")], key=lambda r: fl(r["mass_gev"]))
                g = pts(rows, key, *(("pt_median_err", None) if key == "pt_median" else ("eps_trig_lo", "eps_trig_hi")), prod, E, s * 15)
                LE.setdefault((prod, E), g)
                if ch == "EW": g.SetMarkerColor(INK2); g.SetLineColor(INK2); g.SetLineStyle(2); g.SetMarkerStyle(34 if E == "13.6" else 28); LE[("EW", E)] = g
    if key == "eps_trig": text(0.17, 0.86, "colored: per production channel and all;  EW: all (crosses, dashed)", 0.036, 11, INK2)
    else: text(0.17, 0.86, "error: standard error of the median", 0.036, 11, INK2)
bot.cd(); legend(0.02, 0.05, 0.98, 0.95, [(LE[("gg", "13.6")], "gg", "pl"), (LE[("qqbar", "13.6")], "q#bar{q}", "pl"), (LE[("qg", "13.6")], "qg", "pl"),
       (LE[("all", "13.6")], "colored, all", "pl"), (LE[("EW", "13.6")], "EW, all", "pl"), (LE[("gg", "13")], "open: 13 TeV;  filled: 13.6 TeV", "p")], ncol=3, size=0.26)
save(c, "F15_production_and_pair_pt", """**Fig. 15.** Why ε_trig depends on mass differently for colored and EW quirks, from the existing samples (matched events, every mass point; open: 13 TeV,
filled: 13.6 TeV). (a), (b): fraction of events by initial state of the hard process (Pythia8 status-21 partons: gg, qq̄, qg), Wilson 68% errors. (c): median
pT of the quirk pair, the trigger variable. (d): ε_trig = fraction with pT(QQ̄) > 200 GeV. Colored: gg and qg events are much harder than qq̄ events; the qq̄
share grows from ≈ 30% at 600 GeV to ≈ 80% at 2400 GeV, so the overall median and ε_trig stay flat although each channel rises with mass. EW (qq̄ and qg
only) rises with mass. Source: S2_production_channels.csv, S2_pair_pt.csv via data/.""", ["production_channels.csv", "pair_pt.csv"])
print("F15_EXIT=0")
