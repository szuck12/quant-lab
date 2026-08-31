import { useState } from 'react';
import type { BacktestRequest, BacktestResponse } from './types';
import { runBacktest } from './api';
import { BacktestForm } from './components/BacktestForm';
import { EquityChart } from './components/EquityChart';
import { MetricsTable } from './components/MetricsTable';
import { TradesTable } from './components/TradesTable';

export default function App() {
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
    <div className="min-h-screen bg-white text-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 bg-gray-50 px-4 py-4">
        <div className="mx-auto max-w-5xl">
          <h1 className="text-xl font-semibold tracking-tight">
            QuantLab
          </h1>
          <p className="text-sm text-gray-400">
            Backtest technical indicator strategies
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 p-4">
        {/* Form */}
        <section className="rounded-lg border border-gray-200 p-4">
          <BacktestForm loading={loading} onSubmit={handleSubmit} />
        </section>

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            <section className="rounded-lg border border-gray-200 p-4">
              <EquityChart data={result.equity_curve} />
            </section>

            <section className="rounded-lg border border-gray-200 p-4">
              <MetricsTable
                strategy={result.metrics}
                benchmark={result.benchmark_metrics}
              />
            </section>

            <section className="rounded-lg border border-gray-200 p-4">
              <TradesTable
                trades={result.trades}
                tickerResults={result.ticker_results}
              />
            </section>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-4 text-center text-xs text-gray-400">
        QuantLab v3.0.0 — Free & Open Source
      </footer>
    </div>
  );
}
