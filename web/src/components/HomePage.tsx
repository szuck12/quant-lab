import { useEffect, useRef, useState } from 'react';
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts';
import { SectionRule } from './PageChrome';

const MOCK_EQUITY = [
  { period: 'W1', v: 10000 }, { period: 'W2', v: 10200 },
  { period: 'W3', v: 10150 }, { period: 'W4', v: 10400 },
  { period: 'W5', v: 10350 }, { period: 'W6', v: 10600 },
  { period: 'W7', v: 10500 }, { period: 'W8', v: 10800 },
  { period: 'W9', v: 10950 }, { period: 'W10', v: 10900 },
  { period: 'W11', v: 11100 }, { period: 'W12', v: 11300 },
  { period: 'W13', v: 11200 }, { period: 'W14', v: 11500 },
  { period: 'W15', v: 11700 }, { period: 'W16', v: 11650 },
  { period: 'W17', v: 11900 }, { period: 'W18', v: 12100 },
  { period: 'W19', v: 12000 }, { period: 'W20', v: 12300 },
  { period: 'W21', v: 12500 }, { period: 'W22', v: 12400 },
  { period: 'W23', v: 12700 }, { period: 'W24', v: 12900 },
  { period: 'W25', v: 12800 },
];
const FULL_HEADLINE = 'Backtest Technical Indicators';

