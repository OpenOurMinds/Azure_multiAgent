"""Fundamental Analyst tools: earnings, financials, macro indicators (Yahoo Finance / Alpha Vantage)."""
import os
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


def get_earnings_summary(
    symbol: Annotated[str, Field(description="Stock ticker symbol, e.g. AAPL, MSFT")],
) -> str:
    """Get earnings reports summary and upcoming earnings dates for a security."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        info = t.info
        earnings_dates = t.get_earnings_dates()
        text_parts = [f"Earnings summary for {symbol.upper()}:"]
        if isinstance(info, dict):
            if "earningsQuarterlyGrowth" in info and info["earningsQuarterlyGrowth"]:
                text_parts.append(f"  Earnings quarterly growth: {info.get('earningsQuarterlyGrowth')}")
            if "earningsGrowth" in info and info["earningsGrowth"] is not None:
                text_parts.append(f"  Earnings growth: {info.get('earningsGrowth')}")
            if "targetMeanPrice" in info and info["targetMeanPrice"]:
                text_parts.append(f"  Analyst target mean price: {info.get('targetMeanPrice')}")
        if earnings_dates is not None and not earnings_dates.empty:
            next_dates = earnings_dates.head(4)
            text_parts.append("  Recent/upcoming earnings dates:")
            text_parts.append(next_dates.to_string())
        else:
            text_parts.append("  No earnings dates data available.")
        return "\n".join(text_parts)
    except Exception as e:
        return f"Error fetching earnings for {symbol}: {e}"


def get_income_statement_summary(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="'yearly' or 'quarterly'")] = "yearly",
) -> str:
    """Get income statement summary (revenue, net income, margins) for a security."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        stmt = t.quarterly_income_stmt if period == "quarterly" else t.income_stmt
        if stmt is None or stmt.empty:
            return f"No income statement data for {symbol}."
        # First column is most recent
        recent = stmt.iloc[:, 0] if stmt.shape[1] > 0 else stmt.iloc[:, 0]
        rows = []
        for label in ["Total Revenue", "Net Income", "Gross Profit", "Operating Income"]:
            if label in recent.index:
                rows.append(f"  {label}: {recent[label]}")
        return f"Income statement ({period}) for {symbol.upper()}:\n" + "\n".join(rows) if rows else stmt.head(10).to_string()
    except Exception as e:
        return f"Error fetching income statement for {symbol}: {e}"


def get_balance_sheet_summary(
    symbol: Annotated[str, Field(description="Stock ticker symbol")],
    period: Annotated[str, Field(description="'yearly' or 'quarterly'")] = "yearly",
) -> str:
    """Get balance sheet summary (assets, liabilities, equity) for a security."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    try:
        t = _get_ticker(symbol)
        bs = t.quarterly_balance_sheet if period == "quarterly" else t.balance_sheet
        if bs is None or bs.empty:
            return f"No balance sheet data for {symbol}."
        recent = bs.iloc[:, 0]
        rows = []
        for label in ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity"]:
            if label in recent.index:
                rows.append(f"  {label}: {recent[label]}")
        return f"Balance sheet ({period}) for {symbol.upper()}:\n" + "\n".join(rows) if rows else bs.head(10).to_string()
    except Exception as e:
        return f"Error fetching balance sheet for {symbol}: {e}"


def get_macro_indicators(
    indicator: Annotated[
        str,
        Field(description="Macro indicator: e.g. 'TREASURY_YIELD_10Y', 'GDP', 'INFLATION', 'UNEMPLOYMENT' or 'DXY' for dollar index"),
    ] = "TREASURY_YIELD_10Y",
) -> str:
    """Get macroeconomic indicators (US Treasury yields, DXY). Uses Yahoo Finance macro tickers."""
    if not yf:
        return "Error: yfinance not installed. pip install yfinance"
    macro_tickers = {
        "TREASURY_YIELD_10Y": "^TNX",
        "TREASURY_YIELD_2Y": "^IRX",
        "DXY": "DX-Y.NYB",
        "VIX": "^VIX",
        "SP500": "^GSPC",
    }
    ticker = macro_tickers.get(indicator.upper(), "^TNX")
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist is not None and not hist.empty:
            last = hist["Close"].iloc[-1]
            return f"Macro indicator {indicator} ({ticker}): latest close = {last:.4f}"
        info = t.info
        if isinstance(info, dict) and "regularMarketPrice" in info:
            return f"Macro indicator {indicator} ({ticker}): current = {info.get('regularMarketPrice')}"
        return f"Macro indicator {indicator} ({ticker}): no recent data."
    except Exception as e:
        return f"Error fetching macro indicator {indicator}: {e}"
