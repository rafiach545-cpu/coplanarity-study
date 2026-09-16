"""
Shared provenance/metadata sidecar writer for pile-up study outputs (item 6
of the 2026-09-16 re-audit). Every CSV this pipeline produces gets a
matching `<csv_path>.provenance.json` sidecar -- kept separate from the CSV
itself so existing/downstream CSV readers (pandas, etc.) are unaffected.

Also enforces overwrite protection: writing to an existing CSV path raises,
never silently overwrites a prior result.
"""
import hashlib
import json
import os
import subprocess
import datetime

POOL_PATH = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_FINAL.csv"

# Recorded once, from the actually-validated generation run (RUN_LOG.md,
# 2026-09-16 ~14:40 entry) -- NOT re-verified by instantiating Pythia8 on
# every metadata write (that pool file is a fixed, hashed artifact; its
# generation settings were already validated at creation time).
POOL_GENERATION_SETTINGS = {
    "pythia_version": "8.312",
    "process": "SoftQCD:nonDiffractive = on",
    "beams": "pp, sqrt(s) = 13000 GeV",
    "seed": 20260916,
    "n_events_requested": 20000,
    "note": "125,000-event pool per the paper's own Sec III D; this project "
            "uses 20,000 events by explicit user decision, not a paper "
            "requirement or a feasibility finding -- see RUN_LOG.md "
            "2026-09-16 ~14:40. Sampling from this pool is WITH REPLACEMENT "
            "(documented assumption, not specified by the paper or ref[34]), "
            "so results have REDUCED STATISTICAL INDEPENDENCE relative to "
            "the paper's own 125,000-event pool and must never be described "
            "as an exact paper-sized reproduction.",
}


def _sha256_file(path, chunk_size=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit_hash():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd="/home/rafia/coplanarity_study",
            text=True).strip()
    except Exception as e:
        return f"UNAVAILABLE ({e})"


def build_provenance(*, study_type, mu, n_events_processed, seed,
                      rng_stream_convention, detector_model_version,
                      extra=None, pool_path=POOL_PATH):
    """
    study_type: "SIGNAL_WITH_PILEUP" or "PILEUP_FAKE_BACKGROUND".
    """
    assert study_type in ("SIGNAL_WITH_PILEUP", "PILEUP_FAKE_BACKGROUND"), study_type
    prov = {
        "study_type": study_type,
        "mu": mu,
        "n_events_processed": n_events_processed,
        "seed": seed,
        "rng_stream_convention": rng_stream_convention,
        "detector_model_version": detector_model_version,
        "pool_filename": os.path.basename(pool_path),
        "pool_size_events": 20000,
        "pool_sha256": _sha256_file(pool_path),
        "pool_generation_settings": POOL_GENERATION_SETTINGS,
        "git_commit_hash": _git_commit_hash(),
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if extra:
        prov.update(extra)
    return prov


def write_csv_with_provenance(df, out_path, provenance, overwrite=False):
    """
    Writes df to out_path and a matching `<out_path>.provenance.json`
    sidecar. Raises FileExistsError if out_path (or its sidecar) already
    exists and overwrite=False -- never silently overwrites a prior result.
    """
    sidecar_path = out_path + ".provenance.json"
    if not overwrite:
        if os.path.exists(out_path):
            raise FileExistsError(
                f"Refusing to silently overwrite existing result: {out_path}. "
                "Pass overwrite=True explicitly, or use a new versioned filename.")
        if os.path.exists(sidecar_path):
            raise FileExistsError(
                f"Refusing to silently overwrite existing provenance sidecar: {sidecar_path}.")
    df.to_csv(out_path, index=False)
    with open(sidecar_path, "w") as f:
        json.dump(provenance, f, indent=2, default=str)
    return out_path, sidecar_path
