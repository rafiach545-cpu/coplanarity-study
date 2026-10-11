#!/usr/bin/env python3
"""Combine conversion-only and overlay weighted yields into tables/weighted_yields.csv (A/B/C/D kept as separate columns).
Pile-up alone: no absolute yield (needs the triggered-event rate, not stated in the paper); per-event UL row added."""
import os, pandas as pd
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
y = pd.concat([pd.read_csv(f"{T}/weighted_yields_conversion.csv"), pd.read_csv(f"{T}/weighted_yields_overlay.csv")], ignore_index=True)
pu = pd.read_csv(f"{T}/pileup_cutflow.csv"); r = pu[(pu.config.str.startswith("LITERAL")) & (pu.stage == "final Sec. IV")].iloc[0]
y = pd.concat([y, pd.DataFrame([dict(background="pile-up only (mu=50)", config="LITERAL", sigma_choice="n/a (no absolute normalisation stated in paper)",
                                     eff_D_k=int(r.k), eff_D_n=int(r.n), eff_D=r.frac, eff_D_cp95_upper=r.cp95_upper_one_sided)])], ignore_index=True)
y.to_csv(f"{T}/weighted_yields.csv", index=False); print(len(y), "rows")
