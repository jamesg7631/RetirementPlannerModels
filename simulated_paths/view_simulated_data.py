import numpy as np
import pandas as pd
import os
# Doesn't process any data this file. Used for Sanity checks

# Define the folder where you saved the simulated paths
output_folder = "simulated_paths"

# Re-create the list of all asset class names (without the .npy filename suffix)
all_asset_names = [
    '_IRX', 'AGG', 'LQD', 'HYG', 'IWDA.L', 'EEM', 'VNQI', 'DBC', 'GLD', 'IGF', 'IUKP.L'
]

# --- Load all files into a dictionary for easier access ---
loaded_all_simulated_paths = {}
print("--- Loading all simulated data files ---")
for asset_name in all_asset_names:
    file_path = os.path.join(output_folder, f"{asset_name}_simulated_returns.npy")
    try:
        loaded_all_simulated_paths[asset_name] = np.load(file_path)
        print(f"Loaded {asset_name}: {loaded_all_simulated_paths[asset_name].shape}")
    except FileNotFoundError:
        print(f"Warning: File not found for {asset_name} at {file_path}. Skipping.")
    except Exception as e:
        print(f"An error occurred loading {asset_name}: {e}")

# Check if any data was loaded
if not loaded_all_simulated_paths:
    print("No simulated data was loaded. Cannot proceed with tabular view.")
    exit()

# Define simulation parameters based on loaded data
num_simulations = loaded_all_simulated_paths[all_asset_names[0]].shape[0]
planning_horizon_months = loaded_all_simulated_paths[all_asset_names[0]].shape[1]
planning_horizon_years = planning_horizon_months // 12

print(f"\nTotal simulations: {num_simulations}")
print(f"Planning horizon: {planning_horizon_years} years ({planning_horizon_months} months)")

# --- Process each asset to get annual returns for all simulations ---

print("\n--- Generating Annual Returns DataFrames for Each Asset ---")

# This dictionary will store a DataFrame for each asset
annual_returns_dfs_by_asset = {}

for asset_name in all_asset_names:
    if asset_name not in loaded_all_simulated_paths:
        continue # Skip if the asset wasn't loaded

    print(f"Processing annual returns for: {asset_name}")
    
    # Get the 2D array of monthly returns for the current asset
    # Shape: (num_simulations, planning_horizon_months)
    asset_monthly_returns = loaded_all_simulated_paths[asset_name]

    # Initialize a list to store annual return arrays for each simulation
    annual_returns_for_asset = []

    # Calculate annual returns for each simulation run
    for sim_idx in range(num_simulations):
        # Get the monthly returns for the current simulation run (a 1D array of 900 months)
        current_sim_monthly_returns = asset_monthly_returns[sim_idx, :]

        # Calculate cumulative returns over the entire horizon (for compounding)
        # (1 + r1) * (1 + r2) * ... - 1
        cumulative_returns = (1 + current_sim_monthly_returns).cumprod() - 1

        # Extract the return at the end of each year (month 11, 23, 35, etc., 0-indexed)
        # This will be the cumulative return from month 0 to that specific year-end month
        # We need to compute the *annualized* return for each year, not the cumulative return from start.
        
        # Calculate yearly returns
        yearly_returns = []
        for year_idx in range(planning_horizon_years):
            start_month_idx = year_idx * 12
            end_month_idx = start_month_idx + 12 # This is exclusive, so it gets months [0..11] for year 1 etc.

            # Get the monthly returns for the current year
            returns_this_year = current_sim_monthly_returns[start_month_idx:end_month_idx]
            
            # Calculate the compounded annual return for this year
            compounded_annual_return = (1 + returns_this_year).prod() - 1
            yearly_returns.append(compounded_annual_return)
        
        annual_returns_for_asset.append(yearly_returns)

    # Convert the list of lists into a DataFrame
    # Rows are simulations, columns are years
    annual_df = pd.DataFrame(annual_returns_for_asset, 
                             index=[f"Sim_{i+1}" for i in range(num_simulations)],
                             columns=[f"Year_{i+1}" for i in range(planning_horizon_years)])
    
    annual_returns_dfs_by_asset[asset_name] = annual_df

    # Display a sample (first 5 simulations, first 5 years)
    print(f"\n--- Sample Annual Returns for {asset_name} (First 5 Simulations, First 5 Years) ---")
    print(annual_df.head())
    print(f"\nFull DataFrame for {asset_name} has shape: {annual_df.shape}") # Expected (10000, 75)

    # Optional: Save this DataFrame to a CSV
    # annual_df.to_csv(os.path.join(output_folder, f"{asset_name}_annual_returns_all_sims.csv"))
    # print(f"Saved annual returns for {asset_name} to CSV.")


print("\n--- All Annual Returns DataFrames Generated ---")

# --- Example: How to access and view a specific asset's annual returns DataFrame ---
# For example, to see the full annual returns for IWDA.L
# print("\nFull Annual Returns DataFrame for IWDA.L:")
# print(annual_returns_dfs_by_asset['IWDA.L'])

# You can now access any asset's annual returns like this:
# iwda_annual_df = annual_returns_dfs_by_asset['IWDA.L']
# agg_annual_df = annual_returns_dfs_by_asset['AGG']