from data_layer.market_data import MarketData

def test_data_layer():
    """Test the data layer implementation."""
    
    print("=" * 60)
    print("🧪 Testing Data Layer")
    print("=" * 60)
    
    market = MarketData()
    
    # Get full market snapshot
    snapshot = market.get_full_market_snapshot()
    
    if snapshot:
        print("\n✅ Successfully fetched market data!")
        print("\n" + "=" * 60)
        print("📋 FORMATTED FOR CLAUDE:")
        print("=" * 60)
        print(market.format_for_claude(snapshot))
    else:
        print("\n❌ Failed to fetch market data")

if __name__ == "__main__":
    test_data_layer()