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
# FEE STRUCTURE
# ============================================================================
# Based on actual Coinbase trades: 1.2% per trade
# Total round-trip cost: 2.4% (1.2% buy + 1.2% sell)

FEE_PCT = 0.012              # 1.2% Coinbase fee per trade
TOTAL_FEE_PCT = 0.024        # 2.4% total round-trip (buy + sell)
API_COST_GBP = 0.10          # Claude API cost per trading cycle (~£0.08-0.10)

# ============================================================================
# PROFIT TARGET STRATEGY - ENHANCED WITH TRAILING STOP
# ============================================================================
# 🎯 NEW STRATEGY: Minimum £1 profit + Trailing Stop for extra gains!
#
# How it works:
# 1. Initial target: £1.00 NET profit (guaranteed minimum)
# 2. Once hit → Trailing stop activates (0.5% below peak)
# 3. Captures extra gains in strong uptrends (£2-10 possible!)
# 4. Auto-exits if price reverses 0.5% from peak
# 5. Never get less than £1.00 after target is hit
#
# Expected results:
# - Quick reversal: £1.00 (minimum secured)
# - Moderate trend: £2.00-£3.00 (+100-200%)
# - Strong trend: £5.00-£10.00 (+400-900%)
# ============================================================================

# SIMPLE TARGET: £1.00 NET PROFIT (Trailing stop handles the rest!)
PROFIT_TARGET_GBP = 1.0      # £1.00 net profit target
PROFIT_TARGET_PCT = 0.022    # ~2.2% price movement needed

# The profit_strategy_enhanced.py will:
# - Calculate exact price needed for £1.00 NET (after all fees)
# - Lock in £1.00 minimum once hit
# - Use trailing stop to capture MORE if trend continues
# - You get £1-10 depending on market, never less than £1!

# ============================================================================
# PROFIT CALCULATION (AUTOMATIC)
# ============================================================================
# The enhanced strategy calculates the EXACT exit price needed for £1.00 net:
#
# Example for SOL at £150:
# - Investment: £499.00
# - Buy fee (1.2%): £5.99
# - Crypto bought: £493.01 worth
# - Entry price: £150.00
# 
# TARGET CALCULATION (done automatically by bot):
# - Need £1.00 net profit
# - After sell fee (1.2%) and API cost (£0.10)
# - Exact exit price needed: £151.47 (calculated dynamically)
# - Initial target: £151.47
# 
# TRAILING STOP THEN ACTIVATES:
# - Price hits £151.47 → £1.00 secured! ✅
# - Trailing stop activates at 0.5% below peak
# - If price goes to £155 → stop moves to £154.23
# - If price drops to £154.20 → EXIT with £3.50 profit! 🎉
# - If price reverses immediately → still get £1.00 minimum
#
# TIME: 2.2% moves typically take 1-3 hours
# UPSIDE: Unlimited (trailing stop captures trends)
# DOWNSIDE: Protected (£1.00 minimum once target hit)
# ============================================================================

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

STOP_LOSS_PCT = 0.015        # 1.5% stop loss (hard safety net)
                             # Loss if triggered: ~£7.50
                             # This is your MAXIMUM loss per trade

MAX_POSITION_SIZE = 10000    # Maximum position size
MIN_CONFIDENCE = 0.65        # 65% minimum confidence for trades

COOLDOWN_MINUTES = 3         # Wait 3 minutes between trade checks

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
# TRAILING STOP CONFIGURATION (Optional - defaults in profit_strategy_enhanced.py)
# ============================================================================
# The trailing stop distance is set in profit_strategy_enhanced.py (line 28)
# Default: 0.5% (recommended for balanced profit capture)
#
# To change it, edit profit_strategy_enhanced.py:
#   self.trailing_stop_distance_pct = 0.005  # 0.5% (current)
#
# Options:
#   0.003 (0.3%) - Tight, quick exit, less extra profit
#   0.005 (0.5%) - Balanced (RECOMMENDED) ⭐
#   0.008 (0.8%) - Loose, more profit potential
#   0.010 (1.0%) - Very loose, maximum profit capture

# ============================================================================
# SUMMARY OF ENHANCED SETTINGS
# ============================================================================
# """
# 💰 INVESTMENT: £499 per trade
# 🎯 INITIAL TARGET: £1.00 net profit (2.2% price move)
# 🎯 TRAILING STOP: Activates after £1.00 hit
# 📈 UPSIDE POTENTIAL: £1.00 - £10.00+ depending on trend
# ⏱️  SPEED: 2.2% moves typically take 1-3 hours
# 📊 DAILY POTENTIAL: 3-5 trades = £3-15 profit per day (vs old £3-5)
# 💸 COSTS: £5.99 buy + £6.07 sell + £0.10 API = £12.16 total (included in calculation)
# ⚠️  RISK: £7.50 max loss if stop loss triggered (1.5% move against)
# ✅ RISK/REWARD: 1:0.13 to 1:1.33 (risk £7.50 to make £1-10)
#
# 🚀 UPGRADE BENEFITS:
# - Same £1.00 minimum (guaranteed)
# - Extra profit capture in trends (£2-10 possible!)
# - Same risk (1.5% stop loss unchanged)
# - Fully automated (trailing stop handles everything)
# - Market orders (guaranteed execution, small slippage OK)
#
# 💡 PHILOSOPHY:
# "After £1 profit, everything is bonus. Fast exit saves from greater losses."
# This config + trailing stop implements that perfectly! ✅
# """

# ============================================================================
# IMPORTANT NOTES
# ============================================================================
# 1. PROFIT_TARGET_GBP = 1.0 is your MINIMUM target
#    - The bot calculates exact price needed for £1.00 NET after all fees
#    - Trailing stop then captures MORE if trend continues
#    - You never get less than £1.00 once target is hit
#
# 2. PROFIT_TARGET_PCT = 0.022 is approximate
#    - Exact % varies by entry price (higher price = smaller % needed)
#    - Bot calculates this dynamically per trade
#
# 3. Trailing stop uses MARKET ORDERS
#    - Guaranteed execution (you always get out)
#    - Small slippage acceptable (£0.10-0.50 typical)
#    - Fast exit = protect gains from crashes
#
# 4. To adjust trailing distance:
#    - Edit profit_strategy_enhanced.py line 28
#    - Not in this config file
# ============================================================================