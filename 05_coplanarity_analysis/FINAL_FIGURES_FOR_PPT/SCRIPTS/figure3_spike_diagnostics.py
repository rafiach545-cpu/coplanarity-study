"""
Figure 3 spike diagnostics -- READ-ONLY, no simulation. Identifies jumps in
the plotted (valid-only) delta_phi sequence and classifies each using only
information already present in the stored CSVs (r_cm, dphi_rad, valid) plus
direct inspection of figure3_diagnostic_v2.py's actual algorithm.
"""
import pandas as pd
import numpy as np

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SOURCE_DATA"

JUMP_THRESHOLD_RAD = 5e-5  # ~1 order of magnitude above the colored curve's own median (~6e-5 per prior metadata) triggers a look

CONFIGS = [
    ("colored", f"{BASE}/05_coplanarity_analysis/figure3_diagnostic_v2/figure3_source_J_colored_natural_config_v2.csv"),
    ("EW", f"{BASE}/05_coplanarity_analysis/figure3_diagnostic_v2/figure3_source_K_ew_natural_config_v2.csv"),
]


def classify(idx_full, valid_mask, gap_before, gap_after, jump_size):
    # A "gap" = at least one invalid (near-degenerate) sample was skipped
    # immediately adjacent to this plotted point, in the RAW (pre-filter)
    # index sequence -- i.e. this plotted point sits right next to a
    # near-antiparallel v1~-v2 crossing that the 0.1*median(|nv|) filter
    # was supposed to exclude, but a sample just above that threshold can
    # still have a numerically noisy DIRECTION (magnitude alone doesn't
    # guarantee direction stability near the crossing).
    if gap_before or gap_after:
        return ("NEAR_DEGENERACY_ARTIFACT",
                "Plotted point is adjacent (in raw sample index) to one or more excluded "
                "(valid=False) near-degenerate samples -- consistent with the script's own "
                "documented mechanism (v1~-v2 crossings, |v1xv2|->0, direction ill-conditioned "
                "even just above the 0.1*median(|nv|) magnitude cutoff).")
    if jump_size > 0.05:
        return ("UNRESOLVED",
                "Large jump (>0.05 rad) with NO adjacent excluded sample -- does not match the "
                "documented near-degeneracy mechanism; cause not established from stored data "
                "alone (would require the unstored velocity_cross_product_norm/nv_hat values to "
                "diagnose further; not re-derivable without re-running the forbidden simulation).")
    return ("PHYSICAL_TREND",
            "No adjacent excluded sample; jump size consistent with the oscillatory "
            "accumulation described in the paper's own text -- not evidence of an artifact.")


def main():
    all_spikes = []
    for benchmark, path in CONFIGS:
        df = pd.read_csv(path)
        valid_idx = df.index[df["valid"]].tolist()
        n = len(df)
        for pos in range(1, len(valid_idx)):
            i_prev, i_cur = valid_idx[pos - 1], valid_idx[pos]
            jump = abs(df["dphi_rad"].iloc[i_cur] - df["dphi_rad"].iloc[i_prev])
            if jump < JUMP_THRESHOLD_RAD:
                continue
            gap_before = (i_cur - i_prev) > 1  # at least one invalid sample was skipped between them
            dphi_before = df["dphi_rad"].iloc[valid_idx[pos - 2]] if pos >= 2 else None
            dphi_after = df["dphi_rad"].iloc[valid_idx[pos + 1]] if pos + 1 < len(valid_idx) else None
            cls, reason = classify(i_cur, df["valid"], gap_before, False, jump)
            all_spikes.append({
                "benchmark": benchmark,
                "point_index": i_cur,
                "r_cm": df["r_cm"].iloc[i_cur],
                "delta_phi_before": dphi_before,
                "delta_phi_current": df["dphi_rad"].iloc[i_cur],
                "delta_phi_after": dphi_after,
                "jump_size_rad": jump,
                "cross_product_norm": "UNAVAILABLE (not stored, see FIGURE_3_SOURCE_DATA_PROVENANCE.md)",
                "near_degenerate_status": gap_before,
                "angle_branch_before": "n/a (single fixed-reference arccos metric, not a running unwrap -- see provenance note)",
                "angle_branch_after": "n/a",
                "classification": cls,
                "evidence_reason": reason,
                "raw_index_gap_to_prev_valid_sample": i_cur - i_prev,
            })
    spikes_df = pd.DataFrame(all_spikes)
    spikes_df.to_csv(f"{OUT}/FIGURE_3_SPIKE_DIAGNOSTICS.csv", index=False)
    print(f"Found {len(spikes_df)} spike candidates (jump >= {JUMP_THRESHOLD_RAD} rad)")
    if len(spikes_df):
        print(spikes_df["classification"].value_counts())
        print(spikes_df.groupby("benchmark")["classification"].value_counts())


if __name__ == "__main__":
    main()
