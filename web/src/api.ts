import type {
  BacktestRequest,
  BacktestResponse,
  IndicatorInfo,
  PeriodOption,
} from './types';

const BASE = '';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `GET ${path} failed: ${res.status}`);
  }
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `POST ${path} failed: ${res.status}`);
  }
  return res.json();
}

export function fetchIndicators(): Promise<IndicatorInfo[]> {
  return get<IndicatorInfo[]>('/api/indicators');
}

export function fetchPeriods(): Promise<PeriodOption[]> {
  return get<PeriodOption[]>('/api/periods');
}

export function runBacktest(req: BacktestRequest): Promise<BacktestResponse> {
  return post<BacktestResponse>('/api/backtest', req);
}
