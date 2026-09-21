# Generator configuration summary — 2026-09-21

## Status: ORIGINAL SETTINGS LOCATED (NOT reconstructed)

This is not a "best-effort reconstructed configuration." A full-filesystem
search (per this task's instruction to search "MadGraph directories,
banner files, LHE and HepMC headers, logs, git history and previous
outputs") located the **actual original MadGraph process directories**
used to generate both benchmark samples, at:

- EW: `/home/rafia/hep_tools/quirk_ew_800gev_4kev/`
- Colored: `/home/rafia/hep_tools/quirk_signal_1800gev_2kev/`

These are outside the `coplanarity_study` git repository (in a separate
tool-installation area) and had never been copied into version control,
which is why an earlier turn's audit (Phase 5 of the prior task) incorrectly
stated "no run_card/banner preserved" — that claim is now corrected: the
files exist on disk, they were simply never git-committed. This task
copies the relevant small files into version control for the first time.

**Authenticity verification performed** (not assumed):
1. Particle codes in the MG5ProcCard (`p p > qe+ qe- @0/@1` for EW,
   `p p > t1 t1~ @0/@1` for colored) match exactly the PDG codes
   (`9000011`/`1000006`) already documented and used in this project's own
   `01_signal_generation/extract_ew_quirk_momenta.py` and
   `extract_quirk_momenta.py` — in fact those scripts' own docstrings
   already reference these exact paths.
2. HepMC final-state event counts (511 EW, 419 colored) match **bit-for-bit**
   the "N_matched" figures used throughout this entire project.
3. Re-extracting quirk-pair pT from these original files reproduces the
   existing authoritative CSVs' `pT_pair` column to **0.0 GeV** max
   absolute difference (511/511 and 419/419 events, see
   `distributions/*_comparison_with_existing.csv`).

## EW benchmark (mQ=800 GeV, Λ=4 keV — Λ is not a MadGraph parameter, see note below)

| Item | Value |
|---|---|
| Process definition | `import model quirk` then `generate p p > qe+ qe- @0` + `add process p p > qe+ qe- j @1` |
| Collider energy | 13 TeV (6500+6500 GeV, LHC Run-2) |
| PDF set | NNPDF2.3LO (`nn23lo1`, LHAPDF ID 230000) |
| Generator version | MadGraph5_aMC@NLO 3.7.3 |
| Shower/matching version | Pythia8 (via MadGraph's internal Pythia8 interface) |
| Renormalization/factorization scale | dynamical (`dynamical_scale_choice=-1`), `scalefact=1.0`, `alpsfact=1.0` |
| Generator-level cuts | `ptj=20 GeV`, `etaj=5.0`, `maxjetflavor=4` |
| Matching/merging method | MLM (`ickkw=1`), MadGraph `xqcut=30 GeV`, Pythia8-side `JetMatching:qCut=45 GeV` (standard 1.5×xqcut convention), `JetMatching:nJetMax=1` |
| ISR requirement | none at generation level — the paper's own MET/pT_pair>200GeV trigger cut is applied downstream on the truth-level 4-momenta, not at generation (confirmed: `docs/CUTS_AND_PIPELINE.md` line 45, re-verified this task) |
| Random seed | `iseed=21` |
| Quirk model parameters | mass `mqe=800.0 GeV` (BLOCK MASS 9000011); charge -1 (BLOCK QNUMBERS 9000011: "1 -3" = 3×charge); color singlet (QNUMBERS "3 1") |
| Events requested/generated | 1000 (LHE), showered+matched → 511 |

## Colored benchmark (mQ=1.8 TeV, Λ=2 keV)

| Item | Value |
|---|---|
| Process definition | `import model quirk` then `generate p p > t1 t1~ @0` + `add process p p > t1 t1~ j @1` |
| Collider energy | 13 TeV (6500+6500 GeV) |
| PDF set | NNPDF2.3LO (`nn23lo1`, LHAPDF ID 230000) |
| Generator version | MadGraph5_aMC@NLO 3.7.3 |
| Renormalization/factorization scale | dynamical (`dynamical_scale_choice=-1`), `scalefact=1.0` |
| Generator-level cuts | `ptj=20 GeV`, `etaj=5.0`, `maxjetflavor=4` |
| Matching/merging method | MLM (`ickkw=1`), `xqcut=30 GeV`, Pythia8 `JetMatching:qCut=45 GeV`, `nJetMax=1` |
| ISR requirement | none at generation level (same as EW) |
| Random seed | `iseed=21` |
| Quirk model parameters | mass `mqc=1800.0 GeV` (BLOCK MASS 1000006); charge +2/3 (QNUMBERS "1 2"); color triplet (QNUMBERS "3 3") |
| R-hadronization | Pythia8 `RHadrons:allow=on`, `RHadrons:idStop=1000006` slot — final-state PDG codes are large composite R-hadron codes (≥1000600), not the base 1000006 id (see `extract_pilot_data.py`'s `require_pdg=False` handling) |
| Events requested/generated | 1000 (LHE), showered+matched → 419 |

## What Λ (string tension) is NOT

Λ does not appear anywhere in either param_card/run_card, by design: it is
not a MadGraph production parameter at all. MadGraph only needs the quirk
MASS and gauge quantum numbers (charge, color representation) to compute
the hard-scattering cross-section and generate 4-momenta. Λ governs only
the CLASSICAL POST-GENERATION trajectory (Eq.3, the confining-string
equation of motion), applied entirely downstream by this project's own
`quirk_trajectory.py` — never a generator-level input. This is consistent
with the paper's own structure (Sec. II defines Λ only in the context of
the string action, Sec. III A describes it entering only "the resulting
four-momenta of the quirks are then evolved").

## Paper's own generation-section statement (re-verified this task, page 4)

*"We generate signal samples of vector-like fermions with up to 1 jet
using MadGraph5_aMC@NLO [24,25], which is subsequently matched using
Pythia8 [21,26]. For electroweak production the quirks are taken to have
unit charge and are produced in Drell-Yan, while for colored production
only QCD contributions are included."*

The paper does NOT specify: PDF set, matching scale, renormalization/
factorization scale choice, or random seed. All of the recovered settings
above are this project's OWN prior choices (now fully documented and
preserved), not settings independently confirmable against the paper
text — this remains consistent with the Phase 5 EW-discrepancy audit's
conclusion that an exact apples-to-apples comparison against the paper's
own (unpublished) generator settings is structurally impossible.
