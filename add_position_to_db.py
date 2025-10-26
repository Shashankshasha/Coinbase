from tracking.database import TradingDatabase
from data_layer.market_data import MarketData
from datetime import datetime

def add_orphaned_position():
    """
    Manually add the orphaned SOL position to the database.
    This will make it visible in monitoring scripts.
    
    Run once: python add_position_to_db.py
    """
    
    db = TradingDatabase("trading_bot.db")
    market = MarketData()
    
    print("\n" + "="*70)
    print("🔧 ADDING ORPHANED POSITION TO DATABASE")
    print("="*70)
    
    # Configuration for your SOL position
    PRODUCT_ID = "SOL-GBP"
    
    # Get current balance from Coinbase
    snapshot = market.get_full_market_snapshot(PRODUCT_ID)
    crypto_symbol = PRODUCT_ID.split('-')[0]
    actual_balance = snapshot['balances'].get(crypto_symbol, 0)
    current_price = snapshot['current_price']
    
    print(f"\n📊 Detected on Coinbase:")
    print(f"   Amount: {actual_balance:.6f} {crypto_symbol}")
    print(f"   Current Price: £{current_price:.2f}")
    
    # Check if already in DB
    existing = db.get_open_position(PRODUCT_ID)
    if existing:
        print(f"\n⚠️  Position already exists in database!")
        print(f"   Entry: £{existing.price:.2f}")
        print(f"   Amount: {existing.crypto_amount:.6f} {crypto_symbol}")
        print(f"\n❌ Nothing to do. Database is already updated.")
        return
    
    # Prompt user for entry details
    print(f"\n💡 We need your actual entry details.")
    print(f"   Check your Coinbase order history for the BUY order that created this position.\n")
    
    # Option 1: User provides entry
    print("Choose an option:")
    print("1. Enter exact entry price (if you know it)")
    print("2. Use current price as break-even entry (£{:.2f})".format(current_price))
    print("3. Cancel")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        # User enters exact entry
        try:
            entry_price_input = input(f"Enter exact entry price (e.g., 146.79): £")
            entry_price = float(entry_price_input)
            
            amount_gbp_input = input(f"Enter exact amount spent in GBP (e.g., 144.00): £")
            amount_gbp = float(amount_gbp_input)
            
            print(f"\n✅ Using manual entry:")
            print(f"   Price: £{entry_price:.2f}")
            print(f"   Cost: £{amount_gbp:.2f}")
            print(f"   Amount: {actual_balance:.6f} {crypto_symbol}")
            
        except ValueError:
            print("\n❌ Invalid input. Cancelled.")
            return
            
    elif choice == "2":
        # Use current price as break-even
        entry_price = current_price
        amount_gbp = actual_balance * current_price
        
        print(f"\n✅ Using break-even entry:")
        print(f"   Price: £{entry_price:.2f} (current)")
        print(f"   Cost: £{amount_gbp:.2f} (estimated)")
        print(f"   Amount: {actual_balance:.6f} {crypto_symbol}")
        
    else:
        print("\n❌ Cancelled.")
        return
    
    # Calculate fee (0.6%)
    fee = amount_gbp * 0.006
    
    # Confirm before adding
    print(f"\n⚠️  Ready to add to database:")
    print(f"   Product: {PRODUCT_ID}")
    print(f"   Action: BUY")
    print(f"   Entry Price: £{entry_price:.2f}")
    print(f"   Amount: {actual_balance:.6f} {crypto_symbol}")
    print(f"   Cost: £{amount_gbp:.2f}")
    print(f"   Fee: £{fee:.2f}")
    
    confirm = input(f"\nAdd this position to database? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        # Add to database
        trade_data = {
            'product_id': PRODUCT_ID,
            'action': 'BUY',
            'price': entry_price,
            'crypto_amount': actual_balance,
            'amount_gbp': amount_gbp,
            'fee': fee,
            'confidence': 0.0,  # Unknown
            'reasoning': 'Orphaned position - manually added to database'
        }
        
        db.record_trade(
            product_id=PRODUCT_ID,
            action='BUY',
            price=entry_price,
            crypto_amount=actual_balance,
            amount_gbp=amount_gbp,
            fee=fee
        )
        
        print(f"\n✅ SUCCESS! Position added to database!")
        print(f"\n📊 Monitoring scripts will now show:")
        print(f"   - This position in check_pnl.py")
        print(f"   - Live tracking in live_dashboard.py")
        print(f"   - Accurate profit targets")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Run: python check_pnl.py")
        print(f"   2. Run: python live_dashboard.py")
        print(f"   3. Let beast_mode_bot.py keep running")
        
    else:
        print(f"\n❌ Cancelled. Database not modified.")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        add_orphaned_position()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()