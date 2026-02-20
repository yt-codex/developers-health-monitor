from __future__ import annotations

import re

from src.models.types import Article

TAXONOMY = {
    "refinancing": [r"refinanc", r"facility", r"bridge loan", r"maturity", r"liquidity"],
    "covenant": [r"covenant", r"waiver", r"breach"],
    "distress_sale": [r"discount", r"price cut", r"bulk sale", r"fire sale", r"weak sales"],
    "project_delay": [r"delay", r"stop work", r"construction", r"top"],
    "legal": [r"winding up", r"lawsuit", r"judicial management", r"default"],
    "ratings": [r"downgrade", r"negative outlook", r"rating"],
}


def _severity(theme: str, matched: list[str]) -> str:
    joined = " ".join(matched)
    if theme == "legal" or "default" in joined or "winding up" in joined:
        return "critical"
    if theme in {"covenant", "refinancing"}:
        return "warning"
    if theme in {"distress_sale", "project_delay", "ratings"}:
        return "watch"
    return "info"


def classify_articles(articles: list[Article], companies: list[dict]) -> list[Article]:
    company_names = [company["name"] for company in companies]

    for article in articles:
        text = f"{article.title} {article.summary}".lower()
        article.theme = "general"
        article.matched_terms = []
        for theme, patterns in TAXONOMY.items():
            hits = [pattern for pattern in patterns if re.search(pattern, text)]
            if hits:
                article.theme = theme
                article.matched_terms = hits
                break

        article.severity = _severity(article.theme, article.matched_terms)
        mentioned = [name for name in company_names if name.lower() in text]
        article.developers = mentioned if mentioned else ["general"]

    return articles
