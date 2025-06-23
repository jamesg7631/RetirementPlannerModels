import yfinance as yf
import pandas as pd

ticker_symbol_list = ['AGG', 'LQD', 'HYG', 'IWDA.L', 'EEM', 'VNQI', 'DBC', 'GLD', 'IUKP.L', 'IGF'] # AGG will require currency conversion EEM data looks strange. Remember I converting to monthly adjusted closing anyway
GBP_to_USD = 'GBPUSD=X'

def process_ticker_to_monthly_returns(ticker_symbol: str, start_date: str, end_date: str):
    """
    Downloads historical data for a ticker, converts it to monthly adjusted returns,
    and saves the results to a CSV.
    """
    try:
        # Download historical data. By default, yfinance adjusts Open, High, Low, Close.
        # The 'Close' column will contain the adjusted prices.
        etf_data = yf.download(ticker_symbol, start=start_date, end=end_date)

        # Handle cases where 'Adj Close' might not exist (common with auto_adjust=True)
        # Use 'Close' column as it's typically already adjusted by yfinance's default behavior
        if 'Adj Close' in etf_data.columns:
            prices_to_use = etf_data['Adj Close']
            print(f"Using 'Adj Close' for {ticker_symbol}")
        elif 'Close' in etf_data.columns:
            prices_to_use = etf_data['Close']
            print(f"Using 'Close' (which is typically adjusted) for {ticker_symbol}")
        else:
            print(f"Error: Neither 'Adj Close' nor 'Close' found for {ticker_symbol}. Skipping.")
            return

        # Resample to Monthly (End of Month)
        monthly_prices = prices_to_use.resample('M').last()

        # Calculate Monthly Returns
        monthly_returns = monthly_prices.pct_change()

        # Drop the first NaN value
        monthly_returns = monthly_returns.dropna()
        # monthly_returns.columns[0] = 'Month'
        print(monthly_returns.columns[0])
        monthly_returns = monthly_returns.rename(columns={monthly_returns.columns[0]: 'Monthly_Return'})

        # Display first few monthly returns
        print(f"\nMonthly Returns for {ticker_symbol} (Head):\n{monthly_returns.head()}")
        print(f"\nMonthly Returns for {ticker_symbol} (Tail):\n{monthly_returns.tail()}")


        # Save the monthly returns to a new CSV file
        monthly_file_name = f"monthly_returns/{ticker_symbol}_monthly_returns.csv"
        # Replace '^' with '_' for valid filenames
        monthly_file_name = monthly_file_name.replace("^", "_")

        # Name the series for a clean CSV header
        monthly_returns.name = 'Monthly_Return'
        monthly_returns.to_csv(monthly_file_name)
        print(f"\nMonthly returns for {ticker_symbol} saved to {monthly_file_name}")

    except Exception as e:
        print(f"Error processing data for {ticker_symbol}: {e}")

# Define common start and end dates
# We agreed to start from Jan 2015 for correlation, but downloading from 2010-11-01
# will give us enough data points for monthly returns to start from Dec 2010 or Jan 2011.
start_date_for_download = "2010-11-01"
end_date_for_download = '2025-06-21' # Current date based on your context

print(f"--- Starting data download and monthly return conversion from {start_date_for_download} to {end_date_for_download} ---")
for ticker in ticker_symbol_list:
    process_ticker_to_monthly_returns(ticker, start_date_for_download, end_date_for_download)

process_ticker_to_monthly_returns(GBP_to_USD, start_date_for_download, end_date_for_download)

print("\n--- All monthly return CSVs created ---")