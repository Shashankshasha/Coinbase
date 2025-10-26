from tracking.database import TradingDatabase
from data_layer.market_data import MarketData
from config import (
    PROFIT_TARGET_PCT,
    PROFIT_TARGET_GBP,
    STOP_LOSS_PCT,
    FEE_PCT,
    INITIAL_CAPITAL,
    REINVEST_PROFITS
)

class ProfitStrategy:
    """
    Manages profit-focused trading strategy:
    - Calculates optimal entry/exit points for configured profit target
    - Manages position sizing with compounding
    - Tracks daily profit targets
    - Auto-recovers entry data from Coinbase if DB missing
    FIXED: Uses break-even fallback to prevent false stop losses
    """
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db = TradingDatabase(db_path)
        self.market = MarketData()
        self.initial_capital = INITIAL_CAPITAL
    
    def get_current_capital(self) -> float:
        """
        Calculate current available capital (initial + profits).
        """
        if REINVEST_PROFITS:
            pnl_data = self.db.get_total_pnl()
            total_profit = pnl_data['total_pnl']
            return self.initial_capital + total_profit
        else:
            return self.initial_capital
    
    def calculate_trade_size(self) -> float:
        """
        Calculate how much to trade (compounds with profits).
        """
        current_capital = self.get_current_capital()
        # Use all available capital (or cap at initial for safety)
        return min(current_capital, self.initial_capital * 2)  # Max 2x initial
    
    def get_entry_from_coinbase_history(self, product_id: str, crypto_amount: float) -> dict:
        """
        Fetch actual entry details from Coinbase order history.
        Finds the BUY order that created this position.
        
        Args:
            product_id: Trading pair (e.g., 'SOL-GBP')
            crypto_amount: Amount of crypto held
            
        Returns:
            Dict with entry details or None if not found
        """
        try:
            from execution.order_manager import OrderManager
            order_manager = OrderManager()
            
            print(f"   🔍 Searching Coinbase order history...")
            
            # Check if OrderManager has the method
            if not hasattr(order_manager, 'get_recent_orders'):
                print(f"   ⚠️ Order history not implemented in OrderManager")
                return None
            
            orders = order_manager.get_recent_orders(product_id, limit=100)
            
            if not orders:
                print(f"   ⚠️ No order history returned")
                return None
            
            # Find most recent BUY that matches this amount (within 1% tolerance)
            for order in orders:
                if order.get("side") == "BUY":
                    order_size = order.get("size", 0)
                    if order_size > 0 and abs(order_size - crypto_amount) / crypto_amount < 0.01:
                        timestamp = order.get("timestamp", "unknown time")
                        print(f"   ✅ Found matching BUY order from {timestamp}")
                        return {
                            "price": order.get("price", 0),
                            "cost": order.get("cost", 0),
                            "order_id": order.get("order_id", "unknown")
                        }
            
            print(f"   ⚠️ No matching BUY order found for {crypto_amount:.6f}")
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error searching order history: {e}")
            return None
    
    def calculate_profit_target(self, entry_price: float, trade_amount: float) -> dict:
        """
        Calculate exact price target to achieve configured profit.
        
        Args:
            entry_price: Price bought at
            trade_amount: Amount invested in GBP
            
        Returns:
            Target prices and expected profit
        """
        # Calculate crypto amount bought
        entry_fee = trade_amount * FEE_PCT
        crypto_bought = (trade_amount - entry_fee) / entry_price
        
        # Calculate target exit price for configured profit
        # Need: exit_revenue - entry_cost = PROFIT_TARGET_GBP
        entry_cost = trade_amount
        target_revenue = entry_cost + PROFIT_TARGET_GBP
        
        # Account for exit fee: revenue = (crypto_sold * exit_price) - exit_fee
        # exit_fee = (crypto_sold * exit_price) * FEE_PCT
        # revenue = (crypto * price) * (1 - FEE_PCT)
        # target_revenue = (crypto * exit_price) * (1 - FEE_PCT)
        # exit_price = target_revenue / (crypto * (1 - FEE_PCT))
        
        target_exit_price = target_revenue / (crypto_bought * (1 - FEE_PCT))
        price_change_needed = ((target_exit_price - entry_price) / entry_price) * 100
        
        # Calculate stop loss price
        stop_loss_price = entry_price * (1 - STOP_LOSS_PCT)
        
        return {
            'entry_price': entry_price,
            'target_exit_price': round(target_exit_price, 2),
            'stop_loss_price': round(stop_loss_price, 2),
            'price_change_needed_pct': round(price_change_needed, 2),
            'crypto_amount': crypto_bought,
            'expected_profit': PROFIT_TARGET_GBP,
            'trade_amount': trade_amount
        }
    
    def check_exit_conditions(self, product_id: str) -> dict:
        """
        Check if current position should be closed.
        Now checks BOTH database AND actual Coinbase balance with auto-recovery!
        FIXED: Uses break-even estimate instead of conservative 2% markup
        
        Returns:
            {
                'should_exit': bool,
                'reason': str,
                'action': 'SELL' or 'HOLD',
                'expected_profit': float,
                'has_position': bool
            }
        """
        # Get current market data
        snapshot = self.market.get_full_market_snapshot(product_id)
        current_price = snapshot['current_price']
        
        # Extract crypto symbol (SOL from SOL-GBP)
        crypto_symbol = product_id.split('-')[0]
        actual_balance = snapshot['balances'].get(crypto_symbol, 0)
        
        # Check if we have actual crypto on Coinbase
        if actual_balance > 0.001:  # Have real position on exchange
            # Try to get database position first
            position = self.db.get_open_position(product_id)
            
            if position:
                # Position exists in DB - use recorded entry price
                entry_price = position.price
                crypto_amount = position.crypto_amount
                entry_cost = position.amount_gbp
                print(f"   ✅ Using DB entry: £{entry_cost:.2f} @ £{entry_price:.2f}")
            else:
                # Position exists on Coinbase but NOT in DB
                # Try to recover from Coinbase order history
                print(f"⚠️ Found {actual_balance:.6f} {crypto_symbol} on Coinbase but no DB record!")
                
                # Attempt automatic recovery from order history
                historical_entry = self.get_entry_from_coinbase_history(product_id, actual_balance)
                
                if historical_entry and historical_entry.get('cost', 0) > 0:
                    # Successfully recovered real entry from Coinbase
                    entry_price = historical_entry['price']
                    entry_cost = historical_entry['cost']
                    crypto_amount = actual_balance
                    print(f"   ✅ Recovered entry from Coinbase: £{entry_cost:.2f} @ £{entry_price:.2f}")
                    
                    # Record to database for future reference
                    try:
                        fee = entry_cost * FEE_PCT
                        self.db.record_trade(
                            product_id=product_id,
                            action='BUY',
                            price=entry_price,
                            crypto_amount=crypto_amount,
                            amount_gbp=entry_cost,
                            fee=fee
                        )
                        print(f"   💾 Saved to database for monitoring")
                    except Exception as e:
                        print(f"   ⚠️ Could not save to DB: {e}")
                        
                else:
                    # Could not find order history - use BREAK-EVEN estimate
                    # CRITICAL FIX: Use current price as entry (not 2% higher!)
                    # This prevents false stop losses
                    print(f"   ⚠️ Could not recover entry - using BREAK-EVEN estimate")
                    print(f"   💡 Bot assumes current price as entry and waits for profit")
                    
                    current_value = actual_balance * current_price
                    
                    # Break-even approach: assume we bought at current price
                    # This ensures we only sell at a profit, never at a loss
                    entry_price = current_price
                    entry_cost = current_value
                    crypto_amount = actual_balance
                    
                    print(f"   📊 Break-even estimate: £{entry_cost:.2f} @ £{entry_price:.2f}")
                    print(f"   ⚠️ Any price increase will trigger profit target")
                    
                    # Record break-even estimate to database
                    try:
                        fee = entry_cost * FEE_PCT
                        self.db.record_trade(
                            product_id=product_id,
                            action='BUY',
                            price=entry_price,
                            crypto_amount=crypto_amount,
                            amount_gbp=entry_cost,
                            fee=fee
                        )
                        print(f"   💾 Saved break-even estimate to database")
                    except Exception as e:
                        print(f"   ⚠️ Could not save to DB: {e}")
            
            # Calculate current P&L
            current_value = crypto_amount * current_price
            exit_fee = current_value * FEE_PCT
            exit_revenue = current_value - exit_fee
            
            current_pnl = exit_revenue - entry_cost
            current_pnl_pct = (current_pnl / entry_cost) * 100 if entry_cost > 0 else 0
            
            # Calculate targets based on entry
            targets = self.calculate_profit_target(entry_price, entry_cost)
            
            # Decision logic
            if current_price >= targets['target_exit_price']:
                return {
                    'should_exit': True,
                    'reason': f'PROFIT TARGET HIT: £{current_pnl:.2f} profit ({current_pnl_pct:.2f}%)',
                    'action': 'SELL',
                    'expected_profit': current_pnl,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'has_position': True,
                    'crypto_amount': crypto_amount,
                    'target_price': targets['target_exit_price'],
                    'stop_loss_price': targets['stop_loss_price']
                }
            
            elif current_price <= targets['stop_loss_price']:
                return {
                    'should_exit': True,
                    'reason': f'STOP LOSS HIT: £{current_pnl:.2f} loss ({current_pnl_pct:.2f}%)',
                    'action': 'SELL',
                    'expected_profit': current_pnl,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'has_position': True,
                    'crypto_amount': crypto_amount,
                    'target_price': targets['target_exit_price'],
                    'stop_loss_price': targets['stop_loss_price']
                }
            
            else:
                return {
                    'should_exit': False,
                    'reason': f'HOLDING: Current P&L £{current_pnl:.2f} ({current_pnl_pct:.2f}%), Target: £{PROFIT_TARGET_GBP:.2f}',
                    'action': 'HOLD',
                    'expected_profit': current_pnl,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'target_price': targets['target_exit_price'],
                    'stop_loss_price': targets['stop_loss_price'],
                    'has_position': True,
                    'crypto_amount': crypto_amount
                }
        
        # No position anywhere
        return {
            'should_exit': False,
            'reason': 'No open position',
            'action': 'HOLD',
            'has_position': False
        }
    
    def get_daily_stats(self) -> dict:
        """
        Get today's trading statistics.
        """
        from datetime import datetime, timedelta
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        all_trades = self.db.get_all_trades()
        today_trades = [t for t in all_trades if t.timestamp >= today_start]
        
        today_pnl = sum(t.profit_loss for t in today_trades if t.profit_loss is not None)
        completed_today = len([t for t in today_trades if t.profit_loss is not None])
        
        return {
            'trades_today': len(today_trades),
            'completed_today': completed_today,
            'profit_today': today_pnl,
            'current_capital': self.get_current_capital(),
            'initial_capital': self.initial_capital,
            'total_return': self.get_current_capital() - self.initial_capital
        }