function AnimatedCounter({ value, suffix = '' }: { value: number; suffix?: string }) {
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const [count, setCount] = useState(prefersReducedMotion ? value : 0);

  useEffect(() => {
    if (prefersReducedMotion) return;
    const duration = 1500;
    const steps = 30;
    const increment = value / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [prefersReducedMotion, value]);

  return (
    <span className="animate-count-up">
      {count}{suffix}
    </span>
  );
}

/* ===== INDICATOR TYPE COLOR MAP ===== */
const INDICATOR_TYPE_COLOR: Record<string, string> = {
  RSI: 'bg-emerald-400', MACD: 'bg-emerald-400', CCI: 'bg-emerald-400',
  ROC: 'bg-emerald-400', Stochastic: 'bg-emerald-400',
  SMA: 'bg-cyan-400', EMA: 'bg-cyan-400', ADX: 'bg-cyan-400',
  'Bollinger Bands': 'bg-amber-400', ATR: 'bg-amber-400',
  OBV: 'bg-rose-400', AV: 'bg-rose-400', RVOL: 'bg-rose-400', VWAP: 'bg-rose-400',
};

function TickerTape() {
  const items = [
    'RSI', 'MACD', 'Bollinger Bands', 'SMA', 'EMA', 'VWAP',
    'Stochastic', 'ADX', 'CCI', 'OBV', 'ROC', 'RVOL', 'AV', 'ATR',
  ];
  const groups = [items, items, items];

  return (
    <div className="ticker-tape relative border-y border-slate-200 bg-white/60 py-3">
      <div className="animate-ticker ticker-tape-inner" aria-hidden="true">
        {groups.map((group, groupIndex) => (
          <div key={groupIndex} className="ticker-tape-group">
            {group.map((name, i) => (
              <span key={`${name}-${i}`} className="inline-flex items-center gap-2 text-xs text-slate-400">
                <span className={`h-1 w-1 rounded-full ${INDICATOR_TYPE_COLOR[name] || 'bg-emerald-400'}`} />
                {name}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function ResultsPreview() {
  return (
    <div className="rounded-xl border border-navy-800 bg-navy-950 p-5">
      <div className="mb-3 flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-full bg-rose-500/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-500/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/60" />
        <span className="ml-2 text-[10px] text-slate-500">backtest results</span>
      </div>
      <div
        aria-label="Mock equity curve rising from ten thousand to twelve thousand eight hundred dollars"
        className="mx-auto mb-3 h-36 w-2/3 min-w-[240px]"
        role="img"
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={MOCK_EQUITY}
            margin={{ top: 8, right: 4, bottom: 0, left: 0 }}
          >
            <defs>
              <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="period"
              tick={{ fontSize: 9, fill: '#64748B' }}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              interval={5}
            />
            <YAxis
              width={34}
              tick={{ fontSize: 9, fill: '#64748B' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value: number) => `$${value / 1000}k`}
              domain={[10000, 13000]}
              ticks={[10000, 11000, 12000, 13000]}
            />
            <Area
              type="monotone"
              dataKey="v"
              stroke="#10B981"
              strokeWidth={2}
              fill="url(#equityFill)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-3">
        {[
          { label: 'Return', value: '+24.7%', color: 'text-emerald-400' },
          { label: 'Sharpe', value: '1.41', color: 'text-cyan-400' },
          { label: 'Win Rate', value: '62.3%', color: 'text-purple-400' },
        ].map((m) => (
          <div key={m.label} className="flex-1 rounded-lg bg-navy-900 px-3 py-2 text-center">
            <p className="text-[10px] text-slate-500">{m.label}</p>
            <p className={`font-display text-sm font-bold ${m.color}`}>{m.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function useStagger() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const children = entry.target.querySelectorAll('.stagger-child');
            children.forEach((child, i) => {
              setTimeout(() => child.classList.add('visible'), i * 100);
            });
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return ref;
}

export function HomePage({ onNavigate }: { onNavigate: (page: 'backtest' | 'indicators') => void }) {
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const [headlineText, setHeadlineText] = useState(
    prefersReducedMotion ? FULL_HEADLINE : '',
  );
  const [showCursor, setShowCursor] = useState(!prefersReducedMotion);
  const statsRef = useStagger();
  const howItWorksRef = useStagger();
  const whyRef = useStagger();
  const exploreRef = useStagger();

  useEffect(() => {
    if (prefersReducedMotion) return;
    let i = 0;
    const timer = setInterval(() => {
      if (i < FULL_HEADLINE.length) {
        setHeadlineText(FULL_HEADLINE.slice(0, i + 1));
        i++;
      } else {
        clearInterval(timer);
        setTimeout(() => setShowCursor(false), 1000);
      }
    }, 50);
    return () => clearInterval(timer);
  }, [prefersReducedMotion]);

  return (
    <main className="relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative px-6 pt-20 pb-12 md:pt-28 md:pb-16">
        <div className="relative mx-auto max-w-5xl">
          <div className="max-w-2xl">
            <p className="mb-4 font-mono text-xs font-medium tracking-widest text-emerald-600 uppercase">
              Quantitative Research Platform
            </p>
            <h1 className="font-display text-4xl font-bold tracking-tight text-slate-800 md:text-5xl lg:text-[3.4rem]">
              <span className="block">{headlineText.slice(0, 18)}</span>
              <span className="block text-emerald-600">
                {headlineText.slice(18)}
                {showCursor && (
                  <span className="animate-blink text-emerald-400">|</span>
                )}
              </span>
            </h1>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-500 md:text-lg">
              Test RSI, MACD, Bollinger Bands and more across S&P 500 stocks
              in seconds. Free, open source, and no account required.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <button
                onClick={() => onNavigate('backtest')}
                className="rounded-lg bg-emerald-600 px-5 py-2.5 font-display text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
              >
                Start Backtesting
              </button>
              <button
                onClick={() => onNavigate('indicators')}
                className="rounded-lg border border-slate-200 bg-white px-5 py-2.5 font-display text-sm font-semibold text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50"
              >
                Explore Indicators
              </button>
            </div>
          </div>

          {/* Results preview — right side on desktop */}
          <div className="mt-12 hidden md:block">
            <ResultsPreview />
          </div>
        </div>
      </section>

      {/* Ticker Tape */}
      <TickerTape />

      <SectionRule />

      {/* Stats Section */}
      <section className="px-6 py-14" ref={statsRef}>
        <div className="mx-auto max-w-4xl">
          <div className="grid grid-cols-1 gap-8 text-center sm:grid-cols-3">
            <div className="stagger-child">
              <div className="display-number text-emerald-600">
                <AnimatedCounter value={14} />
              </div>
              <p className="mt-2 font-display text-sm font-medium text-slate-600">
                Indicators
              </p>
              <p className="mt-1 text-xs text-slate-400">
                RSI, MACD, Bollinger Bands, and 11 more
              </p>
            </div>
            <div className="stagger-child">
              <div className="display-number text-cyan-600">
                <AnimatedCounter value={1} suffix="M+" />
              </div>
              <p className="mt-2 font-display text-sm font-medium text-slate-600">
                Indicator Combinations
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Parameters, thresholds, and intervals
              </p>
            </div>
            <div className="stagger-child">
              <div className="display-number text-purple-600">
                <AnimatedCounter value={100} suffix="%" />
              </div>
              <p className="mt-2 font-display text-sm font-medium text-slate-600">
                Free
              </p>
              <p className="mt-1 text-xs text-slate-400">
                No account, no fees, no limits
              </p>
            </div>
          </div>
        </div>
      </section>

      <SectionRule />

      {/* How It Works — split layout with connecting line */}
      <section className="px-6 py-16" ref={howItWorksRef}>
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-10 lg:grid-cols-5 lg:items-center">
            {/* Text side */}
            <div className="lg:col-span-2 stagger-child">
              <p className="mb-3 font-mono text-xs font-medium tracking-widest text-emerald-600 uppercase">
                How It Works
              </p>
              <h2 className="font-display text-2xl font-bold tracking-tight text-slate-800 md:text-3xl">
                From hypothesis to
                <br />
                results in three steps
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-slate-500">
                Configure your indicator conditions, run the backtest across
                hundreds of stocks, and review performance with equity curves,
                Sharpe ratios, and detailed trade logs.
              </p>
              <button
                onClick={() => onNavigate('backtest')}
                className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-600 transition-colors hover:text-emerald-700"
              >
                Try it now
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
            </div>

            {/* Visual side — stepped process with connecting line */}
            <div className="relative lg:col-span-3 space-y-4">
              {/* Vertical connecting line */}
              <div className="absolute left-5 top-6 bottom-6 w-0.5 bg-gradient-to-b from-emerald-300 via-cyan-300 to-purple-300 hidden lg:block" />
              {[
                {
                  step: '01',
                  title: 'Set Conditions',
                  desc: 'Choose indicators, parameters, and entry/exit thresholds',
                  color: 'bg-emerald-500',
                  borderColor: 'border-emerald-200',
                  hoverBorder: 'hover:border-emerald-400',
                },
                {
                  step: '02',
                  title: 'Run Backtest',
                  desc: 'Execute across S&P 500 universe, full results in seconds',
                  color: 'bg-cyan-500',
                  borderColor: 'border-cyan-200',
                  hoverBorder: 'hover:border-cyan-400',
                },
                {
                  step: '03',
                  title: 'Analyze Results',
                  desc: 'Equity curve, Sharpe ratio, win rate, and every trade',
                  color: 'bg-purple-500',
                  borderColor: 'border-purple-200',
                  hoverBorder: 'hover:border-purple-400',
                },
              ].map((item) => (
                <div
                  key={item.step}
                  className={`stagger-child flex items-start gap-4 rounded-xl border-l-3 ${item.borderColor} bg-white p-4 transition-all duration-300 hover:shadow-md hover:bg-slate-50/50 ${item.hoverBorder}`}
                >
                  <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${item.color} font-display text-sm font-bold text-white`}>
                    {item.step}
                  </div>
                  <div>
                    <h3 className="font-display text-sm font-semibold text-slate-800">
                      {item.title}
                    </h3>
                    <p className="mt-0.5 text-xs text-slate-500">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <SectionRule />

      {/* Why QuantLab */}
      <section className="px-6 py-16 bg-white/50" ref={whyRef}>
        <div className="mx-auto max-w-5xl">
          <p className="mb-3 text-center font-mono text-xs font-medium tracking-widest text-emerald-600 uppercase">
            Why QuantLab
          </p>
          <h2 className="mb-10 text-center font-display text-2xl font-bold tracking-tight text-slate-800">
            Built for serious backtesting
          </h2>

          <div className="grid gap-4 lg:grid-cols-3">
            {/* Large feature card */}
            <div className="stagger-child card-accent-hover rounded-xl border border-emerald-200 bg-emerald-50/50 p-6 lg:col-span-2 lg:row-span-2 lg:flex lg:flex-col lg:justify-between">
              <div>
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                  <svg className="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
                  </svg>
                </div>
                <h3 className="font-display text-lg font-bold text-slate-800">
                  14 Parameterizable Indicators
                </h3>
                <p className="mt-2 max-w-md text-sm leading-relaxed text-slate-600">
                  RSI, MACD, Bollinger Bands, Stochastic, ADX, CCI, OBV, ROC, RVOL,
                  AV, ATR, SMA, EMA, and VWAP. Each with configurable windows,
                  thresholds, and signal components.
                </p>
              </div>
              <div className="mt-5 flex flex-wrap gap-1.5">
                {['RSI', 'MACD', 'BB', 'Stoch', 'ADX', 'CCI', 'OBV', 'ROC', 'RVOL', 'AV', 'ATR', 'SMA', 'EMA', 'VWAP'].map((t) => (
                  <span key={t} className="rounded-md bg-emerald-100 px-1.5 py-0.5 font-mono text-[9px] font-medium text-emerald-700">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Small card 1 */}
            <div className="stagger-child card-accent-hover rounded-xl border border-cyan-200 bg-cyan-50/50 p-5">
              <div className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-100">
                <svg className="h-4 w-4 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                </svg>
              </div>
              <h3 className="font-display text-sm font-semibold text-slate-800">
                Full results in 3 seconds
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                Backtest across 500+ S&P 500 stocks without breaking a sweat.
              </p>
            </div>

            {/* Small card 2 */}
            <div className="stagger-child card-accent-hover rounded-xl border border-purple-200 bg-purple-50/50 p-5">
              <div className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-lg bg-purple-100">
                <svg className="h-4 w-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                </svg>
              </div>
              <h3 className="font-display text-sm font-semibold text-slate-800">
                Open source, MIT licensed
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                Transparent code on GitHub. Fork it, extend it, learn from it.
              </p>
            </div>
          </div>
        </div>
      </section>

      <SectionRule />

      {/* Page Previews */}
      <section className="px-6 py-16" ref={exploreRef}>
        <div className="mx-auto max-w-5xl">
          <p className="mb-3 text-center font-mono text-xs font-medium tracking-widest text-emerald-600 uppercase">
            Explore
          </p>
          <h2 className="mb-10 text-center font-display text-2xl font-bold tracking-tight text-slate-800">
            Two tools, one platform
          </h2>
          <div className="grid gap-5 md:grid-cols-2">
            <button
              type="button"
              onClick={() => onNavigate('backtest')}
              className="stagger-child card-accent-hover group w-full cursor-pointer rounded-xl border border-emerald-200 bg-white p-6 text-left transition-colors hover:border-emerald-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300/50"
            >
              <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-emerald-100 transition-colors group-hover:bg-emerald-200">
                <svg className="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
                </svg>
              </div>
              <h3 className="font-display text-base font-bold text-slate-800 group-hover:text-emerald-600 transition-colors">
                Backtest Engine
              </h3>
              <p className="mt-2 text-sm text-slate-500 leading-relaxed">
                Configure conditions, run backtests across S&P 500, and analyze
                results with equity curves and detailed metrics.
              </p>
              <span className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-emerald-600">
                Open backtester
                <svg className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </span>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('indicators')}
              className="stagger-child card-accent-hover group w-full cursor-pointer rounded-xl border border-cyan-200 bg-white p-6 text-left transition-colors hover:border-cyan-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/50"
            >
              <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-cyan-100 transition-colors group-hover:bg-cyan-200">
                <svg className="h-5 w-5 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
              </div>
              <h3 className="font-display text-base font-bold text-slate-800 group-hover:text-cyan-600 transition-colors">
                Indicator Reference
              </h3>
              <p className="mt-2 text-sm text-slate-500 leading-relaxed">
                14 technical indicators with formulas, signals, parameters,
                and practical usage guidance.
              </p>
              <span className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-cyan-600">
                Browse indicators
                <svg className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </span>
            </button>
          </div>
        </div>
      </section>

      <SectionRule />

      {/* Open Source Section */}
      <section className="px-6 py-16 bg-navy-950 text-white">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="mb-3 font-mono text-xs font-medium tracking-widest text-emerald-400 uppercase">
                Open Source
              </p>
              <h2 className="font-display text-2xl font-bold tracking-tight md:text-3xl">
                Transparent code,
                <br />
                no hidden fees
              </h2>
              <p className="mt-4 max-w-md text-sm leading-relaxed text-slate-400">
                QuantLab is built for traders who want to understand their
                indicators. Every line of code is on GitHub. No accounts, no
                paywalls, no tracking.
              </p>
              <a
                href="https://github.com/szuck12/quant-lab"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/50 px-5 py-2.5 font-display text-sm font-semibold text-white transition-colors hover:border-slate-600 hover:bg-slate-800"
              >
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
                View on GitHub
              </a>
            </div>
            <div className="hidden lg:block">
              <div className="code-block p-4 text-xs">
                <p className="text-slate-500"># Clone and run in 30 seconds</p>
                <p className="text-emerald-400">$</p>
                <p>git clone https://github.com/szuck12/quant-lab</p>
                <p className="text-emerald-400">$</p>
                <p>cd quant-lab</p>
                <p className="text-emerald-400">$</p>
                <p>pip install -r requirements.txt</p>
                <p className="text-emerald-400">$</p>
                <p>cd web &amp;&amp; npm install &amp;&amp; cd ..</p>
                <p className="text-emerald-400">$</p>
                <p>npm run dev</p>
                <p className="mt-2 text-slate-500"># runs both backend (:8000) and frontend (:5173)</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
