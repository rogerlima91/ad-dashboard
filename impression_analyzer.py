import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

campaigns = ["Brand Awareness", "Retargeting", "Prospecting", "Seasonal Sale", "Product Launch"]

data = {
    "campaign": np.random.choice(campaigns, 50),
    "impressions": np.random.randint(5000, 100000, 50),
    "clicks": np.random.randint(50, 2000, 50),
    "spend_usd": np.round(np.random.uniform(50, 1500, 50), 2),
}

df = pd.DataFrame(data)
df["clicks"] = df[["clicks", "impressions"]].min(axis=1)  # clicks can't exceed impressions

df["ctr"] = df["clicks"] / df["impressions"]
df["cpm"] = df["spend_usd"] / df["impressions"] * 1000

summary = (
    df.groupby("campaign")
    .agg(
        rows=("campaign", "count"),
        total_impressions=("impressions", "sum"),
        total_clicks=("clicks", "sum"),
        total_spend=("spend_usd", "sum"),
        avg_ctr=("ctr", "mean"),
        avg_cpm=("cpm", "mean"),
    )
    .reset_index()
)

print("=" * 75)
print(f"{'AD IMPRESSION REPORT — ALL ROWS':^75}")
print("=" * 75)
print(f"{'#':>3} {'Campaign':<20} {'Impressions':>12} {'Clicks':>8} {'Spend':>9} {'CTR':>7} {'CPM':>7}")
print("-" * 75)

df_sorted = df.sort_values("campaign").reset_index(drop=True)
for i, row in df_sorted.iterrows():
    print(
        f"{i+1:>3} {row['campaign']:<20} {int(row['impressions']):>12,} "
        f"{int(row['clicks']):>8,} ${row['spend_usd']:>8.2f} "
        f"{row['ctr']:>6.2%} ${row['cpm']:>6.2f}"
    )

print()
print("=" * 75)
print(f"{'SUMMARY BY CAMPAIGN':^75}")
print("=" * 75)
print(f"{'Campaign':<20} {'Rows':>4} {'Impressions':>12} {'Clicks':>8} {'Spend':>9} {'CTR':>7} {'CPM':>7}")
print("-" * 75)

for _, row in summary.iterrows():
    print(
        f"{row['campaign']:<20} {int(row['rows']):>4} {int(row['total_impressions']):>12,} "
        f"{int(row['total_clicks']):>8,} ${row['total_spend']:>8.2f} "
        f"{row['avg_ctr']:>6.2%} ${row['avg_cpm']:>6.2f}"
    )

print("-" * 65)
totals = summary[["total_impressions", "total_clicks", "total_spend"]].sum()
overall_ctr = totals["total_clicks"] / totals["total_impressions"]
overall_cpm = totals["total_spend"] / totals["total_impressions"] * 1000
print(
    f"{'TOTAL':<20} {50:>4} {int(totals['total_impressions']):>12,} "
    f"{int(totals['total_clicks']):>8,} ${totals['total_spend']:>8.2f} "
    f"{overall_ctr:>6.2%} ${overall_cpm:>6.2f}"
)
print("=" * 65)

# Bar chart — avg CTR per campaign
fig, ax = plt.subplots(figsize=(8, 5))

cmap = plt.get_cmap("cool")
colors = [cmap(i / (len(summary) - 1)) for i in range(len(summary))]
bars = ax.bar(summary["campaign"], summary["avg_ctr"] * 100, color=colors, edgecolor="white")

ax.bar_label(bars, fmt="%.2f%%", padding=4, fontsize=9)
ax.set_title("Average CTR by Campaign", fontsize=14, fontweight="bold")
ax.set_xlabel("Campaign")
ax.set_ylabel("Avg CTR (%)")
ax.set_ylim(0, summary["avg_ctr"].max() * 100 * 1.2)
ax.yaxis.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig("chart.png", dpi=150)
print("Chart saved to chart.png")
