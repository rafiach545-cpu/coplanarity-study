"""
PILE-UP-ONLY PROJECT DIAGNOSTICS -- statistics freeze (2026-09-18).

Regenerates all tables/figures for the pile-up-only statistics package from
the two AUTHORITATIVE, already-completed file families (no new simulation,
no rerun of the expensive detector-propagation pipeline):

  1. pileup_fake_background_suppressed_loose_mu{N}_n5000_ancestryv1_detv1_
     seed90210777.csv  -- original sweep: Poisson/pool/ancestry/suppression/
     per-layer-hit/coverage-diagnostic fields (commit d35b562/778df08).
  2. pileup_mu{N}_n5000_sec3c_fullcutflow_v1.csv -- Sec IIIC/Sec IV
     full-cutflow analysis-only rerun (commit e32e03e), same deterministic
     seeds/pool as (1), bit-verified against prior audit reproductions.

Both files are joined on event_i (identical SeedSequence([90210777,mu,i])
convention in both drivers -- same event, same hits, same everything except
which diagnostics were recorded).

Several requested statistics are NOT recoverable from these stored fields
without rerunning the expensive per-event propagation (pool-draw identities,
per-class hit-removal breakdown, full raw-candidate layer-coverage histogram,
per-layer timing-rejected/pre-suppression-only counts, exact failure-layer
detail for every 8/8 candidate). These are explicitly reported as
NOT AVAILABLE FROM STORED FIELDS, not fabricated or silently omitted.
"""
import ast
import json
import os
import sys
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
SWEEP_DIR = f"{BASE}/05_coplanarity_analysis/sweep_mu_2026-09-16"
OUT_DIR = f"{BASE}/05_coplanarity_analysis/pileup_only_statistics_v1"
os.makedirs(OUT_DIR, exist_ok=True)

MUS = [0, 5, 10, 20, 50]
SEED = 90210777
N_EXPECTED = 5000


def orig_path(mu):
    return f"{SWEEP_DIR}/pileup_fake_background_suppressed_loose_mu{mu}_n5000_ancestryv1_detv1_seed90210777.csv"


def full_path(mu):
    return f"{SWEEP_DIR}/pileup_mu{mu}_n5000_sec3c_fullcutflow_v1.csv"


# ---------------------------------------------------------------------------
# Confidence intervals
# ---------------------------------------------------------------------------
def wilson_interval(k, n, z):
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    center = phat + z * z / (2 * n)
    half = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    denom = 1 + z * z / n
    return ((center - half) / denom, (center + half) / denom)


def clopper_pearson_95(k, n):
    from scipy import stats as sstats
    lo = 0.0 if k == 0 else sstats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else sstats.beta.ppf(0.975, k + 1, n - k)
    return (lo, hi)


def rate_report(k, n):
    w68 = wilson_interval(k, n, 1.0)
    w95 = wilson_interval(k, n, 1.96)
    try:
        cp95 = clopper_pearson_95(k, n)
    except Exception:
        cp95 = (float("nan"), float("nan"))
    ul3n = 3.0 / n if n > 0 else float("nan")
    return {
        "k": k, "n": n, "rate": k / n if n else float("nan"),
        "wilson68_lo": w68[0], "wilson68_hi": w68[1],
        "wilson95_lo": w95[0], "wilson95_hi": w95[1],
        "cp95_lo": cp95[0], "cp95_hi": cp95[1],
        "poisson_3overN_UL": ul3n,
        "note": "Zero observed, not zero probability" if k == 0 else "",
    }


