from agent import TradingAgent
from profit_strategy import ProfitStrategy
from tracking.trade_logger import TradeLogger
from config import TRADING_PAIR, MAX_DAILY_TRADES
from datetime import datetime

class AutomatedTradingBot:
    """
    Fully automated trading bot that:
    - Checks for open positions
    - Closes positions when profitable
    - Looks for new entry opportunities
    - Compounds profits
    """
    
    def __init__(self):
        self.agent = TradingAgent()
        self.strategy = ProfitStrategy()
        self.logger = TradeLogger()
        self.product_id = TRADING_PAIR
    
    def run_trading_cycle(self):
        """
        Run one complete trading cycle.
        """
        print("\n" + "="*70)
        print(f"🤖 TRADING CYCLE START - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Check daily limits
        daily_stats = self.strategy.get_daily_stats()
        print(f"\n📊 Today's Stats:")
        print(f"   Trades: {daily_stats['trades_today']} | Completed: {daily_stats['completed_today']}")
        print(f"   Profit Today: £{daily_stats['profit_today']:.2f}")
        print(f"   Current Capital: £{daily_stats['current_capital']:.2f}")
        print(f"   Total Return: £{daily_stats['total_return']:.2f}")
        
        if daily_stats['trades_today'] >= MAX_DAILY_TRADES:
            print("\n⚠️  Daily trade limit reached. Stopping for today.")
            return
        
        # Step 1: Check if we have an open position
        exit_check = self.strategy.check_exit_conditions(self.product_id)
        
        if exit_check['has_position']:
            print(f"\n💼 Open Position Detected")
            print(f"   Entry: £{exit_check['entry_price']:.2f}")
            print(f"   Current: £{exit_check['current_price']:.2f}")
            print(f"   Status: {exit_check['reason']}")
            
            if exit_check['should_exit']:
                print(f"\n🎯 {exit_check['action']} SIGNAL!")
                # Ask Claude to execute the exit
                query = f"""
                We have an open {self.product_id} position that needs to be closed.
                Entry price: £{exit_check['entry_price']:.2f}
                Current price: £{exit_check['current_price']:.2f}
                Expected P&L: £{exit_check['expected_profit']:.2f}
                Reason: {exit_check['reason']}
                
                Execute a SELL order to close this position.
                """
                response = self.agent.run(query)
                print(f"\n{response}\n")
            else:
                print(f"\n⏳ Holding position... waiting for target or stop loss")
        
        else:
            # Step 2: No open position - look for entry
            print(f"\n🔍 No open position. Looking for entry opportunity...")
            
            trade_size = self.strategy.calculate_trade_size()
            
            query = f"""
            Analyze {self.product_id} for a BUY opportunity.
            Available capital: £{trade_size:.2f}
            Target: £1 profit per trade (need 3.2% price gain)
            
            If confidence ≥75% AND conditions favor a 3%+ move, execute a £{trade_size:.2f} BUY.
            Otherwise explain why you're waiting.
            
            Focus on:
            - Strong bullish momentum (RSI rising, EMA crossover)
            - Increasing volume
            - Price near support levels
            """
            
            response = self.agent.run(query)
            print(f"\n{response}\n")
        
        # Reset agent for next cycle
        self.agent.reset()
        
        print("="*70)
        print("✅ Cycle Complete")
        print("="*70 + "\n")
    
    def run_continuous(self, interval_minutes: int = 10):
        """
        Run bot continuously.
        """
        from apscheduler.schedulers.blocking import BlockingScheduler
        
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run_trading_cycle, 'interval', minutes=interval_minutes)
        
        print("\n" + "="*70)
        print("🚀 AUTOMATED TRADING BOT STARTED")
        print("="*70)
        print(f"Trading Pair: {self.product_id}")
        print(f"Cycle Interval: Every {interval_minutes} minutes")
        print(f"Profit Target: £1 per trade")
        print(f"Strategy: Compound profits")
        print(f"\nPress Ctrl+C to stop")
        print("="*70 + "\n")
        
        # Run first cycle immediately
        self.run_trading_cycle()
        
        # Then schedule recurring
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n\n👋 Shutting down trading bot...")

if __name__ == "__main__":
    bot = AutomatedTradingBot()
    bot.run_continuous(interval_minutes=10)  # Check every 10 minutes

    
# ```

# **Save it!**

# ---

# ### **Step 4: Update `.env` for Profit Strategy**

# Add to your `.env`:
# ```
# INITIAL_CAPITAL=50
# PROFIT_TARGET_GBP=1.00
# REINVEST_PROFITS=true