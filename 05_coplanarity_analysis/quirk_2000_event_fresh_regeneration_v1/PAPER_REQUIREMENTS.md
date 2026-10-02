# Paper Requirements — Fresh 2000+2000 Event Regeneration

Reread directly from arXiv:1708.02243v2 (cached primary-source extraction,
`paper.txt`, page markers `===== PAGE N =====`), independent of any prior
project report. Every row below cites the paper text itself.

| # | Section/page | Quotation/paraphrase | Value | Implementation location | Classification |
|---|---|---|---|---|---|
| 1 | Sec II, p.2 | "vector-like quirks in the (1,1)_1 and (3,1)_2/3 representations" | EW=(1,1)_1 singlet, colored=(3,1)_2/3 triplet | MadGraph process definition | DIRECT PAPER REQUIREMENT |
| 2 | Sec II, p.2 | "probability for those final states [colored R-hadrons] to have ±1 charges is roughly 30%" | ~30% | charge-lookup filter, applied to colored sample only | DIRECT PAPER REQUIREMENT |
| 3 | Sec III A, p.5 | "For electroweak production the quirks are taken to have unit charge and are produced in Drell-Yan, while for colored production only QCD contributions are included" | EW=DY, colored=QCD-only | MadGraph proc_card | DIRECT PAPER REQUIREMENT |
| 4 | Sec III A, p.5 | "generate signal samples ... with up to 1 jet using MadGraph5_aMC@NLO, subsequently matched using Pythia8" | MLM matching, +1 jet | ickkw=1 | DIRECT PAPER REQUIREMENT |
| 5 | Sec III A, p.5 | "evolved ... assuming a uniform 2T magnetic field along the z-direction" | B=2T, along z | B_tesla=2.0 | DIRECT PAPER REQUIREMENT |
| 6 | Sec III A, p.5 | "for the pixel detector we use the pixel size rather than the resolution and for ... SCT we conservatively assume a resolution of twice the intrinsic accuracy" | pixel=size; SCT=2x intrinsic (Run-2 spec) | detector geometry module | DIRECT PAPER REQUIREMENT |
| 7 | Sec III A, p.5 | "gaussian smearing with width 45 mm to the z-coordinates ... beamspot" | sigma_z=45mm | beamspot z-smearing | DIRECT PAPER REQUIREMENT |
| 8 | Sec III A, p.5 | "only included the barrel ... effectively restricts the fiducial range to |eta|<~1.8" | barrel-only, 8 layers | fiducial geometry | DIRECT PAPER REQUIREMENT |
| 9 | Sec III B, p.5 | "impose a pT > 200 GeV cut on the center [of] mass momentum of the quirk/anti-quirk system" | pT(quirk pair)>200GeV | trigger cut | DIRECT PAPER REQUIREMENT |
| 10 | Sec III A/B (implied), p.5 | "the quirks must reach the muon chamber in less than 25 ns" | t<25ns | fiducial timing cut | DIRECT PAPER REQUIREMENT |
| 11 | Sec III C, p.5-6 | "Start from the 8th layer, collect all pairs of hits with delta_phi<0.1 and delta_z<2cm. Repeat ... for the 7th layer" | seed layers 8,7; dphi<0.1, dz<2cm | seeding_and_iterative_fit() | DIRECT PAPER REQUIREMENT |
| 12 | Sec III C, p.6 | "Construct four-hit combinations ... xa.n3>0 for all hits, delta_s<0.05cm and delta_w<1cm" | 4-hit seed cuts | seeding | DIRECT PAPER REQUIREMENT |
| 13 | Sec III C, p.6 | "loop over the remaining 6 layers outside-in ... (x.n3)>0, |x.n1|<0.05cm, |x.n2|<1cm" | iterative fit layer 6->1 | iterative growth | DIRECT PAPER REQUIREMENT |
| 14 | Sec III C, p.6 | "If delta_s and delta_w do not increase by a factor of 3, add the hit" | growth factor 3 | growth rule | DIRECT PAPER REQUIREMENT |
| 15 | Sec III C, p.6 | "apply the final cut delta_w<1cm. If more than one plane identified, keep smallest delta_s" | Sec IIIC event selection | select_reconstructed_plane() | DIRECT PAPER REQUIREMENT |
| 16 | Sec IV, p.7 | "At least one plane reconstructed" | cut 1 | apply_signal_region_cuts() | DIRECT PAPER REQUIREMENT |
| 17 | Sec IV, p.7 | "All but one layer must contain 2 hits, the remaining layer at least 1 hit" | hit-multiplicity | check_hit_multiplicity() | DIRECT PAPER REQUIREMENT |
| 18 | Sec IV, p.7 | "delta_w<1.0cm and delta_s<0.01cm" | final Sec IV cuts | apply_signal_region_cuts() | DIRECT PAPER REQUIREMENT |
| 19 | Sec IV, p.7 | "The reconstruction efficiency is defined as the efficiency of our algorithm in finding quirks which satisfy both the trigger and fiducial requirements" | eps_reco = N_plane/N_fiducial (Sec IIIC output, NOT Sec IV final rate) | reported separately, not conflated | DIRECT PAPER REQUIREMENT (definition only; both N_plane/N_fid and N_final/N_fid measured and reported separately per instruction) |
| 20 | Table I, p.7 | Colored (1800GeV): eps_trig=0.24, eps_fid=0.28, eps_reco=0.35 at Lambda=2keV | comparison target only | statistics/paper_comparison.csv | PAPER COMPARISON (not used to tune) |
| 21 | Table I, p.7 | EW (800GeV): eps_trig=0.10, eps_fid=0.28, eps_reco=0.72 at Lambda=4keV | comparison target only | statistics/paper_comparison.csv | PAPER COMPARISON (not used to tune) |
| 22 | Abstract/Fig.6 caption, p.1/8 | L=300 fb^-1 | not used in this task (no yield/contour calc here) | N/A | PAPER-INFERRED (out of scope this task) |

