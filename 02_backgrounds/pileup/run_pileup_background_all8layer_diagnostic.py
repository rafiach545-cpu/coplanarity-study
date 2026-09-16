"""
DIAGNOSTIC ONLY -- NOT a reweighted background estimate, NOT a final
background prediction. This is the input/control population for studying
the paper's reweighting idea (Sec IV: "the pileup backgrounds are derived
by taking the distribution from events that are allowed to have 1-hit per
layer, weighted by the overall efficiency of passing the more stringent
requirement in point 2 above"). The paper does not specify the exact
control-sample selection, the weighting formula, or the statistical-
uncertainty treatment (see the 2026-09-16 Sec IV re-audit report) -- so NO
weight or normalization factor is applied here. This script only
identifies the best-supported reading of the control population and runs
the UNCHANGED Sec III C / Sec IV reconstruction on it, recording every
stage of the resulting cutflow.

CONTROL-SUBSET SELECTION CRITERION (verified from code, not assumed):
run_pileup_fake_background.py's `has_8_of_8_plane` means BOTH (a) all 8
layers have >=1 hit AND (b) that coverage comes from an actual
seeding_and_iterative_fit candidate object -- `best_n_layers` is computed
from `candidates`, and each candidate already passed the seed-level
Delta_s<0.05cm/Delta_w<1cm/x.n3>0 cuts plus the iterative growth-factor-3
tolerance (coplanarity_fit.py:79-136). It is NOT raw, unclustered hit
coverage. This matches the paper's own wording ("a PLANE that contains at
least one hit in each layer") better than a raw-coverage reading would, so
`best_n_layers == 8` (i.e. has_8_of_8_plane) is used here as the entry
criterion for "events allowed to have 1-hit per layer." This is the
BEST-SUPPORTED reading, not a certainty -- the paper's phrase is genuinely
underspecified (see the re-audit report); this is documented as an
ASSUMPTION.

IMPORTANT SUBTLETY, preserved faithfully (Sec III C Event Selection, step
3: "Gather all the reconstructed lists, apply the final cut Delta_w<1cm.
If there are more than one plane identified, keep the one with the
smallest Delta_s."): this selection runs over ALL of an event's
candidates, not just the 8-layer-covering one. So an event can enter this
control subset (>=1 candidate reaches 8/8 layers) while the WINNING
selected plane is actually a DIFFERENT, fewer-layer candidate with smaller
Delta_s. Both facts are recorded, not collapsed into one number.

Sec III C / Sec IV cuts used here are 100% UNCHANGED: seeding_and_iterative_fit,
select_reconstructed_plane, check_hit_multiplicity, apply_signal_region_cuts
-- the same functions already used by the validated signal pipeline and the
direct-count background driver. No new weights, thresholds, or cuts are
introduced anywhere in this file.
"""
import sys
import time
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from coplanarity_fit import (seeding_and_iterative_fit, vertex_relative_hits,
                              select_reconstructed_plane, check_hit_multiplicity,
                              apply_signal_region_cuts)
from pileup_hits import build_pool_index, sample_pileup_hits
from run_pileup_fake_background import n_layers_with_hits, LAYER_NAME_TO_IDX, PRIMARY_VERTEX_CM, POOL_PATH
from provenance import build_provenance, write_csv_with_provenance

DETECTOR_MODEL_VERSION = "atlas_geometry.py Sec-IIIA-barrel-8-layer (no ref[34] endcap/TRT/ECAL/Bethe-Bloch)"
RNG_STREAM_CONVENTION = "default_rng(seed + i), one independent stream per background 'event' i"
CONTROL_SUBSET_DEFINITION = (
    "Event enters the all-8-layer control subset iff >=1 seeding_and_iterative_fit "
    "candidate (already passed seed Delta_s<0.05cm/Delta_w<1cm/x.n3>0 and the "
    "growth-factor-3 iterative tolerance) has hits spanning all 8 layers "
    "(best_candidate_n_layers_with_hit == 8). This is the best-supported but "
    "NOT certain reading of the paper's 'events that are allowed to have "
    "1-hit per layer' (Sec IV) -- documented ASSUMPTION, not a paper requirement."
)


