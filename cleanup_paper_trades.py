from tracking.database import TradingDatabase
from datetime import datetime

def cleanup_paper_trades():
    """
    Remove paper trades from the live trading database.
    This prevents the bot from confusing paper positions with real ones.
    """
    
    db = TradingDatabase("trading_bot.db")
    
    print("\n" + "="*70)
    print("🧹 CLEAN UP PAPER TRADES FROM LIVE DATABASE")
    print("="*70)
    
    # Get all trades
    all_trades = db.get_all_trades()
    
    print(f"\n📊 Found {len(all_trades)} total trades in database:")
    
    # Show all trades
    paper_trades = []
    live_trades = []
    
    for trade in all_trades:
        trade_info = (
            f"   {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{trade.mode:<6} | {trade.action:<4} | {trade.product_id:<8} | "
            f"£{trade.price:>8.2f} | {trade.crypto_amount:.6f}"
        )
        
        if trade.mode == "PAPER":
            paper_trades.append(trade)
            print(f"{trade_info} ← PAPER")
        else:
            live_trades.append(trade)
            print(f"{trade_info}")
    
    if not paper_trades:
        print(f"\n✅ No paper trades found in database!")
        print(f"   Database is clean - only live trades recorded.")
        db.close()
        return
    
    print(f"\n⚠️  Found {len(paper_trades)} paper trade(s) in LIVE database!")
    print(f"   These should not be in the live database as they can confuse the bot.")
    
    print(f"\n📋 Paper trades to remove:")
    for trade in paper_trades:
        print(f"   - {trade.timestamp.strftime('%H:%M:%S')} | {trade.action} {trade.crypto_amount:.6f} {trade.product_id.split('-')[0]} @ £{trade.price:.2f}")
    
    print(f"\n💡 Removing these will:")
    print(f"   ✅ Prevent bot from trying to manage paper positions")
    print(f"   ✅ Keep database clean with only live trades")
    print(f"   ✅ Avoid confusion between paper and live trading")
    
    confirm = input(f"\nRemove {len(paper_trades)} paper trade(s) from database? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        # Delete paper trades
        for trade in paper_trades:
            db.session.delete(trade)
        
        db.session.commit()
        
        print(f"\n✅ SUCCESS! Removed {len(paper_trades)} paper trade(s)")
        print(f"\n📊 Database now has {len(live_trades)} live trade(s) only:")
        
        for trade in live_trades:
            status = "Open" if trade.profit_loss is None else f"£{trade.profit_loss:+.2f}"
            print(f"   - {trade.timestamp.strftime('%H:%M:%S')} | {trade.action} {trade.crypto_amount:.6f} {trade.product_id.split('-')[0]} @ £{trade.price:.2f} | {status}")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Your 0.033615 ETH is still on Coinbase (ignore it)")
        print(f"   2. Bot will only manage your SOL position")
        print(f"   3. Database is now clean!")
        
    else:
        print(f"\n❌ Cancelled. No changes made.")
    
    db.close()
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        cleanup_paper_trades()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()