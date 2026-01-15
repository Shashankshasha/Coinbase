"""
Zerodha Kite Options Trading Bot Configuration
==============================================

Ultra-configurable settings for ML + LLM powered options trading.
Supports both CALL and PUT options with a simple flag switch.
"""

import os
from datetime import time
from enum import Enum

# =============================================================================
# TRADING MODE FLAGS - CRITICAL SETTINGS
# =============================================================================

class OptionType(Enum):
    """Option type flag - switch between CALL and PUT trading"""
    CALL = "CE"  # Call Option (Bullish)
    PUT = "PE"   # Put Option (Bearish)

class TradingMode(Enum):
    """Trading mode - paper or live"""
    PAPER = "paper"
    LIVE = "live"

# PRIMARY TRADING FLAGS
OPTION_TYPE: OptionType = OptionType.CALL  # Change to PUT for bearish trades
TRADING_MODE: TradingMode = TradingMode.PAPER  # Switch to LIVE for real trading

# =============================================================================
# ZERODHA KITE API CREDENTIALS
# =============================================================================

KITE_API_KEY = os.getenv("KITE_API_KEY", "")
KITE_API_SECRET = os.getenv("KITE_API_SECRET", "")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN", "")  # Generated daily via login
KITE_REQUEST_TOKEN = os.getenv("KITE_REQUEST_TOKEN", "")  # From redirect URL

# =============================================================================
# CAPITAL & POSITION SIZING (INR) - OPTIMIZED FOR ₹20,000
# =============================================================================

INITIAL_CAPITAL_INR = 20000.00   # ₹20,000 starting capital
TRADE_AMOUNT_INR = 18000.00      # Use most of capital (1 lot)
MIN_CAPITAL_THRESHOLD_INR = 15000.00  # Stop if drops below ₹15K (₹5K max total loss)
MAX_POSITION_SIZE_INR = 25000.00  # Maximum open position value

# Auto-compounding settings
REINVEST_PROFITS = True          # Compound profits automatically!
COMPOUND_AFTER_TRADES = 5        # Recalculate position size every 5 trades

# Lot sizes for popular indices
LOT_SIZES = {
    "NIFTY": 50,      # NIFTY lot size
    "BANKNIFTY": 15,  # Bank NIFTY lot size
    "FINNIFTY": 40,   # Financial NIFTY lot size
    "MIDCPNIFTY": 75, # Midcap NIFTY lot size
    "SENSEX": 10,     # BSE SENSEX lot size
}

# =============================================================================
# TRADING INSTRUMENTS
# =============================================================================

# Primary trading instrument
PRIMARY_INDEX = "NIFTY"  # Options: NIFTY, BANKNIFTY, FINNIFTY
PRIMARY_EXCHANGE = "NFO"  # NSE F&O segment

# Spot index for reference
SPOT_SYMBOLS = {
    "NIFTY": "NSE:NIFTY 50",
    "BANKNIFTY": "NSE:NIFTY BANK",
    "FINNIFTY": "NSE:NIFTY FIN SERVICE",
    "MIDCPNIFTY": "NSE:NIFTY MIDCAP 50",
}

# =============================================================================
# OPTIONS SELECTION CRITERIA
# =============================================================================

# Strike selection - OTM for lower premium with small capital
STRIKE_SELECTION_MODE = "OTM_1"  # 1 strike OTM = lower premium, good for ₹20K
OTM_OFFSET = 1  # Number of strikes away from ATM for OTM trades
STRIKE_INTERVAL = {
    "NIFTY": 50,       # NIFTY strikes are 50 points apart
    "BANKNIFTY": 100,  # Bank NIFTY strikes are 100 points apart
    "FINNIFTY": 50,
    "MIDCPNIFTY": 25,
}

# Expiry selection
EXPIRY_PREFERENCE = "WEEKLY"  # WEEKLY, MONTHLY, NEXT_WEEK
MIN_DAYS_TO_EXPIRY = 1  # Minimum days to expiry for new trades
MAX_DAYS_TO_EXPIRY = 7  # Maximum days to expiry for weekly options

# =============================================================================
# OPTIONS GREEKS THRESHOLDS
# =============================================================================

# Delta thresholds (probability proxy)
MIN_DELTA_CALL = 0.30  # Minimum delta for calls (30% ITM probability)
MAX_DELTA_CALL = 0.70  # Maximum delta for calls
MIN_DELTA_PUT = -0.70  # Minimum delta for puts
MAX_DELTA_PUT = -0.30  # Maximum delta for puts

