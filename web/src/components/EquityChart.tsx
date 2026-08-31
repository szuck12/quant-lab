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
  return d.length > 7 ? d.slice(5) : d; // MM-DD
}

export function EquityChart({ data }: Props) {
  if (!data.length) return null;

  const formatted = data.map((p) => ({
    ...p,
    label: formatDate(p.date),
  }));

  return (
    <div className="w-full">
      <h3 className="mb-2 text-sm font-medium text-gray-700">Equity Curve</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={formatted}>
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11 }}
            interval="preserveStartEnd"
            minTickGap={40}
          />
          <YAxis
            tick={{ fontSize: 11 }}
            tickFormatter={(v: number) =>
              v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v.toFixed(0)
            }
          />
          <Tooltip
            formatter={(value: unknown, name: unknown) => [
              `$${Number(value).toLocaleString()}`,
              String(name),
            ]}
            labelFormatter={(label: unknown) => `Date: ${String(label)}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="strategy"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            name="Strategy"
          />
          <Line
            type="monotone"
            dataKey="benchmark"
            stroke="#9ca3af"
            strokeWidth={1.5}
            dot={false}
            strokeDasharray="4 4"
            name="Benchmark"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
