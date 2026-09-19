# Converted-photon + pile-up overlay: paper-to-code checklist (v1)

Re-derived from paper.txt (arXiv:1708.02243v2) Sec II, IIIA, IIIB, IIIC,
IIID, IV, Fig.5/Fig.6 captions, Table I — text already directly quoted and
verified multiple times earlier in this session; re-confirmed here, not
re-fetched from memory.

**Direct confirmation of the overlay requirement** (paper.txt, Sec IIID):
*"The e+e− pair is then passed through the same detector simulation as
described for the pile-up background. We subsequently overlay pile-up hits
and pass the resulting set of hits through our reconstruction algorithm."*

| # | Requirement | Label | Code |
|---|---|---|---|
| 1 | Z+γ+j generation, Z→νν, MET>200GeV | DIRECT PAPER REQUIREMENT | `extract_zgamma_photons.py` |
| 2 | photon pT>0.5GeV | DIRECT PAPER REQUIREMENT | `extract_zgamma_photons.py` |
| 3 | ~1pb fiducial σ → ~10fb after conversion probability | DIRECT PAPER REQUIREMENT | `convert_and_analyze.py` constants |
| 4 | conversion probability from PDG figs 33.16/33.17 | CITED-REFERENCE REQUIREMENT | `CONVERSION_PROBABILITY=0.01`, applied as weight not stochastic filter — DOCUMENTED PROJECT ASSUMPTION on the exact value |
| 5 | equal e+/e− energy sharing (paper's conservative choice) | DIRECT PAPER REQUIREMENT | exact 50/50 |
| 6 | e+e− through same detector sim as pile-up | DIRECT PAPER REQUIREMENT | `simulate_quirk_hits`, Λ=0, same 8-layer barrel model |
| 7 | **overlay pile-up hits, then reconstruct** | **DIRECT PAPER REQUIREMENT** | **NEW in this task**: `overlay_and_merge(raw_conv_hits, raw_pileup_hits)`, ONE merge |
| 8 | pile-up: ⟨μ⟩=50, tracking efficiency from ATL-PHYS-PUB-2015-051 | DIRECT PAPER REQUIREMENT | `sample_pileup_hits_suppressed`, LOOSE_BASELINE |
| 9 | 125,000-event minbias pool | DIRECT PAPER REQUIREMENT (value) | PROJECT SIMPLIFICATION: 20,000-event pool, with replacement (documented, not a feasibility finding) |
| 10 | ancestry-aware Bernoulli track suppression mechanism | not explicitly specified by paper or ref[33] | DOCUMENTED PROJECT ASSUMPTION (RUN_LOG/track_suppression.py docstring) |
| 11 | Sec IIIC seeding/iterative-fit/Event Selection | DIRECT PAPER REQUIREMENT | `coplanarity_fit.py`, unchanged |
| 12 | Sec IV hit-multiplicity/Δw/Δs cuts | DIRECT PAPER REQUIREMENT | `coplanarity_fit.py`, unchanged |
| 13 | Fig.5 pile-up curve: 1-hit-per-layer population reweighted by hit-mult efficiency | DIRECT PAPER REQUIREMENT | denominator-population interpretation remains UNRESOLVED (documented ambiguity, unchanged from the pile-up-only freeze) |
| 14 | Fig.6: 95% exclusion at 300fb⁻¹, "negligible irreducible backgrounds" assumed | DIRECT PAPER REQUIREMENT | requires signal production cross-sections (UNRESOLVED — not available in this project) |

**Merge-order correctness** (re-audit history, commit 3213219): raw hard
hits + raw pile-up hits must be merged in exactly ONE pass
(`overlay_and_merge`), never merged separately then re-merged — re-merging
an already-merged multi-source cluster loses provenance
(`quirk_index`→`None`). This overlay driver reuses that exact validated
function unchanged.
