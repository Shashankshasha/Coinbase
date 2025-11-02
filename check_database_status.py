#!/usr/bin/env python3
"""Quick check - What's in the database?"""

from tracking.trade_logger import TradeLogger
import os

print("\n" + "="*70)
print("🔍 DATABASE STATUS CHECK")
print("="*70)

DB_PATH = "trading_bot.db"

# Check if database exists
if not os.path.exists(DB_PATH):
    print(f"\n❌ Database file not found: {DB_PATH}")
    print(f"   Run: python reset_database_clean.py")
    exit(1)

print(f"\n✅ Database file exists: {DB_PATH}")
print(f"   Size: {os.path.getsize(DB_PATH)} bytes")

# Check contents
logger = TradeLogger(DB_PATH)

try:
    # Get all trades
    trades = logger.get_trade_history(limit=50)
    
    print(f"\n📊 Trades in Database: {len(trades)}")
    
    if len(trades) == 0:
        print(f"   ❌ DATABASE IS EMPTY!")
        print(f"   Run: python reset_database_clean.py")
    else:
        print(f"\n   Trade List:")
        for i, trade in enumerate(trades, 1):
            pnl_str = f"£{trade.profit_loss:.2f}" if trade.profit_loss else "Entry"
            print(f"   {i}. {trade.timestamp.strftime('%m/%d %H:%M')} "
                  f"{trade.action} @ £{trade.price:.2f} | {pnl_str}")
    
    # Get P&L stats
    pnl_stats = logger.db.get_total_pnl()
    
    print(f"\n💰 Statistics:")
    print(f"   Total Trades: {pnl_stats['total_trades']}")
    print(f"   Total P&L: £{pnl_stats['total_pnl']:.2f}")
    print(f"   Win Rate: {pnl_stats['win_rate']:.0f}%")
    
    if pnl_stats['total_pnl'] == -13.36:
        print(f"\n   ✅ P&L is correct!")
    elif pnl_stats['total_pnl'] == 0:
        print(f"\n   ❌ No trades recorded!")
    else:
        print(f"\n   ⚠️  P&L unexpected: £{pnl_stats['total_pnl']:.2f}")

finally:
    logger.close()

print(f"\n" + "="*70)
print("Done.")
print("="*70 + "\n")