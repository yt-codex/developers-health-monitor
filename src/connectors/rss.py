from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser

from src.models.types import Article
from src.services.cache import FileCache
from src.utils.dates import to_utc, utc_now
from src.utils.logging import get_logger

LOGGER = get_logger(__name__)


def _parse_datetime(entry: dict[str, Any]) -> datetime:
    for field in ("published", "updated"):
        raw = entry.get(field)
        if raw:
            try:
                return to_utc(parsedate_to_datetime(raw))
            except (TypeError, ValueError):
                continue
    return utc_now()


def fetch_rss_articles(
    feeds: list[dict],
    lookback_days: int,
    ttl_minutes: int,
    cache: FileCache | None = None,
) -> tuple[list[Article], list[str]]:
    cache = cache or FileCache()
    all_articles: list[Article] = []
    failures: list[str] = []
    cutoff = utc_now().timestamp() - lookback_days * 86400

    for feed in feeds:
        name = feed.get("name", "unknown")
        url = feed.get("url", "")
        if not url:
            failures.append(f"{name}: missing URL")
            continue

        cache_key = f"rss_{url}"
        parsed = cache.get(cache_key, ttl_minutes * 60)
        if parsed is None:
            result = feedparser.parse(url)
            if result.bozo:
                failures.append(f"{name}: parse error")
                LOGGER.warning("RSS parse failed for %s", url)
                continue
            parsed = [dict(item) for item in result.entries]
            cache.set(cache_key, parsed)

        for entry in parsed:
            published = _parse_datetime(entry)
            if published.timestamp() < cutoff:
                continue
            all_articles.append(
                Article(
                    title=entry.get("title", "(untitled)"),
                    summary=entry.get("summary", ""),
                    link=entry.get("link", ""),
                    published=published,
                    outlet=name,
                )
            )

    all_articles.sort(key=lambda item: item.published, reverse=True)
    return all_articles, failures
