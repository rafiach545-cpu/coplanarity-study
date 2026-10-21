# L tables of the report, in units of 10^8 ħ (2026-10-21)

These are the same numbers as the L tables in `TABLE_I_REPRODUCTION_REPORT_2026-10-21_partAB.pdf` (Sections A3 and B6), written by `scripts/R_report_2026-10-21_partAB.py`. The figures keep their own units; only the tables use 10^8 ħ.

## `L_meetings_1e8hbar.csv`: |L| at each meeting of the two quirks

**Events (`event` column)**
- `paper`: the paper's Fig. 2 event, read from its vector figure.
- `constructed`: our event with the paper's kinematics.
- `key 8`: event no. 8 of our sample.

**Columns**
- `L_abs_1e8hbar`: |L| = b · p* / ħc, in 10^8 ħ. It is computed from the impact parameter b, so it keeps our residual at the even meetings (1–5 × 10^8 ħ). The 10^12 ħ table rounds that residual to 0.00.
- `L_sign`: the sign of L at the meeting. It is 0 where L is only the numerical residual and its sign is not known.
- `dL_this_half_1e8hbar`: the change of L since the previous meeting.
- `b_cm`: the impact parameter b, in cm.
- `p_star_GeV`: the p* used to compute b. The paper does not give one, so 1204.1 GeV is used for it.

## `L_change_per_half_oscillation_1e8hbar.csv`: change of L in each half-oscillation

This is for our event with the paper's kinematics.
- `total_1e8hbar`: the total change of L.
- `magnetic_1e8hbar`: the part from the magnetic torque q d × E*.
- `string_1e8hbar`: the part from the string term of Eq. 3.
- `paper_1e8hbar`: the change in the paper's curve.

## `L_residual_vs_step_size_1e8hbar.csv`: |L| at meetings 2 and 4 for four RK4 step sizes

- The `*_signed_*` columns keep the sign: at 10,000 steps, L crosses zero.
- At meetings 1 and 3, |L| = 6430 × 10^8 ħ for every step size.
