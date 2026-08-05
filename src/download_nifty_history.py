from pathlib import Path

import yfinance as yf


TICKER = "^NSEI"
START_DATE = "2010-01-01"
OUTPUT_PATH = Path("data/nifty50_history.csv")


def download_market_data() -> None:
    """Download long-term daily NIFTY 50 market data."""

    print("=" * 65)
    print("DOWNLOADING LONG-TERM NIFTY 50 DATA")
    print("=" * 65)

    data = yf.download(
        TICKER,
        start=START_DATE,
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        raise RuntimeError(
            "No data was downloaded. Check the internet connection "
            "and ticker symbol."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(OUTPUT_PATH)

    print(f"Ticker              : {TICKER}")
    print(f"Start date          : {data.index.min().date()}")
    print(f"Latest date         : {data.index.max().date()}")
    print(f"Trading-day records : {len(data):,}")
    print(f"Saved to            : {OUTPUT_PATH}")

    print("=" * 65)


if __name__ == "__main__":
    download_market_data()