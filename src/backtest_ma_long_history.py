from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = Path("data/nifty50_history.csv")
RESULTS_PATH = Path("results")

SHORT_WINDOW = 20
LONG_WINDOW = 50

TRANSACTION_COST = 0.0005
TRADING_DAYS_PER_YEAR = 252


def load_prices(file_path: Path) -> pd.Series:
    """Load NIFTY closing prices from the yfinance CSV."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing data file: {file_path}\n"
            "Run src/download_nifty_history.py first."
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


def create_backtest(close_prices: pd.Series) -> pd.DataFrame:
    """Create the moving-average strategy backtest."""

    backtest = pd.DataFrame(index=close_prices.index)

    backtest["Close"] = close_prices

    backtest["Market Return"] = (
        backtest["Close"]
        .pct_change()
        .fillna(0)
    )

    backtest["Short MA"] = (
        backtest["Close"]
        .rolling(SHORT_WINDOW)
        .mean()
    )

    backtest["Long MA"] = (
        backtest["Close"]
        .rolling(LONG_WINDOW)
        .mean()
    )

    backtest["Signal"] = np.where(
        backtest["Short MA"] > backtest["Long MA"],
        1,
        0,
    )

    # The shift prevents look-ahead bias.
    backtest["Position"] = (
        backtest["Signal"]
        .shift(1)
        .fillna(0)
    )

    backtest["Position Change"] = (
        backtest["Position"]
        .diff()
        .abs()
        .fillna(0)
    )

    backtest["Trading Cost"] = (
        backtest["Position Change"]
        * TRANSACTION_COST
    )

    backtest["Strategy Return"] = (
        backtest["Position"]
        * backtest["Market Return"]
        - backtest["Trading Cost"]
    )

    backtest["Buy Hold Growth"] = (
        1 + backtest["Market Return"]
    ).cumprod()

    backtest["Strategy Growth"] = (
        1 + backtest["Strategy Return"]
    ).cumprod()

    return backtest


def calculate_cagr(growth: pd.Series) -> float:
    """Calculate compound annual growth rate."""

    years = (
        growth.index[-1] - growth.index[0]
    ).days / 365.25

    if years <= 0:
        return float("nan")

    return (
        growth.iloc[-1] / growth.iloc[0]
    ) ** (1 / years) - 1


def calculate_volatility(returns: pd.Series) -> float:
    """Calculate annualized volatility."""

    return (
        returns.std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_sharpe(returns: pd.Series) -> float:
    """Calculate annualized Sharpe ratio using a zero risk-free rate."""

    volatility = returns.std()

    if volatility == 0 or np.isnan(volatility):
        return float("nan")

    return (
        returns.mean()
        / volatility
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_max_drawdown(growth: pd.Series) -> float:
    """Calculate the worst peak-to-trough decline."""

    running_peak = growth.cummax()
    drawdown = growth / running_peak - 1

    return drawdown.min()


def save_growth_chart(backtest: pd.DataFrame) -> None:
    """Save the long-term strategy comparison chart."""

    plt.figure(figsize=(13, 7))

    plt.plot(
        backtest.index,
        backtest["Buy Hold Growth"],
        label="Buy and Hold",
    )

    plt.plot(
        backtest.index,
        backtest["Strategy Growth"],
        label="MA 20/50 Strategy",
    )

    plt.title(
        "NIFTY 50 Long-Term Backtest: "
        "MA 20/50 Strategy vs Buy and Hold"
    )

    plt.xlabel("Date")
    plt.ylabel("Growth of ₹1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "ma_long_history_growth.png",
        dpi=150,
    )

    plt.close()


def main() -> None:
    """Run and report the long-history backtest."""

    RESULTS_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    close_prices = load_prices(DATA_PATH)
    backtest = create_backtest(close_prices)

    buy_hold_cagr = calculate_cagr(
        backtest["Buy Hold Growth"]
    )

    strategy_cagr = calculate_cagr(
        backtest["Strategy Growth"]
    )

    buy_hold_volatility = calculate_volatility(
        backtest["Market Return"]
    )

    strategy_volatility = calculate_volatility(
        backtest["Strategy Return"]
    )

    buy_hold_sharpe = calculate_sharpe(
        backtest["Market Return"]
    )

    strategy_sharpe = calculate_sharpe(
        backtest["Strategy Return"]
    )

    buy_hold_drawdown = calculate_max_drawdown(
        backtest["Buy Hold Growth"]
    )

    strategy_drawdown = calculate_max_drawdown(
        backtest["Strategy Growth"]
    )

    position_changes = int(
        backtest["Position Change"].sum()
    )

    completed_trades = position_changes // 2

    market_exposure = (
        backtest["Position"].mean()
    )

    total_cost = (
        backtest["Trading Cost"].sum()
    )

    save_growth_chart(backtest)

    backtest.to_csv(
        RESULTS_PATH / "ma_long_history_backtest.csv"
    )

    print("=" * 74)
    print("NIFTY 50 LONG-HISTORY MOVING-AVERAGE BACKTEST")
    print("=" * 74)

    print(
        f"Period                  : "
        f"{backtest.index.min().date()} to "
        f"{backtest.index.max().date()}"
    )

    print(
        f"Trading-day records     : "
        f"{len(backtest):,}"
    )

    print(
        f"Completed trades        : "
        f"{completed_trades}"
    )

    print(
        f"Market exposure         : "
        f"{market_exposure:.2%}"
    )

    print(
        f"Cumulative cost drag    : "
        f"{total_cost:.2%}"
    )

    print("-" * 74)

    print(
        f"{'Metric':<28}"
        f"{'Buy & Hold':>20}"
        f"{'MA Strategy':>20}"
    )

    print(
        f"{'CAGR':<28}"
        f"{buy_hold_cagr:>19.2%}"
        f"{strategy_cagr:>20.2%}"
    )

    print(
        f"{'Annualized volatility':<28}"
        f"{buy_hold_volatility:>19.2%}"
        f"{strategy_volatility:>20.2%}"
    )

    print(
        f"{'Sharpe ratio':<28}"
        f"{buy_hold_sharpe:>19.2f}"
        f"{strategy_sharpe:>20.2f}"
    )

    print(
        f"{'Maximum drawdown':<28}"
        f"{buy_hold_drawdown:>19.2%}"
        f"{strategy_drawdown:>20.2%}"
    )

    print("-" * 74)

    print("Saved:")
    print("- results/ma_long_history_backtest.csv")
    print("- results/ma_long_history_growth.png")

    print("=" * 74)


if __name__ == "__main__":
    main()