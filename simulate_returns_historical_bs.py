import pandas as pd
import numpy as np
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

# Monte carlo Simulation Setup
# Simulation Parameters

num_simulations = 10000
planning_horizon_years = 75
planning_horizon_months = planning_horizon_years * 12

# Get the number of historical months for bootstrapping
num_historical_months = len(combined_monthly_returns_gbp)

if num_historical_months < planning_horizon_months:
    print(f"\nWarning: Number of historical months ({num_historical_months}) is less than the planning horizon in months ({planning_horizon_months}).")
    print("This means some simulated paths will reuse historical months more frequently than others.")
    print("This is normal for bootstrapping, but be aware of the implications.")

print(f"\n--- Running {num_simulations} Monte Carlo Simulations ({planning_horizon_years} years horizon) ---")
print("Using Historical Bootstrapping method...")

# Initialize a structure to store all simulated asset paths
# This will be a dictionary where keys are asset names, and values are lists of lists/arrays
# Each inner list will represent one simulation run's 900 monthly returns for that asset
simulated_asset_paths = {col: [] for col in combined_monthly_returns_gbp.columns}

for s in range(num_simulations):
    if (s + 1) % 1000 == 0:
        print(f"Simulations complete: {s + 1} / {num_simulations}")

    # For each simulation, we will generate a sequence of monthly returns for all assets
    # by randomly sampling rows from our historical data
    
    # Store monthly returns for the current simulation run
    current_sim_returns = {col: [] for col in combined_monthly_returns_gbp.columns}

    for month in range(planning_horizon_months):
        # Randomly select an index from the historical data
        random_index = np.random.randint(0, num_historical_months)
        
        # Get the actual historical returns for that random month for all assets
        historical_returns_this_month = combined_monthly_returns_gbp.iloc[random_index]
        
        # Append these returns to the current simulation's path for each asset
        for asset_name, return_val in historical_returns_this_month.items():
            current_sim_returns[asset_name].append(return_val)

    # After generating all months for this simulation, store the paths
    for asset_name in combined_monthly_returns_gbp.columns:
        simulated_asset_paths[asset_name].append(current_sim_returns[asset_name])

print("\n--- Monte Carlo Simulation Complete ---")

# --- Verify and Save Simulated Data ---
print("\n--- Verifying and Saving Simulated Data ---")

# Convert the lists of lists into NumPy arrays for easier manipulation and smaller storage
# And also to check the structure
for asset_name, paths in simulated_asset_paths.items():
    simulated_asset_paths[asset_name] = np.array(paths)
    print(f"Asset '{asset_name}': Shape of simulated paths is {simulated_asset_paths[asset_name].shape} (Simulations x Months)")
    # Expected shape: (10000, 900)

# Save the simulated paths to disk
# Using NumPy's save is efficient for numerical arrays. You can also save as a dictionary of arrays.
output_folder = "simulated_paths"
os.makedirs(output_folder, exist_ok=True)

for asset_name, data_array in simulated_asset_paths.items():
    # Save each asset's simulated paths as a .npy file
    np.save(os.path.join(output_folder, f"{asset_name}_simulated_returns.npy"), data_array)
    print(f"Saved simulated returns for {asset_name} to {os.path.join(output_folder, f'{asset_name}_simulated_returns.npy')}")

print(f"\nAll simulated asset paths saved to the '{output_folder}' folder.")

