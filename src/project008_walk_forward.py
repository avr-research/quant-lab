from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

DATA_PATH = Path("data/nifty50_history.csv")
RESULTS_PATH = Path("results")

FAST_WINDOWS = [5, 10, 15, 20, 30, 40, 50]
SLOW_WINDOWS = [20, 30, 50, 100, 150, 200]

TRAINING_YEARS = 5
TRANSACTION_COST = 0.0005
TRADING_DAYS_PER_YEAR = 252


# =========================================================
# DATA LOADING
# =========================================================

def load_close_prices(file_path: Path) -> pd.Series:
    """Load adjusted NIFTY 50 closing prices."""

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

    expected_column = ("Close", "^NSEI")

    if expected_column not in data.columns:
        raise KeyError(
            f"Expected column {expected_column} was not found."
        )

    close = data[expected_column].copy()
    close.name = "Close"

    return close.dropna().sort_index()


# =========================================================
# PERFORMANCE METRICS
# =========================================================

def calculate_cagr(growth: pd.Series) -> float:
    """Calculate annualized compounded return."""

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


def calculate_volatility(returns: pd.Series) -> float:
    """Calculate annualized volatility."""

    clean_returns = returns.dropna()

    if clean_returns.empty:
        return float("nan")

    return (
        clean_returns.std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_sharpe(returns: pd.Series) -> float:
    """Calculate annualized Sharpe ratio with zero risk-free rate."""

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


def calculate_max_drawdown(growth: pd.Series) -> float:
    """Calculate worst peak-to-trough portfolio decline."""

    running_peak = growth.cummax()
    drawdown = growth / running_peak - 1

    return drawdown.min()


# =========================================================
# BACKTEST ENGINE
# =========================================================

def create_backtest(
    close_prices: pd.Series,
    fast_window: int,
    slow_window: int,
) -> pd.DataFrame:
    """Create a long/cash moving-average strategy."""

    backtest = pd.DataFrame(index=close_prices.index)

    backtest["Close"] = close_prices

    backtest["Market Return"] = (
        backtest["Close"]
        .pct_change()
        .fillna(0)
    )

    backtest["Fast MA"] = (
        backtest["Close"]
        .rolling(fast_window)
        .mean()
    )

    backtest["Slow MA"] = (
        backtest["Close"]
        .rolling(slow_window)
        .mean()
    )

    backtest["Signal"] = np.where(
        backtest["Fast MA"] > backtest["Slow MA"],
        1,
        0,
    )

    # Prevent look-ahead bias.
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

    return backtest


def calculate_metrics(backtest: pd.DataFrame) -> dict:
    """Calculate backtest statistics."""

    position_changes = int(
        backtest["Position Change"].sum()
    )

    return {
        "CAGR": calculate_cagr(
            backtest["Strategy Growth"]
        ),
        "Annualized Volatility": calculate_volatility(
            backtest["Strategy Return"]
        ),
        "Sharpe Ratio": calculate_sharpe(
            backtest["Strategy Return"]
        ),
        "Maximum Drawdown": calculate_max_drawdown(
            backtest["Strategy Growth"]
        ),
        "Completed Trades": position_changes // 2,
        "Market Exposure": backtest["Position"].mean(),
        "Cost Drag": backtest["Trading Cost"].sum(),
        "Final Value": backtest[
            "Strategy Growth"
        ].iloc[-1],
    }


# =========================================================
# TRAINING OPTIMIZATION
# =========================================================

def optimize_training_window(
    training_prices: pd.Series,
) -> pd.DataFrame:
    """Select parameters using one training window only."""

    results = []

    for fast_window in FAST_WINDOWS:
        for slow_window in SLOW_WINDOWS:

            if fast_window >= slow_window:
                continue

            backtest = create_backtest(
                close_prices=training_prices,
                fast_window=fast_window,
                slow_window=slow_window,
            )

            metrics = calculate_metrics(backtest)

            results.append(
                {
                    "Fast MA": fast_window,
                    "Slow MA": slow_window,
                    **metrics,
                }
            )

    results_df = pd.DataFrame(results)

    return (
        results_df
        .sort_values(
            by=["Sharpe Ratio", "CAGR"],
            ascending=[False, False],
        )
        .reset_index(drop=True)
    )


# =========================================================
# TEST-WINDOW CREATION
# =========================================================

def create_test_backtest(
    full_prices: pd.Series,
    test_year: int,
    fast_window: int,
    slow_window: int,
) -> pd.DataFrame:
    """
    Apply frozen parameters to one unseen calendar year.

    Historical warm-up data is retained so moving averages
    are available at the beginning of the test year.
    """

    test_start = pd.Timestamp(f"{test_year}-01-01")
    test_end = pd.Timestamp(f"{test_year}-12-31")

    test_start_position = full_prices.index.searchsorted(
        test_start
    )

    warmup_start_position = max(
        0,
        test_start_position - slow_window - 10,
    )

    prices_with_warmup = full_prices.iloc[
        warmup_start_position:
    ].loc[:test_end]

    complete_backtest = create_backtest(
        close_prices=prices_with_warmup,
        fast_window=fast_window,
        slow_window=slow_window,
    )

    test_backtest = complete_backtest.loc[
        test_start:test_end
    ].copy()

    if test_backtest.empty:
        return test_backtest

    test_backtest["Strategy Growth"] = (
        1 + test_backtest["Strategy Return"]
    ).cumprod()

    return test_backtest


# =========================================================
# WALK-FORWARD PROCESS
# =========================================================

def run_walk_forward(
    close_prices: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run all rolling train/test cycles."""

    first_year = close_prices.index.min().year
    final_year = close_prices.index.max().year

    first_test_year = first_year + TRAINING_YEARS

    window_results = []
    out_of_sample_frames = []

    print("=" * 80)
    print("PROJECT 008 — WALK-FORWARD VALIDATION")
    print("=" * 80)

    for test_year in range(
        first_test_year,
        final_year + 1,
    ):
        training_start_year = (
            test_year - TRAINING_YEARS
        )

        training_start = pd.Timestamp(
            f"{training_start_year}-01-01"
        )

        training_end = pd.Timestamp(
            f"{test_year - 1}-12-31"
        )

        training_prices = close_prices.loc[
            training_start:training_end
        ]

        # Skip windows without sufficient training history.
        if len(training_prices) < 500:
            continue

        optimization = optimize_training_window(
            training_prices
        )

        best_result = optimization.iloc[0]

        selected_fast = int(
            best_result["Fast MA"]
        )

        selected_slow = int(
            best_result["Slow MA"]
        )

        test_backtest = create_test_backtest(
            full_prices=close_prices,
            test_year=test_year,
            fast_window=selected_fast,
            slow_window=selected_slow,
        )

        if test_backtest.empty:
            continue

        test_metrics = calculate_metrics(
            test_backtest
        )

        window_results.append(
            {
                "Training Start": training_start.date(),
                "Training End": training_end.date(),
                "Test Year": test_year,
                "Selected Fast MA": selected_fast,
                "Selected Slow MA": selected_slow,
                "Training Sharpe": best_result[
                    "Sharpe Ratio"
                ],
                "Test CAGR": test_metrics["CAGR"],
                "Test Volatility": test_metrics[
                    "Annualized Volatility"
                ],
                "Test Sharpe": test_metrics[
                    "Sharpe Ratio"
                ],
                "Test Maximum Drawdown": test_metrics[
                    "Maximum Drawdown"
                ],
                "Test Trades": test_metrics[
                    "Completed Trades"
                ],
                "Test Exposure": test_metrics[
                    "Market Exposure"
                ],
                "Test Cost Drag": test_metrics[
                    "Cost Drag"
                ],
            }
        )

        test_output = test_backtest.copy()

        test_output["Test Year"] = test_year
        test_output["Selected Fast MA"] = selected_fast
        test_output["Selected Slow MA"] = selected_slow

        out_of_sample_frames.append(
            test_output
        )

        print(
            f"Train {training_start_year}–{test_year - 1} "
            f"| Test {test_year} "
            f"| Selected MA {selected_fast}/{selected_slow} "
            f"| Sharpe {test_metrics['Sharpe Ratio']:.2f}"
        )

    metrics_df = pd.DataFrame(
        window_results
    )

    if not out_of_sample_frames:
        raise RuntimeError(
            "No out-of-sample windows were created."
        )

    combined_oos = pd.concat(
        out_of_sample_frames
    ).sort_index()

    # Remove any accidental duplicated dates.
    combined_oos = combined_oos[
        ~combined_oos.index.duplicated(
            keep="first"
        )
    ]

    combined_oos["Combined OOS Growth"] = (
        1 + combined_oos["Strategy Return"]
    ).cumprod()

    return metrics_df, combined_oos


# =========================================================
# VISUALIZATIONS
# =========================================================

def save_combined_equity_chart(
    combined_oos: pd.DataFrame,
) -> None:
    """Save continuous out-of-sample equity curve."""

    plt.figure(figsize=(13, 6))

    plt.plot(
        combined_oos.index,
        combined_oos["Combined OOS Growth"],
        label="Combined Out-of-Sample Strategy",
    )

    plt.title(
        "Project 008: Continuous Walk-Forward "
        "Out-of-Sample Equity"
    )
    plt.xlabel("Date")
    plt.ylabel("Growth of ₹1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project008_walk_forward_equity.png",
        dpi=150,
    )

    plt.close()


def save_parameter_chart(
    metrics: pd.DataFrame,
) -> None:
    """Show selected parameters over time."""

    plt.figure(figsize=(12, 6))

    plt.plot(
        metrics["Test Year"],
        metrics["Selected Fast MA"],
        marker="o",
        label="Selected Fast MA",
    )

    plt.plot(
        metrics["Test Year"],
        metrics["Selected Slow MA"],
        marker="o",
        label="Selected Slow MA",
    )

    plt.title(
        "Project 008: Walk-Forward Parameter Evolution"
    )
    plt.xlabel("Out-of-Sample Test Year")
    plt.ylabel("Moving-Average Window")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project008_parameter_evolution.png",
        dpi=150,
    )

    plt.close()


def save_yearly_sharpe_chart(
    metrics: pd.DataFrame,
) -> None:
    """Save out-of-sample Sharpe ratio by test year."""

    plt.figure(figsize=(12, 6))

    plt.bar(
        metrics["Test Year"].astype(str),
        metrics["Test Sharpe"],
    )

    plt.axhline(
        0,
        linewidth=1,
    )

    plt.title(
        "Project 008: Out-of-Sample Sharpe by Year"
    )
    plt.xlabel("Test Year")
    plt.ylabel("Sharpe Ratio")
    plt.xticks(rotation=45)
    plt.grid(axis="y")
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project008_yearly_sharpe.png",
        dpi=150,
    )

    plt.close()


# =========================================================
# SUMMARY
# =========================================================

def print_summary(
    metrics: pd.DataFrame,
    combined_oos: pd.DataFrame,
) -> None:
    """Print walk-forward research summary."""

    combined_cagr = calculate_cagr(
        combined_oos["Combined OOS Growth"]
    )

    combined_volatility = calculate_volatility(
        combined_oos["Strategy Return"]
    )

    combined_sharpe = calculate_sharpe(
        combined_oos["Strategy Return"]
    )

    combined_drawdown = calculate_max_drawdown(
        combined_oos["Combined OOS Growth"]
    )

    best_window = metrics.loc[
        metrics["Test Sharpe"].idxmax()
    ]

    worst_window = metrics.loc[
        metrics["Test Sharpe"].idxmin()
    ]

    positive_sharpe_percentage = (
        metrics["Test Sharpe"] > 0
    ).mean()

    print("\n" + "=" * 80)
    print("WALK-FORWARD SUMMARY")
    print("=" * 80)

    print(
        f"Windows tested             : "
        f"{len(metrics)}"
    )

    print(
        f"Combined OOS CAGR          : "
        f"{combined_cagr:.2%}"
    )

    print(
        f"Combined OOS volatility    : "
        f"{combined_volatility:.2%}"
    )

    print(
        f"Combined OOS Sharpe        : "
        f"{combined_sharpe:.2f}"
    )

    print(
        f"Combined OOS max drawdown  : "
        f"{combined_drawdown:.2%}"
    )

    print(
        f"Average yearly Sharpe      : "
        f"{metrics['Test Sharpe'].mean():.2f}"
    )

    print(
        f"Median yearly Sharpe       : "
        f"{metrics['Test Sharpe'].median():.2f}"
    )

    print(
        f"Positive-Sharpe windows    : "
        f"{positive_sharpe_percentage:.2%}"
    )

    print(
        f"Average selected fast MA   : "
        f"{metrics['Selected Fast MA'].mean():.1f}"
    )

    print(
        f"Average selected slow MA   : "
        f"{metrics['Selected Slow MA'].mean():.1f}"
    )

    print("-" * 80)

    print(
        f"Best test year             : "
        f"{int(best_window['Test Year'])}"
    )

    print(
        f"Best-year parameters       : "
        f"MA "
        f"{int(best_window['Selected Fast MA'])}/"
        f"{int(best_window['Selected Slow MA'])}"
    )

    print(
        f"Best yearly Sharpe         : "
        f"{best_window['Test Sharpe']:.2f}"
    )

    print(
        f"Worst test year            : "
        f"{int(worst_window['Test Year'])}"
    )

    print(
        f"Worst-year parameters      : "
        f"MA "
        f"{int(worst_window['Selected Fast MA'])}/"
        f"{int(worst_window['Selected Slow MA'])}"
    )

    print(
        f"Worst yearly Sharpe        : "
        f"{worst_window['Test Sharpe']:.2f}"
    )

    print("=" * 80)


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    """Run Project 008."""

    RESULTS_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    close_prices = load_close_prices(
        DATA_PATH
    )

    metrics, combined_oos = run_walk_forward(
        close_prices
    )

    metrics.to_csv(
        RESULTS_PATH
        / "project008_walk_forward_metrics.csv",
        index=False,
    )

    combined_oos.to_csv(
        RESULTS_PATH
        / "project008_walk_forward_backtest.csv"
    )

    save_combined_equity_chart(
        combined_oos
    )

    save_parameter_chart(
        metrics
    )

    save_yearly_sharpe_chart(
        metrics
    )

    print_summary(
        metrics=metrics,
        combined_oos=combined_oos,
    )

    print("\nFiles saved:")
    print(
        "- results/"
        "project008_walk_forward_metrics.csv"
    )
    print(
        "- results/"
        "project008_walk_forward_backtest.csv"
    )
    print(
        "- results/"
        "project008_walk_forward_equity.png"
    )
    print(
        "- results/"
        "project008_parameter_evolution.png"
    )
    print(
        "- results/"
        "project008_yearly_sharpe.png"
    )


if __name__ == "__main__":
    main()