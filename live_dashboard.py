from tracking.trade_logger import TradeLogger
from profit_strategy_enhanced import ProfitStrategyEnhanced
from data_layer.market_data import MarketData
from enhanced_entry_system import EnhancedEntrySystem
from datetime import datetime
from config import TRADING_PAIR, MIN_CONFIDENCE
import time
import os

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_dashboard():
    """
    CLEAN LIVE DASHBOARD with Enhanced Entry Scoring
    Shows 100-point scoring system + essential data only
    Updates every 30 seconds
    """
    logger = TradeLogger("trading_bot.db")
    strategy = ProfitStrategyEnhanced("trading_bot.db")
    market = MarketData()
    scorer = EnhancedEntrySystem()
    
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
        # ENHANCED ENTRY SCORING (NEW!)
        # ================================================================
        print(f"\n🎯 ENTRY SCORE (Enhanced Multi-Factor Analysis)")
        print("-" * 80)
        
        analysis = scorer.analyze_entry_opportunity(snapshot, TRADING_PAIR)
        
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
        print(f"   [{bar}] 70% threshold")
        
        # Factor breakdown (compact)
        breakdown = analysis['breakdown']
        
        # Show only scores, not details
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
    # LIVE POSITION
    # ================================================================
    print(f"\n💼 POSITION")
    print("-" * 80)
    
    exit_check = strategy.check_exit_conditions(TRADING_PAIR)
    
    if exit_check['has_position']:
        current_price = exit_check['current_price']
        entry_price = exit_check['entry_price']
        current_pnl = exit_check['expected_profit']
        
        crypto_symbol = TRADING_PAIR.split('-')[0]
        crypto_amount = exit_check.get('crypto_amount', 0)
        
        # Position info
        price_change = ((current_price - entry_price) / entry_price) * 100
        direction = "🟢" if price_change >= 0 else "🔴"
        
        print(f"   OPEN: {crypto_amount:.6f} {crypto_symbol}")
        print(f"   Entry: £{entry_price:.2f} → Now: £{current_price:.2f} {direction} {price_change:+.1f}%")
        print(f"   P&L: £{current_pnl:+.2f}")
        
        # Trailing stop status
        if exit_check.get('trailing_active'):
            peak = exit_check.get('peak_price', 0)
            stop = exit_check.get('trailing_stop_price', 0)
            buffer = current_price - stop
            
            print(f"\n   🎯 TRAILING STOP ACTIVE")
            print(f"   Peak: £{peak:.2f} | Stop: £{stop:.2f} | Buffer: £{buffer:.2f}")
        
        # Exit signal
        if exit_check['should_exit']:
            print(f"\n   ⚡ EXIT SIGNAL: {exit_check['reason']}")
        else:
            print(f"\n   📊 {exit_check['reason']}")
            
    else:
        print(f"   No position - Scanning...")
        
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
                
                # Bonus markers
                current_target = daily.get('current_profit_target', 2.0)
                if trade.profit_loss > (current_target * 2):
                    pnl_str += " 💎💎"
                elif trade.profit_loss > (current_target * 1.5):
                    pnl_str += " 💎"
            else:
                pnl_str = "⏳ Open"
            
            print(f"   {i}. {time_str} {trade.action} @ £{trade.price:.2f} | {pnl_str}")
    else:
        print(f"   No trades yet")
    
    # ================================================================
    # FOOTER
    # ================================================================
    print("\n" + "="*80)
    print("🔄 Refresh: 30s | Ctrl+C to exit | Enhanced Multi-Factor Scoring Active")
    print("="*80)
    
    logger.close()

def run_live_dashboard():
    """Run the clean live dashboard with enhanced scoring."""
    print("\n🚀 Starting Enhanced Live Dashboard...")
    print("\n✨ NEW: 100-Point Multi-Factor Scoring System")
    print("   - Multi-timeframe trend analysis")
    print("   - Support/resistance detection")
    print("   - Market regime adaptation")
    print("   - Volume confirmation")
    print("   - Momentum scoring")
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