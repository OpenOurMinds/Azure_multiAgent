"""Technical Analyst tools: price history, volume, moving averages (Yahoo Finance)."""
from typing import Annotated
from pydantic import Field

try:
    import yfinance as yf
except ImportError:
    yf = None


def _get_ticker(symbol: str):
    if not yf:
        return None
    return yf.Ticker(symbol.upper())


def get_price_history(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="Period: '5d', '1mo', '3mo', '6mo', '1y'")] = "1mo",
) -> str:
    """Get historical OHLCV price data for technical analysis."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        hist = t.history(period=period)
        if hist is None or hist.empty:
            return f"No price history for {symbol}."
        hist = hist.tail(30)
        return f"Price history ({period}) for {symbol.upper()} (last {len(hist)} points):\n" + hist[["Open", "High", "Low", "Close", "Volume"]].to_string()
    except Exception as e:
        return f"Error fetching price history for {symbol}: {e}"


def get_volume_analysis(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="Period: '5d', '1mo', '3mo'")] = "1mo",
) -> str:
    """Analyze trading volume (average volume, recent vs average) for a security."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        hist = t.history(period=period)
        info = t.info
        if hist is None or hist.empty:
            return f"No volume data for {symbol}."
        vol = hist["Volume"]
        avg_vol = vol.mean()
        recent_vol = vol.tail(5).mean() if len(vol) >= 5 else vol.mean()
        text = [f"Volume analysis for {symbol.upper()} ({period}):", f"  Average volume: {avg_vol:,.0f}", f"  Recent 5-period avg volume: {recent_vol:,.0f}"]
        if avg_vol > 0:
            text.append(f"  Recent vs average: {(recent_vol / avg_vol) * 100:.1f}%")
        if isinstance(info, dict) and "averageVolume" in info:
            text.append(f"  Yahoo reported average volume: {info.get('averageVolume', 'N/A')}")
        return "\n".join(text)
    except Exception as e:
        return f"Error in volume analysis for {symbol}: {e}"


def get_moving_averages(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="Period: '1mo', '3mo', '6mo'")] = "3mo",
) -> str:
    """Get simple moving averages (e.g. 20-day, 50-day) for price trend analysis."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        hist = t.history(period=period)
        if hist is None or len(hist) < 50:
            return f"Insufficient history for {symbol} (need ~50 days for 50-day MA)."
        close = hist["Close"]
        ma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else None
        ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
        current = close.iloc[-1]
        parts = [f"Moving averages for {symbol.upper()} (period={period}):", f"  Current close: {current:.2f}"]
        if ma20 is not None:
            parts.append(f"  20-day SMA: {ma20:.2f} ({((current - ma20) / ma20) * 100:+.1f}% vs price)")
        if ma50 is not None:
            parts.append(f"  50-day SMA: {ma50:.2f} ({((current - ma50) / ma50) * 100:+.1f}% vs price)")
        return "\n".join(parts)
    except Exception as e:
        return f"Error computing moving averages for {symbol}: {e}"


def get_price_summary(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="Period: '5d', '1mo', '3mo', '1y'")] = "1mo",
) -> str:
    """Get a concise price summary: current, high, low, change over period (for chart/pattern context)."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        hist = t.history(period=period)
        if hist is None or hist.empty:
            return f"No price data for {symbol}."
        close = hist["Close"]
        current = close.iloc[-1]
        high = close.max()
        low = close.min()
        start = close.iloc[0]
        pct = ((current - start) / start) * 100 if start else 0
        return (
            f"Price summary for {symbol.upper()} ({period}): "
            f"current={current:.2f}, high={high:.2f}, low={low:.2f}, "
            f"period change={pct:+.1f}%"
        )
    except Exception as e:
        return f"Error in price summary for {symbol}: {e}"