# Theta considerations (time decay)
MAX_THETA_DECAY_PCT = 5.0  # Maximum acceptable theta decay % per day

# Implied Volatility
MIN_IV = 10.0   # Minimum IV for trades (avoid low volatility)
MAX_IV = 50.0   # Maximum IV for buying options (avoid expensive premiums)
IV_PERCENTILE_BUY = 30  # Buy when IV percentile below this (cheap options)
IV_PERCENTILE_SELL = 70  # Consider selling when IV above this

# Gamma scalping threshold
HIGH_GAMMA_THRESHOLD = 0.05  # High gamma zone for scalping opportunities

# =============================================================================
# PROFIT & LOSS TARGETS (INR) - OPTIMIZED: LOSS < PROFIT (1:2 Risk/Reward)
# =============================================================================

# Per trade targets - PROFIT IS 2X THE LOSS!
PROFIT_TARGET_INR = 1000.00    # ₹1,000 profit target per trade
PROFIT_TARGET_PCT = 0.05       # 5% profit on premium
STOP_LOSS_PCT = 0.02           # 2% stop loss (TIGHT!)
MAX_LOSS_PER_TRADE_INR = 500.00   # Maximum ₹500 loss per trade

# Risk/Reward = 1:2 (Risk ₹500 to make ₹1,000)
# Break-even win rate = 33% (only need to win 1 out of 3!)

# Daily limits
MAX_DAILY_PROFIT_INR = 3000.00    # Stop after ₹3K daily profit (protect gains)
MAX_DAILY_LOSS_INR = 1500.00      # Stop after ₹1.5K daily loss
MAX_DAILY_TRADES = 5              # Max 5 trades per day (quality over quantity)

# Position management
MAX_CONSECUTIVE_LOSSES = 2  # Stop after 2 losses in a row (preserve capital)
COOLDOWN_MINUTES = 15       # Wait 15 min between trades (avoid revenge trading)

# =============================================================================
# TRAILING STOP - RIDE PROFITS TO THE TOP!
# =============================================================================

ENABLE_TRAILING_STOP = True
TRAILING_STOP_ACTIVATION_PCT = 0.03  # Activate after 3% profit
TRAILING_STOP_DISTANCE_PCT = 0.01    # Trail just 1% below peak (TIGHT - lock profits!)

# Example: Buy @ ₹100, rises to ₹115, stop at ₹113.85
# Price drops to ₹113 → SELL! Locked ₹13 profit instead of just ₹5 target

# Progressive profit targets (scales with YOUR capital growth)
PROFIT_TIERS = {
    15000: 800,     # ₹15K capital → ₹800 target
    20000: 1000,    # ₹20K capital → ₹1,000 target
    30000: 1500,    # ₹30K capital → ₹1,500 target
    50000: 2500,    # ₹50K capital → ₹2,500 target
    75000: 3500,    # ₹75K capital → ₹3,500 target
    100000: 5000,   # ₹1L capital → ₹5,000 target
}

# =============================================================================
# ML MODEL CONFIGURATION
# =============================================================================

# Model settings
ML_MODEL_PATH = "ml_models/options_model.pkl"
ML_SCALER_PATH = "ml_models/options_scaler.pkl"
ML_MIN_TRAINING_TRADES = 30  # Minimum trades before ML training

# Confidence thresholds
ML_CONFIDENCE_THRESHOLD = 0.65  # Minimum ML confidence for trade
ML_STRONG_SIGNAL_THRESHOLD = 0.80  # Strong ML signal

# Feature engineering
ML_LOOKBACK_PERIODS = [5, 10, 20, 50]  # Periods for feature calculation
ML_FEATURE_COUNT = 45  # Total features for ML model

# Adaptive threshold
ADAPTIVE_THRESHOLD_MIN = 55
ADAPTIVE_THRESHOLD_MAX = 85
ADAPTIVE_THRESHOLD_ADJUSTMENT = 3  # Points adjustment per evaluation

# =============================================================================
# LLM (CLAUDE) CONFIGURATION
# =============================================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-sonnet-4-5-20250929"  # Claude model for decisions

# LLM call optimization
SKIP_LLM_BELOW_SCORE = 50  # Skip LLM if score below this (clear HOLD)
SKIP_LLM_ABOVE_SCORE = 85  # Skip LLM if score above this (clear BUY)
LLM_COST_PER_CALL_INR = 5.0  # Estimated cost per Claude API call

