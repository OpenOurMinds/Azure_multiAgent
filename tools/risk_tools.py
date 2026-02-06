"""Risk Management Agent tools: volatility, position limits, downside risk."""
from typing import Annotated
from pydantic import Field

try:
    import yfinance as yf
except ImportError:
    yf = None

# Import config for default limits; avoid circular import by reading env in tools if needed
def _get_max_vol_pct() -> float:
    import os
    return float(os.getenv("MAX_VOLATILITY_PCT", "50.0"))

def _get_max_position_pct() -> float:
    import os
    return float(os.getenv("MAX_POSITION_PCT", "10.0"))


def evaluate_volatility(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="Period for volatility: '1mo', '3mo', '6mo'")] = "1mo",
    max_volatility_pct: Annotated[float, Field(description="Max acceptable annualized volatility % (e.g. 50)")] = None,
) -> str:
    """Evaluate volatility (e.g. annualized) vs a limit. Returns assessment for risk compliance."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    max_pct = max_volatility_pct if max_volatility_pct is not None else _get_max_vol_pct()
    try:
        t = yf.Ticker(symbol.upper())
        hist = t.history(period=period)
        if hist is None or len(hist) < 5:
            return f"Insufficient data for volatility for {symbol}."
        returns = hist["Close"].pct_change().dropna()
        vol_daily = returns.std()
        # Annualized (approx 252 trading days)
        vol_annual_pct = vol_daily * (252 ** 0.5) * 100
        within = "WITHIN" if vol_annual_pct <= max_pct else "EXCEEDS"
        return (
            f"Volatility assessment for {symbol.upper()} ({period}): "
            f"annualized vol ≈ {vol_annual_pct:.1f}%. "
            f"Limit: {max_pct}%. Result: {within} limit."
        )
    except Exception as e:
        return f"Error evaluating volatility for {symbol}: {e}"


def evaluate_position_limit_compliance(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    proposed_position_pct: Annotated[float, Field(description="Proposed position size as % of portfolio")],
    max_position_pct: Annotated[float, Field(description="Max allowed position size %")] = None,
) -> str:
    """Check if a proposed position size complies with trading limits."""
    max_pct = max_position_pct if max_position_pct is not None else _get_max_position_pct()
    compliant = proposed_position_pct <= max_pct
    return (
        f"Position limit check for {symbol.upper()}: "
        f"proposed={proposed_position_pct}%, max={max_pct}%. "
        f"Compliant: {compliant}."
    )


def evaluate_downside_risk(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="Period: '1mo', '3mo', '6mo'")] = "3mo",
) -> str:
    """Evaluate downside risk: max drawdown and worst drawdown over the period."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = yf.Ticker(symbol.upper())
        hist = t.history(period=period)
        if hist is None or len(hist) < 2:
            return f"Insufficient data for downside risk for {symbol}."
        close = hist["Close"]
        cummax = close.cummax()
        drawdown = (close - cummax) / cummax
        max_dd_pct = drawdown.min() * 100
        return (
            f"Downside risk for {symbol.upper()} ({period}): "
            f"max drawdown = {max_dd_pct:.1f}%."
        )
    except Exception as e:
        return f"Error evaluating downside risk for {symbol}: {e}"
