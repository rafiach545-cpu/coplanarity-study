# Pre-registered trigger combination test (written 2026-10-04, BEFORE any combination was generated)

**Purpose.** Answer the review point that one-at-a-time variations cannot show that EW ε_trig = 0.10 is unreachable. Settings that each lowered EW ε_trig in the one-at-a-time screen are combined. Nothing outside the existing screen table is introduced.

**Baseline:** B0 = frozen 2000-event configuration (MG5 3.7.3, nn23lo1, xqcut 30, scalefact 1, Pythia 8.317 MLM qCut 45, nJetMax 1).

**Single-variation results used to choose the combinations** (EW / colored ε_trig): G2 xqcut60 0.140 / 0.196; G3 cteq6l1 0.151 / 0.189; G6 scalefact2 0.149 / 0.219; S4 showerKt 0.148 / 0.203; S5 prodScalesOff 0.148 / 0.226; D2 0-jet no matching 0.130 / 0.200.

| ID | Settings | Level | Paper status |
|---|---|---|---|
| C1 | G2 + G3 + G6: xqcut = 60 (qCut 90), PDF cteq6l1, scalefact = 2.0 | ME + shower | within "up to 1 jet, MLM"; all settings undocumented |
| C2 | C1 + S5 (setProductionScalesFromLHEF = off) | shower on C1 LHE | as C1 |
| C3 | C1 + S4 (doShowerKt = on) | shower on C1 LHE | as C1 |
| C4 | C1 + S4 + S5 | shower on C1 LHE | as C1 |
| C5 | D2 + G3 + G6: 0 jets, no matching, cteq6l1, scalefact = 2.0 | ME + shower | **contradicts the paper** ("up to 1 jet ... matched"): diagnostic only |
| C6 | C5 + S5 | shower on C5 LHE | diagnostic only |

**Rules (fixed now):**
- 2000 LHE events per benchmark per ME-level combination. Seeds: C1 EW 9301 / COL 9311; C5 EW 9302 / COL 9312.
- Trigger = final-state pair pT > 200 GeV over matched events (as in the screen).
- **Pass criterion:** the paper value inside the Wilson 95% interval for EW (0.10) **and** colored (0.24) at the same time.
- A combination that passes gets an independent new-seed confirmation before any statement. No result is adopted as the analysis configuration.
- No further combination is added after seeing results.
