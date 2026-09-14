"""
Stage 5: the coplanarity plane-fit, exactly as specified in Sec. III C of
arXiv:1708.02243 (Knapen, Lou, Papucci, Setford).

Given a set of hits {x_a} (3-vectors, cm, relative to the primary vertex),
build the tensor T_ij = (1/(N-1)) sum_a x_a_i x_a_j (Eq. 11), eigen-decompose:
  - smallest eigenvalue  -> Delta_s^2 ("thickness"),  eigenvector n1 (normal)
  - middle eigenvalue    -> Delta_w^2 ("width"),       eigenvector n2
  - largest eigenvalue   -> (unnamed),                 eigenvector n3 (flight dir)
"""

import numpy as np


def fit_plane(hits_xyz):
    """
    hits_xyz: (N,3) array of hit positions (cm), N >= 2.
    Returns dict with n1 (normal), n2, n3, delta_s, delta_w (cm).
    """
    x = np.asarray(hits_xyz, dtype=float)
    N = x.shape[0]
    if N < 2:
        raise ValueError("Need at least 2 hits to define a plane (paper Eq. 10-11).")

    T = (x.T @ x) / (N - 1)
    eigvals, eigvecs = np.linalg.eigh(T)  # ascending order
    # eigh returns ascending eigenvalues: [smallest, middle, largest]
    delta_s = np.sqrt(max(eigvals[0], 0.0))
    delta_w = np.sqrt(max(eigvals[1], 0.0))
    n1 = eigvecs[:, 0]
    n2 = eigvecs[:, 1]
    n3 = eigvecs[:, 2]

    # Orient n3 so that (x . n3) > 0 for the majority of hits (paper: "the
    # quirks signal we are after will lie in a positive direction").
    if np.mean(x @ n3) < 0:
        n3 = -n3

    return {"n1": n1, "n2": n2, "n3": n3,
            "delta_s": delta_s, "delta_w": delta_w,
            "eigvals": eigvals, "n_hits": N}


def project_hits(hits_xyz, fit):
    """Project hits onto the (n3, n2) plane for a Fig.-4-style display."""
    x = np.asarray(hits_xyz, dtype=float)
    proj_n3 = x @ fit["n3"]
    proj_n2 = x @ fit["n2"]
    return proj_n3, proj_n2


def seeding_and_iterative_fit(hits_by_layer, dphi_seed_max=0.1, dz_seed_max_cm=2.0,
                                ds_seed_max_cm=0.05, dw_seed_max_cm=1.0,
                                ds_iter_max_cm=0.05, dw_iter_max_cm=1.0,
                                growth_factor_max=3.0):
    """
    Full plane-finding algorithm, Sec III C:
      Seeding: layers 8 and 7 (outermost two), pairs of hits with
               Delta_phi < dphi_seed_max, Delta_z < dz_seed_max_cm.
               4-hit combinations (one pair per layer) must satisfy
               x.n3>0 for all hits, Delta_s < ds_seed_max_cm,
               Delta_w < dw_seed_max_cm.
      Iterative fit: layers 6 down to 1, outside-in, adding hits that
               satisfy (x.n3)>0, |x.n1|<0.05cm, |x.n2|<1cm, and that do not
               grow Delta_s or Delta_w by more than growth_factor_max.

    hits_by_layer: dict {layer_index (1-8): list of (x,y,z) hit tuples}.
    Returns list of candidate final hit-lists (each a list of (x,y,z)),
    one per surviving seed, plus their fit info.
    """
    def hit_dphi(h1, h2):
        phi1, phi2 = np.arctan2(h1[1], h1[0]), np.arctan2(h2[1], h2[0])
        d = abs(phi1 - phi2)
        return min(d, 2 * np.pi - d)

    layer8 = hits_by_layer.get(8, [])
    layer7 = hits_by_layer.get(7, [])

    pairs8 = [(a, b) for i, a in enumerate(layer8) for b in layer8[i + 1:]
              if hit_dphi(a, b) < dphi_seed_max and abs(a[2] - b[2]) < dz_seed_max_cm]
    pairs7 = [(a, b) for i, a in enumerate(layer7) for b in layer7[i + 1:]
              if hit_dphi(a, b) < dphi_seed_max and abs(a[2] - b[2]) < dz_seed_max_cm]

    # Track (hit, layer_index) pairs throughout so the final signal-region
    # per-layer hit-count cut (Sec IV, cut 2) can be checked on the actual
    # surviving candidate, not just assumed from the input hit counts.
    candidates = []
    for p8 in pairs8:
        for p7 in pairs7:
            seed_hits = list(p8) + list(p7)
            seed_layers = [8, 8, 7, 7]
            fit = fit_plane(np.array(seed_hits))
            if fit["delta_s"] >= ds_seed_max_cm:
                continue
            if fit["delta_w"] >= dw_seed_max_cm:
                continue
            x = np.array(seed_hits)
            if not np.all(x @ fit["n3"] > 0):
                continue
            candidates.append({"hits": seed_hits, "layers": seed_layers, "fit": fit})

    final_candidates = []
    for cand in candidates:
        current_hits = list(cand["hits"])
        current_layers = list(cand["layers"])
        for layer_idx in range(6, 0, -1):
            layer_hits = hits_by_layer.get(layer_idx, [])
            fit = fit_plane(np.array(current_hits))
            eligible = []
            for h in layer_hits:
                hv = np.array(h)
                if np.dot(hv, fit["n3"]) <= 0:
                    continue
                if abs(np.dot(hv, fit["n1"])) >= ds_iter_max_cm:
                    continue
                if abs(np.dot(hv, fit["n2"])) >= dw_iter_max_cm:
                    continue
                eligible.append((abs(np.dot(hv, fit["n1"])), h))
            eligible.sort(key=lambda t: t[0])
            for _, h in eligible:
                trial_hits = current_hits + [h]
                trial_fit = fit_plane(np.array(trial_hits))
                if (trial_fit["delta_s"] <= growth_factor_max * fit["delta_s"] and
                        trial_fit["delta_w"] <= growth_factor_max * fit["delta_w"]):
                    current_hits = trial_hits
                    current_layers.append(layer_idx)
                    fit = trial_fit
        final_fit = fit_plane(np.array(current_hits))
        final_candidates.append({"hits": current_hits, "layers": current_layers,
                                   "fit": final_fit})

    return final_candidates


