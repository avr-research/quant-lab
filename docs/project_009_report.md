# Project 009 — Multi-Strategy Comparison

## Research Question

How do trend-following, momentum, breakout and mean-reversion
strategies differ in return, volatility, drawdown, exposure and
risk-adjusted performance when tested on the same NIFTY 50 dataset?

## Dataset

- Instrument: NIFTY 50
- Ticker: ^NSEI
- Frequency: Daily
- Historical start date: 2010-01-04
- Historical end date: 2026-08-05
- Transaction cost: 0.05% per position change
- Positioning: Long or cash
- Risk-free rate assumption: 0%

## Strategies Evaluated

### 1. Buy and Hold

The strategy remained continuously invested in NIFTY 50.

### 2. MA 5/50 Trend Strategy

The strategy remained invested when the 5-day moving average was
above the 50-day moving average and moved to cash otherwise.

### 3. 63-Day Momentum Strategy

The strategy remained invested when the current closing price was
above the closing price from 63 trading days earlier.

### 4. 55/20 Breakout Strategy

The strategy entered when price exceeded the previous 55-day high and
exited when price fell below the previous 20-day low.

### 5. RSI Mean-Reversion Strategy

The strategy entered when 14-day RSI fell below 30 and exited when RSI
rose above 55.

## Methodology

All strategies were evaluated using the same backtesting engine.

A one-day signal shift was applied so that information generated from
the current trading day's closing price could only affect the following
trading day's position.

A transaction cost of 0.05% was charged for every position change.

The strategies were compared using:

- Compound annual growth rate
- Annualized volatility
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Calmar ratio
- Completed trades
- Market exposure
- Cumulative transaction-cost drag
- Final growth of ₹1

## Performance Summary

| Strategy | CAGR | Volatility | Sharpe | Sortino | Maximum Drawdown | Calmar | Completed Trades | Exposure | Final Value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Buy and Hold | 9.79% | 16.48% | 0.66 | 0.64 | -38.44% | 0.25 | 0 | 99.98% | ₹4.70 |
| MA 5/50 | 6.91% | 10.52% | 0.70 | 0.57 | -21.77% | 0.32 | 59 | 63.08% | ₹3.03 |
| 63-Day Momentum | 7.53% | 10.76% | 0.75 | 0.61 | -17.95% | 0.42 | 87 | 64.83% | ₹3.33 |
| 55/20 Breakout | 2.67% | 8.48% | 0.36 | 0.24 | -21.18% | 0.13 | 51 | 44.72% | ₹1.55 |
| RSI Mean Reversion | 1.95% | 9.73% | 0.25 | 0.09 | -32.67% | 0.06 | 22 | 13.50% | ₹1.38 |

## Best Strategy by Sharpe Ratio

- Strategy: 63-Day Momentum
- Sharpe ratio: 0.75
- CAGR: 7.53%
- Annualized volatility: 10.76%
- Maximum drawdown: -17.95%
- Market exposure: 64.83%
- Calmar ratio: 0.42
- Final portfolio value: ₹3.33

## Best Strategy by CAGR

- Strategy: Buy and Hold
- CAGR: 9.79%
- Sharpe ratio: 0.66
- Maximum drawdown: -38.44%
- Annualized volatility: 16.48%
- Final portfolio value: ₹4.70

## Best Strategy by Drawdown Protection

- Strategy: 63-Day Momentum
- Maximum drawdown: -17.95%
- CAGR: 7.53%
- Sharpe ratio: 0.75
- Calmar ratio: 0.42

## Research Questions and Answers

### 1. Which strategy generated the highest absolute return?

Buy and Hold generated the highest absolute return.

It achieved:

- CAGR: 9.79%
- Final growth of ₹1: ₹4.70

The active strategies produced lower absolute returns because they
spent significant periods in cash and missed portions of long-term
market advances.

### 2. Which strategy generated the strongest risk-adjusted return?

