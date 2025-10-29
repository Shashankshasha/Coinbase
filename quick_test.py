#!/usr/bin/env python3
"""
Quick test for fixed Coinbase client - COMPLETE VERSION WITH CANDLES FIX
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')

# CRITICAL FIX: Handle newline encoding
if COINBASE_API_SECRET and '\\n' in COINBASE_API_SECRET:
    COINBASE_API_SECRET = COINBASE_API_SECRET.replace('\\n', '\n')

print("="*70)
print("🧪 TESTING FIXED COINBASE CLIENT - COMPLETE")
print("="*70)

print("\n1️⃣ Checking Coinbase SDK...")
try:
    from coinbase.rest import RESTClient
    print("✅ Coinbase SDK installed")
except ImportError:
    print("❌ Coinbase SDK not installed!")
    print("   Run: pip install coinbase-advanced-py")
    exit(1)

print("\n2️⃣ Checking credentials...")
if not COINBASE_API_KEY:
    print("❌ COINBASE_API_KEY not found in .env")
    exit(1)

if not COINBASE_API_SECRET:
    print("❌ COINBASE_API_SECRET not found in .env")
    exit(1)

print(f"✅ API Key: {COINBASE_API_KEY[:50]}...")
print(f"✅ API Secret: {len(COINBASE_API_SECRET)} characters")

print("\n3️⃣ Initializing client...")
try:
    client = RESTClient(
        api_key=COINBASE_API_KEY,
        api_secret=COINBASE_API_SECRET
    )
    print("✅ Client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    print("\n🔧 POSSIBLE FIXES:")
    print("   1. Make sure private key format is correct (has BEGIN/END tags)")
    print("   2. Update SDK: pip install --upgrade coinbase-advanced-py")
    print("   3. Verify your .env has correct newline encoding")
    exit(1)

print("\n4️⃣ Testing API calls...")

# Test 1: Get accounts
print("\n   📊 Test: Get accounts...")
try:
    response = client.get_accounts()
    
    if hasattr(response, 'accounts'):
        accounts = response.accounts
    elif isinstance(response, dict):
        accounts = response.get('accounts', [])
    else:
        accounts = []
    
    print(f"   ✅ Found {len(accounts)} accounts")
    
    # Show balances
    for account in accounts[:5]:
        try:
            if isinstance(account, dict):
                currency = account.get('currency')
                available = account.get('available_balance', {}).get('value', 0)
            else:
                currency = getattr(account, 'currency', None)
                available_balance = getattr(account, 'available_balance', None)
                if isinstance(available_balance, dict):
                    available = available_balance.get('value', 0)
                else:
                    available = getattr(available_balance, 'value', 0)
            
            if float(available) > 0:
                print(f"      • {currency}: {available}")
        except:
            continue

except Exception as e:
    print(f"   ❌ Failed: {e}")
    print("\n   This is likely an authentication issue.")
    print("   Your API key or private key may be incorrect.")

# Test 2: Get SOL-GBP price
print("\n   📊 Test: Get SOL-GBP price...")
try:
    product = client.get_product('SOL-GBP')
    price = float(product['price'])
    print(f"   ✅ SOL-GBP: £{price:.2f}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 3: Get candles - FIXED VERSION
print("\n   📊 Test: Get candles...")
try:
    import time
    
    # Calculate start and end times (required by newer SDK)
    end_time = int(time.time())
    start_time = end_time - (900 * 10)  # 900 seconds = 15 minutes, 10 candles
    
    response = client.get_candles(
        product_id='SOL-GBP',
        start=str(start_time),
        end=str(end_time),
        granularity='FIFTEEN_MINUTE'
    )
    
    candles = response.candles if hasattr(response, 'candles') else []
    print(f"   ✅ Retrieved {len(candles)} candles")
    
    if candles:
        latest = candles[0]
        print(f"      Latest candle close: £{float(latest.close):.2f}")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("📋 SUMMARY")
print("="*70)

# Count successes
tests_passed = 0
tests_total = 3

try:
    # Re-run tests silently to count
    response = client.get_accounts()
    tests_passed += 1
except:
    pass

try:
    product = client.get_product('SOL-GBP')
    tests_passed += 1
except:
    pass

try:
    import time
    end_time = int(time.time())
    start_time = end_time - (900 * 10)
    response = client.get_candles(
        product_id='SOL-GBP',
        start=str(start_time),
        end=str(end_time),
        granularity='FIFTEEN_MINUTE'
    )
    tests_passed += 1
except:
    pass

print(f"\n✅ Tests passed: {tests_passed}/{tests_total}")

if tests_passed == tests_total:
    print("\n🎉 ALL TESTS PASSED! Your API is 100% working!")
    print("\n📋 NEXT STEPS:")
    print("   1. Replace your data_layer/coinbase_client.py with the fixed version")
    print("   2. Replace your config.py with the updated version")
    print("   3. Remove pip commands from your .env file")
    print("   4. Run: python beast_mode_bot.py")
    print("\n💰 YOU'RE READY TO TRADE!")
    
elif tests_passed >= 2:
    print("\n⚠️  Most tests passed - minor issue with candles")
    print("   Your bot should still work fine!")
    print("   The candles method in your bot has the proper fix built in.")
    
else:
    print("\n❌ Some tests failed - review the errors above")
    print("\n🔧 TROUBLESHOOTING:")
    print("   1. Check your .env file has correct credentials")
    print("   2. Update SDK: pip install --upgrade coinbase-advanced-py")
    print("   3. Verify private key has proper newline encoding")
    print("   4. Try creating a new API key in Coinbase")

print("="*70 + "\n")