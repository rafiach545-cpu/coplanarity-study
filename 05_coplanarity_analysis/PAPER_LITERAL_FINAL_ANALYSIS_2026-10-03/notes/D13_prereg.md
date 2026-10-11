### D13 summary and pre-registered test (written BEFORE the run, 2026-10-09)
- **Established:** the particle selection is correct (stored trigger decisions reproduced 1045/1045 EW and 873/873 colored), and the three
  definitions give the eps_trig numbers in the D13 table above.
- **Hypothesis (label: hypothesis):** the paper used the matrix-element (LHE-level, before the parton shower) quirk momenta for EW and the Pythia
  output (after the shower) for colored. If so, the EW trajectories also started from the pre-shower momenta.
- **Test** (`scripts/P23_ew_hard_momenta.py`): the EW2000 events whose pre-shower pair has pT > 200 GeV (121 of 1045). Full pipeline: fiducial
  (Ref. [27] lengths, t < 25 ns), then eps_reco at Lambda = 1, 2, 4 keV, SCT z not smeared, one hit per quirk per layer.
  - Column H (test): trajectories from the pre-shower (status-23) quirk momenta.
  - Column S (control): the same 121 events, trajectories from the after-shower final-state momenta.
  - Both columns use identical beam-spot and SCT R-phi random draws per event (SeedSequence([23, hepmc_event_index])), so H - S isolates the
    momentum effect and S - (186-event reference) the selection effect.
  - Denominators: eps_fid = N(fiducial) / 121; eps_reco = N(signal region) / N(fiducial) within each column.
- **Reference (current, after-shower trigger, 186 events):** eps_fid = 62/186 = 0.333; eps_reco(2 keV) = 40/62 = 0.645 (1 keV 12/62, 4 keV 50/62).
- **Criteria, fixed now (applied to column H; "toward the paper" = at least half of the gap closed):**
  - fiducial condition: eps_fid(H) <= 0.307 (half way from 0.333 to the paper's 0.28);
  - low-Lambda condition: eps_reco(H, 2 keV) <= 0.53 (half way from 0.645 to the paper's 0.41).
  - **Supported:** both conditions met. **Rejected:** neither met. **Partial:** one met.
  - Attribution: a condition counts for the momentum effect only if column S does not meet it as well; otherwise the change is due to the
    event selection.
- Point estimates are used; with ~121 events the fiducial fraction has a statistical spread of about +-0.04, so Wilson 95% intervals are
  reported next to every number. A supported result will be written as "hypothesis supported", not "confirmed". The draft value 0.03 is not
  part of this test. This is the last EW test.
