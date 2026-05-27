# Indicator Formulas

This document describes the mathematical formulas used by each
indicator in quant_indicators.  Indicators are listed in
alphabetical order.

All formulas assume a time series indexed by `t` where `t` advances
forward in time (bar by bar).

---

## Average True Range (ATR)

ATR measures market volatility by computing the Wilder-smoothed
average of the True Range over a lookback window.  Higher values
indicate greater volatility.

$$
\begin{aligned}
\text{TR}_t &= \max(
    H_t - L_t,\;
    |H_t - C_{t-1}|,\;
    |L_t - C_{t-1}|
) \\[4pt]
\text{ATR}_t &= \text{TR}_t \quad \text{if } t = 1 \\
\text{ATR}_t &= \text{ATR}_{t-1} \times (1 - \alpha) +
              \text{TR}_t \times \alpha \quad \text{otherwise}
\end{aligned}
$$

Where $\alpha = 1 / \text{window}$ (Wilder smoothing).

| Variable | Meaning |
|----------|---------|
| $H_t$ | High price at bar `t` |
| $L_t$ | Low price at bar `t` |
| $C_{t-1}$ | Close price at bar `t-1` (previous close) |
| $\text{TR}_t$ | True Range at bar `t` |
| $\alpha$ | Smoothing factor ($1 / \text{window}$) |

### Notes

- The first TR value uses only the `high - low` spread because
  there is no previous close, so ATR is always defined for the
  first bar.
- Wilder smoothing (`RMA`) matches the same algorithm used in
  RSI — an EMA with `alpha = 1 / window`.

---

## Average Volume (AV)

AV is the simple rolling mean of volume — the same SMA calculation
applied to volume data instead of closing prices.

$$
\text{AV}_t = \frac{1}{n} \sum_{i=0}^{n-1} V_{t-i}
$$

| Variable | Meaning |
|----------|---------|
| $V_t$ | Volume at bar `t` |
| $n$   | Window (default 20) |

### Notes

- Zero-volume windows produce `AV = 0.0` (a valid result, unlike
  VWAP which would divide by zero).

---

## Bollinger Bands (BB)

Bollinger Bands consist of a middle band (SMA) and two outer bands
placed `k` standard deviations away.  The standard deviation uses
population normalisation (`ddof=0`), matching TradingView's
`ta.bb()`.

$$
\text{Middle}_t = \text{SMA}_n(C_t) = \frac{1}{n} \sum_{i=0}^{n-1} C_{t-i}
$$

$$
\sigma_t = \sqrt{\frac{1}{n} \sum_{i=0}^{n-1} \left( C_{t-i} - \text{Middle}_t \right)^2 }
$$

$$
\text{Upper}_t = \text{Middle}_t + k \cdot \sigma_t
$$

$$
\text{Lower}_t = \text{Middle}_t - k \cdot \sigma_t
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $n$   | Window for SMA and standard deviation (default 20) |
| $k$   | Number of standard deviations (`num_std`, default 2.0) |
| $\sigma_t$ | Population standard deviation of the last `n` closes |
| $\text{Middle}_t$ | SMA of closing prices |
| $\text{Upper}_t$ | Upper band |
| $\text{Lower}_t$ | Lower band |

### Notes

- The population standard deviation (`ddof=0`) divides by `n`
  rather than `n-1`, producing wider bands than the sample
  standard deviation.
- The three bands are returned as a tuple `(Upper, Middle, Lower)`.

---

## Exponential Moving Average (EMA)

The EMA applies exponentially decaying weights to past prices,
giving more importance to recent observations.  This implementation
uses the span-based formula with `adjust=False`.

$$
\alpha = \frac{2}{n + 1}
$$

$$
\text{EMA}_t = \alpha \cdot C_t + (1 - \alpha) \cdot \text{EMA}_{t-1}
$$

The seed value is the first closing price:

$$
\text{EMA}_1 = C_1
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $n$   | Span of the EMA (the `window` parameter) |
| $\alpha$ | Smoothing factor, derived from the span |

With `adjust=False` in pandas, the EMA is computed recursively:
the first value is set to `C_1` and each subsequent value is a
weighted combination of the current price and the previous EMA.
This matches the standard definition used in TradingView.

---

## Moving Average Convergence Divergence (MACD)

MACD shows the relationship between two exponential moving
averages of the closing price.  It produces three time series:
the MACD line, the signal line, and the histogram.

$$
\begin{aligned}
\text{MACD Line}_t &= \text{EMA}_{\text{fast}}(C_t) - \text{EMA}_{\text{slow}}(C_t) \\
\text{Signal Line}_t &= \text{EMA}_{\text{signal}}(\text{MACD Line}_t) \\
\text{Histogram}_t &= \text{MACD Line}_t - \text{Signal Line}_t
\end{aligned}
$$

