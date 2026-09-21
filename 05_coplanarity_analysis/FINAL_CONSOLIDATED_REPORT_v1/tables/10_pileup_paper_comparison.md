# 10_pileup_paper_comparison

| quantity | paper_value | project_value | ratio_project_over_paper | verdict |
|---|---|---|---|---|
| >=4/8 layer coverage rate at mu=50 | ~1e-3 | 59/5000=1.18e-2 | 11.8 | NOT DIRECTLY COMPARABLE -- project rate ~11.8x paper value, does not numerically reproduce it |
| 8/8 layer coverage rate at mu=50 | ~6e-5 | 0/5000 | nan | INSUFFICIENT STATISTICS -- 0/5000 cannot test a probability as small as 6e-5 (Wilson 95% UL~7.68e-4, consistent with but not confirming 6e-5) |
| Final Sec IV pass rate, all mu | assumed negligible | 0/5000 at every mu | nan | CONSISTENT WITH STATISTICS -- qualitatively consistent with paper assumption of negligible irreducible background; zero observed, not zero probability |
