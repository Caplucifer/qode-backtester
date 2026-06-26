"""
Stock universe: 100+ NSE-listed companies.
Symbols use the Yahoo Finance NSE suffix '.NS'.

This list spans large/mid/small cap across sectors so that
market-cap and fundamental filters in the backtest engine have
something meaningful to filter on.
"""

NSE_UNIVERSE = [
    # --- Banking & Financial Services ---
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
    "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "HDFCLIFE.NS", "SBILIFE.NS", "ICICIPRULI.NS",
    "ICICIGI.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "PFC.NS", "RECLTD.NS",

    # --- IT / Technology ---
    "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS",
    "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS", "LTTS.NS",

    # --- Oil, Gas & Energy ---
    "RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "GAIL.NS",
    "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "TATAPOWER.NS", "ADANIPOWER.NS",

    # --- FMCG ---
    "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
    "MARICO.NS", "GODREJCP.NS", "TATACONSUM.NS", "COLPAL.NS", "VBL.NS",

    # --- Auto ---
    "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "MOTHERSON.NS",

    # --- Pharma & Healthcare ---
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS",
    "AUROPHARMA.NS", "TORNTPHARM.NS", "ALKEM.NS", "APOLLOHOSP.NS", "MAXHEALTH.NS",

    # --- Metals & Mining ---
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JINDALSTEL.NS",
    "SAIL.NS", "NMDC.NS", "NATIONALUM.NS", "HINDZINC.NS", "APLAPOLLO.NS",

    # --- Cement & Construction ---
    "ULTRACEMCO.NS", "GRASIM.NS", "SHREECEM.NS", "AMBUJACEM.NS", "ACC.NS",
    "DALBHARAT.NS", "LT.NS", "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS",

    # --- Consumer Durables / Retail ---
    "TITAN.NS", "TRENT.NS", "DMART.NS", "HAVELLS.NS", "VOLTAS.NS",
    "WHIRLPOOL.NS", "CROMPTON.NS", "BATAINDIA.NS", "PAGEIND.NS", "RELAXO.NS",

    # --- Telecom & Media ---
    "BHARTIARTL.NS", "IDEA.NS", "INDUSTOWER.NS", "PVRINOX.NS", "ZEEL.NS",

    # --- Chemicals & Agro ---
    "PIDILITIND.NS", "UPL.NS", "SRF.NS", "AARTIIND.NS", "DEEPAKNTR.NS",
    "PIIND.NS", "NAVINFLUOR.NS", "ATUL.NS",

    # --- Capital Goods / Industrials ---
    "SIEMENS.NS", "ABB.NS", "CUMMINSIND.NS", "BEL.NS", "BHEL.NS",
    "ASTRAL.NS", "POLYCAB.NS", "KEI.NS", "THERMAX.NS", "AIAENG.NS",
]

# Deduplicate while preserving order, just in case
NSE_UNIVERSE = list(dict.fromkeys(NSE_UNIVERSE))

if __name__ == "__main__":
    print(f"Universe size: {len(NSE_UNIVERSE)} stocks")
