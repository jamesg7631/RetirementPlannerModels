import pandas as pd
import numpy as np
import os
from scipy.optimize import minimize
import matplotlib.pyplot as plt

asset_class_path = 'gbp_monthly_returns/'

all_asset_classes_for_correlation = [
    'Moneymarket_monthly_returns_GBP.csv',
    'AGG_monthly_returns_GBP.csv',
    'LQD_monthly_returns_GBP.csv',
    'HYG_monthly_returns_GBP.csv',
    'IWDA.L_monthly_returns_GBP.csv',
    'EEM_monthly_returns_GBP.csv',
    'VNQI_monthly_returns_GBP.csv',
    'DBC_monthly_returns_GBP.csv',
    'GLD_monthly_returns_GBP.csv',
    'IGF_monthly_returns_GBP.csv',
    'IUKP.L_monthly_returns.csv', # This one is already in GBP
]

def create_combined_returns_df(file_list: list):
    all_returns = {}
    for filename in file_list:
        try:
            file_path = asset_class_path + filename
            ticker_name = filename.replace('_monthly_returns_GBP.csv', '').replace('_monthly_returns.csv', '')
            df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
            if 'Monthly_Return' in df.columns:
                all_returns[ticker_name] = df['Monthly_Return']
            else:
                print(f"Warning: No recognised return column in {file_path}. Skipping.")
        except FileNotFoundError:
            print(f"Error: File not found for {file_path}. Skipping.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

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

# Calculate the MVO inputs from historical data
num_months_in_year = 12

# 1. Expected Returns (Annualized)
# Convert monthly mean to annualized mean
expected_returns_annualized = (1 + combined_monthly_returns_gbp.mean())**num_months_in_year - 1
print("\nAnnualized Expected Returns (from historical monthly means):")
print(expected_returns_annualized)

# 2. Covariance Matrix (Annualized)
# Multiply monthly covariance by 12 to annualize variance, assuming i.i.d. returns
covariance_matrix_annualized = combined_monthly_returns_gbp.cov() * num_months_in_year
print("\nAnnualized Covariance Matrix:")
print(covariance_matrix_annualized)

# 3. Standard Deviations (Annualized)
# For standard deviation, it's sqrt(annualized variance)
std_devs_annualized = np.sqrt(np.diag(covariance_matrix_annualized))
std_devs_annualized = pd.Series(std_devs_annualized, index=combined_monthly_returns_gbp.columns)
print("\nAnnualized Standard Deviations (Volatility):")
print(std_devs_annualized)

# Define the number of assets
num_assets = len(expected_returns_annualized)
asset_names = expected_returns_annualized.index.tolist()

# Define functions for portfolio return, volatility, and negative Sharpe Ratio (for optimization)
def portfolio_return(weights, expected_returns):
    return np.sum(expected_returns * weights)

def portfolio_volatility(weights, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

# We need to maximize return for a given risk, or minimize risk for a given return.
# For simplicity, we'll plot a frontier by minimizing volatility for a range of target returns.
# Or, we can generate many random portfolios and filter for the efficient ones.
# Given your context, let's use the random portfolio generation for visualization,
# which is often more intuitive for seeing the frontier directly.

num_portfolios = 50000 # Number of random portfolios to generate

# Store results for plotting
results = np.zeros((3, num_portfolios)) # Row 0: Vol, Row 1: Return, Row 2: Sharpe Ratio
all_weights = np.zeros((num_portfolios, num_assets)) # Store all weights

print(f"\n--- Generating {num_portfolios} Random Portfolios for MVO ---")

for i in range(num_portfolios):
    weights = np.random.random(num_assets)
    weights /= np.sum(weights) # Normalize weights to sum to 1
    
    p_return = portfolio_return(weights, expected_returns_annualized.values)
    p_volatility = portfolio_volatility(weights, covariance_matrix_annualized.values)
    
    results[0,i] = p_volatility
    results[1,i] = p_return
    results[2,i] = p_return / p_volatility # Sharpe Ratio (assuming 0 risk-free rate for simplicity)
    all_weights[i,:] = weights

# Convert results to a DataFrame
columns = ['Volatility', 'Return', 'Sharpe_Ratio'] + asset_names
portfolios_df = pd.DataFrame(data=np.c_[results.T, all_weights], columns=columns)

print("Sample of generated portfolios:")
print(portfolios_df.head())

# Find the Efficient Frontier (approximate from random portfolios)
# For each level of volatility, find the portfolio with the highest return
# This is a brute-force way; proper MVO involves optimization, but this gives a good visual.
# Sort by volatility, then by return for each volatility bucket.
portfolios_df_sorted = portfolios_df.sort_values(by=['Volatility', 'Return'], ascending=[True, False])

# Discretize volatility to find the frontier
# Group by small volatility bins and pick the max return in each bin
volatility_bins = np.linspace(portfolios_df_sorted['Volatility'].min(), portfolios_df_sorted['Volatility'].max(), 100)
efficient_frontier = pd.DataFrame(columns=portfolios_df.columns)

for i in range(len(volatility_bins) - 1):
    bin_start = volatility_bins[i]
    bin_end = volatility_bins[i+1]
    
    # Portfolios within this volatility bin
    bin_portfolios = portfolios_df_sorted[(portfolios_df_sorted['Volatility'] >= bin_start) & 
                                          (portfolios_df_sorted['Volatility'] < bin_end)]
    
    if not bin_portfolios.empty:
        # Find the portfolio with the max return in this bin
        efficient_portfolio = bin_portfolios.loc[bin_portfolios['Return'].idxmax()]
        efficient_frontier = pd.concat([efficient_frontier, pd.DataFrame([efficient_portfolio])], ignore_index=True)

# Remove duplicates if any (due to binning) and sort by volatility
efficient_frontier.drop_duplicates(subset=['Volatility'], inplace=True)
efficient_frontier.sort_values(by='Volatility', inplace=True)

print("\nApproximate Efficient Frontier (first 5 points):")
print(efficient_frontier)

# Plotting the efficient frontier


plt.figure(figsize=(10, 6))
plt.scatter(portfolios_df['Volatility'], portfolios_df['Return'], c=portfolios_df['Sharpe_Ratio'], cmap='viridis', s=10, alpha=0.5)
plt.colorbar(label='Sharpe Ratio (Annualized)')
plt.scatter(efficient_frontier['Volatility'], efficient_frontier['Return'], color='red', marker='o', s=50, label='Efficient Frontier')
plt.title('Portfolio Optimization - Efficient Frontier (Annualized)')
plt.xlabel('Annualized Volatility (Standard Deviation)')
plt.ylabel('Annualized Return')
plt.grid(True)
plt.legend()
plt.show()

risk_band_definitions = {
    # Risk Level: {'vol_min': X, 'vol_max': Y, 'dd_max': Z}
    # Volatility is from the plot. dd_max you will verify after running the next code.
    1: {'vol_min': 0.090, 'vol_max': 0.100, 'dd_max': -0.075}, # ~9.0% to 10.0% Vol, Max 7.5% DD
    2: {'vol_min': 0.100, 'vol_max': 0.110, 'dd_max': -0.100}, # ~10.0% to 11.0% Vol, Max 10% DD
    3: {'vol_min': 0.110, 'vol_max': 0.120, 'dd_max': -0.125}, # ~11.0% to 12.0% Vol, Max 12.5% DD
    4: {'vol_min': 0.120, 'vol_max': 0.130, 'dd_max': -0.150}, # ~12.0% to 13.0% Vol, Max 15% DD
    5: {'vol_min': 0.130, 'vol_max': 0.140, 'dd_max': -0.175}, # ~13.0% to 14.0% Vol, Max 17.5% DD
    6: {'vol_min': 0.140, 'vol_max': 0.150, 'dd_max': -0.200}, # ~14.0% to 15.0% Vol, Max 20% DD
    7: {'vol_min': 0.150, 'vol_max': 0.160, 'dd_max': -0.250}, # ~15.0% to 16.0% Vol, Max 25% DD
    8: {'vol_min': 0.160, 'vol_max': 0.170, 'dd_max': -0.300}, # ~16.0% to 17.0% Vol, Max 30% DD
    9: {'vol_min': 0.170, 'vol_max': 0.180, 'dd_max': -0.350}, # ~17.0% to 18.0% Vol, Max 35% DD
    10: {'vol_min': 0.180, 'vol_max': 1.0, 'dd_max': -1.0}    # >18.0% Vol, more than 35% DD
}

# Your `target_volatilities_for_risk_levels` would also align with these:
target_volatilities_for_risk_levels = {
    1: 0.095,  # ~9.5%
    2: 0.105,  # ~10.5%
    3: 0.115,  # ~11.5%
    4: 0.125,  # ~12.5%
    5: 0.135,  # ~13.5%
    6: 0.145,  # ~14.5%
    7: 0.155,  # ~15.5%
    8: 0.165,  # ~16.5%
    9: 0.175,  # ~17.5%
    10: 0.185   # ~18.5%
}