# System prompt configuration
LLM_TEMPERATURE = 0.1  # Low temperature for consistent decisions
LLM_MAX_TOKENS = 1000  # Maximum response tokens

# =============================================================================
# TECHNICAL ANALYSIS SETTINGS
# =============================================================================

# RSI settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30  # Buy signal for calls
RSI_OVERBOUGHT = 70  # Buy signal for puts

# Moving averages
EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50

# MACD settings
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD_DEV = 2.0

# ATR for volatility
ATR_PERIOD = 14
ATR_MULTIPLIER = 1.5

# Volume analysis
VOLUME_MA_PERIOD = 20
VOLUME_SPIKE_THRESHOLD = 1.5  # 1.5x average volume

# =============================================================================
# MARKET TIMING (IST)
# =============================================================================

MARKET_OPEN = time(9, 15)   # 9:15 AM IST
MARKET_CLOSE = time(15, 30)  # 3:30 PM IST

# Trading windows
MORNING_SESSION_START = time(9, 20)   # Avoid first 5 minutes volatility
MORNING_SESSION_END = time(11, 30)
AFTERNOON_SESSION_START = time(13, 0)
AFTERNOON_SESSION_END = time(15, 15)  # Stop 15 min before close

# No trading during lunch (optional)
AVOID_LUNCH_HOURS = True
LUNCH_START = time(12, 30)
LUNCH_END = time(13, 30)

# Expiry day special handling
EXPIRY_DAY_TRADING = True  # Trade on expiry day
EXPIRY_DAY_CLOSE_BY = time(14, 30)  # Close positions by 2:30 PM on expiry

# =============================================================================
# SCHEDULING & INTERVALS
# =============================================================================

SCAN_INTERVAL_SECONDS = 60      # Scan for opportunities every 60 seconds
MONITOR_INTERVAL_SECONDS = 30   # Monitor open positions every 30 seconds
GREEKS_UPDATE_INTERVAL = 120    # Update Greeks every 2 minutes

# API rate limiting
API_RATE_LIMIT_PER_SECOND = 3   # Zerodha rate limit
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY_SECONDS = 2

# =============================================================================
# RISK MANAGEMENT
# =============================================================================

# Position limits
MAX_OPEN_POSITIONS = 1  # Only 1 position at a time (small capital)
MAX_LOTS_PER_TRADE = 1  # Only 1 lot with ₹20K capital

# Margin requirements
MARGIN_BUFFER_PCT = 20  # Keep 20% extra margin buffer

# Hedging (for advanced strategies)
ENABLE_HEDGING = False  # Enable protective positions
HEDGE_DELTA_THRESHOLD = 0.8  # Hedge when delta exposure exceeds this

# =============================================================================
# NOTIFICATION & ALERTS
# =============================================================================

ENABLE_TELEGRAM_ALERTS = False
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Alert thresholds
ALERT_ON_TRADE = True
ALERT_ON_PROFIT_TARGET = True
ALERT_ON_STOP_LOSS = True
ALERT_ON_DAILY_LIMIT = True

# =============================================================================
# LOGGING & DATABASE
# =============================================================================

LOG_LEVEL = "INFO"
LOG_FILE = "logs/options_trading.log"
DATABASE_PATH = "tracking/options_trades.db"

# Data retention
KEEP_TRADE_HISTORY_DAYS = 365
KEEP_MARKET_DATA_DAYS = 30

# =============================================================================
# FEES & COSTS (Zerodha)
# =============================================================================

BROKERAGE_PER_ORDER = 20.00  # ₹20 per executed order (F&O)
STT_PCT = 0.0005  # 0.05% STT on sell side (options)
EXCHANGE_TXN_PCT = 0.00053  # Exchange transaction charges
GST_PCT = 0.18  # 18% GST on brokerage + transaction charges
SEBI_CHARGES_PCT = 0.000001  # SEBI charges
STAMP_DUTY_PCT = 0.00003  # Stamp duty on buy side

# Total estimated round-trip cost
ESTIMATED_ROUND_TRIP_COST_PCT = 0.002  # ~0.2% of trade value

# =============================================================================
# STRATEGY FLAGS
# =============================================================================

class Strategy(Enum):
    """Available trading strategies"""
    MOMENTUM = "momentum"          # Trend following
    MEAN_REVERSION = "mean_reversion"  # RSI oversold/overbought
    BREAKOUT = "breakout"          # Support/resistance breakout
    SCALPING = "scalping"          # Quick in-and-out trades
    SWING = "swing"                # Multi-day positions

