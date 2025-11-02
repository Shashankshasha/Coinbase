#!/usr/bin/env python3
"""
FIX DATABASE CALCULATIONS - Remove duplicate P&L and fix capital
"""

from tracking.database import TradingDatabase
from data_layer.coinbase_client import CoinbaseClient
from config import TRADING_PAIR, INITIAL_CAPITAL
from sqlalchemy import text

print("\n" + "="*70)
print("🔧 FIXING DATABASE CALCULATIONS")
print("="*70)

db = TradingDatabase("trading_bot.db")
cb_client = CoinbaseClient()

try:
    # Step 1: Check current GBP balance on Coinbase
    print(f"\n1️⃣ Checking actual Coinbase balance...")
    balances = cb_client.get_account_balance()
    actual_gbp = balances.get('GBP', 0)
    
    print(f"   Actual GBP on Coinbase: £{actual_gbp:.2f}")
    
    # Step 2: Get all trades
    print(f"\n2️⃣ Analyzing trades in database...")
    
    from tracking.trade_logger import TradeLogger
    logger = TradeLogger("trading_bot.db")
    all_trades = logger.get_trade_history(limit=50)
    
    print(f"   Found {len(all_trades)} trades")
    
    # Group into BUY-SELL pairs
    buys = []
    sells = []
    
    for trade in all_trades:
        if trade.action == 'BUY':
            buys.append(trade)
        elif trade.action == 'SELL':
            sells.append(trade)
    
    print(f"   BUYs: {len(buys)}, SELLs: {len(sells)}")
    
    # Step 3: Find the problematic trades
    print(f"\n3️⃣ Looking for trades with duplicate P&L...")
    
    buys_with_pnl = [b for b in buys if b.profit_loss is not None]
    
    if buys_with_pnl:
        print(f"   ⚠️  Found {len(buys_with_pnl)} BUY trades with P&L (should be 0)")
        
        for buy in buys_with_pnl:
            print(f"   - {buy.timestamp.strftime('%H:%M')} BUY @ £{buy.price:.2f} | P&L: £{buy.profit_loss:.2f}")
    
    # Step 4: Fix BUY trades (remove P&L)
    print(f"\n4️⃣ Fixing BUY trades (removing P&L)...")
    
    sql = text("""
    UPDATE trades 
    SET profit_loss = NULL,
        profit_loss_pct = NULL
    WHERE action = 'BUY'
    AND profit_loss IS NOT NULL
    """)
    
    result = db.session.execute(sql)
    db.session.commit()
    
    print(f"   ✅ Fixed {result.rowcount} BUY trades")
    
    # Step 5: Verify SELL trades have correct P&L
    print(f"\n5️⃣ Verifying SELL trades...")
    
    sells_with_pnl = [s for s in sells if s.profit_loss is not None]
    
    print(f"   Found {len(sells_with_pnl)} SELL trades with P&L:")
    
    total_pnl = 0
    for sell in sells_with_pnl:
        print(f"   - {sell.timestamp.strftime('%H:%M')} SELL @ £{sell.price:.2f} | P&L: £{sell.profit_loss:.2f}")
        total_pnl += sell.profit_loss
    
    print(f"   Total P&L from closed trades: £{total_pnl:.2f}")
    
    # Step 6: Calculate what capital should be
    print(f"\n6️⃣ Calculating correct capital...")
    
    expected_capital = INITIAL_CAPITAL + total_pnl
    
    print(f"   Starting Capital: £{INITIAL_CAPITAL:.2f}")
    print(f"   Total P&L: £{total_pnl:.2f}")
    print(f"   Expected Capital: £{expected_capital:.2f}")
    print(f"   Actual on Coinbase: £{actual_gbp:.2f}")
    print(f"   Difference: £{abs(expected_capital - actual_gbp):.2f}")
    
    # Step 7: Summary
    print(f"\n" + "="*70)
    print(f"📊 SUMMARY")
    print(f"="*70)
    
    # Recalculate stats
    wins = sum(1 for s in sells_with_pnl if s.profit_loss > 0)
    losses = sum(1 for s in sells_with_pnl if s.profit_loss < 0)
    total_trades = len(sells_with_pnl)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n✅ CORRECTED STATISTICS:")
    print(f"   Completed Trades: {total_trades} (BUY+SELL pairs)")
    print(f"   Wins: {wins}")
    print(f"   Losses: {losses}")
    print(f"   Win Rate: {win_rate:.0f}%")
    print(f"   Total P&L: £{total_pnl:.2f}")
    print(f"   Current Capital: £{actual_gbp:.2f} (Coinbase)")
    print(f"   Expected Capital: £{expected_capital:.2f} (Database)")
    
    if abs(expected_capital - actual_gbp) > 1.0:
        print(f"\n⚠️  WARNING: Capital mismatch detected!")
        print(f"   Database expects: £{expected_capital:.2f}")
        print(f"   Coinbase shows: £{actual_gbp:.2f}")
        print(f"   Difference: £{abs(expected_capital - actual_gbp):.2f}")
        print(f"\n   💡 Recommendation: Update INITIAL_CAPITAL in config.py to: £{actual_gbp:.2f}")
    
    print(f"\n" + "="*70)
    print(f"✅ DATABASE FIXED!")
    print(f"="*70)
    
    logger.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

print("\n" + "="*70)
print("Done. Check your dashboard - it should now show correct values.")
print("="*70 + "\n")