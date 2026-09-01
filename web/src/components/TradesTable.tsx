import type { TradeResponse } from '../types';

interface Props {
  trades: TradeResponse[];
  tickerResults: Record<string, TradeResponse[]>;
}

function pnlColor(pct: number) {
  if (pct > 0) return 'text-emerald-600';
  if (pct < 0) return 'text-red-500';
  return 'text-slate-500';
}

export function TradesTable({ trades, tickerResults }: Props) {
  const tickers = Object.keys(tickerResults);
  const showTickerCol = tickers.length > 1;

  if (trades.length === 0) {
    return (
      <div>
        <h3 className="mb-4 text-sm font-semibold text-slate-700">
          Trade Log
        </h3>
        <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-8 text-center">
          <p className="text-sm text-slate-500">
            No trades generated. Try adjusting your conditions or
            using a longer period.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">
          Trade Log
        </h3>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
          {trades.length} trades
        </span>
      </div>
      <div className="max-h-[400px] overflow-auto rounded-xl border border-slate-200">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-slate-50">
            <tr className="text-xs font-medium text-slate-400">
              {showTickerCol && <th className="px-3 py-2.5">Ticker</th>}
              <th className="px-3 py-2.5">Entry</th>
              <th className="px-3 py-2.5 text-right">Entry $</th>
              <th className="px-3 py-2.5">Exit</th>
              <th className="px-3 py-2.5 text-right">Exit $</th>
              <th className="px-3 py-2.5 text-right">Bars</th>
              <th className="px-3 py-2.5 text-right">Return</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t, i) => (
              <tr key={i} className="border-t border-slate-100 transition-colors hover:bg-slate-50/50">
                {showTickerCol && (
                  <td className="px-3 py-2 font-medium tabular-nums text-slate-700">
                    {t.ticker}
                  </td>
                )}
                <td className="px-3 py-2 tabular-nums text-slate-600">{t.entry_date}</td>
                <td className="px-3 py-2 text-right tabular-nums text-slate-600">
                  ${t.entry_price.toFixed(2)}
                </td>
                <td className="px-3 py-2 tabular-nums text-slate-600">{t.exit_date}</td>
                <td className="px-3 py-2 text-right tabular-nums text-slate-600">
                  ${t.exit_price.toFixed(2)}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-slate-500">
                  {t.hold_bars}
                </td>
                <td
                  className={`px-3 py-2 text-right font-semibold tabular-nums ${pnlColor(
                    t.return_pct,
                  )}`}
                >
                  {t.return_pct > 0 ? '+' : ''}{(t.return_pct * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
