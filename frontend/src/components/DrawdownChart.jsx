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
    <div className="bg-panel border border-line rounded-lg p-4 sm:p-5 min-w-0">
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-sm font-semibold text-text">Drawdown</h3>
        <span className="font-mono text-2xs text-mute2">PEAK-TO-TROUGH</span>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="ddGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F2545B" stopOpacity={0} />
              <stop offset="100%" stopColor="#F2545B" stopOpacity={0.3} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#232938" strokeDasharray="2 4" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "#5B6472", fontSize: 10, fontFamily: "JetBrains Mono" }}
            tickLine={false}
            axisLine={{ stroke: "#232938" }}
            minTickGap={50}
          />
          <YAxis
            tick={{ fill: "#5B6472", fontSize: 10, fontFamily: "JetBrains Mono" }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${v}%`}
            width={40}
          />
          <Tooltip
            contentStyle={{
              background: "#171C25",
              border: "1px solid #232938",
              borderRadius: 6,
              fontSize: 12,
              fontFamily: "JetBrains Mono",
            }}
            labelStyle={{ color: "#7B8496" }}
            formatter={(value) => [`${value}%`, "Drawdown"]}
          />
          <Area type="monotone" dataKey="drawdown_pct" stroke="#F2545B" strokeWidth={1.5} fill="url(#ddGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}