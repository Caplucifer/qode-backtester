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
      {/* Header — terminal status bar */}
      <header className="border-b border-line bg-panel/60 backdrop-blur-sm">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 shrink-0 rounded border border-accent/40 bg-accent/10 flex items-center justify-center">
              <span className="text-accent font-mono font-bold text-xs">Q</span>
            </div>
            <div className="min-w-0">
              <h1 className="text-text font-semibold text-sm leading-tight truncate">Qode Backtester</h1>
              <p className="text-mute2 text-2xs leading-tight font-mono truncate">fundamental.equity.engine</p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-2xs font-mono text-mute shrink-0">
            <span className="flex items-center gap-1.5 border border-line rounded px-2.5 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              NSE
            </span>
            <span className="border border-line rounded px-2.5 py-1">123 SYMBOLS</span>
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-4 sm:px-6 py-6 sm:py-8 grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-5 sm:gap-6">
        {/* Sidebar: Strategy config */}
        <aside className="bg-panel border border-line rounded-lg p-4 sm:p-5 min-w-0 lg:sticky lg:top-6 lg:self-start lg:max-h-[calc(100vh-3rem)] lg:overflow-y-auto">
          <StrategyForm metrics={metrics} onRun={handleRun} loading={loading} />
        </aside>

        {/* Results */}
        <section className="space-y-4 sm:space-y-5 min-w-0">
          {error && (
            <div className="bg-accent2/10 border border-accent2/30 text-accent2 text-sm rounded-lg p-4 font-mono">
              {error}
            </div>
          )}

          {!result && !error && !loading && (
            <div className="bg-panel border border-line border-dashed rounded-lg p-10 sm:p-14 text-center">
              <p className="font-mono text-mute2 text-2xs tracking-widest mb-2">AWAITING INPUT</p>
              <p className="text-mute text-sm">
                Set your filters and ranking on the left, then run a backtest to see the equity curve and metrics here.
              </p>
            </div>
          )}

          {loading && (
            <div className="bg-panel border border-line rounded-lg p-10 sm:p-14 text-center">
              <p className="font-mono text-accent text-2xs tracking-widest mb-2 animate-pulse">RUNNING</p>
              <p className="text-mute text-sm">Walking the universe through each rebalance date…</p>
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