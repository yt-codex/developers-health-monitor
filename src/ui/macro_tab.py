from __future__ import annotations

import pandas as pd
import streamlit as st

from src.connectors.macro_mock import get_macro_dashboard_series


def render_macro_tab() -> None:
    st.subheader("Singapore Macro Indicators (POC)")
    series_list = get_macro_dashboard_series()

    for series in series_list:
        df = pd.DataFrame(series.values)
        df["date"] = pd.to_datetime(df["date"])
        st.markdown(f"**{series.name}** ({series.unit})")
        st.line_chart(df.set_index("date")["value"])

    st.info(
        "Data source status: **MOCK**\n\n"
        "Planned connectors:\n"
        "- data.gov.sg (placeholder)\n"
        "- SingStat (placeholder)\n"
        "- URA (placeholder)"
    )
