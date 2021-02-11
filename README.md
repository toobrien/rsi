## Validity of the RSI as an "overbought/oversold" indicator

### Introduction

The RSI, or relative strength index, is a indicator for financial time series that ostensibly measures the quality of being "overbought" or "oversold". The indicator's value is a normalized ratio of recent gains to losses ([calculation](https://en.wikipedia.org/wiki/Relative_strength_index#Calculation)), and can be thought of as the "momentum" of price, scored from 0 to 100. Traditionally, an asset is thought to be "overbought" when its RSI value rises above 70 and "oversold" when the RSI falls below 30.

Because the RSI is proportional to the magnitude and frequency of gains or losses, calling extreme values "oversold" or "overbought" implies that extreme price moves are likely to reverse. Accordingly, traders often use the RSI as a signal in mean reversion strategies. But does an extreme RSI value imply a high likelihood of a reversal in an asset's price movements?

### Procedure

To test this question, I first downloaded a large universe of securities from the NYSE an NASDAQ exchanges. Overall, the test includes about 10,000 securities out of the 14,000 or so listed on these exchanges. Each security is represented as up to 10,000 days of OHLC data. For each security, I simulate short trades, entered when the RSI reaches an arbitrary "overbought" level and exited at an arbitrary "neutral" level, as well as long trades to test the "oversold" levels. For each of six strategies, I generate as many trades as possible from each security:

type |enter|exit
----|----|----
short|70|50
short|80|50
short|90|50
long|30|50
long|20|50
long|10|50

For each security, I also generate a second set of trades as a "control group". The methodology involves several steps:

1. Estimating the return distribution of the security
1. Using a random walk, produce a time series of equal length to the original security's returns.
1. Calculate the RSI for these synthetic returns
1. Enter trades on the original security, using the synthetic security's RSI

The synthetic returns are similar to the original security's returns, but random. The synthetic RSI, when applied to the original security's returns, has no meaning, but yields reasonably random entry and exit signals for the control trades. The rough similarity between the original RSI and the synthetic RSI can be assessed visually in the following screenshot. The top subpanel holds the original RSI, and the bottom holds the synthetic series.

![sample data](https://user-images.githubusercontent.com/5386472/107602385-1e49d900-6bde-11eb-83f9-e901fba389ad.png)

To produce the results, the trades are aggregated into twelve groups, six for trades generated from the original series and six for the control group trades. I track four performance measures for each set of trades:

1. mae: maximum adverse excursion, or the maximum drawdown, as percentage of the original entry price.
1. mfe: maximum favorable excursion, or the maximum open profit, as percentage of the original entry price.
1. pnl: profit and loss, the percentage return on the original entry price at the end of the trade.
1. duration: the length, in days, of the trade.

The confidence intervals for these measures can be used to determine whether the RSI generated trades fare any more profitably than the control group trades, which are entered on random signals.

## Results

For mae, mfe, and pnl, the results are expressed as mean, standard deviation, and 99% confidence interval. All units are expressed as continuously compounded percentage return from the opening price level. For duration, the mean and standard deviation are given. The units are days.

group|type|enter|exit|samples|mae|mfe|pnl|duration
---------------|---------------|---------------|---------------|---------------|---------------|---------------|---------------|---------------
experiment|short|70|50|165134|0.049, 0.101, (0.048999, 0.049001)|0.037, 0.057, (0.036999, 0.037001)|0.004, 0.108, (0.003999, 0.004001)|22.829, 16.129
experiment|short|80|50|34799|0.063, 0.137, (0.062996, 0.063004)|0.055, 0.088, (0.054998, 0.055002)|0.012, 0.152, (0.011996, 0.012004)|25.478, 16.822
experiment|short|90|50|2447|0.089, 0.21, (0.088979, 0.089021)|0.138, 0.201, (0.13798, 0.13802)|0.075, 0.289, (0.074971, 0.075029)|28.044, 21.029
experiment|long|30|50|129893|0.045, 0.097, (0.044999, 0.045001)|0.059, 0.078, (0.058999, 0.059001)|0.016, 0.122, (0.015998, 0.016002)|22.136, 15.353
experiment|long|20|50|26480|0.057, 0.113, (0.056997, 0.057003)|0.083, 0.121, (0.082996, 0.083004)|0.028, 0.165, (0.027995, 0.028005)|26.455, 16.288
experiment|long|10|50|1334|0.062, 0.13, (0.061982, 0.062018)|0.165, 0.276, (0.164962, 0.165038)|0.099, 0.306, (0.098958, 0.099042)|30.803, 20.441
control|short|70|50|131586|0.057, 0.096, (0.056999, 0.057001)|0.041, 0.074, (0.040999, 0.041001)|-0.011, 0.123, (-0.011002, -0.010998)|24.437, 17.668
control|short|80|50|24317|0.07, 0.127, (0.069996, 0.070004)|0.048, 0.087, (0.047997, 0.048003)|-0.015, 0.154, (-0.015005, -0.014995)|26.25, 17.889
control|short|90|50|1238|0.187, 1.331, (0.186811, 0.187189)|0.056, 0.117, (0.055983, 0.056017)|-0.068, 0.704, (-0.0681, -0.0679)|15.182, 12.207
control|long|30|50|83133|0.044, 0.079, (0.043999, 0.044001)|0.056, 0.095, (0.055998, 0.056002)|0.008, 0.128, (0.007998, 0.008002)|28.116, 19.239
control|long|20|50|5983|0.042, 0.08, (0.041995, 0.042005)|0.052, 0.092, (0.051994, 0.052006)|0.007, 0.131, (0.006992, 0.007008)|28.337, 21.261
control|long|10|50|121|0.01, 0.048, (0.009978, 0.010022)|0.017, 0.071, (0.016968, 0.017032)|0.003, 0.085, (0.002961, 0.003039)|10.73, 9.82

## Conclusion

Perhaps owing to an upward bias in recent stock returns, the control group longs performed slightly better than break even, while the shorts performed considerably worse. The trade duration, being proportional from the distance between entry and exit levels, effected greater profits and losses, accordingly. The experimental group, by contract, profited both long and short. Once again, the performance was proportional to the distance between entry and exit RSI levels. The 90, short trade had the second highest mean return (7.5%) and the 10, long trade had the best returns of all groups (9.9%). Differences at every level were significant according to the 99% confidence interval.

Although the experimental group RSI trades were profitable at the most extreme levels (90 short, 10 long), they were substantially less profitable at the 70 and 30 levels most commonly used by traders, with a mean profit of 0.4% and 1.6%, respectively. Furthermore, maximum adverse excursion was substantially higher than the returns, and higher than the maximum favorable excursion for the 70 and 80 short trades. Of the short trades, only the 90 level provided favorable reward-to-risk, although even this trade's pnl was worse than its mae. On the long side, all three trades provided favorable reward-to-risk when comparing mae to mfe, although mae still exceeded pnl except at the most extreme level (10).

In summary, the RSI provided better-than-random signals for price reversals at each level tested, and the signal was better at more extreme levels. However, the reward-to-risk characteristics of the short, "oversold" trades are not favorable, except at the most extreme level. On the long side, the signal is better from a reward-to-risk perspective, though this may be explained by market bias. It is worth noting that the most extreme levels (90, 10) occur relatively rarely, and the more commonly used "overbought" and "oversold" levels (70 and 30, respectively) did not have favorable pnl to mae.
