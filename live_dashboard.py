from tracking.trade_logger import TradeLogger
from profit_strategy_enhanced import ProfitStrategyEnhanced  # UPDATED!
from data_layer.market_data import MarketData
from datetime import datetime
from config import TRADING_PAIR, PROFIT_TARGET_GBP, MIN_CONFIDENCE
import time
import os

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_dashboard():
    """
    ENHANCED LIVE DASHBOARD - Shows trailing stop status
    Auto-refreshing P&L monitor with trailing stop indicators
    Updates every 30 seconds with real-time data
    Press Ctrl+C to exit
    """
    logger = TradeLogger("trading_bot.db")
    strategy = ProfitStrategyEnhanced("trading_bot.db")  # UPDATED!
    market = MarketData()
    
    clear_screen()
    
    print("="*70)
    print(f"📊 LIVE TRADING DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Get daily stats
    daily = strategy.get_daily_stats()
    
    print(f"\n💰 CAPITAL:")
    print(f"   Start: £{daily['initial_capital']:.2f} → Current: £{daily['current_capital']:.2f}")
    return_amount = daily['total_return']
    return_pct = (return_amount / daily['initial_capital']) * 100 if daily['initial_capital'] > 0 else 0
    return_emoji = "📈" if return_amount >= 0 else "📉"
    print(f"   Return: {return_emoji} £{return_amount:.2f} ({return_pct:+.2f}%)")
    
    # Performance metrics
    pnl_data = logger.db.get_total_pnl()
    if pnl_data['total_trades'] > 0:
        print(f"\n🎯 PERFORMANCE:")
        print(f"   Trades: {pnl_data['total_trades']} | Wins: {pnl_data['winning_trades']} | Losses: {pnl_data['losing_trades']} | Win Rate: {pnl_data['win_rate']:.1f}%")
        print(f"   Total P&L: £{pnl_data['total_pnl']:.2f}")
        
        # Show average profit (NEW!)
        if pnl_data['winning_trades'] > 0:
            avg_profit = pnl_data['avg_profit']
            if avg_profit > PROFIT_TARGET_GBP:
                extra_avg = avg_profit - PROFIT_TARGET_GBP
                print(f"   Avg Win: £{avg_profit:.2f} (£{extra_avg:.2f} extra via trailing stop! 💎)")
            else:
                print(f"   Avg Win: £{avg_profit:.2f}")
    
    # LIVE POSITION STATUS
    print(f"\n💼 LIVE POSITION:")
    print("-" * 70)
    
    exit_check = strategy.check_exit_conditions(TRADING_PAIR)
    
    if exit_check['has_position']:
        current_price = exit_check['current_price']
        entry_price = exit_check['entry_price']
        current_pnl = exit_check['expected_profit']
        
        crypto_symbol = TRADING_PAIR.split('-')[0]
        crypto_amount = exit_check.get('crypto_amount', 0)
        
        # Price info
        price_diff = current_price - entry_price
        price_diff_pct = (price_diff / entry_price) * 100 if entry_price > 0 else 0
        direction = "🟢 UP" if price_diff >= 0 else "🔴 DOWN"
        
        print(f"   {crypto_amount:.6f} {crypto_symbol}")
        print(f"   Entry: £{entry_price:.2f} → Now: £{current_price:.2f} ({direction} {price_diff_pct:+.2f}%)")
        
        # P&L bar
        pnl_emoji = "💚" if current_pnl >= 0 else "💔"
        print(f"   P&L: {pnl_emoji} £{current_pnl:+.2f}")
        
        # ================================================================
        # NEW: TRAILING STOP STATUS
        # ================================================================
        if exit_check.get('trailing_active'):
            print(f"\n   🎯 TRAILING STOP ACTIVE!")
            peak_price = exit_check.get('peak_price', 0)
            trailing_stop_price = exit_check.get('trailing_stop_price', 0)
            
            extra_profit = current_pnl - PROFIT_TARGET_GBP
            
            print(f"   ├─ Peak Price: £{peak_price:.2f}")
            print(f"   ├─ Trailing Stop: £{trailing_stop_price:.2f}")
            print(f"   ├─ Current Buffer: £{current_price - trailing_stop_price:.2f}")
            print(f"   └─ Extra Profit: £{extra_profit:.2f} above £{PROFIT_TARGET_GBP:.2f} minimum 💎")
            
            # Visual indicator
            distance_from_stop = ((current_price - trailing_stop_price) / current_price) * 100
            trail_distance_pct = strategy.trailing_stop_distance_pct * 100
            
            if distance_from_stop < trail_distance_pct * 0.3:  # Within 30% of trigger
                print(f"\n   ⚠️  CLOSE TO STOP! Only {distance_from_stop:.2f}% buffer")
            else:
                print(f"\n   ✅ Safe buffer: {distance_from_stop:.2f}% from stop")
            
            print(f"   📈 Strategy: Riding the trend, will exit if price drops {trail_distance_pct:.1f}% from peak")
        
        # ================================================================
        # Progress to target (if not yet hit)
        # ================================================================
        elif 'target_price' in exit_check:
            target_price = exit_check['target_price']
            target_distance = target_price - current_price
            target_pct = (target_distance / current_price) * 100
            
            # Calculate progress bar
            total_distance = target_price - entry_price
            progress = ((current_price - entry_price) / total_distance) if total_distance > 0 else 0
            progress = max(0, min(1, progress))  # Clamp between 0-1
            
            bar_length = 40
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\n   Progress to Target:")
            print(f"   [{bar}] {progress*100:.1f}%")
            print(f"   Need: +£{target_distance:.2f} ({target_pct:+.2f}%) to reach £{target_price:.2f}")
            
            if target_pct > 0:
                print(f"   Target: £{PROFIT_TARGET_GBP:.2f} profit (then trailing activates!)")
            else:
                print(f"   ✅ TARGET HIT! Trailing stop will activate next cycle!")
        
        # Stop loss warning
        if 'stop_loss_price' in exit_check:
            stop_loss_price = exit_check['stop_loss_price']
            stop_distance = current_price - stop_loss_price
            
            if stop_distance < 0:
                print(f"\n   🚨 STOP LOSS TRIGGERED: £{stop_loss_price:.2f}")
            else:
                stop_pct = (stop_distance / current_price) * 100
                if stop_pct < 0.5:  # Less than 0.5% buffer
                    print(f"   ⚠️  NEAR STOP LOSS: £{stop_loss_price:.2f} (buffer: {stop_pct:.1f}%)")
                else:
                    print(f"   🛡️  Stop Loss: £{stop_loss_price:.2f} (buffer: {stop_pct:.1f}%)")
        
        # Status
        status = exit_check['reason']
        if exit_check['should_exit']:
            # Check if it's a trailing stop exit
            if 'TRAILING STOP' in status:
                print(f"\n   🎯 TRAILING STOP EXIT: {status}")
            else:
                print(f"\n   🔔 EXIT SIGNAL: {status}")
            print(f"   ⚡ BOT WILL SELL ON NEXT CYCLE!")
        else:
            print(f"\n   📊 Status: {status}")
            
    else:
        print(f"   No open position")
        
        # Show scanning status
        snapshot = market.get_full_market_snapshot(TRADING_PAIR)
        if snapshot:
            current_price = snapshot['current_price']
            rsi = snapshot['indicators'].get('rsi', 0)
            signal = snapshot['signal'].get('signal', 'N/A')
            strength = snapshot['signal'].get('strength', 0)
            
            print(f"\n   Current {TRADING_PAIR}: £{current_price:.2f}")
            print(f"   RSI: {rsi:.1f} | Signal: {signal} (confidence: {strength*100:.0f}%)")
            
            if strength >= MIN_CONFIDENCE:
                print(f"   ✅ Confidence above {MIN_CONFIDENCE*100:.0f}% - Bot should enter soon!")
            else:
                need_pct = (MIN_CONFIDENCE - strength) * 100
                print(f"   ⏳ Scanning... Need +{need_pct:.0f}% more confidence")
            
            # NEW: Show trailing stop info
            trail_pct = strategy.trailing_stop_distance_pct * 100
            print(f"\n   💎 Trailing Stop Ready:")
            print(f"      Distance: {trail_pct:.1f}% below peak")
            print(f"      Min Profit: £{PROFIT_TARGET_GBP:.2f} (then captures more!)")
    
    # Recent trades (compact) - Enhanced to show trailing stop wins
    print(f"\n📋 RECENT TRADES:")
    print("-" * 70)
    trades = logger.get_trade_history(limit=5)
    
    if trades:
        for trade in trades:
            time_str = trade.timestamp.strftime('%H:%M:%S')
            if trade.profit_loss is not None:
                pnl_emoji = "✅" if trade.profit_loss >= 0 else "❌"
                
                # Mark extra profit from trailing stop
                bonus_marker = ""
                if trade.profit_loss > (PROFIT_TARGET_GBP * 1.2):  # 20% above target
                    bonus_marker = " 💎"  # Diamond for big wins
                
                pnl_str = f"{pnl_emoji} £{trade.profit_loss:+.2f}{bonus_marker}"
            else:
                pnl_str = "⏳ Open"
            
            print(f"   {time_str} | {trade.action:<4} @ £{trade.price:.2f} | {pnl_str}")
    else:
        print(f"   No trades yet")
    
    print("\n" + "="*70)
    print("🔄 Refreshing every 30s... Press Ctrl+C to exit")
    print("💡 Look for 🎯 when trailing stop is active!")
    print("="*70)
    
    logger.close()

def run_live_dashboard():
    """Run the enhanced live dashboard with auto-refresh."""
    print("\n🚀 Starting Enhanced Live Dashboard...")
    print("📊 Updates every 30 seconds")
    print("🎯 Shows trailing stop status when active")
    print("⌨️  Press Ctrl+C to exit\n")
    time.sleep(2)
    
    try:
        while True:
            display_dashboard()
            time.sleep(30)  # Refresh every 30 seconds
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n👋 Dashboard closed. Bot continues running in background.")
        print("💡 Run 'python live_dashboard.py' to reopen anytime\n")

if __name__ == "__main__":
    run_live_dashboard()