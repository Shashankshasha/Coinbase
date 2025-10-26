from tracking.trade_logger import TradeLogger
from profit_strategy import ProfitStrategy
from data_layer.market_data import MarketData
from datetime import datetime
from config import TRADING_PAIR, PROFIT_TARGET_GBP, MIN_CONFIDENCE

def check_pnl():
    """
    ENHANCED P&L Monitor - Check current P&L and position status.
    Shows real-time prices, targets, and P&L calculations.
    Run this anytime: python check_pnl.py
    """
    logger = TradeLogger("trading_bot.db")
    strategy = ProfitStrategy("trading_bot.db")
    market = MarketData()
    
    print("\n" + "="*70)
    print(f"📊 LIVE P&L MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Get daily stats
    daily = strategy.get_daily_stats()
    
    print(f"\n💰 CAPITAL STATUS:")
    print(f"   Starting: £{daily['initial_capital']:.2f}")
    print(f"   Current:  £{daily['current_capital']:.2f}")
    return_amount = daily['total_return']
    return_pct = (return_amount / daily['initial_capital']) * 100 if daily['initial_capital'] > 0 else 0
    print(f"   Return:   £{return_amount:.2f} ({return_pct:+.2f}%)")
    
    print(f"\n📈 TODAY'S ACTIVITY:")
    print(f"   Total Trades: {daily['trades_today']}")
    print(f"   Completed:    {daily['completed_today']}")
    print(f"   Today's P&L:  £{daily['profit_today']:.2f}")
    
    # Get overall performance
    pnl_data = logger.db.get_total_pnl()
    if pnl_data['total_trades'] > 0:
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Total Trades: {pnl_data['total_trades']}")
        print(f"   Wins: {pnl_data['winning_trades']} | Losses: {pnl_data['losing_trades']}")
        print(f"   Win Rate: {pnl_data['win_rate']:.1f}%")
        print(f"   Total P&L: £{pnl_data['total_pnl']:.2f}")
        
        if pnl_data['winning_trades'] > 0:
            print(f"   Avg Profit per Win: £{pnl_data['avg_profit']:.2f}")
        if pnl_data['losing_trades'] > 0:
            print(f"   Avg Loss per Loss: £{pnl_data['avg_loss']:.2f}")
    
    # Check for open position with REAL-TIME data
    print(f"\n💼 POSITION STATUS:")
    
    # Use the strategy's position checker (same as bot uses)
    exit_check = strategy.check_exit_conditions(TRADING_PAIR)
    
    if exit_check['has_position']:
        current_price = exit_check['current_price']
        entry_price = exit_check['entry_price']
        current_pnl = exit_check['expected_profit']
        current_pnl_pct = (current_pnl / entry_price) * 100 if entry_price > 0 else 0
        
        crypto_symbol = TRADING_PAIR.split('-')[0]
        crypto_amount = exit_check.get('crypto_amount', 0)
        
        print(f"   Asset: {crypto_amount:.6f} {crypto_symbol}")
        print(f"   Entry Price:   £{entry_price:.2f}")
        print(f"   Current Price: £{current_price:.2f}")
        
        # Price movement
        price_diff = current_price - entry_price
        price_diff_pct = (price_diff / entry_price) * 100 if entry_price > 0 else 0
        direction = "🟢" if price_diff >= 0 else "🔴"
        print(f"   Price Change:  {direction} £{price_diff:+.2f} ({price_diff_pct:+.2f}%)")
        
        # P&L
        pnl_emoji = "💚" if current_pnl >= 0 else "💔"
        print(f"   Current P&L:   {pnl_emoji} £{current_pnl:+.2f}")
        
        # Targets
        if 'target_price' in exit_check:
            target_price = exit_check['target_price']
            target_distance = target_price - current_price
            target_pct = (target_distance / current_price) * 100
            print(f"\n   🎯 Target:     £{target_price:.2f} (need +£{target_distance:.2f} / +{target_pct:.2f}%)")
            
            if target_pct > 0:
                print(f"                 For £{PROFIT_TARGET_GBP:.2f} profit")
            else:
                print(f"                 ✅ TARGET HIT! Should sell soon")
        
        if 'stop_loss_price' in exit_check:
            stop_loss_price = exit_check['stop_loss_price']
            stop_distance = current_price - stop_loss_price
            stop_pct = (stop_distance / current_price) * 100
            
            if stop_distance > 0:
                print(f"   🛑 Stop Loss:  £{stop_loss_price:.2f} (safe, +£{stop_distance:.2f} buffer)")
            else:
                print(f"   🛑 Stop Loss:  £{stop_loss_price:.2f} ⚠️ TRIGGERED!")
        
        # Status message
        print(f"\n   📋 Status: {exit_check['reason']}")
        
        if exit_check['should_exit']:
            print(f"   ⚠️  BOT WILL SELL ON NEXT CYCLE!")
        else:
            print(f"   ⏳ Holding... waiting for target")
            
    else:
        print(f"   No open positions")
        
        # Show current market price for reference
        snapshot = market.get_full_market_snapshot(TRADING_PAIR)
        if snapshot:
            current_price = snapshot['current_price']
            rsi = snapshot['indicators'].get('rsi', 0)
            print(f"\n   Current {TRADING_PAIR}: £{current_price:.2f}")
            print(f"   RSI: {rsi:.1f}")
            print(f"   Bot is scanning for entry with {MIN_CONFIDENCE*100:.0f}%+ confidence")
    
    # Show recent trade history
    print(f"\n📋 LAST 10 TRADES:")
    trades = logger.get_trade_history(limit=10)
    
    if trades:
        print(f"   {'Time':<10} {'Action':<6} {'Price':<10} {'Amount':<12} {'P&L':<12}")
        print(f"   {'-'*60}")
        
        for trade in trades:
            time_str = trade.timestamp.strftime('%H:%M:%S')
            action = trade.action
            price = f"£{trade.price:.2f}"
            amount = f"{trade.crypto_amount:.6f}" if trade.crypto_amount else "N/A"
            
            if trade.profit_loss is not None:
                pnl_emoji = "✅" if trade.profit_loss >= 0 else "❌"
                pnl_str = f"{pnl_emoji} £{trade.profit_loss:+.2f}"
            else:
                pnl_str = "Open"
            
            print(f"   {time_str:<10} {action:<6} {price:<10} {amount:<12} {pnl_str:<12}")
    else:
        print(f"   No trades yet")
    
    # Bot configuration summary
    print(f"\n⚙️  BOT CONFIGURATION:")
    print(f"   Trading Pair: {TRADING_PAIR}")
    print(f"   Profit Target: £{PROFIT_TARGET_GBP:.2f} per trade")
    print(f"   Min Confidence: {MIN_CONFIDENCE*100:.0f}%")
    
    print("\n" + "="*70)
    print("💡 TIP: Run 'python check_pnl.py' anytime to check status")
    print("="*70 + "\n")
    
    logger.close()

if __name__ == "__main__":
    try:
        check_pnl()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting monitor...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()