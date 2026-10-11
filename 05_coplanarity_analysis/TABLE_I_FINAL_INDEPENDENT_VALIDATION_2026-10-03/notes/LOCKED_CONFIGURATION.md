# LOCKED configuration for the independent confirmation (written 2026-10-02T16:56:31Z, BEFORE the confirmation samples exist)

At the time of locking, no CONF_EW / CONF_COL files exist (checked: `ls` returns "No such file").

## Decisions (made from the source audits, not from confirmation efficiencies)
| Item | Locked choice | Basis |
|---|---|---|
| EW model | vector-like (1,1)_1 quirk, Z coupling i e sW/cW (pure gamma^mu) = UFO copy `quirk_vlZ` | paper "(1,1)_1 vector-like"; frozen UFO had SM-electron chiral Z coupling (task 4); trigger-neutral (p=0.60) |
| Colored model | frozen UFO (spin-1/2, colour triplet, Q=2/3, QCD only) | paper "(3,1)_2/3", "only QCD contributions" |
| Generation | MG5 3.7.3, `p p > X X~ @0` + `j @1`, frozen run cards (nn23lo1, xqcut 30, ickkw 1, 13 TeV) | paper "up to 1 jet"; rest undocumented (frozen) |
| Shower | Pythia 8.317, frozen shower settings (qCut 45, nJetMax 1, ...) via driver v3 | validated event-by-event vs frozen |
| Sample sizes / seeds | CONF_EW: 4000 LHE, MG iseed 9401 ; CONF_COL: 10000 LHE, MG iseed 9501 ; detector randoms SeedSequence 81001 (EW) / 82001 (COL) | fresh, never used |
| Trigger | final-state pair pT > 200 GeV / matched | paper |
| Colored charge | both R-hadrons non-zero charge | paper |
| Geometry | PRIMARY B finite barrel (ref [27] dimensions, now read directly); SYSTEMATIC A eta-cone | paper uses ref [27] parameters, barrel only |
| SCT z | ENVELOPE Z0 / Z34 / Z580 / Z1160 (no single primary); Z1160 = paper-text literal; Z0 = calibrated | task 1 |
| Delta_w convention | PRIMARY W1 sqrt(lambda_2) < 1 cm (paper Eqs. 10-11); SYSTEMATIC W2 (paper-quoted 0.5*sqrt(lambda_2) < 1 cm) | task 2 (Fig. 4 factor 2) |
| Algorithm | literal Sec. III C (project coplanarity_fit, unmodified) | paper |
| eps_reco | full Sec. IV SR / (trigger AND fiducial) | paper |
| Statistics | Wilson 95% (primary), Clopper-Pearson 95%, exact binomial p; two-sample compatibility with inferred paper uncertainties | task 5 |
| Pooling | NONE: confirmation samples are reported on their own | user requirement |

## Hashes of the code/config that will produce the confirmation numbers
```
82e49ce99552734c3d1c4a2474077eff69d801eaacb0a9fa2d1e3c7bd4dbeff1  scripts/06_confirmation_chain.py
210b53f3a884a007fdc3a25cdd842ed300dd3a81603586c45f2757de634df850  /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/driver/shower_v3_py8317
3d13aba77fa51e9239468be43620324086ce855e84651eb89f7231afd612f4ce  /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/driver/quirk_mlm_shower_v3.cc
bf1eb53e6861cff414e9be962ae7f28de7b92628e0935c3722c50e54aad5c800  /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/runs/base_EW.cmd
c5c89b38da844ecf9ceb713e0aacf2091f0446b29cc2d5b3852d379b69192b94  /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/runs/base_COL.cmd
46283226dc8fd5be73d5c047a3505ec9d3c1855a419ade33af6533ae780015a2  /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/proc/gen.sh
f5251b85d37cbf1372b06f8fc1af9bf934bd2d02434deadc7b6bc1c0e178f146  /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/proc/runjob.sh
11f81947540fd8a23d0ed4102b5e0e7b5179097a98a079fd4e672c3a94126057  vertices.py
3025da49c0fd7e71bd4b3ab137643422ca6b1d37cc102175454e1b2d1bbdab73  couplings.py
cea7f1a15c361a8863396f130a84cf49cea81d254f0d50d0ea7a1c73f14774ba  particles.py
bef0eebc119698eda0e1388556393b26fd68e4dc3d13b6ccfc5b11d170ca405e  /home/rafia/coplanarity_study/05_coplanarity_analysis/coplanarity_fit.py
d09187776d444729966f47f8a91478bce6a7ab5d19e416863ee484f2a801034e  /home/rafia/coplanarity_study/04_detector_sim/trajectory_to_hits.py
79ec8e28a71dbd3649b0e3845b4bd061f7c835c3e2d32adaa58a803f0e4a2881  /home/rafia/coplanarity_study/03_trajectory_sim/quirk_trajectory_optimized_v2.py
```
