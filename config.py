"""Configuration for the multi-agent trading system."""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI (used by Orchestrator and all agents)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "preview")

# Optional: Alpha Vantage (fundamental/technical data; free tier: 25 req/day)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")

# Risk limits (used by Risk Management Agent)
DEFAULT_MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_PCT", "10.0"))
DEFAULT_MAX_VOLATILITY_PCT = float(os.getenv("MAX_VOLATILITY_PCT", "50.0"))
