# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv('shifts_final.csv')

# Convert CLAIMED column to boolean
df['CLAIMED'] = df['CLAIMED'].astype(bool)

# --- Grouping ---
# Group by DURATION and CLAIMED status, counting unique SHIFT_IDs
grouped = (
    df.groupby(['DURATION', 'CLAIMED'])['SHIFT_ID']
    .nunique()
    .reset_index(name='UNIQUE_COUNT')
)

# Pivot the table to separate claimed and unclaimed counts for each duration
pivot = grouped.pivot_table(index='DURATION', columns='CLAIMED', values='UNIQUE_COUNT', fill_value=0).reset_index()

# Rename columns for clarity
pivot = pivot.rename(columns={False: 'NOT_CLAIMED', True: 'CLAIMED'})

# Calculate total shifts and percent claimed
pivot['TOTAL'] = pivot['CLAIMED'] + pivot['NOT_CLAIMED']
pivot['PCT_CLAIMED'] = (pivot['CLAIMED'] / pivot['TOTAL'] * 100).round(1)

# --- Plotting Function ---
def make_plot(dataframe, title, filename=None):
    df_plot = dataframe.sort_values(by='DURATION')  # Sort by duration
    durations = df_plot['DURATION'].astype(str)     # Convert x-axis to string for labels
    x = np.arange(len(durations))                   # X-axis positions
    width = 0.5

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot total and claimed shifts as overlapping bars
    ax1.bar(x, df_plot['TOTAL'], width=width, color='gray', alpha=0.5, label='Total Shifts')
    ax1.bar(x, df_plot['CLAIMED'], width=width, color='blue', label='Claimed Shifts')
    ax1.set_ylabel("Unique Shifts Count", color='black')
    ax1.set_xlabel("Duration (hrs)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(durations)
    ax1.set_title(title)
    ax1.set_ylim(0, 30000)

    # Add numeric total labels above each bar
    for xi, total in zip(x, df_plot['TOTAL']):
        ax1.text(xi, total + 500, f"{int(total)}", ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Secondary axis for percent claimed
    ax2 = ax1.twinx()
    ax2.plot(x, df_plot['PCT_CLAIMED'], color='orange', marker='o', linewidth=2, label='% Claimed')
    ax2.set_ylabel("% Shifts Claimed", color='orange')
    ax2.set_ylim(0, 100)

    # Add percent labels above line points
    for xi, pct in zip(x, df_plot['PCT_CLAIMED']):
        ax2.text(xi, pct + 2, f"{pct}%", color='orange', ha='center', va='bottom', fontsize=9)

    # Add legends for both axes
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.tight_layout()

    # Save plot if filename is provided
    if filename:
        fig.savefig(filename, dpi=300)
        print(f"Plot saved to {filename}")
    
    plt.show()

# --- Summary Table Printer ---
def print_stats_summary(df_stats, description):
    print(f"\n=== Summary for {description} ===")
    print(f"{'Duration (hrs)':>13} | {'Claimed':>7} | {'Not Claimed':>11} | {'Total':>6} | {'% Claimed':>9}")
    print("-" * 56)
    for _, row in df_stats.iterrows():
        dur = row['DURATION']
        claimed = int(row['CLAIMED'])
        not_claimed = int(row['NOT_CLAIMED'])
        total = int(row['TOTAL'])
        pct_claimed = row['PCT_CLAIMED']
        print(f"{dur:13} | {claimed:7} | {not_claimed:11} | {total:6} | {pct_claimed:9.1f}%")

# --- Generate Plot 1: All durations ---
plot1_df = pivot.copy()
make_plot(plot1_df, "Shifts Offered vs Claimed by Duration (All Durations)", filename="shifts_duration_all.png")
print_stats_summary(plot1_df, "All Durations")

# --- Generate Plot 2: Selected durations (8, 9, 12 hours) ---
plot2_df = pivot[pivot['DURATION'].isin([8, 9, 12])]
make_plot(plot2_df, "Shifts Offered vs Claimed: Durations 8, 9, and 12", filename="shifts_duration_selected.png")
print_stats_summary(plot2_df, "Durations 8, 9, and 12")
