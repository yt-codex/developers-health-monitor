from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class MacroSeries:
    name: str
    source: str
    unit: str
    values: list[dict]


@dataclass
class Article:
    title: str
    summary: str
    link: str
    published: datetime
    outlet: str
    theme: str = "uncategorized"
    severity: str = "info"
    matched_terms: List[str] = field(default_factory=list)
    developers: List[str] = field(default_factory=lambda: ["general"])


@dataclass
class CompanyRatios:
    company: str
    ticker: str
    cash: float
    total_debt: float
    net_debt: float
    debt_to_equity: Optional[float]
    net_debt_to_ebitda: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    interest_coverage: Optional[float]
    prior_quarter_delta: float = 0.0
    data_source: str = "mock"
