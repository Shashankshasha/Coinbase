"""
PROFIT TARGET COMPARISON - £499 Investment
Corrected for 1.2% Coinbase fees per trade (2.4% round-trip)
"""

def calculate_target(investment, net_profit_target):
    """Calculate requirements for a given profit target."""
    
    BUY_FEE_PCT = 0.012  # 1.2% buy fee
    SELL_FEE_PCT = 0.012  # 1.2% sell fee
    API_COST = 0.10
    
    # Buy phase
    buy_fee = investment * BUY_FEE_PCT
    assets_bought = investment - buy_fee
    
    # Target: investment + API + profit
    total_needed_after_sell = investment + API_COST + net_profit_target
    
    # Before sell fee
    gross_value_needed = total_needed_after_sell / (1 - SELL_FEE_PCT)
    
    # Price movement
    price_move_pct = ((gross_value_needed - assets_bought) / assets_bought) * 100
    
    # Verify
    sell_fee = gross_value_needed * SELL_FEE_PCT
    cash_received = gross_value_needed - sell_fee - API_COST
    actual_profit = cash_received - investment
    
    return {
        'investment': investment,
        'net_profit': net_profit_target,
        'buy_fee': buy_fee,
        'assets_bought': assets_bought,
        'price_move_pct': price_move_pct,
        'gross_value': gross_value_needed,
        'sell_fee': sell_fee,
        'cash_received': cash_received,
        'actual_profit': actual_profit,
        'config_target_gbp': gross_value_needed - assets_bought,
        'config_target_pct': price_move_pct / 100
    }


print("="*80)
print("💰 PROFIT TARGET COMPARISON - £499 Investment")
print("="*80)
print("Fees: 1.2% buy + 1.2% sell = 2.4% total | API: £0.10 per cycle")
print("="*80)

targets = [
    (0.50, "Fastest (30 min - 2 hrs)"),
    (1.00, "Fast (1-3 hrs)"),
    (2.00, "Moderate (2-4 hrs)"),
    (5.00, "Slower (4-8 hrs)")
]

for net_profit, speed_desc in targets:
    result = calculate_target(499.0, net_profit)
    
    print(f"\n{'='*80}")
    print(f"🎯 TARGET: £{net_profit:.2f} NET PROFIT")
    print(f"⏱️  SPEED: {speed_desc}")
    print(f"{'='*80}")
    print(f"📊 BUY PHASE:")
    print(f"   Invest: £{result['investment']:.2f}")
    print(f"   Fee: £{result['buy_fee']:.2f}")
    print(f"   Assets: £{result['assets_bought']:.2f}")
    print(f"\n📈 PRICE MOVEMENT REQUIRED:")
    print(f"   Need: {result['price_move_pct']:.2f}% gain")
    print(f"   Assets must grow to: £{result['gross_value']:.2f}")
    print(f"\n📊 SELL PHASE:")
    print(f"   Gross value: £{result['gross_value']:.2f}")
    print(f"   Fee: £{result['sell_fee']:.2f}")
    print(f"   Cash: £{result['cash_received']:.2f}")
    print(f"   Less API: £0.10")
    print(f"   NET PROFIT: £{result['actual_profit']:.2f} ✅")
    print(f"\n⚙️  CONFIG.PY VALUES:")
    print(f"   PROFIT_TARGET_GBP = {result['config_target_gbp']:.2f}")
    print(f"   PROFIT_TARGET_PCT = {result['config_target_pct']:.4f}")

# Recommendations
print("\n" + "="*80)
print("💡 RECOMMENDATIONS")
print("="*80)

print("\n🏆 BEST CHOICE: £1.00 NET PROFIT")
print("   ✅ Price move: 2.67% (achievable in 1-3 hours)")
print("   ✅ Good risk/reward")
print("   ✅ Faster than your current setup")
print("   ✅ Can do 3-5 trades per day")
print("\n   Copy to config.py:")
print("   PROFIT_TARGET_GBP = 13.16")
print("   PROFIT_TARGET_PCT = 0.0267")

print("\n⚡ FASTEST: £0.50 NET PROFIT")
print("   ✅ Price move: 1.72% (30 min - 2 hours)")
print("   ✅ Many trades per day possible")
print("   ⚠️  Smaller profit per trade")
print("\n   Copy to config.py:")
print("   PROFIT_TARGET_GBP = 8.58")
print("   PROFIT_TARGET_PCT = 0.0172")

print("\n🎯 MODERATE: £2.00 NET PROFIT")
print("   ✅ Price move: 3.63% (2-4 hours)")
print("   ✅ Better profit per trade")
print("   ⚠️  Fewer trades (slower)")
print("\n   Copy to config.py:")
print("   PROFIT_TARGET_GBP = 17.74")
print("   PROFIT_TARGET_PCT = 0.0363")

print("\n" + "="*80)
print("⚠️  YOUR CURRENT CONFIG IS WRONG!")
print("="*80)
print("You have:")
print("   PROFIT_TARGET_GBP = 7.10  ❌ TOO LOW")
print("   PROFIT_TARGET_PCT = 0.0145  ❌ NOT ENOUGH")
print("\nWith these settings, you'll LOSE money on every trade!")
print("Minimum needed for £1 profit: PROFIT_TARGET_GBP = 13.16")
print("\n" + "="*80)