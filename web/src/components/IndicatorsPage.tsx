import { useState } from 'react';

interface IndicatorData {
  name: string;
  description: string;
  formula: string;
  formulaBreakdown: string;
}

const INDICATORS: IndicatorData[] = [
  {
    name: 'ADX',
    description:
      'The Average Directional Index measures trend strength regardless of direction. It ranges from 0 to 100, where values above 25 typically indicate a strong trend. ADX is useful for filtering ranging markets from trending ones, helping you avoid false signals in choppy conditions.',
    formula: 'ADX = 100 × EMA(|+DI − −DI| / (+DI + −DI), period)',
    formulaBreakdown:
      '+DI (Plus Directional Indicator) measures upward momentum. −DI (Minus Directional Indicator) measures downward momentum. The DX (Directional Index) is the absolute difference divided by the sum, smoothed with EMA. ADX is the EMA of DX over the specified period (typically 14).',
  },
  {
    name: 'ATR',
    description:
      'The Average True Range measures market volatility by calculating the average of true ranges over a period. Unlike other volatility indicators, ATR does not indicate direction—only the magnitude of price movement. It is useful for setting stop-loss levels and position sizing.',
    formula: 'TR = max(H−L, |H−Cprev|, |L−Cprev|)\nATR = SMA(TR, period)',
    formulaBreakdown:
      'True Range (TR) is the greatest of: current high minus current low, absolute value of current high minus previous close, or absolute value of current low minus previous close. ATR is the simple moving average of TR over the specified period (typically 14).',
  },
  {
    name: 'AV',
    description:
      'Average Volume smooths volume data over a specified period, making it easier to identify volume spikes and trends. Comparing current volume to the average helps confirm price movements—breakouts on high volume are more reliable than those on low volume.',
    formula: 'AV = SMA(Volume, period)',
    formulaBreakdown:
      'Take the closing volume for each bar and compute the simple moving average over the specified period. This creates a baseline to compare against current volume levels.',
  },
  {
    name: 'BB',
    description:
      'Bollinger Bands consist of a middle band (SMA) and two outer bands set at standard deviations from the middle. They expand during high volatility and contract during low volatility. Price touching the upper band may indicate overbought conditions, while touching the lower band may indicate oversold conditions.',
    formula: 'Middle = SMA(close, period)\nUpper = Middle + (num_std × σ)\nLower = Middle − (num_std × σ)',
    formulaBreakdown:
      'The middle band is a simple moving average (typically 20 periods). The upper and lower bands are calculated by adding and subtracting a multiple of the standard deviation (typically 2) from the middle band. σ is the standard deviation of the closing prices over the period.',
  },
  {
    name: 'CCI',
    description:
      'The Commodity Channel Index measures the difference between the current price and the historical average price. Values above +100 suggest overbought conditions, while values below −100 suggest oversold conditions. Despite its name, CCI works on any asset class, not just commodities.',
    formula: 'CCI = (Typical Price − SMA(Typical Price, period)) / (0.015 × Mean Deviation)',
    formulaBreakdown:
      'Typical Price = (High + Low + Close) / 3. The mean deviation is the average of absolute deviations from the SMA. The constant 0.015 ensures approximately 70–80% of values fall between −100 and +100.',
  },
  {
    name: 'EMA',
    description:
      'The Exponential Moving Average gives more weight to recent prices, making it more responsive to new information than a simple moving average. EMAs are commonly used to identify trend direction and as dynamic support/resistance levels.',
    formula: 'EMA = Close × k + EMAprev × (1 − k)\nk = 2 / (period + 1)',
    formulaBreakdown:
      'The multiplier k (smoothing factor) gives more weight to recent prices. For a 20-period EMA, k = 2/(20+1) ≈ 0.095. The EMA is calculated recursively, starting with the SMA as the initial EMA value.',
  },
  {
    name: 'MACD',
    description:
      'Moving Average Convergence Divergence shows the relationship between two EMAs of different periods. The MACD line crossing above the signal line is bullish; crossing below is bearish. The histogram visualizes the distance between the two lines, showing momentum acceleration or deceleration.',
    formula: 'MACD Line = EMA(fast) − EMA(slow)\nSignal = EMA(MACD Line, signal)\nHistogram = MACD Line − Signal',
    formulaBreakdown:
      'The MACD line is the difference between a fast EMA (typically 12) and slow EMA (typically 26). The signal line is an EMA of the MACD line (typically 9 periods). The histogram shows the divergence between MACD and signal—positive values indicate bullish momentum, negative values indicate bearish momentum.',
  },
  {
    name: 'OBV',
    description:
      'On-Balance Volume accumulates volume on up days and subtracts it on down days, creating a cumulative measure of buying and selling pressure. Rising OBV confirms an uptrend; falling OBV confirms a downtrend. Divergences between OBV and price can signal trend reversals.',
    formula: 'If Close > Closeprev: OBV = OBVprev + Volume\nIf Close < Closeprev: OBV = OBVprev − Volume\nIf Close = Closeprev: OBV = OBVprev',
    formulaBreakdown:
      'OBV starts at zero. Each day, if the close is higher than the previous close, volume is added. If lower, volume is subtracted. If unchanged, OBV remains the same. The smoothing parameter applies an optional moving average to reduce noise.',
  },
  {
    name: 'ROC',
    description:
      'Rate of Change measures the percentage change between the current price and the price N periods ago. It identifies momentum strength and direction. Positive values indicate upward momentum; negative values indicate downward momentum. Extreme values may signal overbought or oversold conditions.',
    formula: 'ROC = ((Close − Closeprev) / Closeprev) × 100',
    formulaBreakdown:
      'Subtract the closing price N periods ago from the current closing price, divide by the closing price N periods ago, and multiply by 100 to get a percentage. The period parameter controls how far back to look.',
  },
  {
    name: 'RSI',
    description:
      'The Relative Strength Index measures the speed and magnitude of recent price changes. It ranges from 0 to 100, where values above 70 typically indicate overbought conditions and values below 30 indicate oversold conditions. RSI is one of the most widely used momentum oscillators.',
    formula: 'RS = Avg Gain / Avg Loss\nRSI = 100 − (100 / (1 + RS))',
    formulaBreakdown:
      'Average Gain is the average of upward price changes over the period. Average Loss is the average of downward price changes (as a positive number). RS (Relative Strength) is their ratio. RSI normalizes RS to a 0–100 scale. The period is typically 14.',
  },
  {
    name: 'RVOL',
    description:
      'Relative Volume compares current volume to the average volume over a specified period. An RVOL of 2.0 means current volume is double the average. High relative volume confirms price movements and can signal institutional activity or significant news events.',
    formula: 'RVOL = Volume / SMA(Volume, period)',
    formulaBreakdown:
      'Divide the current bar\'s volume by the simple moving average of volume over the specified period. Values above 1.0 indicate above-average volume; values below 1.0 indicate below-average volume.',
  },
  {
    name: 'SMA',
    description:
      'The Simple Moving Average calculates the arithmetic mean of closing prices over a specified period. It smooths out price data to identify trend direction. SMAs are commonly used as dynamic support/resistance and in crossover strategies (e.g., 50-day crossing above 200-day).',
    formula: 'SMA = (C1 + C2 + ... + Cn) / n',
    formulaBreakdown:
      'Sum the closing prices for the last n periods and divide by n. Each price in the period has equal weight. Common periods: 20 (short-term), 50 (medium-term), 200 (long-term).',
  },
  {
    name: 'STOCH',
    description:
      'The Stochastic Oscillator compares the closing price to the price range over a period. It consists of two lines: %K (fast) and %D (slow, a smoothed version of %K). Values above 80 indicate overbought conditions; values below 20 indicate oversold conditions.',
    formula: '%K = ((Close − Lowest Low) / (Highest High − Lowest Low)) × 100\n%D = SMA(%K, smooth_k)',
    formulaBreakdown:
      'The highest high and lowest low are calculated over the lookback period. %K shows where the close sits within that range as a percentage. %D is a moving average of %K, providing a smoother signal. The smoothing parameters reduce false signals.',
  },
  {
    name: 'VWAP',
    description:
      'Volume Weighted Average Price calculates the average price weighted by volume, representing the "fair value" of an asset for the day. Institutional traders use VWAP to execute large orders without significantly moving the market. Price above VWAP suggests bullish sentiment; below suggests bearish.',
    formula: 'VWAP = Σ(Price × Volume) / Σ(Volume)',
    formulaBreakdown:
      'For each bar, multiply the typical price (H+L+C)/3 by the volume, accumulate these products, and divide by the cumulative volume. The rolling VWAP applies this over a specified window, resetting or rolling forward.',
  },
];

