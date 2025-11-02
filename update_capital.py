
from data_layer.coinbase_client import CoinbaseClient
import re
import os

print("\n" + "="*70)
print("💰 AUTO CAPITAL UPDATE")
print("="*70)

try:
    cb = CoinbaseClient()
    balances = cb.get_account_balance()
    gbp_balance = balances.get('GBP', 0)
    
    print(f"\n📊 Current Balance: £{gbp_balance:.2f}")
    
    if gbp_balance <= 0:
        print(f"❌ No GBP balance!")
        exit(1)
    
    buffer = 5.0
    trade_amount = max(gbp_balance - buffer, 0)
    
    with open('config.py', 'r') as f:
        config = f.read()
    
    config = re.sub(r'INITIAL_CAPITAL\s*=\s*[\d.]+', f'INITIAL_CAPITAL = {gbp_balance:.2f}', config)
    config = re.sub(r'TRADE_AMOUNT_GBP\s*=\s*[\d.]+', f'TRADE_AMOUNT_GBP = {trade_amount:.2f}', config)
    
    with open('config.py', 'w') as f:
        f.write(config)
    
    print(f"✅ Updated: Capital £{gbp_balance:.2f}, Trade £{trade_amount:.2f}\n")
    
except Exception as e:
    print(f"❌ ERROR: {e}\n")
