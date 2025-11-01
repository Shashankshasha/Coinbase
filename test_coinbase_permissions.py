#!/usr/bin/env python3
from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET
import time

# Fix newlines in private key
api_secret = COINBASE_API_SECRET.replace('\\n', '\n')

print("=" * 70)
print("🔍 COINBASE API PERMISSIONS TEST")
print("=" * 70)

client = RESTClient(api_key=COINBASE_API_KEY, api_secret=api_secret)

# Test BUY
print("\nTesting BUY order (£0.50)...")
try:
    order = client.market_order_buy(
        client_order_id=f"test_{int(time.time())}",
        product_id="SOL-GBP",
        quote_size="0.50"
    )
    print("✅ BUY works!")
except Exception as e:
    print(f"❌ BUY failed: {e}")

# Test SELL  
print("\nTesting SELL order (0.001 SOL)...")
try:
    order = client.market_order_sell(
        client_order_id=f"test_{int(time.time())}",
        product_id="SOL-GBP",
        base_size="0.001"
    )
    print("✅ SELL works!")
except Exception as e:
    print(f"❌ SELL failed: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)