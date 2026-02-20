# Singapore Developer Vulnerability Dashboard (POC)

A quick Streamlit prototype for monitoring potential vulnerability signals across Singapore property developers.

## Features

- **Macro (SG)** tab with deterministic mock time-series and connector placeholders for:
  - data.gov.sg
  - SingStat
  - URA
- **Developer News** tab:
  - RSS feed ingestion from configurable sources
  - Last-N-day filtering (default: 30 days)
  - Regex-based theme and severity classification
  - Developer name matching from configured company list
  - Feed failure tolerance + status display
- **Listed Developers Health** tab:
  - Mock fundamentals/ratios for configured developers
  - Composite Health Score with Green/Amber/Red status
  - Per-company explainability (top risk drivers)
  - Optional feature-flagged StockAnalysis parser stub with graceful fallback to mock

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL printed by Streamlit (typically http://localhost:8501).

## Configuration

Edit `config.yaml`:

- `rss_feeds`: list of feed objects `{name, url}`
- `companies`: list of `{name, ticker, stockanalysis_url}`
- `settings`:
  - `lookback_days`
  - `enable_stockanalysis_scrape`
  - `cache_ttl_minutes`

### Feature flag for StockAnalysis parser stub

By default, the app uses mock ratios only.

Enable best-effort StockAnalysis parsing via either:

1. `config.yaml` setting `enable_stockanalysis_scrape: true`, or
2. environment variable:

```bash
export ENABLE_STOCKANALYSIS_SCRAPE=true
```

If parsing fails for a ticker, the app falls back to mock values and shows a warning.

## Data and caching

- File-based TTL cache lives under `data/`.
- RSS responses are cached by feed URL.
- No database is used in this POC.

## Where to add real data connectors later

- `src/connectors/macro_mock.py`
  - `fetch_from_datagov(...)`
  - `fetch_from_singstat(...)`
  - `fetch_from_ura(...)`
- `src/connectors/ratios_stockanalysis_stub.py`
  - swap best-effort stub with a robust extractor/API connector

## Notes

- This POC prioritizes readability and modularity over exhaustive data fidelity.
- The mock layers are intentionally easy to replace with real connectors.