function IndicatorAccordion({ indicator }: { indicator: IndicatorData }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-slate-200/60 last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between py-4 text-left transition-colors hover:bg-slate-50/50"
      >
        <span className="text-sm font-semibold text-slate-800">
          {indicator.name}
        </span>
        <span
          className={`text-slate-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4 6L8 10L12 6"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      </button>
      {isOpen && (
        <div className="pb-4 animate-fade-in">
          <p className="mb-4 text-sm leading-relaxed text-slate-600">
            {indicator.description}
          </p>
          <div className="rounded-xl bg-slate-900 p-4">
            <p className="mb-2 text-xs font-medium text-emerald-400">
              Formula
            </p>
            <pre className="mb-3 whitespace-pre-wrap font-mono text-xs text-slate-300">
              {indicator.formula}
            </pre>
            <p className="mb-2 text-xs font-medium text-cyan-400">
              Breakdown
            </p>
            <p className="text-xs leading-relaxed text-slate-400">
              {indicator.formulaBreakdown}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export function IndicatorsPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-800">
          Technical <span className="gradient-text">Indicators</span>
        </h1>
        <p className="mt-3 text-base text-slate-500">
          14 indicators with formulas, descriptions, and usage guidance
        </p>
      </div>

      {/* Indicators List */}
      <section className="rounded-2xl border border-slate-200/60 bg-white px-6 shadow-sm">
        <div className="divide-y divide-slate-200/60">
          {INDICATORS.map((ind) => (
            <IndicatorAccordion key={ind.name} indicator={ind} />
          ))}
        </div>
      </section>

      {/* Usage Note */}
      <div className="mt-6 rounded-2xl border border-cyan-200 bg-cyan-50/50 p-4">
        <p className="text-sm text-cyan-700">
          <strong>Note:</strong> When adding a new indicator to QuantLab,
          add it to this page with a description and formula, and ensure
          it is registered in the backtest engine and API schema.
        </p>
      </div>
    </main>
  );
}
