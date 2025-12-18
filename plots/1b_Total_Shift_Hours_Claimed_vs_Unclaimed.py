# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

# Set Seaborn style for consistent and clean visuals
sns.set_style("whitegrid")

# Read shift data and parse relevant datetime columns
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT", "OFFER_VIEWED_AT", "CLAIMED_AT"])

# Convert DURATION column to numeric values (in case of invalid entries)
df["DURATION"] = pd.to_numeric(df["DURATION"], errors='coerce')

# Find earliest and latest activity timestamps for annotation purposes
earliest_view = df["OFFER_VIEWED_AT"].min()
latest_activity = max(df["OFFER_VIEWED_AT"].max(), df["CLAIMED_AT"].max())

# Filter claimed and unclaimed shifts
claimed_df = df[df["CLAIMED"].astype(str).str.lower() == "true"]
unclaimed_df = df[df["CLAIMED"].astype(str).str.lower() != "true"]

# Total hours for claimed shifts (sum of all durations)
claimed_hours = claimed_df["DURATION"].sum()

# For unclaimed shifts, count only the first occurrence per SHIFT_ID to avoid duplicates
unclaimed_hours = unclaimed_df.groupby("SHIFT_ID")["DURATION"].first().sum()

# --- Visualization: Bar Chart of Claimed vs Unclaimed Hours ---
fig, ax = plt.subplots(figsize=(8, 6))

# Create bar chart with total hours
bars = ax.bar(
    ["Claimed", "Unclaimed"],                  # X-axis categories
    [claimed_hours, unclaimed_hours],          # Y-axis values
    color=["#5cb85c", "#999999"],              # Green for claimed, gray for unclaimed
    edgecolor="black",
    linewidth=0.8
)

# Add value labels above each bar
for bar in bars:
    yval = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        yval + 10,
        f"{yval:,.0f} hrs",
        ha='center',
        va='bottom',
        fontsize=12,
        fontweight='bold'
    )

# Set plot title and subtitle with data range
ax.set_title("Total Shift Hours: Claimed vs. Unclaimed", fontsize=16, weight='bold')
fig.suptitle(f"Based on shift data from {earliest_view.date()} to {latest_activity.date()}", fontsize=10, y=0.91)

# Y-axis label and limits
ax.set_ylabel("Total Hours")
ax.set_ylim(0, max(claimed_hours, unclaimed_hours) * 1.15)

# Add horizontal grid lines for better readability
ax.grid(axis='y', linestyle='--', alpha=0.6)

# Create custom legend for clarity
custom_lines = [
    plt.Line2D([0], [0], color='#5cb85c', lw=10),
    plt.Line2D([0], [0], color='#999999', lw=10)
]
ax.legend(custom_lines, ["Claimed (Hours Worked)", "Unclaimed (Hours Unfilled)"], loc="upper left")

# Remove top/right plot borders
sns.despine()

# Adjust layout and save figure
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("1b_Total_Shift_Hours_Claimed_vs_Unclaimed.png", dpi=300, bbox_inches='tight')

# --- Summary Statistics ---
# Compute total and percentages
total_hours = claimed_hours + unclaimed_hours
claimed_pct = claimed_hours / total_hours * 100 if total_hours else 0
unclaimed_pct = unclaimed_hours / total_hours * 100 if total_hours else 0

# Print a summary table to the console
print("\n=== Total Shift Hours Summary ===")
print(f"{'':<12} | {'Hours':>12} | {'% of Total':>10}")
print("-" * 38)
print(f"{'Claimed':<12} | {claimed_hours:12,.0f} | {claimed_pct:10.1f}%")
print(f"{'Unclaimed':<12} | {unclaimed_hours:12,.0f} | {unclaimed_pct:10.1f}%")
print(f"{'Total':<12} | {total_hours:12,.0f} | {100.0:10.1f}%")
