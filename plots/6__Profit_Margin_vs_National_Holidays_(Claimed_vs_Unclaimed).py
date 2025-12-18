# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import matplotlib.patheffects as path_effects

# Load shift data and parse the datetime field
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT"])

# Compute shift end time from start time and duration
df["SHIFT_END_AT"] = df["SHIFT_START_AT"] + pd.to_timedelta(df["DURATION"], unit="h")

# Convert rate columns to numeric and remove rows with missing or invalid charge rate
df["PAY_RATE"] = pd.to_numeric(df["PAY_RATE"], errors="coerce")
df["CHARGE_RATE"] = pd.to_numeric(df["CHARGE_RATE"], errors="coerce")
df = df[df["CHARGE_RATE"] > 0]

# Split into claimed and unclaimed shifts
claimed_df = df[df["CLAIMED"].astype(str).str.lower() == "true"].copy()
unclaimed_df = df[df["CLAIMED"].astype(str).str.lower() != "true"].copy()

# Calculate profit margin for claimed shifts at the time they were claimed
claimed_df["PM_AT_CLAIM"] = ((claimed_df["CHARGE_RATE"] - claimed_df["PAY_RATE"]) / claimed_df["CHARGE_RATE"]) * 100

# For unclaimed shifts, compute profit margin using the highest pay rate ever offered
max_pay = unclaimed_df.groupby("SHIFT_ID")["PAY_RATE"].max().reset_index()
unclaimed_unique = unclaimed_df.drop_duplicates(subset=["SHIFT_ID"])
merged_unclaimed = pd.merge(unclaimed_unique, max_pay, on="SHIFT_ID", suffixes=("", "_MAX"))
merged_unclaimed["PM_HIGHEST"] = (
    (merged_unclaimed["CHARGE_RATE"] - merged_unclaimed["PAY_RATE_MAX"]) / merged_unclaimed["CHARGE_RATE"]
) * 100

# Define overall x-axis date range for both subplots
overall_start = min(claimed_df["SHIFT_START_AT"].min(), merged_unclaimed["SHIFT_START_AT"].min())
overall_end   = max(claimed_df["SHIFT_START_AT"].max(), merged_unclaimed["SHIFT_START_AT"].max())

# List of national holidays to annotate on the plot
holidays = {
    "Labor Day": "2024-09-02",
    "Columbus Day": "2024-10-14",
    "Veterans Day": "2024-11-11",
    "Thanksgiving Day": "2024-11-28",
    "Christmas Day": "2024-12-25",
    "New Year's Day": "2025-01-01",
    "MLK Jr. Day": "2025-01-20"
}

# Set up two vertically stacked subplots sharing x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)

# Add background zones to indicate positive vs. negative margins
for ax in [ax1, ax2]:
    ax.axhspan(-125, 0, color="lightcoral", alpha=0.3, zorder=0)
    ax.axhspan(0, 100, color="lightgreen", alpha=0.3, zorder=0)

# Scatter plot: Claimed shifts' profit margins
claimed_scatter = ax1.scatter(
    claimed_df["SHIFT_START_AT"],
    claimed_df["PM_AT_CLAIM"],
    color="#177100DC",           # green tone
    alpha=0.7,
    edgecolor="black",
    linewidth=0.5,
    s=50,
    zorder=2,
    label="Claimed Shifts"
)

# Scatter plot: Unclaimed shifts' profit margins
unclaimed_scatter = ax2.scatter(
    merged_unclaimed["SHIFT_START_AT"],
    merged_unclaimed["PM_HIGHEST"],
    color="gray",
    alpha=0.7,
    edgecolor="black",
    linewidth=0.5,
    s=50,
    zorder=2,
    label="Unclaimed Shifts"
)

# Annotate national holidays with vertical lines and text labels
for name, date_str in holidays.items():
    date = pd.Timestamp(date_str)
    if overall_start <= date <= overall_end:
        for ax in [ax1, ax2]:
            ax.axvline(date, color='red', linestyle='-', linewidth=2, alpha=0.9, zorder=4)
            txt = ax.text(
                date - pd.Timedelta(days=1),
                -120,
                name,
                rotation=90,
                color='red',
                fontsize=13,
                fontweight="bold",
                verticalalignment='bottom',
                horizontalalignment='right',
                zorder=5
            )
            # Add white stroke for better visibility
            txt.set_path_effects([
                path_effects.Stroke(linewidth=3, foreground='white'),
                path_effects.Normal()
            ])

# Add zero-profit line to both subplots
for ax in [ax1, ax2]:
    ax.axhline(0, color="black", linewidth=3, zorder=6)

# --- Configure Top Plot (Claimed Shifts) ---
ax1.set_title("Claimed Shifts: Profit Margin at Claim Pay Rate", fontsize=16, fontweight="bold")
ax1.set_ylabel("Profit Margin (%)", fontsize=14, fontweight="bold")
ax1.set_ylim(-125, 100)
ax1.set_xlim(overall_start, overall_end)
ax1.grid(True, axis='y')

# --- Configure Bottom Plot (Unclaimed Shifts) ---
ax2.set_title("Unclaimed Shifts: Profit Margin at Highest Offer", fontsize=16, fontweight="bold")
ax2.set_ylabel("Profit Margin (%)", fontsize=14, fontweight="bold")
ax2.set_xlabel("Shift Start Date", fontsize=14, fontweight="bold")
ax2.set_ylim(-125, 100)
ax2.set_xlim(overall_start, overall_end)
ax2.grid(True, axis='y')

# Format x-axis as monthly ticks
ax2.xaxis.set_major_locator(mdates.MonthLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45, fontsize=12, fontweight="bold")

# Main figure title and annotation
fig.suptitle(
    "Profit Margin vs National Holidays for Claimed and Unclaimed Shifts",
    fontsize=18,
    fontweight="bold",
    y=1.05
)

# Data range summary label at top
fig.text(
    0.5, 0.99,
    f"Data range: {overall_start.strftime('%b %d, %Y')} to {overall_end.strftime('%b %d, %Y')}",
    fontsize=13,
    fontweight="bold",
    color="black",
    ha="center",
    va="top",
    bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")
)

# Adjust layout and spacing
fig.subplots_adjust(top=0.90)

# Legend showing what each color represents
legend_elements = [
    Patch(facecolor="#177100DC", edgecolor="black", label="Claimed Shifts"),
    Patch(facecolor="gray", edgecolor="black", label="Unclaimed Shifts"),
    Patch(facecolor="red", edgecolor="red", label="National Holiday Marker")
]
ax1.legend(
    handles=legend_elements,
    loc="lower center",
    bbox_to_anchor=(0.5, 1.15),
    ncol=3,
    fontsize=12,
    frameon=True
)

# Final layout tightening and save to file
plt.tight_layout()
plt.savefig("6__Profit_Margin_vs_National_Holidays_(Claimed_vs_Unclaimed).png", dpi=300, bbox_inches='tight')
