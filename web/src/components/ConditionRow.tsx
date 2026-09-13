import { useState, useEffect } from 'react';
import type { IndicatorInfo, ConditionRequest, Operator } from '../types';
import { OPERATORS } from '../types';

interface Props {
  index: number;
  condition: ConditionRequest;
  indicators: IndicatorInfo[];
  onChange: (index: number, condition: ConditionRequest) => void;
  onRemove: (index: number) => void;
  canRemove: boolean;
}

const COMPONENT_LABELS: Record<string, string> = {
  plus_di: '+DI',
  minus_di: '−DI',
  adx: 'ADX',
  upper: 'Upper Band',
  middle: 'Middle Band',
  lower: 'Lower Band',
  line: 'MACD Line',
  signal: 'Signal Line',
  hist: 'Histogram',
  k: '%K',
  d: '%D',
  value: 'Value',
};

function formatComponent(c: string): string {
  return COMPONENT_LABELS[c] ?? c;
}

function formatParamName(name: string): string {
  const labels: Record<string, string> = {
    window: 'Window',
    adx_window: 'ADX Window',
    num_std: 'Std Deviations',
    fast: 'Fast Period',
    slow: 'Slow Period',
    signal: 'Signal Period',
    smooth_k: 'Smooth %K',
    smooth_d: 'Smooth %D',
  };
  return labels[name] ?? name.charAt(0).toUpperCase() + name.slice(1);
}

const DEFAULT_VALUES: Record<string, number> = {
  ADX: 25,
  ATR: 2.0,
  AV: 5000000,
  BB: 150,
  CCI: 0,
  EMA: 150,
  MACD: 0,
  OBV: 0,
  ROC: 0,
  RSI: 50,
  RVOL: 1.0,
  SMA: 150,
  STOCH: 50,
  VWAP: 150,
};

