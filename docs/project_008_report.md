# Project 008 — Walk-Forward Validation

## Research Question

Does the NIFTY 50 moving-average strategy maintain acceptable
performance when parameters are repeatedly selected using past data
and applied to the following unseen calendar year?

## Methodology

A rolling five-year training window was used.

For every cycle:

1. Moving-average combinations were optimized using the preceding
   five calendar years.
2. The configuration with the highest training Sharpe ratio was selected.
3. The selected parameters were frozen.
4. The strategy was evaluated on the following unseen calendar year.
5. The process was moved forward by one year and repeated.

A one-day position shift prevented look-ahead bias.

A transaction cost of 0.05% was applied to every position change.

All yearly out-of-sample returns were combined into one continuous
walk-forward equity curve.

## Dataset

- Instrument: NIFTY 50
- Ticker: ^NSEI
- Frequency: Daily
- Historical start date: 2010-01-04
- Training window: Five years
- Testing window: One calendar year
- Walk-forward test period: 2015 to 2026
- Transaction cost: 0.05% per position change

## Combined Walk-Forward Performance

- Windows tested: 12
- Combined out-of-sample CAGR: 5.64%
- Combined annualized volatility: 10.83%
- Combined Sharpe ratio: 0.58
- Combined maximum drawdown: -20.17%
- Average yearly Sharpe ratio: 0.58
- Median yearly Sharpe ratio: 0.34
- Positive-Sharpe windows: 66.67%
- Positive-Sharpe windows by count: 8 out of 12

## Parameter Stability

- Average selected fast MA: 25.0
- Average selected slow MA: 83.3
- Most frequently selected fast MA: 5
- Most frequently selected slow MA: 50

The selected parameters changed materially across the walk-forward
windows.

The slow 50-day moving average was selected in 7 of the 12 windows,
making it the most persistent slow parameter. The 150-day slow moving
average was selected three times, while the 100-day average was selected
twice.

Fast-window selections were less stable. The 5-day average was selected
four times, the 20-day average three times and the 50-day average three
times. The 30-day and 40-day averages were each selected once.

The results therefore suggest partial parameter stability rather than
one dominant configuration. The 50-day slow average appeared frequently,
but the preferred fast average changed depending on the training period
and market regime.

## Best Out-of-Sample Window

- Test year: 2020
- Selected fast MA: 5
- Selected slow MA: 50
- Sharpe ratio: 2.64
- CAGR: 39.05%
- Maximum drawdown: -7.28%
- Annualized volatility: 12.96%
- Completed trades: 2
- Market exposure: 67.20%

The strategy performed exceptionally well during 2020. However, this
result should not be treated as representative of normal performance
because 2020 contained an unusually sharp market decline followed by a
strong recovery.

## Worst Out-of-Sample Window

- Test year: 2022
- Selected fast MA: 20
- Selected slow MA: 50
- Sharpe ratio: -0.97
- CAGR: -11.56%
- Maximum drawdown: -16.04%
- Annualized volatility: 11.98%
- Completed trades: 3
- Market exposure: 54.44%

The strategy struggled during 2022, indicating that the moving-average
approach was less effective during that market regime.

## Research Questions and Answers

### 1. Did the strategy produce positive out-of-sample performance overall?

Yes.

The continuous walk-forward portfolio achieved a combined out-of-sample
CAGR of 5.64% and a Sharpe ratio of 0.58.

The equity curve increased from approximately ₹1 to approximately ₹1.9
over the walk-forward period, although it experienced multiple flat and
declining periods.

This indicates positive historical out-of-sample performance, but the
return was modest and uneven.

### 2. How many test windows produced a positive Sharpe ratio?

Eight of the twelve windows produced a positive Sharpe ratio.

This equals 66.67% of the yearly test windows.

Four windows had a negative or approximately zero Sharpe ratio,
demonstrating that the strategy did not perform consistently every year.

### 3. Did one moving-average combination dominate?

No single complete moving-average pair dominated every period.

However, the 50-day slow moving average appeared in 7 of the 12 selected
configurations, suggesting that it was the most stable component of the
strategy.

The fast moving average changed considerably across periods. It ranged
from 5 days to 50 days, indicating that the preferred trend sensitivity
varied across different market regimes.

### 4. Was performance consistent across market regimes?

No.

Performance varied substantially across yearly test windows.

Strong years included:

- 2017: Sharpe ratio approximately 2.09
- 2020: Sharpe ratio approximately 2.64
- 2021: Sharpe ratio approximately 1.69
- 2023: Sharpe ratio approximately 1.53

Weak years included:

- 2015: Sharpe ratio approximately -0.55
- 2018: Sharpe ratio approximately -0.67
- 2022: Sharpe ratio approximately -0.97
- 2025: Sharpe ratio approximately -0.06

