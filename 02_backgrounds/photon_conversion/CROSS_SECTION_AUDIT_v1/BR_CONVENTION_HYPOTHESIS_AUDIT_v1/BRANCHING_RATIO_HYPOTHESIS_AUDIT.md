# Branching-Ratio Convention Hypothesis — Disproof-Seeking Audit

**Read-only.** No new simulation run, no existing file modified, nothing
committed/pushed. This audit evaluates a specific hypothesis raised
against the already-completed `CROSS_SECTION_AUDIT_v1` work: that the
paper's "~1 pb" and the project's "~0.23 pb" are not really in tension,
but are the *same underlying number* quoted at two different stages
(before vs after applying BR(Z→νν̄)).

## Final classification: **DISPROVED** (on preponderance of evidence, not absolute certainty)

The hypothesis does not survive scrutiny of the paper's own text and a
structural technical fact about how MET cuts require a decayed final
state. It is disproved with moderate-to-high confidence, not 100%
certainty — see §8 for the residual uncertainty that is honestly kept
open.

---

## 1–2. The exact paper text, quoted with location

arXiv:1708.02243v2, Sec. III D, page 6→7 of the extracted text
(`paper.txt` lines 682–702; this is the same passage already quoted in
`../metadata/PAPER_CROSS_SECTION_DEFINITION.md` §1, reread in full again
for this audit):

> "A second potential background arises from isolated photon conversions
> in the beam pipe. These conversions give rise to a fairly collimated
> e+e− pair, which results in a nearby pair of hits in each layer of the
> tracker. For some conversion events, these hits could all approximately
> lie on a plane, and thus fake a quirk signal. **We model this
> background by generating a Z+γ+j sample with MadGraph5 aMC@NLO, where
> we decay the Z to neutrinos and require at least 200 GeV of MET**, to
> satisfy our trigger requirement. We further require the pT of the
> photon be larger than 0.5 GeV. **The fiducial cross section for this
> process is ∼1 pb**, which drops to ∼10 fb if we require that the
> photon converts in the beampipe using the conversion probability from
> figures 33.16 and 33.17 of [35]."

A full-text search of the entire paper (`grep -in "branching\|MadSpin\|
invisible\|stable\|on-shell\|Z boson\|BR("`) turns up **no other mention**
anywhere in the paper of a branching ratio, MadSpin, an "invisible Z", or
a "stable"/"on-shell" Z. This single paragraph is the *only* place the
paper discusses this background's generation or normalization.

## 3. Does the paper unambiguously state whether ~1 pb includes BR(Z→νν)?

**Not with an explicit, separate statement — but the grammar of the
passage strongly implies it does.** The sentence structure is:

"generating a **Z+γ+j sample** ... **where we decay the Z to neutrinos**
and require ... MET ... [and] pT(γ)>0.5 GeV. The fiducial cross section
for **this process** is ∼1 pb."

