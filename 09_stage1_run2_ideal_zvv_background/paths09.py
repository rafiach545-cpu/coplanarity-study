"""09 (2026-11-20): every external path of the 09 pipeline, overridable by environment variables (laptop defaults unchanged).
  COPLANARITY_BASE  repository root (default: the parent of this folder)
  HEP_TOOLS         folder with MG5, QuirkPheno and the run folders (default: <parent of the repository>/hep_tools)
  MG5_BIN, ZVV_RUNS, WLNU_RUNS, SIGNAL_10K_RUNS, B05_HEPMC, QUIRKPHENO   individual overrides
Samples (B01 / B03 / B09 --sample): zvv = Z(nunu)+jet (the 09 baseline), wlnu = W(lnu)+jet, l = e, mu, tau."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(HERE))
HEP_TOOLS = os.environ.get("HEP_TOOLS", os.path.join(os.path.dirname(BASE), "hep_tools"))
MG5 = os.environ.get("MG5_BIN", f"{HEP_TOOLS}/MG5_aMC_v3_7_3/bin/mg5_aMC")
SIGNAL_10K_RUNS = os.environ.get("SIGNAL_10K_RUNS", f"{HEP_TOOLS}/07_large_runs")
B05_HEPMC = os.environ.get("B05_HEPMC", f"{HEP_TOOLS}/quirk_ew_800gev_4kev/Events/run_01/tag_1_pythia8_events.hepmc.gz")
QUIRKPHENO = os.environ.get("QUIRKPHENO", f"{HEP_TOOLS}/QuirkPheno")

SAMPLES = {
    "zvv": dict(runs=os.environ.get("ZVV_RUNS", f"{HEP_TOOLS}/09_zvv_runs"), seed0=391000, prefix="", chunks="B01_chunks.csv",
                proc="import model sm\ndefine vl = ve vm vt\ndefine vl~ = ve~ vm~ vt~\ngenerate p p > vl vl~ j\noutput {out}\n",
                settings={"ebeam1": "6500.0", "ebeam2": "6500.0", "misset": "200.0", "ptj": "20.0"}),
    # W(lnu)+jet, l = e, mu, tau (2026-11-20): same cuts as zvv; no charged-lepton cut (ptl = 0, no eta cut), so leptons outside the
    # tracker are kept: the 09 trigger proxy is truth MET > 200 GeV only.
    "wlnu": dict(runs=os.environ.get("WLNU_RUNS", f"{HEP_TOOLS}/09_wlnu_runs"), seed0=392000, prefix="wlnu_", chunks="B01_wlnu_chunks.csv",
                 proc=("import model sm\ndefine lp = e+ mu+ ta+\ndefine lm = e- mu- ta-\ndefine vl = ve vm vt\ndefine vl~ = ve~ vm~ vt~\n"
                       "generate p p > lp vl j\nadd process p p > lm vl~ j\noutput {out}\n"),
                 settings={"ebeam1": "6500.0", "ebeam2": "6500.0", "misset": "200.0", "ptj": "20.0", "ptl": "0.0", "etal": "-1.0"}),
}


def hepmc_of(sample, chunk, recorded=None):
    """The chunk's HepMC file: the path recorded by B01 if it exists here, else the standard place under this machine's run folder."""
    if recorded and os.path.exists(recorded): return recorded
    return f"{SAMPLES[sample]['runs']}/chunk_{chunk:02d}/Events/run_b01/tag_1_pythia8_events.hepmc.gz"
