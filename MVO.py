from scipy.optimize import minimize
import pandas as pd
import numpy as np
import os

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
print(efficient_frontier.head())

# Plotting the efficient frontier
import matplotlib.pyplot as plt

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