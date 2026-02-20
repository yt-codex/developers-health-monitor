from __future__ import annotations

import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from src.models.types import CompanyRatios
from src.utils.logging import get_logger

LOGGER = get_logger(__name__)

FIELD_MAP = {
    "Debt / Equity": "debt_to_equity",
    "Net Debt / EBITDA": "net_debt_to_ebitda",
    "Current Ratio": "current_ratio",
    "Quick Ratio": "quick_ratio",
    "Interest Coverage": "interest_coverage",
}


def _to_float(raw: str) -> float | None:
    if not raw:
        return None
    cleaned = re.sub(r"[^\d\-.]", "", raw)
    if cleaned in {"", "-", "."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def fetch_ratios_from_stockanalysis(company: dict[str, Any], timeout: int = 10) -> CompanyRatios | None:
    """Best-effort parser for StockAnalysis ratio pages; may break if site structure changes."""
    url = company.get("stockanalysis_url")
    if not url:
        return None

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        LOGGER.warning("Failed to fetch StockAnalysis page for %s", company.get("ticker"))
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    ratios = {v: None for v in FIELD_MAP.values()}

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [col.get_text(" ", strip=True) for col in row.find_all(["th", "td"])]
            if len(cols) < 2:
                continue
            key, val = cols[0], cols[1]
            mapped = FIELD_MAP.get(key)
            if mapped:
                ratios[mapped] = _to_float(val)

    if all(val is None for val in ratios.values()):
        return None

    return CompanyRatios(
        company=company["name"],
        ticker=company["ticker"],
        cash=0.0,
        total_debt=0.0,
        net_debt=0.0,
        debt_to_equity=ratios["debt_to_equity"],
        net_debt_to_ebitda=ratios["net_debt_to_ebitda"],
        current_ratio=ratios["current_ratio"],
        quick_ratio=ratios["quick_ratio"],
        interest_coverage=ratios["interest_coverage"],
        prior_quarter_delta=0.0,
        data_source="stockanalysis_stub",
    )
