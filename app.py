from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml

from src.ui.listed_tab import render_listed_tab
from src.ui.macro_tab import render_macro_tab
from src.ui.news_tab import render_news_tab


@st.cache_data(show_spinner=False)
def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)
    return yaml.safe_load(config_path.read_text())


def main() -> None:
    st.set_page_config(page_title="SG Developer Vulnerability Monitor", layout="wide")
    st.title("Singapore Property Developer Vulnerability Dashboard (POC)")

    config = load_config()

    tab_macro, tab_news, tab_listed = st.tabs(["Macro", "Developer News", "Listed Developers"])

    with tab_macro:
        render_macro_tab()
    with tab_news:
        render_news_tab(config)
    with tab_listed:
        render_listed_tab(config)


if __name__ == "__main__":
    main()
