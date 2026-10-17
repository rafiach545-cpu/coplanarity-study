# D39 pre-registration (written 2026-10-14, BEFORE the run)
Test: string direction at equal CM time (PreFASERQuirkSim step = arXiv:2002.07503 Eqs. VIII.1-4) instead of equal lab time (our production),
effect on Delta_s and eps_reco (mode FIRST).
Setup: same events, momenta, charges (+-1), vertex z0 and SCT random draws as P18; uniform B = 2 T; no energy loss; production at the origin
(z shifted by z0 for the hits); integration until the CM transverse radius reaches 60 cm; hits with t < 25 ns, Ref. [27] lengths; reconstruction
p18.reco unchanged; SCT z none (Z0) and 580 um (Z580). Benchmarks: colored 1800 GeV 2 keV, EW 800 GeV 4 keV, EW 1 keV and 2 keV.
Denominator: the production (lab-time, 300 steps/period) fiducial set at each Lambda. CM-time step: divStep 30000 (convergence checked on one event
with 3000 / 30000 / 100000 before the run). Lab-time reference: production integrator, 300 steps/period, run in the same script.
Expectations:
- Delta_s, SCT z none: EW median below 43 um, about sqrt(43^2 - 15^2) = 40 um, not down to the paper's 28 um; colored essentially unchanged.
- eps_reco, SCT z none: EW at 4 keV changes by at most +-1-3 events (50/62 already pass Delta_s).
- SCT z 580 um: very small change (Delta_s dominated by the z smearing).
- EW 1-2 keV: thinner planes -> eps_reco can only rise; the low-Lambda excess over the paper can grow, not shrink.
A change of 5 or more events in eps_reco at any benchmark would be a new, significant result.
