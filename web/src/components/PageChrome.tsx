import type { CSSProperties } from 'react';

const DOTS = [
  [8, 15, '0s'], [22, 25, '2s'], [45, 10, '4s'], [60, 30, '1s'],
  [78, 18, '3s'], [92, 28, '5s'], [15, 55, '6s'], [35, 65, '2.5s'],
  [55, 50, '1.5s'], [72, 60, '4.5s'], [88, 48, '3.5s'],
] as const;

const CONNECTIONS = [
  [8, 15, 22, 25], [45, 10, 60, 30], [78, 18, 92, 28],
  [15, 55, 35, 65], [55, 50, 72, 60],
] as const;

export function PageAtmosphere() {
  return (
    <div
      aria-hidden="true"
      className="page-atmosphere pointer-events-none absolute inset-0 min-h-screen overflow-hidden"
    >
      <div className="absolute top-10 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-emerald-500/[0.04] blur-3xl animate-gradient-drift" />
      <svg
        className="absolute inset-0 h-full w-full opacity-40"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        {DOTS.map(([cx, cy, delay]) => (
          <circle
            key={`${cx}-${cy}`}
            cx={cx}
            cy={cy}
            r="0.4"
            fill="#10B981"
            className="constellation-dot"
            style={{ '--delay': delay } as CSSProperties}
          />
        ))}
        {CONNECTIONS.map(([x1, y1, x2, y2], index) => (
          <line
            key={index}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke={index % 2 ? '#06B6D4' : '#10B981'}
            strokeWidth="0.1"
            opacity="0.3"
          />
        ))}
      </svg>
    </div>
  );
}

export function SectionRule() {
  return (
    <div
      aria-hidden="true"
      className="mx-auto flex w-full items-center px-6 py-2"
    >
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-slate-200 to-transparent" />
    </div>
  );
}
