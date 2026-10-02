"""
Bounded diagnostic replay of the 31 EW-2000 trigger-passing, fiducial-
failing, ZERO-hit, MODERATE-truth-eta (<=1.6) events. Deterministic,
stored seeds and stored truth 4-momenta -- NOT new event generation, NOT
a parameter scan. Calls only the existing, validated, unmodified
physics code (simulate_quirk_hits / find_layer_crossing /
integrate_trajectory_fast_v2) and inspects its full returned arrays for
diagnostics that the production pipeline itself does not persist.
"""
import sys, signal, time, json
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
import trajectory_to_hits as tth
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
tth.integrate_trajectory = integrate_trajectory_fast_v2
from atlas_geometry import LAYERS, FIDUCIAL_ETA_MAX

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/ZERO_HIT_REPLAY"
CM_PER_NATURAL = 1.973269804e-14


class TimeoutErr(Exception):
    pass


def _handler(signum, frame):
    raise TimeoutErr()


signal.signal(signal.SIGALRM, _handler)


def eta_from_theta(theta):
    return -np.log(np.tan(theta / 2.0)) if 0 < theta < np.pi else 0.0


def instrument_event(event_idx, seed, p1_gev, p2_gev, charge1, charge2, timeout_s=150):
    signal.alarm(timeout_s)
    t0 = time.time()
    status = "ok"
    err = None
    try:
        rng = np.random.default_rng(seed)
        hits, traj = tth.simulate_quirk_hits(
            p1_gev, p2_gev, mass_gev=800.0, Lambda_gev=4e-6, B_tesla=2.0,
            charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0)
    except TimeoutErr:
        signal.alarm(0)
        return {"event_idx": event_idx, "status": "TIMEOUT", "wall_s": time.time() - t0}
    except RuntimeError as e:
        signal.alarm(0)
        return {"event_idx": event_idx, "status": "RUNTIME_ERROR", "error": str(e), "wall_s": time.time() - t0}
    except Exception as e:
        signal.alarm(0)
        return {"event_idx": event_idx, "status": "OTHER_EXCEPTION", "error": f"{type(e).__name__}: {e}", "wall_s": time.time() - t0}
    signal.alarm(0)
    wall = time.time() - t0

    x1_cm = traj["x1"] * CM_PER_NATURAL
    x2_cm = traj["x2"] * CM_PER_NATURAL
    t_gev_inv = traj["t_gev_inv"]
    p1_arr = traj["p1"]
    p2_arr = traj["p2"]

    r1 = np.hypot(x1_cm[:, 0], x1_cm[:, 1])
    r2 = np.hypot(x2_cm[:, 0], x2_cm[:, 1])
    z1 = x1_cm[:, 2]
    z2 = x2_cm[:, 2]
    E1_arr = np.sqrt(np.sum(p1_arr**2, axis=1) + 800.0**2)
    E2_arr = np.sqrt(np.sum(p2_arr**2, axis=1) + 800.0**2)
    beta1_arr = np.linalg.norm(p1_arr, axis=1) / E1_arr
    beta2_arr = np.linalg.norm(p2_arr, axis=1) / E2_arr

    n_prem = int(traj["n_hits_premerge"])
    max_hit_t_ns = traj["max_hit_t_ns_premerge"]

    # Reproduce the stored zero-hit decision exactly (verification step)
    reproduced_zero = (n_prem == 0)

    # Per-layer crossing attempt, per quirk, with rejection reason
    layer_crossings = []
    for quirk_i, (x_cm, r_arr) in enumerate([(x1_cm, r1), (x2_cm, r2)], start=1):
        for layer in LAYERS:
            result = tth.find_layer_crossing(x_cm, t_gev_inv, layer["r_cm"])
            if result is None:
                reached_max_r = float(r_arr.max())
                reason = "never_reached_radius" if reached_max_r < layer["r_cm"] else "geometry_edge_case"
                layer_crossings.append({
                    "event_idx": event_idx, "quirk_index": quirk_i, "layer": layer["name"],
                    "layer_r_cm": layer["r_cm"], "crossing_found": False,
                    "rejection_stage": "root_finding_no_crossing", "rejection_reason": reason,
                    "max_r_reached_this_layer_check_cm": reached_max_r,
                })
                continue
            hit_xyz, hit_t_ns = result
            hx, hy, hz = hit_xyz
            r_hit = np.hypot(hx, hy)
            eta_hit = eta_from_theta(np.arctan2(r_hit, hz)) if (hz != 0 or r_hit != 0) else 0.0
            eta_ok = abs(eta_hit) <= FIDUCIAL_ETA_MAX
            layer_crossings.append({
                "event_idx": event_idx, "quirk_index": quirk_i, "layer": layer["name"],
                "layer_r_cm": layer["r_cm"], "crossing_found": True,
                "hit_x_cm": hx, "hit_y_cm": hy, "hit_z_cm": hz, "hit_t_ns": hit_t_ns,
                "eta_at_crossing": eta_hit, "eta_cut_pass": eta_ok,
                "rejection_stage": None if eta_ok else "eta_cut",
                "rejection_reason": None if eta_ok else f"|eta|={abs(eta_hit):.3f} > {FIDUCIAL_ETA_MAX}",
            })

    # Truth eta vs trajectory direction near layer 1 (first ~50 steps, small-r regime)
    n_near = min(50, len(x1_cm))
    def direction_eta(x_cm_slice):
        if len(x_cm_slice) < 2:
            return float("nan")
        dx = x_cm_slice[-1] - x_cm_slice[0]
        r_d = np.hypot(dx[0], dx[1])
        return eta_from_theta(np.arctan2(r_d, dx[2])) if (dx[2] != 0 or r_d != 0) else float("nan")
    traj_dir_eta1_near_start = direction_eta(x1_cm[:n_near])
    traj_dir_eta2_near_start = direction_eta(x2_cm[:n_near])

    n_finite = int(np.sum(np.isfinite(x1_cm)) + np.sum(np.isfinite(x2_cm)))
    n_total_elems = x1_cm.size + x2_cm.size
    any_nonfinite = (n_finite != n_total_elems)

    summary = {
        "event_idx": event_idx, "status": status, "wall_s": wall,
        "n_steps": len(t_gev_inv), "t_max_gev_inv": float(t_gev_inv[-1]),
        "n_hits_premerge_reproduced": n_prem, "reproduced_zero_hit": reproduced_zero,
        "max_hit_t_ns_premerge": max_hit_t_ns if not (isinstance(max_hit_t_ns, float) and np.isnan(max_hit_t_ns)) else None,
        "max_r_q1_cm": float(r1.max()), "max_r_q2_cm": float(r2.max()),
        "max_abs_z_q1_cm": float(np.abs(z1).max()), "max_abs_z_q2_cm": float(np.abs(z2).max()),
        "min_beta_q1": float(beta1_arr.min()), "max_beta_q1": float(beta1_arr.max()),
        "min_beta_q2": float(beta2_arr.min()), "max_beta_q2": float(beta2_arr.max()),
        "layer1_r_cm": LAYERS[0]["r_cm"],
        "layer1_crossed_q1": bool(r1.max() >= LAYERS[0]["r_cm"]),
        "layer1_crossed_q2": bool(r2.max() >= LAYERS[0]["r_cm"]),
        "any_nonfinite_state": bool(any_nonfinite),
        "dt_diagnostics": traj.get("dt_diagnostics", {}),
        "traj_dir_eta1_near_start": traj_dir_eta1_near_start,
        "traj_dir_eta2_near_start": traj_dir_eta2_near_start,
        "r1_still_rising_at_end": bool(r1[-1] > r1[max(0, len(r1) - 20)]) if len(r1) > 20 else None,
        "r2_still_rising_at_end": bool(r2[-1] > r2[max(0, len(r2) - 20)]) if len(r2) > 20 else None,
    }
    return summary, layer_crossings


