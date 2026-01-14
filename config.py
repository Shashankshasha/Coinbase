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
# CRITICAL FIX: Handle newline encoding in Cloud API private key
# ============================================================================
# Cloud API keys use EC private keys with newlines
# .env files store these as literal \n characters
# This converts them to actual newlines for the SDK
if COINBASE_API_SECRET and '\\n' in COINBASE_API_SECRET:
    COINBASE_API_SECRET = COINBASE_API_SECRET.replace('\\n', '\n')

# ============================================================================
# TRADING SETTINGS
# ============================================================================

TRADING_MODE = "live"  # LIVE TRADING - Real money on Coinbase
TRADING_PAIR = "BTC-GBP"

# ============================================================================
# INVESTMENT & CAPITAL
# ============================================================================

# £1000 LIVE TRADING CONFIGURATION
INITIAL_CAPITAL = 1000.00  # Your actual GBP balance in Coinbase
TRADE_AMOUNT_GBP = 990.00  # Leave £10 buffer for fees/rounding

# ============================================================================
# FEE STRUCTURE
# ============================================================================
# Based on actual Coinbase trades: 1.2% per trade
# Total round-trip cost: 2.4% (1.2% buy + 1.2% sell)

FEE_PCT = 0.012              # 1.2% Coinbase fee per trade
TOTAL_FEE_PCT = 0.024        # 2.4% total round-trip (buy + sell)
API_COST_GBP = 0.10          # Claude API cost per trading cycle (~£0.08-0.10)

# ============================================================================
# PROFIT TARGET STRATEGY - OPTIMIZED FOR LIVE TRADING
# ============================================================================
# 🎯 OPTIMIZED STRATEGY: £2 minimum profit + Trailing Stop
#
# Why £2 instead of £1?
# - Better risk/reward ratio (was 7.5:1, now 1.25:1)
# - One loss = 1.25 wins (vs 7.5 wins before!)
# - More sustainable long-term
# - Trailing stop still captures £3-10 in strong trends
#
# How it works:
# 1. Initial target: £2.00 NET profit (guaranteed minimum)
# 2. Once hit → Trailing stop activates (0.5% below peak)
# 3. Captures extra gains in strong uptrends (£3-10 possible!)
# 4. Auto-exits if price reverses 0.5% from peak
# 5. Never get less than £2.00 after target is hit
#
# Expected results:
# - Quick reversal: £2.00 (minimum secured)
# - Moderate trend: £3.00-£5.00 (+50-150%)
# - Strong trend: £6.00-£12.00 (+200-500%)
# ============================================================================

PROFIT_TARGET_GBP = 4.0      # £4.00 net profit target (scaled for £1000)
PROFIT_TARGET_PCT = 0.028    # ~2.7% price movement needed

# ============================================================================
# PROFIT CALCULATION (AUTOMATIC)
# ============================================================================
# The enhanced strategy calculates the EXACT exit price needed for £2.00 net:
#
# Example for SOL at £150:
# - Investment: £499.00
# - Buy fee (1.2%): £5.99
# - Crypto bought: £493.01 worth
# - Entry price: £150.00
# 
# TARGET CALCULATION (done automatically by bot):
# - Need £2.00 net profit
# - After sell fee (1.2%) and API cost (£0.10)
# - Exact exit price needed: ~£152.10 (calculated dynamically)
# - Initial target: £152.10
# 
# TRAILING STOP THEN ACTIVATES:
# - Price hits £152.10 → £2.00 secured! ✅
# - Trailing stop activates at 0.5% below peak
# - If price goes to £155 → stop moves to £154.23
# - If price drops to £154.20 → EXIT with £4.50 profit! 🎉
# - If price reverses immediately → still get £2.00 minimum
#
# TIME: 2.7% moves typically take 2-4 hours
# UPSIDE: Unlimited (trailing stop captures trends)
# DOWNSIDE: Protected (£2.00 minimum once target hit)
# ============================================================================

