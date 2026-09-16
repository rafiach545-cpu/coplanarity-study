"""
Phase 1: Pythia8-aware primary/secondary classifier per ref[33]'s definition
(ATL-PHYS-PUB-2015-051, p.5, verbatim):

  "Primary charged particles are defined as charged particles with a mean
  lifetime tau > 300 ps, either directly produced in proton-proton
  interactions or from decays of directly produced particles with mean
  lifetime tau < 30 ps. Particles produced from decays of particles with
  tau > 30 ps are denoted secondary particles and are excluded."

BUG FOUND AND FIXED HERE (2026-09-16 re-audit, Phase 1): a naive single-
mother chain walk that treats "len(motherList())>1" as inherently ambiguous
classified ~90% of charged final-state minbias particles as "ambiguous".
Root cause: Pythia8's mother1/mother2 for a hadronization product (status
71-89) index into a RANGE of the fragmenting string's constituent PARTONS
(quarks/gluons/diquarks), not into two independent physical parent
particles -- this is internal shower/string bookkeeping, not a decay
relationship ref[33]'s definition is talking about at all. Partons have no
macroscopic proper lifetime in the sense tau>30ps/300ps refers to.

FIX: walk the mother chain, but classify the boundary correctly:
  - If the current ancestor is a PARTON (isParton()==True: quark, gluon,
    diquark) or has no mothers at all, the chain has reached "directly
    produced in the pp interaction" with no intervening long-lived HADRON
    decay -- PRIMARY. (Multiple "mothers" at this level are shower/string
    bookkeeping, not decay ambiguity, and are not walked further.)
  - If the current ancestor is a HADRON with tau0 > 30ps, ref[33]'s
    definition draws the line HERE: the ORIGINAL particle is a decay
    product of something too long-lived to be "directly produced" ->
    SECONDARY.
  - If the current ancestor is a HADRON with tau0 <= 30ps, continue
    walking up via ITS single mother (hadron-to-hadron decay chains are
    expected to be single-mother; a genuine multi-mother HADRON decay
    ancestor, if ever encountered, is reported as 'ambiguous' rather than
    guessed).
"""
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from generate_minbias import make_pythia

C_MM_PER_PS = 2.99792458e8 * 1e-12 * 1e3  # speed of light, mm/ps
TAU0_300PS_MM = 300.0 * C_MM_PER_PS   # ~89.94 mm
TAU0_30PS_MM = 30.0 * C_MM_PER_PS     # ~8.994 mm


def classify_particle(event, idx, max_depth=100):
    """
    Returns (label, reason) where label in {'primary', 'secondary', 'ambiguous'}.
    idx: the FINAL charged particle's own index in `event`.
    """
    prt = event[idx]
    cur_idx = idx
    depth = 0
    while depth < max_depth:
        cur = event[cur_idx]
        if depth == 0:
            # Start the walk from the particle's own mother(s), not itself
            # (ref[33]'s tau condition on the particle ITSELF only matters
            # for whether it is even "a primary charged particle" once
            # already classified via its production chain below -- the
            # definition's operative branch point is the PARENT's tau).
            mothers = cur.motherList()
            if len(mothers) == 0:
                return "primary", "no mothers (directly from beam/hard process)"
            if len(mothers) == 1:
                cur_idx = mothers[0]
                depth += 1
                continue
            # Multiple mothers directly on the tracked particle itself:
            # check if they are partons (shower/string bookkeeping) or
            # genuine multi-parent hadron history.
            m_objs = [event[m] for m in mothers]
            if all(m.isParton() for m in m_objs):
                return "primary", f"direct mothers are partons (string/shower bookkeeping): {mothers}"
            return "ambiguous", f"multiple non-parton mothers on the tracked particle: {mothers}"

        # depth >= 1: `cur` is an ancestor already reached via a single-mother step.
        if cur.isParton():
            return "primary", f"reached a parton ancestor (index {cur_idx}) with no long-lived hadron decay in between"
        if cur.isHadron():
            if cur.tau0() > TAU0_30PS_MM:
                return "secondary", f"hadron ancestor (index {cur_idx}, id={cur.id()}, tau0={cur.tau0():.4f}mm > 30ps threshold {TAU0_30PS_MM:.4f}mm)"
            # tau0 <= 30ps hadron: continue walking up.
            mothers = cur.motherList()
            if len(mothers) == 0:
                return "primary", f"short-lived hadron ancestor (index {cur_idx}) traced to no further mothers"
            if len(mothers) == 1:
                cur_idx = mothers[0]
                depth += 1
                continue
            m_objs = [event[m] for m in mothers]
            if all(m.isParton() for m in m_objs):
                return "primary", f"short-lived hadron ancestor's mothers are partons: {mothers}"
            return "ambiguous", f"short-lived hadron ancestor (index {cur_idx}) has multiple non-parton mothers: {mothers}"
        # Neither parton nor hadron (e.g. a lepton/photon ancestor) -- walk
        # its single mother if unambiguous, else flag.
        mothers = cur.motherList()
        if len(mothers) == 0:
            return "primary", f"non-hadron non-parton ancestor (index {cur_idx}, id={cur.id()}) with no further mothers"
        if len(mothers) == 1:
            cur_idx = mothers[0]
            depth += 1
            continue
        return "ambiguous", f"non-hadron non-parton ancestor (index {cur_idx}) has multiple mothers: {mothers}"

    return "ambiguous", f"chain walk exceeded max_depth={max_depth}"


if __name__ == "__main__":
    from collections import Counter

    seed = 20260916
    pythia, version = make_pythia(seed, 13000.0)
    print(f"Pythia version: {version}")

    n_events = 20
    counts = Counter()
    examples = {"primary": [], "secondary": [], "ambiguous": []}
    total_charged_final = 0

    for iev in range(n_events):
        if not pythia.next():
            continue
        event = pythia.event
        for prt in event:
            if not prt.isFinal() or prt.charge() == 0:
                continue
            total_charged_final += 1
            label, reason = classify_particle(event, prt.index())
            counts[label] += 1
            if len(examples[label]) < 3:
                examples[label].append((iev, prt.index(), prt.id(), prt.name(), reason[:180]))

    print(f"\nn_events={n_events}, total charged final-state particles={total_charged_final}")
    for k in ("primary", "secondary", "ambiguous"):
        v = counts[k]
        frac = v / total_charged_final if total_charged_final else float("nan")
        print(f"  {k}: {v} ({frac:.4f})")
    print("\nExample cases:")
    for k, exs in examples.items():
        print(f"  {k}:")
        for ex in exs:
            print(f"    {ex}")
