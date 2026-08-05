import pandas as pd

file_path = "data/nifty50_1year.csv"

data = pd.read_csv(
    file_path,
    header=[0, 1],
    index_col=0,
    parse_dates=True,
)

# Extract NIFTY 50 closing prices from the MultiIndex columns.
close_prices = data[("Close", "^NSEI")]

# Percentage change from one trading day to the next.
daily_returns = close_prices.pct_change().dropna()

print("=" * 60)
print("NIFTY 50 RETURN ANALYSIS")
print("=" * 60)

print(f"Observations        : {len(daily_returns)}")
print(f"Average daily return: {daily_returns.mean():.4%}")
print(f"Daily volatility    : {daily_returns.std():.4%}")
print(f"Best trading day    : {daily_returns.max():.4%}")
print(f"Worst trading day   : {daily_returns.min():.4%}")

print("=" * 60)