"This process" is a backward-referring noun phrase whose antecedent is
the *entire* process just described in the preceding sentence — a
process that explicitly includes "we decay the Z to neutrinos" as one of
its defining steps, on equal footing with the MET and photon-pT cuts.
There is no textual signal (no "before applying the decay", no "at the
production level", no footnote) suggesting the quoted number is for an
earlier, un-decayed stage. Read plainly, **(a) the paper states ~1 pb
includes BR(Z→νν̄)** — this is the most natural reading, though it is an
inference from grammar and phrasing, not a numerically explicit
statement (e.g. the paper never writes "including the branching ratio"
in so many words). Classified: **(a), with moderate-high confidence, not
(c) fully ambiguous** — see §8 for why this isn't pushed to 100%.

## 4. Does the paper specify the decay implementation (inline ME, MadSpin, or unspecified)?

**Unspecified — genuinely UNAVAILABLE from the text.** The paper says
only "we decay the Z to neutrinos"; it does not say whether this was
done via an inline matrix-element-level decay (`generate p p > z a j,
z > vl vl~`, i.e. exactly this project's own LO card), via MadSpin
applied to a stable-Z sample, or via Pythia8's own Z-decay routines
during showering. No sentence in the paper distinguishes between these.

## 5. MadGraph/MadSpin cross-section conventions (explained, not assumed)

- **Inline decay in the `generate` command** (`p p > z a j, z > vl vl~`,
  matching this project's own baseline card exactly): MadGraph computes
  the full matrix element for the specified final state directly. The
  Z propagator's correct partial width for the ν̄ν channel is built into
  the amplitude. The cross section MadGraph reports (survey/refine,
  `results.dat`, the `crossx.html` summary) for this process **is
  already the physical, decay-inclusive cross section** — there is no
  separate BR multiplication step; it is not possible to "forget" to
  apply the BR in this mode because it was never a separate factor to
  begin with.
- **Stable/on-shell Z, decayed afterward via MadSpin**: MadGraph
  generates `p p > z a j` with the Z kept as a final-state particle. The
  production banner (and `results.dat`) for *that* run reports the
  **stable-Z cross section**, which is the cross section for producing a
  Z boson of any decay mode (i.e., effectively "BR=1" for "some Z"). If
  MadSpin is then run as a distinct subsequent step to decay the Z to
  neutrinos, MadSpin performs a spin-correlated decay and reweights
  events; for a narrow resonance like the Z (Γ_Z/M_Z ≈ 2.7%, narrow-width
  approximation excellent), the number of surviving/decayed events
  divided by the original count converges to BR(Z→ chosen channel) to
  very good approximation. **Critically: MadSpin's own decay-efficiency
  report is typically written to its own log file, separate from the
  original production run's banner/`results.dat`.** In practice, this
  creates a well-known opportunity for user error: someone citing "the
  cross section" for a MadSpin-decayed sample can, if they are not
  careful, read off the *original stable-Z production banner's* number
  rather than the MadSpin-adjusted one — because the original
  production banner is not automatically updated or overwritten by the
  MadSpin step. This exact failure mode is the mechanism the hypothesis
  under test proposes.
- **Which number is physically correct for the neutrino-final-state
  background?** Unambiguously the **decay-inclusive** number in both
  cases above. A stable-Z cross section describes producing *a Z boson
  of any kind*; only ~20% of those Z bosons decay invisibly and can
  contribute genuine missing transverse energy that fakes a quirk MET
  trigger. Using the stable-Z number as the background rate would
  overcount the true physical background by a factor of ≈1/BR ≈ 5.

## 6. Numerical comparison

| Quantity | Value | Source |
|---|---|---|
| New stable-Z (undecayed) LO pilot, paper's cuts (MET n/a for undecayed Z, ptgmin=0.5, ptj/etaj as this project's baseline) | **1.133 ± 0.018 pb** | user-supplied new controlled result (this task) |
| BR(Z→ all three ν flavours), PDG SM value | **0.1997 ± 0.0003** (Γ_inv/Γ_Z, PDG) ≈ 0.20 used here | PDG world average (not independently re-derived here; standard textbook/PDG value) |
| Stable-Z × BR (decay-inclusive, computed) | **1.133 × 0.1997 ≈ 0.2263 pb** | derived |
| Project's existing decay-inclusive LO baseline (this project's own MG5 card, inline `z > vl vl~` decay, same cuts) | **0.2300 ± 0.00054 pb** (weighted mean, `CROSS_SECTION_AUDIT_v1/tables/cross_section_scan_full.csv`) | this project, independently generated |
| Agreement: stable-Z×BR vs project's own decay-inclusive number | **0.2263 vs 0.2300 pb → 1.6% difference**, well within combined statistical/systematic uncertainty | strong, expected agreement (this is exactly what NWA physics predicts — not surprising, and not itself evidence either for or against the paper hypothesis, since both numbers come from this project's own generator) |
| Paper's quoted fiducial cross section | **∼1 pb** (order-of-magnitude, "∼" symbol, no error bar given) | direct quote, Sec III D |
| Stable-Z (1.133 pb) vs paper's "∼1 pb" | **close, within the paper's own loose "∼" rounding** | numerically suggestive, see §8 |
| Project's decay-inclusive (0.2300 pb) vs paper's "∼1 pb" | **factor ≈4.35 apart** | the original, still-open discrepancy |

The stable-Z×BR arithmetic is internally consistent and unsurprising —
it simply confirms the narrow-width approximation works as expected on
this project's own numbers. It does **not**, by itself, tell us which
number the paper intended; that determination rests on §3 and §7 below.

## 7. Where should the 1% conversion probability be applied?

