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
  const [capitalError, setCapitalError] = useState('');
  const [yearsError, setYearsError] = useState('');
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

    // Validate capital
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

    // Validate years
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

    return ok;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    onSubmit({
      conditions,
      capital: parseFloat(capital) || 10000,
      years: parseInt(years, 10) || 2,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Error banner */}
      {fetchError && (
        <div className="rounded bg-red-50 p-3 text-sm text-red-700">
          {fetchError}
        </div>
      )}

      {/* Period + Capital row */}
      <div className="grid grid-cols-2 gap-4">
        <label className="flex flex-col text-xs text-gray-500">
          Last N years
          <input
            type="number"
            min={1}
            max={maxYears}
            value={years}
            onChange={(e) => setYears(e.target.value)}
            className={`mt-1 rounded border bg-white px-3 py-2 text-sm ${
              yearsError ? 'border-red-400' : 'border-gray-300'
            }`}
          />
          {yearsError ? (
            <span className="mt-1 text-xs text-red-500">{yearsError}</span>
          ) : (
            <span className="mt-1 text-xs text-gray-400">
              Max {maxYears} years
            </span>
          )}
        </label>

        <label className="flex flex-col text-xs text-gray-500">
          Initial Capital ($)
          <input
            type="text"
            value={capital}
            onChange={(e) => setCapital(e.target.value)}
            className={`mt-1 rounded border bg-white px-3 py-2 text-sm ${
              capitalError ? 'border-red-400' : 'border-gray-300'
            }`}
          />
          {capitalError ? (
            <span className="mt-1 text-xs text-red-500">{capitalError}</span>
          ) : (
            <span className="mt-1 text-xs text-gray-400">
              Starting capital for backtest
            </span>
          )}
        </label>
      </div>

      {/* Conditions */}
      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-700">
          Conditions
        </h3>
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
