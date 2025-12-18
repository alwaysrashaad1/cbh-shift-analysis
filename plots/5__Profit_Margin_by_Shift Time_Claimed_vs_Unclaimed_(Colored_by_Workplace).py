# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV and parse datetime for SHIFT_START_AT
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT"])

# Calculate SHIFT_END_AT using DURATION (in hours)
df["SHIFT_END_AT"] = df["SHIFT_START_AT"] + pd.to_timedelta(df["DURATION"], unit="h")

# Convert rates to numeric values
df["PAY_RATE"] = pd.to_numeric(df["PAY_RATE"], errors="coerce")
df["CHARGE_RATE"] = pd.to_numeric(df["CHARGE_RATE"], errors="coerce")

# Keep only rows where charge rate is positive
df = df[df["CHARGE_RATE"] > 0]

# Helper function: convert time-of-day to fractional hour (e.g., 13.5 for 1:30 PM)
def to_fractional_hour(dt_series):
    return dt_series.dt.hour + dt_series.dt.minute / 60 + dt_series.dt.second / 3600

# Helper function: convert 24-hour clock to 12-hour format with labels (e.g., 14 → 2pm)
def hour_label_12hr(h):
    h = h % 24
    if h == 0:
        return "12am"
    elif h == 12:
        return "12pm"
    elif h < 12:
        return f"{h}am"
    else:
        return f"{h-12}pm"

# Assign a unique color per workplace using a colormap
all_ids = df["WORKPLACE_ID"].unique()
id_to_color = dict(zip(all_ids, plt.cm.get_cmap("tab20", len(all_ids)).colors))

# Setup two subplots side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), sharey=True)

# --- Claimed Shifts ---
claimed_df = df[df["CLAIMED"].astype(str).str.lower() == "true"].copy()

# Compute profit margin: ((charge - pay) / charge) * 100
claimed_df["PM_CLAIMED"] = ((claimed_df["CHARGE_RATE"] - claimed_df["PAY_RATE"]) / claimed_df["CHARGE_RATE"]) * 100

# Convert start and end times to fractional hours
claimed_df["START_HOUR"] = to_fractional_hour(claimed_df["SHIFT_START_AT"])
claimed_df["END_HOUR"] = to_fractional_hour(claimed_df["SHIFT_END_AT"])

# Adjust END_HOUR to span over midnight if needed
claimed_df.loc[claimed_df["END_HOUR"] <= claimed_df["START_HOUR"], "END_HOUR"] += 24

# Add background color spans and zero line
ax1.axhspan(0, 100, color="lightgreen", alpha=0.3, zorder=0)
ax1.axhspan(-125, 0, color="lightcoral", alpha=0.3, zorder=0)
ax1.axhline(0, color="black", linewidth=3, zorder=10)

# Plot horizontal bars per shift for claimed data
for _, row in claimed_df.iterrows():
    color = id_to_color.get(row["WORKPLACE_ID"], "blue")
    ax1.plot(
        [row["START_HOUR"], row["END_HOUR"]],
        [row["PM_CLAIMED"], row["PM_CLAIMED"]],
        color=color,
        linewidth=2,
        alpha=0.8,
        zorder=1
    )

# Configure left plot (Claimed)
ax1.set_title("Claimed Shifts\nProfit Margin on Claimed Pay Rate vs. Time of Day", fontsize=14)
ax1.set_xlabel("Shift Time (Start to End)")
ax1.set_xlim(0, 36)
ax1.set_ylim(-125, 100)
ax1.grid(True)
ax1.set_ylabel("Profit Margin (%)\n((Charge Rate - Pay Rate) × 100 / Charge Rate)")
ax1.set_xticks(range(0, 37, 2))
ax1.set_xticklabels(
    [f"{hour_label_12hr(h)}{'*' if h >= 24 else ''}" for h in range(0, 37, 2)],
    rotation=45
)

# --- Unclaimed Shifts ---
unclaimed_df = df[df["CLAIMED"].astype(str).str.lower() != "true"].copy()

# For unclaimed shifts, use highest pay rate offered for each shift
max_pay = unclaimed_df.groupby("SHIFT_ID")["PAY_RATE"].max().reset_index()

# Keep only one row per SHIFT_ID for metadata (duration, start time, etc.)
unclaimed_unique = unclaimed_df.drop_duplicates(subset=["SHIFT_ID"])

# Merge highest pay with unclaimed shift info
merged_unclaimed = pd.merge(unclaimed_unique, max_pay, on="SHIFT_ID", suffixes=("", "_MAX"))

# Calculate profit margin based on max offer
merged_unclaimed["PM_HIGHEST"] = (
    (merged_unclaimed["CHARGE_RATE"] - merged_unclaimed["PAY_RATE_MAX"]) /
    merged_unclaimed["CHARGE_RATE"]
) * 100

# Convert times to fractional hour format
merged_unclaimed["START_HOUR"] = to_fractional_hour(merged_unclaimed["SHIFT_START_AT"])
merged_unclaimed["END_HOUR"] = to_fractional_hour(merged_unclaimed["SHIFT_END_AT"])
merged_unclaimed.loc[merged_unclaimed["END_HOUR"] <= merged_unclaimed["START_HOUR"], "END_HOUR"] += 24

# Background and 0% line
ax2.axhspan(0, 100, color="lightgreen", alpha=0.3, zorder=0)
ax2.axhspan(-125, 0, color="lightcoral", alpha=0.3, zorder=0)
ax2.axhline(0, color="black", linewidth=3, zorder=10)

# Plot unclaimed shift bars
for _, row in merged_unclaimed.iterrows():
    color = id_to_color.get(row["WORKPLACE_ID"], "blue")
    ax2.plot(
        [row["START_HOUR"], row["END_HOUR"]],
        [row["PM_HIGHEST"], row["PM_HIGHEST"]],
        color=color,
        linewidth=2,
        alpha=0.8,
        zorder=1
    )

# Configure right plot (Unclaimed)
ax2.set_title("Unclaimed Shifts\nProfit Margin at Highest Offer vs. Time of Day", fontsize=14)
ax2.set_xlabel("Shift Time (Start to End)")
ax2.set_xlim(0, 36)
ax2.set_ylim(-125, 100)
ax2.grid(True)
ax2.set_ylabel("Profit Margin (%)\n((Charge Rate - Pay Rate) × 100 / Charge Rate)")
ax2.set_xticks(range(0, 37, 2))
ax2.set_xticklabels(
    [f"{hour_label_12hr(h)}{'*' if h >= 24 else ''}" for h in range(0, 37, 2)],
    rotation=45
)

# Main title and layout
plt.suptitle("Profit Margin by Shift Time: Claimed vs Unclaimed (Colored by Workplace)", fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save final plot
plt.savefig("5__Profit_Margin_by_Shift Time_Claimed_vs_Unclaimed_(Colored_by_Workplace).png", dpi=300, bbox_inches='tight')