Each EMA uses the span-based formula described in the EMA section
above with `adjust=False`.

| Variable | Meaning |
|----------|---------|
| $\text{EMA}_{\text{fast}}$ | EMA with span = `fast` (default 12) |
| $\text{EMA}_{\text{slow}}$ | EMA with span = `slow` (default 26) |
| $\text{EMA}_{\text{signal}}$ | EMA of the MACD line with span = `signal` (default 9) |

### Notes

- The histogram is exactly `MACD Line − Signal Line` by definition.
- A positive histogram means the MACD line is above the signal
  line (bullish momentum); negative means the opposite.

---

## Relative Strength Index (RSI)

RSI measures the magnitude of recent price changes to evaluate
overbought or oversold conditions.  This implementation uses
**Wilder smoothing** (also called RMA — running moving average)
with `alpha = 1 / n`, matching TradingView's default `ta.rsi()`.

$$
\Delta_t = C_t - C_{t-1}
$$

$$
G_t = \max(\Delta_t, 0), \quad L_t = \max(-\Delta_t, 0)
$$

$$
\text{AvgGain}_t = \frac{1}{n} \cdot G_t + \left(1 - \frac{1}{n}\right) \cdot \text{AvgGain}_{t-1}
$$

$$
\text{AvgLoss}_t = \frac{1}{n} \cdot L_t + \left(1 - \frac{1}{n}\right) \cdot \text{AvgLoss}_{t-1}
$$

$$
RS_t = \frac{\text{AvgGain}_t}{\text{AvgLoss}_t}
$$

$$
\text{RSI}_t = 100 - \frac{100}{1 + RS_t}
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $n$   | Lookback window |
| $\Delta_t$ | Period-over-period price change |
| $G_t$ | Gain (positive changes only) |
| $L_t$ | Loss (negative changes, expressed as a positive value) |
| $\text{AvgGain}_t$ | Exponentially smoothed average gain (Wilder) |
| $\text{AvgLoss}_t$ | Exponentially smoothed average loss (Wilder) |
| $RS_t$ | Ratio of average gain to average loss |
| $\text{RSI}_t$ | Relative Strength Index, bounded 0–100 |

### Notes

- The first row of the RSI is always `NaN` because the seed values
  of `AvgGain` and `AvgLoss` are zero, producing `0 / 0`.
- A valid non-`NaN` value appears after at least one price change.
- If all price changes are zero over the window, `RS` is
  undefined (`0 / 0`) and an `IndexError` is raised.

---

## Relative Volume (RVOL)

RVOL compares the current bar's volume to its rolling average.
Values above 1.0 mean volume is higher than the recent average;
below 1.0 means lower.

$$
\text{RVOL}_t = \frac{V_t}{\text{AV}_t}
$$

Where $\text{AV}_t$ is the Average Volume (rolling mean of volume)
as defined in the AV section above.

| Variable | Meaning |
|----------|---------|
| $V_t$ | Volume at bar `t` |
| $\text{AV}_t$ | Average Volume over the window (default 10) |

### Notes

- With `window=1`, `AV_t = V_t` and `RVOL_t = 1.0` exactly
  (a value divided by itself).
- All-zero volume over the window produces `NaN` (division by
  zero) and raises `IndexError`.

---

## Simple Moving Average (SMA)

The SMA is the arithmetic mean of the closing price over the last
`n` bars.

$$
\text{SMA}_t = \frac{1}{n} \sum_{i=0}^{n-1} C_{t-i}
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $n$   | Window (number of bars) |

The first `n-1` bars produce `NaN` because there are not enough
prior bars to fill the window.

---

## Volume Weighted Average Price (VWAP)

VWAP is the ratio of the price-volume sum to the volume sum over
a rolling window.  It reflects the average price weighted by
trading volume.

$$
\text{TP}_t = \frac{H_t + L_t + C_t}{3}
$$

$$
\text{VWAP}_t = \frac{\sum_{i=0}^{n-1} \text{TP}_{t-i} \cdot V_{t-i}}
                       {\sum_{i=0}^{n-1} V_{t-i}}
$$

| Variable | Meaning |
|----------|---------|
| $H_t$ | High price at bar `t` |
| $L_t$ | Low price at bar `t` |
| $C_t$ | Close price at bar `t` |
| $V_t$ | Volume at bar `t` |
| $\text{TP}_t$ | Typical Price |
| $n$   | Window (default 20) |

### Notes

- Zero total volume over the window produces `NaN` (division by
  zero) and raises `IndexError`.


