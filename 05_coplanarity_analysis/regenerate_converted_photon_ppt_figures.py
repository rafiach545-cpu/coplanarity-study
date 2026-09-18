"""
Regeneration script for the converted-photon-only PPT figure set. Read-only
over authoritative files (v3 CSV, zgamma_photons.csv); copies/regenerates
the figures already committed under converted_photon_ppt_statistics_v1/. No
new simulation. Run: python3 regenerate_converted_photon_ppt_figures.py
"""
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"
PH_DIR = f"{BASE}/05_coplanarity_analysis/converted_photon_only_statistics_v1"
OUT = f"{BASE}/05_coplanarity_analysis/converted_photon_ppt_statistics_v1"
LABEL = "CONVERTED-PHOTON-ONLY -- NO PILE-UP OVERLAY"


def photon_kinematics_figures():
    z = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
    p = np.sqrt(z.px**2 + z.py**2 + z.pz**2)
    theta = np.arccos(z.pz / p)
    eta = -np.log(np.tan(theta / 2))
    z["eta"] = eta
    z[["event", "pT_gamma", "eta", "met"]].to_csv(f"{OUT}/plotsrc_photon_kinematics.csv", index=False)

    plt.figure(figsize=(5.5, 4))
    plt.hist(z.pT_gamma, bins=40, color="tab:blue")
    plt.xlabel("photon pT (GeV)"); plt.ylabel("events"); plt.title(f"{LABEL}: photon pT", fontsize=8)
    plt.tight_layout(); plt.savefig(f"{OUT}/fig02_photon_pT.png", dpi=120); plt.close()

    plt.figure(figsize=(5.5, 4))
    plt.hist(z.eta, bins=40, color="tab:orange")
    plt.xlabel("photon eta"); plt.ylabel("events"); plt.title(f"{LABEL}: photon eta", fontsize=8)
    plt.tight_layout(); plt.savefig(f"{OUT}/fig03_photon_eta.png", dpi=120); plt.close()

    plt.figure(figsize=(5.5, 4))
    plt.hist(z.met, bins=40, color="tab:green")
    plt.axvline(200, color="red", ls="--", label="MET>200GeV cut")
    plt.xlabel("MET (GeV)"); plt.ylabel("events"); plt.legend(fontsize=8)
    plt.title(f"{LABEL}: MET", fontsize=8)
    plt.tight_layout(); plt.savefig(f"{OUT}/fig04_met.png", dpi=120); plt.close()


def reuse_frozen_figures():
    pairs = [
        ("fig1_candidate_count_distribution.png", "fig08_candidate_count_distribution.png"),
        ("fig3_layer_coverage_distribution.png", "fig09_layer_coverage_distribution.png"),
        ("fig4_delta_s_histogram.png", "fig10_delta_s_histogram.png"),
        ("fig5_delta_w_histogram.png", "fig11_delta_w_histogram.png"),
        ("fig6_delta_s_vs_delta_w.png", "fig12_delta_s_vs_delta_w.png"),
        ("fig9_cutflow_chart.png", "fig13_cutflow_chart.png"),
        ("fig10_runtime_summary.png", "fig15_runtime_chart.png"),
    ]
    for src, dst in pairs:
        shutil.copyfile(f"{PH_DIR}/{src}", f"{OUT}/{dst}")


if __name__ == "__main__":
    photon_kinematics_figures()
    reuse_frozen_figures()
    print("Regenerated converted-photon-only PPT figures under", OUT)
    print("NOTE: v4-dependent figures (failure-reason chart, e-/e+ hit-origin split) "
          "are added separately once the v4 full-diagnostics rerun completes.")
