# Import libraries
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset and parse datetime columns
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT", "CLAIMED_AT", "OFFER_VIEWED_AT"])

# Convert relevant columns to numeric, handling non-numeric entries safely
df["PAY_RATE"] = pd.to_numeric(df["PAY_RATE"], errors="coerce")
df["CHARGE_RATE"] = pd.to_numeric(df["CHARGE_RATE"], errors="coerce")
df["DURATION"] = pd.to_numeric(df["DURATION"], errors="coerce")

# Filter out rows where CHARGE_RATE is not positive
df = df[df["CHARGE_RATE"] > 0]

# Convert CLAIMED column to boolean
df["CLAIMED"] = df["CLAIMED"].astype(str).str.lower() == "true"

# Separate into claimed and unclaimed DataFrames
claimed_df = df[df["CLAIMED"]].copy()
unclaimed_df = df[~df["CLAIMED"]].copy()

# --- Claimed Shifts: Profit Margin ---
# Profit Margin = (Charge Rate - Pay Rate) / Charge Rate * 100
claimed_df["PROFIT_MARGIN"] = ((claimed_df["CHARGE_RATE"] - claimed_df["PAY_RATE"]) / claimed_df["CHARGE_RATE"]) * 100

# --- Unclaimed Shifts: Highest Offer Analysis ---
# Find the highest pay offer per shift
max_payrates = unclaimed_df.groupby("SHIFT_ID")["PAY_RATE"].max().reset_index(name="MAX_PAY_RATE")

# For each unclaimed shift, take charge rate and duration from the first entry
meta = unclaimed_df.drop_duplicates("SHIFT_ID", keep="first")[["SHIFT_ID", "CHARGE_RATE", "DURATION"]]

# Merge max pay rates with meta info
unclaimed_summary = pd.merge(max_payrates, meta, on="SHIFT_ID")

# Compute hypothetical profit margin for unclaimed shifts based on max offer
unclaimed_summary["PROFIT_MARGIN"] = ((unclaimed_summary["CHARGE_RATE"] - unclaimed_summary["MAX_PAY_RATE"]) / unclaimed_summary["CHARGE_RATE"]) * 100

# --- Visualization ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)  # Two side-by-side plots

# Define x-axis limits and ticks
x_min = 0
x_max = 18
x_ticks = list(range(x_min, x_max + 1))

# --- Left Plot: Claimed Shifts ---
# Color-coded background: red for negative margin, green for positive
ax1.axhspan(-125, 0, color="lightcoral", alpha=0.3)
ax1.axhspan(0, 125, color="lightgreen", alpha=0.3)
ax1.axhline(0, color="black", linewidth=1.2)  # horizontal zero line

# Scatter plot of profit margin vs duration
ax1.scatter(claimed_df["DURATION"], claimed_df["PROFIT_MARGIN"], color="green", alpha=0.6)
ax1.set_title("Claimed Shifts")
ax1.set_xlabel("Shift Duration (hours)")
ax1.set_ylabel("Profit Margin (%)")
ax1.set_xlim(x_min, x_max)
ax1.set_ylim(-125, 125)
ax1.set_xticks(x_ticks)
ax1.grid(True)

# --- Right Plot: Unclaimed Shifts (max offer) ---
ax2.axhspan(-125, 0, color="lightcoral", alpha=0.3)
ax2.axhspan(0, 125, color="lightgreen", alpha=0.3)
ax2.axhline(0, color="black", linewidth=1.2)

# Scatter plot of profit margin vs duration for hypothetical unclaimed shift offers
ax2.scatter(unclaimed_summary["DURATION"], unclaimed_summary["PROFIT_MARGIN"], color="gray", alpha=0.6)
ax2.set_title("Unclaimed Shifts (Highest Offer)")
ax2.set_xlabel("Shift Duration (hours)")
ax2.set_xlim(x_min, x_max)
ax2.set_xticks(x_ticks)
ax2.grid(True)

# Title and layout adjustments
plt.suptitle("Profit Margin vs. Shift Duration (Claimed vs. Unclaimed)", fontsize=14)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save the plot as a PNG file
plt.savefig("4b_Profit_Margin_vs_Shift_Duration_(Claimed_vs_Unclaimed).png", dpi=300, bbox_inches='tight')
