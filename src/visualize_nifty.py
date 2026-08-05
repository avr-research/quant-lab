from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path("data/nifty50_1year.csv")
RESULTS_PATH = Path("results")


def load_nifty_data(file_path: Path) -> pd.DataFrame:
    """Load the NIFTY CSV created by market_data_explorer.py."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}\n"
            "Run src/market_data_explorer.py first."
        )

    data = pd.read_csv(
        file_path,
        header=[0, 1],
        index_col=0,
        parse_dates=True,
    )

    return data


def prepare_analysis(data: pd.DataFrame) -> pd.DataFrame:
    """Create the price, return, moving-average and risk columns."""

    analysis = pd.DataFrame(index=data.index)

    analysis["Close"] = data[("Close", "^NSEI")]
    analysis["Daily Return"] = analysis["Close"].pct_change()

    analysis["MA 20"] = analysis["Close"].rolling(window=20).mean()
    analysis["MA 50"] = analysis["Close"].rolling(window=50).mean()

    analysis["Rolling Volatility 20D"] = (
        analysis["Daily Return"].rolling(window=20).std()
    )

    running_peak = analysis["Close"].cummax()

    analysis["Drawdown"] = (
        analysis["Close"] / running_peak
    ) - 1

    return analysis


def save_price_chart(analysis: pd.DataFrame) -> None:
    """Plot NIFTY price with moving averages."""

    plt.figure(figsize=(12, 6))

    plt.plot(
        analysis.index,
        analysis["Close"],
        label="NIFTY 50 Close",
    )

    plt.plot(
        analysis.index,
        analysis["MA 20"],
        label="20-Day Moving Average",
    )

    plt.plot(
        analysis.index,
        analysis["MA 50"],
        label="50-Day Moving Average",
    )

    plt.title("NIFTY 50 Price and Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Index Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "nifty_price_and_moving_averages.png",
        dpi=150,
    )

    plt.close()


def save_daily_returns_chart(analysis: pd.DataFrame) -> None:
    """Plot daily percentage returns."""

    plt.figure(figsize=(12, 5))

    plt.plot(
        analysis.index,
        analysis["Daily Return"] * 100,
    )

    plt.axhline(0, linewidth=1)

    plt.title("NIFTY 50 Daily Returns")
    plt.xlabel("Date")
    plt.ylabel("Daily Return (%)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "nifty_daily_returns.png",
        dpi=150,
    )

    plt.close()


def save_return_distribution(analysis: pd.DataFrame) -> None:
    """Plot the distribution of daily returns."""

    returns = analysis["Daily Return"].dropna() * 100

    plt.figure(figsize=(10, 5))

    plt.hist(
        returns,
        bins=30,
        edgecolor="black",
    )

    plt.title("Distribution of NIFTY 50 Daily Returns")
    plt.xlabel("Daily Return (%)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "nifty_return_distribution.png",
        dpi=150,
    )

    plt.close()


def save_volatility_chart(analysis: pd.DataFrame) -> None:
    """Plot rolling 20-day daily volatility."""

    plt.figure(figsize=(12, 5))

    plt.plot(
        analysis.index,
        analysis["Rolling Volatility 20D"] * 100,
    )

    plt.title("NIFTY 50 Rolling 20-Day Volatility")
    plt.xlabel("Date")
    plt.ylabel("Daily Volatility (%)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "nifty_rolling_volatility.png",
        dpi=150,
    )

    plt.close()


def save_drawdown_chart(analysis: pd.DataFrame) -> None:
    """Plot decline from the previous running peak."""

    plt.figure(figsize=(12, 5))

    plt.plot(
        analysis.index,
        analysis["Drawdown"] * 100,
    )

    plt.axhline(0, linewidth=1)

    plt.title("NIFTY 50 Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown (%)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "nifty_drawdown.png",
        dpi=150,
    )

    plt.close()


def main() -> None:
    """Run the complete NIFTY visual-analysis workflow."""

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)

    data = load_nifty_data(DATA_PATH)
    analysis = prepare_analysis(data)

    save_price_chart(analysis)
    save_daily_returns_chart(analysis)
    save_return_distribution(analysis)
    save_volatility_chart(analysis)
    save_drawdown_chart(analysis)

    analysis.to_csv(
        RESULTS_PATH / "nifty_analysis.csv"
    )

    print("=" * 60)
    print("NIFTY VISUAL ANALYSIS COMPLETED")
    print("=" * 60)

    print(
        f"Latest close             : "
        f"{analysis['Close'].iloc[-1]:,.2f}"
    )

    print(
        f"Latest 20-day average    : "
        f"{analysis['MA 20'].iloc[-1]:,.2f}"
    )

    print(
        f"Latest 50-day average    : "
        f"{analysis['MA 50'].iloc[-1]:,.2f}"
    )

    print(
        f"Maximum drawdown         : "
        f"{analysis['Drawdown'].min():.2%}"
    )

    print("\nFiles saved inside the results folder:")
    print("- nifty_price_and_moving_averages.png")
    print("- nifty_daily_returns.png")
    print("- nifty_return_distribution.png")
    print("- nifty_rolling_volatility.png")
    print("- nifty_drawdown.png")
    print("- nifty_analysis.csv")

    print("=" * 60)


if __name__ == "__main__":
    main()