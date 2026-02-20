#!/usr/bin/env python3
"""Build mock JSON datasets for the GitHub Pages dashboard.

POC behavior:
- Generates deterministic mock macro, news, and listed developer datasets.
- Applies risk classification and composite health scoring.
- Writes data files into /public/data.

TODO (future integration):
- Replace mock macro generation with data.gov.sg / SingStat / URA ingestion.
- Replace mock news list with RSS ingestion + normalization.
- Replace mock listed ratios with best-effort parsing of public ratio pages.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data"

RNG = random.Random(42)

THEME_PATTERNS: dict[str, str] = {
    "refinancing": r"refinanc|facility|bridge loan|maturity|liquidity",
    "covenant": r"covenant|waiver|breach",
    "distress_sale": r"discount|price cut|bulk sale|fire sale",
    "project_delay": r"delay|stop work|construction|\bTOP\b",
    "legal": r"winding up|lawsuit|judicial management|default",
    "ratings": r"downgrade|negative outlook|rating",
}

CRITICAL_PATTERNS = re.compile(r"\b(default|winding up|judicial management)\b", flags=re.I)
WARNING_PATTERNS = re.compile(r"\b(covenant|waiver|breach|refinanc|bridge loan|maturity)\b", flags=re.I)
WATCH_PATTERNS = re.compile(r"\b(discount|price cut|bulk sale|fire sale|delay|stop work|weak sales)\b", flags=re.I)


@dataclass
class ListedDeveloper:
    ticker: str
    company: str
    net_debt_to_equity: float
    net_debt_to_ebitda: float
    cash_to_short_debt: float
    quick_ratio: float | None
    prior_net_debt_to_equity: float
    prior_net_debt_to_ebitda: float


def compute_health(dev: ListedDeveloper) -> dict[str, Any]:
    score = 100.0

    # Penalize leverage.
    score -= min(45.0, dev.net_debt_to_equity * 18.0)
    score -= min(20.0, max(0.0, dev.net_debt_to_ebitda - 1.0) * 6.0)

    # Penalize liquidity weakness.
    if dev.cash_to_short_debt < 1.0:
        score -= (1.0 - dev.cash_to_short_debt) * 20.0
    if dev.quick_ratio is not None and dev.quick_ratio < 1.0:
        score -= (1.0 - dev.quick_ratio) * 15.0

    # Deterioration penalties.
    if dev.net_debt_to_equity > dev.prior_net_debt_to_equity:
        score -= min(10.0, (dev.net_debt_to_equity - dev.prior_net_debt_to_equity) * 12.0)
    if dev.net_debt_to_ebitda > dev.prior_net_debt_to_ebitda:
        score -= min(8.0, (dev.net_debt_to_ebitda - dev.prior_net_debt_to_ebitda) * 4.0)

    score = round(max(0.0, min(100.0, score)), 1)

    if score >= 70:
        status = "Green"
    elif score >= 40:
        status = "Amber"
    else:
        status = "Red"

    drivers: list[str] = []
    if dev.net_debt_to_equity > 2.5:
        drivers.append("High net debt-to-equity relative to peers.")
    if dev.net_debt_to_ebitda > 4.0:
        drivers.append("Elevated net debt-to-EBITDA indicates stretched leverage.")
    if dev.cash_to_short_debt < 1.0:
        drivers.append("Cash coverage of short-term debt is below 1.0x.")
    if dev.quick_ratio is not None and dev.quick_ratio < 1.0:
        drivers.append("Quick ratio below 1.0x signals weak near-term liquidity.")
    if dev.net_debt_to_equity > dev.prior_net_debt_to_equity:
        drivers.append("Leverage worsened vs prior period (debt-to-equity).")
    if dev.net_debt_to_ebitda > dev.prior_net_debt_to_ebitda:
        drivers.append("Leverage worsened vs prior period (debt-to-EBITDA).")
    if not drivers:
        drivers.append("Balance sheet and liquidity metrics are broadly stable.")

    return {
        "health_score": score,
        "status": status,
        "drivers": drivers,
    }


def classify_news(text: str, companies: list[str]) -> dict[str, Any]:
    tags = [name for name, pattern in THEME_PATTERNS.items() if re.search(pattern, text, flags=re.I)]

    if CRITICAL_PATTERNS.search(text):
        severity = "critical"
    elif WARNING_PATTERNS.search(text):
        severity = "warning"
    elif WATCH_PATTERNS.search(text):
        severity = "watch"
    else:
        severity = "info"

    entity_hits = [company for company in companies if re.search(re.escape(company), text, flags=re.I)]

    return {
        "tags": tags,
        "severity": severity,
        "entities": entity_hits,
    }


def make_macro() -> dict[str, Any]:
    months = [f"2024-{m:02d}" for m in range(1, 13)]

    hdb_resale_index = [174.2, 175.3, 176.7, 177.8, 178.1, 178.9, 179.8, 180.4, 181.0, 181.7, 182.4, 183.1]
    private_home_index = [190.0, 190.6, 191.2, 191.8, 192.5, 193.3, 194.1, 194.8, 195.2, 195.7, 196.1, 196.8]
    mortgage_rate_3m = [3.62, 3.58, 3.51, 3.44, 3.41, 3.35, 3.31, 3.27, 3.24, 3.19, 3.14, 3.08]

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "series": {
            "hdb_resale_index": {"label": "HDB Resale Price Index", "x": months, "y": hdb_resale_index},
            "private_home_index": {"label": "Private Residential Price Index", "x": months, "y": private_home_index},
            "mortgage_rate_3m": {"label": "3M Mortgage Proxy Rate (%)", "x": months, "y": mortgage_rate_3m},
        },
    }


def make_listed() -> dict[str, Any]:
    developers = [
        ListedDeveloper("UOL", "UOL Group", 0.78, 2.3, 1.4, 1.3, 0.73, 2.1),
        ListedDeveloper("CDL", "City Developments", 1.65, 4.6, 0.9, 0.8, 1.51, 4.1),
        ListedDeveloper("9CI", "CapitaLand Investment", 0.92, 3.0, 1.2, 1.1, 0.84, 2.8),
        ListedDeveloper("F17", "GuocoLand", 1.34, 4.1, 0.85, 0.9, 1.30, 3.9),
        ListedDeveloper("A26", "Hongkong Land", 1.12, 3.8, 0.95, 0.96, 1.02, 3.4),
        ListedDeveloper("M44U", "Mapletree Logistics Trust", 2.40, 5.2, 0.62, 0.72, 2.10, 4.8),
        ListedDeveloper("C38U", "CapitaLand Integrated Commercial Trust", 2.10, 5.0, 0.70, 0.75, 1.95, 4.7),
        ListedDeveloper("ME8U", "Mapletree Industrial Trust", 1.75, 4.4, 0.82, 0.88, 1.68, 4.2),
        ListedDeveloper("BUOU", "Frasers Logistics & Commercial Trust", 1.88, 4.7, 0.77, 0.83, 1.79, 4.4),
        ListedDeveloper("N2IU", "Mapletree Pan Asia Commercial Trust", 2.20, 5.1, 0.68, 0.71, 2.03, 4.9),
    ]

    rows: list[dict[str, Any]] = []
    for dev in developers:
        health = compute_health(dev)
        rows.append(
            {
                "ticker": dev.ticker,
                "company": dev.company,
                "net_debt_to_equity": dev.net_debt_to_equity,
                "net_debt_to_ebitda": dev.net_debt_to_ebitda,
                "cash_to_short_debt": dev.cash_to_short_debt,
                "quick_ratio": dev.quick_ratio,
                "prior_net_debt_to_equity": dev.prior_net_debt_to_equity,
                "prior_net_debt_to_ebitda": dev.prior_net_debt_to_ebitda,
                **health,
            }
        )

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "companies": [d.company for d in developers],
        "rows": rows,
    }


def make_news(company_names: list[str]) -> dict[str, Any]:
    base = date(2025, 1, 15)
    raw_items = [
        {
            "title": "City Developments secures bridge loan ahead of debt maturity",
            "outlet": "Business Times",
            "summary": "The group refinanced a major facility as liquidity planning intensifies.",
            "url": "https://example.com/news/cdl-bridge-loan",
        },
        {
            "title": "GuocoLand reports construction delay at flagship mixed-use project",
            "outlet": "The Edge Singapore",
            "summary": "Delay may push TOP timelines and raise carrying costs.",
            "url": "https://example.com/news/guocoland-delay",
        },
        {
            "title": "Mapletree Pan Asia Commercial Trust receives covenant waiver from lenders",
            "outlet": "Reuters",
            "summary": "Waiver tied to temporary covenant breach after valuation decline.",
            "url": "https://example.com/news/mpact-waiver",
        },
        {
            "title": "CapitaLand Investment sees stable sales despite price cut campaign",
            "outlet": "CNA",
            "summary": "Bulk sale discount strategy used to sustain momentum in select assets.",
            "url": "https://example.com/news/cli-price-cut",
        },
        {
            "title": "Legal filing seeks winding up of small contractor tied to project",
            "outlet": "Straits Times",
            "summary": "No immediate default by listed sponsor was disclosed.",
            "url": "https://example.com/news/winding-up-filing",
        },
        {
            "title": "UOL Group reports resilient liquidity position in latest update",
            "outlet": "SG Investors",
            "summary": "Management highlighted conservative balance sheet and rating stability.",
            "url": "https://example.com/news/uol-liquidity",
        },
    ]

    items: list[dict[str, Any]] = []
    for i, row in enumerate(raw_items):
        text = f"{row['title']} {row['summary']}"
        classification = classify_news(text, company_names)
        items.append(
            {
                **row,
                "published_at": base.isoformat() if i == 0 else (base.replace(day=min(28, base.day + i))).isoformat(),
                **classification,
            }
        )

    RNG.shuffle(items)
    items.sort(key=lambda x: x["published_at"], reverse=True)

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }


def write_json(filename: str, payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    listed = make_listed()
    news = make_news(listed.get("companies", []))
    macro = make_macro()

    write_json("listed.json", listed)
    write_json("news.json", news)
    write_json("macro.json", macro)
    write_json(
        "status.json",
        {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": "mock_build",
            "ok": True,
            "errors": [],
            "notes": [
                "POC mode with deterministic mock data.",
                "TODO: Replace mock fetchers with live connectors for macro, news, and ratios.",
            ],
        },
    )


if __name__ == "__main__":
    main()
