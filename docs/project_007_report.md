# Project 007 — Out-of-Sample Validation

## Research Question

Does a moving-average strategy selected using the 2010–2020
training period maintain its performance when applied without
re-optimization to unseen NIFTY 50 data from 2021 onward?

## Methodology

The NIFTY 50 historical dataset was divided into two distinct periods:

- Training period: 2010-01-04 to 2020-12-31
- Testing period: 2021-01-01 to 2026-08-05

All valid fast and slow moving-average combinations were evaluated
using only the training-period dataset.

The configuration with the highest training-period Sharpe ratio was
selected. Its parameters were then frozen and applied to the testing
period without further optimization.

The strategy remained long when the fast moving average was above the
slow moving average and stayed in cash otherwise.

A one-day shift was applied to the strategy position to prevent
look-ahead bias. A transaction cost of 0.05% was deducted for every
position change.

## Research Questions and Answers

### 1. Which parameters were selected using the training data?

The training-period optimization selected:

- Fast moving average: 5 days
- Slow moving average: 50 days

This configuration achieved the highest Sharpe ratio during the
2010-01-04 to 2020-12-31 training period.

### 2. Did the strategy remain profitable out of sample?

Yes.

The strategy produced a positive out-of-sample CAGR of 5.27% during the
2021-01-01 to 2026-08-05 testing period.

However, this was lower than the 7.72% CAGR achieved during training,
indicating weaker performance on unseen data.

### 3. How much did the Sharpe ratio change?

The Sharpe ratio declined from:

- Training: 0.78
- Testing: 0.56

This represents a reduction of 0.22.

The decline indicates that the strategy generated lower return per unit
of volatility during the out-of-sample period.

### 4. Did maximum drawdown become better or worse?

Maximum drawdown improved slightly.

- Training maximum drawdown: -21.77%
- Testing maximum drawdown: -20.39%

The testing-period drawdown was approximately 1.38 percentage points
less severe.

This suggests that downside risk remained broadly stable and did not
deteriorate materially out of sample.

### 5. Was volatility stable across the two periods?

Yes.

Annualized volatility was:

- Training: 10.58%
- Testing: 10.42%

The difference was only -0.16 percentage points.

This indicates that the strategy maintained a very similar risk profile
during the unseen testing period.

### 6. Did market exposure change substantially?

No.

Market exposure was:

- Training: 63.20%
- Testing: 62.85%

The difference was only -0.35 percentage points.

This suggests that the selected MA 5/50 configuration behaved
consistently in terms of how often it remained invested.

### 7. Did the strategy outperform buy-and-hold out of sample?

The current terminal summary does not provide the out-of-sample
buy-and-hold CAGR, Sharpe ratio and drawdown values directly.

The testing equity chart should therefore be used only as a visual
comparison until the exact buy-and-hold metrics are calculated and
reported.

Based on the chart, buy-and-hold appears to have achieved stronger
absolute growth over parts of the test period, while the moving-average
strategy appears smoother and spends substantial time in cash.

A precise conclusion should be made only after adding the corresponding
buy-and-hold metrics to the report.

### 8. Did the strategy show evidence of overfitting?

There is some evidence of performance degradation, but not a complete
collapse.

The CAGR declined by 2.45 percentage points and the Sharpe ratio declined
by 0.22 after moving from training to unseen data.

This suggests that part of the training-period performance may have
resulted from in-sample parameter selection.

However, the strategy retained:

- Positive CAGR
- Positive Sharpe ratio
- Similar volatility
- Similar market exposure
- Slightly better maximum drawdown

Therefore, the result is more consistent with moderate deterioration
than severe overfitting.

### 9. Is the strategy robust enough for live deployment?

No.

A single successful out-of-sample test is not enough to justify live
deployment.

The strategy still requires:

