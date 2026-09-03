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

  const update = (fields: Partial<ConditionRequest>) => {
    const next = { ...condition, ...fields };

    if (fields.indicator && fields.indicator !== condition.indicator) {
      const ind = indicators.find((i) => i.name === fields.indicator);
      if (ind) {
        const params: Record<string, number> = {};
        ind.params.forEach((p) => (params[p.name] = p.default));
        next.params = params;
        next.component = null;
      }
    }

    if (next.component && !components.includes(next.component)) {
      next.component = null;
    }

    onChange(index, next);
  };

  const setParam = (name: string, raw: string) => {
    const val = parseFloat(raw);
    if (isNaN(val)) return;
    update({ params: { ...condition.params, [name]: val } });
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
            className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          >
            {indicators.map((ind) => (
              <option key={ind.name} value={ind.name}>
                {ind.name}
              </option>
            ))}
          </select>
        </label>

        {/* Component */}
        {components.length > 1 && (
          <label className="flex flex-col">
            <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
              Component
            </span>
            <select
              value={condition.component ?? ''}
              onChange={(e) =>
                update({ component: e.target.value || null })
              }
              className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
            >
              <option value="">value</option>
              {components.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
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
            className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          >
            {OPERATORS.map((op) => (
              <option key={op} value={op}>
                {op}
              </option>
            ))}
          </select>
        </label>

        {/* Value */}
        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Value
          </span>
          <input
            type="text"
            inputMode="decimal"
            value={condition.value}
            onChange={(e) => update({ value: parseFloat(e.target.value) || 0 })}
            className="w-24 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm tabular-nums transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          />
        </label>

        {/* Interval */}
        <label className="flex flex-col">
          <span className="mb-1.5 font-display text-xs font-medium text-slate-500">
            Interval
          </span>
          <select
            value={condition.interval}
            onChange={(e) => update({ interval: e.target.value })}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
          >
            <option value="1d">Daily</option>
            <option value="1wk">Weekly</option>
            <option value="1mo">Monthly</option>
          </select>
        </label>

        {/* Remove */}
        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-100"
          >
            Remove
          </button>
        )}
      </div>

      {/* Row 2: Parameters + Value hint */}
      <div className="flex flex-wrap items-end gap-3 border-t border-slate-200/60 pt-3">
        {/* Params */}
        {selected?.params.map((p) => (
          <label key={p.name} className="flex flex-col">
            <span className="mb-1 font-display text-xs font-medium text-slate-500">
              {p.name}
              {p.hint && (
                <span className="ml-1 font-normal text-slate-400">
                  ({p.hint})
                </span>
              )}
            </span>
            <div className="flex items-center gap-1.5">
              <input
                type="number"
                step={p.type === 'float' ? '0.1' : '1'}
                min={p.min}
                max={p.max}
                value={condition.params[p.name] ?? p.default}
                onChange={(e) => setParam(p.name, e.target.value)}
                className="w-20 rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-sm tabular-nums transition-colors focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
              />
              {p.min !== undefined && p.max !== undefined && (
                <span className="text-[10px] text-slate-400">
                  {p.min}–{p.max}
                </span>
              )}
            </div>
          </label>
        ))}

        {/* Value hint */}
        {selected?.value_hint && (
          <span className="ml-auto self-end pb-2 text-[10px] text-slate-400">
            {selected.value_hint}
          </span>
        )}
      </div>
    </div>
  );
}
