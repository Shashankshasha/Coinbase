#!/usr/bin/env python3
"""
RECOVER MISSING TRADE - Fix the SELL that executed but wasn't logged properly
FIXED: Calculates proceeds from price and size when cost is missing
"""

from tracking.trade_logger import TradeLogger
from execution.order_manager import OrderManager
from data_layer.coinbase_client import CoinbaseClient
from config import TRADING_PAIR
from datetime import datetime
import time

print("\n" + "="*70)
print("🔧 RECOVERING MISSING SELL TRADE")
print("="*70)

logger = TradeLogger("trading_bot.db")
order_mgr = OrderManager()
cb_client = CoinbaseClient()

crypto_symbol = TRADING_PAIR.split('-')[0].upper()

try:
    # Get recent trades from database
    print(f"\n1️⃣ Checking database...")
    db_trades = logger.get_trade_history(product_id=TRADING_PAIR, limit=10)
    
    print(f"   Found {len(db_trades)} trades in database:")
    for trade in db_trades[:3]:
        status = "Open" if trade.profit_loss is None else f"£{trade.profit_loss:+.2f}"
        print(f"   - {trade.timestamp.strftime('%H:%M')} {trade.action} @ £{trade.price:.2f} | {status}")
    
    # Find the open BUY
    open_buy = None
    
    for trade in db_trades:
        if trade.profit_loss is None and trade.action == 'BUY':
            open_buy = trade
            break
    
    if not open_buy:
        print(f"\n   ❌ No open BUY found in database")
        exit(1)
    
    print(f"\n2️⃣ Found open BUY:")
    print(f"   Time: {open_buy.timestamp.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Price: £{open_buy.price:.2f}")
    print(f"   Amount: {open_buy.crypto_amount:.6f} {crypto_symbol}")
    
    # Check Coinbase balance
    print(f"\n3️⃣ Checking Coinbase balance...")
    balances = cb_client.get_account_balance()
    actual_balance = balances.get(crypto_symbol, 0)
    gbp_balance = balances.get('GBP', 0)
    
    print(f"   {crypto_symbol}: {actual_balance:.6f}")
    print(f"   GBP: £{gbp_balance:.2f}")
    
    if actual_balance > 0:
        print(f"\n   ⚠️  You still have {crypto_symbol}! Position not actually closed.")
        exit(1)
    
    # Get recent Coinbase orders
    print(f"\n4️⃣ Fetching recent Coinbase orders...")
    recent_orders = order_mgr.get_recent_orders(product_id=TRADING_PAIR, limit=20)
    
    if not recent_orders:
        print(f"   ❌ No orders found")
        exit(1)
    
    print(f"   Found {len(recent_orders)} orders")
    
    # Find the SELL order after the BUY
    print(f"\n5️⃣ Looking for SELL order after {open_buy.timestamp.strftime('%H:%M')}...")
    
    matching_sell = None
    for order in recent_orders:
        if order.get('side') == 'SELL':
            # Try to parse timestamp
            order_time_str = order.get('timestamp', '')
            try:
                order_time = datetime.fromisoformat(order_time_str.replace('Z', '+00:00'))
                order_time = order_time.replace(tzinfo=None)
            except:
                continue
            
            # Check if after BUY
            if order_time > open_buy.timestamp:
                matching_sell = order
                print(f"   ✅ Found SELL: {order_time.strftime('%Y-%m-%d %H:%M')} @ £{order.get('price', 0):.2f}")
                break
    
    if not matching_sell:
        print(f"   ❌ Could not find matching SELL order")
        exit(1)
    
    # Calculate P&L
    print(f"\n6️⃣ Calculating P&L...")
    
    buy_price = open_buy.price
    buy_amount = open_buy.crypto_amount
    
    sell_price = matching_sell.get('price', 0)
    sell_amount = matching_sell.get('size', 0)
    
    print(f"\n   BUY Details:")
    print(f"   - Amount: {buy_amount:.6f} {crypto_symbol}")
    print(f"   - Price: £{buy_price:.2f}")
    
    print(f"\n   SELL Details:")
    print(f"   - Amount: {sell_amount:.6f} {crypto_symbol}")
    print(f"   - Price: £{sell_price:.2f}")
    
    # FIXED: Calculate proceeds from price and amount (don't rely on 'cost')
    # Entry cost (including buy fee 1.2%)
    entry_cost = buy_amount * buy_price * 1.012
    
    # Exit revenue (sell price * amount - 1.2% fee)
    exit_gross = sell_amount * sell_price
    exit_fee = exit_gross * 0.012
    exit_revenue = exit_gross - exit_fee
    
    # Net P&L
    pnl = exit_revenue - entry_cost
    pnl_pct = (pnl / entry_cost) * 100
    
    print(f"\n   💰 P&L CALCULATION:")
    print(f"   Entry Cost: £{entry_cost:.2f} (£{buy_price:.2f} × {buy_amount:.4f} + 1.2% fee)")
    print(f"   Exit Gross: £{exit_gross:.2f} (£{sell_price:.2f} × {sell_amount:.4f})")
    print(f"   Exit Fee: £{exit_fee:.2f} (1.2%)")
    print(f"   Exit Net: £{exit_revenue:.2f}")
    print(f"   ───────────────────────")
    print(f"   Net P&L: £{pnl:+.2f} ({pnl_pct:+.2f}%)")
    
    # Sanity check
    if abs(pnl) > 100:
        print(f"\n   ⚠️  WARNING: P&L seems too large (£{pnl:.2f})")
        print(f"   Please review the numbers above before proceeding.")
    
    # Update database
    print(f"\n7️⃣ Ready to update database")
    print(f"   This will:")
    print(f"   - Record the SELL with P&L: £{pnl:+.2f}")
    print(f"   - Close the position")
    print(f"   - Update capital to: £{gbp_balance:.2f}")
    
    confirm = input(f"\n   Type 'FIX' to proceed: ")
    
    if confirm.strip().upper() != 'FIX':
        print(f"\n   ❌ Recovery cancelled")
        exit(0)
    
    # Update database
    from tracking.database import TradingDatabase
    
    db = TradingDatabase("trading_bot.db")
    
    # Find any SELL trades that are marked as open and update them
    from sqlalchemy import text
    
    # Update SELL trades
    sql_sell = text("""
    UPDATE trades 
    SET profit_loss = :pnl, 
        profit_loss_pct = :pnl_pct,
        entry_price = :entry_price,
        exit_price = :exit_price,
        amount_gbp = :sell_revenue
    WHERE product_id = :product_id
    AND action = 'SELL'
    AND profit_loss IS NULL
    AND timestamp >= :buy_timestamp
    """)
    
    db.session.execute(sql_sell, {
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'entry_price': buy_price,
        'exit_price': sell_price,
        'sell_revenue': exit_revenue,
        'product_id': TRADING_PAIR,
        'buy_timestamp': open_buy.timestamp
    })
    
    # Update BUY trade to mark as closed
    sql_buy = text("""
    UPDATE trades 
    SET profit_loss = :pnl,
        profit_loss_pct = :pnl_pct,
        exit_price = :exit_price
    WHERE trade_id = :trade_id
    """)
    
    db.session.execute(sql_buy, {
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'exit_price': sell_price,
        'trade_id': open_buy.trade_id
    })
    
    db.session.commit()
    db.close()
    
    print(f"\n   ✅ Database updated!")
    
    print(f"\n" + "="*70)
    print(f"✅ RECOVERY COMPLETE!")
    print(f"="*70)
    print(f"\n💰 Summary:")
    print(f"   Entry: £{entry_cost:.2f} @ £{buy_price:.2f}")
    print(f"   Exit: £{exit_revenue:.2f} @ £{sell_price:.2f}")
    print(f"   P&L: £{pnl:+.2f} ({pnl_pct:+.2f}%)")
    print(f"   Capital: £{gbp_balance:.2f}")
    print(f"\n✅ Check your dashboard - trades should now show correctly!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    logger.close()

print("\n" + "="*70)
print("Done.")
print("="*70 + "\n")