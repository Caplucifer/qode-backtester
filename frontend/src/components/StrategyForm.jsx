import React, { useState } from "react";

const FREQUENCIES = ["monthly", "quarterly", "yearly"];
const SIZING_METHODS = [
  { value: "equal", label: "Equal Weighted" },
  { value: "market_cap", label: "Market Cap Weighted" },
  { value: "metric", label: "Metric Weighted" },
];

function FieldLabel({ children }) {
  return (
    <label className="block font-mono text-2xs uppercase tracking-wider text-mute2 mb-1.5">
      {children}
    </label>
  );
}

function TextInput(props) {
  return (
    <input
      {...props}
      className={`w-full bg-panel2 border border-line rounded-md px-3 py-2 text-sm text-text font-mono
                 focus:outline-none focus:ring-1 focus:ring-accent/60 focus:border-accent/60
                 placeholder:text-mute2/70 min-w-0 ${props.className || ""}`}
    />
  );
}

function Select({ value, onChange, options, ...props }) {
  return (
    <select
      value={value}
      onChange={onChange}
      {...props}
      className="w-full bg-panel2 border border-line rounded-md px-3 py-2 text-sm text-text
                 focus:outline-none focus:ring-1 focus:ring-accent/60 focus:border-accent/60 min-w-0"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

export default function StrategyForm({ metrics, onRun, loading }) {
  const [startDate, setStartDate] = useState("2020-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [frequency, setFrequency] = useState("quarterly");
  const [portfolioSize, setPortfolioSize] = useState(20);
  const [sizing, setSizing] = useState("equal");
  const [sizingMetric, setSizingMetric] = useState("roce");
  const [initialCapital, setInitialCapital] = useState(1000000);

  const [filters, setFilters] = useState([
    { metric: "market_cap", min_value: 10000, max_value: 300000 },
    { metric: "pat", min_value: 0, max_value: null },
  ]);

  const [rankRules, setRankRules] = useState([
    { metric: "roce", ascending: false, weight: 1 },
  ]);

  const metricOptions = metrics.length
    ? metrics.map((m) => ({ value: m.name, label: m.label }))
    : [{ value: "roce", label: "ROCE (%)" }];

  function updateFilter(idx, key, value) {
    setFilters((prev) =>
      prev.map((f, i) => (i === idx ? { ...f, [key]: value } : f))
    );
  }
  function addFilter() {
    setFilters((prev) => [...prev, { metric: metricOptions[0].value, min_value: null, max_value: null }]);
  }
  function removeFilter(idx) {
    setFilters((prev) => prev.filter((_, i) => i !== idx));
  }

  function updateRank(idx, key, value) {
    setRankRules((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, [key]: value } : r))
    );
  }
  function addRank() {
    setRankRules((prev) => [...prev, { metric: metricOptions[0].value, ascending: false, weight: 1 }]);
  }
  function removeRank(idx) {
    setRankRules((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onRun({
      start_date: startDate,
      end_date: endDate,
      rebalance_frequency: frequency,
      portfolio_size: Number(portfolioSize),
      position_sizing: sizing,
      sizing_metric: sizing === "metric" ? sizingMetric : null,
      initial_capital: Number(initialCapital),
      filters: filters
        .filter((f) => f.metric)
        .map((f) => ({
          metric: f.metric,
          min_value: f.min_value === "" || f.min_value === null ? null : Number(f.min_value),
          max_value: f.max_value === "" || f.max_value === null ? null : Number(f.max_value),
        })),
      rank_rules: rankRules
        .filter((r) => r.metric)
        .map((r) => ({
          metric: r.metric,
          ascending: !!r.ascending,
          weight: Number(r.weight) || 1,
        })),
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Date range + core params */}
      <section>
        <h3 className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
          <span className="font-mono text-accent">01</span> Period & Rebalancing
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <FieldLabel>Start Date</FieldLabel>
            <TextInput type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
          </div>
          <div>
            <FieldLabel>End Date</FieldLabel>
            <TextInput type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
          </div>
          <div>
            <FieldLabel>Rebalance Frequency</FieldLabel>
            <Select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              options={FREQUENCIES.map((f) => ({ value: f, label: f[0].toUpperCase() + f.slice(1) }))}
            />
          </div>
          <div>
            <FieldLabel>Portfolio Size</FieldLabel>
            <TextInput type="number" min="1" max="100" value={portfolioSize} onChange={(e) => setPortfolioSize(e.target.value)} required />
          </div>
        </div>
      </section>

      {/* Position sizing */}
      <section>
        <h3 className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
          <span className="font-mono text-accent">02</span> Position Sizing
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <FieldLabel>Method</FieldLabel>
            <Select value={sizing} onChange={(e) => setSizing(e.target.value)} options={SIZING_METHODS} />
          </div>
          {sizing === "metric" && (
            <div>
              <FieldLabel>Weighting Metric</FieldLabel>
              <Select value={sizingMetric} onChange={(e) => setSizingMetric(e.target.value)} options={metricOptions} />
            </div>
          )}
          <div>
            <FieldLabel>Initial Capital (₹)</FieldLabel>
            <TextInput type="number" min="1" value={initialCapital} onChange={(e) => setInitialCapital(e.target.value)} required />
          </div>
        </div>
      </section>

      {/* Filters */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-text flex items-center gap-2">
            <span className="font-mono text-accent">03</span> Filters
          </h3>
          <button type="button" onClick={addFilter} className="text-xs text-accent hover:underline">
            + Add filter
          </button>
        </div>
        <div className="space-y-2">
          {filters.map((f, idx) => (
            <div key={idx} className="bg-panel2/50 border border-line rounded-md p-2.5 space-y-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 min-w-0">
                  <Select value={f.metric} onChange={(e) => updateFilter(idx, "metric", e.target.value)} options={metricOptions} />
                </div>
                <button type="button" onClick={() => removeFilter(idx)} className="text-mute2 hover:text-accent2 px-1 text-sm shrink-0">
                  ✕
                </button>
              </div>
              <div className="flex items-center gap-2">
                <TextInput
                  type="number"
                  placeholder="min"
                  value={f.min_value ?? ""}
                  onChange={(e) => updateFilter(idx, "min_value", e.target.value)}
                  className="flex-1 min-w-0"
                />
                <span className="font-mono text-2xs text-mute2 shrink-0">TO</span>
                <TextInput
                  type="number"
                  placeholder="max"
                  value={f.max_value ?? ""}
                  onChange={(e) => updateFilter(idx, "max_value", e.target.value)}
                  className="flex-1 min-w-0"
                />
              </div>
            </div>
          ))}
          {filters.length === 0 && (
            <p className="text-xs text-mute italic">No filters configured — full universe will be ranked.</p>
          )}
        </div>
      </section>

      {/* Ranking */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-text flex items-center gap-2">
            <span className="font-mono text-accent">04</span> Ranking
          </h3>
          <button type="button" onClick={addRank} className="text-xs text-accent hover:underline">
            + Add metric
          </button>
        </div>
        <div className="space-y-2">
          {rankRules.map((r, idx) => (
            <div key={idx} className="bg-panel2/50 border border-line rounded-md p-2.5 space-y-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 min-w-0">
                  <Select value={r.metric} onChange={(e) => updateRank(idx, "metric", e.target.value)} options={metricOptions} />
                </div>
                <button type="button" onClick={() => removeRank(idx)} className="text-mute2 hover:text-accent2 px-1 text-sm shrink-0">
                  ✕
                </button>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-[2] min-w-0">
                  <Select
                    value={r.ascending ? "asc" : "desc"}
                    onChange={(e) => updateRank(idx, "ascending", e.target.value === "asc")}
                    options={[
                      { value: "desc", label: "Higher better" },
                      { value: "asc", label: "Lower better" },
                    ]}
                  />
                </div>
                <TextInput
                  type="number"
                  step="0.1"
                  placeholder="wt"
                  value={r.weight}
                  onChange={(e) => updateRank(idx, "weight", e.target.value)}
                  className="w-16 shrink-0"
                  title="Composite weight"
                />
              </div>
            </div>
          ))}
          {rankRules.length === 0 && (
            <p className="text-xs text-mute italic">Add at least one ranking metric to select top stocks.</p>
          )}
        </div>
        {rankRules.length > 1 && (
          <p className="text-[11px] text-mute mt-2">
            Composite score = average of weighted ranks across all metrics above.
          </p>
        )}
      </section>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-accent text-ink font-semibold text-sm py-3 rounded-md
                   hover:bg-accent/90 active:scale-[0.99] transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Running backtest…" : "Run Backtest"}
      </button>
    </form>
  );
}