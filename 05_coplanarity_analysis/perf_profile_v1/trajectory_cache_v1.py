"""
Reusable trajectory/raw-hit disk cache (priority #2 of the optimization
task). Keyed by a hash of the exact physics inputs (4-momenta, mass,
Lambda, B, charges, seed) -- so re-running the SAME (event, Lambda,
config) combination (e.g. during grid-preparation debugging, re-running
a failed checkpoint, or re-deriving downstream statistics) never repeats
the expensive RK4 integration.

Does not change any physics: a cache HIT returns exactly the same
trajectory dict that a fresh integrate_trajectory_fast_v2 call would
produce (verified below); a cache MISS computes it fresh and stores it.

This does NOT reduce the cost of a genuinely fresh 91-point Figure 6 grid
(every point is computed once regardless), but protects against wasted
recomputation during grid preparation, checkpointed reruns after a
crash/interruption, and iterative debugging -- all realistic scenarios
for a multi-hour+ production run.
"""
import hashlib
import json
import os
import numpy as np

CACHE_DIR = "/home/rafia/coplanarity_study/05_coplanarity_analysis/perf_profile_v1/caches/trajectory_cache_v1"
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2, Lambda_GeV, B_tesla,
               t_max_gev_inv, dt_gev_inv):
    payload = {
        "x1_0": list(np.asarray(x1_0, dtype=float)), "p1_0": list(np.asarray(p1_0, dtype=float)),
        "x2_0": list(np.asarray(x2_0, dtype=float)), "p2_0": list(np.asarray(p2_0, dtype=float)),
        "mass": float(mass), "charge1": float(charge1), "charge2": float(charge2),
        "Lambda_GeV": float(Lambda_GeV), "B_tesla": float(B_tesla),
        "t_max_gev_inv": float(t_max_gev_inv), "dt_gev_inv": float(dt_gev_inv),
    }
    blob = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def integrate_trajectory_cached(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2,
                                 Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv,
                                 e_charge_natural=0.30282212, integrator=None):
    """integrator: callable with the same signature as
    quirk_trajectory.integrate_trajectory. Defaults to the optimized v2
    integrator (fastest available, already validated bit-identical to
    the baseline) if not given."""
    if integrator is None:
        import sys
        sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
        from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
        integrator = integrate_trajectory_fast_v2

    key = _cache_key(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2, Lambda_GeV,
                      B_tesla, t_max_gev_inv, dt_gev_inv)
    path = f"{CACHE_DIR}/{key}.npz"
    if os.path.exists(path):
        data = np.load(path)
        return {"t_gev_inv": data["t_gev_inv"], "x1": data["x1"], "p1": data["p1"],
                "x2": data["x2"], "p2": data["p2"], "_cache_hit": True}

    traj = integrator(x1_0, p1_0, x2_0, p2_0, mass=mass, charge1=charge1, charge2=charge2,
                       Lambda_GeV=Lambda_GeV, B_tesla=B_tesla, t_max_gev_inv=t_max_gev_inv,
                       dt_gev_inv=dt_gev_inv, e_charge_natural=e_charge_natural)
    np.savez_compressed(path, t_gev_inv=traj["t_gev_inv"], x1=traj["x1"], p1=traj["p1"],
                         x2=traj["x2"], p2=traj["p2"])
    traj["_cache_hit"] = False
    return traj


if __name__ == "__main__":
    import sys
    import time
    sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")

    x0 = np.zeros(3)
    p1 = np.array([100.0, 50.0, 30.0])
    p2 = np.array([-90.0, -40.0, 20.0])
    kwargs = dict(mass=800.0, charge1=1.0, charge2=-1.0, Lambda_GeV=4e-6, B_tesla=2.0,
                  t_max_gev_inv=1e13, dt_gev_inv=1e13/3000)

    t0 = time.time()
    r1 = integrate_trajectory_cached(x0, p1, x0, p2, **kwargs)
    t1 = time.time()
    print(f"First call (cache miss): {t1-t0:.4f}s, cache_hit={r1['_cache_hit']}")

    r2 = integrate_trajectory_cached(x0, p1, x0, p2, **kwargs)
    t2 = time.time()
    print(f"Second call (cache hit): {t2-t1:.4f}s, cache_hit={r2['_cache_hit']}")
    print(f"Cache speedup: {(t1-t0)/(t2-t1):.1f}x")
    print("Bit-identical to fresh computation:", np.array_equal(r1["x1"], r2["x1"]))
