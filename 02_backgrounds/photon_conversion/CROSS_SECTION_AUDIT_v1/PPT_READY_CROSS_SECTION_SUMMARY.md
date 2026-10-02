# Converted-Photon Background: Cross-Section Discrepancy — PPT Summary
(Final for this session — verdict: UNRESOLVED. See FINAL_CROSS_SECTION_AUDIT.md for full detail.)

## The gap
| | Paper (Sec III D) | Project |
|---|---|---|
| Process | p p → Z(νν) γ j | identical |
| Cuts | MET>200 GeV, pT(γ)>0.5 GeV | identical (confirmed via new pilot run) |
| Fiducial cross section | **~1 pb** | **0.2300 ± 0.0005 pb** (weighted mean, 8 consistent runs) |
| Gap | factor ~4.3 | **unexplained** |

## What was ruled out (each tested with a dedicated new run)
| Factor tested | Result | Effect |
|---|---|---|
| Photon-pT cut applied at generation vs post-shower | 0.2307 pb | ~0% |
| PDF set (nn23lo1 → cteq6l1) | 0.2241 pb | −2.6% |
| Scale ×0.5 | 0.2592 pb | +12.7% |
| Scale ×2 | 0.1858 pb | −19.2% |
| Jet-pT cut 20→40 GeV | 0.2141 pb | −6.9% |
| Run-to-run MC grid variation | resolved: 8/9 runs consistent (weighted mean 0.2300 pb); the 9th (0.3057 pb) is a demonstrated non-convergence outlier | n/a |

None of these come close to the factor ~4.3 needed.

## Major technical result: NLO compilation fixed
A pre-existing NLO attempt had failed silently because MG5's own FastJet
dependency never built. Root-caused (conda-GCC/libtool shared-library
bug) and **fixed** via a disposable static FastJet build plus one missing
library-path fix — both confined to disposable directories, no change to
the authoritative install. **The NLO compile now succeeds cleanly.**

However, the resulting NLO test (1175 pb) used a process where the Z
boson is left undecayed — no neutrino branching ratio, no MET cut
possible — so it is a different observable, not a usable K-factor. A
genuine paper-comparable NLO number (Z→νν decay + MET cut on the now-
working NLO setup) is the clearest remaining next step, not yet done.

## Bottom line
**The ~1 pb vs ~0.23 pb discrepancy remains unexplained.** Six concrete
candidate causes were tested and excluded or shown insufficient. The NLO
toolchain blocker was fixed, but the specific comparable NLO number is
still outstanding. No tuning was applied at any point.