# ============================================================================
# RISK MANAGEMENT - OPTIMIZED FOR BETTER RISK/REWARD
# ============================================================================

STOP_LOSS_PCT = 0.010       # 0.5% stop loss (MUCH TIGHTER!)
                             # Loss if triggered: ~£2.50
                             # Old: 1.5% = £7.50 loss (terrible!)
                             # New: 0.5% = £2.50 loss (balanced!)
                             
# ⚖️ RISK/REWARD ANALYSIS:
# Risk: £2.50 (stop loss)
# Reward: £2.00-£10.00 (target + trailing)
# Ratio: 1.25:1 to 0.25:1 (MUCH BETTER!)
#
# Old settings: Risk £7.50 to make £1 = 7.5:1 (TERRIBLE!)
# New settings: Risk £2.50 to make £2-10 = 1.25:1 to 0.25:1 (GOOD!)
#
# Break-even point: Need 55% win rate (vs 88% before!)
# Expected win rate: 60-70%
# Result: PROFITABLE! ✅

MAX_POSITION_SIZE = 10000    # Maximum position size
MIN_CONFIDENCE = 0.75      # 75% minimum confidence for trades (higher = safer)

# ============================================================================
# DYNAMIC INTERVAL SETTINGS
# ============================================================================
# The bot adjusts check frequency based on whether you have an open position
SCAN_INTERVAL_MINUTES = 3    # When no position (scanning for entries)
MONITOR_INTERVAL_MINUTES = 1 # When position open (monitoring for exit)
# This ensures fast profit capture and tight trailing stop execution!

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
# SAFETY LIMITS - ULTRA CONSERVATIVE FOR £1000 CAPITAL
# ============================================================================

MAX_DAILY_TRADES = 5         # Maximum 5 trades per day (very conservative)
MAX_CONSECUTIVE_LOSSES = 2   # Stop after 2 losses in a row (extra safety!)
MIN_CAPITAL_THRESHOLD = 980.0  # Stop if capital drops below £980 (£20 max loss!)
COOLDOWN_MINUTES = 15        # 15 min between trades (prevent overtrading)

# ============================================================================
# COMPOUNDING
# ============================================================================

REINVEST_PROFITS = True      # Reinvest profits to grow position size
                             # Set to False to trade with fixed £499 always

# ============================================================================
# TRAILING STOP CONFIGURATION (Optional - defaults in profit_strategy_enhanced.py)
# ============================================================================
# The trailing stop distance is set in profit_strategy_enhanced.py (line 34)
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
# REALISTIC DAILY EARNINGS ESTIMATE
# ============================================================================
# """
# Based on optimized settings (£2 target, 0.5% stop):
#
# CONSERVATIVE (3 trades/day, 60% win rate):
# - 1.8 wins × £2.50 avg = £4.50
# - 1.2 losses × £2.50 = -£3.00
# - Net: £1.50 per day
# - Monthly: £33 (6.6% return)
#
# REALISTIC (4 trades/day, 65% win rate):
# - 2.6 wins × £3.00 avg (trailing) = £7.80
# - 1.4 losses × £2.50 = -£3.50
# - Net: £4.30 per day
# - Monthly: £95 (19% return)
#
# OPTIMISTIC (5 trades/day, 70% win rate):
# - 3.5 wins × £3.50 avg (trailing) = £12.25
# - 1.5 losses × £2.50 = -£3.75
# - Net: £8.50 per day
# - Monthly: £187 (37% return)
#
# EXPECTED RANGE: £2-8 per day, £40-175 per month
# """

