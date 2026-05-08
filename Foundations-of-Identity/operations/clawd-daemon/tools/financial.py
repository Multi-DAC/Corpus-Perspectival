"""Financial tools — market data via yfinance and ccxt."""
import logging
from typing import Any

import config

logger = logging.getLogger("clawd.tools.financial")

TOOL_DEFINITIONS = [
    {
        "name": "market_data",
        "description": "Get financial market data. Stocks, crypto, commodities, forex, economic indicators. Uses yfinance and ccxt.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["price", "history", "technical", "crypto", "compare", "economic"],
                    "description": "Action: price (current), history (OHLCV), technical (indicators), crypto (crypto data), compare (multiple assets), economic (macro data)."
                },
                "symbols": {
                    "type": "string",
                    "description": "Ticker symbol(s). Comma-separated for multiple. Examples: 'AAPL', 'BTC/USDT', 'AAPL,MSFT,GOOGL'."
                },
                "period": {
                    "type": "string",
                    "description": "Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max. Default: 6mo."
                },
                "indicators": {
                    "type": "string",
                    "description": "Technical indicators: sma, ema, rsi, macd, bollinger, atr. Comma-separated."
                }
            },
            "required": ["action", "symbols"]
        }
    },
]


async def _market_data(input_data: dict) -> str:
    """Financial market data via yfinance and ccxt."""
    from tools.execution import _python_eval
    action = input_data["action"]
    symbols_str = input_data.get("symbols", "")
    period = input_data.get("period", "6mo")
    indicators = input_data.get("indicators", "")

    code = ""

    if action == "price":
        tickers = [s.strip() for s in symbols_str.split(",")]
        code = f"""
import yfinance as yf
tickers = {repr(tickers)}
for t in tickers:
    info = yf.Ticker(t).fast_info
    try:
        price = info.get('lastPrice') or info.get('regularMarketPrice', 'N/A')
        change = info.get('regularMarketChangePercent', 'N/A')
        cap = info.get('marketCap', 'N/A')
        print(f"{{t}}: ${{price}} ({{change:.2f}}% change, cap: ${{cap:,.0f}})" if isinstance(cap, (int,float)) else f"{{t}}: ${{price}}")
    except:
        data = yf.download(t, period='5d', progress=False)
        if len(data) > 0:
            last = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2] if len(data) > 1 else last
            chg = (last - prev) / prev * 100
            print(f"{{t}}: ${{last:.2f}} ({{chg:+.2f}}%)")
        else:
            print(f"{{t}}: No data available")
"""

    elif action == "history":
        tickers = [s.strip() for s in symbols_str.split(",")]
        code = f"""
import yfinance as yf
import pandas as pd
tickers = {repr(tickers)}
period = {repr(period)}
for t in tickers:
    df = yf.download(t, period=period, progress=False)
    if len(df) > 0:
        print(f"\\n=== {{t}} ({{period}}) ===")
        print(f"Period: {{df.index[0].strftime('%Y-%m-%d')}} to {{df.index[-1].strftime('%Y-%m-%d')}}")
        print(f"Open: ${{df['Open'].iloc[0]:.2f}} → Close: ${{df['Close'].iloc[-1]:.2f}}")
        ret = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        print(f"Return: {{ret:+.2f}}%")
        print(f"High: ${{df['High'].max():.2f}} | Low: ${{df['Low'].min():.2f}}")
        print(f"Avg Volume: {{df['Volume'].mean():,.0f}}")
        print(f"\\nLast 5 days:")
        print(df.tail().to_string())
    else:
        print(f"{{t}}: No data")
"""

    elif action == "technical":
        ticker = symbols_str.split(",")[0].strip()
        ind_list = [i.strip().lower() for i in indicators.split(",")] if indicators else ["sma", "rsi", "macd"]
        code = f"""
import yfinance as yf
import numpy as np
import pandas as pd

df = yf.download({repr(ticker)}, period={repr(period)}, progress=False)
if len(df) == 0:
    print("No data available")
else:
    close = df['Close'].values.flatten()
    results = []
    results.append(f"=== {{'{ticker}'}} Technical Analysis ===")
    results.append(f"Price: ${{close[-1]:.2f}} | Period: {period}")

    indicators = {repr(ind_list)}

    if 'sma' in indicators:
        sma20 = pd.Series(close).rolling(20).mean().iloc[-1]
        sma50 = pd.Series(close).rolling(50).mean().iloc[-1]
        sma200 = pd.Series(close).rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        results.append(f"SMA20: ${{sma20:.2f}} | SMA50: ${{sma50:.2f}}" + (f" | SMA200: ${{sma200:.2f}}" if sma200 else ""))
        results.append(f"  Price vs SMA20: {{'above' if close[-1] > sma20 else 'below'}} | vs SMA50: {{'above' if close[-1] > sma50 else 'below'}}")

    if 'rsi' in indicators:
        delta = pd.Series(close).diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1]
        signal = 'OVERBOUGHT' if rsi_val > 70 else 'OVERSOLD' if rsi_val < 30 else 'NEUTRAL'
        results.append(f"RSI(14): {{rsi_val:.1f}} [{{signal}}]")

    if 'macd' in indicators:
        ema12 = pd.Series(close).ewm(span=12).mean()
        ema26 = pd.Series(close).ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        results.append(f"MACD: {{macd_line.iloc[-1]:.4f}} | Signal: {{signal_line.iloc[-1]:.4f}} | Hist: {{histogram.iloc[-1]:.4f}}")
        results.append(f"  MACD trend: {{'bullish' if histogram.iloc[-1] > 0 else 'bearish'}}")

    if 'bollinger' in indicators:
        sma = pd.Series(close).rolling(20).mean()
        std = pd.Series(close).rolling(20).std()
        upper = sma + 2 * std
        lower = sma - 2 * std
        bb_pos = (close[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
        results.append(f"Bollinger: Upper ${{upper.iloc[-1]:.2f}} | Lower ${{lower.iloc[-1]:.2f}} | %B: {{bb_pos:.2f}}")

    if 'atr' in indicators:
        high = df['High'].values.flatten()
        low = df['Low'].values.flatten()
        tr = np.maximum(high[1:] - low[1:], np.abs(high[1:] - close[:-1]), np.abs(low[1:] - close[:-1]))
        atr = pd.Series(tr).rolling(14).mean().iloc[-1]
        results.append(f"ATR(14): ${{atr:.2f}} ({{atr/close[-1]*100:.1f}}% of price)")

    print('\\n'.join(results))
"""

    elif action == "crypto":
        symbol = symbols_str.strip()
        if "/" not in symbol:
            symbol = f"{symbol}/USDT"
        code = f"""
import ccxt
ex = ccxt.binance()
try:
    ticker = ex.fetch_ticker({repr(symbol)})
    print(f"=== {symbol} ===")
    print(f"Price: ${{ticker['last']:.4f}}")
    print(f"24h Change: {{ticker['percentage']:+.2f}}%")
    print(f"24h High: ${{ticker['high']:.4f}} | Low: ${{ticker['low']:.4f}}")
    print(f"24h Volume: ${{ticker['quoteVolume']:,.0f}}")
    print(f"Bid: ${{ticker['bid']:.4f}} | Ask: ${{ticker['ask']:.4f}}")
except Exception as e:
    print(f"Error fetching {symbol}: {{e}}")
"""

    elif action == "compare":
        tickers = [s.strip() for s in symbols_str.split(",")]
        code = f"""
import yfinance as yf
import pandas as pd
import numpy as np

tickers = {repr(tickers)}
period = {repr(period)}
data = yf.download(tickers, period=period, progress=False)

if 'Close' in data.columns:
    closes = data['Close']
else:
    closes = data

# Normalize to percentage returns from start
normalized = (closes / closes.iloc[0] - 1) * 100

print(f"=== Asset Comparison ({{period}}) ===\\n")
print("Performance:")
for t in tickers:
    col = closes[t] if len(tickers) > 1 else closes
    ret = (col.iloc[-1] / col.iloc[0] - 1) * 100
    vol = col.pct_change().std() * np.sqrt(252) * 100
    sharpe = (ret / vol) if vol > 0 else 0
    print(f"  {{t}}: {{ret:+.1f}}% return | {{vol:.1f}}% vol | {{sharpe:.2f}} Sharpe")

print(f"\\nCorrelation:")
if len(tickers) > 1:
    corr = closes.pct_change().corr()
    print(corr.round(3).to_string())
"""

    elif action == "economic":
        code = f"""
import yfinance as yf
import pandas as pd
# Economic proxies via ETFs
indicators = {{
    '^TNX': '10Y Treasury Yield',
    '^VIX': 'VIX (Fear Index)',
    'GLD': 'Gold',
    'USO': 'Oil',
    'UUP': 'US Dollar',
    'TLT': '20Y+ Treasury Bonds',
    'HYG': 'High Yield Corporate Bonds',
    'SPY': 'S&P 500',
}}
print("=== Economic Indicators (via ETF proxies) ===\\n")
for sym, name in indicators.items():
    try:
        data = yf.download(sym, period='5d', progress=False)
        if len(data) > 0:
            last = data['Close'].iloc[-1]
            prev = data['Close'].iloc[0]
            chg = (last - prev) / prev * 100
            print(f"  {{name:30s}} ${{last:>10.2f}}  ({{chg:+.2f}}%)")
    except Exception as e:
        print(f"  [warn] Failed to fetch market data for {{sym}}: {{e}}")
"""
    else:
        return f"Unknown market_data action: {action}"

    return await _python_eval({"code": code, "timeout": 60})


TOOL_HANDLERS = {"market_data": _market_data}
