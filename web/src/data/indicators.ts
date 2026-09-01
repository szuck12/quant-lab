export type IndicatorType = 'Momentum' | 'Trend' | 'Volatility' | 'Volume';

export interface ParameterInfo {
  name: string;
  default: number;
  min: number;
  max: number;
  description: string;
}

export interface IndicatorData {
  name: string;
  type: IndicatorType;
  description: string;
  interpretation: string;
  parameters: ParameterInfo[];
  bullishSignals: string[];
  bearishSignals: string[];
  bestFor: string;
  similarTo: string[];
  tips: string[];
  formula: string;
  formulaBreakdown: string;
}

export const INDICATORS: IndicatorData[] = [
  {
    name: 'ADX',
    type: 'Trend',
    description:
      'The Average Directional Index measures trend strength regardless of direction. It ranges from 0 to 100, where values above 25 typically indicate a strong trend.',
    interpretation:
      'ADX does not indicate trend direction—only strength. Values below 20 suggest a weak or nonexistent trend (ranging market). Values between 20–40 suggest a developing trend. Values above 40 suggest a strong trend. Above 60 suggests an extremely strong trend, which is rare.',
    parameters: [
      { name: 'window', default: 14, min: 2, max: 200, description: 'DI smoothing period' },
      { name: 'adx_window', default: 14, min: 2, max: 200, description: 'ADX smoothing period' },
    ],
    bullishSignals: [
      'ADX crosses above 25 (trend emerging)',
      '+DI crosses above −DI (bullish trend)',
      'ADX rising while +DI > −DI (bullish trend strengthening)',
    ],
    bearishSignals: [
      'ADX crosses below 25 (trend weakening)',
      '−DI crosses above +DI (bearish trend)',
      'ADX falling while −DI > +DI (bearish trend strengthening)',
    ],
    bestFor: 'Filtering ranging markets from trending ones. Use ADX to avoid false signals in choppy conditions.',
    similarTo: ['SMA', 'EMA'],
    tips: [
      'Combine ADX with +DI/−DI to determine trend direction',
      'ADX above 25 with +DI > −DI = bullish trend',
      'Use ADX to filter signals from other indicators',
    ],
    formula: 'ADX = 100 × EMA(|+DI − −DI| / (+DI + −DI), period)',
    formulaBreakdown:
      '+DI (Plus Directional Indicator) measures upward momentum. −DI (Minus Directional Indicator) measures downward momentum. The DX is the absolute difference divided by the sum, smoothed with EMA. ADX is the EMA of DX over the specified period.',
  },
  {
    name: 'ATR',
    type: 'Volatility',
    description:
      'The Average True Range measures market volatility by calculating the average of true ranges over a period. It does not indicate direction—only the magnitude of price movement.',
    interpretation:
      'Higher ATR values indicate higher volatility; lower values indicate lower volatility. ATR is useful for setting stop-loss levels (e.g., 2× ATR below entry) and position sizing (risk a fixed percentage of capital per trade).',
    parameters: [
      { name: 'window', default: 14, min: 2, max: 200, description: 'Lookback period for averaging' },
    ],
    bullishSignals: [
      'ATR expanding after a period of contraction (breakout imminent)',
      'ATR spike on high volume (potential trend start)',
    ],
    bearishSignals: [
      'ATR declining (volatility decreasing, trend may be ending)',
      'ATR spike during downtrend (panic selling)',
    ],
    bestFor: 'Setting stop-loss levels, position sizing, and identifying volatility breakouts.',
    similarTo: ['BB'],
    tips: [
      'Use ATR to set trailing stops (e.g., 2× ATR)',
      'Compare current ATR to historical ATR for context',
      'ATR is absolute, not percentage—compare across similar-priced assets',
    ],
    formula: 'TR = max(H−L, |H−Cprev|, |L−Cprev|)\nATR = SMA(TR, period)',
    formulaBreakdown:
      'True Range (TR) is the greatest of: current high minus current low, absolute value of current high minus previous close, or absolute value of current low minus previous close. ATR is the simple moving average of TR over the specified period.',
  },
  {
    name: 'AV',
    type: 'Volume',
    description:
      'Average Volume smooths volume data over a specified period, making it easier to identify volume spikes and trends.',
    interpretation:
      'Comparing current volume to the average helps confirm price movements. Breakouts on high volume (2× average or more) are more reliable than those on low volume. Volume spikes often precede significant price moves.',
    parameters: [
      { name: 'window', default: 20, min: 2, max: 500, description: 'Lookback period for averaging' },
    ],
    bullishSignals: [
      'Volume spikes above 2× average on up days (buying pressure)',
      'Rising volume on price increase (trend confirmation)',
    ],
    bearishSignals: [
      'Volume spikes above 2× average on down days (selling pressure)',
      'Declining volume on price increase (weak trend)',
    ],
    bestFor: 'Confirming breakouts and identifying accumulation/distribution phases.',
    similarTo: ['OBV', 'RVOL'],
    tips: [
      'Volume should confirm price—a breakout without volume is suspect',
      'Look for volume climaxes (extreme spikes) as potential reversals',
    ],
    formula: 'AV = SMA(Volume, period)',
    formulaBreakdown:
      'Take the closing volume for each bar and compute the simple moving average over the specified period. This creates a baseline to compare against current volume levels.',
  },
  {
    name: 'BB',
    type: 'Volatility',
    description:
      'Bollinger Bands consist of a middle band (SMA) and two outer bands set at standard deviations from the middle. They expand during high volatility and contract during low volatility.',
    interpretation:
      'Price touching the upper band may indicate overbought conditions; touching the lower band may indicate oversold conditions. However, in strong trends, price can "ride the bands" for extended periods. The bandwidth (distance between bands) indicates volatility level.',
    parameters: [
      { name: 'window', default: 20, min: 2, max: 500, description: 'SMA period for middle band' },
      { name: 'num_std', default: 2.0, min: 0.5, max: 5.0, description: 'Standard deviations for outer bands' },
    ],
    bullishSignals: [
      'Price bounces off lower band (support)',
      'Bands contracting after expansion (squeeze before breakout)',
      'Price crosses above middle band from below',
    ],
    bearishSignals: [
      'Price rejected at upper band (resistance)',
      'Bands contracting after expansion (squeeze before breakdown)',
      'Price crosses below middle band from above',
    ],
    bestFor: 'Identifying volatility conditions and potential overbought/oversold levels.',
    similarTo: ['ATR'],
    tips: [
      'The "Bollinger squeeze" (contracting bands) often precedes big moves',
      'Don\'t automatically sell at upper band in strong uptrends',
      'Use bandwidth to gauge volatility before entering trades',
    ],
    formula: 'Middle = SMA(close, period)\nUpper = Middle + (num_std × σ)\nLower = Middle − (num_std × σ)',
    formulaBreakdown:
      'The middle band is a simple moving average (typically 20 periods). The upper and lower bands are calculated by adding and subtracting a multiple of the standard deviation (typically 2) from the middle band.',
  },
  {
    name: 'CCI',
    type: 'Momentum',
    description:
      'The Commodity Channel Index measures the difference between the current price and the historical average price. Despite its name, it works on any asset class.',
    interpretation:
      'Values above +100 suggest overbought conditions; values below −100 suggest oversold conditions. The zero line separates bullish and bearish momentum. CCI can also be used to identify divergences and trend direction.',
    parameters: [
      { name: 'window', default: 20, min: 2, max: 200, description: 'Lookback period' },
    ],
    bullishSignals: [
      'CCI crosses above −100 (exiting oversold)',
      'CCI crosses above zero (bullish momentum)',
      'Bullish divergence: price lower low, CCI higher low',
    ],
    bearishSignals: [
      'CCI crosses below +100 (exiting overbought)',
      'CCI crosses below zero (bearish momentum)',
      'Bearish divergence: price higher high, CCI lower high',
    ],
    bestFor: 'Identifying overbought/oversold conditions and trend direction in any market.',
    similarTo: ['RSI', 'STOCH'],
    tips: [
      'CCI is more volatile than RSI—use wider thresholds (+200/−200) in trending markets',
      'Combine with ADX to confirm trend strength',
    ],
    formula: 'CCI = (TP − SMA(TP, period)) / (0.015 × Mean Deviation)',
    formulaBreakdown:
      'Typical Price (TP) = (High + Low + Close) / 3. The mean deviation is the average of absolute deviations from the SMA. The constant 0.015 ensures approximately 70–80% of values fall between −100 and +100.',
  },
  {
    name: 'EMA',
    type: 'Trend',
    description:
      'The Exponential Moving Average gives more weight to recent prices, making it more responsive to new information than a simple moving average.',
    interpretation:
      'Price above EMA suggests bullish momentum; price below suggests bearish momentum. EMA crossovers (fast crossing slow) signal potential trend changes. EMA acts as dynamic support/resistance in trending markets.',
    parameters: [
      { name: 'window', default: 20, min: 2, max: 500, description: 'Lookback period' },
    ],
    bullishSignals: [
      'Price crosses above EMA (bullish signal)',
      'Short EMA crosses above long EMA (golden cross)',
      'Price bounces off EMA as support',
    ],
    bearishSignals: [
      'Price crosses below EMA (bearish signal)',
      'Short EMA crosses below long EMA (death cross)',
      'Price rejected at EMA as resistance',
    ],
    bestFor: 'Trend following, dynamic support/resistance, and crossover strategies.',
    similarTo: ['SMA', 'ADX'],
    tips: [
      'Common periods: 9 (short), 21 (medium), 50 (long), 200 (very long)',
      'The 50/200 EMA crossover is a major long-term signal',
      'EMA works better than SMA in fast-moving markets',
    ],
    formula: 'EMA = Close × k + EMAprev × (1 − k)\nk = 2 / (period + 1)',
    formulaBreakdown:
      'The multiplier k (smoothing factor) gives more weight to recent prices. For a 20-period EMA, k ≈ 0.095. The EMA is calculated recursively, starting with the SMA as the initial value.',
  },
  {
    name: 'MACD',
    type: 'Momentum',
    description:
      'Moving Average Convergence Divergence shows the relationship between two EMAs of different periods. It consists of the MACD line, signal line, and histogram.',
    interpretation:
      'The MACD line crossing above the signal line is bullish; crossing below is bearish. The histogram shows momentum acceleration (growing bars) or deceleration (shrinking bars). Divergences between MACD and price can signal trend reversals.',
    parameters: [
      { name: 'fast', default: 12, min: 2, max: 100, description: 'Fast EMA period' },
      { name: 'slow', default: 26, min: 5, max: 200, description: 'Slow EMA period' },
      { name: 'signal', default: 9, min: 2, max: 50, description: 'Signal line period' },
    ],
    bullishSignals: [
      'MACD crosses above signal line (bullish crossover)',
      'MACD crosses above zero (bullish momentum)',
      'Histogram turns positive and growing',
      'Bullish divergence: price lower low, MACD higher low',
    ],
    bearishSignals: [
      'MACD crosses below signal line (bearish crossover)',
      'MACD crosses below zero (bearish momentum)',
      'Histogram turns negative and growing',
      'Bearish divergence: price higher high, MACD lower high',
    ],
    bestFor: 'Identifying trend changes, momentum shifts, and divergence signals.',
    similarTo: ['RSI', 'EMA'],
    tips: [
      'The zero line crossover is a stronger signal than signal line crossover',
      'Look for histogram divergence before price reverses',
      'MACD works best in trending markets, not ranging ones',
    ],
    formula: 'MACD = EMA(fast) − EMA(slow)\nSignal = EMA(MACD, signal)\nHistogram = MACD − Signal',
    formulaBreakdown:
      'The MACD line is the difference between a fast EMA (12) and slow EMA (26). The signal line is an EMA of the MACD line (9 periods). The histogram shows the divergence between MACD and signal.',
  },
  {
    name: 'OBV',
    type: 'Volume',
    description:
      'On-Balance Volume accumulates volume on up days and subtracts it on down days, creating a cumulative measure of buying and selling pressure.',
    interpretation:
      'Rising OBV confirms an uptrend; falling OBV confirms a downtrend. Divergences between OBV and price can signal trend reversals. OBV can identify accumulation (smart money buying) before price moves.',
    parameters: [
      { name: 'window', default: 30, min: 2, max: 500, description: 'Smoothing period' },
    ],
    bullishSignals: [
      'OBV rising while price is flat (accumulation)',
      'OBV makes higher high with price (trend confirmation)',
      'OBV crosses above its moving average',
    ],
    bearishSignals: [
      'OBV falling while price is flat (distribution)',
      'OBV makes lower high with price (divergence)',
      'OBV crosses below its moving average',
    ],
    bestFor: 'Confirming trends and identifying accumulation/distribution before price moves.',
    similarTo: ['AV', 'RVOL'],
    tips: [
      'OBV is cumulative—focus on the trend, not absolute values',
      'Look for OBV divergence as an early warning signal',
    ],
    formula: 'If C > Cprev: OBV = OBVprev + Vol\nIf C < Cprev: OBV = OBVprev − Vol\nIf C = Cprev: OBV = OBVprev',
    formulaBreakdown:
      'OBV starts at zero. Each day, if the close is higher, volume is added. If lower, volume is subtracted. If unchanged, OBV remains the same.',
  },
  {
    name: 'ROC',
    type: 'Momentum',
    description:
      'Rate of Change measures the percentage change between the current price and the price N periods ago. It identifies momentum strength and direction.',
    interpretation:
      'Positive values indicate upward momentum; negative values indicate downward momentum. Extreme values may signal overbought or oversold conditions. ROC crossing zero indicates a momentum shift.',
    parameters: [
      { name: 'window', default: 9, min: 2, max: 200, description: 'Lookback period' },
    ],
    bullishSignals: [
      'ROC crosses above zero (bullish momentum)',
      'ROC rises from negative to positive (momentum shift)',
      'ROC accelerating upward (strengthening trend)',
    ],
    bearishSignals: [
      'ROC crosses below zero (bearish momentum)',
      'ROC falls from positive to negative (momentum shift)',
      'ROC decelerating downward (weakening trend)',
    ],
    bestFor: 'Measuring momentum strength and identifying overbought/oversold extremes.',
    similarTo: ['RSI', 'MACD'],
    tips: [
      'Shorter periods (5–10) for short-term trading, longer (20–50) for swing trading',
      'ROC works well combined with moving average filters',
    ],
    formula: 'ROC = ((Close − Closeprev) / Closeprev) × 100',
    formulaBreakdown:
      'Subtract the closing price N periods ago from the current closing price, divide by the closing price N periods ago, and multiply by 100 to get a percentage.',
  },
  {
    name: 'RSI',
    type: 'Momentum',
    description:
      'The Relative Strength Index measures the speed and magnitude of recent price changes. It ranges from 0 to 100, where values above 70 typically indicate overbought conditions and values below 30 indicate oversold conditions.',
    interpretation:
      'RSI oscillates between 0 and 100. The 50 level separates bullish and bearish momentum. In strong uptrends, RSI can stay above 70 for extended periods. In strong downtrends, RSI can stay below 30. Divergences between RSI and price often precede reversals.',
    parameters: [
      { name: 'window', default: 14, min: 2, max: 200, description: 'Lookback period' },
    ],
    bullishSignals: [
      'RSI crosses above 30 (exiting oversold)',
      'RSI crosses above 50 (bullish momentum)',
      'Bullish divergence: price lower low, RSI higher low',
      'RSI forms double bottom at 30 level',
    ],
    bearishSignals: [
      'RSI crosses below 70 (exiting overbought)',
      'RSI crosses below 50 (bearish momentum)',
      'Bearish divergence: price higher high, RSI lower high',
      'RSI forms double top at 70 level',
    ],
    bestFor: 'Identifying overbought/oversold conditions and momentum reversals.',
    similarTo: ['STOCH', 'CCI', 'ROC'],
    tips: [
      'Use RSI with trend direction for better signals',
      'In strong trends, RSI can stay overbought/oversold for extended periods',
      'Look for divergences for early reversal signals',
      'RSI 40–80 in uptrends, 20–60 in downtrends',
    ],
    formula: 'RS = Avg Gain / Avg Loss\nRSI = 100 − (100 / (1 + RS))',
    formulaBreakdown:
      'Average Gain is the average of upward price changes over the period. Average Loss is the average of downward price changes (as a positive number). RS is their ratio. RSI normalizes RS to a 0–100 scale.',
  },
  {
    name: 'RVOL',
    type: 'Volume',
    description:
      'Relative Volume compares current volume to the average volume over a specified period. An RVOL of 2.0 means current volume is double the average.',
    interpretation:
      'RVOL > 1.0 indicates above-average volume; RVOL < 1.0 indicates below-average volume. High RVOL confirms price movements and can signal institutional activity or significant news events. Volume spikes often precede price moves.',
    parameters: [
      { name: 'window', default: 10, min: 2, max: 200, description: 'Average volume period' },
    ],
    bullishSignals: [
      'RVOL > 2.0 on up days (strong buying pressure)',
      'RVOL spike at support level (potential reversal)',
    ],
    bearishSignals: [
      'RVOL > 2.0 on down days (strong selling pressure)',
      'RVOL spike at resistance level (potential reversal)',
    ],
    bestFor: 'Confirming breakouts and identifying unusual trading activity.',
    similarTo: ['AV', 'OBV'],
    tips: [
      'RVOL > 2.0 is significant; > 3.0 is very significant',
      'Combine RVOL with price action for best results',
    ],
    formula: 'RVOL = Volume / SMA(Volume, period)',
    formulaBreakdown:
      'Divide the current bar\'s volume by the simple moving average of volume over the specified period. Values above 1.0 indicate above-average volume.',
  },
  {
    name: 'SMA',
    type: 'Trend',
    description:
      'The Simple Moving Average calculates the arithmetic mean of closing prices over a specified period. It smooths out price data to identify trend direction.',
    interpretation:
      'Price above SMA suggests bullish momentum; price below suggests bearish momentum. SMA crossovers (short crossing long) signal potential trend changes. SMA acts as dynamic support/resistance in trending markets.',
    parameters: [
      { name: 'window', default: 50, min: 2, max: 500, description: 'Lookback period' },
    ],
    bullishSignals: [
      'Price crosses above SMA (bullish signal)',
      'Short SMA crosses above long SMA (golden cross)',
      'Price bounces off SMA as support',
    ],
    bearishSignals: [
      'Price crosses below SMA (bearish signal)',
      'Short SMA crosses below long SMA (death cross)',
      'Price rejected at SMA as resistance',
    ],
    bestFor: 'Trend following, dynamic support/resistance, and crossover strategies.',
    similarTo: ['EMA', 'ADX'],
    tips: [
      'Common periods: 20 (short), 50 (medium), 200 (long)',
      'The 50/200 SMA crossover is a major long-term signal',
      'SMA is slower to react than EMA—better for longer timeframes',
    ],
    formula: 'SMA = (C1 + C2 + ... + Cn) / n',
    formulaBreakdown:
      'Sum the closing prices for the last n periods and divide by n. Each price in the period has equal weight.',
  },
  {
    name: 'STOCH',
    type: 'Momentum',
    description:
      'The Stochastic Oscillator compares the closing price to the price range over a period. It consists of two lines: %K (fast) and %D (slow, a smoothed version of %K).',
    interpretation:
      'Values above 80 indicate overbought conditions; values below 20 indicate oversold conditions. The %K/%D crossover provides trading signals. In trending markets, the stochastic can stay overbought/oversold for extended periods.',
    parameters: [
      { name: 'window', default: 14, min: 2, max: 200, description: 'Lookback period' },
      { name: 'smooth_k', default: 3, min: 1, max: 50, description: '%K smoothing' },
      { name: 'smooth_d', default: 3, min: 1, max: 50, description: '%D smoothing' },
    ],
    bullishSignals: [
      '%K crosses above %D in oversold zone (< 20)',
      'Stochastic exits oversold zone',
      'Bullish divergence: price lower low, stochastic higher low',
    ],
    bearishSignals: [
      '%K crosses below %D in overbought zone (> 80)',
      'Stochastic exits overbought zone',
      'Bearish divergence: price higher high, stochastic lower high',
    ],
    bestFor: 'Identifying overbought/oversold conditions and short-term reversals.',
    similarTo: ['RSI', 'CCI'],
    tips: [
      'Use wider thresholds (80/20) in trending markets',
      'Combine with trend filters for better results',
      'The faster %K line is more sensitive; the slower %D is smoother',
    ],
    formula: '%K = ((Close − Low) / (High − Low)) × 100\n%D = SMA(%K, smooth_k)',
    formulaBreakdown:
      'The highest high and lowest low are calculated over the lookback period. %K shows where the close sits within that range as a percentage. %D is a moving average of %K, providing a smoother signal.',
  },
  {
    name: 'VWAP',
    type: 'Volume',
    description:
      'Volume Weighted Average Price calculates the average price weighted by volume, representing the "fair value" of an asset for the day.',
    interpretation:
      'Price above VWAP suggests bullish sentiment (buyers in control); price below suggests bearish sentiment (sellers in control). Institutional traders use VWAP to execute large orders without significantly moving the market.',
    parameters: [
      { name: 'window', default: 20, min: 2, max: 500, description: 'Rolling period' },
    ],
    bullishSignals: [
      'Price crosses above VWAP (bullish control)',
      'Price bounces off VWAP as support',
      'VWAP trending upward',
    ],
    bearishSignals: [
      'Price crosses below VWAP (bearish control)',
      'Price rejected at VWAP as resistance',
      'VWAP trending downward',
    ],
    bestFor: 'Intraday trading, identifying fair value, and institutional order execution.',
    similarTo: ['AV', 'OBV'],
    tips: [
      'VWAP is most useful for intraday trading',
      'The first touch of VWAP often acts as support/resistance',
      'Reset VWAP at the start of each trading day',
    ],
    formula: 'VWAP = Σ(Price × Volume) / Σ(Volume)',
    formulaBreakdown:
      'For each bar, multiply the typical price (H+L+C)/3 by the volume, accumulate these products, and divide by the cumulative volume.',
  },
];

export const INDICATOR_TYPES: IndicatorType[] = ['Momentum', 'Trend', 'Volatility', 'Volume'];

export const TYPE_COLORS: Record<IndicatorType, { bg: string; text: string; border: string }> = {
  Momentum: { bg: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-200' },
  Trend: { bg: 'bg-cyan-100', text: 'text-cyan-700', border: 'border-cyan-200' },
  Volatility: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
  Volume: { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-200' },
};
