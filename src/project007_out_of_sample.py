from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

DATA_PATH = Path("data/nifty50_history.csv")
RESULTS_PATH = Path("results")

TRAIN_END_DATE = "2020-12-31"
TEST_START_DATE = "2021-01-01"

FAST_WINDOWS = [5, 10, 15, 20, 30, 40, 50]
SLOW_WINDOWS = [20, 30, 50, 100, 150, 200]

TRANSACTION_COST = 0.0005
TRADING_DAYS_PER_YEAR = 252


# =========================================================
# DATA LOADING
# =========================================================

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


# =========================================================
# PERFORMANCE METRICS
# =========================================================

def calculate_cagr(growth: pd.Series) -> float:
    """
    Calculate compound annual growth rate.
    """

    clean_growth = growth.dropna()

    if len(clean_growth) < 2:
        return float("nan")

    years = (
        clean_growth.index[-1] - clean_growth.index[0]
    ).days / 365.25

    if years <= 0 or clean_growth.iloc[0] <= 0:
        return float("nan")

    return (
        clean_growth.iloc[-1] / clean_growth.iloc[0]
    ) ** (1 / years) - 1


def calculate_annualized_volatility(
    returns: pd.Series,
) -> float:
    """
    Calculate annualized volatility.
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

    A zero risk-free rate is assumed.
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

    clean_growth = growth.dropna()

    running_peak = clean_growth.cummax()
    drawdown = clean_growth / running_peak - 1

    return drawdown.min()


# =========================================================
# BACKTEST ENGINE
# =========================================================

def create_backtest(
    close_prices: pd.Series,
    fast_window: int,
    slow_window: int,
) -> pd.DataFrame:
    """
    Create a long/cash moving-average strategy.

    The position is shifted by one day to prevent
    look-ahead bias.
    """

    backtest = pd.DataFrame(index=close_prices.index)

    backtest["Close"] = close_prices

    backtest["Daily Return"] = (
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

    # Use today's completed signal from the next day onward.
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
        * backtest["Daily Return"]
        - backtest["Trading Cost"]
    )

    backtest["Strategy Growth"] = (
        1 + backtest["Strategy Return"]
    ).cumprod()

    backtest["Buy Hold Growth"] = (
        1 + backtest["Daily Return"]
    ).cumprod()

    return backtest


def calculate_metrics(
    backtest: pd.DataFrame,
) -> dict:
    """
    Calculate strategy-performance metrics.
    """

    position_changes = int(
        backtest["Position Change"].sum()
    )

    return {
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
        "Completed Trades": position_changes // 2,
        "Position Changes": position_changes,
        "Market Exposure": backtest["Position"].mean(),
        "Cumulative Cost Drag":
            backtest["Trading Cost"].sum(),
        "Final Portfolio Value":
            backtest["Strategy Growth"].iloc[-1],
    }


# =========================================================
# TRAINING OPTIMIZATION
# =========================================================

def optimize_on_training_data(
    training_prices: pd.Series,
) -> pd.DataFrame:
    """
    Test valid MA combinations using training data only.
    """

    optimization_results = []

    valid_combinations = [
        (fast_window, slow_window)
        for fast_window in FAST_WINDOWS
        for slow_window in SLOW_WINDOWS
        if fast_window < slow_window
    ]

    print("=" * 74)
    print("TRAINING-PERIOD PARAMETER OPTIMIZATION")
    print("=" * 74)

    for number, (
        fast_window,
        slow_window,
    ) in enumerate(
        valid_combinations,
        start=1,
    ):
        print(
            f"Testing {number:>2}/{len(valid_combinations)}: "
            f"MA {fast_window}/{slow_window}"
        )

        backtest = create_backtest(
            close_prices=training_prices,
            fast_window=fast_window,
            slow_window=slow_window,
        )

        metrics = calculate_metrics(backtest)

        optimization_results.append(
            {
                "Fast MA": fast_window,
                "Slow MA": slow_window,
                **metrics,
            }
        )

    results = pd.DataFrame(
        optimization_results
    )

    results = results.sort_values(
        by=[
            "Sharpe Ratio",
            "CAGR",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)

    return results


# =========================================================
# PERIOD-SPECIFIC BACKTESTS
# =========================================================

def build_training_backtest(
    full_prices: pd.Series,
    fast_window: int,
    slow_window: int,
) -> pd.DataFrame:
    """
    Backtest only the training period.
    """

    training_prices = full_prices.loc[
        :TRAIN_END_DATE
    ]

    return create_backtest(
        close_prices=training_prices,
        fast_window=fast_window,
        slow_window=slow_window,
    )


def build_test_backtest(
    full_prices: pd.Series,
    fast_window: int,
    slow_window: int,
) -> pd.DataFrame:
    """
    Build the out-of-sample backtest.

    Earlier prices are retained temporarily so the moving
    averages are already formed at the beginning of the test
    period. Metrics are calculated only from TEST_START_DATE.
    """

    # Include warm-up data before 2021 so the slow moving
    # average is available on the first test-period dates.
    warmup_start_position = max(
        0,
        full_prices.index.searchsorted(
            pd.Timestamp(TEST_START_DATE)
        ) - slow_window - 5,
    )

    prices_with_warmup = full_prices.iloc[
        warmup_start_position:
    ]

    complete_backtest = create_backtest(
        close_prices=prices_with_warmup,
        fast_window=fast_window,
        slow_window=slow_window,
    )

    test_backtest = complete_backtest.loc[
        TEST_START_DATE:
    ].copy()

    # Reset growth curves to ₹1 at the start of the
    # out-of-sample period.
    test_backtest["Strategy Growth"] = (
        1 + test_backtest["Strategy Return"]
    ).cumprod()

    test_backtest["Buy Hold Growth"] = (
        1 + test_backtest["Daily Return"]
    ).cumprod()

    return test_backtest


# =========================================================
# CHARTS
# =========================================================

def save_equity_chart(
    backtest: pd.DataFrame,
    title: str,
    file_name: str,
) -> None:
    """
    Save strategy and buy-and-hold equity curves.
    """

    plt.figure(figsize=(12, 6))

    plt.plot(
        backtest.index,
        backtest["Strategy Growth"],
        label="MA Strategy",
    )

    plt.plot(
        backtest.index,
        backtest["Buy Hold Growth"],
        label="Buy and Hold",
    )

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Growth of ₹1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / file_name,
        dpi=150,
    )

    plt.close()


def save_train_test_comparison(
    training_backtest: pd.DataFrame,
    test_backtest: pd.DataFrame,
) -> None:
    """
    Compare normalized strategy growth by elapsed trading day.
    """

    training_growth = (
        training_backtest["Strategy Growth"]
        / training_backtest[
            "Strategy Growth"
        ].iloc[0]
    ).reset_index(drop=True)

    test_growth = (
        test_backtest["Strategy Growth"]
        / test_backtest[
            "Strategy Growth"
        ].iloc[0]
    ).reset_index(drop=True)

    plt.figure(figsize=(12, 6))

    plt.plot(
        training_growth.index,
        training_growth,
        label="Training Strategy Growth",
    )

    plt.plot(
        test_growth.index,
        test_growth,
        label="Test Strategy Growth",
    )

    plt.title(
        "Moving-Average Strategy: "
        "Training vs Out-of-Sample Growth"
    )

    plt.xlabel("Elapsed Trading Days")
    plt.ylabel("Growth of ₹1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH / "project007_train_vs_test.png",
        dpi=150,
    )

    plt.close()


# =========================================================
# REPORTING
# =========================================================

def print_metric_row(
    metric_name: str,
    training_value: float,
    testing_value: float,
    display_type: str,
) -> None:
    """
    Print one comparison-table row.
    """

    if display_type == "percentage":
        training_text = f"{training_value:.2%}"
        testing_text = f"{testing_value:.2%}"
        difference_text = (
            f"{testing_value - training_value:.2%}"
        )

    elif display_type == "decimal":
        training_text = f"{training_value:.2f}"
        testing_text = f"{testing_value:.2f}"
        difference_text = (
            f"{testing_value - training_value:.2f}"
        )

    elif display_type == "integer":
        training_text = f"{int(training_value)}"
        testing_text = f"{int(testing_value)}"
        difference_text = (
            f"{int(testing_value - training_value)}"
        )

    else:
        raise ValueError(
            f"Unknown display type: {display_type}"
        )

    print(
        f"{metric_name:<27}"
        f"{training_text:>16}"
        f"{testing_text:>16}"
        f"{difference_text:>16}"
    )


# =========================================================
# MAIN WORKFLOW
# =========================================================

def main() -> None:
    """
    Run training optimization and out-of-sample validation.
    """

    RESULTS_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    close_prices = load_close_prices(
        DATA_PATH
    )

    training_prices = close_prices.loc[
        :TRAIN_END_DATE
    ]

    testing_prices = close_prices.loc[
        TEST_START_DATE:
    ]

    if training_prices.empty:
        raise RuntimeError(
            "Training-period data is empty."
        )

    if testing_prices.empty:
        raise RuntimeError(
            "Testing-period data is empty."
        )

    optimization_results = (
        optimize_on_training_data(
            training_prices
        )
    )

    best_training_result = (
        optimization_results.iloc[0]
    )

    selected_fast_window = int(
        best_training_result["Fast MA"]
    )

    selected_slow_window = int(
        best_training_result["Slow MA"]
    )

    # Freeze the selected parameters before testing.
    training_backtest = build_training_backtest(
        full_prices=close_prices,
        fast_window=selected_fast_window,
        slow_window=selected_slow_window,
    )

    test_backtest = build_test_backtest(
        full_prices=close_prices,
        fast_window=selected_fast_window,
        slow_window=selected_slow_window,
    )

    training_metrics = calculate_metrics(
        training_backtest
    )

    testing_metrics = calculate_metrics(
        test_backtest
    )

    optimization_results.to_csv(
        RESULTS_PATH
        / "project007_training_optimization.csv",
        index=False,
    )

    training_backtest.to_csv(
        RESULTS_PATH
        / "project007_train_backtest.csv"
    )

    test_backtest.to_csv(
        RESULTS_PATH
        / "project007_test_backtest.csv"
    )

    save_equity_chart(
        backtest=training_backtest,
        title=(
            "Project 007: Training-Period "
            "Strategy Performance"
        ),
        file_name="project007_train_equity.png",
    )

    save_equity_chart(
        backtest=test_backtest,
        title=(
            "Project 007: Out-of-Sample "
            "Strategy Performance"
        ),
        file_name="project007_test_equity.png",
    )

    save_train_test_comparison(
        training_backtest=training_backtest,
        test_backtest=test_backtest,
    )

    print("\n" + "=" * 78)
    print("PROJECT 007 — OUT-OF-SAMPLE VALIDATION")
    print("=" * 78)

    print(
        f"Training period          : "
        f"{training_backtest.index.min().date()} to "
        f"{training_backtest.index.max().date()}"
    )

    print(
        f"Testing period           : "
        f"{test_backtest.index.min().date()} to "
        f"{test_backtest.index.max().date()}"
    )

    print(
        f"Selected fast MA         : "
        f"{selected_fast_window}"
    )

    print(
        f"Selected slow MA         : "
        f"{selected_slow_window}"
    )

    print(
        "Selection criterion      : "
        "Highest training-period Sharpe ratio"
    )

    print("-" * 78)

    print(
        f"{'Metric':<27}"
        f"{'Training':>16}"
        f"{'Testing':>16}"
        f"{'Difference':>16}"
    )

    print_metric_row(
        "CAGR",
        training_metrics["CAGR"],
        testing_metrics["CAGR"],
        "percentage",
    )

    print_metric_row(
        "Annualized volatility",
        training_metrics[
            "Annualized Volatility"
        ],
        testing_metrics[
            "Annualized Volatility"
        ],
        "percentage",
    )

    print_metric_row(
        "Sharpe ratio",
        training_metrics["Sharpe Ratio"],
        testing_metrics["Sharpe Ratio"],
        "decimal",
    )

    print_metric_row(
        "Maximum drawdown",
        training_metrics[
            "Maximum Drawdown"
        ],
        testing_metrics[
            "Maximum Drawdown"
        ],
        "percentage",
    )

    print_metric_row(
        "Completed trades",
        training_metrics[
            "Completed Trades"
        ],
        testing_metrics[
            "Completed Trades"
        ],
        "integer",
    )

    print_metric_row(
        "Market exposure",
        training_metrics[
            "Market Exposure"
        ],
        testing_metrics[
            "Market Exposure"
        ],
        "percentage",
    )

    print("-" * 78)

    print("Files saved:")
    print(
        "- results/"
        "project007_training_optimization.csv"
    )
    print(
        "- results/"
        "project007_train_backtest.csv"
    )
    print(
        "- results/"
        "project007_test_backtest.csv"
    )
    print(
        "- results/"
        "project007_train_equity.png"
    )
    print(
        "- results/"
        "project007_test_equity.png"
    )
    print(
        "- results/"
        "project007_train_vs_test.png"
    )

    print("=" * 78)


if __name__ == "__main__":
    main()