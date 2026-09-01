import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { EquityPoint } from '../types';

interface Props {
  data: EquityPoint[];
}

function formatDate(d: string) {
  return d.length > 7 ? d.slice(5) : d;
}

function formatCurrency(value: number) {
  return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
}

export function EquityChart({ data }: Props) {
  if (!data.length) return null;

  const formatted = data.map((p) => ({
    ...p,
    label: formatDate(p.date),
  }));

  return (
    <div className="w-full">
      <h3 className="mb-4 font-display text-sm font-semibold text-slate-700">
        Equity Curve
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={formatted}>
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: '#64748B' }}
            tickLine={false}
            axisLine={{ stroke: '#E2E8F0' }}
            interval="preserveStartEnd"
            minTickGap={40}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748B' }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v: number) =>
              v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v.toFixed(0)
            }
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              padding: '12px 16px',
            }}
            formatter={(value: unknown, name: unknown) => [
              formatCurrency(Number(value)),
              String(name),
            ]}
            labelFormatter={(label: unknown) => `Date: ${String(label)}`}
          />
          <Legend
            wrapperStyle={{ paddingTop: '16px' }}
            iconType="circle"
            iconSize={8}
          />
          <Line
            type="monotone"
            dataKey="strategy"
            stroke="#10B981"
            strokeWidth={2.5}
            dot={false}
            name="Strategy"
          />
          <Line
            type="monotone"
            dataKey="benchmark"
            stroke="#94A3B8"
            strokeWidth={1.5}
            dot={false}
            strokeDasharray="6 4"
            name="Benchmark"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
