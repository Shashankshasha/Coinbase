

from tracking.database import TradingDatabase
from tracking.trade_logger import TradeLogger
from datetime import datetime
import shutil
import os

print("\n" + "="*70)
print("🗑️  DATABASE RESET - Starting Fresh")
print("="*70)

DB_PATH = "trading_bot.db"

# Backup old database
print(f"\n1️⃣ Backing up old database...")
if os.path.exists(DB_PATH):
    backup_name = f"trading_bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(DB_PATH, backup_name)
    print(f"   ✅ Backed up to: {backup_name}")
    os.remove(DB_PATH)
    print(f"   ✅ Deleted old database")
else:
    print(f"   ℹ️  No existing database found")

# Create fresh database
print(f"\n2️⃣ Creating fresh database...")
db = TradingDatabase(DB_PATH)
print(f"   ✅ New database created")

# Add actual trades
print(f"\n3️⃣ Adding actual trade from Coinbase...")
logger = TradeLogger(DB_PATH)

BUY_ORDER = {
    'trade_id': '3c4884d8-6269-464f-b6af-7ba51b5cd131',
    'order_id': '3c4884d8-6269-464f-b6af-7ba51b5cd131',
    'timestamp': datetime(2025, 10, 31, 23, 32, 4),
    'action': 'BUY',
    'product_id': 'SOL-GBP',
    'mode': 'LIVE',
    'amount_gbp': 538.19,
    'crypto_amount': 3.749,
    'price': 142.49,
    'fee': 4.01,
    'confidence': 0.95,
    'reasoning': 'Actual Coinbase trade',
    'executed': True,
    'entry_price': None,
    'exit_price': None,
    'profit_loss': None,
    'profit_loss_pct': None
}

SELL_ORDER = {
    'trade_id': 'ab6780d2-ee2a-4b4e-b759-f12ece1200fc',
    'order_id': 'ab6780d2-ee2a-4b4e-b759-f12ece1200fc',
    'timestamp': datetime(2025, 11, 1, 13, 39, 53),
    'action': 'SELL',
    'product_id': 'SOL-GBP',
    'mode': 'LIVE',
    'amount_gbp': 524.83,
    'crypto_amount': 3.749,
    'price': 141.05,
    'fee': 3.97,
    'confidence': 0.95,
    'reasoning': 'Stop loss hit',
    'executed': True,
    'entry_price': 142.49,
    'exit_price': 141.05,
    'profit_loss': -13.36,
    'profit_loss_pct': -2.48
}

logger.log_trade(BUY_ORDER)
print(f"   ✅ BUY trade added: 3.749 SOL @ £142.49 = £538.19")

logger.log_trade(SELL_ORDER)
print(f"   ✅ SELL trade added: 3.749 SOL @ £141.05 = £524.83")

logger.close()

# Verify
print(f"\n4️⃣ Verifying database...")
logger = TradeLogger(DB_PATH)
trades = logger.get_trade_history(limit=10)
pnl_stats = logger.db.get_total_pnl()

print(f"   Found {len(trades)} trades")
print(f"   Total P&L: £{pnl_stats['total_pnl']:.2f}")

if pnl_stats['total_pnl'] == -13.36:
    print(f"\n   ✅ P&L matches Coinbase exactly!")
else:
    print(f"\n   ⚠️  P&L mismatch: Expected £-13.36, Got £{pnl_stats['total_pnl']:.2f}")

logger.close()

print(f"\n" + "="*70)
print(f"✅ DATABASE RESET COMPLETE")
print(f"="*70)
print(f"\n💰 Correct Stats: Capital £524.83 | Loss £-13.36\n")
