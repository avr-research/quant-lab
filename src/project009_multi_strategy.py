from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

DATA_PATH = Path("data/nifty50_history.csv")
RESULTS_PATH = Path("results")

TRANSACTION_COST = 0.0005
TRADING_DAYS_PER_YEAR = 252

# Moving-average trend strategy
FAST_MA = 5
SLOW_MA = 50

# Momentum strategy
MOMENTUM_LOOKBACK = 63

# Breakout strategy
BREAKOUT_ENTRY_WINDOW = 55
BREAKOUT_EXIT_WINDOW = 20

# RSI mean-reversion strategy
RSI_WINDOW = 14
RSI_ENTRY_LEVEL = 30
RSI_EXIT_LEVEL = 55


# =========================================================
# DATA LOADING
# =========================================================

def load_close_prices(file_path: Path) -> pd.Series:
    """
    Load adjusted NIFTY 50 closing prices from the yfinance CSV.
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
# TECHNICAL INDICATORS
# =========================================================

def calculate_rsi(
    close_prices: pd.Series,
    window: int = RSI_WINDOW,
) -> pd.Series:
    """
    Calculate the Relative Strength Index using
    exponentially smoothed gains and losses.
    """

    price_change = close_prices.diff()

    gains = price_change.clip(lower=0)
    losses = -price_change.clip(upper=0)

    average_gain = gains.ewm(
        alpha=1 / window,
        adjust=False,
        min_periods=window,
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / window,
        adjust=False,
        min_periods=window,
    ).mean()

    relative_strength = (
        average_gain
        / average_loss.replace(0, np.nan)
    )

    rsi = 100 - (
        100 / (1 + relative_strength)
    )

    # When average loss is zero, RSI should be 100.
    rsi = rsi.where(
        average_loss != 0,
        100,
    )

    return rsi


# =========================================================
# SIGNAL GENERATION
# =========================================================

def generate_buy_hold_signal(
    close_prices: pd.Series,
) -> pd.Series:
    """
    Remain continuously invested.
    """

    return pd.Series(
        1.0,
        index=close_prices.index,
        name="Buy and Hold",
    )


def generate_ma_signal(
    close_prices: pd.Series,
) -> pd.Series:
    """
    Long when the 5-day MA is above the 50-day MA.
    """

    fast_average = close_prices.rolling(
        FAST_MA
    ).mean()

    slow_average = close_prices.rolling(
        SLOW_MA
    ).mean()

    signal = pd.Series(
        np.where(
            fast_average > slow_average,
            1.0,
            0.0,
        ),
        index=close_prices.index,
        name="MA 5/50",
    )

    return signal


def generate_momentum_signal(
    close_prices: pd.Series,
) -> pd.Series:
    """
    Long when the current close is above the close
    from 63 trading days earlier.
    """

    past_price = close_prices.shift(
        MOMENTUM_LOOKBACK
    )

    signal = pd.Series(
        np.where(
            close_prices > past_price,
            1.0,
            0.0,
        ),
        index=close_prices.index,
        name="63-Day Momentum",
    )

    return signal


def generate_breakout_signal(
    close_prices: pd.Series,
) -> pd.Series:
    """
    Enter when price exceeds the previous 55-day high.

    Exit when price falls below the previous 20-day low.

    Current-day price is excluded from both rolling levels
    to prevent the signal from using future information.
    """

    previous_entry_high = (
        close_prices
        .rolling(BREAKOUT_ENTRY_WINDOW)
        .max()
        .shift(1)
    )

    previous_exit_low = (
        close_prices
        .rolling(BREAKOUT_EXIT_WINDOW)
        .min()
        .shift(1)
    )

    signal = pd.Series(
        0.0,
        index=close_prices.index,
        name="55/20 Breakout",
    )

    current_position = 0.0

    for date in close_prices.index:
        current_price = close_prices.loc[date]
        entry_level = previous_entry_high.loc[date]
        exit_level = previous_exit_low.loc[date]

        if pd.isna(entry_level) or pd.isna(exit_level):
            signal.loc[date] = current_position
            continue

        if current_position == 0 and current_price > entry_level:
            current_position = 1.0

        elif (
            current_position == 1
            and current_price < exit_level
        ):
            current_position = 0.0

        signal.loc[date] = current_position

    return signal


def generate_rsi_signal(
    close_prices: pd.Series,
) -> pd.Series:
    """
    Mean-reversion strategy:

    Enter when RSI falls below 30.
    Exit when RSI rises above 55.
    """

    rsi = calculate_rsi(
        close_prices,
        RSI_WINDOW,
    )

    signal = pd.Series(
        0.0,
        index=close_prices.index,
        name="RSI Mean Reversion",
    )

    current_position = 0.0

    for date in close_prices.index:
        current_rsi = rsi.loc[date]

        if pd.isna(current_rsi):
            signal.loc[date] = current_position
            continue

        if (
            current_position == 0
            and current_rsi < RSI_ENTRY_LEVEL
        ):
            current_position = 1.0

        elif (
            current_position == 1
            and current_rsi > RSI_EXIT_LEVEL
        ):
            current_position = 0.0

        signal.loc[date] = current_position

    return signal


# =========================================================
# BACKTEST ENGINE
# =========================================================

def backtest_signal(
    close_prices: pd.Series,
    signal: pd.Series,
    strategy_name: str,
) -> pd.DataFrame:
    """
    Convert a strategy signal into positions, returns,
    costs, growth and drawdowns.
    """

    backtest = pd.DataFrame(
        index=close_prices.index
    )

    backtest["Close"] = close_prices

    backtest["Market Return"] = (
        close_prices
        .pct_change()
        .fillna(0)
    )

    backtest["Signal"] = signal.reindex(
        close_prices.index
    ).fillna(0)

    # The signal formed using today's close is applied
    # from the following trading day.
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

    if strategy_name == "Buy and Hold":
        # Model one initial entry for a fair comparison.
        backtest.iloc[
            0,
            backtest.columns.get_loc(
                "Position Change"
            ),
        ] = 1.0

    backtest["Trading Cost"] = (
        backtest["Position Change"]
        * TRANSACTION_COST
    )

    backtest["Strategy Return"] = (
        backtest["Position"]
        * backtest["Market Return"]
        - backtest["Trading Cost"]
    )

    backtest["Growth"] = (
        1 + backtest["Strategy Return"]
    ).cumprod()

    backtest["Running Peak"] = (
        backtest["Growth"].cummax()
    )

    backtest["Drawdown"] = (
        backtest["Growth"]
        / backtest["Running Peak"]
        - 1
    )

    backtest["Strategy"] = strategy_name

    return backtest


# =========================================================
# PERFORMANCE METRICS
# =========================================================

def calculate_cagr(
    growth: pd.Series,
) -> float:
    """
    Calculate compound annual growth rate.
    """

    clean_growth = growth.dropna()

    if len(clean_growth) < 2:
        return float("nan")

    years = (
        clean_growth.index[-1]
        - clean_growth.index[0]
    ).days / 365.25

    if years <= 0 or clean_growth.iloc[0] <= 0:
        return float("nan")

    return (
        clean_growth.iloc[-1]
        / clean_growth.iloc[0]
    ) ** (1 / years) - 1


def calculate_volatility(
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


def calculate_sharpe(
    returns: pd.Series,
) -> float:
    """
    Calculate annualized Sharpe ratio with a
    zero risk-free rate.
    """

    clean_returns = returns.dropna()

    if clean_returns.empty:
        return float("nan")

    daily_volatility = clean_returns.std()

    if (
        daily_volatility == 0
        or np.isnan(daily_volatility)
    ):
        return float("nan")

    return (
        clean_returns.mean()
        / daily_volatility
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_sortino(
    returns: pd.Series,
) -> float:
    """
    Calculate annualized Sortino ratio using only
    negative-return volatility.
    """

    clean_returns = returns.dropna()
    downside_returns = clean_returns[
        clean_returns < 0
    ]

    if downside_returns.empty:
        return float("nan")

    downside_deviation = (
        np.sqrt(
            np.mean(
                np.square(downside_returns)
            )
        )
    )

    if (
        downside_deviation == 0
        or np.isnan(downside_deviation)
    ):
        return float("nan")

    return (
        clean_returns.mean()
        / downside_deviation
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_calmar(
    cagr: float,
    maximum_drawdown: float,
) -> float:
    """
    Calculate CAGR divided by absolute maximum drawdown.
    """

    if (
        maximum_drawdown == 0
        or np.isnan(maximum_drawdown)
    ):
        return float("nan")

    return cagr / abs(maximum_drawdown)


def calculate_strategy_metrics(
    backtest: pd.DataFrame,
    strategy_name: str,
) -> dict:
    """
    Produce a common performance summary.
    """

    cagr = calculate_cagr(
        backtest["Growth"]
    )

    volatility = calculate_volatility(
        backtest["Strategy Return"]
    )

    sharpe = calculate_sharpe(
        backtest["Strategy Return"]
    )

    sortino = calculate_sortino(
        backtest["Strategy Return"]
    )

    maximum_drawdown = (
        backtest["Drawdown"].min()
    )

    position_changes = int(
        backtest["Position Change"].sum()
    )

    if strategy_name == "Buy and Hold":
        completed_trades = 0
    else:
        completed_trades = (
            position_changes // 2
        )

    positive_days = (
        backtest.loc[
            backtest["Position"] == 1,
            "Strategy Return",
        ] > 0
    )

    invested_days = (
        backtest["Position"] == 1
    )

    if invested_days.sum() > 0:
        positive_invested_day_rate = (
            positive_days.sum()
            / invested_days.sum()
        )
    else:
        positive_invested_day_rate = float("nan")

    return {
        "Strategy": strategy_name,
        "CAGR": cagr,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Maximum Drawdown": maximum_drawdown,
        "Calmar Ratio": calculate_calmar(
            cagr,
            maximum_drawdown,
        ),
        "Completed Trades": completed_trades,
        "Position Changes": position_changes,
        "Market Exposure": (
            backtest["Position"].mean()
        ),
        "Cumulative Cost Drag": (
            backtest["Trading Cost"].sum()
        ),
        "Positive Invested Days": (
            positive_invested_day_rate
        ),
        "Final Portfolio Value": (
            backtest["Growth"].iloc[-1]
        ),
    }


# =========================================================
# STRATEGY EXECUTION
# =========================================================

def run_all_strategies(
    close_prices: pd.Series,
) -> tuple[
    pd.DataFrame,
    dict[str, pd.DataFrame],
]:
    """
    Generate, backtest and evaluate all strategies.
    """

    strategy_signals = {
        "Buy and Hold":
            generate_buy_hold_signal(
                close_prices
            ),
        "MA 5/50":
            generate_ma_signal(
                close_prices
            ),
        "63-Day Momentum":
            generate_momentum_signal(
                close_prices
            ),
        "55/20 Breakout":
            generate_breakout_signal(
                close_prices
            ),
        "RSI Mean Reversion":
            generate_rsi_signal(
                close_prices
            ),
    }

    summaries = []
    backtests = {}

    print("=" * 82)
    print("PROJECT 009 — MULTI-STRATEGY COMPARISON")
    print("=" * 82)

    for strategy_name, signal in (
        strategy_signals.items()
    ):
        print(
            f"Running strategy: {strategy_name}"
        )

        backtest = backtest_signal(
            close_prices=close_prices,
            signal=signal,
            strategy_name=strategy_name,
        )

        metrics = calculate_strategy_metrics(
            backtest=backtest,
            strategy_name=strategy_name,
        )

        backtests[strategy_name] = backtest
        summaries.append(metrics)

    summary = pd.DataFrame(
        summaries
    )

    summary = summary.sort_values(
        by="Sharpe Ratio",
        ascending=False,
    ).reset_index(drop=True)

    return summary, backtests


# =========================================================
# OUTPUT PREPARATION
# =========================================================

def combine_daily_backtests(
    backtests: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Combine selected daily columns for all strategies.
    """

    combined_frames = []

    columns_to_keep = [
        "Close",
        "Signal",
        "Position",
        "Position Change",
        "Trading Cost",
        "Strategy Return",
        "Growth",
        "Drawdown",
        "Strategy",
    ]

    for strategy_name, backtest in (
        backtests.items()
    ):
        output = backtest[
            columns_to_keep
        ].copy()

        output["Strategy"] = strategy_name

        combined_frames.append(output)

    return pd.concat(
        combined_frames
    ).sort_index()