The 63-Day Momentum strategy generated the strongest risk-adjusted
performance.

It achieved:

- Sharpe ratio: 0.75
- Sortino ratio: 0.61
- Calmar ratio: 0.42

Its Sharpe ratio was higher than Buy and Hold at 0.66 and MA 5/50 at
0.70.

This indicates that the momentum strategy generated the most return per
unit of total volatility among the tested strategies.

Buy and Hold had a slightly higher Sortino ratio than momentum, at 0.64
versus 0.61, showing that its relationship between return and downside
deviation remained competitive despite its much larger drawdown.

### 3. Which strategy offered the strongest drawdown protection?

The 63-Day Momentum strategy produced the smallest maximum drawdown.

- 63-Day Momentum: -17.95%
- 55/20 Breakout: -21.18%
- MA 5/50: -21.77%
- RSI Mean Reversion: -32.67%
- Buy and Hold: -38.44%

Momentum reduced maximum drawdown by approximately 20.49 percentage
points compared with Buy and Hold.

It also produced the highest Calmar ratio, indicating the strongest CAGR
relative to maximum drawdown.

### 4. Did lower market exposure reduce risk?

Lower market exposure generally reduced volatility, but it did not
automatically produce better drawdown protection or stronger returns.

For example:

- Buy and Hold had nearly 100% exposure and 16.48% volatility.
- Momentum had 64.83% exposure and 10.76% volatility.
- MA 5/50 had 63.08% exposure and 10.52% volatility.
- Breakout had 44.72% exposure and 8.48% volatility.
- RSI had only 13.50% exposure and 9.73% volatility.

The breakout strategy had the lowest volatility, but its CAGR was only
2.67%.

The RSI strategy had the lowest exposure but still experienced a
-32.67% maximum drawdown. This shows that low exposure alone does not
guarantee strong downside protection. The timing and duration of
individual positions also matter.

### 5. Did the mean-reversion strategy behave differently from the trend strategies?

Yes.

The RSI strategy spent only 13.50% of trading days invested, while the
momentum and moving-average strategies were invested approximately 63%
to 65% of the time.

Its equity curve increased in isolated steps and remained flat for long
periods because it only entered after oversold conditions.

The RSI strategy was also exposed to sharp losses during some market
declines, particularly around 2020. Its low market exposure did not
prevent a large maximum drawdown.

This behaviour differed materially from the smoother and more
continuously invested trend-following strategies.

### 6. Did the breakout and momentum strategies produce similar results?

They shared a trend-following principle but produced materially different
results.

The momentum strategy achieved:

- CAGR: 7.53%
- Sharpe ratio: 0.75
- Maximum drawdown: -17.95%
- Exposure: 64.83%

The breakout strategy achieved:

- CAGR: 2.67%
- Sharpe ratio: 0.36
- Maximum drawdown: -21.18%
- Exposure: 44.72%

The breakout strategy required a new 55-day high before entering, which
made it more selective and caused it to miss a larger portion of market
advances.

Its lower exposure reduced volatility but also reduced return
substantially.

### 7. Did any active strategy outperform Buy and Hold?

No active strategy outperformed Buy and Hold in absolute return.

Buy and Hold achieved the highest CAGR and final portfolio value.

However, the 63-Day Momentum and MA 5/50 strategies outperformed Buy and
Hold on selected risk-adjusted measures.

The momentum strategy achieved:

- Higher Sharpe ratio
- Smaller maximum drawdown
- Higher Calmar ratio
- Lower annualized volatility

Therefore, Buy and Hold was superior for absolute growth, while momentum
offered the strongest overall risk-adjusted trade-off.

### 8. Which strategy appeared most dependent on market regime?

All active strategies showed some regime dependence, but the breakout
and RSI strategies appeared particularly sensitive.

The breakout strategy remained flat for long periods when sustained
new highs did not occur.

The RSI strategy depended on oversold events followed by recoveries.
During prolonged declines or weak rebounds, it remained exposed to
losses after entry.

