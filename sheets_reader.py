import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ── Connect to Google Sheets ──────────────────────────────────────────────────
# These scopes allow read access to Sheets and Google Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# Load the service account credentials from the local file
creds  = Credentials.from_service_account_file("credentials/google-credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

# ── Read data from the spreadsheet ────────────────────────────────────────────
SPREADSHEET_ID = "1Y7YAD9HbM8VCJzEhjH0rhusF0jRqM8iVuiI_nX4Wch0"

spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet   = spreadsheet.get_worksheet(0)           # reads the first sheet tab

print(f"Connected to: '{spreadsheet.title}'")
print(f"Reading sheet: '{worksheet.title}'")

# ── Load into a pandas DataFrame ─────────────────────────────────────────────
# get_all_values() returns every row as a list
# Row 0 contains placeholder letters (A, B, C, D) — skip it
# Row 1 contains the real column headers (campaign, impressions, etc.)
all_values = worksheet.get_all_values()
df         = pd.DataFrame(all_values[2:], columns=all_values[1])

print(f"\n{len(df)} rows loaded.\n")

# ── Calculate CTR ─────────────────────────────────────────────────────────────
# Ensure the columns are numeric (Google Sheets can return strings)
df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce")
df["clicks"]      = pd.to_numeric(df["clicks"],      errors="coerce")

# CTR = clicks divided by impressions
df["ctr"] = df["clicks"] / df["impressions"]

# ── Print the results ─────────────────────────────────────────────────────────
W = 65
print("=" * W)
print(f"{'CAMPAIGN CTR REPORT':^{W}}")
print("=" * W)
print(f"{'Campaign':<25} {'Impressions':>12} {'Clicks':>8} {'CTR':>8}")
print("-" * W)

for _, row in df.iterrows():
    ctr_str = f"{row['ctr']:.2%}" if pd.notna(row['ctr']) else "N/A"
    print(f"{str(row['campaign']):<25} {int(row['impressions']):>12,} {int(row['clicks']):>8,} {ctr_str:>8}")

print("=" * W)
print("Done. Google Sheets data loaded and CTR calculated.")
