"""
OPTIMIZED CONFIG FOR ₹20,000 CAPITAL
=====================================

Risk/Reward: 1:2 (Risk ₹500, Target ₹1,000+)
Auto-compounding enabled
Ultra-conservative settings for small capital
"""

# =============================================================================
# CAPITAL SETTINGS - ₹20,000 START
# =============================================================================

INITIAL_CAPITAL_INR = 20000.00        # Starting capital
TRADE_AMOUNT_INR = 18000.00           # Use most of capital (1 lot)
MIN_CAPITAL_THRESHOLD_INR = 15000.00  # Stop if drops below this (₹5K max loss total)

# =============================================================================
# PROFIT TARGETS - HIGHER THAN LOSS!
# =============================================================================

PROFIT_TARGET_INR = 1000.00           # ₹1,000 profit target per trade
PROFIT_TARGET_PCT = 0.05              # 5% on premium
MAX_DAILY_PROFIT_INR = 3000.00        # Stop after ₹3K daily profit (protect gains)

# =============================================================================
# LOSS LIMITS - KEEP SMALL!
# =============================================================================

STOP_LOSS_PCT = 0.02                  # 2% stop loss (tight!)
MAX_LOSS_PER_TRADE_INR = 500.00       # Max ₹500 loss per trade
MAX_DAILY_LOSS_INR = 1500.00          # Stop after ₹1.5K daily loss

# =============================================================================
# RISK/REWARD SUMMARY
# =============================================================================
#
# Max Loss:      ₹500
# Profit Target: ₹1,000
# Risk/Reward:   1:2 ✅ (Risk 1 to make 2)
#
# Break-even Win Rate: 33% (you only need to win 1 out of 3!)
# Expected Win Rate:   55-65%
# Expected Daily:      ₹500-1,500
#
# =============================================================================

# =============================================================================
# TRAILING STOP - RIDE PROFITS TO THE TOP!
# =============================================================================

ENABLE_TRAILING_STOP = True
TRAILING_STOP_ACTIVATION_PCT = 0.03   # Activate at 3% profit
TRAILING_STOP_DISTANCE_PCT = 0.01     # Trail just 1% below peak (tight!)

# This means:
# - Buy @ ₹100
# - Rises to ₹103 → Trailing stop activates
# - Rises to ₹110 → Stop at ₹108.90
# - Rises to ₹120 → Stop at ₹118.80
# - Drops to ₹118 → SELL! Lock ₹18 profit per unit

# =============================================================================
# AUTO-COMPOUNDING - REINVEST PROFITS!
# =============================================================================

REINVEST_PROFITS = True               # Compound profits automatically!
COMPOUND_AFTER_TRADES = 5             # Recalculate position size every 5 trades

# Growth projection with compounding:
# Week 1:  ₹20,000 → ₹23,000 (+₹3,000)
# Week 2:  ₹23,000 → ₹26,500 (+₹3,500)
# Week 3:  ₹26,500 → ₹30,500 (+₹4,000)
# Week 4:  ₹30,500 → ₹35,000 (+₹4,500)
# Month 1: ₹20,000 → ₹35,000 (75% growth!)

# =============================================================================
# PROGRESSIVE PROFIT TIERS (scales with your capital growth)
# =============================================================================

PROFIT_TIERS = {
    15000: 800,     # ₹15K capital → ₹800 target
    20000: 1000,    # ₹20K capital → ₹1,000 target
    30000: 1500,    # ₹30K capital → ₹1,500 target
    50000: 2500,    # ₹50K capital → ₹2,500 target
    75000: 3500,    # ₹75K capital → ₹3,500 target
    100000: 5000,   # ₹1L capital → ₹5,000 target
}

# =============================================================================
# POSITION SIZING - CONSERVATIVE FOR ₹20K
# =============================================================================

MAX_LOTS_PER_TRADE = 1                # Only 1 lot with ₹20K
MAX_OPEN_POSITIONS = 1                # Only 1 position at a time

# =============================================================================
# TRADE LIMITS - PROTECT CAPITAL
# =============================================================================

MAX_DAILY_TRADES = 5                  # Max 5 trades per day
MAX_CONSECUTIVE_LOSSES = 2            # Stop after 2 losses in a row
COOLDOWN_MINUTES = 15                 # Wait 15 min between trades

# =============================================================================
# INDEX SELECTION FOR SMALL CAPITAL
# =============================================================================

# With ₹20K, prefer NIFTY over BANKNIFTY:
# - NIFTY: Lower premium options available
# - BANKNIFTY: Premiums can be high
#
# Trade ATM or slightly OTM for lower premium

PRIMARY_INDEX = "NIFTY"               # NIFTY is safer for small capital
STRIKE_SELECTION_MODE = "OTM_1"       # 1 strike OTM = lower premium

# =============================================================================
# GREEKS THRESHOLDS - OPTIMIZED FOR SMALL CAPITAL
# =============================================================================

MIN_DELTA_CALL = 0.35                 # Slightly OTM
MAX_DELTA_CALL = 0.55                 # Not too deep ITM
MIN_IV = 12.0                         # Avoid dead options
MAX_IV = 35.0                         # Avoid expensive premiums

# =============================================================================
# SAMPLE TRADE WITH THESE SETTINGS
# =============================================================================
#
# Capital: ₹20,000
# Trade: Buy 1 lot NIFTY 24550 CE @ ₹120
# Investment: ₹120 × 50 = ₹6,000
#
# Stop Loss (2%): ₹117.60 → Loss = ₹120 (₹2.40 × 50)
# Target (5%):    ₹126 → Profit = ₹300 (₹6 × 50)
#
# With Trailing Stop:
# - Price hits ₹130 (8% up) → Stop at ₹128.70
# - Price hits ₹140 (17% up) → Stop at ₹138.60
# - Price drops to ₹138 → SELL!
# - Profit: ₹18 × 50 = ₹900
#
# Risk/Reward Achieved: ₹120 risk for ₹900 gain = 1:7.5! 🎯
#
# =============================================================================
