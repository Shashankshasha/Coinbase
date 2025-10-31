from tracking.trade_logger import TradeLogger
from profit_strategy_enhanced import ProfitStrategyEnhanced
from data_layer.market_data import MarketData
from datetime import datetime, timedelta
from config import TRADING_PAIR, MIN_CONFIDENCE
import time
import os

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_24h_stats(market, product_id):
    """Get 24-hour high/low/volume stats"""
    try:
        candles = market.get_candles(product_id, granularity="ONE_HOUR", limit=24)
        if not candles:
            return None
        
        prices = [c['close'] for c in candles]
        volumes = [c['volume'] for c in candles]
        
        return {
            'high_24h': max([c['high'] for c in candles]),
            'low_24h': min([c['low'] for c in candles]),
            'volume_24h': sum(volumes),
            'open_24h': candles[0]['open'],
            'close_current': prices[-1],
            'avg_volume': sum(volumes) / len(volumes) if volumes else 0
        }
    except:
        return None

def display_dashboard():
    """
    ULTRA-ENHANCED LIVE DASHBOARD v2.0
    NEW FEATURES:
    - All technical indicators displayed
    - 24h high/low prices
    - Volume statistics
    - Price change % (24h)
    - Market momentum indicators
    - Detailed signal breakdown
    - Candle pattern info
    Updates every 30 seconds with real-time data
    Press Ctrl+C to exit
    """
    logger = TradeLogger("trading_bot.db")
    strategy = ProfitStrategyEnhanced("trading_bot.db")
    market = MarketData()
    
    clear_screen()
    
    print("="*90)
    print(f"📊 ULTRA-LIVE TRADING DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)
    
    # ================================================================
    # MARKET DATA SECTION (NEW!)
    # ================================================================
    snapshot = market.get_full_market_snapshot(TRADING_PAIR)
    stats_24h = get_24h_stats(market, TRADING_PAIR)
    
    if snapshot:
        current_price = snapshot['current_price']
        indicators = snapshot.get('indicators', {})
        signal_data = snapshot.get('signal', {})
        
        print(f"\n💹 MARKET DATA - {TRADING_PAIR}")
        print("-" * 90)
        
        # Current price with 24h change
        if stats_24h:
            price_change_24h = current_price - stats_24h['open_24h']
            price_change_pct = (price_change_24h / stats_24h['open_24h']) * 100
            change_emoji = "🟢" if price_change_24h >= 0 else "🔴"
            
            print(f"   Price: £{current_price:.2f} {change_emoji} {price_change_pct:+.2f}% (24h)")
            print(f"   24h High: £{stats_24h['high_24h']:.2f} | Low: £{stats_24h['low_24h']:.2f}")
            
            # Show price position in 24h range
            range_24h = stats_24h['high_24h'] - stats_24h['low_24h']
            if range_24h > 0:
                position_in_range = (current_price - stats_24h['low_24h']) / range_24h
                bar_length = 30
                filled = int(bar_length * position_in_range)
                bar = "░" * filled + "█" + "░" * (bar_length - filled - 1)
                print(f"   Range: [{bar}] {position_in_range*100:.0f}%")
            
            # Volume info
            current_volume = indicators.get('volume_ratio', 0) * stats_24h['avg_volume']
            volume_emoji = "🔥" if indicators.get('volume_ratio', 0) > 1.5 else "📊"
            print(f"   24h Volume: {stats_24h['volume_24h']:.2f} {TRADING_PAIR.split('-')[0]}")
            print(f"   Current Volume: {volume_emoji} {indicators.get('volume_ratio', 0):.2f}x average")
        else:
            print(f"   Price: £{current_price:.2f}")
        
        # ================================================================
        # TECHNICAL INDICATORS (DETAILED)
        # ================================================================
        print(f"\n📈 TECHNICAL INDICATORS")
        print("-" * 90)
        
        # RSI with interpretation
        rsi = indicators.get('rsi', 50)
        if rsi > 70:
            rsi_status = "🔴 OVERBOUGHT"
            rsi_action = "⚠️  Avoid buying (likely to drop)"
        elif rsi > 60:
            rsi_status = "🟡 HIGH"
            rsi_action = "⚠️  Caution (strong but risky)"
        elif rsi > 40:
            rsi_status = "🟢 NEUTRAL"
            rsi_action = "✅ Good for trading"
        elif rsi > 30:
            rsi_status = "🟡 LOW"
            rsi_action = "💡 Watch for bounce"
        else:
            rsi_status = "🔴 OVERSOLD"
            rsi_action = "⚠️  Avoid shorting (likely to rise)"
        
        print(f"   RSI (14): {rsi:.1f} {rsi_status}")
        print(f"             {rsi_action}")
        
        # RSI visual bar
        rsi_bar_length = 50
        rsi_filled = int((rsi / 100) * rsi_bar_length)
        rsi_bar = "█" * rsi_filled + "░" * (rsi_bar_length - rsi_filled)
        print(f"             [{rsi_bar}]")
        print(f"             0 ←─────────── 50 ─────────→ 100")
        
        # MACD with interpretation
        macd_value = indicators.get('macd_value', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_histogram = indicators.get('macd_histogram', 0)
        macd_cross = indicators.get('macd_cross', 'neutral')
        
        if macd_cross == 'bullish':
            macd_status = "🟢 BULLISH CROSS"
            macd_action = "✅ Upward momentum"
        elif macd_cross == 'bearish':
            macd_status = "🔴 BEARISH CROSS"
            macd_action = "⚠️  Downward momentum"
        else:
            macd_status = "🟡 NEUTRAL"
            macd_action = "⏸️  Waiting for signal"
        
        print(f"\n   MACD: {macd_status}")
        print(f"         Value: {macd_value:.4f} | Signal: {macd_signal:.4f} | Histogram: {macd_histogram:.4f}")
        print(f"         {macd_action}")
        
        # EMA with interpretation
        ema_10 = indicators.get('ema_10', 0)
        ema_50 = indicators.get('ema_50', 0)
        ema_cross = indicators.get('ema_cross', 'neutral')
        
        if ema_cross == 'bullish':
            ema_status = "🟢 BULLISH (10 > 50)"
            ema_action = "✅ Uptrend confirmed"
        elif ema_cross == 'bearish':
            ema_status = "🔴 BEARISH (10 < 50)"
            ema_action = "⚠️  Downtrend confirmed"
        else:
            ema_status = "🟡 NEUTRAL"
            ema_action = "⏸️  No clear trend"
        
        print(f"\n   EMA: {ema_status}")
        print(f"        EMA(10): £{ema_10:.2f} | EMA(50): £{ema_50:.2f}")
        print(f"        Current vs EMA(10): {((current_price - ema_10) / ema_10 * 100):+.2f}%")
        print(f"        {ema_action}")
        
        # Bollinger Bands (if available)
        bb_upper = indicators.get('bb_upper', 0)
        bb_middle = indicators.get('bb_middle', 0)
        bb_lower = indicators.get('bb_lower', 0)
        
        if bb_upper > 0:
            print(f"\n   Bollinger Bands:")
            print(f"        Upper: £{bb_upper:.2f} | Middle: £{bb_middle:.2f} | Lower: £{bb_lower:.2f}")
            
            if current_price > bb_upper:
                print(f"        🔴 Price above upper band (overbought)")
            elif current_price < bb_lower:
                print(f"        🟢 Price below lower band (oversold)")
            else:
                print(f"        🟡 Price within bands (normal)")
        
        # ================================================================
        # TRADING SIGNAL ANALYSIS
        # ================================================================
        print(f"\n🎯 SIGNAL ANALYSIS")
        print("-" * 90)
        
        signal = signal_data.get('signal', 'HOLD')
        strength = signal_data.get('strength', 0)
        confirmations = signal_data.get('confirmations', 0)
        
        # Signal display
        if signal == 'BUY':
            signal_emoji = "🟢"
            signal_color = "STRONG BUY"
        elif signal == 'SELL':
            signal_emoji = "🔴"
            signal_color = "STRONG SELL"
        else:
            signal_emoji = "🟡"
            signal_color = "HOLD"
        
        print(f"   Overall Signal: {signal_emoji} {signal_color}")
        print(f"   Strength: {strength*100:.1f}% (Need {MIN_CONFIDENCE*100:.0f}% to trade)")
        print(f"   Confirmations: {confirmations}/4 indicators agree")
        
        # Strength bar
        strength_bar_length = 50
        strength_filled = int(strength * strength_bar_length)
        threshold_pos = int(MIN_CONFIDENCE * strength_bar_length)
        
        strength_bar = ""
        for i in range(strength_bar_length):
            if i < strength_filled:
                strength_bar += "█"
            elif i == threshold_pos:
                strength_bar += "│"
            else:
                strength_bar += "░"
        
        print(f"   [{strength_bar}]")
        print(f"    0% ←──── Threshold ({MIN_CONFIDENCE*100:.0f}%) ────→ 100%")
        
        # Individual indicator breakdown
        print(f"\n   Indicator Breakdown:")
        
        # RSI signal
        if rsi > 70:
            print(f"   ❌ RSI: Too high ({rsi:.1f}) - Overbought")
        elif rsi < 30:
            print(f"   ⚠️  RSI: Too low ({rsi:.1f}) - Oversold")
        elif 40 <= rsi <= 60:
            print(f"   ✅ RSI: Neutral ({rsi:.1f}) - Good range")
        else:
            print(f"   🟡 RSI: Acceptable ({rsi:.1f})")
        
        # MACD signal
        if macd_cross == 'bullish':
            print(f"   ✅ MACD: Bullish cross - Momentum up")
        elif macd_cross == 'bearish':
            print(f"   ❌ MACD: Bearish cross - Momentum down")
        else:
            print(f"   🟡 MACD: Neutral - No clear signal")
        
        # EMA signal
        if ema_cross == 'bullish':
            print(f"   ✅ EMA: Bullish (10 > 50) - Uptrend")
        elif ema_cross == 'bearish':
            print(f"   ❌ EMA: Bearish (10 < 50) - Downtrend")
        else:
            print(f"   🟡 EMA: Neutral - Sideways")
        
        # Volume signal
        volume_ratio = indicators.get('volume_ratio', 0)
        if volume_ratio > 1.5:
            print(f"   ✅ Volume: High ({volume_ratio:.1f}x) - Strong interest")
        elif volume_ratio > 0.8:
            print(f"   ✅ Volume: Normal ({volume_ratio:.1f}x) - Sufficient")
        else:
            print(f"   ❌ Volume: Low ({volume_ratio:.1f}x) - Avoid trading")
        
        # Trading recommendation
        if strength >= MIN_CONFIDENCE and signal == 'BUY':
            print(f"\n   🚀 RECOMMENDATION: Bot should BUY soon!")
        elif strength >= MIN_CONFIDENCE and signal == 'SELL':
            print(f"\n   ⚠️  RECOMMENDATION: Bot waiting for better entry")
        else:
            needed = (MIN_CONFIDENCE - strength) * 100
            print(f"\n   ⏳ RECOMMENDATION: Waiting... Need {needed:+.0f}% more confidence")
    
    # ================================================================
    # ACCOUNT STATUS
    # ================================================================
    daily = strategy.get_daily_stats()
    
    current_tier = daily.get('current_tier', 'Unknown')
    current_target = daily.get('current_profit_target', 2.0)
    
    print(f"\n💰 ACCOUNT STATUS")
    print("-" * 90)
    
    print(f"   🎖️  Profit Tier: {current_tier.upper()}")
    print(f"   🎯 Current Target: £{current_target:.2f} per trade")
    
    # Capital info
    print(f"\n   Capital: £{daily['initial_capital']:.2f} → £{daily['current_capital']:.2f}")
    return_amount = daily['total_return']
    return_pct = (return_amount / daily['initial_capital']) * 100 if daily['initial_capital'] > 0 else 0
    return_emoji = "📈" if return_amount >= 0 else "📉"
    print(f"   Return: {return_emoji} £{return_amount:.2f} ({return_pct:+.2f}%)")
    
    # Progress to next tier
    capital = daily['current_capital']
    if capital < 800:
        needed = 800 - capital
        progress_pct = (capital / 800) * 100
        print(f"   💎 Progress to Intermediate: {progress_pct:.1f}% (need £{needed:.2f} more)")
    elif capital < 1500:
        needed = 1500 - capital
        progress_pct = ((capital - 800) / 700) * 100
        print(f"   💎 Progress to Advanced: {progress_pct:.1f}% (need £{needed:.2f} more)")
    elif capital < 3000:
        needed = 3000 - capital
        progress_pct = ((capital - 1500) / 1500) * 100
        print(f"   💎 Progress to Professional: {progress_pct:.1f}% (need £{needed:.2f} more)")
    elif capital < 10000:
        needed = 10000 - capital
        progress_pct = ((capital - 3000) / 7000) * 100
        print(f"   💎 Progress to Expert: {progress_pct:.1f}% (need £{needed:.2f} more)")
    else:
        print(f"   🏆 Maximum tier reached!")
    
    # Performance metrics
    pnl_data = logger.db.get_total_pnl()
    if pnl_data['total_trades'] > 0:
        print(f"\n   📊 Performance:")
        print(f"      Trades: {pnl_data['total_trades']} | Wins: {pnl_data['winning_trades']} | Losses: {pnl_data['losing_trades']}")
        print(f"      Win Rate: {pnl_data['win_rate']:.1f}%")
        print(f"      Total P&L: £{pnl_data['total_pnl']:.2f}")
        
        if pnl_data['winning_trades'] > 0 and pnl_data['losing_trades'] > 0:
            profit_factor = abs((pnl_data['avg_profit'] * pnl_data['winning_trades']) / 
                               (pnl_data['avg_loss'] * pnl_data['losing_trades']))
            print(f"      Profit Factor: {profit_factor:.2f}")
        
        if pnl_data['winning_trades'] > 0:
            avg_profit = pnl_data['avg_profit']
            if avg_profit > current_target:
                extra_avg = avg_profit - current_target
                print(f"      Avg Win: £{avg_profit:.2f} (£{extra_avg:.2f} extra via trailing! 💎)")
            else:
                print(f"      Avg Win: £{avg_profit:.2f}")
        
        if pnl_data['losing_trades'] > 0:
            print(f"      Avg Loss: £{pnl_data['avg_loss']:.2f}")
    
    # ================================================================
    # LIVE POSITION
    # ================================================================
    print(f"\n💼 LIVE POSITION")
    print("-" * 90)
    
    exit_check = strategy.check_exit_conditions(TRADING_PAIR)
    
    if exit_check['has_position']:
        current_price = exit_check['current_price']
        entry_price = exit_check['entry_price']
        current_pnl = exit_check['expected_profit']
        
        crypto_symbol = TRADING_PAIR.split('-')[0]
        crypto_amount = exit_check.get('crypto_amount', 0)
        position_tier = exit_check.get('profit_tier', current_tier)
        
        # Position header
        print(f"   🔓 OPEN: {crypto_amount:.6f} {crypto_symbol} (Tier: {position_tier})")
        
        # Price movement
        price_diff = current_price - entry_price
        price_diff_pct = (price_diff / entry_price) * 100 if entry_price > 0 else 0
        direction = "🟢" if price_diff >= 0 else "🔴"
        
        print(f"   Entry: £{entry_price:.2f} → Now: £{current_price:.2f} {direction} {price_diff_pct:+.2f}%")
        
        # P&L display
        pnl_emoji = "💚" if current_pnl >= 0 else "💔"
        pnl_status = "PROFIT" if current_pnl >= 0 else "LOSS"
        print(f"   P&L: {pnl_emoji} £{current_pnl:+.2f} ({pnl_status})")
        
        # Trailing stop section
        if exit_check.get('trailing_active'):
            print(f"\n   🎯 TRAILING STOP ACTIVE!")
            peak_price = exit_check.get('peak_price', 0)
            trailing_stop_price = exit_check.get('trailing_stop_price', 0)
            extra_profit = current_pnl - current_target
            
            print(f"   ├─ Peak Reached: £{peak_price:.2f}")
            print(f"   ├─ Trailing Stop: £{trailing_stop_price:.2f}")
            print(f"   ├─ Current Buffer: £{current_price - trailing_stop_price:.2f}")
            print(f"   └─ Extra Profit: £{extra_profit:.2f} above £{current_target:.2f} minimum 💎")
            
            distance_from_stop = ((current_price - trailing_stop_price) / current_price) * 100
            trail_distance_pct = strategy.trailing_stop_distance_pct * 100
            
            if distance_from_stop < trail_distance_pct * 0.3:
                print(f"\n   ⚠️  CLOSE TO STOP! Only {distance_from_stop:.2f}% buffer")
            else:
                print(f"\n   ✅ Safe: {distance_from_stop:.2f}% from stop")
            
            print(f"   📈 Riding the trend, will exit if drops {trail_distance_pct:.1f}% from peak")
        
        # Progress to target
        elif 'target_price' in exit_check:
            target_price = exit_check['target_price']
            target_distance = target_price - current_price
            target_pct = (target_distance / current_price) * 100
            
            total_distance = target_price - entry_price
            progress = ((current_price - entry_price) / total_distance) if total_distance > 0 else 0
            progress = max(0, min(1, progress))
            
            bar_length = 50
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\n   Progress to £{current_target:.2f} Target:")
            print(f"   [{bar}] {progress*100:.1f}%")
            print(f"   Need: +£{target_distance:.2f} ({target_pct:+.2f}%) to reach £{target_price:.2f}")
            
            if target_pct > 0:
                print(f"   🎯 Once hit, trailing stop activates to capture more gains!")
            else:
                print(f"   ✅ TARGET HIT! Trailing activates next cycle!")
        
        # Stop loss info
        if 'stop_loss_price' in exit_check:
            stop_loss_price = exit_check['stop_loss_price']
            stop_distance = current_price - stop_loss_price
            
            if stop_distance < 0:
                print(f"\n   🚨 STOP LOSS TRIGGERED: £{stop_loss_price:.2f}")
            else:
                stop_pct = (stop_distance / current_price) * 100
                if stop_pct < 0.3:
                    print(f"\n   🚨 NEAR STOP LOSS: £{stop_loss_price:.2f} (buffer: {stop_pct:.2f}%)")
                else:
                    print(f"\n   🛡️  Stop Loss: £{stop_loss_price:.2f} (buffer: {stop_pct:.2f}%)")
        
        # Exit status
        status = exit_check['reason']
        if exit_check['should_exit']:
            if 'TRAILING STOP' in status:
                print(f"\n   🎯 TRAILING STOP EXIT: {status}")
            else:
                print(f"\n   🔔 EXIT SIGNAL: {status}")
            print(f"   ⚡ BOT WILL SELL NEXT CYCLE!")
        else:
            print(f"\n   📊 Status: {status}")
            
    else:
        print(f"   🔓 No open position - Scanning for entry...")
        
        if snapshot:
            print(f"\n   Scanning Status:")
            print(f"   ├─ Signal: {signal_data.get('signal', 'N/A')}")
            print(f"   ├─ Strength: {signal_data.get('strength', 0)*100:.1f}%")
            print(f"   └─ Threshold: {MIN_CONFIDENCE*100:.0f}%")
            
            if signal_data.get('strength', 0) >= MIN_CONFIDENCE:
                print(f"\n   ✅ Confidence met! Bot should enter soon!")
            else:
                need_pct = (MIN_CONFIDENCE - signal_data.get('strength', 0)) * 100
                print(f"\n   ⏳ Waiting... Need {need_pct:+.0f}% more confidence")
    
    # ================================================================
    # RECENT TRADES
    # ================================================================
    print(f"\n📋 RECENT TRADES")
    print("-" * 90)
    trades = logger.get_trade_history(limit=7)
    
    if trades:
        print(f"   {'Time':<10} {'Action':<6} {'Price':<12} {'P&L':<15} {'Type'}")
        print(f"   {'-'*80}")
        for trade in trades:
            time_str = trade.timestamp.strftime('%H:%M:%S')
            if trade.profit_loss is not None:
                pnl_emoji = "✅" if trade.profit_loss >= 0 else "❌"
                
                # Enhanced bonus markers
                if trade.profit_loss > (current_target * 3):
                    bonus = " 💎💎💎"  # Triple diamond!
                    trade_type = "Mega Win"
                elif trade.profit_loss > (current_target * 2):
                    bonus = " 💎💎"
                    trade_type = "Big Win"
                elif trade.profit_loss > (current_target * 1.5):
                    bonus = " 💎"
                    trade_type = "Bonus"
                elif trade.profit_loss > 0:
                    bonus = ""
                    trade_type = "Standard"
                else:
                    bonus = ""
                    trade_type = "Loss"
                
                pnl_str = f"{pnl_emoji} £{trade.profit_loss:+7.2f}{bonus}"
            else:
                pnl_str = "⏳ Open"
                trade_type = "Open"
            
            print(f"   {time_str:<10} {trade.action:<6} £{trade.price:<10.2f} {pnl_str:<15} {trade_type}")
    else:
        print(f"   No trades yet - Bot will start trading when conditions are met")
    
    # ================================================================
    # FOOTER
    # ================================================================
    print("\n" + "="*90)
    print("🔄 Auto-refresh: 30s | Press Ctrl+C to exit")
    print(f"🎖️  Tier: {current_tier} | 🎯 Target: £{current_target:.2f} | 📊 Confidence Required: {MIN_CONFIDENCE*100:.0f}%")
    print("="*90)
    
    logger.close()

def run_live_dashboard():
    """Run the ultra-enhanced live dashboard with auto-refresh."""
    print("\n🚀 Starting ULTRA-ENHANCED Live Dashboard v2.0...")
    print("\n✨ NEW FEATURES:")
    print("   📊 All technical indicators (RSI, MACD, EMA, Bollinger)")
    print("   📈 24h high/low prices")
    print("   💹 Volume statistics")
    print("   🎯 Detailed signal breakdown")
    print("   💎 Enhanced profit tracking")
    print("\n⌨️  Press Ctrl+C to exit\n")
    time.sleep(3)
    
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