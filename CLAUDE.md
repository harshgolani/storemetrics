# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
streamlit run app.py

# Install dependencies
pip install -r requirements.txt
```

There are no tests or linting configured.

## Architecture

This is a single-page Streamlit analytics dashboard analysing the [Instacart Market Basket dataset](https://www.kaggle.com/c/instacart-market-basket-analysis). The data pipeline is: **load → analyse → chart → render**.

```
app.py              # Entry point: Streamlit layout, KPI cards, calls analysis + chart functions
src/
  data_loader.py   # Loads all 6 CSVs with optimized dtypes; called once via @st.cache_data
  analysis.py      # Pure pandas/scipy functions; each returns a dict or DataFrame
  charts.py        # Pure Plotly functions; each accepts a dict/DataFrame, returns a Figure
data/raw/           # Raw Instacart CSVs (not committed — must be downloaded separately)
DECISIONS.md        # Records analytical decisions and dataset gotchas — read this before changing analysis logic
```

**Data flow in `app.py`:**
1. `cached_load_data()` — loads all 6 CSVs once and caches them
2. Five analysis functions run on the cached DataFrames, each returning a plain Python dict
3. Five chart functions consume those dicts and return Plotly `Figure` objects
4. Streamlit renders KPI cards (raw HTML), charts (`st.plotly_chart`), and insight boxes (raw HTML)

**Styling:** All Streamlit chrome is hidden via injected CSS. The design system uses a dark palette (`#0a0a0a` background, `#c4a090` accent, `#e8e0dc` text). Chart theme constants are defined at the top of `charts.py` (`_BG`, `_ACCENT`, etc.) — use these when adding charts rather than hardcoding hex values.

## Dataset notes (from DECISIONS.md)

- `days_since_prior_order` is **capped at 30** in the raw data — values of exactly 30 mean "30+ days" and are excluded from retention analysis to avoid skewed metrics
- The dataset **excludes one-time buyers** and has a minimum of 4 orders per user — all frequency/retention metrics reflect repeat customers only
- `aisle_id` max is 134, which exceeds `int8` (127) — it uses `int16`; `days_since_prior_order` uses `float32` because NaN cannot be stored in integer columns
- The prior orders file (`order_products__prior.csv`) is the large file (~1 GB unoptimized, ~309 MB with typed dtypes)
