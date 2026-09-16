"""
Regression test for the raw-hit-merging bug found during the pile-up
overlay re-audit (2026-09-16): merging hard-event hits alone first, then
merging the result again with pile-up hits, is NOT equivalent to merging
raw hard hits + raw pile-up hits together in one pass.

Concrete demonstration: two raw hard hits from DIFFERENT quirks (quirk 1,
quirk 2), exactly one pixel apart (so they merge with each other), plus one
raw pile-up hit exactly one pixel away from hard hit 1 on the other side
(so it is adjacent to hard hit 1, and transitively to hard hit 2, in a
single raw+raw merge pass).

  RAW+RAW (correct, one pass):    1 cluster, source_quirk_indices=[1,2,'pu0']
  MERGED-then-remerge (wrong):    1 cluster, source_quirk_indices=[None,'pu0']
                                  -- provenance for BOTH original hard hits
                                  is lost, because merge_neighboring_pixel_
                                  hits sets a multi-quirk merged cluster's
                                  own quirk_index to None (see its
                                  docstring), and a second merge pass reads
                                  that None instead of the original [1,2].

This is why overlay_and_merge() requires RAW hard hits (e.g.
simulate_quirk_hits(...)'s traj["raw_hits"]), never its primary
already-merged return value.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
from trajectory_to_hits import merge_neighboring_pixel_hits
from atlas_geometry import LAYERS

L1 = [l for l in LAYERS if l["name"] == "L1_IBL"][0]
R_CM = L1["r_cm"]
PITCH_RPHI_CM = L1["eff_res_rphi_um"] * 1e-4
PITCH_Z_CM = L1["eff_res_z_um"] * 1e-4


def mkhit(phi, z, tag):
    x, y = R_CM * np.cos(phi), R_CM * np.sin(phi)
    return {"layer": L1["name"], "layer_r_cm": R_CM, "quirk_index": tag, "t_ns": 1.0,
            "x": x, "y": y, "z": z, "is_pixel": True,
            "idx_rphi": int(round(R_CM * phi / PITCH_RPHI_CM)),
            "idx_z": int(round(z / PITCH_Z_CM))}


def test_raw_plus_raw_vs_merged_plus_raw():
    phi_A = 0.0
    phi_B = phi_A + 1.0 * PITCH_RPHI_CM / R_CM   # 1 pixel from A -> merges with A
    phi_PU = phi_A - 1.0 * PITCH_RPHI_CM / R_CM  # 1 pixel from A on the other side

    hard_raw = [mkhit(phi_A, 0.0, 1), mkhit(phi_B, 0.0, 2)]
    pu_raw = [mkhit(phi_PU, 0.0, "pu0")]

    # WRONG: merge hard hits alone first, then merge the (already-merged)
    # result with raw pile-up hits.
    merged_hard_only = merge_neighboring_pixel_hits(hard_raw)
    combined_wrong = merged_hard_only + pu_raw
    final_wrong = merge_neighboring_pixel_hits(combined_wrong)

    # RIGHT: merge raw hard + raw pile-up together in a single pass.
    combined_right = hard_raw + pu_raw
    final_right = merge_neighboring_pixel_hits(combined_right)

    assert len(final_right) == 1
    assert final_right[0]["merged_count"] == 3
    assert sorted(final_right[0]["source_quirk_indices"], key=str) == sorted([1, 2, "pu0"], key=str), \
        f"raw+raw should preserve both quirks' provenance, got {final_right[0]['source_quirk_indices']}"

    assert len(final_wrong) == 1
    assert final_wrong[0]["merged_count"] == 2  # WRONG count too: the pre-merged hard cluster counts as 1 input hit
    wrong_prov = sorted(final_wrong[0]["source_quirk_indices"], key=str)
    assert wrong_prov != sorted([1, 2, "pu0"], key=str), \
        "expected the merged-then-remerge path to LOSE provenance (this asserts the bug is real, not fixed by accident)"
    assert None in wrong_prov, \
        f"expected merged-then-remerge to collapse quirk 1/2 provenance to None, got {wrong_prov}"

    print("RAW+RAW (correct):", final_right[0]["merged_count"], sorted(final_right[0]["source_quirk_indices"], key=str))
    print("MERGED-then-remerge (wrong, demonstrates the bug this repo now avoids):",
          final_wrong[0]["merged_count"], wrong_prov)
    print("PASS: raw+raw preserves provenance; merged+raw does not (confirming why overlay_and_merge requires raw hits)")


if __name__ == "__main__":
    test_raw_plus_raw_vs_merged_plus_raw()
