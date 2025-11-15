"""
ML-ENHANCED AUTOMATED TRADING BOT
==================================

This bot integrates:
- Machine learning predictions for entry decisions
- Gradient Boosting classifier with 30-feature analysis
- Anomaly detection for crash recovery opportunities
- Adaptive threshold learning from past performance
- Trailing stop profit capture strategy
- Progressive profit targets that scale with capital

NEW: The ML system learns from every trade and improves over time!
"""

from agent import TradingAgent
from profit_strategy_enhanced import ProfitStrategyEnhanced
from data_layer.market_data import MarketData
from tracking.trade_logger import TradeLogger
from execution.trade_executor import TradeExecutor
from config import (
    TRADING_PAIR,
    MAX_DAILY_TRADES,
    MIN_CONFIDENCE,
    COOLDOWN_MINUTES,
    MAX_CONSECUTIVE_LOSSES,
    MIN_CAPITAL_THRESHOLD
)
from datetime import datetime, timedelta
import time
import traceback


class MLTradingBot:
    """
    ML-Enhanced Automated Trading Bot

    Features:
    - ML-driven entry decisions (learns from outcomes)
    - Adaptive threshold adjustment
    - Anomaly detection for opportunities
    - Trailing stop profit capture
    - Progressive profit targets
    - Safety limits and risk management
    """

    def __init__(self):
        print("\n" + "="*70)
        print("🚀 INITIALIZING ML-ENHANCED TRADING BOT")
        print("="*70)

        # Core components
        self.agent = TradingAgent()  # Has ML system built-in
        self.strategy = ProfitStrategyEnhanced()
        self.market = MarketData()
        self.logger = TradeLogger()
        self.executor = TradeExecutor()
        self.product_id = TRADING_PAIR

        # Trading state
        self.consecutive_losses = 0
        self.last_trade_time = None

        # ML performance tracking
        self.session_ml_stats = {
            'total_trades': 0,
            'ml_triggered': 0,
            'anomaly_detected': 0,
            'threshold_adjustments': 0
        }

        print("✅ ML-Enhanced Trading Bot Ready!")
        print("="*70 + "\n")

    def run_trading_cycle(self):
        """
        Run one complete ML-enhanced trading cycle.

        Flow:
        1. Check safety limits (daily trades, capital, losses)
        2. If position open → check ML-enhanced exit
        3. If no position → check ML-enhanced entry
        4. Update ML system with outcomes
        """
        try:
            print("\n" + "="*70)
            print(f"🤖 ML TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)

            # ==================== SAFETY CHECKS ====================
            if not self._check_safety_limits():
                return False  # Stop trading for safety

            # ==================== COOLDOWN CHECK ====================
            if not self._check_cooldown():
                return True  # Continue but skip this cycle

            # ==================== POSITION MANAGEMENT ====================
            exit_check = self.strategy.check_exit_conditions(self.product_id)

            if exit_check['has_position']:
                self._handle_position_exit(exit_check)
            else:
                self._handle_entry_opportunity()

            # Reset agent conversation for next cycle
            self.agent.reset()

            print("="*70)
            print("✅ Cycle Complete")
            print("="*70 + "\n")

            return True  # Continue trading

        except Exception as e:
            print(f"\n❌ ERROR in trading cycle: {e}")
            print(traceback.format_exc())
            return True  # Continue despite error

    def _check_safety_limits(self) -> bool:
        """
        Check all safety limits before trading.

        Returns:
            bool: True if safe to continue, False if limits hit
        """
        # Get daily stats
        daily_stats = self.strategy.get_daily_stats()
        current_capital = daily_stats['current_capital']

        print(f"\n📊 Today's Performance:")
        print(f"   Trades: {daily_stats['trades_today']}/{MAX_DAILY_TRADES}")
        print(f"   Completed: {daily_stats['completed_today']}")
        print(f"   Profit Today: £{daily_stats['profit_today']:.2f}")
        print(f"   Current Capital: £{current_capital:.2f}")
        print(f"   Total Return: £{daily_stats['total_return']:.2f}")

        # Get ML performance
        ml_stats = self.agent.get_ml_performance()
        if ml_stats['total_trades'] > 0:
            print(f"\n🧠 ML Performance:")
            print(f"   Total ML Trades: {ml_stats['total_trades']}")
            print(f"   Win Rate: {ml_stats['win_rate']:.1%}")
            print(f"   Adaptive Threshold: {ml_stats['adaptive_threshold']:.0f}")
            print(f"   Model Trained: {'✅ Yes' if ml_stats['model_trained'] else '⏳ Learning...'}")

        # Check 1: Daily trade limit
        if daily_stats['trades_today'] >= MAX_DAILY_TRADES:
            print(f"\n⛔ SAFETY LIMIT: Daily trade limit reached ({MAX_DAILY_TRADES})")
            print("   Stopping for today. Resume tomorrow.")
            return False

        # Check 2: Capital threshold
        if current_capital < MIN_CAPITAL_THRESHOLD:
            print(f"\n⛔ SAFETY LIMIT: Capital below minimum (£{current_capital:.2f} < £{MIN_CAPITAL_THRESHOLD})")
            print("   Stopping to preserve capital.")
            return False

        # Check 3: Consecutive losses
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
            print(f"\n⛔ SAFETY LIMIT: {self.consecutive_losses} consecutive losses")
            print("   Taking a break. Check market conditions.")
            return False

        print(f"✅ All safety checks passed")
        return True

    def _check_cooldown(self) -> bool:
        """
        Check if enough time has passed since last trade.

        Returns:
            bool: True if cooldown expired, False if still cooling
        """
        if self.last_trade_time is None:
            return True

        time_since_last = datetime.now() - self.last_trade_time
        cooldown_period = timedelta(minutes=COOLDOWN_MINUTES)

        if time_since_last < cooldown_period:
            remaining = (cooldown_period - time_since_last).total_seconds() / 60
            print(f"\n⏸️  Cooldown: {remaining:.1f} minutes remaining")
            return False

        return True

    def _handle_position_exit(self, exit_check: dict):
        """
        Handle exit decision for open position.

        The ML system has already learned from entry. Now we just execute
        the profit strategy (trailing stop + target).
        """
        print(f"\n💼 Open Position Detected")
        print(f"   Entry: £{exit_check['entry_price']:.2f}")
        print(f"   Current: £{exit_check['current_price']:.2f}")
        print(f"   P&L: £{exit_check['expected_profit']:+.2f}")
        print(f"   Status: {exit_check['reason']}")

        if exit_check['should_exit']:
            print(f"\n🎯 {exit_check['action']} SIGNAL!")

            # Use ML-enhanced sell decision
            sell_decision = self.agent.run_auto_sell_with_ml(exit_check)

            if sell_decision['executed']:
                profit = sell_decision.get('profit', 0)

                # Update consecutive loss counter
                if profit > 0:
                    self.consecutive_losses = 0
                    print(f"   ✅ WIN! Consecutive losses reset.")
                else:
                    self.consecutive_losses += 1
                    print(f"   ❌ LOSS. Consecutive losses: {self.consecutive_losses}")

                # Update session stats
                self.session_ml_stats['total_trades'] += 1
                self.last_trade_time = datetime.now()

                print(f"\n📝 {sell_decision['reasoning']}")
            else:
                print(f"\n⏸️  {sell_decision['reasoning']}")
        else:
            print(f"\n⏳ Holding position... waiting for target or stop loss")

    def _handle_entry_opportunity(self):
        """
        Handle ML-enhanced entry decision.

        Uses:
        - 30 technical features
        - Gradient Boosting predictions
        - Anomaly detection
        - Adaptive threshold
        """
        print(f"\n🔍 No open position. Running ML analysis...")

        # Get market snapshot
        try:
            snapshot = self.market.get_full_market_snapshot(self.product_id)
        except Exception as e:
            print(f"   ❌ Error getting market data: {e}")
            return

        # Calculate trade size
        trade_size = self.strategy.calculate_trade_size()
        print(f"   💰 Available capital: £{trade_size:.2f}")

        # Get ML-enhanced buy decision
        try:
            buy_decision = self.agent.run_auto_buy_with_ml(snapshot)

            # Track ML usage
            if buy_decision.get('anomaly_type'):
                self.session_ml_stats['anomaly_detected'] += 1

            if buy_decision.get('adaptive_threshold', 70) != 70:
                self.session_ml_stats['threshold_adjustments'] += 1

            if buy_decision['executed']:
                self.session_ml_stats['ml_triggered'] += 1
                self.last_trade_time = datetime.now()

                print(f"\n✅ ML TRIGGERED BUY!")
                print(f"   ML Score: {buy_decision['ml_score']}/100")
                print(f"   Base Score: {buy_decision['base_score']}/100")
                print(f"   Confidence: {buy_decision['confidence']:.2%}")

                if buy_decision.get('anomaly_type'):
                    print(f"   🚨 Anomaly: {buy_decision['anomaly_type']}")

                print(f"\n📝 {buy_decision['reasoning']}")
                print(f"\n🧠 ML Insights: {buy_decision.get('ml_reasoning', 'N/A')}")
            else:
                print(f"\n⏸️  ML recommends HOLD")
                print(f"   ML Score: {buy_decision['ml_score']}/100")
                print(f"   Confidence: {buy_decision['confidence']:.2%}")
                print(f"\n📝 {buy_decision['reasoning']}")

        except Exception as e:
            print(f"   ❌ Error in ML analysis: {e}")
            print(traceback.format_exc())

    def run_continuous(self, interval_minutes: int = COOLDOWN_MINUTES):
        """
        Run bot continuously with scheduled cycles.

        Args:
            interval_minutes: Minutes between cycles (default from config)
        """
        from apscheduler.schedulers.blocking import BlockingScheduler

        scheduler = BlockingScheduler()
        scheduler.add_job(
            self.run_trading_cycle,
            'interval',
            minutes=interval_minutes,
            max_instances=1  # Prevent overlapping runs
        )

        print("\n" + "="*70)
        print("🚀 ML-ENHANCED AUTOMATED TRADING BOT STARTED")
        print("="*70)
        print(f"Trading Pair: {self.product_id}")
        print(f"Cycle Interval: Every {interval_minutes} minutes")
        print(f"Min Confidence: {MIN_CONFIDENCE:.0%}")
        print(f"Max Daily Trades: {MAX_DAILY_TRADES}")
        print(f"Max Consecutive Losses: {MAX_CONSECUTIVE_LOSSES}")
        print(f"\n🧠 ML Features:")
        print(f"   - Gradient Boosting Classifier (30 features)")
        print(f"   - Anomaly Detection (crash recovery)")
        print(f"   - Adaptive Threshold Learning")
        print(f"   - Continuous improvement from outcomes")
        print(f"\nPress Ctrl+C to stop")
        print("="*70 + "\n")

        # Run first cycle immediately
        should_continue = self.run_trading_cycle()

        if not should_continue:
            print("\n⛔ Bot stopped due to safety limits")
            return

        # Then schedule recurring
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n\n👋 Shutting down ML trading bot...")
            self._print_session_summary()

    def _print_session_summary(self):
        """
        Print summary of ML performance for this session.
        """
        print("\n" + "="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)

        # Get final ML stats
        ml_stats = self.agent.get_ml_performance()

        print(f"\n🧠 ML System Performance:")
        print(f"   Total Trades: {ml_stats.get('total_trades', 0)}")
        if ml_stats.get('total_trades', 0) > 0:
            print(f"   Wins: {ml_stats.get('wins', 0)} | Losses: {ml_stats.get('losses', 0)}")
            print(f"   Win Rate: {ml_stats.get('win_rate', 0):.1%}")
            print(f"   Total Profit: £{ml_stats.get('total_profit', 0):.2f}")
            print(f"   Best Trade: £{ml_stats.get('best_trade', 0):.2f}")
            print(f"   Worst Trade: £{ml_stats.get('worst_trade', 0):.2f}")

        print(f"\n📈 Session Stats:")
        print(f"   ML-Triggered Entries: {self.session_ml_stats['ml_triggered']}")
        print(f"   Anomalies Detected: {self.session_ml_stats['anomaly_detected']}")
        print(f"   Threshold Adjustments: {self.session_ml_stats['threshold_adjustments']}")

        print(f"\n   Model Status: {'✅ Trained' if ml_stats.get('model_trained') else '⏳ Learning'}")
        print(f"   Adaptive Threshold: {ml_stats.get('adaptive_threshold', 70):.0f}")

        print("\n" + "="*70 + "\n")


def main():
    """
    Main entry point for ML-enhanced trading bot.
    """
    bot = MLTradingBot()

    # Run with configured cooldown interval
    bot.run_continuous(interval_minutes=COOLDOWN_MINUTES)


if __name__ == "__main__":
    main()
