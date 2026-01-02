from tracking.trade_logger import TradeLogger
from profit_strategy_enhanced import ProfitStrategyEnhanced
from data_layer.market_data import MarketData
from entry_analyzer import EnhancedEntrySystem
from enhanced_entry_system import MLEnhancedEntrySystem
from datetime import datetime
from config import TRADING_PAIR, MIN_CONFIDENCE, PROFIT_TARGET_GBP, STOP_LOSS_PCT
import time
import os

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_dashboard():
    """
    CLEAN LIVE DASHBOARD with Enhanced Entry Scoring + Dual Target Tracking
    Shows 100-point scoring + profit target + stop loss tracking
    Updates every 30 seconds
    """
    logger = TradeLogger("trading_bot.db")
    strategy = ProfitStrategyEnhanced("trading_bot.db")
    market = MarketData()
    scorer = MLEnhancedEntrySystem(EnhancedEntrySystem())
    
    clear_screen()
    
    print("="*80)
    print(f"📊 ENHANCED TRADING DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    # ================================================================
    # MARKET DATA
    # ================================================================
    snapshot = market.get_full_market_snapshot(TRADING_PAIR)
    
    if snapshot:
        current_price = snapshot['current_price']
        indicators = snapshot.get('indicators', {})
        
        print(f"\n💹 {TRADING_PAIR}")
        print(f"   Price: £{current_price:.2f}")
        print(f"   RSI: {indicators.get('rsi', 0):.0f} | Volume: {indicators.get('volume_ratio', 0):.1f}x | "
              f"EMA: {indicators.get('ema_cross', 'neutral')} | MACD: {indicators.get('macd_cross', 'neutral')}")
        
        # ================================================================
        # ENHANCED ENTRY SCORING
        # ================================================================
        print(f"\n🎯 ENTRY SCORE (Enhanced Multi-Factor Analysis)")
        print("-" * 80)
        
        analysis = scorer.analyze_entry_with_ml(snapshot, TRADING_PAIR)
        
        score = analysis['score']
        quality = analysis['quality']
        
        # Score bar
        bar_length = 50
        filled = int((score / 100) * bar_length)
        threshold = int((70 / 100) * bar_length)
        
        bar = ""
        for i in range(bar_length):
            if i < filled:
                bar += "█"
            elif i == threshold:
                bar += "│"
            else:
                bar += "░"
        
        # Quality emoji
        if quality == "EXCELLENT":
            emoji = "🌟"
        elif quality == "GOOD":
            emoji = "✅"
        elif quality == "FAIR":
            emoji = "⚠️"
        else:
            emoji = "❌"
        
        print(f"   {emoji} Score: {score}/100 ({quality})")
        print(f"   [{bar}] 75% threshold")
        
        # Factor breakdown (compact)
        breakdown = analysis['breakdown']
        
        print(f"\n   Factors:")
        for factor, data in breakdown.items():
            score_val = data['score']
            max_val = data['max']
            pct = int((score_val / max_val) * 100) if max_val > 0 else 0
            
            # Visual indicator
            if pct >= 80:
                icon = "✅"
            elif pct >= 50:
                icon = "⚠️"
            else:
                icon = "❌"
            
            # Compact bar (10 chars)
            mini_bar_len = 10
            mini_filled = int((pct / 100) * mini_bar_len)
            mini_bar = "█" * mini_filled + "░" * (mini_bar_len - mini_filled)
            
            factor_name = factor.replace('_', ' ').title()[:20]
            print(f"   {icon} {factor_name:<20} [{mini_bar}] {score_val}/{max_val}")
        
        # Decision
        if analysis['should_enter']:
            print(f"\n   🚀 DECISION: STRONG ENTRY SIGNAL")
        else:
            print(f"\n   ⏸️  DECISION: SKIP (Score below 70)")
    
    # ================================================================
    # ACCOUNT STATUS
    # ================================================================
    daily = strategy.get_daily_stats()
    pnl_data = logger.db.get_total_pnl()
    
    print(f"\n💰 ACCOUNT")
    print("-" * 80)
    
    # Capital and return
    capital = daily['current_capital']
    return_amt = daily['total_return']
    return_pct = (return_amt / daily['initial_capital']) * 100 if daily['initial_capital'] > 0 else 0
    
    return_icon = "📈" if return_amt >= 0 else "📉"
    print(f"   Capital: £{capital:.2f} | Return: {return_icon} £{return_amt:+.2f} ({return_pct:+.1f}%)")
    
    # Performance stats
    if pnl_data['total_trades'] > 0:
        print(f"   Trades: {pnl_data['total_trades']} | "
              f"Win Rate: {pnl_data['win_rate']:.0f}% | "
              f"Wins: {pnl_data['winning_trades']} | "
              f"Losses: {pnl_data['losing_trades']}")
        
        if pnl_data['winning_trades'] > 0:
            print(f"   Avg Win: £{pnl_data['avg_profit']:.2f} | ", end="")
        if pnl_data['losing_trades'] > 0:
            print(f"Avg Loss: £{pnl_data['avg_loss']:.2f}")
        else:
            print()
    
    # ================================================================
    # LIVE POSITION WITH DUAL TARGET TRACKING
    # ================================================================
    print(f"\n💼 POSITION")
    print("-" * 80)
    
    exit_check = strategy.check_exit_conditions(TRADING_PAIR)
    
    if exit_check['has_position']:
        current_price = exit_check['current_price']
        entry_price = exit_check['entry_price']
        current_pnl = exit_check['expected_profit']
        stop_loss_price = exit_check.get('stop_loss_price', 0)
        
        crypto_symbol = TRADING_PAIR.split('-')[0]
        crypto_amount = exit_check.get('crypto_amount', 0)
        
        # Position info
        price_change = ((current_price - entry_price) / entry_price) * 100
        direction = "🟢" if price_change >= 0 else "🔴"
        
        print(f"   OPEN: {crypto_amount:.6f} {crypto_symbol}")
        print(f"   Entry: £{entry_price:.2f} → Now: £{current_price:.2f} {direction} {price_change:+.1f}%")
        print(f"   P&L: £{current_pnl:+.2f}")
        
        # ================================================================
        # PROFIT TARGET: £2.00 (UPSIDE)
        # ================================================================
        profit_target = PROFIT_TARGET_GBP  # £2.00
        
        print(f"\n   🎯 PROFIT TARGET: £{profit_target:.2f}")
        
        # Progress calculation
        if current_pnl >= profit_target:
            profit_progress = 100
            profit_icon = "✅"
            profit_msg = "TARGET HIT! Trailing stop active"
        elif current_pnl > 0:
            profit_progress = int((current_pnl / profit_target) * 100)
            profit_icon = "📈"
            remaining = profit_target - current_pnl
            profit_msg = f"£{remaining:.2f} to go"
        else:
            profit_progress = 0
            profit_icon = "📉"
            profit_msg = f"Below entry"
        
        # Progress bar (40 chars wide)
        bar_width = 40
        profit_filled = int((profit_progress / 100) * bar_width)
        
        # Color coding
        if profit_progress >= 100:
            profit_bar_char = "█"
            profit_empty = " "
            profit_color = "🟩"
        elif profit_progress >= 75:
            profit_bar_char = "█"
            profit_empty = "░"
            profit_color = "🟨"
        elif profit_progress >= 50:
            profit_bar_char = "█"
            profit_empty = "░"
            profit_color = "🟦"
        elif profit_progress > 0:
            profit_bar_char = "▓"
            profit_empty = "░"
            profit_color = "⬜"
        else:
            profit_bar_char = ""
            profit_empty = "░"
            profit_color = "⚪"
        
        profit_bar = profit_bar_char * profit_filled + profit_empty * (bar_width - profit_filled)
        
        print(f"   {profit_color} [{profit_bar}] {profit_progress}%")
        print(f"   {profit_icon} {profit_msg}")
        
        # Show target price
        target_price = exit_check.get('target_price', 0)
        if target_price > 0 and current_pnl < profit_target:
            price_to_target = target_price - current_price
            print(f"   💡 Need: £{target_price:.2f} (+£{price_to_target:.2f})")
        
        # ================================================================
        # STOP LOSS: (DOWNSIDE RISK)
        # ================================================================
        print(f"\n   🛑 STOP LOSS: £{stop_loss_price:.2f} ({STOP_LOSS_PCT*100:.1f}%)")
        
        # Distance to stop loss
        price_to_stop = current_price - stop_loss_price
        price_to_stop_pct = (price_to_stop / current_price) * 100
        
        # Calculate "safety buffer" (how far from stop loss)
        # If we're at entry price, buffer is 100%
        # If we're at stop loss, buffer is 0%
        max_buffer = entry_price - stop_loss_price
        current_buffer = current_price - stop_loss_price
        
        if max_buffer > 0:
            buffer_pct = int((current_buffer / max_buffer) * 100)
            buffer_pct = max(0, min(100, buffer_pct))  # Clamp 0-100
        else:
            buffer_pct = 100
        
        # Stop loss bar (inverted - full bar = safe, empty = danger)
        stop_filled = int((buffer_pct / 100) * bar_width)
        
        # Color coding (opposite of profit - green when far, red when close)
        if buffer_pct >= 80:
            stop_color = "🟩"
            stop_icon = "✅"
            stop_msg = "Safe"
            stop_bar_char = "█"
        elif buffer_pct >= 50:
            stop_color = "🟨"
            stop_icon = "⚠️"
            stop_msg = "Caution"
            stop_bar_char = "█"
        elif buffer_pct >= 20:
            stop_color = "🟧"
            stop_icon = "⚠️"
            stop_msg = "Warning!"
            stop_bar_char = "▓"
        elif buffer_pct > 0:
            stop_color = "🟥"
            stop_icon = "🚨"
            stop_msg = "DANGER!"
            stop_bar_char = "▓"
        else:
            stop_color = "🟥"
            stop_icon = "💥"
            stop_msg = "STOP HIT!"
            stop_bar_char = ""
        
        stop_empty = "░"
        stop_bar = stop_bar_char * stop_filled + stop_empty * (bar_width - stop_filled)
        
        print(f"   {stop_color} [{stop_bar}] {buffer_pct}% buffer")
        print(f"   {stop_icon} {stop_msg} | £{price_to_stop:.2f} away ({price_to_stop_pct:.1f}%)")
        
        # ================================================================
        # RISK/REWARD VISUALIZATION
        # ================================================================
        print(f"\n   ⚖️  RISK/REWARD")
        
        # Calculate potential loss if stop hit
        potential_loss = current_pnl if current_price <= stop_loss_price else (stop_loss_price - entry_price) * crypto_amount * (1 - 0.012)
        potential_gain = profit_target - current_pnl if current_pnl < profit_target else 0
        
        print(f"   Downside: £{potential_loss:.2f} | Upside: +£{potential_gain:.2f}")
        
        # ================================================================
        # Trailing stop status (shown AFTER target hit)
        # ================================================================
        if exit_check.get('trailing_active'):
            peak = exit_check.get('peak_price', 0)
            trailing_stop = exit_check.get('trailing_stop_price', 0)
            buffer = current_price - trailing_stop
            extra_profit = current_pnl - profit_target
            
            print(f"\n   🎯 TRAILING STOP ACTIVE (£{profit_target:.2f} secured!)")
            print(f"   Peak: £{peak:.2f} | Stop: £{trailing_stop:.2f} | Buffer: £{buffer:.2f}")
            print(f"   💎 Extra Profit: £{extra_profit:+.2f} above target")
        
        # Exit signal
        if exit_check['should_exit']:
            print(f"\n   ⚡ EXIT SIGNAL: {exit_check['reason']}")
        else:
            print(f"\n   📊 Status: {exit_check['reason']}")
            
    else:
        print(f"   No position - Scanning for entry...")
        print(f"   🎯 Profit Target: £{PROFIT_TARGET_GBP:.2f} NET")
        print(f"   🛑 Stop Loss: {STOP_LOSS_PCT*100:.1f}% below entry")
        
        if snapshot and analysis['should_enter']:
            print(f"   ✅ Entry conditions met! Bot should enter soon.")
        elif snapshot:
            need = 70 - score
            print(f"   ⏳ Need +{need} points to reach threshold")
    
    # ================================================================
    # RECENT TRADES (Compact)
    # ================================================================
    print(f"\n📋 RECENT TRADES (Last 5)")
    print("-" * 80)
    trades = logger.get_trade_history(limit=5)
    
    if trades:
        for i, trade in enumerate(trades, 1):
            time_str = trade.timestamp.strftime('%H:%M')
            
            if trade.profit_loss is not None:
                pnl_icon = "✅" if trade.profit_loss >= 0 else "❌"
                pnl_str = f"{pnl_icon} £{trade.profit_loss:+.2f}"
                
                # Bonus markers relative to £2 target
                if trade.profit_loss >= PROFIT_TARGET_GBP * 3:
                    pnl_str += " 💎💎💎"
                elif trade.profit_loss >= PROFIT_TARGET_GBP * 2:
                    pnl_str += " 💎💎"
                elif trade.profit_loss >= PROFIT_TARGET_GBP * 1.5:
                    pnl_str += " 💎"
                elif trade.profit_loss >= PROFIT_TARGET_GBP:
                    pnl_str += " ✨"  # Hit target
                
                # Stop loss marker
                if trade.profit_loss < 0 and abs(trade.profit_loss) >= 2.0:
                    pnl_str += " 🛑"  # Stop loss hit
            else:
                pnl_str = "⏳ Open"
            
            print(f"   {i}. {time_str} {trade.action} @ £{trade.price:.2f} | {pnl_str}")
    else:
        print(f"   No trades yet")
    
    # ================================================================
    # FOOTER
    # ================================================================
    print("\n" + "="*80)
    print(f"🔄 Refresh: 30s | 🎯 Target: £{PROFIT_TARGET_GBP:.2f} | 🛑 Stop: {STOP_LOSS_PCT*100:.1f}% | Ctrl+C")
    print("="*80)
    
    logger.close()

def run_live_dashboard():
    """Run the clean live dashboard with enhanced scoring + dual target tracking."""
    print("\n🚀 Starting Enhanced Live Dashboard...")
    print("\n✨ NEW FEATURES:")
    print("   - 100-Point Multi-Factor Scoring System")
    print("   - Multi-timeframe trend analysis")
    print("   - Support/resistance detection")
    print("   - Market regime adaptation")
    print(f"   - 🎯 Profit Target: £{PROFIT_TARGET_GBP:.2f} Progress Tracking")
    print(f"   - 🛑 Stop Loss: {STOP_LOSS_PCT*100:.1f}% Risk Monitoring")
    print("\n⌨️  Press Ctrl+C to exit\n")
    time.sleep(2)
    
    try:
        while True:
            display_dashboard()
            time.sleep(30)  # Refresh every 30 seconds
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n👋 Dashboard closed.\n")

if __name__ == "__main__":
    run_live_dashboard()