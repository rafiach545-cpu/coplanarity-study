# D41 pre-registration addendum: interim rule (written 2026-10-15, after the run started and BEFORE any result was looked at;
# only the number of finished events was read). The original text notes/D41_prereg.md (sha256 70d7d29e...) is unchanged.
Reason: runtime ~50-60 s per event for 5 Lambda points (3000 events ~ 14 h). The run continues to 3000 events in any case.
Interim analysis on the first 1000 events of sample B (events are processed in order; checkpoint logs/D41_mg5_373_lo_events.jsonl).
Simple uncertainty sigma = sqrt(e (1 - e) / n) for each efficiency e = k / n.
A criterion is DECIDED at the interim if its outcome does not change when the estimate is moved by +-2 sigma:
  (i)   eps_fid (Lambda = 4 keV) consistent with 0.28: evaluated with the exact binomial test at e - 2 sigma, e and e + 2 sigma (n = events);
        decided if all three give the same outcome (p >= 0.05 or p < 0.05).
  (ii)  combined chi2 p >= 0.05: decided FAIL if p < 0.0027, decided PASS if p > 0.32, otherwise undecided.
  (iii) eps_reco(2 keV) <= 0.545: decided if |e - 0.545| > 2 sigma (n = fiducial events at 2 keV).
  REJECT clause parts: eps_fid vs the production 0.333 (as (i), with 0.333) and |eps_reco(2 keV) - 0.645| < 0.10 (decided if
  |e - 0.545| > 2 sigma and |e - 0.745| > 2 sigma).
If every criterion that enters the verdict is decided, the interim verdict (SUPPORT / PARTIAL / REJECT, original definitions) is final.
Otherwise the verdict waits for 3000 events. The showered sensitivity run starts after the main run (3000 events).
