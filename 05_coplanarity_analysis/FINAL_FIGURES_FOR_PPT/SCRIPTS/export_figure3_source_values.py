"""
Figure 3 source-data export -- READ-ONLY. Reads the already-committed,
already-plotted CSVs (no trajectory re-integration, no MadGraph/Pythia,
no new simulation). Exports the exact plotted arrays plus every derivable
diagnostic column; explicitly marks columns that were never stored by the
original script (and would require re-running the forbidden simulation to
obtain) as UNAVAILABLE rather than inferring or regenerating them.
"""
import hashlib
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
FIG3_DIAG = f"{BASE}/05_coplanarity_analysis/figure3_diagnostic_v2"
OUT = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SOURCE_DATA"

CONFIGS = [
    ("colored", "J_colored_natural_config", f"{FIG3_DIAG}/figure3_source_J_colored_natural_config_v2.csv",
     1800.0, 2.0, 2.0),
    ("EW", "K_ew_natural_config", f"{FIG3_DIAG}/figure3_source_K_ew_natural_config_v2.csv",
     800.0, 2.0, 2.0),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    all_rows = []
    per_benchmark = {}
    for benchmark, config_id, path, mQ, Lambda_keV, B_T in CONFIGS:
        df = pd.read_csv(path)
        out_rows = []
        for idx, row in df.iterrows():
            out_rows.append({
                "benchmark": benchmark,
                "point_index": idx,
                "r_cm": row["r_cm"],
                "delta_phi_rad": row["dphi_rad"],
                "delta_phi_times_1e3": row["dphi_rad"] * 1e3,
                "velocity_cross_product_norm": "UNAVAILABLE (|v1 x v2| computed in-memory by "
                    "figure3_diagnostic_v2.py but never written to the saved CSV -- recovering it "
                    "would require re-running the trajectory integration, which this audit is "
                    "explicitly forbidden from doing)",
                "valid_plane_normal": bool(row["valid"]),
                "near_degenerate_flag": not bool(row["valid"]),
                "angle_unwrapped": row["dphi_rad"],  # the stored quantity IS the unwrapped accumulated angle
                "plotted_in_final_figure": bool(row["valid"]),  # ax.plot used cv = c[c["valid"]] only
                "source_event_configuration_id": config_id,
                "mQ_GeV": mQ,
                "Lambda_keV": Lambda_keV,
                "B_T": B_T,
                "source_file": path,
                "source_row_index": idx,
            })
        per_benchmark[benchmark] = pd.DataFrame(out_rows)
        all_rows.extend(out_rows)
        print(f"{benchmark} ({config_id}): {len(out_rows)} rows from {path}")

    combined = pd.DataFrame(all_rows)
    combined.to_csv(f"{OUT}/FIGURE_3_FINAL_Plane_Rotation_VALUES.csv", index=False)
    per_benchmark["colored"].to_csv(f"{OUT}/FIGURE_3_COLORED_VALUES.csv", index=False)
    per_benchmark["EW"].to_csv(f"{OUT}/FIGURE_3_EW_VALUES.csv", index=False)

    print(f"\nWrote {len(combined)} total rows.")
    print(f"colored: {len(per_benchmark['colored'])}, EW: {len(per_benchmark['EW'])}")

    # independent validation stats
    for benchmark, df in per_benchmark.items():
        finite = df["delta_phi_rad"].apply(lambda x: x == x and abs(x) != float("inf"))
        print(f"\n--- {benchmark} independent validation ---")
        print("row count:", len(df))
        print("r_cm min/max:", df["r_cm"].min(), df["r_cm"].max())
        print("delta_phi_rad min/max:", df["delta_phi_rad"].min(), df["delta_phi_rad"].max())
        print("finite count:", int(finite.sum()), "of", len(df))
        print("NaN count:", int(df["delta_phi_rad"].isna().sum()))
        print("duplicate (r_cm,delta_phi_rad) rows:", int(df.duplicated(subset=["r_cm", "delta_phi_rad"]).sum()))
        print("max delta_phi among plotted (valid) points:",
              df.loc[df["plotted_in_final_figure"], "delta_phi_rad"].max())

    for f in [
        f"{FIG3_DIAG}/figure3_source_J_colored_natural_config_v2.csv",
        f"{FIG3_DIAG}/figure3_source_K_ew_natural_config_v2.csv",
        f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/PNG/FIGURE_3_FINAL_Plane_Rotation.png",
        f"{BASE}/03_trajectory_sim/figure3_diagnostic_v2.py",
        f"{OUT}/FIGURE_3_FINAL_Plane_Rotation_VALUES.csv",
        f"{OUT}/FIGURE_3_COLORED_VALUES.csv",
        f"{OUT}/FIGURE_3_EW_VALUES.csv",
    ]:
        print(f"SHA256 {sha256_of(f)}  {f}")


if __name__ == "__main__":
    main()
