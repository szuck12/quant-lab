import { useState, useCallback } from 'react';
import {
  INDICATORS,
  INDICATOR_TYPES,
  type IndicatorType,
  type IndicatorData,
} from '../data/indicators';
import { SectionRule } from './PageChrome';

const TYPE_ACCENT: Record<IndicatorType, string> = {
  Momentum: 'border-l-emerald-500',
  Trend: 'border-l-cyan-500',
  Volatility: 'border-l-amber-500',
  Volume: 'border-l-rose-500',
};

const TYPE_BADGE: Record<IndicatorType, string> = {
  Momentum: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Trend: 'bg-cyan-50 text-cyan-700 border-cyan-200',
  Volatility: 'bg-amber-50 text-amber-700 border-amber-200',
  Volume: 'bg-rose-50 text-rose-700 border-rose-200',
};

const TYPE_TAB_ACTIVE: Record<IndicatorType, string> = {
  Momentum: 'bg-emerald-600 text-white',
  Trend: 'bg-cyan-600 text-white',
  Volatility: 'bg-amber-600 text-white',
  Volume: 'bg-rose-600 text-white',
};

const TYPE_GLOW: Record<IndicatorType, string> = {
  Momentum: 'hover:shadow-[0_0_12px_-6px_rgba(16,185,129,0.12)]',
  Trend: 'hover:shadow-[0_0_12px_-6px_rgba(6,182,212,0.12)]',
  Volatility: 'hover:shadow-[0_0_12px_-6px_rgba(245,158,11,0.12)]',
  Volume: 'hover:shadow-[0_0_12px_-6px_rgba(244,63,94,0.12)]',
};

