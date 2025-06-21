import yfinance as yf
import pandas as pd

# Define the ETF ticker symbol
ticker_symbol = "GBPUSD=X" # Example: S&P 500 ETF

# Define the start and end dates for your historical data
start_date = "2010-11-01"
end_date = "2025-06-21" # Current date (or your desired end date)

try:
    # Download historical data
    etf_data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Display the first few rows of the data
    print(etf_data.head())

    # Save the data to a CSV file
    file_name = f"{ticker_symbol}_historical_data.csv"
    etf_data.to_csv(file_name)
    print(f"\nHistorical data for {ticker_symbol} saved to {file_name}")

except Exception as e:
    print(f"Error downloading data: {e}")

# You can also get data for a specific period like "1y", "5y", "max"
# etf_data_max = yf.Ticker(ticker_symbol).history(period="max")
# print("\nData for max period:")
# print(etf_data_max.head())