- Walk-forward validation
- Testing across multiple train/test windows
- Testing on additional indices and asset classes
- More realistic Indian transaction-cost modeling
- Slippage and liquidity assumptions
- Comparison against exact out-of-sample buy-and-hold metrics
- Sensitivity analysis around the selected MA 5/50 parameters

The current result supports further investigation, not live trading.

### 10. What is the main research conclusion?

The MA 5/50 strategy showed partial out-of-sample robustness.

Its return and Sharpe ratio weakened on unseen data, but its volatility,
drawdown and exposure remained stable. This suggests that the underlying
trend-following behaviour may persist, although the historical edge is
modest and not yet strong enough to support deployment.

## The research questions were answered using the exact training and testing
## metrics generated by the backtest, without modifying the selected
## parameters after observing the test results. 


## Selected Parameters

- Fast MA: 5
- Slow MA: 50
- Training selection criterion: Highest Sharpe ratio

## Training Performance

- CAGR: 7.72%
- Annualized volatility: 10.58%
- Sharpe ratio: 0.78
- Maximum drawdown: -21.77%
- Completed trades: 36
- Market exposure: 63.20%

## Out-of-Sample Performance

- CAGR: 5.27%
- Annualized volatility: 10.42%
- Sharpe ratio: 0.56
- Maximum drawdown: -20.39%
- Completed trades: 23
- Market exposure: 62.85%

## Performance Change

- Change in CAGR: -2.45 percentage points
- Change in Sharpe ratio: -0.22
- Change in annualized volatility: -0.16 percentage points
- Change in maximum drawdown: improved by 1.38 percentage points
- Change in market exposure: -0.35 percentage points

## Observations

1. The strategy remained profitable during the out-of-sample period,
   but its CAGR declined from 7.72% to 5.27%.

2. The Sharpe ratio declined from 0.78 to 0.56, indicating weaker
   risk-adjusted performance on unseen data.

3. Annualized volatility remained almost unchanged, suggesting that
   the strategy maintained a similar risk profile in both periods.

4. Maximum drawdown improved slightly from -21.77% to -20.39%.

5. Market exposure remained stable at approximately 63% in both the
   training and testing periods.

6. The strategy did not experience a complete performance collapse
   after the parameters were frozen.

## Robustness Assessment

The out-of-sample results show moderate deterioration rather than
complete failure.

The strategy retained a positive CAGR and positive Sharpe ratio during
the testing period. Its volatility, drawdown and market exposure also
remained broadly consistent with the training-period results.

The decline in CAGR and Sharpe ratio suggests that part of the stronger
training performance may have resulted from favourable historical
conditions or in-sample parameter selection.

However, the stability of volatility, drawdown and exposure indicates
that the strategy's underlying behaviour generalized reasonably well
to the unseen period.

These findings support further research but are not sufficient to
justify live deployment.

## Limitations

- Only one fixed train/test split was used.
- The strategy was evaluated only on NIFTY 50.
- Trading costs remain simplified.
- Slippage, STT, exchange charges and taxes were not modeled separately.
- Cash earned no interest while the strategy was out of the market.
- The parameter set was selected from a limited predefined search space.
- The training and testing periods contain different market regimes.
- The analysis does not include rolling or walk-forward validation.
- The strategy was not tested on other indices or asset classes.
- Positive out-of-sample performance does not guarantee future returns.

## Conclusion

The MA 5/50 moving-average strategy demonstrated partial out-of-sample
robustness.

Its CAGR declined from 7.72% during training to 5.27% during testing,
and its Sharpe ratio declined from 0.78 to 0.56. This represents
meaningful performance deterioration, but not a complete breakdown.

The strategy retained positive returns, stable volatility, similar
market exposure and a slightly improved maximum drawdown during the
unseen testing period.

The evidence suggests that the strategy may contain a persistent but
modest trend-following effect. Nevertheless, the results are based on
one train/test split and one financial instrument.

The next required step is walk-forward validation across multiple
training and testing windows, followed by testing on additional
markets before stronger claims about robustness can be made.