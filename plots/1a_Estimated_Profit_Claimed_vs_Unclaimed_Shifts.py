# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

# Set Seaborn style for better visuals
sns.set_style("whitegrid")

# Read CSV file and parse specific columns as datetime
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT", "OFFER_VIEWED_AT", "CLAIMED_AT"])

# Convert relevant columns to numeric, coercing errors (invalid values become NaN)
df["PAY_RATE"] = pd.to_numeric(df["PAY_RATE"], errors='coerce')
df["CHARGE_RATE"] = pd.to_numeric(df["CHARGE_RATE"], errors='coerce')
df["DURATION"] = pd.to_numeric(df["DURATION"], errors='coerce')

# Track the overall time range of the data
earliest_view = df["OFFER_VIEWED_AT"].min()
latest_activity = max(df["OFFER_VIEWED_AT"].max(), df["CLAIMED_AT"].max())

# Split the dataframe into claimed and unclaimed shifts
claimed_df = df[df["CLAIMED"].astype(str).str.lower() == "true"]
unclaimed_df = df[df["CLAIMED"].astype(str).str.lower() != "true"]

# Calculate profit for claimed shifts: (CHARGE_RATE - PAY_RATE) * DURATION
claimed_profit = ((claimed_df["CHARGE_RATE"] - claimed_df["PAY_RATE"]) * claimed_df["DURATION"]).sum()

# For unclaimed shifts:
# 1. Group by SHIFT_ID and get the highest pay rate offered
max_offers = unclaimed_df.groupby("SHIFT_ID")["PAY_RATE"].max().reset_index()

# 2. Merge with a representative (first) shift per SHIFT_ID to get CHARGE_RATE and DURATION
merged_unclaimed = pd.merge(
    unclaimed_df.drop_duplicates("SHIFT_ID", keep="first"),
    max_offers,
    on="SHIFT_ID",
    suffixes=("", "_MAX")  # Avoid name collision
)

# 3. Estimate potential unclaimed profit using max PAY_RATE offered
unclaimed_profit = ((merged_unclaimed["CHARGE_RATE"] - merged_unclaimed["PAY_RATE_MAX"]) * merged_unclaimed["DURATION"]).sum()

# Create bar plot for claimed vs unclaimed profits
fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(
    ["Claimed", "Unclaimed"],                          # X-axis categories
    [claimed_profit, unclaimed_profit],                # Y-axis values
    color=["#5cb85c", "#999999"],                      # Green for claimed, gray for unclaimed
    edgecolor='black',
    linewidth=0.8
)

# Format y-axis ticks as currency
formatter = FuncFormatter(lambda x, _: f"${x:,.0f}")
ax.yaxis.set_major_formatter(formatter)

# Add value labels on top of each bar
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.01 * height,
        f"${height:,.0f}",
        ha='center',
        va='bottom',
        fontsize=12,
        fontweight='bold'
    )

# Set plot title and subtitle
ax.set_title("Estimated Profit: Claimed vs. Unclaimed Shifts", fontsize=16, weight='bold')
fig.suptitle(f"Based on shift data from {earliest_view.date()} to {latest_activity.date()}", fontsize=10, y=0.91)

# Label the Y-axis
ax.set_ylabel("Total Profit ($)")

# Set Y-axis limit slightly above the higher of the two bars
ax.set_ylim(0, max(claimed_profit, unclaimed_profit) * 1.15)

# Create custom legend lines for visual explanation
custom_lines = [
    plt.Line2D([0], [0], color='#5cb85c', lw=10),
    plt.Line2D([0], [0], color='#999999', lw=10)
]
ax.legend(custom_lines, ["Profits Collected (Claimed)", "Potential Profits Lost (Unclaimed)"], loc="upper left")

# Remove top/right spines for a cleaner look
sns.despine()

# Adjust layout and save figure to file
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("1a_Estimated_Profit_Claimed_vs_Unclaimed_Shifts.png", dpi=300, bbox_inches='tight')

# Uncomment below to display plot
# plt.show()
