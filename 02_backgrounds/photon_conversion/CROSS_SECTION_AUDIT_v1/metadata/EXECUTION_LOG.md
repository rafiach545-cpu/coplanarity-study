# Execution Log — Cross-Section Discrepancy Investigation

Chronological, timestamped where available. All work confined to
`02_backgrounds/photon_conversion/CROSS_SECTION_AUDIT_v1/`. No existing
authoritative file modified or deleted. Figure 6 confirmed paused
(pgrep clean) and untouched before starting. Fresh 2000+2000 quirk
regeneration directory not touched.

1. Safety check: `pgrep -fal "run_phase5|madgraph|pythia|generate_events"`
   → no matches, confirmed safe to start.
2. Created `CROSS_SECTION_AUDIT_v1/{metadata,tables,generation,logs,checkpoints}`.
3. Located cached paper text extraction (from an earlier session's
   scratchpad) and grepped for the conversion-background passage. Found
   exact text at `paper.txt` lines 658-702 (Sec III D). Read in full.
4. Located the actual MadGraph run directory used for the project's
   existing "~0.23 pb" figure: `/home/rafia/hep_tools/zgamma_background_test/`
   (outside the git repo, as is standard for this project's HEP tool
   runs). Inspected `Cards/proc_card_mg5.dat`, `Cards/run_card.dat`,
   `SubProcesses/results.dat`, `crossx.html`, and the per-run archived
   banners in `Events/run_0{1..5}/`.
5. Discovered 5 separate `generate_events` runs already exist for the
   identical card configuration, with cross sections spanning
   0.2225-0.3057 pb — flagged as a project-internal reproducibility
   caveat (see PAPER_CROSS_SECTION_DEFINITION.md §4 and
   cross_section_scan_full.csv row `reproducibility_spread_summary`).
6. Confirmed via banner inspection that `run_02` (0.2311 ± 0.00072 pb,
   10000 events) is the specific run consumed by
   `extract_zgamma_photons.py`'s hardcoded default path — this is the
   project's actual traceable baseline number, not an arbitrary rounding.
7. Discovered the photon-pT>0.5 GeV cut (which the paper includes IN its
   quoted ~1pb fiducial cross section) is NOT applied at generation in
   the project's baseline (`ptgmin=0.0`) — it is applied post-shower, in
   the separate analysis script, and is therefore NOT part of the quoted
   0.2311 pb figure. This is a selection-stage mismatch between what the
   paper's "~1pb" and the project's "~0.23pb" actually represent.
8. Discovered a pre-existing, PRIOR (2026-09-14, before this audit)
   attempt at an NLO version of this process at
   `/home/rafia/hep_tools/zgamma_nlo_test/` (`p p > z a [QCD]`, NLO
   FKS/MCatNLO structure, `ptgmin=0.5` matching paper). Inspected
   `run_01_tag_1_debug.log`: the run failed at the Fortran/C++
   compilation stage (`ld returned 1 exit status` building
   `test_soft_col_limits`) — no cross section was ever obtained. Also
   noted this attempt never set the MET>200 GeV cut at all, so even a
   successful compile would not have produced a directly comparable
   number as-is. Logged as NON_AUTHORITATIVE, not rerun/fixed (fixing an
   NLO toolchain compilation failure is an open-ended engineering task,
   flagged for explicit user decision rather than attempted silently
   under an assumed unlimited time/resource budget).
9. Wrote `metadata/PAPER_CROSS_SECTION_DEFINITION.md` (step required by
   the task before any new run), classifying every claim DIRECT PAPER
   EVIDENCE / DIRECT CODE EVIDENCE / INFERENCE / UNAVAILABLE.
10. Wrote `tables/cross_section_scan_full.csv` and
    `tables/cut_and_process_definition_matrix.csv`, populated with the
    findings from steps 4-8.
11. Launched ONE new, cheap, single-factor pilot run to directly test
    the selection-stage mismatch found in step 7: copied the baseline
    process directory (rsync, excluding Events/HTML, to
    `generation/scan_D_ptgmin05/`), changed ONLY `ptgmin` from 0.0 to
    0.5 GeV, set `nevents=5000`, `iseed=91001` (fresh, distinct seed —
    never used elsewhere in this project), left every other run_card
    setting byte-identical to the baseline. Launched
    `./bin/generate_events run_D1 -f` in background (PYTHIA8DATA unset
    per the project's established fix for the MadGraph-bundled-vs-conda
    Pythia8 version mismatch). Status/result recorded below as it
    becomes available.

