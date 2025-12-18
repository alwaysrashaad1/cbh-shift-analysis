# Import libraries
import pandas as pd
import matplotlib.pyplot as plt

# Load data and parse dates
df = pd.read_csv("shifts_final.csv", parse_dates=["SHIFT_START_AT", "OFFER_VIEWED_AT"])

# Convert CLAIMED to boolean (True/False)
df["CLAIMED"] = df["CLAIMED"].astype(str).str.lower() == "true"

# Separate data into claimed and unclaimed shifts
claimed_df = df[df["CLAIMED"]]
unclaimed_df = df[~df["CLAIMED"]]

# Count number of claimed shifts where PAY_RATE < CHARGE_RATE
claimed_below = claimed_df[claimed_df["PAY_RATE"] < claimed_df["CHARGE_RATE"]]["SHIFT_ID"].nunique()

# Count number of claimed shifts where PAY_RATE >= CHARGE_RATE
claimed_above = claimed_df[claimed_df["PAY_RATE"] >= claimed_df["CHARGE_RATE"]]["SHIFT_ID"].nunique()

# For unclaimed shifts:
# Group by SHIFT_ID to summarize by the highest PAY_RATE offered and the CHARGE_RATE
unclaimed_summary = (
    df[df["SHIFT_ID"].isin(unclaimed_df["SHIFT_ID"].unique())]
    .groupby("SHIFT_ID")
    .agg(
        max_payrate=("PAY_RATE", "max"),
        charge_rate=("CHARGE_RATE", "first")  # Assuming charge rate is constant per SHIFT_ID
    )
    .reset_index()
)

# Count number of unclaimed shifts where max PAY_RATE < CHARGE_RATE
unclaimed_below = unclaimed_summary[unclaimed_summary["max_payrate"] < unclaimed_summary["charge_rate"]].shape[0]

# Count number of unclaimed shifts where max PAY_RATE >= CHARGE_RATE
unclaimed_above = unclaimed_summary[unclaimed_summary["max_payrate"] >= unclaimed_summary["charge_rate"]].shape[0]

# --- Visualization ---

fig, ax1 = plt.subplots(figsize=(8, 6))

# Colors and positions
color_below = "#add8e6"   # Light blue for below charge rate
edge_below = "#0000cc"
color_above = "#dab0ff"   # Light purple for at/above charge rate
edge_above = "#800080"

x = [0, 1]  # Bar positions for "Claimed" and "Unclaimed"
bar_width = 0.5

# Bar values
labels = ["Claimed", "Unclaimed"]
below_values = [claimed_below, unclaimed_below]
above_values = [claimed_above, unclaimed_above]

# Draw stacked bars
ax1.bar(x, below_values, bar_width, color=color_below, edgecolor=edge_below, linewidth=1.5, label="Below Charge Rate")
ax1.bar(x, above_values, bar_width, bottom=below_values, color=color_above, edgecolor=edge_above, linewidth=1.5, label="At or Above Charge Rate")

# Add count labels inside the bars and totals above
for i in range(len(x)):
    if below_values[i] > 0:
        ax1.text(x[i], below_values[i] / 2, str(below_values[i]), ha='center', va='center', fontsize=10, fontweight='bold')
    if above_values[i] > 0:
        ax1.text(x[i], below_values[i] + (above_values[i] / 2), str(above_values[i]), ha='center', va='center', fontsize=10, fontweight='bold')
    
    total = below_values[i] + above_values[i]
    ax1.text(x[i], total + 2, f"Total: {total}", ha='center', va='bottom', fontsize=10, fontweight='bold')

# Customize axes and labels
ax1.set_title("Shifts Claimed and Unclaimed\nPay Rate vs. Charge Rate", fontsize=13, pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.set_ylabel("Number of Shifts")
ax1.legend()

# Add subtitle with date range
start_date = df["OFFER_VIEWED_AT"].min().strftime("%b %d, %Y")
end_date = df["OFFER_VIEWED_AT"].max().strftime("%b %d, %Y")
fig.text(0.5, 0.93, f"Based on shift offers viewed from {start_date} to {end_date}", ha='center', fontsize=10, color='gray')

# Adjust layout and save figure
plt.tight_layout(rect=[0, 0.05, 1, 0.90])
plt.savefig("3__Shifts_Claimed_and_Unclaimed_Pay_Rate_vs_Charge_Rate.png", dpi=300, bbox_inches='tight')

# --- Summary Output ---
print("\n=== Summary for Claimed & Unclaimed Shifts ===")
print(f"Claimed Shifts - Below Charge Rate: {claimed_below}")
print(f"Claimed Shifts - At or Above Charge Rate: {claimed_above}")
print(f"Total Claimed Shifts: {claimed_below + claimed_above}")
print()
print(f"Unclaimed Shifts - Max Offer Below Charge Rate: {unclaimed_below}")
print(f"Unclaimed Shifts - Max Offer At or Above Charge Rate: {unclaimed_above}")
print(f"Total Unclaimed Shifts: {unclaimed_below + unclaimed_above}")
print(f"\nDate Range: {start_date} to {end_date}")
