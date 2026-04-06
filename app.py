import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Ad Dashboard", layout="wide")

# ── DoubleVerify brand colours ────────────────────────────────────────────────
DV_CYAN    = "#00b2a9"
DV_NAVY    = "#14113b"
DV_GREEN   = "#34b233"
DV_PURPLE  = "#6e2ca9"
DV_MAGENTA = "#c70099"

# Ordered palette used to colour bars (one colour per campaign)
DV_PALETTE = [DV_CYAN, DV_GREEN, DV_PURPLE, DV_MAGENTA, DV_NAVY]

# Custom matplotlib colormap that blends across the DV palette
dv_cmap = LinearSegmentedColormap.from_list("dv", DV_PALETTE)

# ── Generate fake campaign data ───────────────────────────────────────────────
# Using the same seed as our other scripts so the numbers are consistent
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

    # Make sure clicks never exceed impressions
    df["clicks"] = df[["clicks", "impressions"]].min(axis=1)

    # Calculate CTR and CPM for each row
    df["ctr"] = df["clicks"] / df["impressions"]
    df["cpm"] = df["spend_usd"] / df["impressions"] * 1000

    return df

df = load_data()

# ── Header row — title on the left, DV logo on the right ─────────────────────
col_title, col_logo = st.columns([6, 1])
with col_title:
    st.title("Ad Tech Campaign Dashboard")
    st.write("A simple dashboard to explore ad campaign performance across impressions, clicks, spend, CTR, and CPM.")
with col_logo:
    st.image(
        "https://images.seeklogo.com/logo-png/41/1/doubleverify-logo-png_seeklogo-411808.png",
        width=160,
    )

# ── Sidebar filter ────────────────────────────────────────────────────────────
st.sidebar.header("Filters")

# Get the list of campaigns and add an "All" option at the top
campaign_options = ["All"] + sorted(df["campaign"].unique().tolist())
selected_campaign = st.sidebar.selectbox("Select Campaign", campaign_options)

# Apply the filter — if "All" is selected, show everything
if selected_campaign == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df["campaign"] == selected_campaign].copy()

# ── Summary metrics row ───────────────────────────────────────────────────────
st.subheader("Summary Metrics")

total_impressions = filtered_df["impressions"].sum()
total_clicks      = filtered_df["clicks"].sum()
total_spend       = filtered_df["spend_usd"].sum()
avg_ctr           = filtered_df["ctr"].mean()
avg_cpm           = filtered_df["cpm"].mean()

# Display metrics side by side using Streamlit columns
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Impressions", f"{total_impressions:,}")
col2.metric("Total Clicks",      f"{total_clicks:,}")
col3.metric("Total Spend",       f"${total_spend:,.0f}")
col4.metric("Avg CTR",           f"{avg_ctr:.2%}")
col5.metric("Avg CPM",           f"${avg_cpm:,.0f}")

# ── Bar chart — CTR per campaign ──────────────────────────────────────────────
st.subheader("Average CTR by Campaign")

# Group by campaign and calculate average CTR
chart_df = filtered_df.groupby("campaign")["ctr"].mean().reset_index()
chart_df["ctr_pct"] = chart_df["ctr"] * 100  # Convert to percentage for display

# Pick one DV colour per bar, cycling through the palette if needed
bar_colors = [DV_PALETTE[i % len(DV_PALETTE)] for i in range(len(chart_df))]

# Build the chart with matplotlib
fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.bar(chart_df["campaign"], chart_df["ctr_pct"], color=bar_colors, edgecolor="white")

ax.bar_label(bars, fmt="%.2f%%", padding=4, fontsize=9)
ax.set_ylabel("Avg CTR (%)")
ax.set_ylim(0, chart_df["ctr_pct"].max() * 1.25)
ax.yaxis.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=15, ha="right")
plt.tight_layout()

st.pyplot(fig)

# ── Horizontal bar chart — total spend per campaign ───────────────────────────
st.subheader("Total Spend by Campaign")

# Group by campaign and sum spend
spend_df = filtered_df.groupby("campaign")["spend_usd"].sum().reset_index()
spend_df = spend_df.sort_values("spend_usd", ascending=True)  # ascending so largest bar is at the top

# Pick one DV colour per bar
spend_colors = [DV_PALETTE[i % len(DV_PALETTE)] for i in range(len(spend_df))]

# Build the horizontal bar chart
fig2, ax2 = plt.subplots(figsize=(9, 4))
hbars = ax2.barh(spend_df["campaign"], spend_df["spend_usd"], color=spend_colors, edgecolor="white")

# Add spend labels at the end of each bar (formatted with comma and no decimals)
ax2.bar_label(hbars, labels=[f"${v:,.0f}" for v in spend_df["spend_usd"]], padding=4, fontsize=9)
ax2.set_xlabel("Total Spend (USD)")
ax2.set_xlim(0, spend_df["spend_usd"].max() * 1.2)
ax2.xaxis.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)
ax2.set_axisbelow(True)
plt.tight_layout()

st.pyplot(fig2)

# ── Raw data table ────────────────────────────────────────────────────────────
st.subheader("Raw Data")

# Format columns for display before showing the table
display_df = filtered_df.copy()
display_df["ctr"]       = display_df["ctr"].map("{:.2%}".format)
display_df["cpm"]       = display_df["cpm"].map("${:,.0f}".format)
display_df["spend_usd"] = display_df["spend_usd"].map("${:,.0f}".format)
display_df.columns      = ["Campaign", "Impressions", "Clicks", "Spend", "CTR", "CPM"]

st.dataframe(display_df, use_container_width=True)