## Scan item D result

(Filled in when the background run completes — see
`tables/cross_section_scan_full.csv` row `scan_D_ptgmin05_pilot` and
`logs/scan_D_ptgmin05_generation.log`.)

## Continuation (second work session, same audit)

12. Investigated the 0.2225-0.3057 pb run-to-run spread per explicit
    instruction: confirmed all runs report the same quantity at the same
    stage (no matched-vs-unmatched confusion). Ran 3 new independent-seed
    reproducibility tests (seeds 101/202/303, N=100 each, reusing
    scan_D's already-compiled binary): 0.2337, 0.2221, 0.2215 pb. Combined
    with runs 01-04 and scan_D: weighted mean 0.2300+-0.00054 pb,
    chi2/dof=24.7/7 -- run_05 alone is a ~21-sigma outlier, traced to
    likely VEGAS grid non-convergence at its low (300) event-count survey
    for that specific seed. Documented in cross_section_scan_full.csv
    row `reproducibility_diagnosis`.
13. Diagnosed the NLO compilation failure's true root cause: MG5's own
    bundled FastJet library silently failed to build (a conda-GCC 16.2 /
    libtool `__TMC_END__` shared-library linking incompatibility) but
    MG5's installer did not check the build exit code and proceeded
    anyway, leaving no `libfastjet.so` at all. Documented in
    `metadata/NLO_COMPILATION_FAILURE_DIAGNOSIS.md`.
14. Repaired this in a disposable directory (`/tmp/fastjet_disposable_build/`,
    outside any project or authoritative-install path): downloaded
    FastJet 3.4.2 fresh, built with `--disable-shared --enable-static`
    (sidesteps the broken shared-library link path entirely). Build
    succeeded; `fastjet-config --version` confirmed working.
15. Ran the PDF (cteq6l1), scale (0.5x, 2x), and jet-pT-cut (40 GeV)
    single-factor LO scans, each as its own new pilot run in scan_D's
    already-compiled directory (fresh seeds 404/505/606/707). All
    results recorded in `tables/cross_section_scan_full.csv`; none
    explain the paper gap (see FINAL_CROSS_SECTION_AUDIT.md Section 1).
16. Attempted an actual NLO pilot using the repaired FastJet: created a
    fresh disposable NLO output directory
    (`generation/nlo_pilot_attempt/`, process `p p > z a [QCD]`,
    matching the original failed attempt), pointed its own
    `Cards/amcatnlo_configuration.txt` at the disposable static FastJet
    (a change to this audit's own new output directory only). Hit a
    second, unrelated, easily-fixed issue (`libninja.so.0` not on
    `LD_LIBRARY_PATH` despite the file existing) -- fixed by exporting
    `LD_LIBRARY_PATH` for this subprocess only. Compilation then
    succeeded cleanly (all 4 subprocess channels passed
    test_ME/test_MC/check_poles). This conclusively resolves the
    original NLO compilation blocker.
17. The resulting cross section (1175 pb) was NOT paper-comparable
    (process leaves Z undecayed, no MET cut applicable) -- documented
    honestly in `metadata/NLO_REPAIR_ATTEMPT.md` rather than presented
    as a K-factor result. Process killed cleanly once this was
    understood (no further value in letting it run to full unweighting).
18. Verified via `pgrep`/`ps aux` that no generation/compile processes
    remain running, Figure 6 remains untouched, the fresh 2000+2000
    quirk regeneration directory is untouched, and `git status --short`
    shows no changes outside `CROSS_SECTION_AUDIT_v1/` and the
    (already-untracked, pre-existing) quirk regeneration directory.

## What remains (not completed in this session, honestly disclosed)

The full task specification calls for a 15-item (A-O) one-factor-at-a-time
scan. Completed this session: photon-pT-cut stage (D), PDF set, scale
(0.5x/2x), jet-pT cut, and the run-to-run reproducibility investigation.
The NLO compilation blocker (item A) was fully diagnosed and fixed, but
a genuinely paper-comparable NLO cross section (with Z->nunu decay and a
MET cut) was not obtained -- this is the clearest remaining next step.
Not attempted this session: inclusive Zgamma vs Zgamma+j, DeltaR cuts,
coupling-order restrictions, generator-version differences, and the
combined "closest paper-compatible configuration" run. This is disclosed
explicitly in `FINAL_CROSS_SECTION_AUDIT.md`, not presented as complete.
