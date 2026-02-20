from __future__ import annotations

from src.models.types import CompanyRatios


def _safe(value: float | None, fallback: float) -> float:
    return fallback if value is None else value


def score_company(r: CompanyRatios) -> tuple[float, str, list[str]]:
    score = 100.0
    drivers: list[str] = []

    nde = _safe(r.net_debt_to_ebitda, 8.0)
    dte = _safe(r.debt_to_equity, 2.0)
    cr = _safe(r.current_ratio, 0.8)
    qr = _safe(r.quick_ratio, 0.6)
    ic = _safe(r.interest_coverage, 1.0)

    if nde > 6:
        score -= 20
        drivers.append("High net debt/EBITDA")
    elif nde > 4:
        score -= 10

    if dte > 1.5:
        score -= 18
        drivers.append("High debt/equity")
    elif dte > 1.0:
        score -= 10

    if cr < 1.0:
        score -= 15
        drivers.append("Low current ratio")

    if qr < 0.8:
        score -= 10
        drivers.append("Low quick ratio")

    if ic < 1.5:
        score -= 20
        drivers.append("Weak interest coverage")
    elif ic < 3.0:
        score -= 8

    if r.prior_quarter_delta > 0:
        penalty = min(15, r.prior_quarter_delta * 6)
        score -= penalty
        drivers.append("Deterioration vs prior quarter")

    score = max(0, round(score, 1))
    if score >= 70:
        status = "Green"
    elif score >= 45:
        status = "Amber"
    else:
        status = "Red"

    if not drivers:
        drivers.append("No major risk drivers from selected ratios")

    return score, status, drivers
