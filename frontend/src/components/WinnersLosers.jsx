import React from "react";

function StockRow({ symbol, stock_return, positive }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-line/50 last:border-0 min-w-0">
      <span className="text-sm text-text font-medium truncate pr-2">{symbol}</span>
      <span
        className={`font-mono text-sm font-semibold shrink-0 ${positive ? "text-accent" : "text-accent2"}`}
      >
        {(stock_return * 100).toFixed(2)}%
      </span>
    </div>
  );
}

export default function WinnersLosers({ winners, losers }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="bg-panel border border-line border-l-2 border-l-accent/50 rounded-md p-4 min-w-0">
        <p className="font-mono text-2xs tracking-wider text-mute2 uppercase mb-2">Top Winners</p>
        {winners?.length ? (
          winners.map((w) => <StockRow key={w.symbol} {...w} positive />)
        ) : (
          <p className="text-xs text-mute italic">No qualifying positions yet</p>
        )}
      </div>
      <div className="bg-panel border border-line border-l-2 border-l-accent2/50 rounded-md p-4 min-w-0">
        <p className="font-mono text-2xs tracking-wider text-mute2 uppercase mb-2">Top Losers</p>
        {losers?.length ? (
          losers.map((l) => <StockRow key={l.symbol} {...l} positive={l.stock_return >= 0} />)
        ) : (
          <p className="text-xs text-mute italic">No qualifying positions yet</p>
        )}
      </div>
    </div>
  );
}