from execution.trade_executor import TradeExecutor

def test_trade_execution():
    """Test the trade execution system."""
    
    print("=" * 60)
    print("🧪 Testing Trade Execution")
    print("=" * 60)
    
    executor = TradeExecutor()
    
    # Test 1: Execute a paper trade
    print("\n📊 Test 1: Execute paper BUY trade")
    result = executor.execute_trade(
        action="BUY",
        product_id="SOL-GBP",
        confidence=0.85,
        reasoning="Strong bullish signals: RSI neutral, EMA bullish cross, MACD positive",
        trade_amount=50.0
    )
    
    print(f"\nResult: {result['success']}")
    if result.get('executed'):
        print(f"Trade ID: {result.get('trade_id')}")
        print(f"Crypto Amount: {result.get('crypto_amount', 0):.6f}")
    
    # Test 2: Try another trade (should fail cooldown)
    print("\n\n📊 Test 2: Try immediate second trade (cooldown test)")
    result2 = executor.execute_trade(
        action="SELL",
        product_id="SOL-GBP",
        confidence=0.80,
        reasoning="Taking profit",
        trade_amount=50.0
    )
    
    print(f"\nResult: {result2['success']}")
    print(f"Executed: {result2.get('executed', False)}")
    
    # Show all paper trades
    print("\n\n📋 All Paper Trades:")
    print("=" * 60)
    for trade in executor.get_paper_trades():
        print(f"{trade['action']} {trade['crypto_amount']:.6f} {trade['product_id']} @ £{trade['price']:.2f}")
        print(f"   Trade ID: {trade['trade_id']}")
        print(f"   Confidence: {trade['confidence']:.0%}")
        print()

if __name__ == "__main__":
    test_trade_execution()