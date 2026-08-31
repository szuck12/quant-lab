import type { MetricsResponse } from '../types';

interface Props {
  strategy: MetricsResponse;
  benchmark: MetricsResponse;
}

function pct(v: number) {
  return `${(v * 100).toFixed(2)}%`;
}

function num(v: number, dec = 2) {
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
  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-1.5 pr-4 text-sm text-gray-500">{label}</td>
      <td className="py-1.5 pr-4 text-right text-sm font-medium tabular-nums">
        {fmt(sv)}
      </td>
      <td className="py-1.5 text-right text-sm text-gray-500 tabular-nums">
        {fmt(bv)}
      </td>
    </tr>
  );
}

export function MetricsTable({ strategy, benchmark }: Props) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-medium text-gray-700">Metrics</h3>
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-gray-200 text-xs text-gray-400">
            <th className="pb-1 pr-4" />
            <th className="pb-1 pr-4 text-right">Strategy</th>
            <th className="pb-1 text-right">Benchmark</th>
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
