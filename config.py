import os
from dotenv import load_dotenv

load_dotenv()

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "claude-sonnet-4-5-20250929"

# Coinbase API
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET")

# Trading Settings
TRADING_MODE = os.getenv("TRADING_MODE", "paper")  # paper or live
TRADING_PAIR = os.getenv("TRADING_PAIR", "ETH-GBP")
TRADE_AMOUNT_GBP = float(os.getenv("TRADE_AMOUNT_GBP", "100"))
PROFIT_TARGET_GBP = float(os.getenv("PROFIT_TARGET_GBP", "1"))

# Risk Management
MAX_POSITION_SIZE = 1000  # GBP
RISK_PER_TRADE = 0.02  # 2%
MIN_CONFIDENCE = 0.75  # Claude must be 75%+ confident
COOLDOWN_MINUTES = 15  # Wait between trades

# Technical Indicators Settings
RSI_PERIOD = 14
EMA_FAST = 10
EMA_SLOW = 50
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9