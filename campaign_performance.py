import pandas as pd
import numpy as np

# ── Reproducible random data ──────────────────────────────────────────────────
np.random.seed(42)

campaigns = ["Brand Awareness", "Retargeting", "Prospecting", "Seasonal Sale", "Product Launch"]

# Generate 50 rows of fake ad impression data
data = {
    "campaign":    np.random.choice(campaigns, 50),
    "impressions": np.random.randint(5000, 100000, 50),
    "clicks":      np.random.randint(50, 2000, 50),
    "conversions": np.random.randint(0, 100, 50),
    "spend_usd":   np.round(np.random.uniform(50, 1500, 50), 2),
}

df = pd.DataFrame(data)

# Make sure clicks never exceed impressions, conversions never exceed clicks
df["clicks"]      = df[["clicks", "impressions"]].min(axis=1)
df["conversions"] = df[["conversions", "clicks"]].min(axis=1)

# ── Calculate per-row metrics ─────────────────────────────────────────────────
df["ctr"]  = df["clicks"] / df["impressions"]               # Click-through rate
df["cpm"]  = df["spend_usd"] / df["impressions"] * 1000     # Cost per 1000 impressions
df["cpc"]  = df["spend_usd"] / df["clicks"]                 # Cost per click
df["cvr"]  = df["conversions"] / df["clicks"]               # Conversion rate
df["cpa"]  = df["spend_usd"] / df["conversions"].replace(0, np.nan)  # Cost per acquisition (skip zeros)

# ── Aggregate metrics by campaign ────────────────────────────────────────────
summary = df.groupby("campaign").agg(
    impressions  = ("impressions",  "sum"),
    clicks       = ("clicks",       "sum"),
    conversions  = ("conversions",  "sum"),
    spend_usd    = ("spend_usd",    "sum"),
).reset_index()

# Recalculate blended metrics from totals (more accurate than averaging per-row)
summary["ctr"] = summary["clicks"]      / summary["impressions"]
summary["cpm"] = summary["spend_usd"]   / summary["impressions"] * 1000
summary["cpc"] = summary["spend_usd"]   / summary["clicks"]
summary["cvr"] = summary["conversions"] / summary["clicks"]
summary["cpa"] = summary["spend_usd"]   / summary["conversions"].replace(0, np.nan)

# ── Rank campaigns by key metrics ────────────────────────────────────────────
# Lower spend metrics (CPM, CPC, CPA) = better, so rank ascending
# Higher engagement metrics (CTR, CVR) = better, so rank descending
summary["ctr_rank"] = summary["ctr"].rank(ascending=False).astype(int)
summary["cpa_rank"] = summary["cpa"].rank(ascending=True).astype(int)   # lower CPA is better
summary["cvr_rank"] = summary["cvr"].rank(ascending=False).astype(int)

# ── Print the performance report ─────────────────────────────────────────────
W = 80
print("=" * W)
print(f"{'CAMPAIGN PERFORMANCE ANALYSIS':^{W}}")
print("=" * W)

# -- Volume & spend table --
print(f"\n{'[ Volume & Spend ]'}")
print(f"  {'Campaign':<20} {'Impressions':>12} {'Clicks':>8} {'Conversions':>12} {'Spend':>10}")
print(f"  {'-'*66}")
for _, r in summary.iterrows():
    print(f"  {r['campaign']:<20} {int(r['impressions']):>12,} {int(r['clicks']):>8,} "
          f"{int(r['conversions']):>12,} ${r['spend_usd']:>9.2f}")

# -- Efficiency metrics table --
print(f"\n{'[ Efficiency Metrics ]'}")
print(f"  {'Campaign':<20} {'CTR':>7} {'CVR':>7} {'CPM':>8} {'CPC':>8} {'CPA':>8}")
print(f"  {'-'*62}")
for _, r in summary.iterrows():
    cpa_str = f"${r['cpa']:>7.2f}" if pd.notna(r['cpa']) else "     N/A"
    print(f"  {r['campaign']:<20} {r['ctr']:>6.2%} {r['cvr']:>6.2%} "
          f"${r['cpm']:>7.2f} ${r['cpc']:>7.2f} {cpa_str}")

# -- Rankings table --
print(f"\n{'[ Campaign Rankings ]'}  (1 = best)")
print(f"  {'Campaign':<20} {'CTR Rank':>10} {'CVR Rank':>10} {'CPA Rank':>10}")
print(f"  {'-'*52}")
for _, r in summary.iterrows():
    print(f"  {r['campaign']:<20} {'#'+str(r['ctr_rank']):>10} {'#'+str(r['cvr_rank']):>10} {'#'+str(r['cpa_rank']):>10}")

# -- Highlight best performers --
best_ctr = summary.loc[summary["ctr"].idxmax(), "campaign"]
best_cvr = summary.loc[summary["cvr"].idxmax(), "campaign"]
best_cpa = summary.loc[summary["cpa"].idxmin(), "campaign"]

print(f"\n{'[ Top Performers ]'}")
print(f"  Highest CTR : {best_ctr}")
print(f"  Highest CVR : {best_cvr}")
print(f"  Lowest CPA  : {best_cpa}")

print("\n" + "=" * W)
print("Done. Campaign performance analysis complete.")