def run_one_diagnostic_event(event_id, mu, rng, pool_index, B_tesla=2.0):
    pu_hits, pu_stats = sample_pileup_hits(pool_index, mu, rng, B_tesla=B_tesla)

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in pu_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    per_layer_counts = {k: len(v) for k, v in hits_by_layer.items()}
    n_total_hits = sum(per_layer_counts.values())

    candidates = seeding_and_iterative_fit(hits_by_layer)  # UNCHANGED Sec III C
    n_seeds_and_candidates = len(candidates)  # seeding_and_iterative_fit does not
    # expose the raw seed count separately from final iterative candidates (each
    # seed that survives becomes exactly one final candidate in its returned
    # list) -- recorded honestly as n_candidates, not invented as a separate
    # "n_seeds" the function does not actually report.
    best_n_layers = max((n_layers_with_hits(c["layers"]) for c in candidates), default=0)
    in_control_subset = (best_n_layers == 8)

    result = {
        "event_id": event_id, "mu": mu,
        "n_pu_interactions": pu_stats["n_pu_interactions"],
        "n_pu_particles_propagated": pu_stats["n_pu_particles_propagated"],
        "n_total_hits": n_total_hits,
        "per_layer_hit_counts": per_layer_counts,
        "n_candidates": n_seeds_and_candidates,
        "best_candidate_n_layers_with_hit": best_n_layers,
        "in_all8layer_control_subset": in_control_subset,
        "has_reconstructed_plane_dw_lt_1cm": False,  # Sec III C Event Selection step 3
        "selected_plane_ds": np.nan, "selected_plane_dw": np.nan,  # NaN, never 0, if no plane
        "selected_plane_n_layers": np.nan,
        "passes_hit_multiplicity": None,
        "passes_signal_region_final": False,
    }
    if not in_control_subset:
        return result  # only the control subset gets full Sec III C Event Selection + Sec IV below

    # Sec III C, "Event Selection" (step 3) -- UNCHANGED, over ALL candidates
    # for this event (not restricted to the 8-layer one -- see module docstring).
    winner = select_reconstructed_plane(candidates)  # Delta_w<1cm, smallest Delta_s
    if winner is not None:
        result["has_reconstructed_plane_dw_lt_1cm"] = True
        result["selected_plane_ds"] = winner["fit"]["delta_s"]
        result["selected_plane_dw"] = winner["fit"]["delta_w"]
        result["selected_plane_n_layers"] = n_layers_with_hits(winner["layers"])
        result["passes_hit_multiplicity"] = check_hit_multiplicity(winner["layers"])

    # Sec IV final signal-region cuts -- UNCHANGED (Delta_s<0.01cm, hit
    # multiplicity, Delta_w<1cm already enforced by the selection above).
    final_winner = apply_signal_region_cuts(candidates)
    result["passes_signal_region_final"] = final_winner is not None

    return result


def run_diagnostic_study(mu, n_events, seed=13371337, label=None, overwrite=False):
    pool_index = build_pool_index(pd.read_csv(POOL_PATH))
    rows = []
    t0 = time.time()
    for i in range(n_events):
        rng = np.random.default_rng(seed + i)
        rows.append(run_one_diagnostic_event(event_id=i, mu=mu, rng=rng, pool_index=pool_index))
    dt = time.time() - t0

    df = pd.DataFrame(rows)
    tag = label if label is not None else f"mu{mu}"
    out_path = (f"/home/rafia/coplanarity_study/05_coplanarity_analysis/"
                f"pileup_background_all8layer_diagnostic_{tag}.csv")

    n = len(df)
    n_control = int(df["in_all8layer_control_subset"].sum())
    n_plane = int(df["has_reconstructed_plane_dw_lt_1cm"].sum())
    n_final = int(df["passes_signal_region_final"].sum())

    prov = build_provenance(
        study_type="PILEUP_FAKE_BACKGROUND", mu=mu, n_events_processed=n,
        seed=seed, rng_stream_convention=RNG_STREAM_CONVENTION,
        detector_model_version=DETECTOR_MODEL_VERSION,
        extra={
            "diagnostic_only": True,
            "purpose": "This is the input/control population for studying the paper's "
                       "reweighting idea. It is NOT a reweighted background estimate and "
                       "NOT a final background prediction.",
            "control_subset_definition": CONTROL_SUBSET_DEFINITION,
            "primary_vertex_convention": "global origin (0,0,0), NOT SPECIFIED by paper/ref[34] "
                                          "for a no-hard-vertex event -- documented assumption",
            "cutflow_denominators": {
                "n_bg_events_total": n,
                "n_in_all8layer_control_subset": n_control,
                "n_with_reconstructed_plane_dw_lt_1cm": n_plane,
                "n_passing_final_signal_region": n_final,
            },
            "no_weights_or_normalization_applied": True,
            "wall_time_s": dt,
        },
    )
    write_csv_with_provenance(df, out_path, prov, overwrite=overwrite)

    print(f"[ALL8LAYER DIAGNOSTIC mu={mu}, n={n}] wall time {dt:.1f}s -> {out_path}")
    print(f"  n_bg_events_total                    = {n}")
    print(f"  n_in_all8layer_control_subset         = {n_control}")
    print(f"  n_with_reconstructed_plane(dw<1cm)    = {n_plane}")
    print(f"  n_passing_final_signal_region          = {n_final}")
    return df, out_path


if __name__ == "__main__":
    mu = float(sys.argv[1])
    n_events = int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else None
    run_diagnostic_study(mu, n_events, label=label)
