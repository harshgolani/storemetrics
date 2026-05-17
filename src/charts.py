import plotly.graph_objects as go # type: ignore
from plotly.subplots import make_subplots # type: ignore

_BG = "#0a0a0a"
_ACCENT = "#c4a090"
_TEXT = "#e8e0dc"
_MUTED = "#7a6a65"
_SUBTLE = "#2a1f1c"
_FONT = "Inter, system-ui, sans-serif"

_BASE = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_BG,
    font=dict(family=_FONT, color=_TEXT, size=13),
    margin=dict(l=10, r=40, t=60, b=20),
    showlegend=False,
)

def _axis(**kw):
    return dict(showgrid=False, zeroline=False, showline=False, ticks="", **kw)


def chart_reorder_frequency(retention_data):
    """Horizontal bar chart: % of users who reordered within 7/14/28 days."""
    labels = ["Within 28 days", "Within 14 days", "Within 7 days"]
    values = [
        retention_data["reorder_within_28_days_pct"],
        retention_data["reorder_within_14_days_pct"],
        retention_data["reorder_within_7_days_pct"],
    ]
    colors = ["rgba(196,160,144,0.45)", "rgba(196,160,144,0.72)", _ACCENT]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color=_TEXT, size=13),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))

    median = retention_data["median_days_between_orders"]
    fig.add_annotation(
        x=0.99, y=0.04,
        xref="paper", yref="paper",
        text=f"Median reorder: <b>{median:.1f} days</b>",
        showarrow=False,
        font=dict(color=_MUTED, size=12, family=_FONT),
        xanchor="right", yanchor="bottom",
    )

    fig.update_layout(
        **_BASE,
        title=dict(text="Reorder Frequency", font=dict(size=18)),
        xaxis=_axis(title="% of users", range=[0, max(values) * 1.28]),
        yaxis=_axis(tickfont=dict(size=13)),
        bargap=0.35,
    )
    return fig


def chart_reorder_by_department(dept_data):
    """Horizontal bar chart: reorder rate by department, top 10 highest."""
    top10 = dept_data.head(10).sort_values("reorder_rate", ascending=True)

    norm = (top10["reorder_rate"] - top10["reorder_rate"].min())
    norm = norm / norm.max() if norm.max() > 0 else norm

    def _lerp_hex(t):
        r = int(0x7a + t * (0xc4 - 0x7a))
        g = int(0x6a + t * (0xa0 - 0x6a))
        b = int(0x65 + t * (0x90 - 0x65))
        return f"#{r:02x}{g:02x}{b:02x}"

    colors = [_lerp_hex(float(t)) for t in norm]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10["reorder_rate"],
        y=top10["department"].str.title(),
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in top10["reorder_rate"]],
        textposition="outside",
        textfont=dict(color=_TEXT, size=12),
        hovertemplate="%{y}: %{x:.1f}% reorder rate<extra></extra>",
    ))

    fig.update_layout(
        **_BASE,
        title=dict(text="Reorder Rate by Department — Top 10", font=dict(size=18)),
        xaxis=_axis(title="Reorder Rate (%)", range=[0, top10["reorder_rate"].max() * 1.2]),
        yaxis=_axis(tickfont=dict(size=12)),
        bargap=0.28,
    )
    return fig


def chart_order_frequency(freq_data):
    """Vertical bar chart: users per order-frequency bucket with % labels."""
    buckets = freq_data["buckets"]
    x = buckets["order_range"].astype(str).tolist()
    y = buckets["user_count"].tolist()
    pct = buckets["pct"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        marker=dict(color=_ACCENT, line=dict(width=0)),
        text=[f"{p:.1f}%" for p in pct],
        textposition="outside",
        textfont=dict(color=_TEXT, size=13),
        hovertemplate="Orders %{x}<br>%{y:,} users (%{text})<extra></extra>",
    ))

    fig.update_layout(
        **_BASE,
        title=dict(text="Order Frequency Distribution", font=dict(size=18)),
        xaxis=_axis(title="Orders per User", tickfont=dict(size=13)),
        yaxis=_axis(title="Number of Users", range=[0, max(y) * 1.18]),
        bargap=0.3,
    )
    return fig