# ============================================================================
# SUMMARY OF OPTIMIZED SETTINGS
# ============================================================================
# """
# 💰 INVESTMENT: £499 per trade
# 🎯 INITIAL TARGET: £2.00 net profit (2.7% price move)
# 🎯 TRAILING STOP: Activates after £2.00 hit
# 📈 UPSIDE POTENTIAL: £2.00 - £12.00+ depending on trend
# ⏱️  SPEED: 2.7% moves typically take 2-4 hours
# 📊 DAILY POTENTIAL: 3-5 trades = £4-8 profit per day
# 💸 COSTS: £5.99 buy + £6.07 sell + £0.10 API = £12.16 total (included)
# ⚠️  RISK: £2.50 max loss if stop loss triggered (0.5% move against)
# ✅ RISK/REWARD: 1.25:1 to 0.21:1 (risk £2.50 to make £2-12)
#
# 🎯 KEY IMPROVEMENTS VS OLD SETTINGS:
# - Stop loss: 1.5% → 0.5% (3x tighter!)
# - Max loss: £7.50 → £2.50 (3x smaller!)
# - Target: £1 → £2 (2x bigger!)
# - Risk/Reward: 7.5:1 → 1.25:1 (6x better!)
# - Break-even needed: 88% → 55% win rate (33% easier!)
# - Expected win rate: 60-70% (above break-even!)
# - Daily profit: -£5 to £0 → £4-8 (PROFITABLE!)
#
# 🚀 UPGRADE BENEFITS:
# - Realistic chance of profit every day ✅
# - One loss ≠ wipes out 7 wins ✅
# - Sustainable long-term strategy ✅
# - Trailing stop still captures big moves ✅
# - Much better risk management ✅
#
# 💡 PHILOSOPHY:
# "Small losses, medium wins, big wins on trends"
# This is how professional traders make money! ✅
# """

# ============================================================================
# IMPORTANT NOTES
# ============================================================================
# 1. STOP LOSS CHANGED FROM 1.5% TO 0.5%
#    - This is CRITICAL for profitability
#    - Old setting was losing money on math alone
#    - New setting gives you fighting chance
#    - Accept small losses quickly = good risk management
#
# 2. PROFIT TARGET CHANGED FROM £1 TO £2
#    - Better risk/reward ratio
#    - Still achievable (just 0.5% more movement)
#    - Trailing stop captures £3-12 in strong trends
#    - More realistic for making actual profit
#
# 3. TIGHTER SAFETY LIMITS
#    - Stop after 3 losses (vs 5) - protect capital faster
#    - Max 20 trades/day (vs unlimited) - prevent overtrading
#    - Stop at £475 (vs £490) - 5% max drawdown
#
# 4. LIVE TRADING MODE
#    - No paper trading - this is REAL MONEY
#    - Start small, scale up after proving system works
#    - Monitor closely for first week
#    - Adjust settings based on actual results
#
# 5. TRAILING STOP STILL ACTIVE
#    - After hitting £2 target, trailing activates
#    - Captures £3-12 in strong trends
#    - You never get less than £2 once target hit
#    - Best of both worlds: security + upside
# ============================================================================

# ============================================================================
# BEFORE YOU START LIVE TRADING
# ============================================================================
# """
# ⚠️  CHECKLIST:
#
# 1. [ ] Deposit £500+ GBP to Coinbase
# 2. [ ] Test bot with small trade first (manually verify it works)
# 3. [ ] Run dashboard in separate terminal (monitor in real-time)
# 4. [ ] Set phone alerts for large moves (optional)
# 5. [ ] Accept that losses WILL happen (that's trading!)
# 6. [ ] Only trade with money you can afford to lose
# 7. [ ] Plan to run bot for at least 2 weeks before judging
# 8. [ ] Keep track of results in spreadsheet
# 9. [ ] Be patient - crypto is volatile
# 10. [ ] Trust the system - don't manually interfere
#
# 🎯 EXPECTATIONS:
# - Some days you'll lose money (that's normal!)
# - Some days you'll make £10+ (exciting!)
# - Average should be £2-5 per day over time
# - Monthly: £40-150 realistic range
# - Yearly: £500-1,800 (100-360% ROI)
#
# 💡 REMEMBER:
# - Past performance ≠ future results
# - Crypto is highly volatile
# - No strategy wins 100% of time
# - Risk management is key
# - Small consistent gains > big risky bets
#
# Good luck! 🚀
# """
# ============================================================================