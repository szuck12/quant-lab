import { useEffect, useState } from 'react';
import type {
  BacktestRequest,
  ConditionRequest,
  IndicatorInfo,
  PeriodOption,
} from '../types';
import { fetchIndicators, fetchPeriods } from '../api';
import { ConditionRow } from './ConditionRow';

const EMPTY: ConditionRequest = {
  indicator: 'RSI',
  params: { window: 14 },
  component: null,
  operator: '<',
  value: 30,
  interval: '1d',
};

interface Props {
  loading: boolean;
  onSubmit: (req: BacktestRequest) => void;
}

export function BacktestForm({ loading, onSubmit }: Props) {
  const [indicators, setIndicators] = useState<IndicatorInfo[]>([]);
  const [periods, setPeriods] = useState<PeriodOption[]>([]);
  const [tickers, setTickers] = useState('AAPL');
  const [conditions, setConditions] = useState<ConditionRequest[]>([EMPTY]);
  const [hold, setHold] = useState(10);
  const [capital, setCapital] = useState(10000);
  const [period, setPeriod] = useState('2yr');
  const [benchmark, setBenchmark] = useState('SPY');
  const [stopLoss, setStopLoss] = useState('');

  useEffect(() => {
    fetchIndicators().then(setIndicators).catch(console.error);
    fetchPeriods().then(setPeriods).catch(console.error);
  }, []);

  const addCondition = () =>
    setConditions([...conditions, { ...EMPTY }]);

  const updateCondition = (i: number, c: ConditionRequest) =>
    setConditions(conditions.map((x, j) => (j === i ? c : x)));

  const removeCondition = (i: number) =>
    setConditions(conditions.filter((_, j) => j !== i));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const tickerList = tickers
      .split(/[,\s]+/)
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);

    if (!tickerList.length || !conditions.length) return;

    const yearsNum = parseInt(period.replace(/\D/g, ''), 10) || 2;

    onSubmit({
      tickers: tickerList,
      conditions,
      hold,
      capital,
      years: yearsNum,
      benchmark: benchmark.toUpperCase() || 'SPY',
      stop_loss: stopLoss ? parseFloat(stopLoss) : null,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Tickers */}
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Tickers
        </label>
        <input
          type="text"
          value={tickers}
          onChange={(e) => setTickers(e.target.value)}
          placeholder="AAPL, MSFT, GOOG"
          className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <p className="mt-1 text-xs text-gray-400">
          Comma-separated. Max 100 for scanner mode.
        </p>
      </div>

      {/* Period / Hold / Capital row */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <label className="flex flex-col text-xs text-gray-500">
          Period
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          >
            {periods.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col text-xs text-gray-500">
          Hold (bars)
          <input
            type="number"
            min={1}
            max={100}
            value={hold}
            onChange={(e) => setHold(parseInt(e.target.value, 10) || 10)}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          />
        </label>
        <label className="flex flex-col text-xs text-gray-500">
          Capital ($)
          <input
            type="number"
            min={100}
            step={100}
            value={capital}
            onChange={(e) => setCapital(parseInt(e.target.value, 10) || 10000)}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          />
        </label>
        <label className="flex flex-col text-xs text-gray-500">
          Benchmark
          <input
            type="text"
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value)}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          />
        </label>
      </div>

      {/* Stop loss */}
      <div className="w-48">
        <label className="flex flex-col text-xs text-gray-500">
          Stop Loss % (optional)
          <input
            type="number"
            min={0}
            max={100}
            step={0.5}
            value={stopLoss}
            onChange={(e) => setStopLoss(e.target.value)}
            placeholder="None"
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          />
        </label>
      </div>

      {/* Conditions */}
      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-700">Conditions</h3>
        <div className="space-y-2">
          {conditions.map((c, i) => (
            <ConditionRow
              key={i}
              index={i}
              condition={c}
              indicators={indicators}
              onChange={updateCondition}
              onRemove={removeCondition}
              canRemove={conditions.length > 1}
            />
          ))}
        </div>
        <button
          type="button"
          onClick={addCondition}
          className="mt-2 rounded bg-blue-50 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-100"
        >
          + Add Condition
        </button>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Running backtest...' : 'Run Backtest'}
      </button>
    </form>
  );
}
