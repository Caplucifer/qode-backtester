import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export default function DrawdownChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-panel border border-line rounded-lg p-4">
      <h3 className="text-sm font-semibold text-text mb-3">Drawdown</h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="ddGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#FF6B5E" stopOpacity={0} />
              <stop offset="100%" stopColor="#FF6B5E" stopOpacity={0.35} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#232938" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "#6B7385", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "#232938" }}
            minTickGap={40}
          />
          <YAxis
            tick={{ fill: "#6B7385", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${v}%`}
            width={45}
          />
          <Tooltip
            contentStyle={{ background: "#161B27", border: "1px solid #232938", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#6B7385" }}
            formatter={(value) => [`${value}%`, "Drawdown"]}
          />
          <Area type="monotone" dataKey="drawdown_pct" stroke="#FF6B5E" strokeWidth={1.5} fill="url(#ddGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
