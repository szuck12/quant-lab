import { useState, useEffect } from 'react';
import { runBacktest } from './api';
import { BacktestForm } from './components/BacktestForm';
import { EquityChart } from './components/EquityChart';
import { HomePage } from './components/HomePage';
import { IndicatorsPage } from './components/IndicatorsPage';
import { MetricsTable } from './components/MetricsTable';
import { SectionRule } from './components/PageChrome';
import { TradesTable } from './components/TradesTable';
import type { BacktestRequest, BacktestResponse } from './types';

type Page = 'home' | 'backtest' | 'indicators';

function NodeGraphLogo({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 28 28" fill="none" className={className}>
      <line x1="14" y1="5" x2="5" y2="14" stroke="#10B981" strokeWidth="1" opacity="0.6" />
      <line x1="14" y1="5" x2="23" y2="14" stroke="#06B6D4" strokeWidth="1" opacity="0.6" />
      <line x1="5" y1="14" x2="14" y2="23" stroke="#06B6D4" strokeWidth="1" opacity="0.6" />
      <line x1="23" y1="14" x2="14" y2="23" stroke="#10B981" strokeWidth="1" opacity="0.6" />
      <circle cx="14" cy="14" r="1.8" fill="#F8FAFC" />
      <circle cx="14" cy="5" r="2.2" fill="#10B981" />
      <circle cx="5" cy="14" r="2.2" fill="#06B6D4" />
      <circle cx="23" cy="14" r="2.2" fill="#06B6D4" />
      <circle cx="14" cy="23" r="2.2" fill="#10B981" />
    </svg>
  );
}

export function App() {
  const [page, setPage] = useState<Page>(() => {
    const hash = window.location.hash.replace(/^#\/?/, '');
    return (['home', 'backtest', 'indicators'] as const).includes(hash as Page) ? (hash as Page) : 'home';
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace(/^#\/?/, '');
      if (['home', 'backtest', 'indicators'].includes(hash)) {
        setPage(hash as Page);
      }
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

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
    window.location.hash = `/${newPage}`;
    if (newPage !== 'backtest') {
      setResult(null);
      setError(null);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Navigation — solid, no glass morphism */}
      <nav
        aria-label="Primary navigation"
        className="sticky top-0 z-50 border-b border-slate-200 bg-white/95"
      >
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-2.5">
            <NodeGraphLogo className="h-7 w-7" />
            <span className="font-display text-lg font-semibold tracking-tight text-slate-800">
              QuantLab
            </span>
            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
              v3.7.0
            </span>
          </div>

          <div className="flex items-center gap-1">
            {(['home', 'backtest', 'indicators'] as const).map((p) => (
              <button
                key={p}
                onClick={() => handleNavigate(p)}
                aria-current={page === p ? 'page' : undefined}
                className={`relative px-4 py-2 text-sm font-medium capitalize transition-colors ${
                  page === p
                    ? 'text-emerald-600'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                {p === 'home'
                  ? 'Home'
                  : p === 'backtest'
                    ? 'Backtest'
                    : 'Indicators'}
                {page === p && (
                  <span className="absolute bottom-0 left-2 right-2 h-0.5 rounded-full bg-emerald-500" />
                )}
              </button>
            ))}
          </div>

          <a
            href="https://github.com/szuck12/quant-lab"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-slate-400 transition-colors hover:text-slate-700"
          >
            GitHub
          </a>
        </div>
      </nav>

      {/* Main Content */}
      <div key={page} className="animate-page-in">
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
      <footer className="border-t border-slate-200 bg-white/60 py-8">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <p className="font-display text-sm font-medium text-slate-600">
            QuantLab v3.7.0
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Free & Open Source — Built for traders who want to understand
            their indicators
          </p>
          <div className="mx-auto mt-6 max-w-3xl border-t border-slate-200 pt-5 text-left">
            <h3 className="mb-2 font-display text-xs font-semibold text-slate-500">
              Legal Disclaimer
            </h3>
            <p className="text-[11px] leading-relaxed text-slate-400">
              QuantLab is a research and educational tool for testing quantitative
              trading strategies. It is not a broker-dealer, investment advisor, or
              financial advisor. Nothing on this platform constitutes investment
              advice, a solicitation, or an offer to buy or sell any security.
              Trading involves risk of loss. Past performance does not guarantee
              future results. Users should conduct their own due diligence and
              consult a qualified financial advisor before making investment
              decisions.
            </p>
          </div>
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
      {/* Page Header */}
      <div className="mb-8">
        <div className="mb-8 h-0.5 w-16 rounded-full bg-emerald-500" />
        <h1 className="font-display text-3xl font-bold tracking-tight text-slate-800">
          Backtest{' '}
          <span className="text-emerald-600">Engine</span>
        </h1>
        <p className="mt-3 text-base text-slate-500">
          Configure conditions, run across S&P 500, analyze results
        </p>
      </div>

      <SectionRule />

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
        <div className="mb-6 rounded-xl border border-emerald-200 bg-emerald-50/80 p-5 animate-fade-in">
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
                position_size: 100,
                position_size_base: 'total',
              });
            }}
            disabled={loading}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Try this example'}
          </button>
        </div>
      )}

      {/* Form */}
      <section
        className="rounded-xl border border-slate-300 border-t-4 border-t-navy-800 bg-white/95 p-6 shadow-sm"
      >
        <BacktestForm loading={loading} onSubmit={onSubmit} />
      </section>

      {/* Error */}
      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 animate-fade-in">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6 animate-fade-in">
          <SectionRule />
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
                className="rounded-xl border border-slate-200 bg-white p-4"
              >
                <p className="text-xs font-medium text-slate-500">{card.label}</p>
                <p className={`mt-1 font-display text-2xl font-bold tabular-nums ${card.color}`}>
                  {card.value}
                </p>
              </div>
            ))}
          </div>

          {/* Chart */}
          <section className="rounded-xl border border-slate-200 bg-white p-6">
            <EquityChart data={result.equity_curve} />
          </section>

          {/* Metrics + Trades */}
          <div className="grid gap-6 lg:grid-cols-2">
            <section className="rounded-xl border border-slate-200 bg-white p-6">
              <MetricsTable
                strategy={result.metrics}
                benchmark={result.benchmark_metrics}
              />
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-6">
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
