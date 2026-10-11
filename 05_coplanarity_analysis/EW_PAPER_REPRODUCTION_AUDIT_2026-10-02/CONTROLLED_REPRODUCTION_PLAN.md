# Controlled Reproduction Plan — EW trigger efficiency (NOT LAUNCHED)

Status: **proposal only. Nothing has been run.** It needs explicit approval.

## Why only a narrow plan is defensible

The published paper (arXiv:1708.02243v2) fixes only these generator settings:

- signal "with up to 1 jet",
- MadGraph5_aMC@NLO,
- matched using Pythia8,
- unit-charge Drell-Yan production.

It does **not** state √s, PDF, μR/μF, xqcut/qCut, matching scheme, tune, or generator-level cuts.

The only further author-traceable information is two LaTeX comments in the arXiv source: `%MG5 v2.3.3` and `%Pythia 8.212`. They are not printed in the paper.

Under the audit's rules, a version change is therefore the **only** generator change with any source support. Every other setting must stay at the project's current values, or at the documented defaults of those versions. Each such setting must be labelled as an assumption and never varied to approach 0.10.

The fiducial question needs **no** new simulation. The finite-barrel result in the audit report was obtained on existing events.

## Hypothesis under test (single)

H_v: generating with MG5 v2.3.3 + Pythia 8.212 changes the EW mQ = 800 GeV matched-sample fraction with quirk-pair pT > 200 GeV from ≈0.177 toward 0.10.

Pass and fail are both reportable outcomes. A null result keeps the trigger verdict UNRESOLVED.

## Isolated setup

- New directory: `/home/rafia/hep_tools/EW_VERSION_PILOT_<date>/`. Write nothing into existing run directories or the repo, except a new audit subfolder for results.
- MG5 v2.3.3 tarball: download and record its SHA-256. Pythia 8.212 built against it, with its own `PYTHIA8DATA`. The driver's `PYTHIA8DATA` handling must not leak into this.
- MG5 2.3.3 predates the MG5→Pythia8 interface (introduced in 2.5.x), so matching would be run with Pythia's `main89`-style MLM program on the LHE file. Its settings must be recorded verbatim.

## Settings table (to be filled and frozen before running)

| Setting | Value | Source label |
|---|---|---|
| Process | `p p > qe+ qe- @0`, `add process p p > qe+ qe- j @1` | paper-confirmed ("up to 1 jet") |
| Model | same `quirk` UFO as the project | project (paper: unit charge, DY) |
| √s | 13 TeV | **assumption** (Run-2 context) |
| PDF | MG5 2.3.3 template default (to be read from its `run_card.dat`, not assumed) | **version default** |
| Scales | MG5 2.3.3 template default | **version default** |
| xqcut | 30 GeV (project value) | **assumption, held fixed** |
| qCut | 45 GeV (project value) | **assumption, held fixed** |
| nJetMax / scheme | 1 / MadGraph-style MLM | paper "up to 1 jet" / assumption |
| Tune | Pythia 8.212 default | **version default** |

## Validation gates (all must pass before any large sample)

1. **Pilot of 500 LHE events** with a fixed recorded seed.
2. **Cards proven:**
   - diff `proc_card`, `run_card` and the Pythia settings against the table above;
   - banner and log confirm the versions (MG5 2.3.3, "This is PYTHIA version 8.212");
   - zero JetMatching errors.
3. **Process proven:** LHE multiplicity split shows both 0-jet and 1-jet subprocesses. Quirk PDG ±9000011 with mass 800 GeV.
4. **Cuts proven:**
   - no generator-level cuts on quirks;
   - trigger computed by `scripts/01_raw_event_recount.py` unchanged: final status-1 pair pT > 200, strict.
5. **Denominators proven:**
   - generated = LHE count;
   - matched = HepMC events with exactly 2 final quirks;
   - trigger/matched reported with Wilson 95% interval and an exact binomial p-value vs 0.10 and vs the project's 0.177.
6. **Colored control:** repeat gates 1–5 for colored mQ = 1800 GeV with the same versions. If the colored value moves away from the reproduced 0.24, the version change is not neutral, and that must be reported.

## Only if gates pass

Run a 2000-event EW sample with the frozen settings and a new seed, then report the result against the existing 1000 and 2000 samples with a Fisher exact test.

No parameter in the settings table may be changed after seeing results. Any further variation (e.g. qCut) would be a labelled sensitivity study, not a reproduction.
