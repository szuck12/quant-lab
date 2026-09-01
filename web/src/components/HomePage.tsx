import { useState, useEffect } from 'react';

function FloatingDot({ delay, x, y, size, color }: { delay: number; x: number; y: number; size: number; color: string }) {
  return (
    <div
      className={`absolute rounded-full opacity-20 animate-float`}
      style={{
        left: `${x}%`,
        top: `${y}%`,
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: color,
        animationDelay: `${delay}s`,
      }}
    />
  );
}

function AnimatedCounter({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
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
  }, [value]);

  return (
    <span className="animate-count-up">
      {count}{suffix}
    </span>
  );
}

export function HomePage({ onNavigate }: { onNavigate: (page: 'backtest' | 'indicators') => void }) {
  const [isLoaded] = useState(true);

  return (
    <main className="relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative px-6 py-20 md:py-28">
        {/* Floating dots */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <FloatingDot delay={0} x={10} y={20} size={8} color="#10B981" />
          <FloatingDot delay={1} x={85} y={15} size={12} color="#06B6D4" />
          <FloatingDot delay={2} x={20} y={70} size={6} color="#8B5CF6" />
          <FloatingDot delay={3} x={75} y={60} size={10} color="#10B981" />
          <FloatingDot delay={4} x={50} y={85} size={8} color="#06B6D4" />
          <FloatingDot delay={5} x={90} y={40} size={6} color="#8B5CF6" />
          <FloatingDot delay={0.5} x={5} y={50} size={10} color="#10B981" />
          <FloatingDot delay={1.5} x={95} y={75} size={8} color="#06B6D4" />
        </div>

        <div className="relative mx-auto max-w-4xl text-center">
          <div className={`transition-all duration-1000 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <h1 className="font-display text-5xl md:text-6xl font-bold tracking-tight text-slate-800">
              Backtest{' '}
              <span className="bg-gradient-to-r from-emerald-500 via-cyan-500 to-purple-500 bg-clip-text text-transparent animate-gradient-rotate">
                Technical Indicators
              </span>
            </h1>
          </div>
          
          <div className={`mt-6 transition-all duration-1000 delay-200 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto">
              Test RSI, MACD, Bollinger Bands and more across S&P 500 stocks in seconds. 
              Free, open source, and no account required.
            </p>
          </div>

          <div className={`mt-8 flex flex-wrap items-center justify-center gap-4 transition-all duration-1000 delay-400 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <button
              onClick={() => onNavigate('backtest')}
              className="rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 px-6 py-3 font-display text-sm font-semibold text-white shadow-lg shadow-emerald-500/25 transition-all hover:shadow-xl hover:shadow-emerald-500/30 glow-emerald-hover"
            >
              Start Backtesting →
            </button>
            <button
              onClick={() => onNavigate('indicators')}
              className="rounded-xl border border-slate-200 bg-white px-6 py-3 font-display text-sm font-semibold text-slate-700 transition-all hover:bg-slate-50 hover:border-slate-300"
            >
              Explore Indicators
            </button>
          </div>

          <div className={`mt-8 flex flex-wrap items-center justify-center gap-6 text-sm text-slate-500 transition-all duration-1000 delay-500 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Backtest in seconds
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-cyan-500" />
              14 indicators
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-purple-500" />
              S&P 500 coverage
            </span>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="px-6 py-12 bg-white/50">
        <div className="mx-auto max-w-4xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="p-4">
              <div className="font-display text-3xl font-bold text-emerald-600">
                <AnimatedCounter value={500} suffix="+" />
              </div>
              <div className="mt-1 text-sm text-slate-500">S&P 500 Stocks</div>
            </div>
            <div className="p-4">
              <div className="font-display text-3xl font-bold text-cyan-600">
                <AnimatedCounter value={14} />
              </div>
              <div className="mt-1 text-sm text-slate-500">Indicators</div>
            </div>
            <div className="p-4">
              <div className="font-display text-3xl font-bold text-purple-600">
                <AnimatedCounter value={671} suffix="+" />
              </div>
              <div className="mt-1 text-sm text-slate-500">Tests Passing</div>
            </div>
            <div className="p-4">
              <div className="font-display text-3xl font-bold text-emerald-600">
                <AnimatedCounter value={0} suffix="%" />
              </div>
              <div className="mt-1 text-sm text-slate-500">Cost</div>
            </div>
          </div>
        </div>
      </section>

      {/* Why QuantLab Section */}
      <section className="px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-8 text-center font-display text-2xl font-bold text-slate-800">
            Why QuantLab
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: '⚡',
                title: 'Lightning Fast',
                description: 'Results in seconds across 500+ S&P 500 stocks',
                color: 'border-emerald-200 bg-emerald-50/50',
              },
              {
                icon: '📊',
                title: '14 Indicators',
                description: 'RSI, MACD, Bollinger Bands, and more',
                color: 'border-cyan-200 bg-cyan-50/50',
              },
              {
                icon: '🎯',
                title: 'Precision Control',
                description: 'Custom parameters, thresholds, and intervals',
                color: 'border-purple-200 bg-purple-50/50',
              },
              {
                icon: '📈',
                title: 'S&P 500 Universe',
                description: 'Test across the entire market automatically',
                color: 'border-emerald-200 bg-emerald-50/50',
              },
              {
                icon: '🔓',
                title: 'No Account Required',
                description: 'Start backtesting immediately, no signup needed',
                color: 'border-cyan-200 bg-cyan-50/50',
              },
              {
                icon: '💻',
                title: 'Open Source',
                description: 'Free forever, transparent code on GitHub',
                color: 'border-purple-200 bg-purple-50/50',
              },
            ].map((feature, index) => (
              <div
                key={feature.title}
                className={`rounded-2xl border p-5 card-hover ${feature.color} animate-stagger-${index + 1}`}
              >
                <span className="text-2xl">{feature.icon}</span>
                <h3 className="mt-3 font-display text-sm font-semibold text-slate-800">
                  {feature.title}
                </h3>
                <p className="mt-1 text-xs text-slate-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="px-6 py-16 bg-white/50">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-8 text-center font-display text-2xl font-bold text-slate-800">
            How It Works
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                step: '01',
                title: 'Set Conditions',
                description: 'Choose indicators, parameters, and thresholds',
                color: 'from-emerald-500 to-emerald-600',
              },
              {
                step: '02',
                title: 'Run Backtest',
                description: 'Execute across S&P 500 in seconds',
                color: 'from-cyan-500 to-cyan-600',
              },
              {
                step: '03',
                title: 'Analyze Results',
                description: 'Review equity curve, metrics, and trades',
                color: 'from-purple-500 to-purple-600',
              },
            ].map((item, index) => (
              <div
                key={item.step}
                className={`relative rounded-2xl border border-slate-200/60 bg-white p-6 shadow-sm card-hover animate-stagger-${index + 1}`}
              >
                <div
                  className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} text-base font-bold text-white`}
                >
                  {item.step}
                </div>
                <h3 className="font-display text-base font-semibold text-slate-800">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm text-slate-500">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Page Previews */}
      <section className="px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-8 text-center font-display text-2xl font-bold text-slate-800">
            Explore QuantLab
          </h2>
          <div className="grid gap-6 md:grid-cols-2">
            <div
              onClick={() => onNavigate('backtest')}
              className="group cursor-pointer rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-cyan-50 p-6 transition-all hover:shadow-lg hover:shadow-emerald-500/10 card-hover"
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 text-xl">
                ⚡
              </div>
              <h3 className="font-display text-lg font-semibold text-slate-800 group-hover:text-emerald-600 transition-colors">
                Backtest Engine
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Configure conditions, run backtests across S&P 500, and analyze results with equity curves and detailed metrics.
              </p>
              <div className="mt-4 text-sm font-medium text-emerald-600 group-hover:text-emerald-700">
                Start Backtesting →
              </div>
            </div>

            <div
              onClick={() => onNavigate('indicators')}
              className="group cursor-pointer rounded-2xl border border-cyan-200 bg-gradient-to-br from-cyan-50 to-purple-50 p-6 transition-all hover:shadow-lg hover:shadow-cyan-500/10 card-hover"
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-purple-500 text-xl">
                📊
              </div>
              <h3 className="font-display text-lg font-semibold text-slate-800 group-hover:text-cyan-600 transition-colors">
                Indicator Reference
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                14 technical indicators with formulas, signals, parameters, and usage guidance.
              </p>
              <div className="mt-4 text-sm font-medium text-cyan-600 group-hover:text-cyan-700">
                Explore Indicators →
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Open Source Banner */}
      <section className="px-6 py-12 bg-slate-900 text-white">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="font-display text-2xl font-bold">
            Free & Open Source
          </h2>
          <p className="mt-3 text-slate-400 max-w-xl mx-auto">
            QuantLab is built for traders who want to understand their indicators. 
            Transparent code, no hidden fees, no account required.
          </p>
          <a
            href="https://github.com/szuck12/quant-lab"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 font-display text-sm font-semibold text-slate-800 transition-all hover:bg-slate-100"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
            View on GitHub
          </a>
        </div>
      </section>
    </main>
  );
}