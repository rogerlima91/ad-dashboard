import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Ad Dashboard", layout="wide")

# ── DoubleVerify brand colours ────────────────────────────────────────────────
DV_CYAN    = "#00b2a9"
DV_NAVY    = "#14113b"
DV_GREEN   = "#34b233"
DV_PURPLE  = "#6e2ca9"
DV_MAGENTA = "#c70099"
DV_PALETTE = [DV_CYAN, DV_GREEN, DV_PURPLE, DV_MAGENTA, DV_NAVY]

# ── Global CSS — card styling, typography, section headers ────────────────────
st.markdown("""
<style>
    /* Overall page font */
    html, body, [class*="css"] {
        font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e8e8f0;
        border-top: 4px solid #00b2a9;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(20,17,59,0.07);
    }
    [data-testid="metric-container"] label {
        font-size: 12px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 700;
        color: #14113b;
    }

    /* Section subheaders */
    h3 {
        color: #14113b !important;
        font-weight: 700 !important;
        margin-top: 1.4rem !important;
        border-bottom: 2px solid #00b2a9;
        padding-bottom: 6px;
    }

    /* Insight card */
    .insight-card {
        background: #f4f6fb;
        border-left: 4px solid #00b2a9;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 14px;
        color: #14113b;
        line-height: 1.6;
    }

    /* CPM table */
    .cpm-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    .cpm-table th {
        background: #14113b;
        color: white;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
        border-radius: 4px;
    }
    .cpm-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #e8e8f0;
        color: #374151;
    }
    .cpm-best  { color: #34b233; font-weight: 700; }
    .cpm-worst { color: #c70099; font-weight: 700; }
    .badge-best  { background:#e6f7e6; color:#34b233; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:700; }
    .badge-worst { background:#fce8f5; color:#c70099; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ── Generate fake campaign data ───────────────────────────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)
    campaigns = ["Brand Awareness", "Retargeting", "Prospecting", "Seasonal Sale", "Product Launch"]
    df = pd.DataFrame({
        "campaign":    np.random.choice(campaigns, 50),
        "impressions": np.random.randint(5000, 100000, 50),
        "clicks":      np.random.randint(50, 2000, 50),
        "spend_usd":   np.round(np.random.uniform(50, 1500, 50), 2),
    })
    df["clicks"]  = df[["clicks", "impressions"]].min(axis=1)
    df["ctr"]     = df["clicks"] / df["impressions"]
    df["cpm"]     = df["spend_usd"] / df["impressions"] * 1000
    return df

df = load_data()

# ── Helper: apply clean chart style to any axis ───────────────────────────────
def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors="#6b7280", labelsize=9)
    ax.set_axisbelow(True)

# ── Header — title left, logo right ──────────────────────────────────────────
col_title, col_logo = st.columns([6, 1])
with col_title:
    st.title("Ad Tech Campaign Dashboard")
    st.markdown("<p style='color:#6b7280;font-size:14px;margin-top:-12px;'>Campaign performance across impressions, clicks, spend, CTR and CPM.</p>", unsafe_allow_html=True)
with col_logo:
    st.image(
        "https://images.seeklogo.com/logo-png/41/1/doubleverify-logo-png_seeklogo-411808.png",
        width=160,
    )

# ── Sidebar filter ────────────────────────────────────────────────────────────
st.sidebar.header("Filters")
campaign_options  = ["All"] + sorted(df["campaign"].unique().tolist())
selected_campaign = st.sidebar.selectbox("Select Campaign", campaign_options)

filtered_df = df.copy() if selected_campaign == "All" else df[df["campaign"] == selected_campaign].copy()

# ── Summary metrics ───────────────────────────────────────────────────────────
st.subheader("Summary Metrics")

total_impressions = filtered_df["impressions"].sum()
total_clicks      = filtered_df["clicks"].sum()
total_spend       = filtered_df["spend_usd"].sum()
avg_ctr           = filtered_df["ctr"].mean()
avg_cpm           = filtered_df["cpm"].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Impressions", f"{total_impressions:,}")
col2.metric("Total Clicks",      f"{total_clicks:,}")
col3.metric("Total Spend",       f"${total_spend:,.0f}")
col4.metric("Avg CTR",           f"{avg_ctr:.2%}")
col5.metric("Avg CPM",           f"${avg_cpm:,.0f}")

# ── Row: Pie chart (left) + CPM best/worst table (right) ─────────────────────
st.subheader("CTR by Campaign & CPM Performance")

pie_col, cpm_col = st.columns([1.4, 1])

# -- Pie chart: share of average CTR per campaign --
with pie_col:
    chart_df = filtered_df.groupby("campaign")["ctr"].mean().reset_index()
    pie_colors = [DV_PALETTE[i % len(DV_PALETTE)] for i in range(len(chart_df))]

    fig, ax = plt.subplots(figsize=(5, 3.5))
    wedges, texts, autotexts = ax.pie(
        chart_df["ctr"],
        labels=chart_df["campaign"],
        colors=pie_colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for t in texts:
        t.set_fontsize(8)
        t.set_color("#374151")
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("CTR Share by Campaign", fontsize=11, fontweight="bold", color=DV_NAVY, pad=10)
    plt.tight_layout()
    st.pyplot(fig)

# -- CPM best / worst table --
with cpm_col:
    cpm_summary = (
        filtered_df.groupby("campaign")["cpm"]
        .mean()
        .reset_index()
        .sort_values("cpm")
        .reset_index(drop=True)
    )

    # Top 2 best (lowest CPM) and top 2 worst (highest CPM)
    best  = cpm_summary.head(2)
    worst = cpm_summary.tail(2).iloc[::-1]  # highest first

    rows_best  = "".join(
        f"<tr><td>{r['campaign']}</td><td class='cpm-best'>${r['cpm']:,.0f}</td><td><span class='badge-best'>BEST</span></td></tr>"
        for _, r in best.iterrows()
    )
    rows_worst = "".join(
        f"<tr><td>{r['campaign']}</td><td class='cpm-worst'>${r['cpm']:,.0f}</td><td><span class='badge-worst'>WORST</span></td></tr>"
        for _, r in worst.iterrows()
    )

    st.markdown(f"""
    <br><br>
    <p style='font-weight:700;color:{DV_NAVY};font-size:14px;margin-bottom:8px;'>Top 2 Best CPM</p>
    <table class='cpm-table'>
        <tr><th>Campaign</th><th>Avg CPM</th><th></th></tr>
        {rows_best}
    </table>
    <br>
    <p style='font-weight:700;color:{DV_NAVY};font-size:14px;margin-bottom:8px;'>Top 2 Worst CPM</p>
    <table class='cpm-table'>
        <tr><th>Campaign</th><th>Avg CPM</th><th></th></tr>
        {rows_worst}
    </table>
    <p style='font-size:11px;color:#9ca3af;margin-top:8px;'>Lower CPM = more efficient spend per 1,000 impressions.</p>
    """, unsafe_allow_html=True)

# ── Horizontal bar chart — total spend per campaign ───────────────────────────
st.subheader("Total Spend by Campaign")

spend_df     = filtered_df.groupby("campaign")["spend_usd"].sum().reset_index()
spend_df     = spend_df.sort_values("spend_usd", ascending=True)
spend_colors = [DV_PALETTE[i % len(DV_PALETTE)] for i in range(len(spend_df))]

fig2, ax2 = plt.subplots(figsize=(8, 3))
hbars = ax2.barh(spend_df["campaign"], spend_df["spend_usd"], color=spend_colors, edgecolor="white", height=0.55)
ax2.bar_label(hbars, labels=[f"${v:,.0f}" for v in spend_df["spend_usd"]], padding=5, fontsize=9, color="#374151")
ax2.set_xlabel("Total Spend (USD)", fontsize=9, color="#6b7280")
ax2.set_xlim(0, spend_df["spend_usd"].max() * 1.2)
ax2.xaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.6, color="#d1d5db")
style_ax(ax2)
plt.tight_layout()
st.pyplot(fig2)

# ── Insights ──────────────────────────────────────────────────────────────────
st.subheader("Campaign Insights")

# Build summary stats needed for the insight copy
summary = (
    filtered_df.groupby("campaign")
    .agg(avg_ctr=("ctr", "mean"), avg_cpm=("cpm", "mean"), total_spend=("spend_usd", "sum"))
    .reset_index()
)

best_ctr_row   = summary.loc[summary["avg_ctr"].idxmax()]
worst_ctr_row  = summary.loc[summary["avg_ctr"].idxmin()]
best_cpm_row   = summary.loc[summary["avg_cpm"].idxmin()]   # lowest CPM = most efficient
worst_cpm_row  = summary.loc[summary["avg_cpm"].idxmax()]
top_spend_row  = summary.loc[summary["total_spend"].idxmax()]

insights = [
    f"<b>{best_ctr_row['campaign']}</b> leads on click-through rate with an avg CTR of "
    f"<b>{best_ctr_row['avg_ctr']:.2%}</b>, making it the strongest campaign for driving audience engagement. "
    f"<b>{worst_ctr_row['campaign']}</b> trails at <b>{worst_ctr_row['avg_ctr']:.2%}</b> — "
    f"consider reviewing its creative or targeting.",

    f"<b>{best_cpm_row['campaign']}</b> is the most cost-efficient campaign with an avg CPM of "
    f"<b>${best_cpm_row['avg_cpm']:,.0f}</b>, delivering the most impressions per dollar spent. "
    f"In contrast, <b>{worst_cpm_row['campaign']}</b> has the highest CPM at "
    f"<b>${worst_cpm_row['avg_cpm']:,.0f}</b> — its placements may be in premium inventory.",

    f"<b>{top_spend_row['campaign']}</b> accounts for the largest share of budget at "
    f"<b>${top_spend_row['total_spend']:,.0f}</b>. Cross-referencing its CTR of "
    f"<b>{summary.loc[summary['campaign']==top_spend_row['campaign'], 'avg_ctr'].values[0]:.2%}</b> "
    f"against lower-spend campaigns can reveal whether this investment is proportionally justified.",
]

for insight in insights:
    st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)

# ── Raw data table ────────────────────────────────────────────────────────────
st.subheader("Raw Data")

display_df              = filtered_df.copy()
display_df["ctr"]       = display_df["ctr"].map("{:.2%}".format)
display_df["cpm"]       = display_df["cpm"].map("${:,.0f}".format)
display_df["spend_usd"] = display_df["spend_usd"].map("${:,.0f}".format)
display_df.columns      = ["Campaign", "Impressions", "Clicks", "Spend", "CTR", "CPM"]

st.dataframe(display_df, use_container_width=True)
