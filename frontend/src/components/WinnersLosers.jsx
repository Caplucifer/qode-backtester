import React from "react";

function StockRow({ symbol, stock_return, positive }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-line/60 last:border-0">
      <span className="text-sm text-text font-medium">{symbol}</span>
      <span className={`text-sm tabular font-semibold ${positive ? "text-accent" : "text-accent2"}`}>
        {(stock_return * 100).toFixed(2)}%
      </span>
    </div>
  );
}

export default function WinnersLosers({ winners, losers }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="bg-panel border border-line rounded-lg p-4">
        <h3 className="text-sm font-semibold text-text mb-2">Top Winners</h3>
        {winners?.length ? (
          winners.map((w) => <StockRow key={w.symbol} {...w} positive />)
        ) : (
          <p className="text-xs text-mute italic">No data</p>
        )}
      </div>
      <div className="bg-panel border border-line rounded-lg p-4">
        <h3 className="text-sm font-semibold text-text mb-2">Top Losers</h3>
        {losers?.length ? (
          losers.map((l) => <StockRow key={l.symbol} {...l} positive={l.stock_return >= 0} />)
        ) : (
          <p className="text-xs text-mute italic">No data</p>
        )}
      </div>
    </div>
  );
}
