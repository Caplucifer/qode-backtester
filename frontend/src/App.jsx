import React, { useState, useEffect } from "react";
import StrategyForm from "./components/StrategyForm.jsx";
import MetricsCards from "./components/MetricsCards.jsx";
import EquityCurveChart from "./components/EquityCurveChart.jsx";
import DrawdownChart from "./components/DrawdownChart.jsx";
import WinnersLosers from "./components/WinnersLosers.jsx";
import PortfolioLogTable from "./components/PortfolioLogTable.jsx";
import { runBacktest, getAvailableMetrics } from "./api.js";

export default function App() {
  const [metrics, setMetrics] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAvailableMetrics()
      .then(setMetrics)
      .catch(() => setMetrics([])); // backend may not be running yet -- form has fallback defaults
  }, []);

  async function handleRun(payload) {
    setLoading(true);
    setError(null);
    try {
      const data = await runBacktest(payload);
      setResult(data);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(detail || "Failed to run backtest. Is the backend running on localhost:8000?");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink">
      {/* Header */}
      <header className="border-b border-line bg-panel/40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-accent/15 border border-accent/30 flex items-center justify-center">
              <span className="text-accent font-bold text-sm">Q</span>
            </div>
            <div>
              <h1 className="text-text font-semibold text-sm leading-tight">Qode Backtester</h1>
              <p className="text-mute text-[11px] leading-tight">Fundamental equity strategy engine</p>
            </div>
          </div>
          <span className="text-[11px] text-mute tabular border border-line rounded-full px-3 py-1">
            NSE · 100+ Universe
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6">
        {/* Sidebar: Strategy config */}
        <aside className="bg-panel border border-line rounded-xl p-5 lg:sticky lg:top-6 lg:self-start lg:max-h-[calc(100vh-3rem)] lg:overflow-y-auto">
          <StrategyForm metrics={metrics} onRun={handleRun} loading={loading} />
        </aside>

        {/* Results */}
        <section className="space-y-5">
          {error && (
            <div className="bg-accent2/10 border border-accent2/30 text-accent2 text-sm rounded-lg p-4">
              {error}
            </div>
          )}

          {!result && !error && !loading && (
            <div className="bg-panel border border-line rounded-xl p-10 text-center">
              <p className="text-mute text-sm">
                Configure your strategy on the left and click <span className="text-accent">Run Backtest</span> to see results.
              </p>
            </div>
          )}

          {loading && (
            <div className="bg-panel border border-line rounded-xl p-10 text-center">
              <p className="text-mute text-sm animate-pulse">Running backtest across the universe…</p>
            </div>
          )}

          {result && (
            <>
              <MetricsCards metrics={result.metrics} />
              <EquityCurveChart data={result.equity_curve} />
              <DrawdownChart data={result.drawdown} />
              <WinnersLosers winners={result.top_winners} losers={result.top_losers} />
              <PortfolioLogTable logs={result.portfolio_logs} />
            </>
          )}
        </section>
      </main>
    </div>
  );
}
