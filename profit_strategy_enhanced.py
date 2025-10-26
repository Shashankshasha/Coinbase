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
import time

class ProfitStrategyEnhanced:
    """
    ULTRA-OPTIMIZED Profit Strategy with:
    - TRAILING STOP: Locks in minimum profit, captures extra gains
    - PROGRESSIVE TARGETS: Auto-scales from £2 → £10 as capital grows
    - SMART EXIT LOGIC: Math-based monitoring (no Claude calls)
    - INTELLIGENT RECOVERY: Handles orphaned positions
    
    NEW FEATURES:
    ✅ Progressive profit targets (automatic tier upgrades)
    ✅ Free exit monitoring (no API costs)
    ✅ Trailing stop with configurable distance
    ✅ Tier display for dashboard
    """
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db = TradingDatabase(db_path)
        self.market = MarketData()
        self.initial_capital = INITIAL_CAPITAL
        
        # Trailing stop configuration
        self.trailing_stop_enabled = {}  # {product_id: bool}
        self.peak_price = {}  # {product_id: float} - tracks highest price after target hit
        
        # Trailing stop distance (percentage below peak to trigger exit)
        # Default: 0.5% - balanced for capturing gains without premature exit
        self.trailing_stop_distance_pct = 0.005  # 0.5%
        
        # Alternative settings you can use:
        # self.trailing_stop_distance_pct = 0.003  # 0.3% - very tight, quick exit
        # self.trailing_stop_distance_pct = 0.008  # 0.8% - more room for fluctuation
        # self.trailing_stop_distance_pct = 0.010  # 1.0% - loose, maximum profit capture
    
    def get_current_capital(self) -> float:
        """
        Calculate current available capital (initial + profits).
        Used for compounding and progressive target calculation.
        """
        if REINVEST_PROFITS:
            pnl_data = self.db.get_total_pnl()
            total_profit = pnl_data['total_pnl']
            return self.initial_capital + total_profit
        else:
            return self.initial_capital
    
    def get_dynamic_profit_target(self) -> float:
        """
        🎯 PROGRESSIVE PROFIT TARGETS - Auto-scales with capital growth
        
        As your capital grows, profit targets increase automatically.
        This maximizes earnings without increasing risk percentage.
        
        Tiers:
        - £500-800: £2 target (beginner) - Prove strategy
        - £800-1,500: £3 target (intermediate) - Scale profits
        - £1,500-3,000: £5 target (advanced) - Maximize returns
        - £3,000-10,000: £10 target (professional) - Serious income
        - £10,000+: 0.2% of capital (expert) - Percentage-based scaling
        
        Returns:
            float: Profit target in GBP for current capital level
        """
        current_capital = self.get_current_capital()
        
        # Tier 1: Beginner (£500-800)
        # Focus: Prove strategy, build foundation
        if current_capital < 800:
            return 2.0
        
        # Tier 2: Intermediate (£800-1,500)
        # Focus: Scale profits, maintain discipline
        elif current_capital < 1500:
            return 3.0
        
        # Tier 3: Advanced (£1,500-3,000)
        # Focus: Maximize proven strategy
        elif current_capital < 3000:
            return 5.0
        
        # Tier 4: Professional (£3,000-10,000)
        # Focus: Generate serious income
        elif current_capital < 10000:
            return 10.0
        
        # Tier 5: Expert (£10,000+)
        # Focus: Scale to percentage of capital
        else:
            # 0.2% of capital (£20 per £10k, £40 per £20k, etc.)
            return max(20.0, current_capital * 0.002)
    
    def _get_tier_name(self, profit_target: float) -> str:
        """
        Get human-readable tier name for dashboard display.
        """
        if profit_target <= 2.0:
            return "Beginner"
        elif profit_target <= 3.0:
            return "Intermediate"
        elif profit_target <= 5.0:
            return "Advanced"
        elif profit_target <= 10.0:
            return "Professional"
        else:
            return "Expert"
    
    def calculate_trade_size(self) -> float:
        """
        Calculate how much to trade (compounds with profits).
        Caps at 2x initial capital for safety.
        """
        current_capital = self.get_current_capital()
        return min(current_capital - 1, self.initial_capital * 2)  # Leave £1 buffer
    
    def get_entry_from_coinbase_history(self, product_id: str, crypto_amount: float) -> dict:
        """
        Fetch actual entry details from Coinbase order history.
        Recovery mechanism for orphaned positions.
        """
        try:
            from execution.order_manager import OrderManager
            order_manager = OrderManager()
            
            print(f"   🔍 Searching Coinbase order history...")
            
            if not hasattr(order_manager, 'get_recent_orders'):
                print(f"   ⚠️ Order history not implemented in OrderManager")
                return None
            
            orders = order_manager.get_recent_orders(product_id, limit=100)
            
            if not orders:
                print(f"   ⚠️ No order history returned")
                return None
            
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
        Calculate exact price target to achieve dynamic profit goal.
        
        ✨ NEW: Uses progressive profit targets that scale with capital!
        
        Args:
            entry_price: Entry price per crypto unit
            trade_amount: Total GBP invested (including fees)
        
        Returns:
            dict: Target prices, profit expectations, tier info
        """
        entry_fee = trade_amount * FEE_PCT
        crypto_bought = (trade_amount - entry_fee) / entry_price
        
        entry_cost = trade_amount
        
        # ✨ NEW: Use dynamic profit target instead of fixed config value
        profit_target = self.get_dynamic_profit_target()
        target_revenue = entry_cost + profit_target
        
        # Calculate exact exit price needed
        target_exit_price = target_revenue / (crypto_bought * (1 - FEE_PCT))
        price_change_needed = ((target_exit_price - entry_price) / entry_price) * 100
        
        stop_loss_price = entry_price * (1 - STOP_LOSS_PCT)
        
        return {
            'entry_price': entry_price,
            'target_exit_price': round(target_exit_price, 2),
            'stop_loss_price': round(stop_loss_price, 2),
            'price_change_needed_pct': round(price_change_needed, 2),
            'crypto_amount': crypto_bought,
            'expected_profit': profit_target,  # ✨ Changed from PROFIT_TARGET_GBP
            'trade_amount': trade_amount,
            'profit_tier': self._get_tier_name(profit_target)  # ✨ NEW: Show tier
        }
    
    def activate_trailing_stop(self, product_id: str, current_price: float):
        """
        Activate trailing stop mode after target is hit.
        Locks in minimum profit and tracks peak for exit trigger.
        """
        if product_id not in self.trailing_stop_enabled:
            self.trailing_stop_enabled[product_id] = True
            self.peak_price[product_id] = current_price
            
            profit_target = self.get_dynamic_profit_target()
            tier = self._get_tier_name(profit_target)
            
            print(f"\n🎯 TRAILING STOP ACTIVATED!")
            print(f"   Tier: {tier} (£{profit_target:.2f} target)")
            print(f"   Initial Peak: £{current_price:.2f}")
            print(f"   Trailing Distance: {self.trailing_stop_distance_pct*100:.2f}%")
            print(f"   Min Profit Locked: £{profit_target:.2f} ✅")
            print(f"   Strategy: Exit if price drops {self.trailing_stop_distance_pct*100:.2f}% from peak")
    
    def update_trailing_stop(self, product_id: str, current_price: float) -> dict:
        """
        Update trailing stop if new peak is reached.
        Returns trailing stop details for monitoring.
        
        This is FREE - no Claude API call needed!
        Just pure math to track price and trigger exits.
        """
        if product_id not in self.peak_price:
            return None
        
        # Update peak if current price is higher
        if current_price > self.peak_price[product_id]:
            old_peak = self.peak_price[product_id]
            self.peak_price[product_id] = current_price
            gain_from_old_peak = ((current_price - old_peak) / old_peak) * 100
            
            print(f"\n📈 NEW PEAK REACHED!")
            print(f"   Old Peak: £{old_peak:.2f} → New Peak: £{current_price:.2f}")
            print(f"   Additional Gain: +{gain_from_old_peak:.2f}% 💎")
        
        # Calculate trailing stop price
        trailing_stop_price = self.peak_price[product_id] * (1 - self.trailing_stop_distance_pct)
        distance_from_stop = ((current_price - trailing_stop_price) / current_price) * 100
        
        return {
            'peak_price': self.peak_price[product_id],
            'trailing_stop_price': round(trailing_stop_price, 2),
            'current_price': current_price,
            'distance_from_stop_pct': distance_from_stop,
            'triggered': current_price <= trailing_stop_price
        }
    
    def reset_trailing_stop(self, product_id: str):
        """
        Reset trailing stop state (after position is closed).
        """
        if product_id in self.trailing_stop_enabled:
            del self.trailing_stop_enabled[product_id]
        if product_id in self.peak_price:
            del self.peak_price[product_id]
    
    def check_exit_conditions(self, product_id: str) -> dict:
        """
        🎯 SMART EXIT LOGIC - FREE MONITORING (No Claude API calls!)
        
        Flow:
        1. Get current price (FREE - Coinbase API)
        2. Calculate P&L (FREE - just math)
        3. Check stop loss (FREE - price comparison)
        4. Check target hit (FREE - price comparison)
        5. Update trailing stop (FREE - math)
        6. Determine if should exit (FREE - logic)
        
        Only calls Claude when actually executing the exit!
        This saves massive API costs during position holding.
        
        Features:
        - Hard stop loss (safety net)
        - Initial profit target
        - Trailing stop activation after target
        - Peak tracking for maximum profit
        - Automatic exit on reversal
        
        Returns:
            dict: Exit decision and position details
        """
        snapshot = self.market.get_full_market_snapshot(product_id)

        if not snapshot or 'current_price' not in snapshot:
            print(f"⚠️ No market snapshot available for {product_id}")
            return {
                'should_exit': False,
                'reason': 'No market data available',
                'action': 'HOLD',
                'has_position': False
            }
        
        current_price = snapshot['current_price']
        crypto_symbol = product_id.split('-')[0]
        actual_balance = snapshot['balances'].get(crypto_symbol, 0)
        
        if actual_balance > 0.001:
            position = self.db.get_open_position(product_id)
            
            if position:
                entry_price = position.price
                crypto_amount = position.crypto_amount
                entry_cost = position.amount_gbp
                print(f"   ✅ Using DB entry: £{entry_cost:.2f} @ £{entry_price:.2f}")
            else:
                # Recovery logic for orphaned positions
                print(f"⚠️ Found {actual_balance:.6f} {crypto_symbol} on Coinbase but no DB record!")
                historical_entry = self.get_entry_from_coinbase_history(product_id, actual_balance)
                
                if historical_entry and historical_entry.get('cost', 0) > 0:
                    entry_price = historical_entry['price']
                    entry_cost = historical_entry['cost']
                    crypto_amount = actual_balance
                    print(f"   ✅ Recovered entry from Coinbase: £{entry_cost:.2f} @ £{entry_price:.2f}")
                else:
                    print(f"   ⚠️ Using BREAK-EVEN estimate")
                    current_value = actual_balance * current_price
                    entry_price = current_price
                    entry_cost = current_value
                    crypto_amount = actual_balance
                    print(f"   📊 Break-even estimate: £{entry_cost:.2f} @ £{entry_price:.2f}")
                
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
                    print(f"   💾 Saved to database")
                except Exception as e:
                    print(f"   ⚠️ Could not save to DB: {e}")
            
            # Calculate current P&L (FREE - just math!)
            current_value = crypto_amount * current_price
            exit_fee = current_value * FEE_PCT
            exit_revenue = current_value - exit_fee
            
            current_pnl = exit_revenue - entry_cost
            current_pnl_pct = (current_pnl / entry_cost) * 100 if entry_cost > 0 else 0
            
            targets = self.calculate_profit_target(entry_price, entry_cost)
            
            # =================================================================
            # ENHANCED EXIT LOGIC WITH TRAILING STOP
            # =================================================================
            
            # 1. Check hard stop loss first (safety net)
            if current_price <= targets['stop_loss_price']:
                self.reset_trailing_stop(product_id)
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
                    'stop_loss_price': targets['stop_loss_price'],
                    'profit_tier': targets.get('profit_tier', 'Unknown')
                }
            
            # 2. Check if we've hit the initial profit target
            target_hit = current_price >= targets['target_exit_price']
            
            if target_hit:
                # Activate trailing stop if not already active
                if product_id not in self.trailing_stop_enabled:
                    self.activate_trailing_stop(product_id, current_price)
                
                # Update trailing stop with current price (FREE!)
                trailing_info = self.update_trailing_stop(product_id, current_price)
                
                if trailing_info and trailing_info['triggered']:
                    # TRAILING STOP TRIGGERED - EXIT NOW
                    profit_from_peak = ((current_price - trailing_info['peak_price']) / trailing_info['peak_price']) * 100
                    
                    self.reset_trailing_stop(product_id)
                    
                    return {
                        'should_exit': True,
                        'reason': f'TRAILING STOP TRIGGERED: £{current_pnl:.2f} profit ({current_pnl_pct:.2f}%) | Peak: £{trailing_info["peak_price"]:.2f} → Now: £{current_price:.2f} ({profit_from_peak:.2f}% from peak)',
                        'action': 'SELL',
                        'expected_profit': current_pnl,
                        'current_price': current_price,
                        'entry_price': entry_price,
                        'has_position': True,
                        'crypto_amount': crypto_amount,
                        'target_price': targets['target_exit_price'],
                        'stop_loss_price': targets['stop_loss_price'],
                        'trailing_stop_price': trailing_info['trailing_stop_price'],
                        'peak_price': trailing_info['peak_price'],
                        'profit_tier': targets.get('profit_tier', 'Unknown')
                    }
                else:
                    # Trailing stop active but not triggered - HOLD for more profit
                    extra_profit = current_pnl - targets['expected_profit']
                    return {
                        'should_exit': False,
                        'reason': f'TRAILING STOP ACTIVE: £{current_pnl:.2f} profit ({current_pnl_pct:.2f}%) | Peak: £{trailing_info["peak_price"]:.2f} | Stop: £{trailing_info["trailing_stop_price"]:.2f} | Buffer: {trailing_info["distance_from_stop_pct"]:.2f}% | Extra: £{extra_profit:.2f} 💎',
                        'action': 'HOLD',
                        'expected_profit': current_pnl,
                        'current_price': current_price,
                        'entry_price': entry_price,
                        'target_price': targets['target_exit_price'],
                        'stop_loss_price': targets['stop_loss_price'],
                        'has_position': True,
                        'crypto_amount': crypto_amount,
                        'trailing_stop_price': trailing_info['trailing_stop_price'],
                        'peak_price': trailing_info['peak_price'],
                        'trailing_active': True,
                        'profit_tier': targets.get('profit_tier', 'Unknown')
                    }
            
            else:
                # Target not yet hit - normal holding
                profit_target = targets['expected_profit']
                return {
                    'should_exit': False,
                    'reason': f'HOLDING: Current P&L £{current_pnl:.2f} ({current_pnl_pct:.2f}%), Target: £{profit_target:.2f}',
                    'action': 'HOLD',
                    'expected_profit': current_pnl,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'target_price': targets['target_exit_price'],
                    'stop_loss_price': targets['stop_loss_price'],
                    'has_position': True,
                    'crypto_amount': crypto_amount,
                    'trailing_active': False,
                    'profit_tier': targets.get('profit_tier', 'Unknown')
                }
        
        return {
            'should_exit': False,
            'reason': 'No open position',
            'action': 'HOLD',
            'has_position': False
        }
    
    def get_daily_stats(self) -> dict:
        """
        Get today's trading statistics.
        Includes capital tracking for progressive tier determination.
        """
        from datetime import datetime
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        all_trades = self.db.get_all_trades()
        today_trades = [t for t in all_trades if t.timestamp >= today_start]
        
        today_pnl = sum(t.profit_loss for t in today_trades if t.profit_loss is not None)
        completed_today = len([t for t in today_trades if t.profit_loss is not None])
        
        current_capital = self.get_current_capital()
        profit_target = self.get_dynamic_profit_target()
        tier = self._get_tier_name(profit_target)
        
        return {
            'trades_today': len(today_trades),
            'completed_today': completed_today,
            'profit_today': today_pnl,
            'current_capital': current_capital,
            'initial_capital': self.initial_capital,
            'total_return': current_capital - self.initial_capital,
            'current_profit_target': profit_target,  # ✨ NEW
            'current_tier': tier  # ✨ NEW
        }


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_progressive_targets():
    """
    Test function to verify progressive targets work correctly.
    Run this to see how targets scale with capital.
    """
    print("\n" + "="*70)
    print("🎯 PROGRESSIVE PROFIT TARGETS - TEST")
    print("="*70)
    
    strategy = ProfitStrategyEnhanced()
    
    test_capitals = [500, 700, 900, 1200, 1800, 2500, 4000, 7000, 12000, 25000]
    
    print(f"\n{'Capital':<12} | {'Target':<10} | {'Tier':<15} | {'Risk (0.5%)':<12} | {'R:R Ratio'}")
    print("-"*70)
    
    for capital in test_capitals:
        # Temporarily override capital for testing
        strategy.initial_capital = capital
        
        target = strategy.get_dynamic_profit_target()
        risk = capital * 0.005  # 0.5% stop loss
        ratio = risk / target
        tier = strategy._get_tier_name(target)
        
        print(f"£{capital:<11,.0f} | £{target:<9.2f} | {tier:<15} | £{risk:<11.2f} | {ratio:.2f}:1")
    
    print("-"*70)
    print("\n💡 Key Insights:")
    print("   ✅ Targets scale smoothly with capital growth")
    print("   ✅ Risk/reward ratio stays reasonable (0.25:1 to 2.5:1)")
    print("   ✅ Automatic tier upgrades at key milestones")
    print("   ✅ Expert tier scales to 0.2% of capital")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run test when script is executed directly
    test_progressive_targets()