# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data and parse datetime columns
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT", "OFFER_VIEWED_AT"])

# Calculate how many hours in advance the shift was first offered
df["HOURS_DIFF"] = (df["SHIFT_START_AT"] - df["OFFER_VIEWED_AT"]).dt.total_seconds() / 3600

# Filter out any invalid negative time differences (e.g., OFFER_VIEWED_AT after the shift start)
df = df[df["HOURS_DIFF"] >= 0]

# Create 24-hour (1-day) time bins from 0 to 720 hours (30 days)
hour_bins = list(range(0, 721, 24))
df["TIME_BUCKET_DAYS"] = pd.cut(df["HOURS_DIFF"], bins=hour_bins, right=False)

# Separate into claimed and unclaimed shifts
claimed_df = df[df["CLAIMED"].astype(str).str.lower() == "true"].copy()
unclaimed_df = df[df["CLAIMED"].astype(str).str.lower() != "true"].copy()

# Count unique shifts per time bucket
total_counts = df.groupby("TIME_BUCKET_DAYS", observed=False)["SHIFT_ID"].nunique()

# Only keep buckets with at least 50 shifts for statistical significance
valid_buckets = total_counts[total_counts >= 50].index

# Count claimed shifts in each valid time bucket
claimed_counts = claimed_df.groupby("TIME_BUCKET_DAYS", observed=False)["SHIFT_ID"].nunique().reindex(valid_buckets)

# Calculate % of shifts claimed in each valid bucket
percent_claimed = (claimed_counts / total_counts[valid_buckets] * 100).fillna(0)

# Prepare x-axis labels (in days)
bucket_labels = [f"{int(b.right // 24)}" for b in valid_buckets]
x = np.arange(len(bucket_labels))

# Plotting
fig, ax1 = plt.subplots(figsize=(14, 6))

# Bar plot of % claimed vs days in advance the shift was posted
ax1.bar(x, percent_claimed.values, color='orange', width=0.6, label='% Claimed')
ax1.set_ylabel("% Shifts Claimed", color="orange")
ax1.set_ylim(0, 100)
ax1.set_xlabel("Days Between First View and Shift Start")
ax1.set_title("Claim Rate by Days Between First View and Shift Start (≥ 50 Shifts Offered)")
ax1.set_xticks(x)
ax1.set_xticklabels(bucket_labels)
ax1.legend(loc='upper left')

# Save the figure
plt.tight_layout()
plt.savefig("7a_Claim_Percentages_vs_Timeposted_Before_Start.png", dpi=300)

# Print table summary in the terminal
print("\n=== Claimed Percentage by Days Before Shift Start (only buckets with >=50 shifts) ===")
print(f"{'Days Before Start':>18} | {'% Claimed':>9}")
print("-" * 32)
for label, pct in zip(bucket_labels, percent_claimed.values):
    print(f"{label:18} | {pct:9.1f}%")
