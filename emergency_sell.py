#!/usr/bin/env python3
"""
EMERGENCY SELL - Exit position immediately at market price
Use when you need to manually close a position fast
"""

from execution.order_manager import OrderManager
from data_layer.coinbase_client import CoinbaseClient
from config import TRADING_PAIR
import sys

def emergency_sell():
    """Sell entire position immediately at market price"""
    
    print("\n" + "="*70)
    print("🚨 EMERGENCY SELL - IMMEDIATE MARKET EXIT")
    print("="*70)
    
    # Initialize clients
    cb_client = CoinbaseClient()
    order_mgr = OrderManager()
    
    # Get crypto symbol
    crypto_symbol = TRADING_PAIR.split('-')[0].upper()
    
    print(f"\n📊 Checking {crypto_symbol} balance...")
    
    try:
        # Get current balance
        balances = cb_client.get_account_balance()
        crypto_balance = balances.get(crypto_symbol, 0)
        
        if crypto_balance <= 0:
            print(f"\n❌ ERROR: No {crypto_symbol} balance to sell!")
            print(f"   Balance: {crypto_balance}")
            return
        
        print(f"   Balance: {crypto_balance:.6f} {crypto_symbol}")
        
        # Get current price for reference
        price_data = cb_client.get_current_price(TRADING_PAIR)
        current_price = price_data['price']
        estimated_gbp = crypto_balance * current_price
        
        print(f"   Current Price: £{current_price:.2f}")
        print(f"   Estimated Value: £{estimated_gbp:.2f}")
        
        # Confirmation
        print(f"\n⚠️  YOU ARE ABOUT TO SELL ALL {crypto_symbol}!")
        print(f"   Amount: {crypto_balance:.6f} {crypto_symbol}")
        print(f"   Pair: {TRADING_PAIR}")
        print(f"   Type: MARKET ORDER (immediate execution)")
        
        confirm = input(f"\n   Type 'SELL NOW' to confirm: ")
        
        if confirm.strip().upper() != 'SELL NOW':
            print("\n❌ Sale cancelled.")
            return
        
        print(f"\n⚡ EXECUTING EMERGENCY SELL...")
        
        # Execute sell
        result = order_mgr.place_market_sell(TRADING_PAIR, crypto_balance)
        
        if result.get('success'):
            order_id = result.get('order_id', 'unknown')
            sold_amount = result.get('crypto_amount', crypto_balance)
            
            print(f"\n✅ SELL ORDER EXECUTED!")
            print(f"{'='*70}")
            print(f"   Order ID: {order_id}")
            print(f"   Sold: {sold_amount:.6f} {crypto_symbol}")
            print(f"   Pair: {TRADING_PAIR}")
            print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
            print(f"{'='*70}")
            print(f"\n💰 Position closed! Check Coinbase for exact fill price.")
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n❌ SELL FAILED!")
            print(f"   Error: {error}")
            
            if 'raw_response' in result:
                print(f"   Response: {result['raw_response']}")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚨 Emergency Sell Tool")
    print("   Use this to exit your position immediately")
    print("   WARNING: This executes a MARKET order (no price limit)")
    
    emergency_sell()
    
    print("\n" + "="*70)
    print("Done.")
    print("="*70 + "\n")