## Items the paper does not specify (PROJECT ASSUMPTION, disclosed)

- Exact PDF set, renormalization/factorization scales: not stated by the
  paper. This regeneration uses NNPDF2.3LO (nn23lo1), MadGraph's dynamic
  default scales — a **PROJECT ASSUMPTION**, unchanged from what frozen
  templates already used (see Independence Log below).
- Exact MLM xqcut value: not stated. Uses xqcut=30 GeV (from frozen
  template) — **PROJECT ASSUMPTION**.
- Hit-merging exact algorithm ("attempt to model the ATLAS hit merging
  procedure", p.5): paper does not give the precise rule. Uses
  neighboring-pixel adjacency merge (adjacency=1) — **PROJECT ASSUMPTION**.

## Independence Log (frozen technical templates reused, explicitly recorded)

Per the explicit exception ("Previously recovered generator/process cards
may be used only as frozen technical templates where the paper does not
publish enough information to build them from scratch"):

- `/home/rafia/hep_tools/quirk_signal_1800gev_2kev/` (colored, QCD-only
  process definition) and `/home/rafia/hep_tools/quirk_ew_800gev_4kev/`
  (EW, Drell-Yan process definition) are reused as **frozen, unmodified
  process-directory templates** — MadGraph process/model compilation
  (QCD-only vs. DY-only matrix elements, PDF set, xqcut) is technical
  infrastructure the paper does not publish in buildable form, not a
  numerical result. No LHE file, HepMC file, cutflow, efficiency, or
  numerical conclusion from those directories' *prior runs* is read, copied,
  or referenced anywhere in this task. Only `Cards/proc_card_mg5.dat`
  process structure is reused; `Cards/run_card.dat` (nevents, iseed) and
  `Cards/param_card.dat` (mass — unchanged here, both already at the target
  masses) are freshly edited for this run.
- The validated trajectory integrator (`quirk_trajectory_optimized_v2.py`,
  commit `3c33601`), detector-response code (`trajectory_to_hits.py`), and
  reconstruction algorithm (`coplanarity_fit.py`) are reused **as code**
  (the physics implementation itself, already independently validated
  bit-identical to the unoptimized baseline in prior sessions) — this is
  software infrastructure, not a numerical result of this task, and
  re-deriving validated RK4 integration code from scratch would introduce
  new, unvalidated risk rather than independence. No cached trajectory,
  hit table, candidate table, or efficiency number from any prior run is
  imported.
