# Paper Cross-Section Definition — What Is Being Compared

Scope: determine exactly what the paper's quoted "~1 pb" fiducial cross
section for the converted-photon Z(νν)+γ+j background refers to, and what
the project's existing generation actually computed, before any new runs
are launched. Every statement below is classified as **DIRECT PAPER
EVIDENCE**, **DIRECT CODE EVIDENCE**, **INFERENCE**, or **UNAVAILABLE**.

## 1. The exact paper passage

arXiv:1708.02243v2, Sec. III D ("Backgrounds"), page 6→7 of the extracted
text (`paper.txt` lines 682–702):

> "A second potential background arises from isolated photon conversions
> in the beam pipe. These conversions give rise to a fairly collimated
> e+e− pair, which results in a nearby pair of hits in each layer of the
> tracker. For some conversion events, these hits could all approximately
> lie on a plane, and thus fake a quirk signal. We model this background
> by generating a Z+γ+j sample with MadGraph5 aMC@NLO, where we decay the
> Z to neutrinos and require at least 200 GeV of MET, to satisfy our
> trigger requirement. We further require the pT of the photon be larger
> than 0.5 GeV. The fiducial cross section for this process is ~1 pb,
> which drops to ~10 fb if we require that the photon converts in the
> beampipe using the conversion probability from figures 33.16 and 33.17
> of [35]."

**[DIRECT PAPER EVIDENCE]** Process: p p → Z γ j, Z → νν (invisible).
**[DIRECT PAPER EVIDENCE]** Cuts applied before quoting "~1 pb": MET > 200
GeV, photon pT > 0.5 GeV.
**[DIRECT PAPER EVIDENCE]** Generator named: "MadGraph5 aMC@NLO".
**[DIRECT PAPER EVIDENCE]** "~1 pb" is explicitly called the **fiducial**
cross section, i.e. after the two stated cuts, not an inclusive/total
cross section.
**[DIRECT PAPER EVIDENCE]** The conversion probability (→ ~10 fb) is
applied as a *separate, subsequent* factor, not part of generation.
**[UNAVAILABLE]** The paper does not state: beam energy/sqrt(s) for this
specific background sample (the paper's signal samples use 13 TeV
elsewhere, but this is not repeated in Sec III D itself), PDF set, parton
shower/matching scheme (if any) for the +jet, a technical minimum jet-pT
generation cut, LO vs NLO accuracy of the actual computed matrix element,
number of neutrino flavours summed, renormalization/factorization scale
choice, or any K-factor.

## 2. Is "MadGraph5 aMC@NLO" a claim of NLO accuracy, or just the tool's name?

**[INFERENCE — genuinely ambiguous, do not over-read]** Since MG5_aMC v2.x
(released ~2014, well before this 2017 paper), the package's own banner
and self-identification is literally "MadGraph5_aMC@NLO" *regardless of
whether the specific run requested is LO or NLO* — confirmed directly by
inspecting this project's own existing LO-only run banners (see §4 below),
which self-identify as "MadGraph5_aMC@NLO VERSION 3.7.3" despite running a
plain LO `generate` command with no NLO order tags. Many papers from this
era cite "MadGraph5_aMC@NLO" simply as the tool name even for LO
processes. The paper's phrasing alone is therefore **not** conclusive
evidence that Z+γ+j was computed at NLO accuracy — it is *consistent with*
either LO or NLO. This project's existing generation is LO (see §4). This
is flagged as an open, testable factor (item A/N in the scan), not
asserted as the explanation.

## 3. What "fiducial cross section ~1 pb" most likely means, before conversion

**[INFERENCE]** Given it is called "fiducial" and explicitly listed after
the MET and photon-pT cuts, and the conversion-probability factor is kept
separate, the most natural reading is: ~1 pb = generator-level cross
section for p p → Z(→νν) γ j with MET>200 GeV and pT(γ)>0.5 GeV applied
at parton/generation level (or equivalently after shower, given these are
hard, well-separated cuts unlikely to be significantly altered by
showering). This is the quantity the project's own baseline should be
compared against — not any post-shower, post-detector-simulation,
post-preselection number.

## 4. What the project's existing generation actually computed
[DIRECT CODE EVIDENCE — inspected directly at
`/home/rafia/hep_tools/zgamma_background_test/`, outside the git repo]

- Process card (`Cards/proc_card_mg5.dat`, sha256
  `a0839f6185330748c0cfb1dcd1b7396f08015cc35ba3d9779bf09c2f866a8126`):
  `generate p p > z a j, z > vl vl~` with `vl = ve vm vt` — matches the
  paper's process (Z+γ+j, Z→ all 3 neutrino flavours), **LO only** (no
  `[QCD]`, `[QED]`, or NLO order tags; standard MadEvent `P1_*`
  SubProcesses directory structure, not an NLO `MadFKS`/`P0_*` structure).
