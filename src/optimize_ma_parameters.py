from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------------------------------------------------
# PROJECT CONFIGURATION
# ---------------------------------------------------------

DATA_PATH = Path("data/nifty50_history.csv")
RESULTS_PATH = Path("results")

FAST_WINDOWS = [5, 10, 15, 20, 30, 40, 50]
SLOW_WINDOWS = [20, 30, 50, 100, 150, 200]

TRANSACTION_COST = 0.0005
TRADING_DAYS_PER_YEAR = 252


# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------

def load_close_prices(file_path: Path) -> pd.Series:
    """
    Load NIFTY 50 closing prices from the saved yfinance CSV.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}\n"
            "Run src/download_nifty_history.py first."
        )

    data = pd.read_csv(
        file_path,
        header=[0, 1],
        index_col=0,
        parse_dates=True,
    )

    expected_column = ("Close", "^NSEI")

    if expected_column not in data.columns:
        raise KeyError(
            f"Expected column {expected_column} was not found.\n"
            f"Available columns: {list(data.columns)}"
        )

    close_prices = data[expected_column].copy()
    close_prices.name = "Close"

    return close_prices.dropna().sort_index()


# ---------------------------------------------------------
# PERFORMANCE METRICS
# ---------------------------------------------------------

def calculate_cagr(growth: pd.Series) -> float:
    """
    Calculate compound annual growth rate.
    """

    growth = growth.dropna()

    if len(growth) < 2:
        return float("nan")

    years = (
        growth.index[-1] - growth.index[0]
    ).days / 365.25

    if years <= 0 or growth.iloc[0] <= 0:
        return float("nan")

    return (
        growth.iloc[-1] / growth.iloc[0]
    ) ** (1 / years) - 1


def calculate_annualized_volatility(
    returns: pd.Series,
) -> float:
    """
    Calculate annualized volatility from daily returns.
    """

    clean_returns = returns.dropna()

    if clean_returns.empty:
        return float("nan")

    return (
        clean_returns.std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_sharpe_ratio(
    returns: pd.Series,
) -> float:
    """
    Calculate annualized Sharpe ratio.

    A zero risk-free rate is assumed for this educational
    research project.
    """

    clean_returns = returns.dropna()

    if clean_returns.empty:
        return float("nan")

    daily_volatility = clean_returns.std()

    if daily_volatility == 0 or np.isnan(daily_volatility):
        return float("nan")

    return (
        clean_returns.mean()
        / daily_volatility
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_max_drawdown(
    growth: pd.Series,
) -> float:
    """
    Calculate the worst peak-to-trough decline.
    """

    running_peak = growth.cummax()
    drawdown = growth / running_peak - 1

    return drawdown.min()


# ---------------------------------------------------------
# SINGLE STRATEGY BACKTEST
# ---------------------------------------------------------

def run_backtest(
    close_prices: pd.Series,
    fast_window: int,
    slow_window: int,
) -> dict:
    """
    Backtest one moving-average crossover configuration.

    Strategy:
    - Long NIFTY when the fast MA is above the slow MA.
    - Stay in cash otherwise.
    """

    backtest = pd.DataFrame(index=close_prices.index)

    backtest["Close"] = close_prices

    backtest["Market Return"] = (
        backtest["Close"]
        .pct_change()
        .fillna(0)
    )

    backtest["Fast MA"] = (
        backtest["Close"]
        .rolling(window=fast_window)
        .mean()
    )

    backtest["Slow MA"] = (
        backtest["Close"]
        .rolling(window=slow_window)
        .mean()
    )

    backtest["Signal"] = np.where(
        backtest["Fast MA"] > backtest["Slow MA"],
        1,
        0,
    )

    # Shift by one day to prevent look-ahead bias.
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

    backtest["Strategy Growth"] = (
        1 + backtest["Strategy Return"]
    ).cumprod()

    position_changes = int(
        backtest["Position Change"].sum()
    )

    completed_trades = position_changes // 2

    return {
        "Fast MA": fast_window,
        "Slow MA": slow_window,
        "CAGR": calculate_cagr(
            backtest["Strategy Growth"]
        ),
        "Annualized Volatility":
            calculate_annualized_volatility(
                backtest["Strategy Return"]
            ),
        "Sharpe Ratio": calculate_sharpe_ratio(
            backtest["Strategy Return"]
        ),
        "Maximum Drawdown": calculate_max_drawdown(
            backtest["Strategy Growth"]
        ),
        "Completed Trades": completed_trades,
        "Position Changes": position_changes,
        "Market Exposure": (
            backtest["Position"].mean()
        ),
        "Cumulative Cost Drag": (
            backtest["Trading Cost"].sum()
        ),
        "Final Portfolio Value": (
            backtest["Strategy Growth"].iloc[-1]
        ),
    }


# ---------------------------------------------------------
# PARAMETER OPTIMIZATION
# ---------------------------------------------------------

def optimize_parameters(
    close_prices: pd.Series,
) -> pd.DataFrame:
    """
    Test every valid fast/slow moving-average combination.
    """

    results = []

    total_combinations = sum(
        1
        for fast_window in FAST_WINDOWS
        for slow_window in SLOW_WINDOWS
        if fast_window < slow_window
    )

    completed = 0

    print("=" * 72)
    print("MOVING-AVERAGE PARAMETER OPTIMIZATION")
    print("=" * 72)

    print(
        f"Valid parameter combinations: "
        f"{total_combinations}"
    )

    for fast_window in FAST_WINDOWS:
        for slow_window in SLOW_WINDOWS:

            if fast_window >= slow_window:
                continue

            completed += 1

            print(
                f"Testing {completed:>2}/{total_combinations}: "
                f"MA {fast_window}/{slow_window}"
            )

            result = run_backtest(
                close_prices=close_prices,
                fast_window=fast_window,
                slow_window=slow_window,
            )

            results.append(result)

    results_df = pd.DataFrame(results)

    return results_df


# ---------------------------------------------------------
# HEATMAP CREATION
# ---------------------------------------------------------

def save_heatmap(
    results: pd.DataFrame,
    metric: str,
    file_name: str,
    title: str,
    percentage_format: bool = False,
) -> None:
    """
    Create and save a moving-average parameter heatmap.
    """

    pivot_table = results.pivot(
        index="Fast MA",
        columns="Slow MA",
        values=metric,
    )

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    image = axis.imshow(
        pivot_table.values,
        aspect="auto",
    )

    axis.set_xticks(
        range(len(pivot_table.columns))
    )

    axis.set_xticklabels(
        pivot_table.columns
    )

    axis.set_yticks(
        range(len(pivot_table.index))
    )

    axis.set_yticklabels(
        pivot_table.index
    )

    axis.set_xlabel("Slow Moving Average")
    axis.set_ylabel("Fast Moving Average")
    axis.set_title(title)

    figure.colorbar(
        image,
        ax=axis,
        label=metric,
    )

    # Write metric values inside each cell.
    for row_index in range(
        len(pivot_table.index)
    ):
        for column_index in range(
            len(pivot_table.columns)
        ):
            value = pivot_table.iloc[
                row_index,
                column_index,
            ]

            if pd.isna(value):
                display_value = ""
            elif percentage_format:
                display_value = f"{value:.1%}"
            else:
                display_value = f"{value:.2f}"

            axis.text(
                column_index,
                row_index,
                display_value,
                ha="center",
                va="center",
                fontsize=8,
            )

    figure.tight_layout()

    figure.savefig(
        RESULTS_PATH / file_name,
        dpi=150,
    )

    plt.close(figure)


# ---------------------------------------------------------
# RESULT REPORTING
# ---------------------------------------------------------

def print_rankings(
    results: pd.DataFrame,
) -> None:
    """
    Display the leading parameter combinations.
    """

    columns_to_show = [
        "Fast MA",
        "Slow MA",
        "CAGR",
        "Sharpe Ratio",
        "Maximum Drawdown",
        "Annualized Volatility",
        "Completed Trades",
        "Market Exposure",
    ]

    print("\n" + "=" * 72)
    print("TOP FIVE CONFIGURATIONS BY SHARPE RATIO")
    print("=" * 72)

    top_sharpe = (
        results
        .sort_values(
            by="Sharpe Ratio",
            ascending=False,
        )
        .head(5)
    )

    print(
        top_sharpe[
            columns_to_show
        ].to_string(
            index=False,
            formatters={
                "CAGR": "{:.2%}".format,
                "Sharpe Ratio": "{:.2f}".format,
                "Maximum Drawdown": "{:.2%}".format,
                "Annualized Volatility":
                    "{:.2%}".format,
                "Market Exposure": "{:.2%}".format,
            },
        )
    )

    print("\n" + "=" * 72)
    print("TOP FIVE CONFIGURATIONS BY CAGR")
    print("=" * 72)

    top_cagr = (
        results
        .sort_values(
            by="CAGR",
            ascending=False,
        )
        .head(5)
    )

    print(
        top_cagr[
            columns_to_show
        ].to_string(
            index=False,
            formatters={
                "CAGR": "{:.2%}".format,
                "Sharpe Ratio": "{:.2f}".format,
                "Maximum Drawdown": "{:.2%}".format,
                "Annualized Volatility":
                    "{:.2%}".format,
                "Market Exposure": "{:.2%}".format,
            },
        )
    )

    print("\n" + "=" * 72)
    print("TOP FIVE CONFIGURATIONS BY LOWEST DRAWDOWN")
    print("=" * 72)

    # A drawdown closer to zero is better.
    lowest_drawdown = (
        results
        .sort_values(
            by="Maximum Drawdown",
            ascending=False,
        )
        .head(5)
    )

    print(
        lowest_drawdown[
            columns_to_show
        ].to_string(
            index=False,
            formatters={
                "CAGR": "{:.2%}".format,
                "Sharpe Ratio": "{:.2f}".format,
                "Maximum Drawdown": "{:.2%}".format,
                "Annualized Volatility":
                    "{:.2%}".format,
                "Market Exposure": "{:.2%}".format,
            },
        )
    )


# ---------------------------------------------------------
# MAIN WORKFLOW
# ---------------------------------------------------------

def main() -> None:
    """
    Run the complete parameter-optimization workflow.
    """

    RESULTS_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    close_prices = load_close_prices(
        DATA_PATH
    )

    results = optimize_parameters(
        close_prices
    )

    results = results.sort_values(
        by="Sharpe Ratio",
        ascending=False,
    ).reset_index(drop=True)

    output_csv = (
        RESULTS_PATH
        / "ma_parameter_optimization.csv"
    )

    results.to_csv(
        output_csv,
        index=False,
    )

    save_heatmap(
        results=results,
        metric="Sharpe Ratio",
        file_name="ma_sharpe_heatmap.png",
        title=(
            "NIFTY 50 Moving-Average "
            "Sharpe Ratio Heatmap"
        ),
    )

    save_heatmap(
        results=results,
        metric="CAGR",
        file_name="ma_cagr_heatmap.png",
        title=(
            "NIFTY 50 Moving-Average "
            "CAGR Heatmap"
        ),
        percentage_format=True,
    )

    save_heatmap(
        results=results,
        metric="Maximum Drawdown",
        file_name="ma_drawdown_heatmap.png",
        title=(
            "NIFTY 50 Moving-Average "
            "Maximum Drawdown Heatmap"
        ),
        percentage_format=True,
    )

    print_rankings(results)

    print("\n" + "=" * 72)
    print("OPTIMIZATION COMPLETED")
    print("=" * 72)

    print(
        f"Strategies tested : {len(results)}"
    )

    print("Files saved:")
    print(
        "- results/"
        "ma_parameter_optimization.csv"
    )
    print(
        "- results/"
        "ma_sharpe_heatmap.png"
    )
    print(
        "- results/"
        "ma_cagr_heatmap.png"
    )
    print(
        "- results/"
        "ma_drawdown_heatmap.png"
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
