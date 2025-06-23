import pandas as pd
import os

# No longer in use as I'm now usinh a historical bootstrapping approach However, there was high correlation between asset classes, this 
# suggests I should maybe look at changing my asset classes later. For now, keep as is.

all_asset_classes_for_correlation = [
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

# Calculate Statistical Properties
mean_monthly_returns_gbp = combined_monthly_returns_gbp.mean()
print("\nMean Monthly Returns (GBP):")
print(mean_monthly_returns_gbp)

# 2. Monthly Standard Deviation (Volatility)
std_dev_monthly_gbp = combined_monthly_returns_gbp.std()
print("\nMonthly Standard Deviations (GBP):")
print(std_dev_monthly_gbp)

# 3. Correlation Matrix
correlation_matrix_gbp = combined_monthly_returns_gbp.corr()
print("\nCorrelation Matrix (GBP):")
print(correlation_matrix_gbp)
    
# 4. Covariance Matrix (often needed for multivariate normal distribution sampling)
covariance_matrix_gbp = combined_monthly_returns_gbp.cov()
print("\nCovariance Matrix (GBP):")
print(covariance_matrix_gbp)

# mean_monthly_returns_gbp.to_csv('mean_monthly_returns_GBP.csv')
# std_dev_monthly_gbp.to_csv('std_dev_monthly_gbp.csv')
# correlation_matrix_gbp.to_csv('correlation_matrix_gbp.csv')
# covariance_matrix_gbp.to_csv('covariance_matrix_gbp.csv')
# print("\nStatistical properties saved to CSV files.")
