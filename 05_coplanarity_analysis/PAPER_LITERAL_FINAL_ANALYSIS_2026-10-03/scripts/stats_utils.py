"""Shared binomial statistics (Wilson, Clopper-Pearson, exact two-sided binomial p, one-sided upper limits)."""
from scipy import stats
import numpy as np
def wilson(k, n, cl):
    if n == 0: return (np.nan, np.nan)
    z = stats.norm.ppf(0.5 + cl / 2); p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))
def cp(k, n, cl=0.95):
    a = 1 - cl
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return (lo, hi)
def cp_upper(k, n, cl=0.95):
    """One-sided Clopper-Pearson upper limit."""
    return 1.0 if k == n else stats.beta.ppf(cl, k + 1, n - k)
def pval(k, n, p0):
    return stats.binomtest(k, n, p0).pvalue if n else np.nan
def row(k, n, p0=None):
    r = dict(k=k, n=n, frac=k / n if n else np.nan, se=np.sqrt(k / n * (1 - k / n) / n) if n else np.nan)
    r["wilson68_lo"], r["wilson68_hi"] = wilson(k, n, 0.6827); r["wilson95_lo"], r["wilson95_hi"] = wilson(k, n, 0.95)
    r["cp95_lo"], r["cp95_hi"] = cp(k, n); r["cp95_upper_one_sided"] = cp_upper(k, n)
    if p0 is not None:
        r["paper_value"] = p0; r["p_exact_vs_paper"] = pval(k, n, p0)
        r["paper_inside_wilson95"] = r["wilson95_lo"] <= p0 <= r["wilson95_hi"]; r["paper_inside_cp95"] = r["cp95_lo"] <= p0 <= r["cp95_hi"]
    return r
