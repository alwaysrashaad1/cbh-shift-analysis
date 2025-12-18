import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset with shift start and offer viewed timestamps parsed as dates
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT", "OFFER_VIEWED_AT"])

# Calculate the hours difference between when the offer was viewed and the shift start time
df["HOURS_DIFF"] = (df["SHIFT_START_AT"] - df["OFFER_VIEWED_AT"]).dt.total_seconds() / 3600

# Keep only rows where the offer was viewed before the shift starts (non-negative difference)
df = df[df["HOURS_DIFF"] >= 0]

# Define hourly bins representing full days from 0 up to 720 hours (30 days), with 24-hour intervals
hour_bins = list(range(0, 721, 24))

# Create a categorical column with each shift assigned to a time bucket based on HOURS_DIFF
# Bins are left-closed intervals [x, y)
df["TIME_BUCKET_DAYS"] = pd.cut(df["HOURS_DIFF"], bins=hour_bins, right=False)

# Prepare x-axis values (days 1 through 29) and labels for plotting
x_vals = np.arange(1, 30)
labels_29 = [str(i) for i in range(1, 30)]
bar_width = 0.6  # Width of bars for bar plots

# Convert PAY_RATE and CHARGE_RATE columns to numeric, coercing invalid parsing to NaN
df["PAY_RATE"] = pd.to_numeric(df["PAY_RATE"], errors="coerce")
df["CHARGE_RATE"] = pd.to_numeric(df["CHARGE_RATE"], errors="coerce")

# Convert CLAIMED column to boolean (True if string is 'true', else False)
df["CLAIMED"] = df["CLAIMED"].astype(str).str.lower() == "true"

# Filter to only claimed shifts
claimed = df[df["CLAIMED"]].copy()

# Calculate profit margin per shift for claimed shifts: Charge Rate - Pay Rate
claimed["PROFIT_MARGIN"] = claimed["CHARGE_RATE"] - claimed["PAY_RATE"]

# Group by time bucket and calculate the average profit margin for claimed shifts
claimed_pm_avg = claimed.groupby("TIME_BUCKET_DAYS", observed=False)["PROFIT_MARGIN"].mean()

# Filter to only unclaimed shifts
unclaimed = df[~df["CLAIMED"]].copy()

# Find the highest pay rate offered per unclaimed shift (by SHIFT_ID)
max_pay = unclaimed.groupby("SHIFT_ID")["PAY_RATE"].max().reset_index(name="HIGHEST_PAY")

# Get metadata for unclaimed shifts (unique SHIFT_ID with their time bucket and charge rate)
unclaimed_meta = unclaimed.drop_duplicates(subset=["SHIFT_ID"])[["SHIFT_ID", "TIME_BUCKET_DAYS", "CHARGE_RATE"]]

# Merge metadata with highest pay offered per shift
unclaimed_merged = pd.merge(unclaimed_meta, max_pay, on="SHIFT_ID")

# Calculate profit margin for unclaimed shifts using highest pay offered
unclaimed_merged["PROFIT_MARGIN"] = unclaimed_merged["CHARGE_RATE"] - unclaimed_merged["HIGHEST_PAY"]

# Calculate average profit margin for unclaimed shifts by time bucket
unclaimed_pm_avg = unclaimed_merged.groupby("TIME_BUCKET_DAYS", observed=False)["PROFIT_MARGIN"].mean()

# Create full time buckets IntervalIndex (excluding the 0th bin) for consistent x-axis alignment
full_bins = pd.IntervalIndex.from_breaks(hour_bins, closed='left')[1:]

# Reindex claimed and unclaimed profit margin averages to full bins; fill missing bins with 0
claimed_pm_avg = claimed_pm_avg.reindex(full_bins).fillna(0)
unclaimed_pm_avg = unclaimed_pm_avg.reindex(full_bins).fillna(0)

# Create a figure with 3 subplots stacked vertically, sharing the y-axis
fig, axes = plt.subplots(3, 1, figsize=(14, 18), sharey=True)

