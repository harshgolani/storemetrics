import json
import pandas as pd # type: ignore
import streamlit as st # type: ignore

from src.charts import (
    chart_reorder_frequency,
    chart_reorder_by_department,
    chart_order_frequency,
    chart_peak_times,
    chart_ab_test,
)

st.set_page_config(
    page_title="Storemetrics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* ── Hide chrome ── */
    #MainMenu { display: none; }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stStatusWidget"] { display: none; }
    [data-testid="stSidebar"] { display: none; }

    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #0a0a0a;
        color: #e8e0dc;
    }
    .block-container {
        padding: 0 2.5rem 2rem;
        max-width: 1200px;
        margin: auto;
    }

    /* ── Sticky KPI bar ── */
    .kpi-sticky {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #0a0a0a;
        padding: 0.85rem 0 0.6rem;
    }
    .kpi-row {
        display: flex;
        gap: 12px;
    }
    .kpi-card {
        flex: 1;
        background: #111;
        border-radius: 8px;
        padding: 0.9rem 1.25rem 0.8rem;
        border: 1px solid #1e1614;
    }
    .kpi-number {
        color: #c4a090;
        font-size: 1.75rem;
        font-weight: 600;
        font-family: Inter, system-ui, sans-serif;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .kpi-label {
        color: #5a4e4a;
        font-size: 0.68rem;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-top: 0.3rem;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] { margin-top: 0.1rem; }
    [data-testid="stTabBar"] {
        background: transparent;
        border-bottom: 1px solid #1e1614;
        gap: 0;
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #7a6a65 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.70rem !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        padding: 0.65rem 1.25rem !important;
        border-bottom: 2px solid transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #c4a090 !important;
        border-bottom: 2px solid #c4a090 !important;
    }
    button[data-baseweb="tab"]:hover { color: #c4a090 !important; }
    [data-baseweb="tab-highlight"] { display: none; }
    [data-baseweb="tab-border"] { display: none; }

    /* ── Insight panel ── */
    .insight-panel {
        background: #111;
        border: 1px solid #1e1614;
        border-radius: 8px;
        padding: 0.9rem 1.25rem;
        margin-top: 0.6rem;
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .insight-row {
        display: flex;
        align-items: baseline;
        gap: 1rem;
        padding: 0.55rem 0;
    }
    .insight-row + .insight-row {
        border-top: 1px solid #1a1210;
    }
    .insight-label {
        color: #c4a090;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.60rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        white-space: nowrap;
        min-width: 9.5rem;
    }
    .insight-text {
        color: #c4b8b4;
        font-size: 0.875rem;
        font-family: Inter, system-ui, sans-serif;
        line-height: 1.5;
    }

    /* ── Chart background ── */
    [data-testid="stPlotlyChart"] { background: #0a0a0a; }
</style>
""", unsafe_allow_html=True)


def insight_panel(finding, why, recommendation):
    return f"""
<div class="insight-panel">
  <div class="insight-row">
    <span class="insight-label">Finding</span>
    <span class="insight-text">{finding}</span>
  </div>
  <div class="insight-row">
    <span class="insight-label">Why It Matters</span>
    <span class="insight-text">{why}</span>
  </div>
  <div class="insight-row">
    <span class="insight-label">Recommendation</span>
    <span class="insight-text">{recommendation}</span>
  </div>
</div>
"""


def load_precomputed():
    with open('assets/precomputed.json', 'r') as f:
        data = json.load(f)
    return (
        data['retention'],
        pd.DataFrame(data['dept_data']),
        {'stats': None, 'buckets': pd.DataFrame(data['freq_data']['buckets'])},
        {'hourly': pd.DataFrame(data['time_data']['hourly']), 'daily': pd.DataFrame(data['time_data']['daily'])},
        data['ab_data']
    )


# ── Load precomputed data ─────────────────────────────────────────────────────
retention, dept_data, freq_data, time_data, ab_data = load_precomputed()

median   = retention["median_days_between_orders"]
top_day  = time_data["daily"].sort_values("order_count", ascending=False).iloc[0]["day_name"]
buckets  = freq_data["buckets"]
low_pct  = buckets.loc[buckets["order_range"].astype(str) == "1-5",  "pct"].values[0]
high_pct = buckets.loc[buckets["order_range"].astype(str).isin(["21-50", "51-100"]), "pct"].sum()
diff     = abs(ab_data["morning_avg_basket"] - ab_data["evening_avg_basket"])

# ── Sticky KPI bar ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-sticky">
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-number">206K</div>
      <div class="kpi-label">Total Users</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-number">{median:.0f}</div>
      <div class="kpi-label">Median Reorder Days</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-number">67%</div>
      <div class="kpi-label">Top Dept - Dairy &amp; Eggs</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-number">{top_day}</div>
      <div class="kpi-label">Peak Day</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tab navigation ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Reorder Frequency",
    "Department Loyalty",
    "Customer Segments",
    "Peak Times",
    "A/B Test",
])

with tab1:
    st.plotly_chart(chart_reorder_frequency(retention), width="stretch")
    st.markdown(insight_panel(
        finding=f"The median customer reorders in <strong>{median:.0f} days</strong>, with the majority returning within 14 days.",
        why="A predictable two week replenishment cycle is short enough to intercept with timed outreach before intent fades.",
        recommendation="Send triggered re-engagement notifications at day 10-12 to reach customers before they consider ordering elsewhere.",
    ), unsafe_allow_html=True)

with tab2:
    st.plotly_chart(chart_reorder_by_department(dept_data), width="stretch")
    st.markdown(insight_panel(
        finding="Dairy &amp; Eggs leads with a <strong>67% reorder rate</strong>; personal care trails at the bottom with roughly 32%.",
        why="High-reorder categories are need driven staples that anchor loyalty; low-reorder categories signal channel-switching to Amazon or Target.",
        recommendation="Build subscription pricing around dairy and produce; run bundle promotions in personal care to compete with off platform alternatives.",
    ), unsafe_allow_html=True)

with tab3:
    st.plotly_chart(chart_order_frequency(freq_data), width="stretch")
    st.markdown(insight_panel(
        finding=f"<strong>{low_pct:.0f}%</strong> of users placed only 1–5 orders; <strong>{high_pct:.0f}%</strong> placed 21 or more.",
        why="The casual shopper majority represents untapped lifetime value - converting even a fraction to habitual buyers moves revenue significantly.",
        recommendation="Trigger onboarding nudges after orders 2–3 for light users; protect power users with loyalty perks before they churn.",
    ), unsafe_allow_html=True)

with tab4:
    st.plotly_chart(chart_peak_times(time_data), width="stretch")
    st.markdown(insight_panel(
        finding=f"<strong>{top_day}</strong> dominates order volume, followed closely by Monday - together accounting for over a third of weekly orders.",
        why="The Sunday/Monday peak reflects weekly meal-planning behavior when purchase intent is naturally highest.",
        recommendation="Schedule promotional push notifications on Saturday evening or Sunday morning to align with peak intent windows.",
    ), unsafe_allow_html=True)

with tab5:
    st.plotly_chart(chart_ab_test(ab_data), width="stretch")
    sig_text = "statistically significant" if ab_data["significant"] else "not statistically significant"
    st.markdown(insight_panel(
        finding=f"Morning vs evening basket sizes differ by <strong>{diff:.2f} items</strong> (p = {ab_data['p_value']:.4f}) - {sig_text} but not practically significant.",
        why="With 32M+ order lines, even negligible differences register as significant - p value alone is not a reliable decision criterion at this scale.",
        recommendation="Set a minimum effect size threshold (1+ items) before acting on A/B results; evaluate revenue per order as a more actionable metric.",
    ), unsafe_allow_html=True)
