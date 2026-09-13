import type {
  AppConfig,
  BacktestRequest,
  BacktestResponse,
  IndicatorInfo,
} from './types';

const BASE = import.meta.env.VITE_API_URL ?? '';

const NETWORK_ERROR =
  'Could not reach the server. Please check your connection and try again.';
const GENERIC_ERROR =
  'Something went wrong. Please try again in a moment.';

function extractDetail(body: unknown, status: number): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.trim()) return detail;
  }
  if (status >= 500) return GENERIC_ERROR;
  return `Request failed (${status}). Please try again.`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, init);
  } catch {
    // Network / CORS failure — never surface a raw browser error.
    throw new Error(NETWORK_ERROR);
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractDetail(body, res.status));
  }
  return res.json();
}

export function fetchIndicators(): Promise<IndicatorInfo[]> {
  return request<IndicatorInfo[]>('/api/indicators');
}

export function fetchConfig(): Promise<AppConfig> {
  return request<AppConfig>('/api/config');
}

export function runBacktest(req: BacktestRequest): Promise<BacktestResponse> {
  return request<BacktestResponse>('/api/backtest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
}

export function startBacktest(
  req: BacktestRequest,
): Promise<{ backtest_id: number }> {
  return request<{ backtest_id: number }>('/api/backtest/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
}

export function getBacktestProgress(
  backtestId: number,
): Promise<{ status: string; progress: number; detail?: string }> {
  return request<{ status: string; progress: number; detail?: string }>(
    `/api/backtest/${backtestId}/progress`,
  );
}

export function getBacktestResult(backtestId: number): Promise<BacktestResponse> {
  return request<BacktestResponse>(`/api/backtest/${backtestId}/result`);
}
