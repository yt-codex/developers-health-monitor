from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from src.connectors.ratios_mock import get_mock_ratios
from src.connectors.ratios_stockanalysis_stub import fetch_ratios_from_stockanalysis
from src.services.scoring import score_company


def render_listed_tab(config: dict) -> None:
    st.subheader("Listed Developers Health")
    companies = config.get("companies", [])
    settings = config.get("settings", {})

    use_scrape = bool(settings.get("enable_stockanalysis_scrape", False))
    env_flag = os.getenv("ENABLE_STOCKANALYSIS_SCRAPE")
    if env_flag is not None:
        use_scrape = env_flag.lower() == "true"

    ratios = get_mock_ratios(companies)
    scrape_failures: list[str] = []

    if use_scrape:
        merged = []
        for c, mock_row in zip(companies, ratios):
            parsed = fetch_ratios_from_stockanalysis(c)
            if parsed is None:
                scrape_failures.append(c["ticker"])
                merged.append(mock_row)
            else:
                parsed.cash = mock_row.cash
                parsed.total_debt = mock_row.total_debt
                parsed.net_debt = mock_row.net_debt
                parsed.prior_quarter_delta = mock_row.prior_quarter_delta
                merged.append(parsed)
        ratios = merged

    if scrape_failures:
        st.warning(
            "StockAnalysis scrape failed for: "
            + ", ".join(scrape_failures)
            + ". Falling back to mock ratios for those tickers."
        )

    rows = []
    explain_map: dict[str, list[str]] = {}
    for r in ratios:
        score, status, drivers = score_company(r)
        explain_map[r.ticker] = drivers
        rows.append(
            {
                "Company": r.company,
                "Ticker": r.ticker,
                "Cash": r.cash,
                "Total Debt": r.total_debt,
                "Net Debt": r.net_debt,
                "Debt/Equity": r.debt_to_equity,
                "Net Debt/EBITDA": r.net_debt_to_ebitda,
                "Current Ratio": r.current_ratio,
                "Quick Ratio": r.quick_ratio,
                "Interest Coverage": r.interest_coverage,
                "Health Score": score,
                "Status": status,
                "Source": r.data_source,
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    for _, row in df.iterrows():
        with st.expander(f"Explain: {row['Company']} ({row['Ticker']})"):
            for driver in explain_map[row["Ticker"]]:
                st.write(f"- {driver}")
