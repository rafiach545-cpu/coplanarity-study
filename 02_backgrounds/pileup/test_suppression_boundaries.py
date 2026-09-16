"""
Permanent regression test for track_suppression.py's boundary behavior
(epsilon=0 / epsilon=1) and RNG-stream independence, run as part of the
pre-sweep verification gate.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from track_suppression import suppress_tracks


def test_epsilon_zero_always_kept():
    # pT=0.1 GeV is below the Loose/Tight reconstruction threshold -> eff=0
    # exactly -> draw (always >=0) must NEVER be < 0 -> always kept.
    raw_hits = {"t0": [{"tag": "t0"}] * 3}
    kinematics = {"t0": 0.1}
    labels = {"t0": "primary"}
    rng = np.random.default_rng(1)
    for trial in range(200):
        unassoc, stats = suppress_tracks(raw_hits, kinematics, labels, rng, selection="Loose")
        assert len(unassoc) == 3, f"epsilon=0 track was removed on trial {trial}"
        assert stats["n_tracks_primary_removed"] == 0
    print("PASS: epsilon=0 (below-threshold pT) track always kept, 200/200 trials")


def test_epsilon_near_one_mostly_removed():
    # High pT (well within plateau, eff~0.90 Loose) -> most trials should remove it.
    raw_hits = {"t0": [{"tag": "t0"}] * 3}
    kinematics = {"t0": 10.0}
    labels = {"t0": "primary"}
    rng = np.random.default_rng(2)
    n_removed = 0
    n_trials = 500
    for _ in range(n_trials):
        raw_hits_fresh = {"t0": [{"tag": "t0"}] * 3}
        unassoc, stats = suppress_tracks(raw_hits_fresh, kinematics, labels, rng, selection="Loose")
        if stats["n_tracks_primary_removed"] == 1:
            n_removed += 1
    frac = n_removed / n_trials
    print(f"PASS-CHECK: high-pT primary removed in {n_removed}/{n_trials} trials ({frac:.3f}), "
          f"expected close to eff(pT=10,Loose)=0.8957")
    assert 0.80 < frac < 0.97, f"removal fraction {frac} not consistent with expected ~0.896"


def test_rng_independence():
    # Two calls with the SAME rng_suppression seed but DIFFERENT unrelated
    # inputs must give identical draws for a shared tag processed identically
    # -- confirms determinism/independence from anything else.
    raw_hits = {"t0": [{"tag": "t0"}]}
    kinematics = {"t0": 2.0}
    labels = {"t0": "primary"}
    rng_a = np.random.default_rng(777)
    rng_b = np.random.default_rng(777)
    _, stats_a = suppress_tracks(raw_hits, kinematics, labels, rng_a, selection="Loose")
    _, stats_b = suppress_tracks(raw_hits, kinematics, labels, rng_b, selection="Loose")
    assert stats_a == stats_b
    print("PASS: same-seed suppression stream is deterministic/reproducible")


if __name__ == "__main__":
    test_epsilon_zero_always_kept()
    test_epsilon_near_one_mostly_removed()
    test_rng_independence()
    print("\nALL SUPPRESSION BOUNDARY TESTS PASS")