# =========================================================
# VISUALIZATIONS
# =========================================================

def save_equity_curve_chart(
    backtests: dict[str, pd.DataFrame],
) -> None:
    """
    Compare growth of ₹1 across strategies.
    """

    plt.figure(figsize=(14, 7))

    for strategy_name, backtest in (
        backtests.items()
    ):
        plt.plot(
            backtest.index,
            backtest["Growth"],
            label=strategy_name,
        )

    plt.title(
        "Project 009: NIFTY 50 "
        "Multi-Strategy Equity Curves"
    )

    plt.xlabel("Date")
    plt.ylabel("Growth of ₹1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project009_equity_curves.png",
        dpi=150,
    )

    plt.close()


def save_drawdown_chart(
    backtests: dict[str, pd.DataFrame],
) -> None:
    """
    Compare strategy drawdowns.
    """

    plt.figure(figsize=(14, 7))

    for strategy_name, backtest in (
        backtests.items()
    ):
        plt.plot(
            backtest.index,
            backtest["Drawdown"] * 100,
            label=strategy_name,
        )

    plt.title(
        "Project 009: Strategy Drawdown Comparison"
    )

    plt.xlabel("Date")
    plt.ylabel("Drawdown (%)")
    plt.axhline(0, linewidth=1)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project009_drawdowns.png",
        dpi=150,
    )

    plt.close()


