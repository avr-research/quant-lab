from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = Path("data/nifty50_1year.csv")
RESULTS_PATH = Path("results")

SHORT_WINDOW = 20
LONG_WINDOW = 50

# Approximate one-way trading cost:
# 0.05% = 5 basis points.
TRANSACTION_COST = 0.0005

TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.0


def load_close_prices(file_path: Path) -> pd.Series:
    """Load NIFTY 50 closing prices from the saved yfinance CSV."""

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

    close_prices = data[("Close", "^NSEI")].copy()
    close_prices.name = "Close"

    return close_prices.dropna()


def build_strategy(close_prices: pd.Series) -> pd.DataFrame:
    """Create moving averages, trading signals and strategy returns."""

    strategy = pd.DataFrame(index=close_prices.index)

    strategy["Close"] = close_prices
    strategy["Daily Return"] = strategy["Close"].pct_change()

    strategy["MA 20"] = (
        strategy["Close"]
        .rolling(window=SHORT_WINDOW)
        .mean()
    )

    strategy["MA 50"] = (
        strategy["Close"]
        .rolling(window=LONG_WINDOW)
        .mean()
    )

    # Signal:
    # 1 = invested in NIFTY
    # 0 = out of the market
    strategy["Signal"] = np.where(
        strategy["MA 20"] > strategy["MA 50"],
        1,
        0,
    )

    # Shift the signal by one day.
    # Today's moving-average information can only affect tomorrow's return.
    strategy["Position"] = strategy["Signal"].shift(1).fillna(0)

    # A trade occurs whenever the position changes.
    strategy["Trade"] = strategy["Position"].diff().abs().fillna(0)

    strategy["Trading Cost"] = (
        strategy["Trade"] * TRANSACTION_COST
    )

    strategy["Strategy Return"] = (
        strategy["Position"] * strategy["Daily Return"]
        - strategy["Trading Cost"]
    )

    strategy["Buy and Hold Growth"] = (
        1 + strategy["Daily Return"].fillna(0)
    ).cumprod()

    strategy["Strategy Growth"] = (
        1 + strategy["Strategy Return"].fillna(0)
    ).cumprod()

    return strategy


def calculate_cagr(growth: pd.Series) -> float:
    """Calculate compound annual growth rate."""

    growth = growth.dropna()

    if len(growth) < 2:
        return float("nan")

    number_of_years = len(growth) / TRADING_DAYS_PER_YEAR

    return (
        growth.iloc[-1] / growth.iloc[0]
    ) ** (1 / number_of_years) - 1


