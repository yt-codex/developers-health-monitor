from __future__ import annotations

import streamlit as st

from src.connectors.rss import fetch_rss_articles
from src.services.classifier import classify_articles
from src.services.cache import FileCache

SEVERITY_COLORS = {
    "info": "#4c78a8",
    "watch": "#f2a900",
    "warning": "#ff7f0e",
    "critical": "#d62728",
}


def render_news_tab(config: dict) -> None:
    settings = config.get("settings", {})
    lookback_days = int(settings.get("lookback_days", 30))
    ttl_minutes = int(settings.get("cache_ttl_minutes", 60))

    articles, failures = fetch_rss_articles(
        feeds=config.get("rss_feeds", []),
        lookback_days=lookback_days,
        ttl_minutes=ttl_minutes,
        cache=FileCache(),
    )
    articles = classify_articles(articles, config.get("companies", []))

    st.subheader("Developer News Feed")
    with st.expander("Feed status"):
        if failures:
            for failure in failures:
                st.warning(failure)
        else:
            st.success("All feeds fetched successfully (or loaded from cache).")

    severities = sorted({a.severity for a in articles})
    themes = sorted({a.theme for a in articles})
    outlets = sorted({a.outlet for a in articles})
    developers = sorted({dev for a in articles for dev in a.developers})

    left, right = st.columns([1, 3])
    with left:
        selected_severity = st.multiselect("Severity", severities, default=severities)
        selected_theme = st.multiselect("Theme", themes, default=themes)
        selected_outlet = st.multiselect("Outlet", outlets, default=outlets)
        selected_developer = st.multiselect("Developer", developers, default=developers)

    filtered = [
        a
        for a in articles
        if a.severity in selected_severity
        and a.theme in selected_theme
        and a.outlet in selected_outlet
        and any(dev in selected_developer for dev in a.developers)
    ]

    with right:
        st.caption(f"Showing {len(filtered)} articles in last {lookback_days} days")
        if not filtered:
            st.info("No articles matched selected filters.")
        for article in filtered:
            color = SEVERITY_COLORS.get(article.severity, "#4c78a8")
            terms = ", ".join(article.matched_terms) if article.matched_terms else "none"
            devs = ", ".join(article.developers)
            st.markdown(
                f"<span style='background:{color};color:white;padding:2px 8px;border-radius:8px;'>"
                f"{article.severity.upper()}</span> "
                f"**{article.title}**",
                unsafe_allow_html=True,
            )
            st.caption(
                f"{article.published.strftime('%Y-%m-%d %H:%M UTC')} | {article.outlet} | "
                f"theme={article.theme} | matched={terms} | developer={devs}"
            )
            st.write(article.summary)
            st.markdown(f"[Read more]({article.link})")
            st.divider()
