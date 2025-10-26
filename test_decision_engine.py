from decision_engine.validator import DecisionValidator

def test_decision_engine():
    """Test the decision validation system."""
    
    print("=" * 60)
    print("🧪 Testing Decision Engine")
    print("=" * 60)
    
    validator = DecisionValidator()
    
    # Test 1: Valid trade
    print("\n📊 Test 1: Valid BUY trade with high confidence")
    validation = validator.validate_trade(
        action="BUY",
        product_id="SOL-GBP",
        confidence=0.85,
        trade_amount=50.0,
        available_balance=100.0
    )
    print(validator.format_validation_report(validation))
    
    # Test 2: Low confidence
    print("\n📊 Test 2: Low confidence trade")
    validation = validator.validate_trade(
        action="BUY",
        product_id="SOL-GBP",
        confidence=0.50,
        trade_amount=50.0,
        available_balance=100.0
    )
    print(validator.format_validation_report(validation))
    
    # Test 3: Insufficient balance
    print("\n📊 Test 3: Insufficient balance")
    validation = validator.validate_trade(
        action="BUY",
        product_id="SOL-GBP",
        confidence=0.85,
        trade_amount=150.0,
        available_balance=100.0
    )
    print(validator.format_validation_report(validation))
    
    # Test 4: Cooldown (simulate recent trade)
    print("\n📊 Test 4: Cooldown check (after recording a trade)")
    validator.record_execution("SOL-GBP", "BUY", 0.017, 2970.0)
    validation = validator.validate_trade(
        action="SELL",
        product_id="SOL-GBP",
        confidence=0.85,
        trade_amount=50.0,
        available_balance=100.0
    )
    print(validator.format_validation_report(validation))

if __name__ == "__main__":
    test_decision_engine()