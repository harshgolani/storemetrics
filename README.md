# Storemetrics

E-commerce analytics dashboard built on the Instacart Market Basket Analysis dataset (3.4M orders, 206K users).

**Live Demo:** https://storemetrics.streamlit.app

---

## What it shows

Five analyses, each with a structured Finding / Why It Matters / Recommendation:

- **Reorder Frequency** — D7, D14, D28 reorder rates and median days between orders
- **Department Loyalty** — reorder rate by product category, top 10 departments
- **Customer Segments** — order frequency distribution across user cohorts
- **Peak Times** — hourly heatmap and day-of-week order volume
- **A/B Test** — morning vs evening shopper basket size with t-test and p-value

## Stack

Python · Pandas · Plotly · Streamlit · SciPy

## Key decisions

- `days_since_prior_order` is capped at 30 in the dataset — values of exactly 30 mean "30+ days" and are excluded from retention analysis to avoid skewed metrics
- Dataset excludes one-time buyers — all frequency and retention metrics reflect repeat customers only
- Dtype optimization reduces the prior orders file from ~1GB to ~309MB in memory
- Analysis is pre-computed from the full dataset and served as static JSON for fast load times on Streamlit Cloud

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To regenerate precomputed analysis from raw data:
```bash
# Download Instacart dataset from Kaggle into data/raw/
python3 scripts/precompute.py
```