if __name__ == "__main__":
    targets = pd.read_csv(f"{OUT}/tables/target_event_list.csv")
    all_summaries = []
    all_crossings = []
    t0 = time.time()
    for _, row in targets.iterrows():
        eidx = int(row["event_idx"])
        p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
        p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
        res = instrument_event(eidx, int(row["seed"]), p1, p2, float(row["charge1"]), float(row["charge2"]))
        if isinstance(res, dict):  # error/timeout path
            all_summaries.append(res)
            print(f"event_idx={eidx}: {res['status']} ({res.get('wall_s', 0):.1f}s)", flush=True)
        else:
            summary, crossings = res
            all_summaries.append(summary)
            all_crossings.extend(crossings)
            print(f"event_idx={eidx}: reproduced_zero={summary['reproduced_zero_hit']} "
                  f"max_r_q1={summary['max_r_q1_cm']:.2f}cm max_r_q2={summary['max_r_q2_cm']:.2f}cm "
                  f"layer1_r={summary['layer1_r_cm']}cm wall={summary['wall_s']:.1f}s", flush=True)
        # checkpoint after every event
        pd.DataFrame(all_summaries).to_csv(f"{OUT}/tables/instrumented_replay_summary.csv", index=False)
        pd.DataFrame(all_crossings).to_csv(f"{OUT}/tables/layer_crossing_detail.csv", index=False)

    print(f"\nDONE. {len(all_summaries)}/{len(targets)} events processed in {time.time()-t0:.0f}s")
