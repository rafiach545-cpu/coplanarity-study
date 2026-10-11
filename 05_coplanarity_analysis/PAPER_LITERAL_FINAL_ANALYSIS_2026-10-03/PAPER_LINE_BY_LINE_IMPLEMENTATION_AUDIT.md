# Paper Line-by-Line Implementation Audit (Phase 1)

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

**Paper:** S. Knapen, H. K. Lou, M. Papucci, J. Setford, "Tracking down Quirks at the Large Hadron Collider", arXiv:1708.02243v2.
- **v2 source:** `quirks_prd_v2.tex`, identical to `https://arxiv.org/src/1708.02243`.
- **v1 source:** `quirks_arxiv.tex`.
- Both are archived with SHA-256 in `EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/paper_source/`.
- The arXiv HTML rendering does not exist for this 2017 paper; the LaTeX source and the rendered PDF were used.

## Coverage

`tables/PAPER_REQUIREMENTS_LINE_BY_LINE.csv` (identical copy: `tables/paper_requirement_matrix.csv`) has **347 rows**. Columns: source, TeX line, section, exact text, requirement, reference, implementation consequence, current project value, status, ambiguity, action.
- **275 body sentences:** every non-comment sentence of the v2 body, from the Introduction through Appendix A, including equations, figure captions, footnotes and Table I. Coverage check: 44,874 characters captured versus 42,961 in the body (whitespace normalisation).
- **65 TeX comment lines:** listed with status COMMENT; they are not paper text. They include `%MG5 v2.3.3`, `%Pythia 8.212` and the draft Table I with DY ε_trig = 0.03 and QCD 0.21.
- **7 v1 → v2 changes:** abstract wording, "Drell-Yann" → "Drell-Yan", Fig. 5 caption, Sec. III C summary list. **None changes Table I or an implementation-relevant statement.**
- Statuses used: PAPER-STATED (requirements), NARRATIVE (motivation or physics discussion with no direct implementation consequence; still listed), COMMENT.

## Implementation-relevant requirements (summary)

| Paper statement (section) | Implementation | Status |
|---|---|---|
| Vector-like quirks in (1,1)₁ and (3,1)₂/₃ (II) | EW UFO: correct spin/charge/colour, **but SM-electron chiral Z coupling** (implementation error, trigger-neutral, σ −24%); colored UFO correct | partly violated (EW Z coupling) |
| Both quirk-hadrons with non-zero charge (II) | colored: both R-hadrons q ≠ 0, applied after the trigger | implemented |
| Eqs. 2–4: Nambu–Goto, straight string, Λ² = tension (II) | project integrator, validated against Eq. 4; amplitudes reproduce Eq. 1 and paper Fig. 2 scale | implemented |
| "up to 1 jet … matched using Pythia8"; DY for EW, QCD-only for colored (III A) | 0+1-jet MLM; matching parameters, PDF, scale, √s, tune and versions **not stated** | UNDOCUMENTED settings (frozen values) |
| Uniform 2 T along z; numerical EOM (III A) | yes | implemented |
| Simplified ATLAS ID, parameters from [27]; pixel-centre hits; SCT 2 × intrinsic accuracy; neighbouring-pixel merging; 45 mm beam spot; barrel only (III A) | literal: finite barrel from [27], SCT 34/1160 µm, merging, common z shift | implemented (see detector report) |
| Trigger: pT of the QQ̄ CM system > 200 GeV (III B) | final-state pair pT > 200, matched denominator | implemented |
| Eqs. 10–11; Sec. III C algorithm (seeds L8/L7, Δφ < 0.1, Δz < 2 cm, seed Δs < 0.05 / Δw < 1, windows, ×3 growth, Δw < 1, smallest Δs) | `coplanarity_fit.py`, verified line by line and by an instrumented re-implementation (identical candidates) | implemented |
| Signal region: plane; 7 layers × 2 hits + 1 × ≥ 1; Δw < 1 cm; Δs < 0.01 cm; "reconstruction efficiency for these cuts" (IV) | ε_reco = full SR / (trigger ∧ fiducial); plane-only kept as diagnostic | implemented |
| ε_fid: each quirk crosses each layer at least once, in triggered events, with the 25 ns cut (IV) | 16 first crossings, max t < 25 ns | implemented |
| Eq. 12, ε = ε_trig ε_fid ε_reco (IV) | factorisation used | implemented |
| Pile-up: ⟨μ⟩ = 50, 45 mm, 125k min-bias, simplified detector of [1612.00850] with energy loss/brems/endcaps, tracking-efficiency removal (III D) | μ = 50, 45 mm per vertex, 20k pool, helix in the 8-layer barrel without energy loss/brems/endcaps, ATLAS tracking efficiency | partly (pool size and detector simplification documented) |
| ~1e-3 of background events with a plane with ≥ 1 hit in 4/8 layers; 6e-5 with 8/8 (IV) | reported (Phase 8) | compared |
| Relaxed 1-hit-per-layer background control (IV) | 8/8 relaxed rate reported | compared |
| Conversion background: Z(νν)γj, MET > 200, pT(γ) > 0.5 GeV, σ ~ 1 pb → ~10 fb in the beam pipe, equal energy sharing, same detector simulation as pile-up, overlay with pile-up (III D) | project σ = 0.231 pb (kept separate, unresolved); 1% probability; literal reprocessing uses the pile-up helix detector and the primary-vertex fit origin | implemented / σ unresolved |
| Fig. 6 contours (IV) | **out of scope (Figure 6 paused)** | not done by instruction |
| App. A dE/dx | not used by the analysis | n/a |

## Cited sources read

| Source | Status |
|---|---|
| [27] ATL-PHYS-PUB-2009-002 | **Read** via its CSC-book publication (arXiv:0901.0512 pp. 40–43); CDS bot-blocked |
| arXiv:1612.00850 App. A (pile-up detector) | **Read** (LaTeX source) |
| ATL-PHYS-PUB-2015-051 (tracking efficiency) | **Read**: local copy and digitisation in `docs/reference/atl_phys_pub_2015_051/` |
| PDG 2016 "Passage of particles through matter", Figs. 33.16/33.17 | **Read** (pdg.lbl.gov); curves need the beam-pipe material/thickness, which the paper does not state → 1% kept as DERIVED from the paper's own 1 pb → 10 fb |
| ATL-DAQ-PUB-2016-001 (trigger thresholds) | **BLOCKED** (CDS bot check); not needed (the paper states the 200 GeV value) |
| MG5_aMC (arXiv:1405.0301), Pythia8 (arXiv:1410.3012), Buchkremer:2013bha | software references; contain no paper-specific settings |
| Farina:2017cts (HSCP/monojet limits), Aad:2014sca (muon trigger) | context for Figure 6 / motivation only |
