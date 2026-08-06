# Project 006 — Moving-Average Parameter Optimization

## Research Question

How sensitive is the NIFTY 50 moving-average strategy to the choice
of fast and slow moving-average windows?

## Dataset

- Instrument: NIFTY 50
- Ticker: ^NSEI
- Start date: 2010-01-04
- End date: 2026-08-05
- Frequency: Daily
- Trading-day records: 4,074
- Transaction cost: 0.05% per position change

## Best Configuration by Sharpe Ratio

The terminal output rounded both MA 5/50 and MA 10/50 to a Sharpe ratio
of 0.70. Based on the sorted optimization output, MA 5/50 ranked first.

- Fast MA: 5
- Slow MA: 50
- CAGR: 6.91%
- Sharpe ratio: 0.70
- Maximum drawdown: -21.77%
- Annualized volatility: 10.52%
- Completed trades: 59
- Market exposure: 63.08%

## Best Configuration by CAGR

- Fast MA: 10
- Slow MA: 50
- CAGR: 7.04%
- Sharpe ratio: 0.70
- Maximum drawdown: -24.65%

## Lowest-Drawdown Configuration

- Fast MA: 20
- Slow MA: 30
- Maximum drawdown: -16.83%
- CAGR: 6.93%
- Sharpe ratio: 0.69

## Parameter Stability

The strongest results were not concentrated in one isolated parameter
combination. Several neighbouring configurations produced similar
risk-adjusted performance.

The most consistent region appeared around fast moving-average windows
of 5 to 20 days and slow moving-average windows of 30 to 50 days.
Configurations such as MA 5/50, MA 10/50, MA 15/50, MA 20/30 and
MA 20/50 all produced relatively similar Sharpe ratios and CAGRs.

This suggests moderate parameter stability rather than dependence on
one unusually successful historical combination. However, the results
were still produced using the same dataset for both parameter selection
and evaluation, so the apparent stability must be tested out of sample.

## Key Findings

1. MA 5/50 and MA 10/50 produced the highest risk-adjusted performance,
   with Sharpe ratios rounded to approximately 0.70.

2. MA 10/50 achieved the highest CAGR of approximately 7.04%, although
   several nearby configurations produced similar returns.

3. MA 20/30 produced the lowest maximum drawdown at approximately
   -16.83%, while maintaining a CAGR of 6.93% and a Sharpe ratio of 0.69.

4. The strongest results were generally concentrated around slow
   moving-average windows of 30 to 50 days.

5. Very slow moving-average combinations using 150-day and 200-day
   windows generally produced weaker CAGR and Sharpe-ratio results.

6. Parameter optimization produced only modest improvement compared
   with the original MA 20/50 strategy, suggesting that aggressive
   tuning did not create a dramatically superior model.

## Limitations

- Parameters were evaluated on the same dataset used to compare them.
- The project does not yet include an out-of-sample test.
- Trading costs are simplified.
- Slippage and taxes are not modeled separately.
- Selecting the highest historical result may lead to overfitting.
- The strategy remains long or in cash and does not test short exposure.
- The analysis uses one instrument and therefore does not establish
  whether the findings generalize to other asset classes or markets.
- Sharpe ratios assume a zero risk-free rate.
- Performance may be sensitive to the quality and adjustment method of
  the downloaded historical data.

## Conclusion

The parameter optimization showed that NIFTY 50 moving-average strategy
performance was moderately sensitive to the selected fast and slow
windows.

The strongest historical results were concentrated around fast windows
of 5 to 20 days and slow windows of 30 to 50 days. MA 10/50 generated
the highest CAGR, while MA 5/50 ranked among the strongest configurations
by Sharpe ratio. MA 20/30 provided the best drawdown protection.

The presence of several neighbouring configurations with similar
performance is more encouraging than finding one isolated winning
parameter pair. However, all results remain in sample. Therefore, the
analysis does not demonstrate that any configuration will remain
profitable in the future.

The next required step is to freeze the selected parameters and evaluate
them on an unseen out-of-sample period before making stronger claims
about robustness.