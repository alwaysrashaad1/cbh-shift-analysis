import pandas as pd

# Load data
df = pd.read_csv('shifts_final.csv')
df.columns = df.columns.str.strip()

# Convert relevant columns to datetime
df['CLAIMED_AT'] = pd.to_datetime(df['CLAIMED_AT'])
df['CANCELED_AT'] = pd.to_datetime(df['CANCELED_AT'])

# Add CLAIMED column
df['CLAIMED'] = df['CLAIMED_AT'].notna()

# Total unique SHIFT_IDs in original data
total_shifts = df['SHIFT_ID'].nunique()
print(f"Total unique SHIFT_IDs: {total_shifts}")

# Identify claimed rows
claimed_df = df[df['CLAIMED']]
first_claimers_total = claimed_df['SHIFT_ID'].nunique()
print(f"Total shifts with at least one claimer (first claimers total): {first_claimers_total}")

# First claim per SHIFT_ID
claimed_df_sorted = claimed_df.sort_values(by='CLAIMED_AT')
first_claims = claimed_df_sorted.groupby('SHIFT_ID', as_index=False).first()

# Handle IS_VERIFIED column (if present)
if 'IS_VERIFIED' in first_claims.columns:
    first_claims['IS_VERIFIED'] = first_claims['IS_VERIFIED'].fillna(False).astype(bool)
else:
    # If not present, assume all first claimers worked
    first_claims['IS_VERIFIED'] = True

# Count first claims worked vs not
num_first_claims_worked = first_claims[first_claims['IS_VERIFIED']].shape[0]
num_first_claims_not_worked = first_claims[~first_claims['IS_VERIFIED']].shape[0]

# Calculate shifts never claimed in original data
claimed_shift_ids = set(claimed_df['SHIFT_ID'])
num_never_claimed = total_shifts - len(claimed_shift_ids)

print(f"Shifts with first claimer who worked: {num_first_claims_worked}")
print(f"Shifts with first claimer who did NOT work: {num_first_claims_not_worked}")
print(f"Shifts never claimed: {num_never_claimed}")
print(f"Percentage worked: {num_first_claims_worked / total_shifts * 100:.2f}%")
print(f"Percentage not worked: {num_first_claims_not_worked / total_shifts * 100:.2f}%")
print(f"Percentage never claimed: {num_never_claimed / total_shifts * 100:.2f}%")
print()
print()

# --- Create df_final filtering out shifts with any cancellation, any no-call-no-show, or first claimer did not work ---

# Shifts with canceled rows
canceled_shift_ids = set(df.loc[df['CANCELED_AT'].notna(), 'SHIFT_ID'])

# Shifts with any no-call-no-show (IS_NCNS == True)
ncns_shift_ids = set(df.loc[df['IS_NCNS'] == True, 'SHIFT_ID']) if 'IS_NCNS' in df.columns else set()

# Shifts where first claimer did NOT work
first_claims_not_worked_shift_ids = set(first_claims.loc[~first_claims['IS_VERIFIED'], 'SHIFT_ID'])

# Combine all shifts to exclude
excluded_shift_ids = canceled_shift_ids.union(ncns_shift_ids).union(first_claims_not_worked_shift_ids)

# Filter out excluded SHIFT_IDs
df_final = df[~df['SHIFT_ID'].isin(excluded_shift_ids)].copy()

# Remove rows where IS_NCNS is True just to be safe (should be none)
if 'IS_NCNS' in df_final.columns:
    df_final = df_final[df_final['IS_NCNS'] != True]

# Add SHIFT_END_AT calculated from SHIFT_START_AT + DURATION (assuming DURATION is in minutes)
df_final['SHIFT_END_AT'] = pd.to_datetime(df_final['SHIFT_START_AT']) + pd.to_timedelta(df_final['DURATION'], unit='m')

# Insert SHIFT_END_AT right after SHIFT_START_AT
shift_start_idx = df_final.columns.get_loc("SHIFT_START_AT")
shift_end_col = df_final.pop('SHIFT_END_AT')
df_final.insert(shift_start_idx + 1, 'SHIFT_END_AT', shift_end_col)

# Confirm all first claimers in df_final worked (before dropping IS_VERIFIED)
claimed_df_final = df_final[df_final['CLAIMED']]
claimed_df_final_sorted = claimed_df_final.sort_values(by='CLAIMED_AT')
first_claims_final = claimed_df_final_sorted.groupby('SHIFT_ID', as_index=False).first()

if 'IS_VERIFIED' in first_claims_final.columns:
    first_claims_final['IS_VERIFIED'] = first_claims_final['IS_VERIFIED'].fillna(False).astype(bool)
else:
    first_claims_final['IS_VERIFIED'] = True

# Drop IS_VERIFIED (no longer needed)
df_final.drop(columns=['IS_VERIFIED'], errors='ignore', inplace=True)

# Drop fully empty columns if any
df_final.dropna(axis=1, how='all', inplace=True)

# Drop IS_NCNS column entirely
if 'IS_NCNS' in df_final.columns:
    df_final.drop(columns=['IS_NCNS'], inplace=True)

# Calculate shifts never claimed in df_final
final_shift_ids = set(df_final['SHIFT_ID'])
original_claimed_shift_ids = set(df.loc[df['CLAIMED'], 'SHIFT_ID'])
never_claimed_in_final = final_shift_ids - original_claimed_shift_ids

# Calculate counts for df_final
num_first_claims_worked_final = first_claims_final[first_claims_final['IS_VERIFIED']].shape[0]
num_first_claims_not_worked_final = first_claims_final[~first_claims_final['IS_VERIFIED']].shape[0]

print("\n=== Stats for df_final ===")
print(f"Total unique SHIFT_IDs in df_final: {len(final_shift_ids)}")
print(f"Shifts with first claimer who worked: {num_first_claims_worked_final}")
print(f"Shifts with first claimer who did NOT work: {num_first_claims_not_worked_final}")
print(f"Shifts never claimed in df_final: {len(never_claimed_in_final)}")
print()

# Save to CSV
#df_final.to_csv("shifts_final.csv", index=False)
print("✅ Saved df_final to 'shifts_final.csv'")
