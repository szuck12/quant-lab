import type { MetricsResponse } from '../types';

interface Props {
  strategy: MetricsResponse;
  benchmark: MetricsResponse;
}

const NA = 'N/A';

function pct(v: number, signed = true) {
  if (!Number.isFinite(v)) return '—';
  const formatted = (v * 100).toFixed(2);
  if (!signed) return `${formatted}%`;
  return v > 0 ? `+${formatted}%` : `${formatted}%`;
}

function num(v: number, dec = 2) {
  if (!Number.isFinite(v)) return '—';
  return v.toFixed(dec);
}

function Row({
  label,
  sv,
  bv,
}: {
  label: string;
  sv: string;
  bv?: string;
}) {
  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="py-2.5 pr-4 text-sm text-slate-500">{label}</td>
      <td className="py-2.5 pr-4 text-right text-sm font-semibold tabular-nums text-slate-700">
        {sv}
      </td>
      <td className="py-2.5 text-right text-sm tabular-nums text-slate-500">
        {bv ?? NA}
      </td>
    </tr>
  );
}

export function MetricsTable({ strategy, benchmark }: Props) {
  return (
    <div>
      <h3 className="mb-4 font-display text-sm font-semibold text-slate-700">
        Performance Metrics
      </h3>
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-slate-200 text-xs font-medium text-slate-400">
            <th className="pb-2 pr-4" />
            <th className="pb-2 pr-4 text-right">Strategy</th>
            <th className="pb-2 text-right">Benchmark (SPY)</th>
          </tr>
        </thead>
        <tbody>
          <Row
            label="Total trades"
            sv={String(strategy.total_trades)}
          />
          <Row
            label="Win rate"
            sv={pct(strategy.win_rate, false)}
          />
          <Row
            label="Total return"
            sv={pct(strategy.total_return)}
            bv={pct(benchmark.total_return)}
          />
          <Row
            label="Annualized"
            sv={pct(strategy.annualized_return)}
            bv={pct(benchmark.annualized_return)}
          />
          <Row
            label="Sharpe"
            sv={num(strategy.sharpe_ratio)}
            bv={num(benchmark.sharpe_ratio)}
          />
          <Row
            label="Sortino"
            sv={num(strategy.sortino_ratio)}
            bv={num(benchmark.sortino_ratio)}
          />
          <Row
            label="Max drawdown"
            sv={pct(strategy.max_drawdown)}
            bv={pct(benchmark.max_drawdown)}
          />
          <Row
            label="Avg trade return"
            sv={pct(strategy.avg_trade_return)}
          />
        </tbody>
      </table>
    </div>
  );
}