ax1, ax2, ax3 = axes  # Unpack the axes for clarity

# Set y-axis limits and font sizes for titles and labels
ymin, ymax = 0, 100
title_fontsize = 18
label_fontsize = 14

# === Plot 1: Claimed Shifts Average Profit Margin ===
ax1.bar(x_vals, claimed_pm_avg.iloc[:29], width=bar_width, color='#4CAF50', edgecolor='black')
ax1.set_title("Claimed Shifts: Average Profit Margin per Shift", fontweight='bold', fontsize=title_fontsize)
ax1.set_xlabel("Days Between First View and Shift Start", fontsize=label_fontsize)
ax1.set_ylabel("Average Profit Margin ($)", fontsize=label_fontsize)
ax1.set_xticks(x_vals)
ax1.set_xticklabels(labels_29)
ax1.set_ylim(ymin, ymax)
ax1.grid(axis='y', linestyle='--', alpha=0.6)

# === Plot 2: Unclaimed Shifts Average Profit Margin ===
ax2.bar(x_vals, unclaimed_pm_avg.iloc[:29], width=bar_width, color='#D32F2F', edgecolor='black')
ax2.set_title("Unclaimed Shifts: Average Profit Margin per Shift", fontweight='bold', fontsize=title_fontsize)
ax2.set_xlabel("Days Between First View and Shift Start", fontsize=label_fontsize)
ax2.set_ylabel("Average Profit Margin ($)", fontsize=label_fontsize)
ax2.set_xticks(x_vals)
ax2.set_xticklabels(labels_29)
ax2.set_ylim(ymin, ymax)
ax2.grid(axis='y', linestyle='--', alpha=0.6)

# === Plot 3: Side-by-Side Comparison of Claimed vs Unclaimed Profit Margins ===
bar_width_small = 0.35  # Narrower bars to fit side by side
ax3.bar(x_vals - bar_width_small/2, claimed_pm_avg.iloc[:29], width=bar_width_small,
        label="Claimed Profit Margin", color='#4CAF50', edgecolor='black')
ax3.bar(x_vals + bar_width_small/2, unclaimed_pm_avg.iloc[:29], width=bar_width_small,
        label="Unclaimed Profit Margin", color='#D32F2F', edgecolor='black')
ax3.set_title("Profit Margin Comparison: Claimed vs Unclaimed", fontweight='bold', fontsize=title_fontsize)
ax3.set_xlabel("Days Between First View and Shift Start", fontsize=label_fontsize)
ax3.set_ylabel("Average Profit Margin ($)", fontsize=label_fontsize)
ax3.set_xticks(x_vals)
ax3.set_xticklabels(labels_29)
ax3.set_ylim(ymin, ymax)
ax3.grid(axis='y', linestyle='--', alpha=0.6)
ax3.legend()

# Adjust layout to prevent overlap and improve spacing
plt.tight_layout()

# Save the figure as a high-resolution PNG file
plt.savefig("7b_Profit_Margin_Statistics_by_Days_Between_First_View_and_Shift_Start.png", dpi=300)

# Optional: Show the plots (currently commented out)
# plt.show()

# Print a table summary of average profit margins by days before shift start
print("\n=== Profit Margin Statistics by Days Between First View and Shift Start ===")
print(f"{'Days':>5} | {'Claimed Avg Profit':>18} | {'Unclaimed Avg Profit':>20} | {'Difference':>10}")
print("-" * 65)
for day, c_pm, u_pm in zip(labels_29, claimed_pm_avg.iloc[:29], unclaimed_pm_avg.iloc[:29]):
    c_val = 0 if pd.isna(c_pm) else c_pm
    u_val = 0 if pd.isna(u_pm) else u_pm
    diff = c_val - u_val
    print(f"{day:>5} | {c_val:18.2f} | {u_val:20.2f} | {diff:10.2f}")