def chart_peak_times(time_data):
    """Two-panel figure: hourly heatmap (top) + daily bar chart (bottom)."""
    hourly = time_data["hourly"]
    daily = time_data["daily"]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["Order Volume by Hour of Day", "Order Volume by Day of Week"],
        row_heights=[0.38, 0.62],
        vertical_spacing=0.20,
    )

    # — Hourly heatmap (1 × 24)
    counts = (
        hourly.set_index("hour")["order_count"]
        .reindex(range(24), fill_value=0)
    )
    hour_labels = [f"{h:02d}:00" for h in range(24)]
    colorscale = [[0, "#120806"], [0.4, "#5c2e22"], [0.75, "#9e6654"], [1, _ACCENT]]

    fig.add_trace(
        go.Heatmap(
            z=[counts.tolist()],
            x=hour_labels,
            y=[""],
            colorscale=colorscale,
            showscale=False,
            hovertemplate="%{x} — %{z:,} orders<extra></extra>",
        ),
        row=1, col=1,
    )

    # — Daily bar chart
    day_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    daily_sorted = (
        daily.set_index("day_name")
        .reindex(day_order)
        .reset_index()
        .fillna(0)
    )
    day_counts = daily_sorted["order_count"].tolist()

    peak_idx = int(daily_sorted["order_count"].idxmax())
    bar_colors = [_ACCENT if i == peak_idx else "rgba(196,160,144,0.5)"
                  for i in range(len(day_counts))]

    fig.add_trace(
        go.Bar(
            x=daily_sorted["day_name"],
            y=day_counts,
            marker=dict(color=bar_colors, line=dict(width=0)),
            hovertemplate="%{x}: %{y:,} orders<extra></extra>",
        ),
        row=2, col=1,
    )

    fig.update_layout(
        **_BASE,
        title=dict(text="Peak Ordering Times", font=dict(size=18)),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="")
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False, ticks="")

    for ann in fig.layout.annotations:
        ann.font.color = _TEXT
        ann.font.size = 13
        ann.font.family = _FONT

    return fig


def chart_ab_test(ab_data):
    """Grouped bar chart: morning vs evening average basket size with p-value annotation."""
    groups = ["Morning Shoppers<br><sup>6 am – 12 pm</sup>", "Evening Shoppers<br><sup>5 pm – 11 pm</sup>"]
    baskets = [ab_data["morning_avg_basket"], ab_data["evening_avg_basket"]]
    users = [ab_data["morning_users"], ab_data["evening_users"]]
    colors = [_ACCENT, "rgba(196,160,144,0.5)"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=groups,
        y=baskets,
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{b:.2f}" for b in baskets],
        textposition="outside",
        textfont=dict(color=_TEXT, size=14),
        customdata=users,
        hovertemplate="%{x}<br>Avg basket: <b>%{y:.2f}</b> items<br>n = %{customdata:,}<extra></extra>",
        width=0.4,
    ))

    p_val = ab_data["p_value"]
    significant = ab_data["significant"]
    sig_label = "Statistically significant (p < 0.05)" if significant else "Not significant (p ≥ 0.05)"
    ann_color = _ACCENT if significant else _MUTED

    fig.add_annotation(
        x=0.5, y=0.97,
        xref="paper", yref="paper",
        text=f"p = {p_val:.4f} — {sig_label}",
        showarrow=False,
        font=dict(color=ann_color, size=12, family=_FONT),
        xanchor="center", yanchor="top",
        bgcolor="rgba(20,10,8,0.85)",
        bordercolor=ann_color,
        borderwidth=1,
        borderpad=6,
    )

    fig.update_layout(
        **_BASE,
        title=dict(text="A/B Test: Basket Size by Shopping Window", font=dict(size=18)),
        xaxis=_axis(tickfont=dict(size=13)),
        yaxis=_axis(title="Avg Basket Size (items)", range=[0, max(baskets) * 1.22]),
        bargap=0.5,
    )
    return fig
