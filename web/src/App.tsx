import { useState } from 'react';
import type { BacktestRequest, BacktestResponse } from './types';
import { runBacktest } from './api';
import { BacktestForm } from './components/BacktestForm';
import { EquityChart } from './components/EquityChart';
import { MetricsTable } from './components/MetricsTable';
import { TradesTable } from './components/TradesTable';
import { IndicatorsPage } from './components/IndicatorsPage';

type Page = 'backtest' | 'indicators';

export default function App() {
  const [page, setPage] = useState<Page>('backtest');
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

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-slate-200/60 glass">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500">
              <span className="text-sm font-bold text-white">Q</span>
            </div>
            <span className="font-display text-lg font-semibold text-slate-800">
              QuantLab
            </span>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage('backtest')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                page === 'backtest'
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Backtest
            </button>
            <button
              onClick={() => setPage('indicators')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                page === 'indicators'
                  ? 'bg-slate-800 text-white'
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
            className="text-sm text-slate-500 hover:text-slate-700"
          >
            GitHub
          </a>
        </div>
      </nav>

      {/* Main Content */}
      {page === 'backtest' ? (
        <BacktestPage
          loading={loading}
          result={result}
          error={error}
          onSubmit={handleSubmit}
        />
      ) : (
        <IndicatorsPage />
      )}

      {/* Footer */}
      <footer className="mt-12 border-t border-slate-200/60 bg-white/50 py-8">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <p className="font-display text-sm font-medium text-slate-600">
            QuantLab v3.2.0
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
      {/* Hero Section */}
      <div className="mb-10 text-center">
        <h1 className="font-display text-5xl font-bold tracking-tight text-slate-800">
          Backtest{' '}
          <span className="bg-gradient-to-r from-emerald-500 via-cyan-500 to-purple-500 bg-clip-text text-transparent">
            Technical Indicators
          </span>
        </h1>
        <p className="mt-4 text-lg text-slate-500">
          Test RSI, MACD, Bollinger Bands and more across S&P 500 stocks
        </p>
        <div className="mt-5 flex flex-wrap items-center justify-center gap-5 text-sm text-slate-500">
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Backtest in seconds
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-cyan-500" />
            14 indicators
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-purple-500" />
            S&P 500 coverage
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Free & open source
          </span>
        </div>
      </div>

      {/* How It Works */}
      <div className="mb-10">
        <h2 className="mb-6 text-center font-display text-lg font-semibold text-slate-700">
          How It Works
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          {[
            {
              step: '01',
              title: 'Set Conditions',
              description: 'Choose indicators, parameters, and thresholds',
              color: 'from-emerald-500 to-emerald-600',
            },
            {
              step: '02',
              title: 'Run Backtest',
              description: 'Execute across S&P 500 in seconds',
              color: 'from-cyan-500 to-cyan-600',
            },
            {
              step: '03',
              title: 'Analyze Results',
              description: 'Review equity curve, metrics, and trades',
              color: 'from-purple-500 to-purple-600',
            },
          ].map((item) => (
            <div
              key={item.step}
              className={`relative rounded-2xl border border-slate-200/60 bg-white p-5 shadow-sm card-hover`}
            >
              <div
                className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} text-sm font-bold text-white`}
              >
                {item.step}
              </div>
              <h3 className="font-display text-sm font-semibold text-slate-800">
                {item.title}
              </h3>
              <p className="mt-1 text-xs text-slate-500">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

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
        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 animate-fade-in">
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
                      ? 'text-red-500'
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

      {/* Features Bento Grid */}
      {!result && !loading && (
        <div className="mt-12">
          <h2 className="mb-6 text-center font-display text-lg font-semibold text-slate-700">
            Why QuantLab
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: '⚡',
                title: 'Lightning Fast',
                description: 'Results in seconds across 500+ S&P 500 stocks',
                color: 'border-emerald-200 bg-emerald-50/50',
              },
              {
                icon: '📊',
                title: '14 Indicators',
                description: 'RSI, MACD, Bollinger Bands, and more',
                color: 'border-cyan-200 bg-cyan-50/50',
              },
              {
                icon: '🎯',
                title: 'Precision Control',
                description: 'Custom parameters, thresholds, and intervals',
                color: 'border-purple-200 bg-purple-50/50',
              },
              {
                icon: '📈',
                title: 'S&P 500 Universe',
                description: 'Test across the entire market automatically',
                color: 'border-emerald-200 bg-emerald-50/50',
              },
              {
                icon: '🔓',
                title: 'No Account Required',
                description: 'Start backtesting immediately, no signup needed',
                color: 'border-cyan-200 bg-cyan-50/50',
              },
              {
                icon: '💻',
                title: 'Open Source',
                description: 'Free forever, transparent code on GitHub',
                color: 'border-purple-200 bg-purple-50/50',
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className={`rounded-2xl border p-5 card-hover ${feature.color}`}
              >
                <span className="text-2xl">{feature.icon}</span>
                <h3 className="mt-3 font-display text-sm font-semibold text-slate-800">
                  {feature.title}
                </h3>
                <p className="mt-1 text-xs text-slate-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
