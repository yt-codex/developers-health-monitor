from __future__ import annotations

import random

from src.models.types import CompanyRatios


RNG = random.Random(7)


def get_mock_ratios(companies: list[dict]) -> list[CompanyRatios]:
    rows: list[CompanyRatios] = []
    for company in companies:
        cash = round(RNG.uniform(120, 2800), 2)
        debt = round(RNG.uniform(300, 6500), 2)
        net_debt = round(max(0.0, debt - cash), 2)
        debt_equity = round(RNG.uniform(0.2, 2.4), 2)
        net_debt_ebitda = round(RNG.uniform(1.2, 10.5), 2)
        current_ratio = round(RNG.uniform(0.6, 2.1), 2)
        quick_ratio = round(max(0.2, current_ratio - RNG.uniform(0.0, 0.5)), 2)
        interest_coverage = round(RNG.uniform(0.5, 8.5), 2)
        prior_delta = round(RNG.uniform(-1.5, 2.5), 2)

        rows.append(
            CompanyRatios(
                company=company["name"],
                ticker=company["ticker"],
                cash=cash,
                total_debt=debt,
                net_debt=net_debt,
                debt_to_equity=debt_equity,
                net_debt_to_ebitda=net_debt_ebitda,
                current_ratio=current_ratio,
                quick_ratio=quick_ratio,
                interest_coverage=interest_coverage,
                prior_quarter_delta=prior_delta,
                data_source="mock",
            )
        )
    return rows