def save_risk_return_chart(
    summary: pd.DataFrame,
) -> None:
    """
    Compare annualized volatility and CAGR.
    """

    plt.figure(figsize=(10, 7))

    for _, row in summary.iterrows():
        plt.scatter(
            row["Annualized Volatility"] * 100,
            row["CAGR"] * 100,
            s=90,
        )

        plt.annotate(
            row["Strategy"],
            (
                row["Annualized Volatility"] * 100,
                row["CAGR"] * 100,
            ),
            xytext=(6, 6),
            textcoords="offset points",
        )

    plt.title(
        "Project 009: Strategy Risk–Return Comparison"
    )

    plt.xlabel("Annualized Volatility (%)")
    plt.ylabel("CAGR (%)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project009_risk_return.png",
        dpi=150,
    )

    plt.close()


def save_metric_comparison_chart(
    summary: pd.DataFrame,
) -> None:
    """
    Compare Sharpe and Sortino ratios.
    """

    chart_data = (
        summary
        .set_index("Strategy")[
            [
                "Sharpe Ratio",
                "Sortino Ratio",
            ]
        ]
    )

    axis = chart_data.plot.bar(
        figsize=(12, 6),
    )

    axis.set_title(
        "Project 009: Risk-Adjusted "
        "Performance Comparison"
    )

    axis.set_xlabel("Strategy")
    axis.set_ylabel("Ratio")
    axis.axhline(0, linewidth=1)
    axis.grid(axis="y")

    plt.xticks(
        rotation=25,
        ha="right",
    )

    plt.tight_layout()

    plt.savefig(
        RESULTS_PATH
        / "project009_metric_comparison.png",
        dpi=150,
    )

    plt.close()


