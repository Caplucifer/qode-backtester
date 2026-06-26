import React from "react";

function Card({ label, value, accent }) {
  return (
    <div className="bg-panel border border-line rounded-lg p-4 flex flex-col gap-1">
      <span className="text-[11px] uppercase tracking-wider text-mute font-medium">{label}</span>
      <span className={`text-2xl font-semibold tabular ${accent || "text-text"}`}>{value}</span>
    </div>
  );
}

export default function MetricsCards({ metrics }) {
  if (!metrics) return null;

  const cagrColor = metrics.cagr >= 0 ? "text-accent" : "text-accent2";
  const ddColor = "text-accent2";

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <Card label="CAGR" value={`${metrics.cagr}%`} accent={cagrColor} />
      <Card label="Sharpe Ratio" value={metrics.sharpe_ratio} />
      <Card label="Max Drawdown" value={`${metrics.max_drawdown}%`} accent={ddColor} />
      <Card label="Total Return" value={`${metrics.total_return_pct}%`} accent={cagrColor} />
      <Card
        label="Final Value"
        value={`₹${Number(metrics.final_portfolio_value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`}
      />
      <Card label="Rebalances" value={metrics.num_rebalances} />
    </div>
  );
}
