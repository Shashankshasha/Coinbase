
from execution.order_manager import OrderManager
from data_layer.coinbase_client import CoinbaseClient

print("=" * 70)
print("🧪 TESTING FIXED ORDER MANAGER")
print("=" * 70)

# Initialize
order_mgr = OrderManager()
cb_client = CoinbaseClient()

# Get current SOL balance
print("\n1️⃣ Checking SOL balance...")
try:
    balances = cb_client.get_account_balance()
    sol_balance = balances.get('SOL', 0)
    print(f"   SOL Balance: {sol_balance:.6f}")
    
    if sol_balance == 0:
        print("   ⚠️  No SOL to test with. Trying BUY test instead...")
        
        # Test BUY with £1
        print("\n2️⃣ Testing BUY order (£1.00)...")
        buy_result = order_mgr.place_market_buy("SOL-GBP", 1.00)
        
        if buy_result.get('success'):
            print("   ✅ BUY order works!")
            print(f"   Order ID: {buy_result.get('order_id')}")
        else:
            print(f"   ❌ BUY failed: {buy_result.get('error')}")
        
    else:
        # Test SELL with tiny amount
        test_amount = min(0.001, sol_balance)  # Sell 0.001 SOL or whatever is available
        print(f"\n2️⃣ Testing SELL order ({test_amount:.6f} SOL)...")
        
        sell_result = order_mgr.place_market_sell("SOL-GBP", test_amount)
        
        if sell_result.get('success'):
            print("   ✅ SELL order works!")
            print(f"   Order ID: {sell_result.get('order_id')}")
            print("\n🎉 FIX CONFIRMED: Your bot should now work!")
        else:
            print(f"   ❌ SELL failed: {sell_result.get('error')}")
            print(f"   Error code: {sell_result.get('error_code')}")
            print(f"   Full response: {sell_result.get('raw_response')}")

except Exception as e:
    print(f"   ❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
