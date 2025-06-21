import yfinance as yf
import pandas as pd
import os

# Define the list of tickers for which you have monthly return CSVs
# Based on your latest confirmation, all of these except IUKP.L are USD-denominated
asset_tickers_to_convert = [
    '_IRX',  # Represents ^IRX in filename
    'AGG',
    'LQD',
    'HYG',
    'IWDA.L', # Treating as USD based on your latest check
    'EEM',
    'VNQI',
    'DBC',
    'GLD',
    'IGF'
]

fx_ticker_symbol = "GBPUSD=X"

def get_monthly_fx_returns(ticker: str, start: str, end: str) -> pd.Series:
    """
    Downloads daily FX data, converts it to monthly returns, and returns the series.
    """
    fx_data = yf.download(ticker, start=start, end=end)
    if 'Adj Close' in fx_data.columns:
        fx_prices = fx_data['Adj Close']
    elif 'Close' in fx_data.columns:
        fx_prices = fx_data['Close']
    else:
        raise ValueError(f"Could not find 'Adj Close' or 'Close' for FX ticker {ticker}")

    monthly_fx_prices = fx_prices.resample('M').last()
    monthly_fx_returns = monthly_fx_prices.pct_change().dropna()
    monthly_fx_returns.name = 'FX_Return' # Name the series for merging
    return monthly_fx_returns

def convert_usd_to_gbp_returns(asset_ticker: str, currency_conversion: str):
    """
    Loads monthly returns for a USD-denominated asset, converts them to GBP returns
    using the provided FX returns, and saves the new GBP returns to a CSV.
    """
    input_file_name = f"{asset_ticker}_monthly_returns.csv"
    currency_conversion = f"{currency_conversion}_monthly_returns.csv"
    if not os.path.exists(input_file_name):
        print(f"Error: Monthly returns CSV for {asset_ticker} not found at {input_file_name}. Skipping conversion.")
        return

    try:
        # Load the monthly returns for the USD asset
        # Ensure 'Date' is parsed as datetime and set as index
        usd_returns_df = pd.read_csv(input_file_name, index_col='Date', parse_dates=True)
        usd_to_gbp_df = pd.read_csv(currency_conversion, index_col='Date', parse_dates=True)
        # Assuming the returns column is named 'Monthly_Return' from previous step
        usd_returns_series = usd_returns_df['Monthly_Returns']
        usd_to_gbp_series = usd_to_gbp_df['Monthly_Returns']

        # Align the FX returns with the USD asset returns
        # This will automatically handle any date mismatches by creating NaNs
        combined_data = pd.DataFrame({
            'USD_Return': usd_returns_series,
            'FX_Return': usd_to_gbp_series
        }).dropna() # Drop rows where either USD return or FX return is missing

        # Ensure we have enough data after merging
        if combined_data.empty:
            print(f"Warning: No overlapping historical data found for {asset_ticker} and FX rates. Skipping conversion.")
            return

        # Perform the currency conversion: R_GBP = (1 + R_USD) * (1 + R_FX) - 1
        # If GBPUSD=X increases, GBP strengthens, so a USD asset's return in GBP will be (1+R_USD)*(1+FX_Return)-1
        # Example: USD asset +10%, GBP strengthens +5% (more USD per GBP)
        # (1+0.10)*(1+0.05)-1 = 1.10 * 1.05 - 1 = 1.155 - 1 = 0.155 (15.5% in GBP)
        gbp_returns_series = (1 + combined_data['USD_Return']) * (1 + combined_data['FX_Return']) - 1
        gbp_returns_series.name = 'Monthly_Return_GBP' # Name for the new CSV header

        # Save the converted GBP returns to a new CSV
        output_file_name = f"{asset_ticker}_monthly_returns_GBP.csv"
        gbp_returns_series.to_csv(output_file_name)
        print(f"Converted monthly returns for {asset_ticker} to GBP and saved to {output_file_name}")

    except Exception as e:
        print(f"Error converting {asset_ticker} to GBP: {e}")

# --- Main Execution ---

# print(f"--- Step 1: Getting monthly FX returns for {fx_ticker_symbol} ---")
# try:
#     monthly_gbpusd_returns = get_monthly_fx_returns(fx_ticker_symbol, "2010-11-01", '2025-06-21')
#     print(f"FX returns obtained from {monthly_gbpusd_returns.index.min().strftime('%Y-%m')} to {monthly_gbpusd_returns.index.max().strftime('%Y-%m')}")
# except Exception as e:
#     print(f"Failed to get FX data. Cannot proceed with conversions: {e}")
#     exit() # Exit if FX data cannot be obtained
GBP_to_USD = 'GBPUSD=X'
print("\n--- Step 2: Converting USD asset monthly returns to GBP ---")
for ticker in asset_tickers_to_convert:
    convert_usd_to_gbp_returns(ticker, GBP_to_USD)

print(f"\n--- All specified USD asset conversions to GBP complete. IUKP.L remains in original GBP. ---")