def check_hit_multiplicity(layers, n_layers_total=8):
    """
    Sec IV, cut 2: "All but one layer must contain 2 hits, the remaining
    layer must contain at least 1 hit." Checked on the candidate's ACTUAL
    surviving hit list (the greedy iterative fit can drop hits, so this
    cannot be assumed just because the event started with 16 available
    hits -- must be checked on the final candidate).
    """
    from collections import Counter
    counts = Counter(layers)
    n_with_2plus = sum(1 for l in range(1, n_layers_total + 1) if counts.get(l, 0) >= 2)
    n_with_1plus = sum(1 for l in range(1, n_layers_total + 1) if counts.get(l, 0) >= 1)
    return n_with_2plus >= (n_layers_total - 1) and n_with_1plus == n_layers_total


def select_reconstructed_plane(candidates, dw_max_cm=1.0):
    """
    Sec III C, "Event Selection" (step 3), exactly as written: "Gather all
    the reconstructed lists, apply the final cut Delta_w < 1cm. If there
    are more than one plane identified, keep the one with the smallest
    Delta_s." This is the algorithm's OWN selection rule and collapses all
    raw seed-candidates down to at most one plane per event, BEFORE any
    Sec IV signal-region cut is even considered.

    Returns the single winning candidate dict, or None if no candidate has
    Delta_w < dw_max_cm.
    """
    surviving = [c for c in candidates if c["fit"]["delta_w"] < dw_max_cm]
    if not surviving:
        return None
    return min(surviving, key=lambda c: c["fit"]["delta_s"])


def apply_signal_region_cuts(candidates, dw_max_cm=1.0, ds_max_cm=0.01,
                               n_layers_total=8):
    """
    Sec IV signal-region cuts, applied to the SINGLE plane produced by Sec
    III C's own event-selection rule (select_reconstructed_plane) -- an
    event has exactly one "reconstructed plane," not whichever raw
    candidate happens to separately satisfy every downstream cut. Searching
    across all raw candidates for one that jointly passes Delta_w, Delta_s
    and hit-multiplicity (as an earlier version of this function did) lets
    an event pass via a candidate the paper's own algorithm would never
    have selected as *the* reconstructed plane in the first place, which
    inflates reconstruction efficiency relative to the paper.

      1. >=1 reconstructed plane (Delta_w < 1cm, smallest Delta_s -- Sec III C)
      2. all layers but one have >=2 hits, remaining layer >=1 hit (Sec IV)
      3. Delta_s < 0.01 cm (Delta_w < 1cm already guaranteed by selection)
    Returns the winning candidate dict, or None if the event fails.
    """
    winner = select_reconstructed_plane(candidates, dw_max_cm=dw_max_cm)
    if winner is None:
        return None
    if winner["fit"]["delta_s"] >= ds_max_cm:
        return None
    if not check_hit_multiplicity(winner["layers"], n_layers_total):
        return None
    return winner
