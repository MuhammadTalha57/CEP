"""Statistics (design.md §6): Wilson 95% CI (P10 p4), exact McNemar for paired trials (P10 p4)."""
from __future__ import annotations

import math
from typing import Iterable


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value; b = success only in A, c = success only in B."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired(a: dict[str, bool], b: dict[str, bool]) -> dict[str, float]:
    """Compare two conditions on the same trial ids (e.g. none vs defense, local vs cloud)."""
    ids = sorted(set(a) & set(b))
    bb = sum(1 for i in ids if a[i] and not b[i])
    cc = sum(1 for i in ids if b[i] and not a[i])
    ka, kb = sum(a[i] for i in ids), sum(b[i] for i in ids)
    n = len(ids)
    return {"n": n, "rate_a": ka / n if n else float("nan"), "rate_b": kb / n if n else float("nan"),
            "only_a": bb, "only_b": cc, "p_mcnemar": mcnemar_exact(bb, cc)}


def mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def percentile(xs: Iterable[float], q: float) -> float:
    xs = sorted(xs)
    if not xs:
        return float("nan")
    i = (len(xs) - 1) * q
    lo, hi = math.floor(i), math.ceil(i)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
