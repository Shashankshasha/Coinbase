from agent import TradingAgent
from profit_strategy import ProfitStrategy
from tracking.trade_logger import TradeLogger
from config import (
    TRADING_PAIR,
    MIN_CONFIDENCE,
    MAX_CONSECUTIVE_LOSSES,
    MIN_CAPITAL_THRESHOLD,
    INITIAL_CAPITAL
)
from datetime import datetime
import time

class BeastModeBot:
    """
    FULLY AUTOMATED AGGRESSIVE TRADING BOT
    - NO daily limits
    - NO human intervention
    - Trades 24/7
    - Targets £1 per trade
    - Compounds profits automatically
    """
    
    def __init__(self):
        self.agent = TradingAgent()
        self.strategy = ProfitStrategy()
        self.logger = TradeLogger()
        self.product_id = TRADING_PAIR
        self.consecutive_losses = 0
        self.is_running = True
    
    def check_safety_limits(self) -> tuple[bool, str]:
        """
        Check if we should stop for safety reasons.
        """
        daily_stats = self.strategy.get_daily_stats()
        current_capital = daily_stats['current_capital']
        
        # Check capital threshold
        if current_capital < MIN_CAPITAL_THRESHOLD:
            return False, f"⛔ Capital dropped to £{current_capital:.2f} (below £{MIN_CAPITAL_THRESHOLD} threshold)"
        
        # Check consecutive losses
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
            return False, f"⛔ {self.consecutive_losses} consecutive losses - stopping for safety"
        
        return True, "All systems go ✅"
    
    def run_cycle(self):
        """
        One complete trading cycle - AGGRESSIVE & AUTOMATED
        """
        print("\n" + "="*70)
        print(f"⚡ CYCLE {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        
        # Check safety
        safe, message = self.check_safety_limits()
        if not safe:
            print(f"\n{message}")
            print("🛑 STOPPING BOT FOR SAFETY")
            self.is_running = False
            return
        
        # Get stats
        daily_stats = self.strategy.get_daily_stats()
        print(f"\n📊 Stats:")
        print(f"   Trades: {daily_stats['completed_today']} | Profit: £{daily_stats['profit_today']:.2f}")
        print(f"   Capital: £{daily_stats['current_capital']:.2f} | Return: £{daily_stats['total_return']:.2f}")
        print(f"   Consecutive Losses: {self.consecutive_losses}")
        
        # Check position
        exit_check = self.strategy.check_exit_conditions(self.product_id)
        
        if exit_check['has_position']:
            # WE HAVE AN OPEN POSITION
            current_pnl = exit_check.get('expected_profit', 0)
            
            print(f"\n💼 Position Open:")
            print(f"   Entry: £{exit_check['entry_price']:.2f}")
            print(f"   Current: £{exit_check['current_price']:.2f}")
            print(f"   P&L: £{current_pnl:.2f}")
            
            if exit_check['should_exit']:
                # TIME TO EXIT!
                print(f"\n🎯 EXITING: {exit_check['reason']}")
            
                trade_size = self.strategy.calculate_trade_size()
                
                # AUTOMATIC SELL - NO ASKING!
                result = self._execute_sell(trade_size, exit_check)
                
                # Track consecutive losses
                if result and result.get('executed'):
                    actual_pnl = result.get('expected_profit', current_pnl)
                    if actual_pnl < 0:
                        self.consecutive_losses += 1
                        print(f"📉 Loss recorded. Consecutive: {self.consecutive_losses}")
                    else:
                        self.consecutive_losses = 0  # Reset on profit
                        print(f"💰 Profit! Resetting loss counter")
            else:
                # HOLDING
                if exit_check.get('target_price'):
                    distance = exit_check['target_price'] - exit_check['current_price']
                    distance_pct = (distance / exit_check['current_price']) * 100
                    print(f"⏳ Holding... Need £{distance:.2f} ({distance_pct:+.2f}%) to hit target")
                    print(f"   Target: £{exit_check['target_price']:.2f}")
                    print(f"   Stop Loss: £{exit_check['stop_loss_price']:.2f}")
        
        else:
            # NO POSITION - LOOK FOR ENTRY
            print(f"\n🔍 No position. Scanning for opportunity...")
            
            trade_size = self.strategy.calculate_trade_size()
            
            # AUTOMATIC BUY SCAN
            self._execute_buy_scan(trade_size)
        
        print("="*70 + "\n")
    
    def _execute_sell(self, trade_size: float, exit_check: dict) -> dict:
        """
        Automatically execute a SELL order - NO ASKING!
        """
        print(f"\n🤖 AUTOMATIC SELL EXECUTION")
        
        query = f"""
AUTOMATIC POSITION CLOSE - EXECUTE IMMEDIATELY, NO QUESTIONS.

Action: SELL
Product: {self.product_id}
Entry Price: £{exit_check['entry_price']:.2f}
Current Price: £{exit_check['current_price']:.2f}
Expected P&L: £{exit_check['expected_profit']:.2f}
Exit Reason: {exit_check['reason']}
Amount: £{trade_size:.2f}

This is position management - EXECUTE NOW using execute_trade_decision tool.
Use confidence 0.95 (position exit, not discretionary entry).
Provide brief reasoning after execution.

DO NOT ASK FOR CONFIRMATION. EXECUTE IMMEDIATELY.
"""
        
        response = self.agent.run(query)
        print(f"\n📤 SELL RESULT:\n{response}\n")
        
        self.agent.reset()
        time.sleep(2)
        
        return exit_check
    
    def _execute_buy_scan(self, trade_size: float):
        """
        Automatically scan and execute BUY if conditions met - NO ASKING!
        """
        print(f"\n🤖 AUTOMATIC BUY SCAN")
        
        query = f"""
AUTOMATIC ENTRY SYSTEM - EXECUTE IF CONDITIONS MET, NO QUESTIONS.

Trading Pair: {self.product_id}
Available Capital: £{trade_size:.2f}
Profit Target: £1 per trade (2.2% price movement)
Confidence Threshold: {MIN_CONFIDENCE*100:.0f}%

YOUR TASK:
1. Analyze market NOW using get_market_analysis tool
2. Calculate confidence level
3. Decision logic:
   - IF confidence ≥ {MIN_CONFIDENCE*100:.0f}% AND 2%+ upside potential exists:
     → EXECUTE £{trade_size:.2f} BUY using execute_trade_decision tool IMMEDIATELY
     → Provide reasoning after execution
   - IF confidence < {MIN_CONFIDENCE*100:.0f}%:
     → Respond "HOLD - [specific reason]"

Favorable buying conditions:
- RSI: 30-65 (not overbought, room to rise)
- EMA10 > EMA50 (bullish trend)
- MACD > Signal (positive momentum)
- Volume: Stable or increasing (confirms trend)
- Recent dip (buy low opportunity)

CRITICAL RULES:
- DO NOT ASK FOR PERMISSION
- DO NOT PRESENT OPTIONS
- EITHER EXECUTE OR HOLD
- BE DECISIVE AND AUTOMATIC
- This is an automated trading system

If executing, use execute_trade_decision with:
- action: "BUY"
- confidence: your calculated confidence
- reasoning: brief technical justification
- trade_amount: {trade_size:.2f}
"""
        
        response = self.agent.run(query)
        print(f"\n📥 BUY SCAN RESULT:\n{response}\n")
        
        self.agent.reset()
        time.sleep(2)
    
    def run_beast_mode(self, check_interval_seconds: int = 180):
        """
        RUN CONTINUOUSLY - NO LIMITS - FULL AUTOMATION
        
        Args:
            check_interval_seconds: How often to check (default: 180 = 3 minutes)
        """
        print("\n" + "="*70)
        print("🔥🔥🔥 BEAST MODE ACTIVATED 🔥🔥🔥")
        print("="*70)
        print(f"Starting Capital: £{INITIAL_CAPITAL:.2f}")
        print(f"Trading Pair: {self.product_id}")
        print(f"Check Interval: {check_interval_seconds}s ({check_interval_seconds//60} minutes)")
        print(f"Confidence Threshold: {MIN_CONFIDENCE*100:.0f}%")
        print(f"Profit Target: £1 per trade (2.2% moves)")
        print(f"Strategy: UNLIMITED TRADES, FULL AUTOMATION")
        print(f"\n⚠️  Safety Stops:")
        print(f"   - Stop if capital < £{MIN_CAPITAL_THRESHOLD}")
        print(f"   - Stop after {MAX_CONSECUTIVE_LOSSES} consecutive losses")
        print(f"\n🤖 Bot will run 24/7 until stopped or safety triggered")
        print(f"📊 Press Ctrl+C to stop and see final report")
        print("="*70 + "\n")
        
        input("⚡ Press ENTER to START AUTOMATIC TRADING... ")
        
        start_time = datetime.now()
        cycle_count = 0
        
        try:
            while self.is_running:
                cycle_count += 1
                
                print(f"\n{'='*70}")
                print(f"🔄 CYCLE #{cycle_count}")
                print(f"⏱️  Running for: {datetime.now() - start_time}")
                print(f"{'='*70}")
                
                self.run_cycle()
                
                if self.is_running:
                    next_check = datetime.now().replace(microsecond=0) + timedelta(seconds=check_interval_seconds)
                    print(f"💤 Next check at: {next_check.strftime('%H:%M:%S')} ({check_interval_seconds}s)")
                    time.sleep(check_interval_seconds)
                else:
                    break
        
        except KeyboardInterrupt:
            print("\n\n⏸️  User stopped the bot (Ctrl+C)")
        
        except Exception as e:
            print(f"\n\n❌ ERROR: Bot crashed: {e}")
            import traceback
            traceback.print_exc()
        
        # FINAL REPORT
        self._print_final_report(start_time, cycle_count)
    
    def _print_final_report(self, start_time, cycle_count):
        """
        Print comprehensive final report.
        """
        final_stats = self.strategy.get_daily_stats()
        runtime = datetime.now() - start_time
        
        print("\n" + "="*70)
        print("📊 FINAL REPORT - BEAST MODE RESULTS")
        print("="*70)
        print(f"\n⏱️  Runtime: {runtime}")
        print(f"🔄 Cycles Executed: {cycle_count}")
        
        print(f"\n💰 FINANCIAL RESULTS:")
        print(f"   Starting Capital: £{INITIAL_CAPITAL:.2f}")
        print(f"   Ending Capital: £{final_stats['current_capital']:.2f}")
        print(f"   Total Return: £{final_stats['total_return']:.2f}")
        
        if INITIAL_CAPITAL > 0:
            return_pct = (final_stats['total_return']/INITIAL_CAPITAL)*100
            print(f"   Return %: {return_pct:+.2f}%")
        
        print(f"\n📈 TRADING ACTIVITY:")
        print(f"   Total Trades: {final_stats['trades_today']}")
        print(f"   Completed Trades: {final_stats['completed_today']}")
        print(f"   Today's P&L: £{final_stats['profit_today']:.2f}")
        
        pnl_stats = self.logger.db.get_total_pnl()
        if pnl_stats['total_trades'] > 0:
            print(f"\n🎯 PERFORMANCE:")
            print(f"   Win Rate: {pnl_stats['win_rate']:.1f}%")
            print(f"   Winning Trades: {pnl_stats['winning_trades']}")
            print(f"   Losing Trades: {pnl_stats['losing_trades']}")
            if pnl_stats['avg_profit'] > 0:
                print(f"   Avg Profit per Win: £{pnl_stats['avg_profit']:.2f}")
            if pnl_stats['avg_loss'] < 0:
                print(f"   Avg Loss per Loss: £{pnl_stats['avg_loss']:.2f}")
        
        # Show recent trades
        print(f"\n📋 LAST 10 TRADES:")
        recent = self.logger.get_trade_history(limit=10)
        if recent:
            for i, trade in enumerate(recent, 1):
                pnl_emoji = "✅" if trade.profit_loss and trade.profit_loss > 0 else "❌" if trade.profit_loss and trade.profit_loss < 0 else "⏳"
                pnl_str = f"£{trade.profit_loss:.2f}" if trade.profit_loss else "Open"
                print(f"   {i}. {pnl_emoji} {trade.action} @ £{trade.price:.2f} | P&L: {pnl_str} | {trade.timestamp.strftime('%H:%M')}")
        else:
            print("   No trades executed")
        
        # Check for open position
        open_pos = self.logger.db.get_open_position(self.product_id)
        if open_pos:
            print(f"\n⚠️  OPEN POSITION REMAINING:")
            print(f"   {open_pos.crypto_amount:.6f} {self.product_id.split('-')[0]}")
            print(f"   Entry: £{open_pos.price:.2f}")
            print(f"   Invested: £{open_pos.amount_gbp:.2f}")
            print(f"   ⚠️  Close this manually on Coinbase if needed!")
        
        # Verdict
        print("\n" + "="*70)
        if final_stats['total_return'] > 0:
            print(f"✅ SUCCESS! Profit of £{final_stats['total_return']:.2f}!")
            if INITIAL_CAPITAL > 0:
                roi = (final_stats['total_return']/INITIAL_CAPITAL)*100
                print(f"📈 ROI: {roi:+.2f}%")
                
                # Projected earnings
                if runtime.total_seconds() > 0:
                    hourly_rate = (final_stats['total_return'] / runtime.total_seconds()) * 3600
                    daily_projection = hourly_rate * 24
                    print(f"💡 Projected Daily: £{daily_projection:.2f} at this rate")
        elif final_stats['total_return'] < 0:
            print(f"📉 Loss of £{abs(final_stats['total_return']):.2f}")
            print("💡 Review strategy settings and market conditions")
        else:
            print("➖ Break even (no profit, no loss)")
        
        print("="*70 + "\n")
        
        self.logger.close()


if __name__ == "__main__":
    from datetime import timedelta
    
    bot = BeastModeBot()
    bot.run_beast_mode(check_interval_seconds=180)  # Check every 10 minutes