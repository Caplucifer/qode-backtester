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

export default function EquityCurveChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-panel border border-line rounded-lg p-4">
      <h3 className="text-sm font-semibold text-text mb-3">Equity Curve</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3FE0A5" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#3FE0A5" stopOpacity={0} />
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
            tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
            width={60}
          />
          <Tooltip
            contentStyle={{ background: "#161B27", border: "1px solid #232938", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#6B7385" }}
            formatter={(value) => [`₹${Number(value).toLocaleString("en-IN")}`, "Portfolio Value"]}
          />
          <Area type="monotone" dataKey="value" stroke="#3FE0A5" strokeWidth={2} fill="url(#equityGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
