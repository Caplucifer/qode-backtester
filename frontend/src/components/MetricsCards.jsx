import React from "react";

function Card({ label, value, tone }) {
  const toneClass =
    tone === "up" ? "text-accent" : tone === "down" ? "text-accent2" : "text-text";
  const borderClass =
    tone === "up" ? "border-l-accent/60" : tone === "down" ? "border-l-accent2/60" : "border-l-line2";

  return (
    <div
      className={`bg-panel border border-line border-l-2 ${borderClass} rounded-md px-3.5 py-3 min-w-0`}
    >
      <p className="font-mono text-2xs tracking-wider text-mute2 uppercase truncate">{label}</p>
      <p
        className={`font-mono font-semibold ${toneClass} text-base sm:text-lg lg:text-xl mt-1 truncate`}
        title={String(value)}
      >
        {value}
      </p>
    </div>
  );
}

export default function MetricsCards({ metrics }) {
  if (!metrics) return null;

  const cagrTone = metrics.cagr >= 0 ? "up" : "down";

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
      <Card label="CAGR" value={`${metrics.cagr}%`} tone={cagrTone} />
      <Card label="Sharpe" value={metrics.sharpe_ratio} />
      <Card label="Max DD" value={`${metrics.max_drawdown}%`} tone="down" />
      <Card label="Total Return" value={`${metrics.total_return_pct}%`} tone={cagrTone} />
      <Card
        label="Final Value"
        value={`₹${Number(metrics.final_portfolio_value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`}
      />
      <Card label="Rebalances" value={metrics.num_rebalances} />
    </div>
  );
}