# Cross-Section Discrepancy Investigation — Final Report (this session)

**Overall verdict: UNRESOLVED.** Every single-factor cause tested this
session was ruled out or shown to be far too small to explain the ~4.3×
gap between the paper's quoted ~1 pb and the project's ~0.23 pb. One
major technical blocker (NLO compilation) was fixed, but the specific
paper-comparable NLO number (with Z→νν decay and a MET cut) was not
obtained. This report does not claim the gap is explained, and nothing
was tuned toward 1 pb.

See `metadata/PAPER_CROSS_SECTION_DEFINITION.md` (paper evidence),
`metadata/NLO_COMPILATION_FAILURE_DIAGNOSIS.md` and
`metadata/NLO_REPAIR_ATTEMPT.md` (NLO root cause + fix), `metadata/
EXECUTION_LOG.md` (full chronology), and `tables/cross_section_scan_full.csv`
(every run, every result) for full detail.

## Section 1 — What was conclusively established

1. **Paper's ~1 pb is the fiducial cross section** for p p → Z(→νν)γj,
   AFTER MET>200 GeV and photon pT>0.5 GeV cuts, generated with
   "MadGraph5 aMC@NLO" (Sec III D). Conversion probability (→~10 fb) is
   a separate subsequent factor.

2. **Photon-pT-cut selection-stage mismatch: RULED OUT.** The baseline
   0.2311 pb figure lacked the paper's photon-pT>0.5 GeV cut at
   generation (`ptgmin=0.0`). A new controlled run with `ptgmin=0.5`
   (fresh seed, otherwise identical cards) gave **0.2307 ± 0.00098 pb**
   — statistically indistinguishable from baseline. Effect: <0.2%.

3. **Run-to-run reproducibility spread: DIAGNOSED, not a cause.** The
   project's 5 pre-existing identical-card runs spanned 0.2225–0.3057
   pb. Investigating this directly (3 new independent-seed reruns plus
   the scan_D pilot): 8 of 9 total runs (run_01–04, scan_D, and 3 new
   repro runs) are mutually consistent — inverse-variance-weighted mean
   **0.2300 ± 0.00054 pb**, reduced χ²≈3.5 (quoted per-run statistical
   errors mildly underestimate true grid-to-grid scatter, roughly 1.5–2×,
   a known VEGAS-reseeding effect). **run_05 (0.3057 pb) is a genuine
   ~21-combined-sigma outlier** — traced to its own low-statistics (300
   event) survey producing an under-converged integration grid for that
   particular random seed, not evidence of a generally unreliable setup.
   run_05 should be excluded from any authoritative average.

4. **PDF set: RULED OUT as a major cause.** cteq6l1 vs the baseline's
   nn23lo1: **0.2241 ± 0.0053 pb** — consistent with baseline within ~1σ.
   (Caveat: LHAPDF itself is not installed on this machine, so only
   MadGraph's small set of internally-compiled PDF tables could be
   tested — a modern PDF set like NNPDF3.1/4.0 was not accessible.)

5. **Scale variation: RULED OUT as sufficient.** Full 0.5×–2× band:
   **0.2592 ± 0.0073 pb (0.5×)** to **0.1858 ± 0.0052 pb (2×)** — a
   factor of ~1.4 spread, in the physically expected direction, typical
   LO scale uncertainty. Far short of the needed ×4.3.

6. **Jet-pT technical cut (20→40 GeV): RULED OUT as sufficient.**
   **0.2141 ± 0.0049 pb**, a modest −7% effect. (Paper doesn't state its
   own value for this technical cut, so this only bounds sensitivity.)

7. **NLO compilation blocker: ROOT-CAUSED AND FIXED.** The pre-existing
   failed NLO attempt (found on disk, dated before this audit) died
   because MG5's own bundled FastJet library never actually built
   (silent failure in its installer, masked by MG5 not checking the
   build's exit code — a `__TMC_END__` conda-GCC/libtool shared-library
   incompatibility). Repaired via a disposable **static** FastJet build
   (`--disable-shared`, sidesteps the broken shared-library link path
   entirely) plus fixing a second, independent, unrelated missing
   `LD_LIBRARY_PATH` entry for `libninja.so.0` (the file existed all
   along; this was purely an environment-variable gap, not a build
   failure). With both fixes, a fresh NLO process directory compiled
   **cleanly** — all 4 subprocess channels passed `test_ME`, `test_MC`,
   and `check_poles` (FKS pole cancellation confirmed to 1e-5 tolerance).
   **This is a genuine, reproducible technical fix**, confined entirely
   to disposable directories, with no change to the authoritative
   MadGraph installation or the original failed attempt (both preserved
   unmodified).