# =========================================================
# TERMINAL REPORT
# =========================================================

def print_summary(
    summary: pd.DataFrame,
) -> None:
    """
    Print formatted strategy rankings.
    """

    display_columns = [
        "Strategy",
        "CAGR",
        "Annualized Volatility",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Maximum Drawdown",
        "Calmar Ratio",
        "Completed Trades",
        "Market Exposure",
        "Final Portfolio Value",
    ]

    formatted_summary = summary[
        display_columns
    ].copy()

    print("\n" + "=" * 110)
    print("STRATEGY PERFORMANCE RANKING — SORTED BY SHARPE RATIO")
    print("=" * 110)

    print(
        formatted_summary.to_string(
            index=False,
            formatters={
                "CAGR": "{:.2%}".format,
                "Annualized Volatility":
                    "{:.2%}".format,
                "Sharpe Ratio":
                    "{:.2f}".format,
                "Sortino Ratio":
                    "{:.2f}".format,
                "Maximum Drawdown":
                    "{:.2%}".format,
                "Calmar Ratio":
                    "{:.2f}".format,
                "Market Exposure":
                    "{:.2%}".format,
                "Final Portfolio Value":
                    "{:.2f}".format,
            },
        )
    )

    best_sharpe = summary.iloc[0]

    best_cagr = summary.loc[
        summary["CAGR"].idxmax()
    ]

    best_drawdown = summary.loc[
        summary["Maximum Drawdown"].idxmax()
    ]

    print("\n" + "-" * 110)

    print(
        f"Best Sharpe ratio       : "
        f"{best_sharpe['Strategy']} "
        f"({best_sharpe['Sharpe Ratio']:.2f})"
    )

    print(
        f"Highest CAGR            : "
        f"{best_cagr['Strategy']} "
        f"({best_cagr['CAGR']:.2%})"
    )

    print(
        f"Lowest maximum drawdown : "
        f"{best_drawdown['Strategy']} "
        f"({best_drawdown['Maximum Drawdown']:.2%})"
    )

    print("=" * 110)


# =========================================================
# MAIN WORKFLOW
# =========================================================

def main() -> None:
    """
    Run Project 009.
    """

    RESULTS_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    close_prices = load_close_prices(
        DATA_PATH
    )

    summary, backtests = run_all_strategies(
        close_prices
    )

    daily_backtests = combine_daily_backtests(
        backtests
    )

    summary.to_csv(
        RESULTS_PATH
        / "project009_strategy_summary.csv",
        index=False,
    )

    daily_backtests.to_csv(
        RESULTS_PATH
        / "project009_daily_backtests.csv"
    )

    save_equity_curve_chart(
        backtests
    )

    save_drawdown_chart(
        backtests
    )

    save_risk_return_chart(
        summary
    )

    save_metric_comparison_chart(
        summary
    )

    print_summary(
        summary
    )

    print("\nFiles saved:")
    print(
        "- results/"
        "project009_strategy_summary.csv"
    )
    print(
        "- results/"
        "project009_daily_backtests.csv"
    )
    print(
        "- results/"
        "project009_equity_curves.png"
    )
    print(
        "- results/"
        "project009_drawdowns.png"
    )
    print(
        "- results/"
        "project009_risk_return.png"
    )
    print(
        "- results/"
        "project009_metric_comparison.png"
    )


if __name__ == "__main__":
    main()