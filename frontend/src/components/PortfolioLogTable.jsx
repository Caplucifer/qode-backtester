import React, { useState } from "react";

function toCSV(rows) {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((h) => row[h]).join(","));
  }
  return lines.join("\n");
}

function downloadFile(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function PortfolioLogTable({ logs }) {
  const [page, setPage] = useState(0);
  const pageSize = 15;

  if (!logs || logs.length === 0) return null;

  const totalPages = Math.ceil(logs.length / pageSize);
  const pageRows = logs.slice(page * pageSize, page * pageSize + pageSize);

  function exportCSV() {
    const csv = toCSV(logs);
    downloadFile(csv, "portfolio_logs.csv", "text/csv");
  }

  // Simple "Excel" export: tab-separated values open cleanly in Excel,
  // saved with .xls extension (no extra library needed for this scope).
  function exportExcel() {
    if (!logs.length) return;
    const headers = Object.keys(logs[0]);
    const lines = [headers.join("\t")];
    for (const row of logs) {
      lines.push(headers.map((h) => row[h]).join("\t"));
    }
    downloadFile(lines.join("\n"), "portfolio_logs.xls", "application/vnd.ms-excel");
  }

  return (
    <div className="bg-panel border border-line rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-text">Portfolio Logs</h3>
        <div className="flex gap-2">
          <button onClick={exportCSV} className="text-xs border border-line rounded px-3 py-1.5 text-mute hover:text-accent hover:border-accent transition">
            Export CSV
          </button>
          <button onClick={exportExcel} className="text-xs border border-line rounded px-3 py-1.5 text-mute hover:text-accent hover:border-accent transition">
            Export Excel
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-mute uppercase text-[10px] tracking-wider border-b border-line">
              <th className="text-left py-2 px-2">Rebalance Date</th>
              <th className="text-left py-2 px-2">Symbol</th>
              <th className="text-right py-2 px-2">Weight</th>
              <th className="text-right py-2 px-2">Entry Price</th>
              <th className="text-right py-2 px-2">Exit Price</th>
              <th className="text-right py-2 px-2">Return</th>
            </tr>
          </thead>
          <tbody className="tabular">
            {pageRows.map((row, i) => (
              <tr key={i} className="border-b border-line/40 hover:bg-panel2/50">
                <td className="py-1.5 px-2 text-text">{row.rebalance_date}</td>
                <td className="py-1.5 px-2 text-text font-medium">{row.symbol}</td>
                <td className="py-1.5 px-2 text-right text-mute">{(row.weight * 100).toFixed(1)}%</td>
                <td className="py-1.5 px-2 text-right text-mute">{row.entry_price ?? "—"}</td>
                <td className="py-1.5 px-2 text-right text-mute">{row.exit_price ?? "—"}</td>
                <td className={`py-1.5 px-2 text-right font-semibold ${row.stock_return >= 0 ? "text-accent" : "text-accent2"}`}>
                  {(row.stock_return * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-3 text-xs text-mute">
        <span>
          Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, logs.length)} of {logs.length}
        </span>
        <div className="flex gap-2">
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
            className="border border-line rounded px-2 py-1 disabled:opacity-30 hover:text-accent hover:border-accent transition"
          >
            Prev
          </button>
          <button
            disabled={page >= totalPages - 1}
            onClick={() => setPage((p) => p + 1)}
            className="border border-line rounded px-2 py-1 disabled:opacity-30 hover:text-accent hover:border-accent transition"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
