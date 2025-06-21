import pandas as pd
import os

all_asset_classes_for_correlation = [
    '_IRX_monthly_returns_GBP.csv',
    'AGG_monthly_returns_GBP.csv',
    'LQD_monthly_returns_GBP.csv',
    'HYG_monthly_returns_GBP.csv',
    'IWDA.L_monthly_returns_GBP.csv',
    'EEM_monthly_returns_GBP.csv',
    'VNQI_monthly_returns_GBP.csv',
    'DBC_monthly_returns_GBP.csv',
    'GLD_monthly_returns_GBP.csv',
    'IGF_monthly_returns_GBP.csv',
    'IUKP.L_monthly_returns.csv' # This one is already in GBP
]

def create_combined_returns_df(file_list: list):
    all_returns = {}
    for filename in file_list:
        try:
            ticker_name = filename.replace('_monthly_returns_GBP.csv', '').replace('_monthly_returns.csv', '')

            df = pd.read_csv(filename, index_col='Date', parse_dates=True)
            if 'Monthly_Return' in df.columns:
                all_returns[ticker_name] = df['Monthly_Return']
            else:
                print(f"Warning: No recognised return column in {filename}. Skipping.")
        except FileNotFoundError:
            print(f"Error: File not found for {filename}. Skipping.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Combine all series into a single DataFrame
    combined_df = pd.DataFrame(all_returns)
    
    ##Check the below
    initial_rows = len(combined_df)
    combined_df.dropna(inplace=True)
    final_rows = len(combined_df)

    if initial_rows != final_rows:
        print(f"Warning: Dropped {initial_rows - final_rows} rows due to missing data for some assets.")
        print(f"Common data period: {combined_df.index.min().strftime('%Y-%m')} to {combined_df.index.max().strftime('%Y-%m')}")

    return combined_df

# Create the combined DataFrame
print("--- Consolidating Monthly Returns Data ---")
combined_monthly_returns_gbp = create_combined_returns_df(all_asset_classes_for_correlation)

if combined_monthly_returns_gbp.empty:
    print("No data to proceed. Please check your CSV files and paths.")
    exit()

print(f"\nCombined DataFrame shape: {combined_monthly_returns_gbp.shape}")
print(f"Data covers: {combined_monthly_returns_gbp.index.min().strftime('%Y-%m')} to {combined_monthly_returns_gbp.index.max().strftime('%Y-%m')}")
print("\nFirst 5 rows of combined data:")
print(combined_monthly_returns_gbp.head())
print("\nLast 5 rows of combined data:")
print(combined_monthly_returns_gbp.tail())
    