This variation shows that the strategy was highly dependent on the
prevailing market regime.

### 5. Did repeated re-optimization improve robustness?

Repeated re-optimization produced a positive combined out-of-sample
result, but it did not eliminate poor test years.

The combined Sharpe ratio of 0.58 and maximum drawdown of -20.17% suggest
that the walk-forward process produced an acceptable but not exceptional
risk-adjusted outcome.

Re-optimization allowed the selected parameters to adapt over time, but
the yearly results still varied widely.

### 6. Is there evidence of overfitting?

There is some evidence of instability, but not clear evidence of complete
overfitting.

Several training-selected configurations performed poorly during the
following test year. For example, the configuration selected for 2022
had a strong training Sharpe ratio but produced an out-of-sample Sharpe
ratio of approximately -0.97.

This shows that strong training results did not always generalize.

However, the combined walk-forward portfolio remained profitable, and
two-thirds of the yearly windows produced positive Sharpe ratios.
Therefore, the evidence is more consistent with a modest and
regime-dependent signal than with total historical overfitting.

### 7. Did the parameters remain stable?

Only partially.

The 50-day slow moving average was selected most often, which suggests
some stability around medium-term trend measurement.

The fast window changed frequently, indicating that the strategy's
preferred responsiveness varied across different periods.

This suggests that the underlying trend-following concept may be more
stable than any specific parameter pair.

### 8. Would one fixed parameter pair have worked equally well?

This project does not directly compare the walk-forward strategy against
one fixed parameter configuration across the same period.

A valid next test would compare:

- Walk-forward optimized parameters
- Fixed MA 5/50
- Fixed MA 20/50
- Buy and hold

using the same 2015–2026 out-of-sample dates.

Without this direct comparison, it is not possible to conclude whether
repeated optimization added meaningful value.

### 9. Was the strategy robust across all years?

No.

The strategy produced several strong years and several negative years.

Its robustness is therefore moderate rather than universal. It appears
capable of benefiting from strongly trending conditions while struggling
during sideways, whipsawing or rapidly changing environments.

### 10. Is the strategy ready for live deployment?

No.

The results justify further research, but not deployment.

Additional work should include:

- Comparison with fixed-parameter strategies
- Buy-and-hold benchmark metrics over the same walk-forward period
- Testing on Bank NIFTY, gold and international indices
- More realistic Indian transaction costs
- Slippage and execution assumptions
- Different training-window lengths
- Multi-year test windows
- Statistical significance analysis
- Regime-based performance analysis

## Key Findings

1. The combined walk-forward strategy achieved a positive CAGR of 5.64%
   and a Sharpe ratio of 0.58.

2. Eight of twelve yearly test windows produced positive Sharpe ratios,
   showing moderate but inconsistent robustness.

3. The 50-day slow moving average was selected in most windows, while
   the fast parameter changed frequently.

4. Performance varied significantly by market regime, with very strong
   results in 2020 and very weak results in 2022.

5. Repeated optimization did not prevent negative years and may not
   necessarily outperform a simpler fixed-parameter strategy.

6. The combined maximum drawdown of -20.17% remained material despite
   the strategy spending part of the time in cash.

7. The evidence supports a persistent but modest trend-following effect,
   rather than a stable high-performance trading system.

## Limitations

- The training window was fixed at five years.
- The testing window was limited to one calendar year.
- Only NIFTY 50 was evaluated.
- The model used daily closing prices.
- Trading costs were simplified.
- Slippage, STT, exchange fees and taxes were not modeled separately.
- Cash earned no interest.
- The strategy remained long or in cash and did not short the market.
- Parameter selection used the highest training Sharpe ratio.
- Repeated parameter selection may still introduce data-mining bias.
- The 2026 test window is incomplete and should not be compared directly
  with complete calendar years.
- Annualized metrics for partial-year windows can be unstable.
- No direct comparison was made with a fixed-parameter strategy over
  the same walk-forward period.
- No formal statistical significance test was performed.

## Conclusion

The walk-forward analysis produced evidence of moderate out-of-sample
robustness for the NIFTY 50 moving-average strategy.

Across twelve rolling test windows, the combined strategy achieved a
5.64% CAGR, a Sharpe ratio of 0.58 and a maximum drawdown of -20.17%.
Eight of the twelve yearly windows produced positive Sharpe ratios.

The strategy performed well during several strongly trending years but
also produced losses during unfavourable regimes. Parameter selections
changed over time, although the 50-day slow moving average appeared
frequently.

These findings suggest that the trend-following concept may contain a
persistent but modest historical effect. However, the considerable
variation across years shows that the strategy is not reliably profitable
under all market conditions.

The next research step should compare the walk-forward approach against
fixed moving-average configurations and buy-and-hold over the same dates.
This will determine whether repeated optimization added genuine value or
introduced unnecessary complexity.