from config import (
    MIN_CONFIDENCE, 
    COOLDOWN_MINUTES, 
    MAX_POSITION_SIZE,
    TRADE_AMOUNT_GBP,
    TRADING_MODE
)
from datetime import datetime, timedelta

class TradingRules:
    """
    Safety rules and risk management for trading decisions.
    """
    
    def __init__(self):
        self.last_trade_time = None
        self.open_positions = {}  # {product_id: {amount, entry_price, timestamp}}
    
    def check_confidence_threshold(self, confidence: float) -> tuple[bool, str]:
        """
        Check if confidence meets minimum threshold.
        
        Returns:
            (passed, reason)
        """
        if confidence >= MIN_CONFIDENCE:
            return True, f"Confidence {confidence:.0%} meets threshold {MIN_CONFIDENCE:.0%}"
        else:
            return False, f"Confidence {confidence:.0%} below threshold {MIN_CONFIDENCE:.0%}"
    
    def check_cooldown(self) -> tuple[bool, str]:
        """
        Check if enough time has passed since last trade.
        
        Returns:
            (passed, reason)
        """
        if self.last_trade_time is None:
            return True, "No recent trades"
        
        time_since_last = datetime.now() - self.last_trade_time
        cooldown = timedelta(minutes=COOLDOWN_MINUTES)
        
        if time_since_last >= cooldown:
            return True, f"Cooldown satisfied ({time_since_last.seconds // 60} minutes since last trade)"
        else:
            remaining = (cooldown - time_since_last).seconds // 60
            return False, f"Cooldown active: {remaining} minutes remaining"
    
    def check_position_limit(self, product_id: str) -> tuple[bool, str]:
        """
        Check if we already have an open position.
        
        Returns:
            (passed, reason)
        """
        if product_id in self.open_positions:
            position = self.open_positions[product_id]
            return False, f"Already have open position: {position['amount']} {product_id} at £{position['entry_price']}"
        else:
            return True, "No open position"
    
    def check_balance(self, available_balance: float, trade_amount: float) -> tuple[bool, str]:
        """
        Check if we have enough balance for the trade.
        In paper mode, be more lenient.
        
        Returns:
            (passed, reason)
        """
        # Add 1% buffer for fees
        required = trade_amount * 1.01
        
        # In paper mode, allow if balance is close (within 5%)
        if TRADING_MODE == "paper":
            if available_balance >= trade_amount * 0.95:
                return True, f"Sufficient balance for paper trading: £{available_balance:.2f} available"
        
        if available_balance >= required:
            return True, f"Sufficient balance: £{available_balance:.2f} available"
        else:
            if TRADING_MODE == "paper":
                return True, f"Paper mode: allowing trade despite low balance (£{available_balance:.2f})"
            return False, f"Insufficient balance: need £{required:.2f}, have £{available_balance:.2f}"
    
    def check_trade_amount(self, trade_amount: float) -> tuple[bool, str]:
        """
        Check if trade amount is within limits.
        
        Returns:
            (passed, reason)
        """
        if trade_amount > MAX_POSITION_SIZE:
            return False, f"Trade amount £{trade_amount} exceeds max position size £{MAX_POSITION_SIZE}"
        
        if trade_amount < 10:  # Coinbase minimum
            return False, f"Trade amount £{trade_amount} below minimum £10"
        
        return True, f"Trade amount £{trade_amount} within limits"
    
    def check_trading_mode(self, action: str) -> tuple[bool, str]:
        """
        Check trading mode. Paper mode should allow trades (they'll be simulated).
        
        Returns:
            (passed, reason)
        """
        if TRADING_MODE == "paper":
            return True, f"Paper trading mode: trade will be simulated"
        elif TRADING_MODE == "live":
            return True, f"Live trading mode: trade will be executed on Coinbase"
        else:
            return False, f"Unknown trading mode: {TRADING_MODE}"
    
    def record_trade(self, product_id: str, action: str, amount: float, price: float):
        """
        Record a trade execution.
        """
        self.last_trade_time = datetime.now()
        
        if action == "BUY":
            self.open_positions[product_id] = {
                "amount": amount,
                "entry_price": price,
                "timestamp": self.last_trade_time
            }
        elif action == "SELL" and product_id in self.open_positions:
            del self.open_positions[product_id]
    
    def get_position(self, product_id: str) -> dict:
        """
        Get current position for a product.
        """
        return self.open_positions.get(product_id, None)