**Structural argument, not paper-text-dependent:** photon-conversion
probability is a property of a real photon in a real event that
*already satisfies the signal-mimicking topology* (Z decayed invisibly,
so the event has genuine MET, matching the actual trigger/background
definition). Applying the conversion probability to the **stable-Z**
number would include the ~80% of Z bosons that do *not* decay invisibly
— i.e., events with no genuine missing energy, which by construction
cannot fake the quirk trigger signature this background is modeling.
**The conversion probability must be applied to the decay-inclusive
cross section (≈0.227–0.230 pb in this project's numbers), never to the
stable-Z number (1.133 pb), regardless of which convention the paper's
own quoted figures use.** This is true independent of how the paper's
"~1 pb → ~10 fb" figures were internally computed — if the paper did
apply its 1% conversion probability to a stable-Z number, that would be
a physics error in the paper's own background estimate (see §8), not a
justification for this project to do the same.

**Does the paper's own "~1 pb → ~10 fb via ~1% conversion probability"
arithmetic discriminate between the two scenarios?** Checked explicitly:
it does **not**, because the ~1% factor is applied consistently in both
scenarios (whether "~1 pb" is stable-Z or decay-inclusive, multiplying
by ~1% reproduces "~10 fb" either way: 1.133 pb × 1% ≈ 11.3 fb ≈ "~10 fb",
and a hypothetical true decay-inclusive ~1 pb × 1% = 10 fb exactly). This
specific ratio is therefore **not usable evidence either way** — it was
checked and found non-discriminating, not silently assumed to support
either side.

## 8. Actively seeking evidence against the hypothesis (as instructed)

**The strongest disproof found is structural, not textual, and comes
from this project's own first-hand experience this session, not
assumption:**

While repairing this project's NLO toolchain (`../metadata/
NLO_REPAIR_ATTEMPT.md`), a fresh MadGraph process directory was
generated for the **undecayed, stable-Z** process `p p > z a [QCD]`
(same structural process as the "stable-Z" pilot referenced in this
hypothesis). Direct inspection of that process's own `run_card.dat`
template showed **no `misset` (MET) parameter exists at all** for the
undecayed-Z process — confirmed by `grep -n "misset" run_card.dat`
returning zero matches. This is not a paper-specific claim; it is a
structural fact about how MadGraph defines missing-transverse-energy
cuts: `misset` is computed from the vector sum of particles flagged as
invisible in the model (neutrinos, PDG 12/14/16), evaluated **at the
generated final state**. If the Z is left undecayed, no neutrinos exist
in the generated final state at all, so there is nothing for a MET cut
to act on — MadGraph's own run_card generator does not even offer the
option.

**The paper explicitly states it "require[s] at least 200 GeV of MET"
as part of the same process whose cross section is quoted as ~1 pb.**
For that cut to be applicable and meaningful at all, the Z **must**
already have been decayed to neutrinos in the generated sample before
the cross section was computed and the cut applied. This is a
structural necessity, not an inference from ambiguous wording — it
directly disproves the possibility that "this process" (to which the
MET cut and the ~1 pb figure both refer) is the stable, undecayed Z
process.

**Weighed against this:** the numerical closeness of 1.133 pb to "~1 pb"
is real and should not be dismissed as pure coincidence without comment.
However, "~1 pb" is an order-of-magnitude, unit-precision figure (no
decimal places, no quoted uncertainty) in the paper — many cross
sections for SM electroweak+jet processes at 13 TeV with O(GeV)-scale
cuts naturally fall in the 0.1–few pb range, so a match at this precision
is less improbable, and less diagnostic, than it might first appear.

## 9. Final classification

**DISPROVED**, with the following honesty about residual uncertainty:

- The disproof rests on (a) the grammatical antecedent of "this process"
  in the paper's own sentence, and (b) the structural fact that a MET
  cut cannot be meaningfully defined or applied without a decayed final
  state, independently confirmed via this project's own MadGraph
  experience this session. Both point the same direction.
- It is not pushed to 100% certainty because: the paper never uses the
  word "branching" or otherwise explicitly confirms the BR was applied;
  it is conceivable (though not evidenced) that the paper's authors
  described their pipeline narratively (mentioning the neutrino decay as
  part of the physical picture) while separately quoting a cross section
  drawn from an earlier, un-decayed production step by oversight — the
  exact MadSpin-banner-confusion failure mode described in §5 is a real,
  documented way this class of error happens in practice, and cannot be
  ruled out from text alone.
- Per the explicit instruction not to claim NLO explains the discrepancy
  until the BR-convention hypothesis was first ruled out: **that
  requirement is now satisfied.** This audit disproves the BR-labeling
  explanation (on preponderance of evidence), which means the original,
  still-unresolved ≈4.3× gap between the paper's ~1 pb and this
  project's ≈0.23 pb (both now understood to be decay-inclusive,
  cut-matched, fiducial cross sections) **remains open**, and the
  previously-identified NLO-accuracy question (`../metadata/
  NLO_REPAIR_ATTEMPT.md`) is reinstated as the leading untested
  candidate — not proven, but no longer preemptively dismissed by an
  easier labeling explanation, and no longer blocked by the BR question
  either.

## What this audit did NOT do (explicitly, per instructions)

No new MadGraph run was launched. No existing file in this project was
modified. Nothing was committed or pushed. Figure 6 was not touched. The
fresh 2000+2000 quirk regeneration directory was not touched. The
"1.133 ± 0.018 pb" stable-Z number was supplied by the user's message and
is treated here as an input to be reasoned about, not independently
re-verified by rerunning it (that would have required a new simulation,
which this audit was explicitly instructed not to run).
