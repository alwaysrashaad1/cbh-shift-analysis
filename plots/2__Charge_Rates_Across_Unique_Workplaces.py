# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt

# Load shift data from CSV
df = pd.read_csv("shifts_final.csv")

# Convert CHARGE_RATE to numeric, coercing errors (invalid strings become NaN)
df["CHARGE_RATE"] = pd.to_numeric(df["CHARGE_RATE"], errors='coerce')

# Drop rows where CHARGE_RATE or WORKPLACE_ID is missing
df = df.dropna(subset=["CHARGE_RATE", "WORKPLACE_ID"])

# Remove duplicate WORKPLACE_IDs to get unique workplace-level charge rates
workplace_rates = df.drop_duplicates(subset="WORKPLACE_ID")[["WORKPLACE_ID", "CHARGE_RATE"]]
charge_values = workplace_rates["CHARGE_RATE"]

# --- Calculate summary statistics ---
q1 = charge_values.quantile(0.25)  # 25th percentile
q2 = charge_values.quantile(0.50)  # Median (50th percentile)
q3 = charge_values.quantile(0.75)  # 75th percentile
minimum = charge_values.min()      # Minimum charge rate
maximum = charge_values.max()      # Maximum charge rate

# Print summary stats to console
print("Summary Statistics for CHARGE_RATE across unique workplaces:")
print(f"Minimum: ${minimum:.2f}")
print(f"Q1 (25th percentile): ${q1:.2f}")
print(f"Median (Q2): ${q2:.2f}")
print(f"Q3 (75th percentile): ${q3:.2f}")
print(f"Maximum: ${maximum:.2f}")

# --- Visualization: Box Plot of Charge Rates ---
plt.figure(figsize=(10, 4))  # Set figure size (wide horizontal)
plt.boxplot(charge_values, vert=False, patch_artist=True, widths=0.6)  # Horizontal boxplot

# Annotate key summary statistics on the plot
summary_stats = [minimum, q1, q2, q3, maximum]
y_pos = 1.05  # Slightly above the boxplot line

for val in summary_stats:
    plt.text(val, y_pos, f"${val:.2f}", va='bottom', ha='center', fontsize=9, color='black')

# Customize plot title and labels
plt.title("Charge Rates Across Unique Workplaces")
plt.xlabel("Charge Rate ($)")
plt.yticks([])  # Remove Y-axis ticks since it's a single horizontal line
plt.grid(True, axis='x')  # Add horizontal gridlines for readability
plt.tight_layout()

# Save plot as PNG image
plt.savefig("2__Charge_Rates_Across_Unique_Workplaces.png", dpi=300)
