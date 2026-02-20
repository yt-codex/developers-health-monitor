# Singapore Property Developer Vulnerability Monitor (POC)

GitHub Pages-hosted static dashboard for monitoring vulnerability signals across Singapore property developers.

## What this POC includes

- **Static frontend** (`/public`) with 3 dashboard pages:
  - `macro.html`: three macro time-series charts from `public/data/macro.json`
  - `news.html`: article feed with regex risk tags and severity filtering from `public/data/news.json`
  - `listed.html`: listed developer ratio table with composite health scores and expandable explanations from `public/data/listed.json`
- **Mock data pipeline** (`scripts/build_data.py`) that generates deterministic JSON outputs.
- **GitHub Actions job** (`.github/workflows/build-data.yml`) to regenerate and commit `public/data/*.json` every 6 hours or on demand.

## Repo layout

```text
public/
  index.html
  macro.html
  news.html
  listed.html
  assets/
    css/styles.css
    js/common.js
    js/macro.js
    js/news.js
    js/listed.js
  data/
    macro.json
    news.json
    listed.json
    status.json
scripts/
  build_data.py
  fetch_rss.py
  fetch_macro.py
  fetch_ratios.py
.github/workflows/
  build-data.yml
```

## Local run

1. Generate mock data:

```bash
python scripts/build_data.py
```

2. Serve the static site from `public/`:

```bash
cd public
python -m http.server 8000
```

3. Open `http://localhost:8000`.

## GitHub Pages deployment

Because this is a static site, it can be hosted directly on GitHub Pages.

### Option A: Deploy from `/docs` (recommended by Pages UI)

GitHub Pages natively supports `/docs` or root for branch deployments. If you prefer native Pages without an extra action:

1. Copy/sync `public/` to `/docs` in your branch, **or** set up a small sync step in your workflow.
2. In GitHub repo settings: **Pages** → **Build and deployment** → **Deploy from a branch**.
3. Select branch `main` and folder `/docs`.

### Option B: Deploy `public/` with a Pages workflow

Use a GitHub Pages workflow that uploads `public/` as the artifact. (Good when you want to keep `/public` as source of truth.)

> This repository currently includes only the data-build workflow. Add a Pages deploy workflow when you are ready to publish.

## Data model and scoring

`build_data.py` computes a **0–100 health score** (`higher = healthier`) using:

- Leverage penalties: `net_debt_to_equity`, `net_debt_to_ebitda`
- Liquidity penalties: `cash_to_short_debt`, `quick_ratio` (if present)
- Deterioration penalties when leverage worsens vs prior period

Status thresholds:

- `Green` >= 70
- `Amber` 40–69
- `Red` < 40

## News taxonomy (current mock implementation)

Themes and keywords:

- `refinancing`: refinanc|facility|bridge loan|maturity|liquidity
- `covenant`: covenant|waiver|breach
- `distress_sale`: discount|price cut|bulk sale|fire sale
- `project_delay`: delay|stop work|construction|TOP
- `legal`: winding up|lawsuit|judicial management|default
- `ratings`: downgrade|negative outlook|rating

Severity mapping:

- `critical`: legal/default/winding up
- `warning`: covenant breach/waiver or refinancing/bridge loan
- `watch`: distress sale/project delay/weak sales
- `info`: otherwise

Entity matching is also attempted using company names from listed developers.

## Future integration TODOs

- `scripts/fetch_macro.py`: data.gov.sg / SingStat / URA ingestion.
- `scripts/fetch_rss.py`: RSS fetch + normalize + classify.
- `scripts/fetch_ratios.py`: best-effort ratio parsing (e.g., StockAnalysis SGX pages).

