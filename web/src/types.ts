export interface ParamInfo {
  name: string;
  type: string;
  default: number;
  min?: number;
  max?: number;
  hint?: string;
}

export interface IndicatorInfo {
  name: string;
  params: ParamInfo[];
  components: string[];
  value_hint?: string;
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
  conditions: ConditionRequest[];
  capital: number;
  years: number;
  position_size: number;
  position_size_base: 'total' | 'unallocated';
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
  cash_remaining: number;
  positions_value: number;
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

export interface AppConfig {
  max_years: number;
  default_years: number;
  default_capital: number;
}

export const OPERATORS = [
  '<',
  '>',
  '<=',
  '>=',
  '==',
] as const;

export type Operator = (typeof OPERATORS)[number];
