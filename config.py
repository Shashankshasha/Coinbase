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
TRADING_MODE = os.getenv("TRADING_MODE", "live")
TRADING_PAIR = os.getenv("TRADING_PAIR", "SOL-GBP")
INITIAL_CAPITAL = 144.0
TRADE_AMOUNT_GBP = 144.0

# REALISTIC Profit Strategy (covers fees + API costs + £0.50 profit)
PROFIT_TARGET_GBP = 2.35  # £2.35 gross = £0.50 net after all costs
PROFIT_TARGET_PCT = 0.0165  # 1.65% gain (covers £1.72 fees + £0.10 API + £0.50 profit)
STOP_LOSS_PCT = 0.010  # 1.0% stop loss
FEE_PCT = 0.006

# ADJUSTED Risk Management - Lower threshold to allow trades
MAX_POSITION_SIZE = 10000
MIN_CONFIDENCE = 0.65  # LOWERED from 0.70 to 0.65 (your Claude returns 67%)
COOLDOWN_MINUTES = 3

# Technical Indicators
RSI_PERIOD = 14
EMA_FAST = 10
EMA_SLOW = 50
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Safety Limits
MAX_DAILY_TRADES = 999
MAX_CONSECUTIVE_LOSSES = 5
MIN_CAPITAL_THRESHOLD = 140.0

# Compounding
REINVEST_PROFITS = True
# ```

# ## Key Changes:
# 1. ✅ **MIN_CONFIDENCE: 0.65** (was 0.70) - Trades will now execute at 67%
# 2. ✅ **PROFIT_TARGET_PCT: 0.0165** (was 0.025) - 1.65% to cover all costs + £0.50 profit
# 3. ✅ **PROFIT_TARGET_GBP: £2.35** - Gross profit target

# ## Cost Math (for £0.50 net profit):
# ```
# Buy:  £144.00 spent → £143.14 in assets (after £0.86 fee)
# Need: 1.65% price rise
# Sell: £145.50 assets → £144.62 received (after £0.87 fee)
# Less: £0.10 API costs
# Net:  £144.52 = £0.52 profit ✅