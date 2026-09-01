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
            <span className="text-lg font-semibold text-slate-800">
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
      <footer className="mt-auto border-t border-slate-200/60 bg-white/50 py-6">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <p className="text-sm text-slate-500">
            QuantLab v3.1.0 — Free & Open Source
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Built for traders who want to understand their indicators
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
  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      {/* Hero Section */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-slate-800">
          Backtest <span className="gradient-text">Technical Indicators</span>
        </h1>
        <p className="mt-3 text-lg text-slate-500">
          Test RSI, MACD, Bollinger Bands and more across S&P 500 stocks
        </p>
        <div className="mt-4 flex flex-wrap items-center justify-center gap-4 text-sm text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Backtest in seconds
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-500" />
            14 indicators
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
            S&P 500 coverage
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Free & open source
          </span>
        </div>
      </div>

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
        <div className="mt-6 space-y-6 animate-fade-in">
          <section className="rounded-2xl border border-slate-200/60 bg-white p-6 shadow-sm">
            <EquityChart data={result.equity_curve} />
          </section>

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