The moving-average and momentum strategies also experienced flat and
declining periods, but their long-term equity curves were more persistent.

### 9. Did transaction frequency materially affect performance?

The 63-Day Momentum strategy traded most frequently:

- Momentum: 87 completed trades
- MA 5/50: 59 completed trades
- Breakout: 51 completed trades
- RSI: 22 completed trades

Its modeled cumulative transaction-cost drag was 8.75%, compared with
5.95% for MA 5/50, 5.15% for breakout and 2.20% for RSI.

Despite having the highest transaction-cost drag, momentum still ranked
first by Sharpe ratio and active-strategy CAGR.

This suggests that its historical advantage was strong enough to survive
the simplified cost assumption. However, more realistic Indian market
charges and slippage could reduce its performance further.

### 10. Is any strategy ready for deployment?

No.

The results are based on one historical instrument and one full-sample
comparison.

Before deployment, each strategy would require:

- Out-of-sample validation
- Walk-forward testing
- Testing on other indices and asset classes
- More realistic transaction-cost assumptions
- Slippage and liquidity modeling
- Parameter sensitivity analysis
- Benchmark comparison over identical periods
- Statistical significance assessment
- Paper trading and execution testing

The current results identify research candidates, not deployable trading
systems.

## Key Findings

1. Buy and Hold delivered the highest absolute return, with a 9.79% CAGR
   and final portfolio value of ₹4.70.

2. The 63-Day Momentum strategy produced the strongest overall
   risk-adjusted result, with a 0.75 Sharpe ratio and -17.95% maximum
   drawdown.

3. MA 5/50 also improved risk-adjusted performance relative to Buy and
   Hold, but it underperformed momentum on CAGR, Sharpe and drawdown.

4. Lower market exposure reduced volatility but did not automatically
   improve returns or drawdown protection.

5. The breakout and RSI strategies were too selective to capture enough
   long-term market growth under the tested rules.

6. Momentum's higher trading frequency created the largest cumulative
   modeled cost drag, but it still ranked first among active strategies.

7. No strategy dominated every metric. Buy and Hold was strongest for
   absolute return, while momentum offered the best balance of return,
   volatility and drawdown.

## Limitations

- All strategies were evaluated on one financial instrument.
- Parameters were chosen from established conventions but were not
  independently validated in this project.
- The full historical period was used for comparison.
- No separate training and testing period was included.
- Transaction costs were simplified.
- Slippage, STT, taxes, exchange charges and bid-ask spreads were not
  modeled separately.
- Cash earned no interest.
- Strategies remained long or in cash and did not short the index.
- Daily closing prices do not model intraday execution.
- NIFTY index data may not perfectly represent a tradable instrument.
- The strategies may be correlated because several depend on price
  trends.
- The RSI rules may expose the strategy to falling-market risk after
  entering an oversold position.
- The breakout strategy may be sensitive to its 55-day entry and 20-day
  exit parameters.
- The momentum strategy's 63-day lookback was not tested against nearby
  alternatives.
- No statistical-significance test was performed.
- The 2026 data represents an incomplete calendar year.

## Conclusion

The multi-strategy comparison demonstrated that absolute return and
risk-adjusted performance can lead to different strategy rankings.

Buy and Hold achieved the highest long-term CAGR at 9.79%, but it also
experienced the highest volatility and maximum drawdown.

The 63-Day Momentum strategy generated a lower CAGR of 7.53% but offered
the strongest Sharpe ratio, smallest maximum drawdown and highest Calmar
ratio. This made it the strongest historical active strategy on a
risk-adjusted basis.

The MA 5/50 strategy also reduced risk materially but performed slightly
below momentum. The breakout and RSI strategies reduced market exposure,
but their lower participation resulted in weak long-term returns.

The results suggest that medium-term momentum deserves further research.
However, its apparent advantage must be validated using parameter
sensitivity testing, walk-forward analysis and additional assets before
stronger conclusions can be made.