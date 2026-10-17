# D41 pre-registration: EW trigger as an LO ratio (written 2026-10-15, BEFORE any D41 run)
Hypothesis (D39, inference from 1911.02223 App. A and our LO numbers): the paper's EW eps_trig = 0.10 is the LO ratio sigma(QQj, pT(j) > 200 GeV) / sigma(QQ),
i.e. its EW signal sample is parton-level QQ + 1 jet with pT(j) > 200 GeV, not a matched + showered sample with a cut on pT(QQ).
1. Samples (13 TeV, nn23lo1, MG default dynamical scale, our quirk model, shower off):
   A: p p > qe+ qe- (inclusive, sigma only);  B: p p > qe+ qe- j, ptj = 200, ickkw = 0, xqcut = 0, 3000 events.
   Colored (sigma only): p p > t1 t1~ and p p > t1 t1~ j (ptj = 200), m = 1800 GeV.  MG5 3.7.3 and MG5 2.3.3 (both if they run).
2. eps_trig = sigma(B) / sigma(A). Expected: EW ~0.095, colored ~0.14.
3. Pipeline on sample B of MG5 3.7.3 (LHE quirk momenta, every event has pT(QQ) = pT(j) > 200 GeV): fiducial (Ref. [27] lengths, t < 25 ns,
   P20 definition) and eps_reco for EW Lambda = 1, 2, 3, 4, 5 keV; SCT z none, first crossing, production integrator (300 steps/period),
   beam spot one z0 per event (sigma 4.5 cm), SCT r-phi draws from a per-event seed (SeedSequence([41, event index])).
   Sensitivity (reported, not used in the criteria): the same sample B showered with Pythia 8.317 without matching.
4. Statistics: k/n, Wilson 95%, exact two-sided binomial p against the paper; combined chi2 of the EW Lambda column with the event-level bootstrap
   correlation (10 000 resamples, as scripts/D3b). Production reference: EW, no SCT z smearing, first crossing: chi2_corr = 23.81, p = 2.4e-4
   (tables/lambda_scan_combined_test_2000.csv; the request quoted 25.3, p = 1.2e-4, which is not in our tables).
5. Criteria:
   (i)   eps_fid of sample B consistent with the paper's 0.28 (exact binomial p >= 0.05);
   (ii)  combined chi2 p of the EW Lambda column >= 0.05;
   (iii) eps_reco at 2 keV at least 0.10 below the production 0.645 (i.e. <= 0.545).
   SUPPORT: (i), (ii) and (iii). PARTIAL: one or two of them. REJECT: eps_fid and the 2 keV eps_reco both as in production
   (eps_fid consistent with our production 0.333 = 62/186 at p >= 0.05 and eps_reco(2 keV) within 0.10 of 0.645), and (ii) fails.