8. **The resulting NLO number is NOT paper-comparable.** The pilot's
   process (`p p > z a [QCD]`, matching the original failed attempt)
   leaves the Z boson **undecayed** — no Z→νν branching ratio, no MET
   cut possible (this NLO run_card template has no `misset` parameter at
   all). Result: **1175 ± 16 pb**, the fully inclusive Zγ(+jet) NLO cross
   section — a ~5000× difference from the LO baseline for structural
   reasons (missing BR and missing MET cut), not a K-factor. **A genuine
   paper-comparable NLO K-factor was not obtained** — it would require
   adding the Z→νν decay (via MadSpin or an inline NLO decay chain) plus
   reintroducing the MET cut, which was not attempted this session.

## Section 2 — Answers to the 10 required questions

1. **Is 0.23 pb correct for the current process definition?** Yes,
   independently reproduced multiple times (weighted mean 0.2300 ±
   0.00054 pb across 8 consistent runs).
2. **Is the paper's ~1 pb the same observable?** As far as could be
   tested, yes on process/MET/photon-pT-cut. PDF, scale, and jet-cut
   choices were tested and found not to explain the gap. LO-vs-NLO
   remains the one dimension where the paper text is genuinely ambiguous
   and where a real, working NLO computation now exists but hasn't yet
   been made decay-chain-comparable.
3. **Which single setting causes the largest justified increase?**
   Among factors actually tested: halving the scale (+12.7%, to 0.2592
   pb) was the largest. None came close to the needed factor of 4.3.
4. **How much does each tested setting change the cross section?**
   Photon-pT cut: −0.2% (not significant). PDF (cteq6l1): −2.6%. Scale
   0.5×: +12.7%. Scale 2×: −19.2%. Jet-pT 40 GeV: −6.9%. All small,
   all far short of the needed gap.
5. **Can a paper-compatible setup reach ~1 pb without unjustified
   tuning?** Not with any single factor tested. Combining all of them in
   the "generous" direction (loosest scale, PDF, and cut choices found)
   would still fall well short of 1 pb — this was not explicitly run as
   a combined "closest compatible" configuration, but the individual
   magnitudes make it implausible that it would close a 4.3× gap.
6. **If not, what residual difference remains and its likely cause?**
   The most plausible remaining candidate is genuine NLO accuracy
   (properly decay-chained and MET-cut), still untested. A typical
   Zγ+jet K-factor (~1.3–1.6×) would not alone close a 4.3× gap either,
   so even a full NLO computation may not fully resolve this — a
   possibility this report does not rule out.
7. **Does the paper use LO/NLO/K-factor/undocumented normalization?**
   Still cannot be determined from paper text alone. The tool name
   ("MadGraph5 aMC@NLO") remains ambiguous — this project's own LO runs
   use the identical banner name.
8. **What cross-section/weight should the project use?** Continue using
   **0.2300 ± 0.00054 pb** (the 8-run weighted mean, excluding the
   demonstrated run_05 outlier) as the best current estimate of this
   project's LO, cut-matched cross section. This is very close to the
   previously-cited 0.2311 pb; no numerically significant change.
9. **Which existing PPT/report statements need correction?** (a) Any
   statement treating "~0.23 pb" as bit-precise should note the true
   run-to-run scatter is ±~0.03 pb (1σ) once grid non-convergence is
   accounted for; (b) any statement implying the photon-pT cut was
   already included in that number should be corrected (it wasn't,
   though the numerical impact is negligible); (c) run_05's 0.3057 pb
   should not be cited as an equally-valid alternative baseline — it is
   a demonstrated non-convergence outlier.
10. **Does any finding change the converted-photon background verdict?**
    No discrete verdict changes. The corrected baseline (0.2300 pb) is
    numerically indistinguishable from what was already used downstream.

## Section 3 — What remains open

- A genuine paper-comparable NLO K-factor (Z→νν decay + MET cut, on top
  of the now-working NLO compile) — the single most promising remaining
  lever, not completed this session.
- Inclusive Zγ (no `+j`) vs Zγ+j comparison, ΔR cuts, coupling-order
  restrictions, generator-version differences, and a combined "closest
  paper-compatible configuration" run — not attempted this session.
- Whether the paper used a merged/matched multi-jet-multiplicity sample
  (would inflate its inclusive rate relative to this project's single
  "≥1 hard parton" sample) — remains an untested INFERENCE-level
  hypothesis.

## Section 4 — Recommendation

The NLO toolchain is now demonstrably working on this machine (a
concrete, reusable fix for any future NLO need in this project). The
highest-value next step is adding the Z→νν decay chain to the now-working
NLO setup and re-testing with the MET cut, to get the first genuinely
paper-comparable NLO/LO K-factor. This was not completed here due to the
time already invested across both audit sessions, and is left as an
explicit next step rather than a silent continuation.
