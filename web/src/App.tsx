import { useState } from 'react';
import type { BacktestRequest, BacktestResponse } from './types';
import { runBacktest } from './api';
import { BacktestForm } from './components/BacktestForm';
import { EquityChart } from './components/EquityChart';
import { MetricsTable } from './components/MetricsTable';
import { TradesTable } from './components/TradesTable';
import { IndicatorsPage } from './components/IndicatorsPage';
import { HomePage } from './components/HomePage';

type Page = 'home' | 'backtest' | 'indicators';

export default function App() {
  const [page, setPage] = useState<Page>('home');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (req: BacktestRequest) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runBacktest(req);
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = (newPage: Page) => {
    setPage(newPage);
    if (newPage !== 'backtest') {
      setResult(null);
      setError(null);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-slate-200/60 glass">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500 transition-transform hover:scale-105">
              <span className="text-sm font-bold text-white">Q</span>
            </div>
            <span className="font-display text-lg font-semibold text-slate-800">
              QuantLab
            </span>
            <span className="ml-2 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-medium text-emerald-700">
              v3.3.0
            </span>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => handleNavigate('home')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                page === 'home'
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => handleNavigate('backtest')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                page === 'backtest'
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Backtest
            </button>
            <button
              onClick={() => handleNavigate('indicators')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                page === 'indicators'
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Indicators
            </button>
          </div>

          <a
            href="https://github.com/szuck12/quant-lab"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
          >
            GitHub
          </a>
        </div>
      </nav>

      {/* Main Content */}
      <div className="animate-page-in">
        {page === 'home' && (
          <HomePage onNavigate={handleNavigate} />
        )}
        {page === 'backtest' && (
          <BacktestPage
            loading={loading}
            result={result}
            error={error}
            onSubmit={handleSubmit}
          />
        )}
        {page === 'indicators' && (
          <IndicatorsPage />
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 border-t border-slate-200/60 bg-white/50 py-8">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <p className="font-display text-sm font-medium text-slate-600">
            QuantLab v3.3.0
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Free & Open Source — Built for traders who want to understand their indicators
          </p>
        </div>
      </footer>
    </div>
  );
}

function BacktestPage({
  loading,
  result,
  error,
  onSubmit,
}: {
  loading: boolean;
  result: BacktestResponse | null;
  error: string | null;
  onSubmit: (req: BacktestRequest) => void;
}) {
  const [showQuickStart, setShowQuickStart] = useState(false);

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      {/* Quick Start Toggle */}
      <div className="mb-6 text-center">
        <button
          onClick={() => setShowQuickStart(!showQuickStart)}
          className="text-sm font-medium text-emerald-600 hover:text-emerald-700"
        >
          {showQuickStart ? 'Hide quick start' : 'Show quick start example'}
        </button>
      </div>

      {/* Quick Start Example */}
      {showQuickStart && (
        <div className="mb-6 rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-cyan-50 p-5 animate-fade-in">
          <h3 className="mb-2 font-display text-sm font-semibold text-slate-800">
            Quick Start: RSI Oversold Buy Signal
          </h3>
          <p className="mb-4 text-xs text-slate-600">
            This example finds stocks where RSI drops below 30 (oversold), suggesting
            a potential buying opportunity. The strategy enters when RSI is oversold
            and exits after 10 days.
          </p>
          <button
            onClick={() => {
              onSubmit({
                conditions: [
                  {
                    indicator: 'RSI',
                    params: { window: 14 },
                    component: null,
                    operator: '<',
                    value: 30,
                    interval: '1d',
                  },
                ],
                capital: 10000,
                years: 2,
              });
            }}
            disabled={loading}
            className="rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-500/20 transition-all hover:shadow-lg hover:shadow-emerald-500/30 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Try this example'}
          </button>
        </div>
      )}

      {/* Form */}
      <section className="rounded-2xl border border-slate-200/60 bg-white p-6 shadow-sm">
        <BacktestForm loading={loading} onSubmit={onSubmit} />
      </section>

      {/* Error */}
      {error && (
        <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 animate-fade-in">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6 animate-fade-in">
          {/* Summary Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                label: 'Total Return',
                value:
                  result.metrics.total_return !== 0
                    ? `${result.metrics.total_return > 0 ? '+' : ''}${(result.metrics.total_return * 100).toFixed(2)}%`
                    : '—',
                color:
                  result.metrics.total_return > 0
                    ? 'text-emerald-600'
                    : result.metrics.total_return < 0
                      ? 'text-rose-500'
                      : 'text-slate-500',
              },
              {
                label: 'Sharpe Ratio',
                value:
                  result.metrics.sharpe_ratio !== 0
                    ? result.metrics.sharpe_ratio.toFixed(2)
                    : '—',
                color: 'text-slate-800',
              },
              {
                label: 'Win Rate',
                value:
                  result.metrics.win_rate !== 0
                    ? `${(result.metrics.win_rate * 100).toFixed(1)}%`
                    : '—',
                color: 'text-slate-800',
              },
              {
                label: 'Total Trades',
                value: String(result.metrics.total_trades),
                color: 'text-slate-800',
              },
            ].map((card) => (
              <div
                key={card.label}
                className="rounded-2xl border border-slate-200/60 bg-white p-4 shadow-sm"
              >
                <p className="text-xs font-medium text-slate-500">{card.label}</p>
                <p className={`mt-1 font-display text-2xl font-bold tabular-nums ${card.color}`}>
                  {card.value}
                </p>
              </div>
            ))}
          </div>

          {/* Chart */}
          <section className="rounded-2xl border border-slate-200/60 bg-white p-6 shadow-sm">
            <EquityChart data={result.equity_curve} />
          </section>

          {/* Metrics + Trades */}
          <div className="grid gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-slate-200/60 bg-white p-6 shadow-sm">
              <MetricsTable
                strategy={result.metrics}
                benchmark={result.benchmark_metrics}
              />
            </section>

            <section className="rounded-2xl border border-slate-200/60 bg-white p-6 shadow-sm">
              <TradesTable
                trades={result.trades}
                tickerResults={result.ticker_results}
              />
            </section>
          </div>
        </div>
      )}
    </main>
  );
}
