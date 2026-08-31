import type { TradeResponse } from '../types';

interface Props {
  trades: TradeResponse[];
  tickerResults: Record<string, TradeResponse[]>;
}

function pnlColor(pct: number) {
  if (pct > 0) return 'text-green-600';
  if (pct < 0) return 'text-red-600';
  return 'text-gray-500';
}

export function TradesTable({ trades, tickerResults }: Props) {
  const tickers = Object.keys(tickerResults);
  const showTickerCol = tickers.length > 1;

  return (
    <div>
      <h3 className="mb-2 text-sm font-medium text-gray-700">
        Trades ({trades.length})
      </h3>
      <div className="max-h-[400px] overflow-auto rounded border border-gray-200">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr className="text-xs text-gray-400">
              {showTickerCol && <th className="px-3 py-2">Ticker</th>}
              <th className="px-3 py-2">Entry</th>
              <th className="px-3 py-2 text-right">Entry $</th>
              <th className="px-3 py-2">Exit</th>
              <th className="px-3 py-2 text-right">Exit $</th>
              <th className="px-3 py-2 text-right">Bars</th>
              <th className="px-3 py-2 text-right">Return</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t, i) => (
              <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                {showTickerCol && (
                  <td className="px-3 py-1.5 font-medium tabular-nums">
                    {t.ticker}
                  </td>
                )}
                <td className="px-3 py-1.5 tabular-nums">{t.entry_date}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">
                  ${t.entry_price.toFixed(2)}
                </td>
                <td className="px-3 py-1.5 tabular-nums">{t.exit_date}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">
                  ${t.exit_price.toFixed(2)}
                </td>
                <td className="px-3 py-1.5 text-right tabular-nums">
                  {t.hold_bars}
                </td>
                <td
                  className={`px-3 py-1.5 text-right font-medium tabular-nums ${pnlColor(
                    t.return_pct,
                  )}`}
                >
                  {(t.return_pct * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
