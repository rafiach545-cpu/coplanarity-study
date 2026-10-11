#!/usr/bin/env python3
"""
Layer-by-layer barrel acceptance table and overlap ("double counting") test
between a finite-z barrel and the project's origin-measured |eta|<1.8 cone.

Geometry sources (primary documents, archived under paper_source/):
  IBL     : |z| < 330.15 mm active stave length -- arXiv:1803.00844, IBL layout table
  Pixel   : sensitive barrel |z| < 400.5 mm     -- ATLAS JINST 3 S08003, Table 1.2 / Fig 4.1
  SCT     : sensitive barrel |z| < 749 mm       -- ATLAS JINST 3 S08003, Table 1.2 / Fig 4.1
  Radii   : project values (arXiv:2007.07624 Table 1), identical to JINST for pixel/SCT

Overlap test re-uses the per-event layer crossings produced by the previous
audit's replay (read-only):
  ../EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/tables/*_layer_crossings_vertex_relative.csv
  ../EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/tables/*_fiducial_variants_per_event.csv
"""
import math
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f"{HERE}/../tables"
PREV = f"{HERE}/../../EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/tables"

LAYERS = [  # (idx, name, r_cm, half_length_cm, source)
    (1, "IBL", 3.325, 33.015, "arXiv:1803.00844 (active |z| 330.15 mm)"),
    (2, "Pixel B-layer", 5.05, 40.05, "JINST 3 S08003 Table 1.2"),
    (3, "Pixel L1", 8.85, 40.05, "JINST 3 S08003 Table 1.2"),
    (4, "Pixel L2", 12.25, 40.05, "JINST 3 S08003 Table 1.2"),
    (5, "SCT B3", 29.9, 74.9, "JINST 3 S08003 Table 1.2"),
    (6, "SCT B4", 37.1, 74.9, "JINST 3 S08003 Table 1.2"),
    (7, "SCT B5", 44.3, 74.9, "JINST 3 S08003 Table 1.2"),
    (8, "SCT B6", 51.4, 74.9, "JINST 3 S08003 Table 1.2"),
]
ETA = 1.8
SIG_Z = 4.5


def eta(r, z):
    return math.asinh(z / r)


def main():
    rows = []
    for i, n, r, L, src in LAYERS:
        zc = r * math.sinh(ETA)
        rows.append(dict(
            layer=i, name=n, radius_cm=r, half_length_cm=L, source=src,
            eta_edge_vertex_at_0=eta(r, L),
            eta_edge_vertex_at_plus2sigma=eta(r, L - 2 * SIG_Z),
            project_cone_equivalent_half_length_cm=zc,
            project_implementation="infinite cylinder + per-hit |eta_origin|<1.8",
            binding_constraint_if_both=("eta<1.8 cone" if zc < L else "finite z"),
            cone_vs_barrel=("cone TIGHTER than barrel" if zc < L else "cone LOOSER than barrel"),
        ))
    t = pd.DataFrame(rows)
    t.to_csv(f"{OUT}/barrel_layer_acceptance_table.csv", index=False)
    pd.set_option("display.width", 250)
    print(t.drop(columns=["source", "project_implementation"]).round(3).to_string(index=False))

    # overlap test: which layer makes C (cone AND finite) differ from B (finite only)?
    ov = []
    for s in ("EW1000", "EW2000", "COL2000"):
        v = pd.read_csv(f"{PREV}/{s}_fiducial_variants_per_event.csv")
        x = pd.read_csv(f"{PREV}/{s}_layer_crossings_vertex_relative.csv")
        z0 = v.set_index("row_index")["z0_cm"]
        extra = v[v.B_finite_barrel_nominal & ~v.C_eta1p8_and_finite_barrel]
        for k in extra.row_index:
            c = x[x.key == k].copy()
            c["z_lab"] = c.z_rel + z0[k]
            c["eta_lab"] = [eta(r, z) for r, z in zip(c.r, c.z_lab)]
            bad = c[c.eta_lab.abs() >= ETA]
            ov.append(dict(sample=s, row_index=int(k),
                           event_id=int(v.loc[v.row_index == k, "event_id"].iloc[0]),
                           z0_cm=float(z0[k]), layers_failing_cone=" ".join(map(str, sorted(set(bad.layer)))),
                           max_abs_z_lab_cm=float(c.z_lab.abs().max())))
        print(f"{s}: B={int(v.B_finite_barrel_nominal.sum())} C={int(v.C_eta1p8_and_finite_barrel.sum())} "
              f"(cone removes {len(extra)} events that are inside every finite barrel layer)")
    o = pd.DataFrame(ov)
    o.to_csv(f"{OUT}/cone_on_top_of_finite_barrel_extra_losses.csv", index=False)
    print(o.to_string(index=False))


if __name__ == "__main__":
    main()
