"""Calendar and JSON rules shared by publication and regression tests."""
import calendar
import math


def season_window_predicate(month, day):
    """SQL for Jul 1 → cutoff, on dates in a July–June season.

    In Jul–Dec, Jan–Jun must never enter historical accumulations. In Jan–Jun,
    include the preceding Jul–Dec and only the elapsed part of Jan–Jun.
    """
    if not 1 <= month <= 12 or not 1 <= day <= calendar.monthrange(2024, month)[1]:
        raise ValueError("Invalid cutoff month/day")
    elapsed = f"(month(acq_date), day(acq_date)) <= ({month}, {day})"
    return f"month(acq_date) >= 7 and {elapsed}" if month >= 7 else f"(month(acq_date) >= 7 or {elapsed})"


def finite_json(value, path="", unavailable=None):
    """Represent non-finite diagnostics as null, with explicit paths for disclosure.

    This is serialization, not a new score or model fit. Preserve original
    diagnostics in data/processed; JSON consumers cannot parse Infinity or NaN.
    """
    if unavailable is None:
        unavailable = []
    if isinstance(value, dict):
        return {k: finite_json(v, f"{path}.{k}" if path else k, unavailable) for k, v in value.items()}
    if isinstance(value, list):
        return [finite_json(v, f"{path}[{i}]", unavailable) for i, v in enumerate(value)]
    if isinstance(value, float) and not math.isfinite(value):
        unavailable.append(path)
        return None
    return value
