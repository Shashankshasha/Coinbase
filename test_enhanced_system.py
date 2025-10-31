"""
TEST SCRIPT: Enhanced Entry System Demo
Run this to see the scoring system in action WITHOUT placing real trades
"""

from enhanced_entry_system import EnhancedEntrySystem
from data_layer.market_data import MarketData
from data_layer.coinbase_client import CoinbaseClient
import time


def test_enhanced_scoring():
    """
    Test the enhanced scoring system with live market data
    """
    print("\n" + "="*70)
    print("🧪 ENHANCED ENTRY SYSTEM - TEST MODE")
    print("="*70)
    print("\nThis will analyze current market conditions using the 100-point")
    print("scoring system WITHOUT placing any trades.\n")
    
    # Initialize systems
    print("Initializing systems...")
    scorer = EnhancedEntrySystem()
    market = MarketData()
    
    product_id = "ETH-GBP"
    
    print(f"✅ Systems ready\n")
    print(f"Target: {product_id}")
    print(f"Minimum score for entry: {scorer.MIN_SCORE}/100")
    print(f"Excellent score threshold: {scorer.EXCELLENT_SCORE}/100\n")
    
    # Get market snapshot
    print("Fetching market data...")
    snapshot = market.get_full_market_snapshot(product_id)
    
    if not snapshot:
        print("❌ Failed to get market data")
        return
    
    print("✅ Market data received\n")
    
    # Show current market conditions
    print("="*70)
    print("📊 CURRENT MARKET CONDITIONS")
    print("="*70)
    print(f"Price: £{snapshot['current_price']:.2f}")
    
    indicators = snapshot.get('indicators', {})
    print(f"RSI: {indicators.get('rsi', 0):.1f}")
    print(f"Volume Ratio: {indicators.get('volume_ratio', 0):.1f}x")
    print(f"EMA Cross: {indicators.get('ema_cross', 'unknown')}")
    print(f"MACD Cross: {indicators.get('macd_cross', 'unknown')}")
    
    # Run enhanced analysis
    print("\n" + "="*70)
    print("🎯 RUNNING ENHANCED ANALYSIS")
    print("="*70)
    print("\nAnalyzing multiple factors...")
    
    analysis = scorer.analyze_entry_opportunity(snapshot, product_id)
    
    # Print full detailed analysis
    scorer.print_detailed_analysis(analysis)
    
    # Show comparison to simple method
    print("="*70)
    print("📈 COMPARISON: Simple vs Enhanced")
    print("="*70)
    
    # Simulate simple method
    simple_conditions = 0
    simple_details = []
    
    rsi = indicators.get('rsi', 50)
    volume_ratio = indicators.get('volume_ratio', 0)
    ema_cross = indicators.get('ema_cross', '')
    macd_cross = indicators.get('macd_cross', '')
    
    if 30 < rsi < 70:
        simple_conditions += 1
        simple_details.append(f"✓ RSI neutral ({rsi:.0f})")
    else:
        simple_details.append(f"✗ RSI not neutral ({rsi:.0f})")
    
    if volume_ratio > 0.8:
        simple_conditions += 1
        simple_details.append(f"✓ Volume OK ({volume_ratio:.1f}x)")
    else:
        simple_details.append(f"✗ Volume low ({volume_ratio:.1f}x)")
    
    if ema_cross == 'bullish':
        simple_conditions += 1
        simple_details.append("✓ EMA bullish")
    else:
        simple_details.append("✗ EMA not bullish")
    
    if macd_cross == 'bullish':
        simple_conditions += 1
        simple_details.append("✓ MACD bullish")
    else:
        simple_details.append("✗ MACD not bullish")
    
    simple_would_enter = simple_conditions >= 3
    
    print("\n🔵 SIMPLE METHOD (Original):")
    print(f"   Conditions met: {simple_conditions}/4")
    for detail in simple_details:
        print(f"   {detail}")
    print(f"   Decision: {'✅ ENTER' if simple_would_enter else '❌ SKIP'}")
    
    print("\n🟢 ENHANCED METHOD (New):")
    print(f"   Score: {analysis['score']}/100 ({analysis['quality']})")
    print(f"   Confidence: {analysis['confidence']*100:.1f}%")
    print(f"   Decision: {'✅ ENTER' if analysis['should_enter'] else '❌ SKIP'}")
    
    # Show if decisions differ
    if simple_would_enter != analysis['should_enter']:
        print(f"\n⚠️  DECISIONS DIFFER!")
        if analysis['should_enter']:
            print("   Enhanced method found a better opportunity that simple method missed")
        else:
            print("   Enhanced method filtered out a weak setup that simple method would take")
    else:
        print(f"\n✅ Both methods agree")
    
    print("\n" + "="*70)
    print("💡 KEY INSIGHTS")
    print("="*70)
    
    # Analyze what's strong/weak
    breakdown = analysis['breakdown']
    
    strongest = max(breakdown.items(), key=lambda x: x[1]['score'] / x[1]['max'])
    weakest = min(breakdown.items(), key=lambda x: x[1]['score'] / x[1]['max'])
    
    strongest_pct = (strongest[1]['score'] / strongest[1]['max']) * 100
    weakest_pct = (weakest[1]['score'] / weakest[1]['max']) * 100
    
    print(f"\n🏆 Strongest factor: {strongest[0].replace('_', ' ').title()}")
    print(f"   Score: {strongest[1]['score']}/{strongest[1]['max']} ({strongest_pct:.0f}%)")
    print(f"   {strongest[1]['details']}")
    
    print(f"\n⚠️  Weakest factor: {weakest[0].replace('_', ' ').title()}")
    print(f"   Score: {weakest[1]['score']}/{weakest[1]['max']} ({weakest_pct:.0f}%)")
    print(f"   {weakest[1]['details']}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if analysis['should_enter']:
        if analysis['score'] >= scorer.EXCELLENT_SCORE:
            print("   🎯 EXCELLENT setup! Strong entry with high confidence.")
            print("   → Consider slightly larger position size")
        else:
            print("   ✅ GOOD setup. Entry conditions met.")
            print("   → Proceed with normal position size")
    else:
        # Suggest what to wait for
        if weakest_pct < 30:
            print(f"   Wait for improvement in: {weakest[0].replace('_', ' ').title()}")
            print(f"   Current: {weakest_pct:.0f}% | Target: >50%")
        
        score_needed = scorer.MIN_SCORE - analysis['score']
        print(f"\n   Need {score_needed} more points to reach threshold")
        print("   → Be patient and wait for better setup")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
    print("\nTo run live: python beast_mode_bot_optimized.py")
    print("(Make sure to update imports first - see INTEGRATION_GUIDE.md)\n")


def continuous_monitoring(interval_seconds=300):
    """
    Continuously monitor and score market conditions
    Useful for seeing how scores change over time
    """
    print("\n" + "="*70)
    print("📡 CONTINUOUS MONITORING MODE")
    print("="*70)
    print(f"\nWill check market every {interval_seconds} seconds")
    print("Press Ctrl+C to stop\n")
    
    scorer = EnhancedEntrySystem()
    market = MarketData()
    product_id = "ETH-GBP"
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            print(f"\n{'='*70}")
            print(f"🔄 Cycle {cycle} - {time.strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            
            snapshot = market.get_full_market_snapshot(product_id)
            
            if snapshot:
                analysis = scorer.analyze_entry_opportunity(snapshot, product_id)
                
                # Compact output
                print(f"\n💰 Price: £{snapshot['current_price']:.2f}")
                print(f"📊 Score: {analysis['score']}/100 ({analysis['quality']})")
                print(f"🎯 Decision: {'✅ ENTER' if analysis['should_enter'] else '❌ SKIP'}")
                print(f"💡 {analysis['reason']}")
                
                # Show score change if we have history
                if cycle > 1:
                    # You could track score history here
                    pass
            else:
                print("⚠️ Failed to get market data")
            
            print(f"\n⏱️  Next check in {interval_seconds} seconds...")
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
        print(f"Completed {cycle} cycles")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🧪 ENHANCED ENTRY SYSTEM - TEST SUITE")
    print("="*70)
    print("\nChoose test mode:")
    print("1. Single analysis (test once and exit)")
    print("2. Continuous monitoring (check every 5 minutes)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_enhanced_scoring()
    elif choice == "2":
        print("\nHow often to check? (seconds)")
        try:
            interval = int(input("Enter interval (default 300): ").strip() or "300")
        except:
            interval = 300
        continuous_monitoring(interval)
    else:
        print("\nExiting...")
    
    print("\n")