- Run card (`Cards/run_card.dat`, sha256
  `a9157ca198e8750cada4fe72cd2b2491b142f9ac452e7542cbce8df3498b966c`):
  `ebeam1=ebeam2=6500 GeV` (√s=13 TeV), `misset=200.0` (matches paper's
  MET cut exactly), `ptj=20.0`, `etaj=5.0` (technical jet-acceptance
  cuts, generation-level), **`ptgmin=0.0`** — i.e. **no photon-pT cut
  applied at generation**, unlike the paper's stated 0.5 GeV. (The
  project's separate analysis script `extract_zgamma_photons.py` applies
  a post-hoc pT_gamma>0.5 GeV cut after showering — see §5.) PDF:
  `nn23lo1` (NNPDF2.3 LO), `lhaid=230000`. No MLM matching: pythia8 card
  in the archived banners shows `JetMatching:qCut = -1.0`,
  `JetMatching:doShowerKt = off` — matching is **not** enabled
  (`ickkw`/`xqcut` not set to a positive value).
- Five separate `generate_events` runs exist for this exact configuration
  (`run_01` through `run_05`), with **generator-level cross sections
  ranging 0.2225–0.3057 pb** despite each quoting a tiny statistical
  error (e.g. run_02: 0.2311 ± 0.0007 pb from 10000 events; run_05:
  0.3057 ± 0.0035 pb from 300 events) — full table in
  `tables/cross_section_scan_full.csv` row group "REPRODUCIBILITY". This
  spread (~±20% around the mean) reflects MadEvent's phase-space
  integration grid being freshly surveyed/adapted on each independent
  `generate_events` invocation, not a fluctuation the quoted per-run
  statistical error captures. **The project's downstream analysis
  (`extract_zgamma_photons.py`) uses `run_02`'s HEPMC file specifically**
  (hardcoded default path), so **0.2311 pb is the actual baseline
  generator-level number this project's ~0.23 pb figure traces back to**
  — not an arbitrary round number.

## 5. Where does the project's quoted "~0.23 pb" actually come from?

**[DIRECT CODE EVIDENCE]** `run_02`'s generator-level cross section
(0.2311 ± 0.0007 pb, 10000 events, MET>200 & ptj>20 & etaj<5 & ptgmin=0
applied at generation) is the number carried forward. The paper-matching
`pT_gamma>0.5 GeV` cut is applied *after* showering, in
`extract_zgamma_photons.py`, as a post-hoc selection on the LHE/HepMC
final state — it is not baked into the quoted 0.2311 pb generator
cross-section itself. This means the "~0.23 pb" figure most commonly
cited in project reports is **the pre-photon-pT-cut generator cross
section**, while the paper's "~1 pb" is explicitly **post**-cut (both
cuts applied). This is a genuine **like-for-like mismatch in what stage
of selection the quoted number represents** — not yet evidence of which
number is "correct" for comparison, but a definition inconsistency that
must be fixed before any other factor is meaningfully compared. Given the
photon-pT cut is very soft (0.5 GeV) its own effect is expected to be
small (see `extract_zgamma_photons.py` inline note: `n_pt_gamma_fail`
measured near-zero historically) — but this has not yet been quantified
in this audit and is scan item D.

## 6. Summary classification table

| Question | Paper | Project baseline (run_02) | Class |
|---|---|---|---|
| Process | p p > z a j, z > νν | identical | DIRECT PAPER + CODE EVIDENCE, MATCH |
| √s | not restated in Sec IIID (13 TeV used elsewhere) | 13 TeV | INFERENCE (assumed match) |
| MET cut | >200 GeV | misset=200.0 (generation-level) | MATCH |
| Photon pT cut | >0.5 GeV, part of quoted "~1pb" | ptgmin=0 at generation; 0.5 GeV applied post-shower, NOT part of quoted 0.2311pb | **MISMATCH IN STAGE** |
| Jet pT/η technical cuts | not stated | ptj=20 GeV, etaj<5 | UNAVAILABLE (paper), so cannot compare |
| LO vs NLO | ambiguous tool-name only | confirmed LO | **UNRESOLVED — scan item A** |
| Matching (MLM/CKKW) | not stated | not enabled (qCut=-1) | UNAVAILABLE (paper) |
| PDF | not stated | NNPDF2.3 LO (lhaid 230000) | UNAVAILABLE (paper) |
| Run-to-run generator spread | n/a | 0.2225–0.3057 pb across 5 identical-card runs | project-internal caveat, independent of paper comparison |

## 7. What this means for the rest of the audit

The single largest, most concretely actionable next step is **not** yet
"why is 0.23 different from 1" in one dimension — it is that the
project's own quoted number is defined at a different selection stage
than the paper's. The scan (§ tables/cross_section_scan_full.csv) tests
this (item D) alongside the LO/NLO ambiguity (item A) and PDF/scale
choices, one factor at a time, without combining changes, per the task's
explicit requirement.
