#!/usr/bin/env python3
"""
FIX P&L WITH ACTUAL COINBASE VALUES
Uses real order totals instead of calculated fees
"""

from tracking.database import TradingDatabase
from sqlalchemy import text

print("\n" + "="*70)
print("🔧 FIXING P&L WITH ACTUAL COINBASE VALUES")
print("="*70)

# ACTUAL VALUES FROM COINBASE ORDERS
BUY_TOTAL = 538.19      # Total paid (including fees)
SELL_TOTAL = 524.83     # Total received (after fees)
ACTUAL_PNL = SELL_TOTAL - BUY_TOTAL  # -13.36

BUY_PRICE = 142.49      # Actual execution price
SELL_PRICE = 141.05     # Actual execution price
AMOUNT = 3.749          # Amount traded

print(f"\n📊 ACTUAL COINBASE VALUES:")
print(f"   BUY:  3.749 SOL @ £{BUY_PRICE:.2f} = £{BUY_TOTAL:.2f} total")
print(f"   SELL: 3.749 SOL @ £{SELL_PRICE:.2f} = £{SELL_TOTAL:.2f} total")
print(f"   ACTUAL P&L: £{ACTUAL_PNL:.2f}")

db = TradingDatabase("trading_bot.db")

try:
    # Calculate P&L percentage
    pnl_pct = (ACTUAL_PNL / BUY_TOTAL) * 100
    
    print(f"\n🔧 Updating database with correct values...")
    
    # Update BUY trade
    sql_buy = text("""
    UPDATE trades 
    SET price = :price,
        amount_gbp = :amount_gbp,
        profit_loss = NULL,
        profit_loss_pct = NULL
    WHERE action = 'BUY'
    AND product_id = 'SOL-GBP'
    AND timestamp >= '2025-10-31 23:00:00'
    """)
    
    db.session.execute(sql_buy, {
        'price': BUY_PRICE,
        'amount_gbp': BUY_TOTAL
    })
    
    print(f"   ✅ Updated BUY trade")
    
    # Update SELL trade
    sql_sell = text("""
    UPDATE trades 
    SET price = :price,
        amount_gbp = :amount_gbp,
        profit_loss = :pnl,
        profit_loss_pct = :pnl_pct,
        entry_price = :entry_price,
        exit_price = :exit_price
    WHERE action = 'SELL'
    AND product_id = 'SOL-GBP'
    AND timestamp >= '2025-11-01 13:00:00'
    ORDER BY timestamp DESC
    LIMIT 1
    """)
    
    db.session.execute(sql_sell, {
        'price': SELL_PRICE,
        'amount_gbp': SELL_TOTAL,
        'pnl': ACTUAL_PNL,
        'pnl_pct': pnl_pct,
        'entry_price': BUY_PRICE,
        'exit_price': SELL_PRICE
    })
    
    print(f"   ✅ Updated SELL trade")
    
    db.session.commit()
    
    print(f"\n" + "="*70)
    print(f"✅ DATABASE UPDATED WITH CORRECT VALUES")
    print(f"="*70)
    
    print(f"\n📊 CORRECTED TRADE:")
    print(f"   Entry: £{BUY_TOTAL:.2f} @ £{BUY_PRICE:.2f}")
    print(f"   Exit: £{SELL_TOTAL:.2f} @ £{SELL_PRICE:.2f}")
    print(f"   P&L: £{ACTUAL_PNL:.2f} ({pnl_pct:.2f}%)")
    
    print(f"\n💰 YOUR ACTUAL CAPITAL:")
    print(f"   Before trade: £538.19")
    print(f"   After trade: £524.83")
    print(f"   Loss: £{abs(ACTUAL_PNL):.2f}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.session.rollback()

finally:
    db.close()

print("\n" + "="*70)
print("Done. Check dashboard - P&L should now show £-13.36")
print("="*70 + "\n")