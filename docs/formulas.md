# Indicator Formulas

This document describes the mathematical formulas used by each
indicator in QuantLab.  Indicators are listed in
alphabetical order.

All formulas assume a time series indexed by `t` where `t` advances
forward in time (bar by bar).

---

## Average Directional Index (ADX)

ADX is part of Wilder's Directional Movement system.  Directional
movement is extracted from consecutive highs and lows, smoothed,
and normalised by True Range to produce the directional
indicators +DI and −DI.  ADX itself is a smoothed measure of the
gap between them and quantifies trend strength regardless of
direction.

**Directional movement** — for each bar, one of +DM, −DM, or
neither is non-zero:

$$
\text{+DM}_t = \begin{cases} H_t - H_{t-1} & \text{if } H_t - H_{t-1} > L_{t-1} - L_t \text{ and } H_t > H_{t-1} \\ 0 & \text{otherwise} \end{cases}
$$

$$
\text{−DM}_t = \begin{cases} L_{t-1} - L_t & \text{if } L_{t-1} - L_t > H_t - H_{t-1} \text{ and } L_t < L_{t-1} \\ 0 & \text{otherwise} \end{cases}
$$

**True Range** (same definition as ATR):

$$
\text{TR}_t = \max(
    H_t - L_t,\;
    |H_t - C_{t-1}|,\;
    |L_t - C_{t-1}|
)
$$

**Wilder smoothing** — TR, +DM, and −DM are smoothed with an RMA
(`alpha = 1 / n`, `adjust=False`, identical to ATR):

$$
\text{RMA}_t(x) = (1 - \alpha) \cdot \text{RMA}_{t-1}(x) + \alpha \cdot x_t
$$

**Directional indicators and ADX:**

$$
\text{+DI}_t = 100 \cdot \frac{\text{RMA}_t(\text{+DM})}{\text{RMA}_t(\text{TR})}
$$

$$
\text{−DI}_t = 100 \cdot \frac{\text{RMA}_t(\text{−DM})}{\text{RMA}_t(\text{TR})}
$$

$$
\text{DX}_t = 100 \cdot \frac{|\text{+DI}_t - \text{−DI}_t|}{\text{+DI}_t + \text{−DI}_t}
$$

$$
\text{ADX}_t = \text{RMA}_{m}(\text{DX})
$$

| Variable | Meaning |
|----------|---------|
| $H_t$, $L_t$, $C_t$ | High, low, and close at bar `t` |
| $\text{+DM}_t$ / $\text{−DM}_t$ | Upward / downward directional movement |
| $\text{TR}_t$ | True Range |
| $n$ | DI smoothing window (default 14) |
| $m$ | ADX smoothing window over DX (default 14) |
| $\alpha$ | Wilder smoothing factor ($1 / n$) |

### Notes

- The first bar has no previous bar; its directional movement is
  `NaN` and is dropped like other leading `NaN` rows.
- When both movements compete within a bar (higher high AND
  lower low), only the larger one counts.
- `DX` is `NaN` whenever `+DI + −DI` is zero (no dominant
  movement); those rows are dropped and may raise `IndexError`
  if too few valid values remain.
- A zero True Range (flat highs, lows, and closes) makes the DI
  denominators zero and raises `IndexError`.
- All three outputs are bounded to 0–100.  ADX measures trend
  strength only: a strong downtrend produces the same high ADX
  as a strong uptrend, while +DI vs −DI identifies direction.

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

## On-Balance Volume (OBV)

OBV is a cumulative momentum indicator that relates volume to
price movement.  Each bar adds its volume to a running total when
the close rises, subtracts it when the close falls, and leaves
the total unchanged when closes are equal.

$$
\text{OBV}_t = \text{OBV}_{t-1} + \text{sign}(C_t - C_{t-1}) \cdot V_t
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $C_{t-1}$ | Close price at bar `t-1` (previous close) |
| $V_t$ | Volume at bar `t` |
| $\text{sign}(x)$ | $+1$ if $x > 0$, $-1$ if $x < 0$, $0$ if $x = 0$ |

### Notes

- The accumulation runs from the first fetched bar, so the
  `window` parameter controls how much history is included
  rather than a rolling calculation length.
- The first bar has no previous close and produces `NaN`;
  accumulation starts from the second bar.
- Fewer than two bars raises `IndexError`; unlike rolling
  indicators, a window larger than the available data is not an
  error.

---

## Rate of Change (ROC)

ROC measures the percentage change in the closing price over
`n` bars, gauging the strength and direction of momentum.

$$
\text{ROC}_t = \frac{C_t - C_{t-n}}{C_{t-n}} \times 100
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $C_{t-n}$ | Closing price `n` bars ago |
| $n$   | Lookback window (default 9) |

### Notes

- Positive values indicate upward momentum; negative values
  indicate downward momentum.
- The first `n` bars produce `NaN` because there is no close
  `n` bars earlier.
- A close price of exactly zero `n` bars ago makes ROC
  undefined; those rows are dropped like `NaN` rows and may
  raise `IndexError` if too few valid values remain.

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

## Stochastic Oscillator (STOCH)

A momentum indicator that compares the closing price to the high-low
range over `t` periods.

**Raw %K** (pre-smoothing):

$$
K_{raw} = \frac{C_t - L_t}{H_t - L_t} \times 100
$$

| Variable | Meaning |
|----------|---------|
| $C_t$ | Closing price at bar `t` |
| $L_t$ | Lowest low over the window |
| $H_t$ | Highest high over the window |

**%K** = SMA of raw %K over `smooth_k` periods (default 3).

**%D** = SMA of %K over `smooth_d` periods (default 3).

Both %K and %D are clamped to $[0, 100]$.

When `count > 1`, the output is two columns: `%K` and `%D`.

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


