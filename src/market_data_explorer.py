import yfinance as yf

ticker = "^NSEI"

print("Downloading NIFTY 50 data...")

data = yf.download(
    ticker,
    period="1y",
    interval="1d",
    auto_adjust=True,
    progress=False,
)

if data.empty:
    print("No market data was downloaded.")
else:
    print("\nFirst five rows:")
    print(data.head())

    print("\nLast five rows:")
    print(data.tail())

    print("\nDataset information:")
    print(f"Number of trading days: {len(data)}")
    print(f"Columns: {list(data.columns)}")

    output_path = "data/nifty50_1year.csv"
    data.to_csv(output_path)

    print(f"\nData saved successfully to: {output_path}")