export function ConditionRow({
  index,
  condition,
  indicators,
  onChange,
  onRemove,
  canRemove,
}: Props) {
  const selected = indicators.find((i) => i.name === condition.indicator);
  const components = selected?.components ?? [];

  // Local state for raw input strings (allows empty state)
  // Initialize directly from condition.params — no need to wait for selected
  const [paramRaw, setParamRaw] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    if (condition.params) {
      Object.entries(condition.params).forEach(([key, val]) => {
        init[key] = String(val);
      });
    }
    return init;
  });
  const [valueRaw, setValueRaw] = useState(String(condition.value));
  const [paramErrors, setParamErrors] = useState<Record<string, string>>({});
  const [valueError, setValueError] = useState('');

  // Reset local state when indicator changes (skip initial mount)
  useEffect(() => {
    if (!selected) return;
    const init: Record<string, string> = {};
    selected.params.forEach((p) => {
      init[p.name] = String(condition.params[p.name] ?? p.default);
    });
    setParamRaw(init);
    setValueRaw(String(condition.value));
    setParamErrors({});
    setValueError('');
  }, [condition.indicator]);

  const update = (fields: Partial<ConditionRequest>) => {
    const next = { ...condition, ...fields };

    if (fields.indicator && fields.indicator !== condition.indicator) {
      const ind = indicators.find((i) => i.name === fields.indicator);
      if (ind) {
        const params: Record<string, number> = {};
        ind.params.forEach((p) => (params[p.name] = p.default));
        next.params = params;
        next.value = DEFAULT_VALUES[ind.name] ?? 0;
        const indComponents = ind.components ?? [];
        next.component = indComponents.length > 1 ? indComponents[0] : null;
      }
    }

    if (next.component && !components.includes(next.component)) {
      next.component = null;
    }

    onChange(index, next);
  };

  const setParam = (name: string, raw: string) => {
    setParamRaw((prev) => ({ ...prev, [name]: raw }));
    setParamErrors((prev) => ({ ...prev, [name]: '' }));

    if (raw === '') return;

    const val = parseFloat(raw);
    if (isNaN(val)) return;

    // For integer params (window), reject decimals
    const param = selected?.params.find((p) => p.name === name);
    if (param?.type === 'int' && raw.includes('.')) {
      setParamErrors((prev) => ({ ...prev, [name]: 'Must be a whole number' }));
      return;
    }

    update({ params: { ...condition.params, [name]: val } });
  };

  const validateParam = (name: string) => {
    const raw = paramRaw[name];
    if (raw === '' || raw === undefined) {
      setParamErrors((prev) => ({ ...prev, [name]: 'Required' }));
      return;
    }
    const val = parseFloat(raw);
    if (isNaN(val)) {
      setParamErrors((prev) => ({ ...prev, [name]: 'Invalid number' }));
      return;
    }
    const param = selected?.params.find((p) => p.name === name);
    if (param?.type === 'int' && !Number.isInteger(val)) {
      setParamErrors((prev) => ({ ...prev, [name]: 'Must be a whole number' }));
      return;
    }
    update({ params: { ...condition.params, [name]: val } });
  };

  const setValue = (raw: string) => {
    setValueRaw(raw);
    setValueError('');
    if (raw === '') return;
    const val = parseFloat(raw);
    if (!isNaN(val)) {
      update({ value: val });
    }
  };

  const validateValue = () => {
    if (valueRaw === '') {
      setValueError('Required');
      return;
    }
    const val = parseFloat(valueRaw);
    if (isNaN(val)) {
      setValueError('Invalid number');
    }
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 space-y-4">
      {/* Row 1: Indicator + Component + Operator + Value */}
      <div className="flex flex-wrap items-end gap-3">
        {/* Indicator */}
        <label className="flex flex-1 min-w-[140px] flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Indicator
          </span>
          <select
            value={condition.indicator}
            onChange={(e) => update({ indicator: e.target.value })}
            className="condition-field appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          >
            {indicators.map((ind) => (
              <option key={ind.name} value={ind.name}>
                {ind.name}
              </option>
            ))}
          </select>
          <span className="h-3 text-[10px] text-slate-400">
            {selected?.description
              ? `${selected.description}${selected.value_hint ? `, ${selected.value_hint}` : ''}`
              : '\u00A0'}
          </span>
        </label>

        {/* Component */}
        {components.length > 1 && (
          <label className="flex flex-col">
            <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
              Component
            </span>
            <select
              value={condition.component ?? components[0] ?? ''}
              onChange={(e) =>
                update({ component: e.target.value || null })
              }
              className="condition-field appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
            >
              {components.map((c) => (
                <option key={c} value={c}>
                  {formatComponent(c)}
                </option>
              ))}
            </select>
            <span className="h-3" />
          </label>
        )}

        {/* Operator */}
        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Operator
          </span>
          <select
            value={condition.operator}
            onChange={(e) => update({ operator: e.target.value as Operator })}
            className="condition-field appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          >
            {OPERATORS.map((op) => (
              <option key={op} value={op}>
                {op}
              </option>
            ))}
          </select>
          <span className="h-3" />
        </label>

        {/* Value */}
        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Value
          </span>
          <input
            type="text"
            inputMode="decimal"
            value={valueRaw}
            onChange={(e) => setValue(e.target.value)}
            onBlur={validateValue}
            className={`condition-field w-32 rounded-xl border px-3 py-2.5 text-sm tabular-nums transition-colors focus:outline-none focus:ring-2 ${
              valueError
                ? 'border-red-300 focus:border-red-400 focus:ring-red-400/20'
                : 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-emerald-400/20'
            }`}
          />
          <span className="h-3">
            {valueError && (
              <span className="text-[10px] text-red-500">{valueError}</span>
            )}
          </span>
        </label>

        {/* Interval */}
        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Interval
          </span>
          <select
            value={condition.interval}
            onChange={(e) => update({ interval: e.target.value })}
            className="condition-field appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          >
            <option value="5m">5 Minute</option>
            <option value="15m">15 Minute</option>
            <option value="30m">30 Minute</option>
            <option value="1h">1 Hour</option>
            <option value="1d">Daily</option>
            <option value="1wk">Weekly</option>
            <option value="1mo">Monthly</option>
            <option value="3mo">Quarterly</option>
          </select>
          <span className="h-3 text-[10px] text-slate-400">
            {['5m', '15m', '30m', '1h'].includes(condition.interval)
              ? 'Intraday data limited to 60 days (1h: 2 years)'
              : '\u00A0'}
          </span>
        </label>

        {/* Remove */}
        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="condition-field rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-100"
          >
            Remove
          </button>
        )}
      </div>

      {/* Row 2: Parameters */}
      {selected && selected.params.length > 0 && (
        <div className="flex flex-wrap items-end gap-3 border-t border-slate-200/60 pt-3">
          {selected.params.map((p) => (
            <label key={p.name} className="flex flex-col">
              <span className="mb-1 font-display text-xs font-medium text-slate-500">
                {formatParamName(p.name)}
              </span>
              <div className="flex items-center gap-1.5">
                <input
                  type="text"
                  inputMode={p.type === 'float' ? 'decimal' : 'numeric'}
                  value={paramRaw[p.name] ?? ''}
                  onChange={(e) => setParam(p.name, e.target.value)}
                  onBlur={() => validateParam(p.name)}
                  className={`w-20 rounded-lg border px-2.5 py-2 text-sm tabular-nums transition-colors focus:outline-none focus:ring-2 ${
                    paramErrors[p.name]
                      ? 'border-red-300 focus:border-red-400 focus:ring-red-400/20'
                      : 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-emerald-400/20'
                  }`}
                />
                {p.min !== undefined && p.max !== undefined && (
                  <span className="text-[10px] text-slate-400">
                    Default: {p.default}, {p.min}–{p.max}
                  </span>
                )}
              </div>
              {paramErrors[p.name] && (
                <span className="mt-0.5 text-[10px] text-red-500">
                  {paramErrors[p.name]}
                </span>
              )}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
