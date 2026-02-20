from __future__ import annotations

import random
from datetime import timedelta

from src.models.types import MacroSeries
from src.utils.dates import utc_now


SEED = 42


def _build_series(name: str, unit: str, base: float, step: float, noise: float = 0.2) -> MacroSeries:
    random.seed(f"{SEED}-{name}")
    today = utc_now().date()
    values = []
    for idx in range(36):
        date = today - timedelta(days=(35 - idx) * 30)
        value = base + idx * step + random.uniform(-noise, noise)
        values.append({"date": str(date), "value": round(max(0, value), 2)})

    return MacroSeries(name=name, source="MOCK", unit=unit, values=values)


def get_macro_dashboard_series() -> list[MacroSeries]:
    return [
        _build_series("SORA Proxy", "%", base=2.4, step=0.01, noise=0.08),
        _build_series("Private Residential Price Index Proxy", "index", base=150, step=0.6, noise=1.2),
        _build_series("New Home Sales Volume Proxy", "units", base=780, step=3, noise=40),
        _build_series("Construction Cost Pressure Proxy", "index", base=110, step=0.35, noise=0.7),
    ]


def fetch_from_datagov(series_id: str, start: str, end: str) -> MacroSeries:
    """TODO: Implement connector to data.gov.sg API and return a MacroSeries."""
    raise NotImplementedError("data.gov.sg connector is not implemented in POC")


def fetch_from_singstat(table_id: str, start: str, end: str) -> MacroSeries:
    """TODO: Implement connector to SingStat API and return a MacroSeries."""
    raise NotImplementedError("SingStat connector is not implemented in POC")


def fetch_from_ura(endpoint: str, start: str, end: str) -> MacroSeries:
    """TODO: Implement connector to URA endpoint and return a MacroSeries."""
    raise NotImplementedError("URA connector is not implemented in POC")
