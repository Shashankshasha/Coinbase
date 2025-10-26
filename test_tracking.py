from tracking.trade_logger import TradeLogger
from execution.trade_executor import TradeExecutor

def test_tracking():
    """Test the trade logging and tracking system."""
    
    print("=" * 70)
    print("🧪 Testing Trade Tracking & Logging")
    print("=" * 70)
    
    logger = TradeLogger("test_trading.db")
    executor = TradeExecutor()
    
    # Execute a paper trade
    print("\n📊 Test 1: Execute and log a trade")
    result = executor.execute_trade(
        action="BUY",
        product_id="SOL-GBP",
        confidence=0.85,
        reasoning="Strong bullish signals from technical analysis",
        trade_amount=50.0
    )
    
    if result['executed']:
        logger.log_trade(result)
    
    # Get trade history
    print("\n📊 Test 2: Retrieve trade history")
    trades = logger.get_trade_history(limit=5)
    print(logger.format_trade_history(trades))
    
    # Get performance summary
    print("\n📊 Test 3: Performance summary")
    print(logger.get_performance_summary())
    
    logger.close()

if __name__ == "__main__":
    test_tracking()