ACTIVE_STRATEGY = Strategy.MOMENTUM  # Current active strategy

# Strategy-specific settings
STRATEGY_SETTINGS = {
    Strategy.MOMENTUM: {
        "min_trend_strength": 0.6,
        "entry_on_pullback": True,
        "hold_duration_minutes": 60,
    },
    Strategy.MEAN_REVERSION: {
        "rsi_entry_oversold": 25,
        "rsi_entry_overbought": 75,
        "quick_exit": True,
    },
    Strategy.BREAKOUT: {
        "breakout_confirmation_candles": 2,
        "volume_confirmation": True,
    },
    Strategy.SCALPING: {
        "max_hold_minutes": 15,
        "tight_stops": True,
        "profit_target_pct": 0.02,
    },
    Strategy.SWING: {
        "min_hold_hours": 4,
        "wider_stops": True,
        "profit_target_pct": 0.08,
    },
}

# =============================================================================
# PAPER TRADING SIMULATION
# =============================================================================

PAPER_TRADING_SLIPPAGE_PCT = 0.001  # 0.1% simulated slippage
PAPER_TRADING_FILL_PROBABILITY = 0.95  # 95% fill rate simulation

# =============================================================================
# DEBUG & DEVELOPMENT
# =============================================================================

DEBUG_MODE = False
VERBOSE_LOGGING = False
SAVE_RAW_DATA = True  # Save raw market data for backtesting
BACKTESTING_MODE = False

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_lot_size(index: str = PRIMARY_INDEX) -> int:
    """Get lot size for given index"""
    return LOT_SIZES.get(index, 50)

def get_strike_interval(index: str = PRIMARY_INDEX) -> int:
    """Get strike interval for given index"""
    return STRIKE_INTERVAL.get(index, 50)

def get_profit_target(current_capital: float) -> float:
    """Get profit target based on current capital"""
    for capital_threshold, target in sorted(PROFIT_TIERS.items(), reverse=True):
        if current_capital >= capital_threshold:
            return target
    return 1000.0  # Default target

def is_market_hours() -> bool:
    """Check if current time is within market hours"""
    from datetime import datetime
    import pytz

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist).time()

    if now < MARKET_OPEN or now > MARKET_CLOSE:
        return False

    if AVOID_LUNCH_HOURS and LUNCH_START <= now <= LUNCH_END:
        return False

    return True

def get_option_symbol(
    index: str,
    expiry_date: str,
    strike: int,
    option_type: OptionType = OPTION_TYPE
) -> str:
    """
    Generate Zerodha option symbol
    Format: NIFTY23DEC24500CE
    """
    return f"{index}{expiry_date}{strike}{option_type.value}"


# =============================================================================
# CONFIGURATION SUMMARY
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ZERODHA OPTIONS TRADING BOT - CONFIGURATION")
    print("=" * 60)
    print(f"\nOption Type: {OPTION_TYPE.value} ({'CALL - Bullish' if OPTION_TYPE == OptionType.CALL else 'PUT - Bearish'})")
    print(f"Trading Mode: {TRADING_MODE.value}")
    print(f"Primary Index: {PRIMARY_INDEX}")
    print(f"Lot Size: {get_lot_size()}")
    print(f"\nCapital Settings:")
    print(f"  Initial Capital: ₹{INITIAL_CAPITAL_INR:,.2f}")
    print(f"  Trade Amount: ₹{TRADE_AMOUNT_INR:,.2f}")
    print(f"  Min Capital Threshold: ₹{MIN_CAPITAL_THRESHOLD_INR:,.2f}")
    print(f"\nProfit/Loss Settings:")
    print(f"  Profit Target: ₹{PROFIT_TARGET_INR:,.2f} ({PROFIT_TARGET_PCT*100:.1f}%)")
    print(f"  Stop Loss: {STOP_LOSS_PCT*100:.1f}%")
    print(f"  Max Daily Loss: ₹{MAX_DAILY_LOSS_INR:,.2f}")
    print(f"\nML Settings:")
    print(f"  Confidence Threshold: {ML_CONFIDENCE_THRESHOLD*100:.0f}%")
    print(f"  Min Training Trades: {ML_MIN_TRAINING_TRADES}")
    print(f"\nStrategy: {ACTIVE_STRATEGY.value}")
    print("=" * 60)
