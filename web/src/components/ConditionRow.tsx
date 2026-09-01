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

    // Reset params when indicator changes
    if (fields.indicator && fields.indicator !== condition.indicator) {
      const ind = indicators.find((i) => i.name === fields.indicator);
      if (ind) {
        const params: Record<string, number> = {};
        ind.params.forEach((p) => (params[p.name] = p.default));
        next.params = params;
        next.component = null;
      }
    }

    // Reset component if not valid for new indicator
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
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 space-y-3">
      {/* Row 1: Indicator + Component + Operator + Value */}
      <div className="flex flex-wrap items-end gap-2">
        {/* Indicator */}
        <label className="flex flex-col text-xs text-gray-500">
          Indicator
          <select
            value={condition.indicator}
            onChange={(e) => update({ indicator: e.target.value })}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm font-medium"
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
          <label className="flex flex-col text-xs text-gray-500">
            Component
            <select
              value={condition.component ?? ''}
              onChange={(e) =>
                update({ component: e.target.value || null })
              }
              className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
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
        <label className="flex flex-col text-xs text-gray-500">
          Operator
          <select
            value={condition.operator}
            onChange={(e) => update({ operator: e.target.value as Operator })}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          >
            {OPERATORS.map((op) => (
              <option key={op} value={op}>
                {op}
              </option>
            ))}
          </select>
        </label>

        {/* Value */}
        <label className="flex flex-col text-xs text-gray-500">
          Value
          <input
            type="number"
            step="any"
            value={condition.value}
            onChange={(e) => update({ value: parseFloat(e.target.value) || 0 })}
            className="mt-1 w-24 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
          />
        </label>

        {/* Interval */}
        <label className="flex flex-col text-xs text-gray-500">
          Interval
          <select
            value={condition.interval}
            onChange={(e) => update({ interval: e.target.value })}
            className="mt-1 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
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
            className="rounded bg-red-100 px-2 py-1.5 text-xs text-red-600 hover:bg-red-200"
          >
            Remove
          </button>
        )}
      </div>

      {/* Row 2: Parameters + Value hint */}
      <div className="flex flex-wrap items-end gap-2">
        {/* Params */}
        {selected?.params.map((p) => (
          <label key={p.name} className="flex flex-col text-xs text-gray-500">
            <span className="font-medium">
              {p.name}
              {p.hint && (
                <span className="ml-1 font-normal text-gray-400">
                  ({p.hint})
                </span>
              )}
            </span>
            <div className="mt-1 flex items-center gap-1">
              <input
                type="number"
                step={p.type === 'float' ? '0.1' : '1'}
                min={p.min}
                max={p.max}
                value={condition.params[p.name] ?? p.default}
                onChange={(e) => setParam(p.name, e.target.value)}
                className="w-20 rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
              />
              {p.min !== undefined && p.max !== undefined && (
                <span className="text-[10px] text-gray-400">
                  {p.min}–{p.max}
                </span>
              )}
            </div>
          </label>
        ))}

        {/* Value hint */}
        {selected?.value_hint && (
          <span className="ml-auto text-[10px] text-gray-400 self-end pb-0.5">
            {selected.value_hint}
          </span>
        )}
      </div>
    </div>
  );
}
