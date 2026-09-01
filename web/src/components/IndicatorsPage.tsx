import { useState } from 'react';
import {
  INDICATORS,
  INDICATOR_TYPES,
  TYPE_COLORS,
  type IndicatorType,
  type IndicatorData,
} from '../data/indicators';

function IndicatorAccordion({ indicator, expandAll }: { indicator: IndicatorData; expandAll: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const effectiveIsOpen = expandAll || isOpen;
  const colors = TYPE_COLORS[indicator.type];

  return (
    <div
      className={`border-b border-slate-200/60 last:border-0 transition-colors ${
        effectiveIsOpen ? 'bg-slate-50/50' : ''
      }`}
    >
      <button
        onClick={() => setIsOpen(!effectiveIsOpen)}
        className="flex w-full items-center justify-between py-4 text-left transition-colors hover:bg-slate-50/50"
      >
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${colors.bg} ${colors.text} ${colors.border} border`}
          >
            {indicator.type}
          </span>
          <span className="text-sm font-semibold text-slate-800">
            {indicator.name}
          </span>
        </div>
        <span
          className={`text-slate-400 transition-transform duration-200 ${
            effectiveIsOpen ? 'rotate-180' : ''
          }`}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4 6L8 10L12 6"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      </button>

      {effectiveIsOpen && (
        <div className="pb-5 animate-fade-in">
          {/* Description */}
          <p className="mb-4 text-sm leading-relaxed text-slate-600">
            {indicator.description}
          </p>

          {/* Interpretation */}
          <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              How to Read It
            </h4>
            <p className="text-sm leading-relaxed text-slate-600">
              {indicator.interpretation}
            </p>
          </div>

          {/* Signals */}
          <div className="mb-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4">
              <h4 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Bullish Signals
              </h4>
              <ul className="space-y-1.5">
                {indicator.bullishSignals.map((signal, i) => (
                  <li key={i} className="text-xs text-slate-600">
                    {signal}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-red-200 bg-red-50/50 p-4">
              <h4 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-red-600">
                <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                Bearish Signals
              </h4>
              <ul className="space-y-1.5">
                {indicator.bearishSignals.map((signal, i) => (
                  <li key={i} className="text-xs text-slate-600">
                    {signal}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Parameters */}
          <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Parameters
            </h4>
            <div className="space-y-2">
              {indicator.parameters.map((param) => (
                <div
                  key={param.name}
                  className="flex items-start justify-between gap-4 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-slate-700">
                      {param.name}
                    </code>
                    <span className="text-slate-500">{param.description}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400">
                    <span>
                      {param.min}–{param.max}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className="font-medium text-slate-600">
                      default: {param.default}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Best For & Similar */}
          <div className="mb-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Best For
              </h4>
              <p className="text-xs text-slate-600">{indicator.bestFor}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Similar Indicators
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {indicator.similarTo.map((name) => (
                  <span
                    key={name}
                    className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600"
                  >
                    {name}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Tips */}
          <div className="mb-4 rounded-xl border border-cyan-200 bg-cyan-50/50 p-4">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-cyan-600">
              Pro Tips
            </h4>
            <ul className="space-y-1.5">
              {indicator.tips.map((tip, i) => (
                <li key={i} className="text-xs text-slate-600">
                  {tip}
                </li>
              ))}
            </ul>
          </div>

          {/* Formula */}
          <div className="rounded-xl bg-slate-900 p-4">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Formula
            </h4>
            <pre className="mb-3 whitespace-pre-wrap font-mono text-xs text-slate-300">
              {indicator.formula}
            </pre>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
              Breakdown
            </h4>
            <p className="text-xs leading-relaxed text-slate-400">
              {indicator.formulaBreakdown}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export function IndicatorsPage() {
  const [activeType, setActiveType] = useState<IndicatorType | 'All'>('All');
  const [expandAll, setExpandAll] = useState(false);

  const filteredIndicators =
    activeType === 'All'
      ? INDICATORS
      : INDICATORS.filter((ind) => ind.type === activeType);

  const counts: Record<IndicatorType | 'All', number> = {
    All: INDICATORS.length,
    Momentum: INDICATORS.filter((i) => i.type === 'Momentum').length,
    Trend: INDICATORS.filter((i) => i.type === 'Trend').length,
    Volatility: INDICATORS.filter((i) => i.type === 'Volatility').length,
    Volume: INDICATORS.filter((i) => i.type === 'Volume').length,
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="font-display text-3xl font-bold tracking-tight text-slate-800">
          Technical{' '}
          <span className="bg-gradient-to-r from-emerald-500 to-cyan-500 bg-clip-text text-transparent">
            Indicators
          </span>
        </h1>
        <p className="mt-3 text-base text-slate-500">
          14 indicators with formulas, signals, and usage guidance
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-1.5">
          {(['All', ...INDICATOR_TYPES] as const).map((type) => (
            <button
              key={type}
              onClick={() => setActiveType(type)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                activeType === type
                  ? 'bg-slate-800 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {type}
              <span className="ml-1.5 text-slate-400">({counts[type]})</span>
            </button>
          ))}
        </div>
        <button
          onClick={() => setExpandAll(!expandAll)}
          className="text-xs text-slate-500 hover:text-slate-700"
        >
          {expandAll ? 'Collapse All' : 'Expand All'}
        </button>
      </div>

      {/* Indicators List */}
      <section className="rounded-2xl border border-slate-200/60 bg-white px-6 shadow-sm">
        <div className="divide-y divide-slate-200/60">
          {filteredIndicators.map((ind) => (
            <IndicatorAccordion key={ind.name} indicator={ind} expandAll={expandAll} />
          ))}
        </div>
      </section>
    </main>
  );
}