# ---------------------------------------------------------------------------
# 1. Input inventory
# ---------------------------------------------------------------------------
def build_inventory():
    import hashlib
    rows = []
    for mu in MUS:
        for kind, path in [("original_sweep", orig_path(mu)), ("fullcutflow", full_path(mu))]:
            if not os.path.exists(path):
                rows.append({"mu": mu, "kind": kind, "path": path, "status": "MISSING"})
                continue
            size = os.path.getsize(path)
            sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
            df = pd.read_csv(path)
            n_rows = len(df)
            n_unique = df["event_i"].nunique()
            n_dup = n_rows - n_unique
            expected_ids = set(range(N_EXPECTED))
            missing_ids = sorted(expected_ids - set(df["event_i"]))
            done_marker = os.path.exists(path + ".DONE")
            ckpt = os.path.exists(path + ".checkpoint")
            prov_path = path + ".provenance.json"
            prov = json.load(open(prov_path)) if os.path.exists(prov_path) else {}
            rows.append({
                "mu": mu, "kind": kind, "path": path, "status": "OK",
                "size_bytes": size, "sha256": sha, "n_rows": n_rows,
                "n_unique_event_i": n_unique, "n_duplicate_ids": n_dup,
                "n_missing_ids": len(missing_ids),
                "missing_ids_sample": missing_ids[:10],
                "done_marker": done_marker, "checkpoint_present": ckpt,
                "provenance_present": os.path.exists(prov_path),
                "seed": prov.get("seed"), "git_commit_hash": prov.get("git_commit_hash"),
                "pool_filename": prov.get("pool_filename"), "pool_sha256": prov.get("pool_sha256"),
                "detector_model_version": prov.get("detector_model_version"),
                "tracking_efficiency_selection": prov.get("tracking_efficiency_selection"),
                "wall_time_s": prov.get("wall_time_s") or prov.get("wall_time_s_this_segment"),
                "created_utc": prov.get("created_utc"),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Merge helper
# ---------------------------------------------------------------------------
def load_merged(mu):
    orig = pd.read_csv(orig_path(mu))
    full = pd.read_csv(full_path(mu))
    m = orig.merge(full, on="event_i", how="outer", suffixes=("_orig", "_full"), indicator=True)
    return orig, full, m


# ---------------------------------------------------------------------------
# 3. File-integrity checks
# ---------------------------------------------------------------------------
def integrity_checks(mu, orig, full, m):
    issues = []
    if len(orig) != N_EXPECTED:
        issues.append(f"orig row count {len(orig)} != {N_EXPECTED}")
    if len(full) != N_EXPECTED:
        issues.append(f"full row count {len(full)} != {N_EXPECTED}")
    if orig["event_i"].nunique() != N_EXPECTED:
        issues.append("orig has duplicate/missing event_i")
    if full["event_i"].nunique() != N_EXPECTED:
        issues.append("full has duplicate/missing event_i")
    if (m["_merge"] != "both").any():
        issues.append(f"{(m['_merge']!='both').sum()} event_i not present in both files")
    for col in ["n_pu_interactions", "n_pu_particles_propagated", "n_pu_hits_before_suppression",
                "n_pu_hits_after_suppression", "n_tracks_primary", "n_tracks_primary_removed",
                "n_tracks_primary_kept", "n_tracks_secondary", "n_tracks_ambiguous", "n_candidates"]:
        if (orig[col] < 0).any():
            issues.append(f"{col} has negative values")
    if (orig["n_pu_hits_after_suppression"] > orig["n_pu_hits_before_suppression"]).any():
        issues.append("post-suppression hits > pre-suppression hits for some event")
    if (full["n_candidates_raw"] < 0).any():
        issues.append("n_candidates_raw negative")
    # final_sec_iv_pass implies plane_found & hit_mult_pass & delta_s_pass_0p01
    bad_final = full[full["final_sec_iv_pass"] & ~(full["sec3c_plane_found"] & full["hit_multiplicity_pass"] & full["delta_s_pass_0p01"])]
    if len(bad_final):
        issues.append(f"{len(bad_final)} events have final_sec_iv_pass True without all upstream cuts True")
    if mu == 0:
        if orig["n_pu_interactions"].sum() != 0:
            issues.append("mu=0 has nonzero n_pu_interactions")
        if orig["n_pu_particles_propagated"].sum() != 0:
            issues.append("mu=0 has nonzero particles propagated")
        if orig["n_pu_hits_before_suppression"].sum() != 0 or orig["n_pu_hits_after_suppression"].sum() != 0:
            issues.append("mu=0 has nonzero hits")
        if full["n_candidates_raw"].sum() != 0:
            issues.append("mu=0 has nonzero candidates")
        if full["final_sec_iv_pass"].sum() != 0:
            issues.append("mu=0 has nonzero final passes")
    return issues


# ---------------------------------------------------------------------------
# Per-layer stats from per_layer_hit_counts (post-suppression, pre-merge)
# ---------------------------------------------------------------------------
def per_layer_frame(orig):
    parsed = orig["per_layer_hit_counts"].apply(ast.literal_eval)
    layer_df = pd.DataFrame(list(parsed))
    layer_df.columns = [int(c) for c in layer_df.columns]
    layer_df = layer_df[sorted(layer_df.columns)]
    return layer_df


# ---------------------------------------------------------------------------
# 9. Coverage/multiplicity table (available fields only)
# ---------------------------------------------------------------------------
def coverage_multiplicity_row(mu, full):
    n_total = len(full)
    n_plane = int(full["sec3c_plane_found"].sum())
    n_4of8 = int(full["has_4_of_8_plane"].sum())
    n_8of8 = int(full["has_8_of_8_plane"].sum())
    n_mult = int((full["sec3c_plane_found"] & full["hit_multiplicity_pass"]).sum())
    n_ds_fail_given_mult = int((full["sec3c_plane_found"] & full["hit_multiplicity_pass"] & ~full["delta_s_pass_0p01"]).sum())
    n_mult_fail_given_plane = int((full["sec3c_plane_found"] & ~full["hit_multiplicity_pass"]).sum())
    return {
        "mu": mu,
        "full_1/8_to_7/8_histogram": "NOT AVAILABLE FROM STORED FIELDS (only the WINNER's sec3c_n_layers and the BEST RAW CANDIDATE's has_4_of_8/has_8_of_8 flags were persisted; the full raw-candidate coverage histogram across all seeding_and_iterative_fit candidates per event was never saved)",
        "N_>=4/8_layers": n_4of8, "N_8/8_layers": n_8of8,
        "N_sec3c_plane_found": n_plane,
        "N_hit_mult_pass_given_plane": n_mult,
        "N_hit_mult_fail_given_plane": n_mult_fail_given_plane,
        "N_Delta_s_fail_given_mult_pass": n_ds_fail_given_mult,
        "exact_failure_layer_detail": "NOT AVAILABLE FROM STORED FIELDS for the general population; recovered for the single mu=5 8/8-coverage event via a tiny deterministic replay -- see table10_rare_event_evidence.csv",
    }


# ---------------------------------------------------------------------------
# 10. Paper comparison table
# ---------------------------------------------------------------------------
def paper_comparison_rows(master_df):
    rows = []
    row50 = master_df[master_df["mu"] == 50].iloc[0]
    paper_defs = [
        ("A", ">=4/8 reconstructed-plane probability",
         "background events contain a plane with at least one hit in 4 out of 8 layers",
         "~1e-3", "N_>=4/8 / N_total", row50["N_>=4/8"], row50["N_total"],
         "PARTIAL", "Our N_>=4/8 uses the BEST RAW candidate's layer coverage (any Delta_w), same conceptual quantity as the paper's phrasing, but our suppression model/pool/tracking-efficiency curve are documented assumptions, not the paper's exact ones."),
        ("B", "8/8 reconstructed-plane probability",
         "drops rapidly to 6e-5, for events with a plane that contains at least one hit in each layer",
         "~6e-5", "N_8/8 / N_total", row50["N_8/8"], row50["N_total"],
         "PARTIAL", "Same caveats as A; only 1 event across the whole 25,000-event sweep reaches this bar."),
        ("C", "Sec IIIC selected-plane probability",
         "Fig.5 population (\"before the final cut\"), Sec IIIC Event Selection output",
         "not numerically quoted", "N_selected_plane / N_total", row50["N_selected_plane"], row50["N_total"],
         "NO", "Paper does not quote this rate directly; it is the Fig.5 input population, not a stated benchmark number."),
        ("D", "hit-multiplicity efficiency conditional on Fig.5 control population",
         "\"weighted by the overall efficiency of passing the more stringent requirement in point 2\"",
         "not numerically quoted", "N_multiplicity / N_selected_plane", row50["N_multiplicity"], row50["N_selected_plane"],
         "PARTIAL", "This is our best-effort match to the paper's w_mult; the exact denominator population (\"1-hit-per-layer-allowed\") is an ASSUMPTION equated here with our Sec IIIC selected-plane population."),
        ("E", "final Sec IV probability", "signal region final rate (not numerically quoted for background)",
         "not numerically quoted (paper: \"we suspect they can easily be removed\")", "N_final / N_total",
         row50["N_final"], row50["N_total"], "NO",
         "Must NOT be compared directly to the paper's ~1e-3/6e-5 partial-plane rates -- those are earlier-stage coverage diagnostics, not the final signal-region rate."),
    ]
    for tag, quantity, paper_def, paper_val, field, num, den, comparable, limitation in paper_defs:
        r = rate_report(int(num), int(den))
        rows.append({
            "tag": tag, "quantity": quantity, "paper_definition": paper_def, "paper_approx_value": paper_val,
            "project_field": field, "numerator": int(num), "denominator": int(den),
            "project_rate": r["rate"], "wilson95_lo": r["wilson95_lo"], "wilson95_hi": r["wilson95_hi"],
            "exact_comparability": comparable, "limitation": limitation,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 10 (cont). w_mult reassessment + rare-event evidence via tiny deterministic replay
# ---------------------------------------------------------------------------
def w_mult_reassessment(master_df):
    row50 = master_df[master_df["mu"] == 50].iloc[0]
    k, n = int(row50["N_multiplicity"]), int(row50["N_selected_plane"])
    r = rate_report(k, n)
    return {
        "formula": "w_mult = N_hit_mult_pass / N_sec3c_plane_found",
        "numerator": k, "denominator": n, "point_estimate": r["rate"],
        "wilson95_lo": r["wilson95_lo"], "wilson95_hi": r["wilson95_hi"],
        "poisson_3overN_UL": r["poisson_3overN_UL"],
        "denominator_matches_paper_exactly": "UNRESOLVED / ASSUMPTION",
        "alternative_denominator": "paper says \"events allowed to have 1-hit per layer\" -- could instead mean events with >=1 hit in every layer among a LOOSER (non-Delta_w-filtered) raw-candidate population; not distinguishable from the paper text alone",
        "do_not_treat_as_exact_zero": "point estimate is 0 but the true rate is only bounded above (Wilson 95% UL ~= {:.4f}) -- must be carried as an uncertainty band, not a hard zero, in any Fig.5 pile-up weighting".format(r["wilson95_hi"]),
    }


def rare_event_evidence():
    """Tiny deterministic replay (1 event) to recover exact per-layer hit
    counts for the ONLY has_8_of_8_plane=True event in the whole 25,000-event
    sweep (mu=5, event_i=2006) -- justified per the freeze protocol's
    'tiny replay only if a stored field cannot otherwise be verified'
    exception; this is NOT a rerun of the statistics themselves."""
    sys.path.insert(0, f"{BASE}/05_coplanarity_analysis")
    sys.path.insert(0, f"{BASE}/02_backgrounds/pileup")
    from run_pileup_fake_background_suppressed import run_one_background_event_full_cutflow, ANCESTRY_POOL_PATH
    from pileup_hits_suppressed import build_ancestry_pool_index
    from collections import Counter

    pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))
    mu, event_i = 5.0, 2006
    ss = np.random.SeedSequence([SEED, int(mu), event_i])
    cp, cs = ss.spawn(2)

    # need the winner's raw layers list -- run_one_background_event_full_cutflow
    # doesn't expose it, so replicate its internals here for this ONE event only
    sys.path.insert(0, f"{BASE}/05_coplanarity_analysis")
    from coplanarity_fit import seeding_and_iterative_fit, vertex_relative_hits, select_reconstructed_plane, check_hit_multiplicity
    from run_pileup_fake_background import LAYER_NAME_TO_IDX, PRIMARY_VERTEX_CM
    from pileup_hits_suppressed import sample_pileup_hits_suppressed
    from tracking_efficiency import BASELINE_SELECTION

    rng_pileup = np.random.default_rng(cp)
    rng_suppression = np.random.default_rng(cs)
    pu_hits, _ = sample_pileup_hits_suppressed(pool_index, mu, rng_pileup, rng_suppression,
                                                 B_tesla=2.0, selection=BASELINE_SELECTION)
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in pu_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    candidates = seeding_and_iterative_fit(hits_by_layer)
    winner = select_reconstructed_plane(candidates)
    layer_counts = dict(Counter(winner["layers"])) if winner is not None else {}
    mult_pass = check_hit_multiplicity(winner["layers"]) if winner is not None else False
    n_with_2plus = sum(1 for l in range(1, 9) if layer_counts.get(l, 0) >= 2)
    n_with_1plus = sum(1 for l in range(1, 9) if layer_counts.get(l, 0) >= 1)
    failure_reasons = []
    if n_with_1plus < 8:
        failure_reasons.append(f"only {n_with_1plus}/8 layers have >=1 hit")
    if n_with_2plus < 7:
        failure_reasons.append(f"only {n_with_2plus}/8 layers have >=2 hits (need >=7)")
    return pd.DataFrame([{
        "mu": mu, "event_i": event_i, "seed_tuple": f"[{SEED},{int(mu)},{event_i}]",
        "n_candidates": len(candidates),
        "selected_plane": winner is not None,
        "covered_layers": sorted(layer_counts.keys()),
        "per_layer_hit_counts": layer_counts,
        "delta_s": winner["fit"]["delta_s"] if winner else float("nan"),
        "delta_w": winner["fit"]["delta_w"] if winner else float("nan"),
        "multiplicity_pass": mult_pass,
        "delta_w_pass": True if winner else False,
        "delta_s_pass": (winner["fit"]["delta_s"] < 0.01) if winner else False,
        "final_pass": mult_pass and winner is not None and winner["fit"]["delta_s"] < 0.01,
        "failure_reason": "; ".join(failure_reasons) if failure_reasons else "none (would need Delta_s check)",
    }])


# ---------------------------------------------------------------------------
# 12. Transition tables (bookkeeping only -- different RNG per mu)
# ---------------------------------------------------------------------------
def transition_tables():
    fields = ["raw_candidate", "selected_plane", "4of8", "8of8", "multiplicity", "delta_s", "final_pass"]
    field_cols = {
        "raw_candidate": lambda f: f["n_candidates_raw"] >= 1,
        "selected_plane": lambda f: f["sec3c_plane_found"],
        "4of8": lambda f: f["has_4_of_8_plane"],
        "8of8": lambda f: f["has_8_of_8_plane"],
        "multiplicity": lambda f: f["sec3c_plane_found"] & f["hit_multiplicity_pass"],
        "delta_s": lambda f: f["sec3c_plane_found"] & f["hit_multiplicity_pass"] & f["delta_s_pass_0p01"],
        "final_pass": lambda f: f["final_sec_iv_pass"],
    }
    rows = []
    pairs = [(0, 5), (5, 10), (10, 20), (20, 50)]
    for mu_a, mu_b in pairs:
        _, full_a, _ = load_merged(mu_a)
        _, full_b, _ = load_merged(mu_b)
        merged = full_a.merge(full_b, on="event_i", suffixes=("_a", "_b"))
        for field in fields:
            a_bool = field_cols[field](full_a.set_index("event_i")).reindex(merged["event_i"]).to_numpy()
            b_bool = field_cols[field](full_b.set_index("event_i")).reindex(merged["event_i"]).to_numpy()
            n00 = int((~a_bool & ~b_bool).sum())
            n01 = int((~a_bool & b_bool).sum())
            n10 = int((a_bool & ~b_bool).sum())
            n11 = int((a_bool & b_bool).sum())
            rows.append({"mu_a": mu_a, "mu_b": mu_b, "field": field,
                         "0->0": n00, "0->1": n01, "1->0": n10, "1->1": n11,
                         "label": "BOOKKEEPING COMPARISON ONLY -- NOT A PHYSICAL EVENT-BY-EVENT TRANSITION (distinct SeedSequence([seed,mu,i]) per mu means event_i is not a paired physical event across mu)"})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 13. Figures
# ---------------------------------------------------------------------------
def make_figures(master_df, cross_mu_layer_means):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = OUT_DIR

    # 1. Poisson multiplicity distributions mu=5,10,20,50
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.5))
    for ax, mu in zip(axes, [5, 10, 20, 50]):
        orig = pd.read_csv(orig_path(mu))
        ax.hist(orig["n_pu_interactions"], bins=30, color="tab:blue", alpha=0.7)
        ax.axvline(mu, color="red", ls="--", label=f"mu={mu}")
        ax.set_title(f"mu={mu}")
        ax.set_xlabel("n_pu_interactions")
    axes[0].set_ylabel("events")
    plt.suptitle("PILE-UP-ONLY PROJECT DIAGNOSTICS: Poisson multiplicity")
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/fig1_poisson_multiplicity.png", dpi=120)
    plt.close(fig)

    mus = master_df["mu"].to_numpy()

    # 2. mean retained hits vs mu
    plt.figure(figsize=(5, 4))
    plt.plot(mus, master_df["mean_retained_hits"], "o-")
    plt.xlabel("mu"); plt.ylabel("mean retained hits/crossing")
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig2_mean_retained_hits_vs_mu.png", dpi=120); plt.close()

    # 3. per-layer mean hits vs mu
    plt.figure(figsize=(6, 4))
    for L in range(1, 9):
        vals = [cross_mu_layer_means[mu].get(L, np.nan) for mu in mus]
        plt.plot(mus, vals, "o-", label=f"L{L}")
    plt.xlabel("mu"); plt.ylabel("mean hits/crossing")
    plt.legend(fontsize=7, ncol=2)
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS: per-layer mean hits")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig3_per_layer_mean_hits_vs_mu.png", dpi=120); plt.close()

    # 4. suppression fraction vs mu
    hit_df = pd.read_csv(f"{OUT_DIR}/table6_delta_s_delta_w.csv") if False else None
    supp = []
    for mu in mus:
        orig = pd.read_csv(orig_path(mu))
        b, a = orig["n_pu_hits_before_suppression"].sum(), orig["n_pu_hits_after_suppression"].sum()
        supp.append(1 - a / b if b else np.nan)
    plt.figure(figsize=(5, 4))
    plt.plot(mus, supp, "o-")
    plt.xlabel("mu"); plt.ylabel("suppression fraction")
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig4_suppression_fraction_vs_mu.png", dpi=120); plt.close()

    def rate_with_err(k_col, n_col="N_total"):
        ks = master_df[k_col].to_numpy()
        ns = master_df[n_col].to_numpy()
        rates = ks / ns
        los, his = [], []
        for k, n in zip(ks, ns):
            lo, hi = wilson_interval(int(k), int(n), 1.96)
            los.append(rates[list(ks).index(k)] - lo if not np.isnan(lo) else 0)
            his.append(hi - rates[list(ks).index(k)] if not np.isnan(hi) else 0)
        return rates, los, his

    # 5. selected-plane probability vs mu
    plt.figure(figsize=(5, 4))
    rates, los, his = rate_with_err("N_selected_plane")
    plt.errorbar(mus, rates, yerr=[los, his], fmt="o-", capsize=3)
    plt.xlabel("mu"); plt.ylabel("epsilon_plane (Wilson 95% CI)")
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig5_epsilon_plane_vs_mu.png", dpi=120); plt.close()

    # 6. >=4/8 probability vs mu
    plt.figure(figsize=(5, 4))
    rates, los, his = rate_with_err("N_>=4/8")
    plt.errorbar(mus, rates, yerr=[los, his], fmt="o-", capsize=3, color="tab:orange")
    plt.xlabel("mu"); plt.ylabel("epsilon_>=4/8 (Wilson 95% CI)")
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig6_epsilon_4of8_vs_mu.png", dpi=120); plt.close()

    # 7. 8/8 probability vs mu
    plt.figure(figsize=(5, 4))
    rates, los, his = rate_with_err("N_8/8")
    plt.errorbar(mus, rates, yerr=[los, his], fmt="o-", capsize=3, color="tab:green")
    plt.xlabel("mu"); plt.ylabel("epsilon_8/8 (Wilson 95% CI)")
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig7_epsilon_8of8_vs_mu.png", dpi=120); plt.close()

    # 8. final probability/UL vs mu
    plt.figure(figsize=(5, 4))
    uls = master_df["final_95CL_upper_limit_wilson"].to_numpy()
    plt.plot(mus, uls, "v--", color="red", label="Wilson 95% UL (point estimate = 0 at every mu)")
    plt.xlabel("mu"); plt.ylabel("final Sec IV rate upper limit")
    plt.legend(fontsize=8)
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS: zero observed, not zero probability")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig8_final_rate_upper_limit_vs_mu.png", dpi=120); plt.close()

    # 9/10. Delta_s / Delta_w distribution by mu
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for mu in [5, 10, 20, 50]:
        full = pd.read_csv(full_path(mu))
        ds = full.loc[full["sec3c_plane_found"], "sec3c_ds"].dropna()
        if len(ds):
            ax.hist(ds, bins=15, histtype="step", label=f"mu={mu} (N={len(ds)})", density=True)
    ax.axvline(0.01, color="red", ls="--")
    ax.set_xlabel("Delta_s (cm)"); ax.set_ylabel("unit-normalized density")
    ax.legend(fontsize=8)
    ax.set_title("PILE-UP-ONLY PROJECT DIAGNOSTICS: Delta_s by mu")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig9_delta_s_by_mu.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    for mu in [5, 10, 20, 50]:
        full = pd.read_csv(full_path(mu))
        dw = full.loc[full["sec3c_plane_found"], "sec3c_dw"].dropna()
        if len(dw):
            ax.hist(dw, bins=15, histtype="step", label=f"mu={mu} (N={len(dw)})", density=True)
    ax.set_xlabel("Delta_w (cm)"); ax.set_ylabel("unit-normalized density")
    ax.legend(fontsize=8)
    ax.set_title("PILE-UP-ONLY PROJECT DIAGNOSTICS: Delta_w by mu")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig10_delta_w_by_mu.png", dpi=120); plt.close(fig)

    # 11. runtime vs mu
    plt.figure(figsize=(5, 4))
    plt.plot(mus, master_df["wall_time_s_original_sweep"], "o-", label="original sweep")
    plt.plot(mus, master_df["wall_time_s_fullcutflow_rerun"], "s-", label="fullcutflow rerun")
    plt.xlabel("mu"); plt.ylabel("wall time (s)")
    plt.legend(fontsize=8)
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS: runtime")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig11_runtime_vs_mu.png", dpi=120); plt.close()

    # 12. pool fraction/reuse vs mu -- NOT AVAILABLE, placeholder figure stating so
    plt.figure(figsize=(5, 4))
    plt.text(0.5, 0.5, "NOT AVAILABLE FROM STORED FIELDS\n(sampled_pool_event_ids not persisted\nby either authoritative CSV family)",
             ha="center", va="center", fontsize=11)
    plt.axis("off")
    plt.title("PILE-UP-ONLY PROJECT DIAGNOSTICS: pool reuse")
    plt.tight_layout(); plt.savefig(f"{fig_dir}/fig12_pool_reuse_NOT_AVAILABLE.png", dpi=120); plt.close()


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------
def main():
    inv = build_inventory()
    inv.to_csv(f"{OUT_DIR}/table1_input_inventory.csv", index=False)

    all_issues = {}
    poisson_rows = []
    perevent_rows = []
    ancestry_rows = []
    hit_rows = []
    layer_rows = []
    cutflow_rows = []
    ds_dw_rows = []
    master_rows = []
    cross_mu_layer_means = {}

    for mu in MUS:
        orig, full, m = load_merged(mu)
        issues = integrity_checks(mu, orig, full, m)
        all_issues[mu] = issues

        n_total = len(orig)

        # --- 4B Poisson ---
        interactions = orig["n_pu_interactions"].to_numpy()
        exp_mean, exp_var = mu, mu
        poisson_rows.append({
            "mu": mu, "N_total": n_total, "total_interactions": int(interactions.sum()),
            "mean": float(interactions.mean()), "variance": float(interactions.var(ddof=1)) if n_total > 1 else float("nan"),
            "std": float(interactions.std(ddof=1)) if n_total > 1 else float("nan"),
            "median": float(np.median(interactions)), "min": int(interactions.min()), "max": int(interactions.max()),
            "p16": float(np.percentile(interactions, 16)), "p84": float(np.percentile(interactions, 84)),
            "p2.5": float(np.percentile(interactions, 2.5)), "p97.5": float(np.percentile(interactions, 97.5)),
            "expected_mean": exp_mean, "expected_variance": exp_var,
        })

        # --- 4D / hit stats ---
        hits_before = orig["n_pu_hits_before_suppression"].to_numpy()
        hits_after = orig["n_pu_hits_after_suppression"].to_numpy()
        particles = orig["n_pu_particles_propagated"].to_numpy()
        retained_tracks = orig["n_tracks_primary_kept"].to_numpy() + orig["n_tracks_secondary"].to_numpy() + orig["n_tracks_ambiguous"].to_numpy()
        perevent_rows.append({
            "mu": mu,
            "mean_interactions": float(interactions.mean()), "median_interactions": float(np.median(interactions)),
            "min_interactions": int(interactions.min()), "max_interactions": int(interactions.max()),
            "mean_particles": float(particles.mean()), "median_particles": float(np.median(particles)),
            "min_particles": int(particles.min()), "max_particles": int(particles.max()),
            "mean_retained_tracks": float(retained_tracks.mean()), "median_retained_tracks": float(np.median(retained_tracks)),
            "min_retained_tracks": int(retained_tracks.min()), "max_retained_tracks": int(retained_tracks.max()),
            "mean_hits_before": float(hits_before.mean()), "median_hits_before": float(np.median(hits_before)),
            "mean_hits_after": float(hits_after.mean()), "median_hits_after": float(np.median(hits_after)),
        })

        # --- 5 Ancestry/suppression ---
        n_prim = orig["n_tracks_primary"].sum()
        n_sec = orig["n_tracks_secondary"].sum()
        n_amb = orig["n_tracks_ambiguous"].sum()
        n_tot_tracks = n_prim + n_sec + n_amb
        n_removed = orig["n_tracks_primary_removed"].sum()
        n_kept = orig["n_tracks_primary_kept"].sum()
        ancestry_rows.append({
            "mu": mu,
            "total_primary": int(n_prim), "total_secondary": int(n_sec), "total_ambiguous": int(n_amb),
            "primary_fraction": n_prim / n_tot_tracks if n_tot_tracks else float("nan"),
            "secondary_fraction": n_sec / n_tot_tracks if n_tot_tracks else float("nan"),
            "ambiguous_fraction": n_amb / n_tot_tracks if n_tot_tracks else float("nan"),
            "primary_removed": int(n_removed), "primary_kept": int(n_kept),
            "primary_removal_fraction": n_removed / n_prim if n_prim else float("nan"),
            "primary_retention_fraction": n_kept / n_prim if n_prim else float("nan"),
            "mean_primary_per_crossing": n_prim / n_total, "mean_secondary_per_crossing": n_sec / n_total,
            "mean_ambiguous_per_crossing": n_amb / n_total,
            "per_class_hit_removal_breakdown": "NOT AVAILABLE FROM STORED FIELDS (n_hits_removed/n_hits_kept_* not saved to CSV, only aggregate n_pu_hits_before/after_suppression)",
            "tracking_efficiency_selection": "Loose (BASELINE_SELECTION, confirmed via provenance sidecar)",
            "one_bernoulli_draw_per_primary_track": "confirmed by code inspection: track_suppression.py loops once per particle tag, one rng_suppression draw per primary track",
            "all_or_none_correlated_hit_retention": "confirmed: draw outcome applied to ALL hits of that tag at once (unassociated_hits.extend(hits))",
            "secondaries_assigned_primary_efficiency": "NO -- secondary/ambiguous hits always kept, never drawn on (track_suppression.py:67-79)",
            "suppression_rng_independence": "confirmed: rng_suppression is a separate SeedSequence child, spawned via ss.spawn(2), independent of rng_pileup (Poisson/pool/vertex/smearing stream)",
        })

        # --- 6 hit stats ---
        n_zero_hits = int((hits_after == 0).sum())
        hit_rows.append({
            "mu": mu, "total_hits_before_suppression": int(hits_before.sum()),
            "total_hits_after_suppression": int(hits_after.sum()),
            "suppression_fraction": 1 - (hits_after.sum() / hits_before.sum()) if hits_before.sum() else float("nan"),
            "mean_hits_before": float(hits_before.mean()), "median_hits_before": float(np.median(hits_before)),
            "mean_hits_after": float(hits_after.mean()), "median_hits_after": float(np.median(hits_after)),
            "events_zero_hits_after_suppression": n_zero_hits,
            "events_ge1_hit": n_total - n_zero_hits,
            "combined_premerge_postmerge_note": "per_layer_hit_counts is POST-suppression, PRE-merge (no merge_neighboring_pixel_hits call in run_one_background_event_suppressed) -- 'premerge'==the only hit-count stage recorded here",
            "postmerge_hits": "NOT AVAILABLE FROM STORED FIELDS (this driver never calls merge_neighboring_pixel_hits)",
        })

        # --- per-layer table ---
        layer_df = per_layer_frame(orig)
        layer_summary = {"mu": mu}
        for L in sorted(layer_df.columns):
            v = layer_df[L].to_numpy()
            layer_summary[f"L{L}_total"] = int(v.sum())
            layer_summary[f"L{L}_mean"] = float(v.mean())
            layer_summary[f"L{L}_median"] = float(np.median(v))
            layer_summary[f"L{L}_p16"] = float(np.percentile(v, 16))
            layer_summary[f"L{L}_p84"] = float(np.percentile(v, 84))
            layer_summary[f"L{L}_frac_zero"] = float((v == 0).mean())
            layer_summary[f"L{L}_frac_ge1"] = float((v >= 1).mean())
            layer_summary[f"L{L}_frac_ge2"] = float((v >= 2).mean())
        layer_rows.append(layer_summary)
        cross_mu_layer_means[mu] = {L: float(layer_df[L].mean()) for L in layer_df.columns}
        layer_df.to_csv(f"{OUT_DIR}/perlayer_raw_mu{mu}.csv", index=False)

        # --- 7 cutflow ---
        n_any_hit = int((hits_after >= 1).sum())
        n_raw_cand = int((full["n_candidates_raw"] >= 1).sum())
        n_plane = int(full["sec3c_plane_found"].sum())
        n_4of8 = int(full["has_4_of_8_plane"].sum())
        n_8of8 = int(full["has_8_of_8_plane"].sum())
        n_mult = int((full["sec3c_plane_found"] & full["hit_multiplicity_pass"]).sum())
        n_ds = int((full["sec3c_plane_found"] & full["hit_multiplicity_pass"] & full["delta_s_pass_0p01"]).sum())
        n_final = int(full["final_sec_iv_pass"].sum())
        # actual code order (from run_one_background_event_full_cutflow):
        # candidates -> select_reconstructed_plane (Delta_w<1cm structurally required) ->
        # check_hit_multiplicity -> delta_s<0.01 -> final = plane & mult & ds
        stages = [
            ("analysed_bunch_crossings", n_total, n_total),
            ("events_any_retained_hit", n_total, n_any_hit),
            ("events_ge1_raw_candidate", n_any_hit, n_raw_cand),
            ("sec3c_selected_plane_(Delta_w<1cm_structural)", n_raw_cand, n_plane),
            ("plane_>=4/8_layers_(coverage_diag,_BEST_RAW_candidate,_independent_axis)", n_total, n_4of8),
            ("plane_8/8_layers_(coverage_diag,_BEST_RAW_candidate,_independent_axis)", n_total, n_8of8),
            ("hit_multiplicity_pass_(given_plane)", n_plane, n_mult),
            ("delta_s<0.01cm_pass_(given_mult)", n_mult, n_ds),
            ("final_sec_iv_pass", n_total, n_final),
        ]
        for stage, entering, passing in stages:
            failing = entering - passing
            cond_eff = passing / entering if entering else float("nan")
            cum_eff = passing / n_total if n_total else float("nan")
            r = rate_report(passing, entering) if entering else {}
            cutflow_rows.append({
                "mu": mu, "stage": stage, "entering": entering, "passing": passing,
                "failing": failing, "conditional_efficiency": cond_eff, "cumulative_efficiency": cum_eff,
                "wilson68_lo": r.get("wilson68_lo"), "wilson68_hi": r.get("wilson68_hi"),
                "wilson95_lo": r.get("wilson95_lo"), "wilson95_hi": r.get("wilson95_hi"),
            })

        # --- 8 Delta_s/Delta_w stats, multiple populations ---
        plane_pop = full[full["sec3c_plane_found"]]
        def ds_dw_stats(pop, label):
            ds = pop["sec3c_ds"].dropna().to_numpy()
            dw = pop["sec3c_dw"].dropna().to_numpy()
            row = {"mu": mu, "population": label, "N_plane": len(pop),
                   "N_finite_ds": len(ds), "N_finite_dw": len(dw)}
            if len(ds):
                row.update({
                    "ds_min": float(ds.min()), "ds_max": float(ds.max()), "ds_mean": float(ds.mean()),
                    "ds_median": float(np.median(ds)), "ds_std": float(ds.std(ddof=1)) if len(ds) > 1 else float("nan"),
                    "ds_p2.5": float(np.percentile(ds, 2.5)), "ds_p16": float(np.percentile(ds, 16)),
                    "ds_p84": float(np.percentile(ds, 84)), "ds_p97.5": float(np.percentile(ds, 97.5)),
                    "N_ds<0.01": int((ds < 0.01).sum()), "frac_ds<0.01": float((ds < 0.01).mean()),
                    "N_ds<0.05": int((ds < 0.05).sum()), "frac_ds<0.05": float((ds < 0.05).mean()),
                })
            else:
                row.update({k: float("nan") for k in ["ds_min", "ds_max", "ds_mean", "ds_median", "ds_std",
                                                        "ds_p2.5", "ds_p16", "ds_p84", "ds_p97.5"]})
                row.update({"N_ds<0.01": 0, "frac_ds<0.01": float("nan"), "N_ds<0.05": 0, "frac_ds<0.05": float("nan")})
            if len(dw):
                row.update({
                    "dw_min": float(dw.min()), "dw_max": float(dw.max()), "dw_mean": float(dw.mean()),
                    "dw_median": float(np.median(dw)), "dw_std": float(dw.std(ddof=1)) if len(dw) > 1 else float("nan"),
                    "dw_p2.5": float(np.percentile(dw, 2.5)), "dw_p16": float(np.percentile(dw, 16)),
                    "dw_p84": float(np.percentile(dw, 84)), "dw_p97.5": float(np.percentile(dw, 97.5)),
                    "N_dw<1": int((dw < 1.0).sum()), "frac_dw<1": float((dw < 1.0).mean()),
                })
            else:
                row.update({k: float("nan") for k in ["dw_min", "dw_max", "dw_mean", "dw_median", "dw_std",
                                                        "dw_p2.5", "dw_p16", "dw_p84", "dw_p97.5"]})
                row.update({"N_dw<1": 0, "frac_dw<1": float("nan")})
            return row

        ds_dw_rows.append(ds_dw_stats(plane_pop, "all_selected_planes"))
        ds_dw_rows.append(ds_dw_stats(full[full["has_4_of_8_plane"] & full["sec3c_plane_found"]], ">=4/8_AND_plane"))
        ds_dw_rows.append(ds_dw_stats(full[full["has_8_of_8_plane"] & full["sec3c_plane_found"]], "8/8_AND_plane"))
        mult_pop = full[full["sec3c_plane_found"] & full["hit_multiplicity_pass"]]
        ds_dw_rows.append(ds_dw_stats(mult_pop, "multiplicity_passing"))

        # --- master row ---
        r_final = rate_report(n_final, n_total)
        master_rows.append({
            "mu": mu, "N_total": n_total, "poisson_mean": float(interactions.mean()),
            "poisson_variance": float(interactions.var(ddof=1)) if n_total > 1 else float("nan"),
            "total_interactions": int(interactions.sum()),
            "unique_pool_events": "NOT AVAILABLE (sampled_pool_event_ids not persisted)",
            "pool_fraction_touched": "NOT AVAILABLE", "max_reuse": "NOT AVAILABLE",
            "primary": int(n_prim), "secondary": int(n_sec), "ambiguous": int(n_amb),
            "primary_removed": int(n_removed), "primary_retained": int(n_kept),
            "mean_raw_hits": float(hits_before.mean()), "mean_retained_hits": float(hits_after.mean()),
            "mean_premerge_hits": float(hits_after.mean()), "mean_postmerge_hits": "NOT AVAILABLE",
            "timing_rejected_hits": "NOT AVAILABLE (not separately recorded)",
            "N_raw_candidate": n_raw_cand, "N_selected_plane": n_plane,
            "epsilon_plane": n_plane / n_total,
            "N_>=4/8": n_4of8, "epsilon_>=4/8": n_4of8 / n_total,
            "N_8/8": n_8of8, "epsilon_8/8": n_8of8 / n_total,
            "N_multiplicity": n_mult, "epsilon_mult_given_plane": n_mult / n_plane if n_plane else float("nan"),
            "N_Delta_w": n_plane, "N_Delta_s": n_ds, "N_final": n_final,
            "epsilon_final": n_final / n_total,
            "final_95CL_upper_limit_wilson": r_final["wilson95_hi"],
            "final_95CL_upper_limit_clopper_pearson": r_final["cp95_hi"],
            "wall_time_s_original_sweep": None, "wall_time_s_fullcutflow_rerun": None,
        })

    # attach wall times from inventory
    inv_idx = inv.set_index(["mu", "kind"])
    for row in master_rows:
        mu = row["mu"]
        try:
            row["wall_time_s_original_sweep"] = inv_idx.loc[(mu, "original_sweep"), "wall_time_s"]
        except Exception:
            pass
        try:
            row["wall_time_s_fullcutflow_rerun"] = inv_idx.loc[(mu, "fullcutflow"), "wall_time_s"]
        except Exception:
            pass

    # write tables
    pd.DataFrame(poisson_rows).to_csv(f"{OUT_DIR}/table2_poisson_pool_reuse.csv", index=False)
    pd.DataFrame(ancestry_rows).to_csv(f"{OUT_DIR}/table3_ancestry_suppression.csv", index=False)
    pd.DataFrame(layer_rows).to_csv(f"{OUT_DIR}/table4_per_layer.csv", index=False)
    pd.DataFrame(cutflow_rows).to_csv(f"{OUT_DIR}/table5_cutflow.csv", index=False)
    pd.DataFrame(ds_dw_rows).to_csv(f"{OUT_DIR}/table6_delta_s_delta_w.csv", index=False)
    master_df = pd.DataFrame(master_rows)
    master_df.to_csv(f"{OUT_DIR}/table9_master_cross_mu.csv", index=False)
    pd.DataFrame(perevent_rows).to_csv(f"{OUT_DIR}/perevent_distributions.csv", index=False)

    # integrity report
    with open(f"{OUT_DIR}/integrity_check_report.json", "w") as f:
        json.dump({str(mu): v for mu, v in all_issues.items()}, f, indent=2)

    any_issues = any(len(v) for v in all_issues.values())

    # table7 coverage/multiplicity
    cov_rows = []
    for mu in MUS:
        _, full, _ = load_merged(mu)
        cov_rows.append(coverage_multiplicity_row(mu, full))
    pd.DataFrame(cov_rows).to_csv(f"{OUT_DIR}/table7_coverage_multiplicity.csv", index=False)

    # table8 paper comparison
    paper_cmp = paper_comparison_rows(master_df)
    paper_cmp.to_csv(f"{OUT_DIR}/table8_paper_comparison.csv", index=False)

    # w_mult reassessment
    wmult = w_mult_reassessment(master_df)
    with open(f"{OUT_DIR}/w_mult_reassessment.json", "w") as f:
        json.dump(wmult, f, indent=2)

    # table10 rare-event evidence (tiny deterministic replay, 1 event)
    rare_df = rare_event_evidence()
    rare_df.to_csv(f"{OUT_DIR}/table10_rare_event_evidence.csv", index=False)

    # table12 transitions
    trans_df = transition_tables()
    trans_df.to_csv(f"{OUT_DIR}/table12_transitions_bookkeeping_only.csv", index=False)

    # figures
    make_figures(master_df, cross_mu_layer_means)

    # markdown export of master table (no tabulate dependency)
    def df_to_md(df):
        cols = df.columns.tolist()
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, row in df.iterrows():
            lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        return "\n".join(lines)

    with open(f"{OUT_DIR}/pileup_only_complete_statistics_v1.md", "w") as f:
        f.write("# Pile-up-only complete statistics (master cross-mu table)\n\n")
        f.write(df_to_md(master_df))
        f.write("\n")
    master_df.to_csv(f"{OUT_DIR}/pileup_only_complete_statistics_v1.csv", index=False)

    return inv, master_df, all_issues, any_issues, cross_mu_layer_means, cov_rows, paper_cmp, wmult, rare_df, trans_df


if __name__ == "__main__":
    inv, master_df, all_issues, any_issues, cross_mu_layer_means, cov_rows, paper_cmp, wmult, rare_df, trans_df = main()
    print("=== Input inventory ===")
    print(inv[["mu", "kind", "status", "n_rows", "n_duplicate_ids", "n_missing_ids"]].to_string(index=False))
    print()
    print("=== Integrity issues (should be empty per mu) ===")
    for mu, issues in all_issues.items():
        print(f"mu={mu}: {issues if issues else 'NONE'}")
    print()
    print("=== Master cross-mu table ===")
    print(master_df.to_string(index=False))
    print()
    print("ANY INTEGRITY ISSUES FOUND:", any_issues)
    sys.exit(1 if any_issues else 0)
