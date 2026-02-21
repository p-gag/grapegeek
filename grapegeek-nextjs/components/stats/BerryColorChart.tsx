'use client';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ChartData {
  name: string;
  value: number;
}

interface BerryColorChartProps {
  data: ChartData[];
}

// Use colors matching actual berry colors
const COLOR_MAP: { [key: string]: string } = {
  'Red': '#dc2626',
  'White': '#fbbf24',
  'Black': '#1f2937',
  'Rose': '#f472b6',
  'Grey': '#9ca3af',
  'Blue': '#3b82f6',
  'Green': '#22c55e',
};

export default function BerryColorChart({ data }: BerryColorChartProps) {
  const getBarColor = (name: string): string => {
    return COLOR_MAP[name] || '#8b5cf6';
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
        <XAxis
          dataKey="name"
          tick={{ fill: '#6b7280', fontSize: 12 }}
          tickLine={{ stroke: '#e5e7eb' }}
        />
        <YAxis
          tick={{ fill: '#6b7280', fontSize: 12 }}
          tickLine={{ stroke: '#e5e7eb' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '8px 12px',
          }}
          labelStyle={{ color: '#111827', fontWeight: 600 }}
        />
        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.name)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