def calculate_annualized_volatility(
    returns: pd.Series,
) -> float:
    """Calculate annualized volatility from daily returns."""

    return (
        returns.dropna().std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_sharpe_ratio(
    returns: pd.Series,
) -> float:
    """Calculate annualized Sharpe ratio."""

    clean_returns = returns.dropna()

    volatility = clean_returns.std()

    if volatility == 0 or np.isnan(volatility):
        return float("nan")

    daily_risk_free_rate = (
        RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
    )

    excess_returns = (
        clean_returns - daily_risk_free_rate
    )

    return (
        excess_returns.mean()
        / volatility
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_max_drawdown(
    growth: pd.Series,
) -> float:
    """Calculate the worst peak-to-trough decline."""

    running_peak = growth.cummax()
    drawdown = growth / running_peak - 1

    return drawdown.min()


def calculate_exposure(
    position: pd.Series,
) -> float:
    """Calculate percentage of days invested."""

    return position.mean()


def save_performance_chart(
    strategy: pd.DataFrame,
) -> None:
    """Save comparison of strategy and buy-and-hold growth."""

    plt.figure(figsize=(12, 6))

    plt.plot(
        strategy.index,
        strategy["Buy and Hold Growth"],
        label="Buy and Hold",
    )

    plt.plot(
        strategy.index,
        strategy["Strategy Growth"],
        label="MA 20/50 Strategy",
    )

    plt.title(
        "NIFTY 50: Moving-Average Strategy vs Buy and Hold"
    )
    plt.xlabel("Date")
    plt.ylabel("Growth of ₹1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "ma_strategy_vs_buy_hold.png",
        dpi=150,
    )

    plt.close()


def save_signal_chart(
    strategy: pd.DataFrame,
) -> None:
    """Save price, moving averages and entry/exit markers."""

    entries = strategy[
        strategy["Position"].diff() == 1
    ]

    exits = strategy[
        strategy["Position"].diff() == -1
    ]

    plt.figure(figsize=(12, 6))

    plt.plot(
        strategy.index,
        strategy["Close"],
        label="NIFTY 50 Close",
    )

    plt.plot(
        strategy.index,
        strategy["MA 20"],
        label="20-Day MA",
    )

    plt.plot(
        strategy.index,
        strategy["MA 50"],
        label="50-Day MA",
    )

    plt.scatter(
        entries.index,
        entries["Close"],
        marker="^",
        s=80,
        label="Entry",
    )

    plt.scatter(
        exits.index,
        exits["Close"],
        marker="v",
        s=80,
        label="Exit",
    )

    plt.title("NIFTY 50 Moving-Average Trading Signals")
    plt.xlabel("Date")
    plt.ylabel("Index Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "ma_strategy_signals.png",
        dpi=150,
    )

    plt.close()


def main() -> None:
    """Run the complete moving-average backtest."""

    RESULTS_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    close_prices = load_close_prices(DATA_PATH)
    strategy = build_strategy(close_prices)

    buy_hold_cagr = calculate_cagr(
        strategy["Buy and Hold Growth"]
    )

    strategy_cagr = calculate_cagr(
        strategy["Strategy Growth"]
    )

    buy_hold_volatility = calculate_annualized_volatility(
        strategy["Daily Return"]
    )

    strategy_volatility = calculate_annualized_volatility(
        strategy["Strategy Return"]
    )

    buy_hold_sharpe = calculate_sharpe_ratio(
        strategy["Daily Return"]
    )

    strategy_sharpe = calculate_sharpe_ratio(
        strategy["Strategy Return"]
    )

    buy_hold_drawdown = calculate_max_drawdown(
        strategy["Buy and Hold Growth"]
    )

    strategy_drawdown = calculate_max_drawdown(
        strategy["Strategy Growth"]
    )

    number_of_position_changes = int(
        strategy["Trade"].sum()
    )

    completed_trades = (
        number_of_position_changes // 2
    )

    exposure = calculate_exposure(
        strategy["Position"]
    )

    save_performance_chart(strategy)
    save_signal_chart(strategy)

    strategy.to_csv(
        RESULTS_PATH / "ma_strategy_backtest.csv"
    )

    print("=" * 68)
    print("NIFTY 50 MOVING-AVERAGE STRATEGY BACKTEST")
    print("=" * 68)

    print(
        f"Strategy rule          : "
        f"Long when MA {SHORT_WINDOW} > MA {LONG_WINDOW}"
    )

    print(
        f"Transaction cost       : "
        f"{TRANSACTION_COST:.2%} per position change"
    )

    print(
        f"Completed trades       : "
        f"{completed_trades}"
    )

    print(
        f"Market exposure        : "
        f"{exposure:.2%}"
    )

    print("-" * 68)

    print(
        f"{'Metric':<26}"
        f"{'Buy & Hold':>18}"
        f"{'MA Strategy':>18}"
    )

    print(
        f"{'CAGR':<26}"
        f"{buy_hold_cagr:>17.2%}"
        f"{strategy_cagr:>18.2%}"
    )

    print(
        f"{'Annualized volatility':<26}"
        f"{buy_hold_volatility:>17.2%}"
        f"{strategy_volatility:>18.2%}"
    )

    print(
        f"{'Sharpe ratio':<26}"
        f"{buy_hold_sharpe:>17.2f}"
        f"{strategy_sharpe:>18.2f}"
    )

    print(
        f"{'Maximum drawdown':<26}"
        f"{buy_hold_drawdown:>17.2%}"
        f"{strategy_drawdown:>18.2%}"
    )

    print("-" * 68)

    print("Files saved:")
    print("- results/ma_strategy_backtest.csv")
    print("- results/ma_strategy_vs_buy_hold.png")
    print("- results/ma_strategy_signals.png")

    print("=" * 68)


if __name__ == "__main__":
    main()