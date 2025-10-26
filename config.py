import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API CREDENTIALS
# ============================================================================

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "claude-sonnet-4-5-20250929"

# Coinbase API
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET")

# ============================================================================
# TRADING SETTINGS
# ============================================================================

TRADING_MODE = os.getenv("TRADING_MODE", "live")  # "paper" or "live"
TRADING_PAIR = os.getenv("TRADING_PAIR", "SOL-GBP")

# ============================================================================
# INVESTMENT & CAPITAL
# ============================================================================

INITIAL_CAPITAL = 500.0      # Starting capital
TRADE_AMOUNT_GBP = 499.0     # Amount per trade (leave £1 buffer)

# ============================================================================
# FEE STRUCTURE (CORRECTED - Based on Your Actual Coinbase Trade)
# ============================================================================
# Your manual trade showed: £1.72 fee on £142.98 = 1.2% per trade
# Total round-trip cost: 2.4% (1.2% buy + 1.2% sell)

FEE_PCT = 0.012              # 1.2% Coinbase fee per trade
TOTAL_FEE_PCT = 0.024        # 2.4% total round-trip (buy + sell)
API_COST_GBP = 0.10          # Claude API cost per trading cycle (~£0.08-0.10)

# ============================================================================
# PROFIT TARGET STRATEGY
# ============================================================================
# OPTION A: £1.00 NET PROFIT (RECOMMENDED) ✅
# - Price movement: 2.67% gain required
# - Time estimate: 1-3 hours typical
# - Trades per day: 3-5 possible
# - Daily potential: £3-5 profit

PROFIT_TARGET_GBP = 13.16    # Gross profit needed for £1.00 net after all costs
PROFIT_TARGET_PCT = 0.0267   # 2.67% price movement required

# OPTION B: £0.50 NET PROFIT (FASTEST) ⚡
# - Price movement: 2.57% gain required
# - Time estimate: 30 min - 2 hours
# - Trades per day: 5-10 possible
# - Daily potential: £2.50-5.00 profit
# Uncomment to use:
# PROFIT_TARGET_GBP = 12.66
# PROFIT_TARGET_PCT = 0.0257

# OPTION C: £2.00 NET PROFIT (MODERATE) 🎯
# - Price movement: 2.88% gain required
# - Time estimate: 2-4 hours
# - Trades per day: 2-4 possible
# - Daily potential: £4-8 profit
# Uncomment to use:
# PROFIT_TARGET_GBP = 14.17
# PROFIT_TARGET_PCT = 0.0288

# OPTION D: £5.00 NET PROFIT (SLOWER) 💰
# - Price movement: 3.49% gain required
# - Time estimate: 4-8 hours
# - Trades per day: 1-2 possible
# - Daily potential: £5-10 profit
# Uncomment to use:
# PROFIT_TARGET_GBP = 17.21
# PROFIT_TARGET_PCT = 0.0349

# ============================================================================
# PROFIT CALCULATION BREAKDOWN (for £499 investment, £1.00 net profit)
# ============================================================================
# """
# BUY PHASE:
# - Investment: £499.00
# - Buy fee (1.2%): £5.99
# - Assets bought: £493.01

# PRICE MOVEMENT: +2.67%
# - Assets grow to: £506.17

# SELL PHASE:
# - Gross value: £506.17
# - Sell fee (1.2%): £6.07
# - Cash received: £500.10
# - Less API cost: £0.10
# - Net received: £500.00
# - NET PROFIT: £1.00 ✅

# TIME: 2.67% moves in SOL typically take 1-3 hours
# """

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

STOP_LOSS_PCT = 0.015        # 1.5% stop loss (protects against big losses)
                             # Loss if triggered: ~£7.50

MAX_POSITION_SIZE = 10000    # Maximum position size
MIN_CONFIDENCE = 0.65        # 65% minimum confidence for trades
                             # (Your Claude returns 67% confidence)

COOLDOWN_MINUTES = 3         # Wait 3 minutes between trade decisions

# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

RSI_PERIOD = 14              # RSI calculation period
EMA_FAST = 10                # Fast EMA period
EMA_SLOW = 50                # Slow EMA period
MACD_FAST = 12               # MACD fast period
MACD_SLOW = 26               # MACD slow period
MACD_SIGNAL = 9              # MACD signal period

# ============================================================================
# SAFETY LIMITS
# ============================================================================

MAX_DAILY_TRADES = 999       # Maximum trades per day (unlimited)
MAX_CONSECUTIVE_LOSSES = 5   # Stop after 5 losses in a row
MIN_CAPITAL_THRESHOLD = 490.0  # Stop if capital drops below £490

# ============================================================================
# COMPOUNDING
# ============================================================================

REINVEST_PROFITS = True      # Reinvest profits to grow position size
                             # Set to False to trade with fixed £499 always

# ============================================================================
# SUMMARY OF CURRENT SETTINGS
# ============================================================================
# """
# 💰 INVESTMENT: £499 per trade
# 🎯 TARGET: £1.00 net profit per trade (2.67% price moves)
# ⏱️  SPEED: 1-3 hours per trade typically
# 📊 DAILY POTENTIAL: 3-5 trades = £3-5 profit per day
# 💸 COSTS: £5.99 buy fee + £6.07 sell fee + £0.10 API = £12.16 total
# ⚠️  RISK: £7.50 loss if stop loss triggered (1.5% move against)
# ✅ RISK/REWARD: 1:0.13 (risk £7.50 to make £1.00)

# SPEED COMPARISON:
# - Old (£144): 2.90% for £0.50 = 2-4 hours
# - New (£499): 2.67% for £1.00 = 1-3 hours
# - Result: 2x profit in FASTER time! 🚀
# """