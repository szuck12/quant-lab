import type { MetricsResponse } from '../types';

interface Props {
  strategy: MetricsResponse;
  benchmark: MetricsResponse;
}

function pct(v: number) {
  if (!Number.isFinite(v)) return '—';
  const formatted = (v * 100).toFixed(2);
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
  fmt,
}: {
  label: string;
  sv: number;
  bv: number;
  fmt: (v: number) => string;
}) {
  const svFmt = fmt(sv);
  const bvFmt = fmt(bv);
  const isPositive = sv > 0;
  const isNegative = sv < 0;

  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="py-2.5 pr-4 text-sm text-slate-500">{label}</td>
      <td
        className={`py-2.5 pr-4 text-right text-sm font-semibold tabular-nums ${
          isPositive
            ? 'text-emerald-600'
            : isNegative
              ? 'text-red-500'
              : 'text-slate-800'
        }`}
      >
        {svFmt}
      </td>
      <td className="py-2.5 text-right text-sm text-slate-500 tabular-nums">
        {bvFmt}
      </td>
    </tr>
  );
}

export function MetricsTable({ strategy, benchmark }: Props) {
  return (
    <div>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">
        Performance Metrics
      </h3>
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-slate-200 text-xs font-medium text-slate-400">
            <th className="pb-2 pr-4" />
            <th className="pb-2 pr-4 text-right">Strategy</th>
            <th className="pb-2 text-right">Benchmark</th>
          </tr>
        </thead>
        <tbody>
          <Row label="Total trades" sv={strategy.total_trades} bv={benchmark.total_trades} fmt={(v) => String(v)} />
          <Row label="Win rate" sv={strategy.win_rate} bv={benchmark.win_rate} fmt={pct} />
          <Row label="Total return" sv={strategy.total_return} bv={benchmark.total_return} fmt={pct} />
          <Row label="Annualized" sv={strategy.annualized_return} bv={benchmark.annualized_return} fmt={pct} />
          <Row label="Sharpe" sv={strategy.sharpe_ratio} bv={benchmark.sharpe_ratio} fmt={(v) => num(v)} />
          <Row label="Sortino" sv={strategy.sortino_ratio} bv={benchmark.sortino_ratio} fmt={(v) => num(v)} />
          <Row label="Max drawdown" sv={strategy.max_drawdown} bv={benchmark.max_drawdown} fmt={pct} />
          <Row label="Profit factor" sv={strategy.profit_factor} bv={benchmark.profit_factor} fmt={(v) => num(v)} />
          <Row label="Avg trade return" sv={strategy.avg_trade_return} bv={benchmark.avg_trade_return} fmt={pct} />
        </tbody>
      </table>
    </div>
  );
}
