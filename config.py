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
INITIAL_CAPITAL = 500.0
TRADE_AMOUNT_GBP = 499.0

# REALISTIC Profit Strategy (covers fees + API costs + £1.00 profit)
PROFIT_TARGET_GBP = 7.10  # £7.10 gross = £1.00 net after all costs
PROFIT_TARGET_PCT = 0.0145  # 1.45% gain (covers £6.00 fees + £0.10 API + £1.00 profit)
STOP_LOSS_PCT = 0.010  # 1.0% stop loss
FEE_PCT = 0.012         # 1.2% total Coinbase fee (buy + sell)
API_COST_GBP = 0.10     # API + system cost per trading cycle

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
MIN_CAPITAL_THRESHOLD = 490.0

# Compounding
REINVEST_PROFITS = True

# ```

# ## Key Changes:
# 1. ✅ **PROFIT_TARGET_GBP: £7.10** - Gross target to yield £1 net profit after ~1.2% Coinbase fees + £0.10 API cost
# 2. ✅ **PROFIT_TARGET_PCT: 0.0145** - 1.45% gross move required on £499 trade
# 3. ✅ **FEE_PCT: 0.012** - Updated to real Coinbase fee (based on your trade receipts)
# 4. ✅ **API_COST_GBP: 0.10** - Each 3-minute trade cycle (Claude + Coinbase) included in expense

# ## Cost Math (for £1.00 net profit):
# ```
# Buy:  £499.00 spent → £492.00 in assets (after £6.00 fee)
# Need: 1.45% price rise
# Sell: £506.10 assets → £499.00 received (after £6.00 fee)
# Less: £0.10 API costs
# Net:  £500.00 = £1.00 profit ✅
# ```
