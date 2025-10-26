from tracking.database import TradingDatabase
from datetime import datetime

def cleanup_all_trades():
    """
    Completely remove ALL trade records (paper + live) from the trading database.
    This is useful when you want to start fresh while keeping the same DB file structure.
    """
    db = TradingDatabase("trading_bot.db")
    
    print("\n" + "="*70)
    print("🧹 FULL DATABASE CLEANUP - REMOVE ALL TRADES")
    print("="*70)

    all_trades = db.get_all_trades()
    trade_count = len(all_trades)

    if trade_count == 0:
        print("\n✅ Database is already empty. Nothing to clean.")
        db.close()
        return

    print(f"\n📊 Found {trade_count} total trades in database:")
    for trade in all_trades:
        trade_info = (
            f"   {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{trade.mode:<6} | {trade.action:<4} | {trade.product_id:<8} | "
            f"£{trade.price:>8.2f} | {trade.crypto_amount:.6f}"
        )
        print(trade_info)

    print(f"\n⚠️  This will permanently delete ALL {trade_count} trade(s) "
          f"from 'trading_bot.db'. This includes live, paper, and historical trades.")

    confirm = input("\nType 'DELETE ALL' to confirm full database cleanup: ").strip().upper()
    if confirm == "DELETE ALL":
        for trade in all_trades:
            db.session.delete(trade)
        db.session.commit()

        print(f"\n✅ SUCCESS! Deleted all {trade_count} trade record(s).")
        print("📁 Database now contains 0 trades. You can start fresh safely.")
    else:
        print("\n❌ Cancelled. No data removed.")

    db.close()
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        cleanup_all_trades()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