function IndicatorAccordion({
  indicator,
  isOpen,
  onToggle,
}: {
  indicator: IndicatorData;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const accent = TYPE_ACCENT[indicator.type];
  const badge = TYPE_BADGE[indicator.type];
  const glow = TYPE_GLOW[indicator.type];

  const components = indicator.formulaComponents.split('|');
  const panelId = `indicator-panel-${indicator.name.toLowerCase()}`;
  const buttonId = `indicator-button-${indicator.name.toLowerCase()}`;

  return (
    <div
      className={`border-b border-slate-200/60 last:border-0 border-l-[3px]
        transition-colors ${accent} ${isOpen ? 'bg-slate-50/60' : ''}`}
    >
      <button
        onClick={onToggle}
        aria-expanded={isOpen}
        aria-controls={panelId}
        id={buttonId}
        className={`flex w-full items-center justify-between py-4 px-4
          text-left transition-colors active:bg-slate-100
          focus-visible:outline-none focus-visible:ring-2
          focus-visible:ring-inset focus-visible:ring-emerald-300/40
          hover:bg-slate-50/40 ${glow}`}
      >
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium ${badge}`}
          >
            {indicator.type}
          </span>
          <span className="font-display text-sm font-semibold text-slate-800">
            {indicator.name}
          </span>
        </div>
        <span
          className={`text-slate-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
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

      {isOpen && (
        <div
          aria-labelledby={buttonId}
          className="px-4 pt-3 pb-5 animate-fade-in"
          id={panelId}
          role="region"
        >
          {/* Description */}
          <p className="mb-4 text-sm leading-relaxed text-slate-600">
            {indicator.description}
          </p>

          {/* Interpretation */}
          <div className="mb-4 rounded-lg border border-slate-200 bg-white p-4">
            <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-slate-500">
              How to Read It
            </h4>
            <p className="text-sm leading-relaxed text-slate-600">
              {indicator.interpretation}
            </p>
          </div>

          {/* Signals */}
          <div className="mb-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 p-4">
              <h4 className="mb-2 flex items-center gap-1.5 font-display text-xs font-semibold uppercase tracking-wider text-emerald-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Bullish Signals
              </h4>
              <ul className="space-y-1.5">
                {indicator.bullishSignals.map((signal, i) => (
                  <li key={i} className="text-xs text-slate-600">{signal}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-lg border border-rose-200 bg-rose-50/60 p-4">
              <h4 className="mb-2 flex items-center gap-1.5 font-display text-xs font-semibold uppercase tracking-wider text-rose-600">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
                Bearish Signals
              </h4>
              <ul className="space-y-1.5">
                {indicator.bearishSignals.map((signal, i) => (
                  <li key={i} className="text-xs text-slate-600">{signal}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Parameters */}
          <div className="mb-4 rounded-lg border border-slate-200 bg-white p-4">
            <h4 className="mb-3 font-display text-xs font-semibold uppercase tracking-wider text-slate-500">
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
                    <span>{param.min}–{param.max}</span>
                    <span className="text-slate-300">|</span>
                    <span className="font-medium text-slate-600">default: {param.default}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Best For & Similar */}
          <div className="mb-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-slate-500">
                Best For
              </h4>
              <p className="text-xs text-slate-600">{indicator.bestFor}</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-slate-500">
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
          <div className="mb-4 rounded-lg border border-cyan-200 bg-cyan-50/60 p-4">
            <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-cyan-600">
              Pro Tips
            </h4>
            <ul className="space-y-1.5">
              {indicator.tips.map((tip, i) => (
                <li key={i} className="text-xs text-slate-600">{tip}</li>
              ))}
            </ul>
          </div>

          {/* Formula — 3 sections */}
          <div className="rounded-lg bg-slate-900 p-4">
            {/* Formula */}
            <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Formula
            </h4>
            <pre className="mb-4 whitespace-pre-wrap font-mono text-xs text-slate-300">
              {indicator.formula}
            </pre>

            {/* Components */}
            <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-cyan-400">
              Components
            </h4>
            <div className="mb-4 space-y-1">
              {components.map((comp) => {
                const eqIndex = comp.indexOf(' = ');
                if (eqIndex === -1) return null;
                const sym = comp.slice(0, eqIndex);
                const desc = comp.slice(eqIndex + 3);
                return (
                  <div key={sym} className="flex gap-2 text-xs">
                    <code className="shrink-0 text-emerald-400 font-mono">{sym}</code>
                    <span className="text-slate-400">= {desc}</span>
                  </div>
                );
              })}
            </div>

            {/* Breakdown */}
            <h4 className="mb-2 font-display text-xs font-semibold uppercase tracking-wider text-purple-400">
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
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());

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

  const openCount = filteredIndicators.filter((ind) => openIds.has(ind.name)).length;
  const totalCount = filteredIndicators.length;
  const showExpand = openCount <= Math.floor(totalCount / 2);

  const toggleAccordion = useCallback((name: string) => {
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  }, []);

  const handleExpandAll = useCallback(() => {
    if (showExpand) {
      setOpenIds(new Set(filteredIndicators.map((i) => i.name)));
    } else {
      setOpenIds(new Set());
    }
  }, [showExpand, filteredIndicators]);

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      {/* Accent line */}
      <div className="mb-8 h-0.5 w-16 rounded-full bg-emerald-500" />

      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight text-slate-800">
          Technical{' '}
          <span className="text-emerald-600">
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
          <button
            onClick={() => setActiveType('All')}
            aria-pressed={activeType === 'All'}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
              activeType === 'All'
                ? 'bg-slate-800 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All
            <span className="ml-1.5 text-slate-400">({counts.All})</span>
          </button>
          {INDICATOR_TYPES.map((type) => (
            <button
              key={type}
              onClick={() => setActiveType(type)}
              aria-pressed={activeType === type}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                activeType === type
                  ? TYPE_TAB_ACTIVE[type]
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {type}
              <span className="ml-1.5 opacity-70">({counts[type]})</span>
            </button>
          ))}
        </div>
        <button
          onClick={handleExpandAll}
          className="text-xs font-medium text-slate-500 hover:text-slate-700"
        >
          {showExpand ? 'Expand All' : 'Collapse All'}
        </button>
      </div>

      <SectionRule />

      {/* Indicators List */}
      <section className="border border-slate-200 bg-white shadow-sm">
        <div className="divide-y divide-slate-200/60">
          {filteredIndicators.map((ind) => (
            <IndicatorAccordion
              key={ind.name}
              indicator={ind}
              isOpen={openIds.has(ind.name)}
              onToggle={() => toggleAccordion(ind.name)}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
