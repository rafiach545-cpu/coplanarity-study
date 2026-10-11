# Part B — pre-registered trigger-only screen (written before any screen result)

**Baseline B0** (= the frozen 2000-event configuration, both benchmarks):
- MG5 3.7.3, `p p > X X~ @0` + `j @1`, 4-flavour p/j
- nn23lo1, dynamical_scale_choice −1, ickkw 1, xqcut 30, ptj 20, 13 TeV
- Pythia 8.317 (Monash): MLM `JetMatchingMadgraph` scheme 1, qCut 45, nJetMax 1, setMad off, doShowerKt off, setProductionScalesFromLHEF on
- Colored only: `RHadrons:allow on`, `allowDecay off`

**Trigger:** final-state pair pT > 200 GeV (strict), denominator = matched events. Colored is counted before any R-hadron charge requirement; that convention reproduced the paper's 0.24.

**Driver:** `quirk_mlm_shower_v2.cc`. It reproduces the frozen showers event by event: EW 1045/186 and colored 873/207.

**Acceptance:** the paper value must lie inside the Wilson 95% interval for EW (0.10) **and** colored (0.24) **simultaneously**. A configuration that matches EW but breaks colored is rejected.

## One-setting-at-a-time screen

| ID | Change vs B0 | Level | Paper status |
|---|---|---|---|
| S1 | JetMatching:qCut = 30 (= xqcut) | shower | undocumented |
| S2 | JetMatching:qCut = 60 | shower | undocumented |
| S3 | JetMatching:qCut = 90 | shower | undocumented |
| S4 | JetMatching:doShowerKt = on | shower | undocumented |
| S5 | Beams:setProductionScalesFromLHEF = off (Pythia default) | shower | undocumented |
| S6 | Tune:pp = 5 (4C; Pythia 8.1-era default) | shower | undocumented |
| S7 | ATLAS A14 tune (NNPDF2.3LO) | shower | undocumented |
| S8 | SpaceShower:pTmaxMatch = 1 (ISR limited by the LHE scale) | shower | undocumented |
| S9 | SpaceShower:pTmaxMatch = 2 (power shower) | shower | undocumented |
| G0 | B0 regenerated with a new seed | ME | control |
| G1 | xqcut = 15 (qCut = 1.5×xqcut = 22.5, MG recommendation) | ME | undocumented |
| G2 | xqcut = 60 (qCut = 90) | ME | undocumented |
| G3 | PDF cteq6l1 (MG built-in; common LO choice of that era) | ME | undocumented |
| G4 | dynamical_scale_choice = 3 (HT/2) | ME | undocumented |
| G5 | scalefact = 0.5 | ME | undocumented |
| G6 | scalefact = 2.0 | ME | undocumented |
| G7 | √s = 14 TeV | ME | undocumented |
| D1 | up to 2 jets (0+1+2, nJetMax 2) | ME | **contradicts paper** ("up to 1 jet"): diagnostic only |
| D2 | 0 jets, no matching (ickkw 0, shower only) | ME | **contradicts paper**: diagnostic only |

Additional rules:
- Pilot size: 2000 LHE events per benchmark per ME-level setting.
- Shower-level settings reuse the frozen 2000-event LHE files (read-only copies).
- A configuration that passes both benchmarks gets an independent confirmation sample with a new seed.
- No setting outside this table will be introduced to chase 0.10.
