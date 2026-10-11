# NON-AUTHORITATIVE ARCHIVE (2026-10-03)

**Everything referenced here is NON-AUTHORITATIVE.** It must not be quoted as a literal reproduction of arXiv:1708.02243 Table I.

- Nothing was moved or deleted. `links/` holds relative symlinks to the original directories, which stay at their original paths.
- `ORIGINAL_PATHS_SHA256.txt` records the SHA-256 of every report, table, script and JSON file in those directories at archive time.

| Original path | Why it is non-authoritative |
|---|---|
| `TABLE_I_FINAL_INDEPENDENT_VALIDATION_2026-10-03/PROVISIONAL_PAPER_MATCHED_CONFIGURATION_v1/` | Calibrated configuration: SCT z smearing 0 (not paper/reference-stated) and η-cone acceptance (not paper-stated). Its numbers (EW reco ≈ 0.81, COL ≈ 0.36–0.83) are a **calibrated** result. |
| `TABLE_I_FINAL_REPRODUCTION_2026-10-02/` | Same calibrated reading. |
| `TABLE_I_FINAL_INDEPENDENT_VALIDATION_2026-10-03/` | Its calibrated rows are non-authoritative. Its LITERAL rows (EW 14/102, COL 6/94) agree with, and are cited by, the authoritative literal analysis. |
| `PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/` | Forensic and search work, including trigger-setting scans. It contains the contaminated plane numerators (COL2000 20/25, EW2000 84/94), which are **rejected**. |

**Authoritative result:** `PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/`.

## Correction (2026-10-03, v2)

The table above called the η-cone acceptance "not paper-stated". **That was wrong.** The paper states "effectively restricts the fiducial range to |η| ≲ 1.8", and the η-cone (|η| < 1.8, no finite-z boundary) is now the PRIMARY acceptance (see `PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`).

**What remains non-authoritative:**
- The calibrated SCT z = 0 setting. It is UNDOCUMENTED: Ref. [27] gives 580 µm (z), and the paper does not say whether its doubling applies to z.
- Any result presented as a reproduction that uses that setting.

**The η-cone counts with SCT z 1160 µm in these directories** (COL2000 25/12/7/3, EW2000 94/75/48/21) are exactly the v2 primary counts for that SCT z treatment.
