#!/usr/bin/env python3
"""Assembles R_report_2026-10-21_partAB.py (2026-10-21) from the template (new Part A / Part B / Table II structure) and the unchanged blocks of
R_report_2026-10-21_v2.py (Fig. 2, annihilation, repeated crossings, Fig. 3, Fig. 7, LO samples). Only headings and the units of the L tables (now 1e8 hbar)
are changed in those blocks; every replacement must match exactly once."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/R_report_2026-10-21_v2.py").read()
tpl = open(sys.argv[1]).read()
def cut(a, b): i, j = src.index(a), src.index(b); assert i < j; return src[i:j]
def rep(block, pairs):
    for a, b in pairs:
        assert block.count(a) == 1, (a[:80], block.count(a)); block = block.replace(a, b)
    return block
HEAD = rep(cut("import os, sys, json, subprocess", 'S = [P("Reproduction of Table I'),
           [('OUT = f"{R.L_}/TABLE_I_REPRODUCTION_REPORT_2026-10-21_v2.pdf"', 'OUT = f"{R.L_}/TABLE_I_REPRODUCTION_REPORT_2026-10-21_partAB.pdf"')])
FIG2 = rep(cut("# 3 Figure 2", "# 4 annihilation"), [
    ('P("3. Figure 2 and Appendix A of arXiv:2002.07503", "h2")', 'P("A3. Figure 2: angular momentum L of the quirk pair (with Appendix A of arXiv:2002.07503)", "h2")'),
    ("units 10¹² ħ)", "units 10⁸ ħ)"),
    ('*[f"{r_[0]:+.2f}" for r_ in tq]', '*[f"{r_[0]*1e4:+.0f}" for r_ in tq]'),
    ('*[f"{r_[1]:+.2f}" for r_ in tq]', '*[f"{r_[1]*1e4:+.0f}" for r_ in tq]'),
    ('*[f"{r_[2]:+.2f}" for r_ in tq]', '*[f"{r_[2]*1e4:+.0f}" for r_ in tq]'),
    ('*[f"<b>{x:+.2f}</b>" for x in S2["paper"]["dL_half"]]', '*[f"<b>{x*1e4:+.0f}</b>" for x in S2["paper"]["dL_half"]]'),
    ("adds or removes the same amount (±0.64), so", "adds or removes the same amount (±0.64×10¹² ħ = ±6400×10⁸ ħ), so"),
    ("In the paper the halves are unequal (+0.65, −0.84, +0.71, −0.80), so", "In the paper the halves are unequal (+0.65, −0.84, +0.71, −0.80, in 10¹² ħ), so"),
    ('g = [H("meeting", "", "r (cm)", "|L| (10¹² ħ)", "signed L", "change of L in this half", "|L| = 0 at r (cm)", "b = |L| / p* (cm)")]; ex = []',
     'g = [H("meeting", "", "r (cm)", "|L| (10⁸ ħ)", "signed L (10⁸ ħ)", "change of L in this half (10⁸ ħ)", "|L| = 0 at r (cm)", "b = |L| / p* (cm)")]; ex = []\n'
     '_HBC = 1.973e-14; _PS = {"paper": 1204.1, "constructed": float(iv0.p_star_GeV), "key 8": float(iv1.p_star_GeV)}   # hbar*c (GeV cm); p* (GeV) used for b\n'
     'L8 = lambda r_, ev: r_.b_cm * _PS[ev] / _HBC / 1e8                          # |L| in 1e8 hbar from b = |L| / p* (keeps the residual at the even meetings)\n'
     'F8 = lambda v: f"{v:.0f}" if v >= 100 else f"{v:.2g}"\n'
     'LMEET = []'),
    ('f"{r_.L_abs_at_meeting:.2f}", f"{r_.L_signed_at_meeting:+.2f}",\n                   f\'<font color="{RED}"><b>{r_.dL_this_half:+.2f}</b></font>\'',
     'F8(L8(r_, ev)), ((("+" if r_.L_signed_at_meeting > 0 else "−") + F8(L8(r_, ev))) if r_.L_signed_at_meeting != 0 else "±" + F8(L8(r_, ev))),\n'
     '                   f\'<font color="{RED}"><b>{r_.dL_this_half*1e4:+.0f}</b></font>\''),
    ('        if ev == "paper": ex.append(("BACKGROUND", (0, i_), (-1, i_), KEYB))',
     '        LMEET.append(dict(event=ev, meeting=m_, r_meeting_cm=r_.r_meeting_cm, L_abs_1e8hbar=round(L8(r_, ev), 4), L_sign=int(np.sign(r_.L_signed_at_meeting)),\n'
     '                          dL_this_half_1e8hbar=round(r_.dL_this_half * 1e4, 1), b_cm=r_.b_cm, p_star_GeV=_PS[ev]))\n'
     '        if ev == "paper": ex.append(("BACKGROUND", (0, i_), (-1, i_), KEYB))'),
    ("† At the even meetings our left-over |L| (~10<super>8</super> ħ) is the limit", "† At the even meetings our left-over |L| (1–5 in units of 10⁸ ħ) is the limit"),
    ("The paper's first-half change is +0.64 in this table (from its curve's first point, 0.008) and +0.65 in the half-oscillation table above (from zero)",
     "The paper's first-half change is +6400 in this table (from its curve's first point, 80) and +6452 in the half-oscillation table above (from zero)"),
    ("The first meeting agrees (0.65 vs 0.64).", "The first meeting agrees (0.65 vs 0.64 ×10¹² ħ)."),
    ("(±0.64; ±0.86 for event 8)", "(±0.64×10¹² ħ; ±0.86×10¹² ħ for event 8)"),
    ("its small ones rise (0.20 → 0.29).", "its small ones rise (0.20 → 0.29; all in 10¹² ħ)."),
    ('g = [H("RK4 steps per oscillation", "|L| at meeting 2 (ħ)", "|L| at meeting 4 (ħ)", "|L| at meetings 1 and 3 (ħ)")]',
     'g = [H("RK4 steps per oscillation", "|L| at meeting 2 (10⁸ ħ)", "|L| at meeting 4 (10⁸ ħ)", "|L| at meetings 1 and 3 (10⁸ ħ)")]'),
    ('for n_, l2, l4 in LR: g.append(C(f"{n_:,}", sci(abs(l2)), sci(abs(l4)), "6.43×10<super>11</super>"))',
     'for n_, l2, l4 in LR: g.append(C(f"{n_:,}", f"{abs(l2)/1e8:.3g}", f"{abs(l4)/1e8:.3g}", "6430"))\n'
     '_LD = f"{R.L_}/L_VALUES_CSV_2026-10-21"; os.makedirs(_LD, exist_ok=True)   # the L tables of the report, in 1e8 hbar\n'
     'pd.DataFrame(LMEET).to_csv(f"{_LD}/L_meetings_1e8hbar.csv", index=False)\n'
     'pd.DataFrame([dict(half_oscillation=i + 1, total_1e8hbar=round(r_[0] * 1e4, 1), magnetic_1e8hbar=round(r_[1] * 1e4, 1), string_1e8hbar=round(r_[2] * 1e4, 1),\n'
     '                   paper_1e8hbar=round(float(S2["paper"]["dL_half"][i]) * 1e4, 1)) for i, r_ in enumerate(tq)]).to_csv(f"{_LD}/L_change_per_half_oscillation_1e8hbar.csv", index=False)\n'
     'pd.DataFrame([dict(rk4_steps_per_oscillation=n_, L_meeting2_1e8hbar=abs(l2) / 1e8, L_meeting2_signed_1e8hbar=l2 / 1e8, L_meeting4_1e8hbar=abs(l4) / 1e8,\n'
     '                   L_meeting4_signed_1e8hbar=l4 / 1e8, L_meetings_1_3_1e8hbar=6430.0) for n_, l2, l4 in LR]).to_csv(f"{_LD}/L_residual_vs_step_size_1e8hbar.csv", index=False)'),
    ('P("3.1 Is L exactly zero? Fig. 2 on a log scale", "h3")', 'P("A3.1 Is L exactly zero? Fig. 2 on a log scale", "h3")')])
ANNI = rep(cut("# 4 annihilation", "# 5 repeated crossings"), [
    ('S += [P("4. Does L = 0 mean the quirks annihilate?", "h2"),', 'S += [P("B5. Annihilation: does L = 0 mean the quirks annihilate?", "h2"),\n      P("Why tested: our |L| returns to zero at every second meeting (Section A3), so the quirks might annihilate; the paper assumes they do not.", "b"),'),
    ('P("4.1 Classical L ≈ 0 is not a collision", "h3")', 'P("B5.1 Classical L ≈ 0 is not a collision", "h3")'),
    ('g = [H("time steps per oscillation", "|L| at meeting 2 (ħ)", "|L| at meeting 4 (ħ)", "b = |L| / p (cm)", "b / (1/m<sub>Q</sub>)")]',
     'g = [H("time steps per oscillation", "|L| at meeting 2 (10⁸ ħ)", "|L| at meeting 4 (10⁸ ħ)", "b = |L| / p (cm)", "b / (1/m<sub>Q</sub>)")]'),
    ('g.append(C(f"{n_:,}", sci(abs(l2)), sci(abs(l4)),', 'g.append(C(f"{n_:,}", f"{abs(l2)/1e8:.3g}", f"{abs(l4)/1e8:.3g}",'),
    ('P("4.2 Even if L returns exactly to its production value, annihilation is not certain", "h3")', 'P("B5.2 Even if L returns exactly to its production value, annihilation is not certain", "h3")'),
    ("Table I assumes no annihilation.", "Part A, like the paper, assumes no annihilation.")])
REPEAT = rep(cut("# 5 repeated crossings", "# 6 Figures 3-5"), [('P("5. Quirks crossing the same layer more than once", "h2")', 'P("A10. Quirks crossing the same layer more than once", "h2")'),
                                                               ("Table I above uses the first crossing only.", "Part A uses the first crossing only, as the paper implies.")])
FIG3 = rep(cut("# 6 Figures 3-5", 'S += [P("Figure 4: hits of one signal event", "h3")]'),
           [('S += [P("6. Figures 3, 4, 5", "h2"), P("Figure 3: turning of the quirks\' plane", "h3"),', 'S += [P("A4. Figure 3: turning of the quirks\' plane", "h2"),')])
FIG7 = rep(cut("# 9 Figure 7", "# 10 open + refs"), [('P("9. Figure 7: dE/dx and βγ of the pixel hits (Appendix A)", "h2")', 'P("A9. Figure 7: dE/dx and βγ of the pixel hits (paper\'s Appendix A)", "h2")'),
                                                    ('P("9.1 Test: which dE/dx definition does the paper use?", "h3")', 'P("A9.1 Test: which dE/dx definition does the paper use?", "h3")')])
LO = rep(cut("lt, lt2, lc = LT[", "# 3 Figure 2"), [
    ('lt, lt2, lc = LT[', 'S += [P("B2. LO-ratio trigger (EW)", "h2"), P(f"Why tested: our EW ε<sub>trig</sub> ({e[\'trig\']/e[\'matched\']:.3f}, matched count) is far above the paper\'s 0.10; arXiv:1911.02223 obtains about 0.1 '
                          'as a leading-order cross-section ratio. Two leading-order samples were made for the EW benchmark; everything else as in Part A but without SCT z smearing.", "b")]\nlt, lt2, lc = LT['),
    ("all other cells use the 2σ₀ rule of Section 1.", "all other cells use the 2σ₀ rule of the Formulas section."),
    ('({ETR["k1"]/ETR["n1"]:.2f}) is far above', '({ETR["k1"]/ETR["n1"]:.3f}) is far above'),
    ("not to our matched sample ({ETR['k1']/ETR['n1']:.2f})", "not to our matched sample ({ETR['k1']/ETR['n1']:.3f})"),
    ("[P(f\"{e['trig']}/{e['matched']} = {es(e['trig'], e['matched'])}\", \"c\"), dt]", "[P(f\"{e['trig']}/{e['matched']} = {es(e['trig'], e['matched'], 3)}\", \"c\"), dt]")])
out = tpl
for k, v in (("#<<HEAD>>", HEAD), ("#<<FIG2>>", FIG2), ("#<<FIG3>>", FIG3), ("#<<FIG7>>", FIG7), ("#<<REPEAT>>", REPEAT), ("#<<ANNI>>", ANNI)):   # LO-ratio block (B2) removed on 2026-10-22
    assert out.count(k) == 1, k; out = out.replace(k, v)
open(f"{HERE}/R_report_2026-10-21_partAB.py", "w").write(out); print("wrote R_report_2026-10-21_partAB.py", len(out.splitlines()), "lines")
