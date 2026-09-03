import { useEffect, useState } from 'react';
import type {
  BacktestRequest,
  ConditionRequest,
  IndicatorInfo,
} from '../types';
import { fetchConfig, fetchIndicators } from '../api';
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
  const [maxYears, setMaxYears] = useState(20);
  const [conditions, setConditions] = useState<ConditionRequest[]>([EMPTY]);
  const [capital, setCapital] = useState('10000');
  const [years, setYears] = useState('2');
  const [positionSize, setPositionSize] = useState('100');
  const [positionSizeBase, setPositionSizeBase] = useState<'total' | 'unallocated'>('total');
  const [capitalError, setCapitalError] = useState('');
  const [yearsError, setYearsError] = useState('');
  const [positionSizeError, setPositionSizeError] = useState('');
  const [fetchError, setFetchError] = useState('');

  useEffect(() => {
    fetchIndicators()
      .then(setIndicators)
      .catch((err) => {
        console.error('Failed to fetch indicators:', err);
        setFetchError('Failed to load indicators. Is the backend server running?');
      });
    fetchConfig()
      .then((cfg) => setMaxYears(cfg.max_years))
      .catch((err) => {
        console.error('Failed to fetch config:', err);
      });
  }, []);

  const addCondition = () =>
    setConditions([...conditions, { ...EMPTY }]);

  const updateCondition = (i: number, c: ConditionRequest) =>
    setConditions(conditions.map((x, j) => (j === i ? c : x)));

  const removeCondition = (i: number) =>
    setConditions(conditions.filter((_, j) => j !== i));

  const validate = (): boolean => {
    let ok = true;

    const cap = parseFloat(capital);
    if (!capital.trim()) {
      setCapitalError('Capital is required');
      ok = false;
    } else if (isNaN(cap) || cap <= 0) {
      setCapitalError('Must be a positive number');
      ok = false;
    } else if (cap > 1_000_000_000) {
      setCapitalError('Cannot exceed $1,000,000,000');
      ok = false;
    } else {
      setCapitalError('');
    }

    const yr = parseInt(years, 10);
    if (!years.trim()) {
      setYearsError('Years is required');
      ok = false;
    } else if (isNaN(yr) || yr < 1) {
      setYearsError('Must be at least 1 year');
      ok = false;
    } else if (yr > maxYears) {
      setYearsError(`Maximum is ${maxYears} years`);
      ok = false;
    } else {
      setYearsError('');
    }

    if (conditions.length === 0) {
      ok = false;
    }

    const ps = parseFloat(positionSize);
    if (isNaN(ps) || ps < 0 || ps > 100) {
      setPositionSizeError('Must be between 0 and 100');
      ok = false;
    } else {
      setPositionSizeError('');
    }

    return ok;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    onSubmit({
      conditions,
      capital: parseFloat(capital) || 10000,
      years: parseInt(years, 10) || 2,
      position_size: parseFloat(positionSize) || 100,
      position_size_base: positionSizeBase,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error banner */}
      {fetchError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {fetchError}
        </div>
      )}

      {/* Period + Capital + Position Size row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Last N Years
          </span>
          <input
            type="number"
            min={1}
            max={maxYears}
            value={years}
            onChange={(e) => setYears(e.target.value)}
            className={`rounded-xl border bg-slate-50 px-4 py-2.5 text-sm font-medium tabular-nums transition-colors ${
              yearsError
                ? 'border-red-300 focus:border-red-400 focus:ring-red-400/20'
                : 'border-slate-200 focus:border-emerald-400 focus:ring-emerald-400/20'
            } focus:outline-none focus:ring-2`}
          />
          {yearsError ? (
            <span className="mt-1 text-xs text-red-500">{yearsError}</span>
          ) : (
            <span className="mt-1 text-xs text-slate-400">
              Max {maxYears} years
            </span>
          )}
        </label>

        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Initial Capital
          </span>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-sm text-slate-400">
              $
            </span>
            <input
              type="text"
              value={capital}
              onChange={(e) => setCapital(e.target.value)}
              className={`w-full rounded-xl border bg-slate-50 py-2.5 pl-7 pr-4 text-sm font-medium tabular-nums transition-colors ${
                capitalError
                  ? 'border-red-300 focus:border-red-400 focus:ring-red-400/20'
                  : 'border-slate-200 focus:border-emerald-400 focus:ring-emerald-400/20'
              } focus:outline-none focus:ring-2`}
            />
          </div>
          {capitalError ? (
            <span className="mt-1 text-xs text-red-500">{capitalError}</span>
          ) : (
            <span className="mt-1 text-xs text-slate-400">
              Starting capital for backtest
            </span>
          )}
        </label>

        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Position Size
          </span>
          <div className="relative">
            <input
              type="number"
              min={0}
              max={100}
              value={positionSize}
              onChange={(e) => setPositionSize(e.target.value)}
              className={`w-full rounded-xl border bg-slate-50 px-4 py-2.5 text-sm font-medium tabular-nums transition-colors ${
                positionSizeError
                  ? 'border-red-300 focus:border-red-400 focus:ring-red-400/20'
                  : 'border-slate-200 focus:border-emerald-400 focus:ring-emerald-400/20'
              } focus:outline-none focus:ring-2`}
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-slate-400">
              %
            </span>
          </div>
          {positionSizeError ? (
            <span className="mt-1 text-xs text-red-500">{positionSizeError}</span>
          ) : (
            <span className="mt-1 text-xs text-slate-400">
              Percent of portfolio per buy
            </span>
          )}
        </label>
      </div>

      {/* Position Size Base */}
      <div>
        <span className="mb-2 block font-display text-xs font-medium text-slate-500">
          Position Size Base
        </span>
        <div className="flex gap-3">
          <label className="flex flex-1 cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm transition-colors has-[:checked]:border-emerald-400 has-[:checked]:bg-emerald-50">
            <input
              type="radio"
              name="positionSizeBase"
              value="total"
              checked={positionSizeBase === 'total'}
              onChange={() => setPositionSizeBase('total')}
              className="accent-emerald-600"
            />
            <span className="font-medium text-slate-700">Total Capital</span>
          </label>
          <label className="flex flex-1 cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm transition-colors has-[:checked]:border-emerald-400 has-[:checked]:bg-emerald-50">
            <input
              type="radio"
              name="positionSizeBase"
              value="unallocated"
              checked={positionSizeBase === 'unallocated'}
              onChange={() => setPositionSizeBase('unallocated')}
              className="accent-emerald-600"
            />
            <span className="font-medium text-slate-700">Unallocated Capital</span>
          </label>
        </div>
        <p className="mt-1.5 text-xs text-slate-400">
          {positionSizeBase === 'total'
            ? 'Position size calculated from total portfolio value'
            : 'Position size calculated from available cash only'}
        </p>
      </div>

      {/* Conditions */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-display text-sm font-semibold text-slate-700">
            Conditions
          </h3>
          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
            {conditions.length} active
          </span>
        </div>
        <div className="space-y-3">
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
          className="mt-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-2 text-xs font-medium text-slate-600 transition-colors hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-600"
        >
          + Add Condition
        </button>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-emerald-600 px-6 py-3.5 font-display text-sm font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Running Backtest...
          </span>
        ) : (
          'Run Backtest'
        )}
      </button>
    </form>
  );
}
