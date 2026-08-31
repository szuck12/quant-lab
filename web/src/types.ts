export interface ParamInfo {
  name: string;
  type: string;
  default: number;
  min?: number;
  max?: number;
}

export interface IndicatorInfo {
  name: string;
  params: ParamInfo[];
  components: string[];
}

export interface ConditionRequest {
  indicator: string;
  params: Record<string, number>;
  component?: string | null;
  operator: string;
  value: number;
  interval: string;
}

export interface BacktestRequest {
  tickers: string[];
  conditions: ConditionRequest[];
  hold: number;
  capital: number;
  years: number;
  benchmark: string;
  stop_loss?: number | null;
  max_tickers?: number | null;
}

export interface TradeResponse {
  ticker: string;
  entry_date: string;
  entry_price: number;
  exit_date: string;
  exit_price: number;
  hold_bars: number;
  return_pct: number;
}

export interface MetricsResponse {
  total_trades: number;
  win_rate: number;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  profit_factor: number;
  avg_trade_return: number;
}

export interface EquityPoint {
  date: string;
  strategy: number;
  benchmark: number;
}

export interface BacktestResponse {
  trades: TradeResponse[];
  metrics: MetricsResponse;
  benchmark_metrics: MetricsResponse;
  equity_curve: EquityPoint[];
  ticker_results: Record<string, TradeResponse[]>;
  conditions: ConditionRequest[];
  config: Record<string, unknown>;
}

export interface PeriodOption {
  label: string;
  value: string;
  months: number;
}

export const OPERATORS = [
  '<',
  '>',
  '<=',
  '>=',
  '==',
] as const;

export type Operator = (typeof OPERATORS)[number];
