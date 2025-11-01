#!/usr/bin/env python3
"""
EMERGENCY BUY - Enter position immediately at market price
Use when you need to manually open a position fast
"""

from execution.order_manager import OrderManager
from data_layer.coinbase_client import CoinbaseClient
from config import TRADING_PAIR, TRADE_AMOUNT_GBP
import sys

def emergency_buy(amount_gbp=None):
    """Buy crypto immediately at market price"""
    
    print("\n" + "="*70)
    print("🚨 EMERGENCY BUY - IMMEDIATE MARKET ENTRY")
    print("="*70)
    
    # Use config default if not specified
    if amount_gbp is None:
        amount_gbp = TRADE_AMOUNT_GBP
    
    # Initialize clients
    cb_client = CoinbaseClient()
    order_mgr = OrderManager()
    
    # Get crypto symbol
    crypto_symbol = TRADING_PAIR.split('-')[0].upper()
    
    print(f"\n📊 Checking GBP balance...")
    
    try:
        # Get current balance
        balances = cb_client.get_account_balance()
        gbp_balance = balances.get('GBP', 0)
        
        print(f"   Available: £{gbp_balance:.2f}")
        
        if gbp_balance < amount_gbp:
            print(f"\n❌ ERROR: Insufficient GBP balance!")
            print(f"   Need: £{amount_gbp:.2f}")
            print(f"   Have: £{gbp_balance:.2f}")
            print(f"   Short: £{amount_gbp - gbp_balance:.2f}")
            return
        
        # Get current price for reference
        price_data = cb_client.get_current_price(TRADING_PAIR)
        current_price = price_data['price']
        estimated_crypto = amount_gbp / current_price
        
        print(f"   Current Price: £{current_price:.2f}")
        print(f"   Estimated Crypto: {estimated_crypto:.6f} {crypto_symbol}")
        
        # Confirmation
        print(f"\n⚠️  YOU ARE ABOUT TO BUY {crypto_symbol}!")
        print(f"   Amount: £{amount_gbp:.2f}")
        print(f"   Pair: {TRADING_PAIR}")
        print(f"   Type: MARKET ORDER (immediate execution)")
        print(f"   Est. Receive: ~{estimated_crypto:.6f} {crypto_symbol}")
        
        confirm = input(f"\n   Type 'BUY NOW' to confirm: ")
        
        if confirm.strip().upper() != 'BUY NOW':
            print("\n❌ Purchase cancelled.")
            return
        
        print(f"\n⚡ EXECUTING EMERGENCY BUY...")
        
        # Execute buy
        result = order_mgr.place_market_buy(TRADING_PAIR, amount_gbp)
        
        if result.get('success'):
            order_id = result.get('order_id', 'unknown')
            
            print(f"\n✅ BUY ORDER EXECUTED!")
            print(f"{'='*70}")
            print(f"   Order ID: {order_id}")
            print(f"   Spent: £{amount_gbp:.2f}")
            print(f"   Pair: {TRADING_PAIR}")
            print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
            print(f"{'='*70}")
            print(f"\n💰 Position opened! Check Coinbase for exact fill details.")
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n❌ BUY FAILED!")
            print(f"   Error: {error}")
            
            if 'raw_response' in result:
                print(f"   Response: {result['raw_response']}")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚨 Emergency Buy Tool")
    print("   Use this to enter a position immediately")
    print("   WARNING: This executes a MARKET order (no price limit)")
    
    # Check if amount specified via command line
    if len(sys.argv) > 1:
        try:
            custom_amount = float(sys.argv[1])
            print(f"   Custom amount: £{custom_amount:.2f}")
            emergency_buy(custom_amount)
        except ValueError:
            print(f"\n❌ Invalid amount: {sys.argv[1]}")
            print(f"   Usage: python emergency_buy.py [amount]")
            print(f"   Example: python emergency_buy.py 100")
    else:
        print(f"   Using default amount: £{TRADE_AMOUNT_GBP:.2f}")
        print(f"   (Or specify: python emergency_buy.py [amount])")
        emergency_buy()
    
    print("\n" + "="*70)
    print("Done.")
    print("="*70 + "\n")