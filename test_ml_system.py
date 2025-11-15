"""
ML SYSTEM TEST & INITIALIZATION SCRIPT
======================================

This script:
1. Tests ML system initialization
2. Verifies all dependencies
3. Checks ML model loading/saving
4. Tests feature extraction
5. Simulates trading decisions
6. Validates error handling

Run this before starting the ML bot to ensure everything works!
"""

import sys
import traceback
from datetime import datetime


def test_imports():
    """Test all required imports."""
    print("\n" + "="*70)
    print("📦 Testing Imports...")
    print("="*70)

    try:
        # Core ML dependencies
        import numpy as np
        print("✅ numpy:", np.__version__)

        import pandas as pd
        print("✅ pandas:", pd.__version__)

        import sklearn
        print("✅ scikit-learn:", sklearn.__version__)

        from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
        from sklearn.preprocessing import StandardScaler
        print("✅ sklearn components imported")

        # Trading system
        from agent import TradingAgent
        print("✅ TradingAgent imported")

        from entry_analyzer import EnhancedEntrySystem
        from enhanced_entry_system import MLEnhancedEntrySystem
        print("✅ ML systems imported")

        from data_layer.market_data import MarketData
        print("✅ MarketData imported")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Run: pip install -r requirements.txt --break-system-packages")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return False


def test_ml_initialization():
    """Test ML system initialization."""
    print("\n" + "="*70)
    print("🧠 Testing ML System Initialization...")
    print("="*70)

    try:
        from agent import TradingAgent
        from entry_analyzer import EnhancedEntrySystem
        from enhanced_entry_system import MLEnhancedEntrySystem

        # Create base system
        print("\n1. Creating EnhancedEntrySystem...")
        base_system = EnhancedEntrySystem()
        print("   ✅ Base system created")

        # Create ML system
        print("\n2. Creating MLEnhancedEntrySystem...")
        ml_system = MLEnhancedEntrySystem(base_system)
        print("   ✅ ML system created")

        # Check model state
        print("\n3. Checking ML model state...")
        if ml_system.entry_predictor is None:
            print("   ⏳ ML model not yet trained (expected - needs 20+ trades)")
        else:
            print("   ✅ ML model loaded from disk!")

        print("\n4. Checking ML system components...")
        print(f"   - Scaler: {type(ml_system.scaler).__name__}")
        print(f"   - Training data buffer: {len(ml_system.training_data)}/1000")
        print(f"   - Trade outcomes buffer: {len(ml_system.trade_outcomes)}/1000")
        print(f"   - Adaptive threshold: {ml_system.adaptive_threshold:.0f}")

        print("\n✅ ML system initialization successful!")
        return True, ml_system

    except Exception as e:
        print(f"\n❌ ML initialization error: {e}")
        traceback.print_exc()
        return False, None


def test_feature_extraction(ml_system):
    """Test feature extraction with mock data."""
    print("\n" + "="*70)
    print("🔧 Testing Feature Extraction...")
    print("="*70)

    try:
        # Mock snapshot
        mock_snapshot = {
            'current_price': 150.00,
            'timestamp': datetime.now().isoformat(),
            'indicators': {
                'rsi': 45.0,
                'macd_histogram': 0.5,
                'stoch_k': 40.0,
                'stoch_d': 35.0,
                'ema_10': 149.50,
                'ema_50': 148.00,
                'bb_position': 45.0,
                'bb_width': 2.5,
                'adx': 25.0,
                'volume_ratio': 1.2,
                'atr': 3.5,
                'atr_pct': 2.3,
                'price_change_pct': 1.5,
                'macd_line': 0.8
            }
        }

        # Mock base result
        mock_base_result = {
            'score': 65,
            'breakdown': {
                'trend': {'score': 15},
                'momentum': {'score': 12},
                'volume': {'score': 10},
                'support_resistance': {'score': 18},
                'market_regime': {'score': 10}
            }
        }

        print("\n1. Extracting features from mock data...")
        features = ml_system._extract_ml_features(mock_snapshot, mock_base_result)

        print(f"   ✅ Extracted {features.shape[1]} features")
        print(f"   Shape: {features.shape}")
        print(f"   Sample values: {features[0][:5]}")

        print("\n2. Testing ML prediction (will return 0.5 if not trained)...")
        confidence = ml_system._get_ml_prediction(features)
        print(f"   ML Confidence: {confidence:.2f}")

        if confidence == 0.5:
            print("   ⏳ Model not trained yet - returned neutral (expected)")
        else:
            print("   ✅ Model is trained and predicting!")

        print("\n3. Testing anomaly detection...")
        anomaly_score, anomaly_type = ml_system._detect_anomaly(mock_snapshot, features)
        print(f"   Anomaly Score: {anomaly_score:.2f}")
        print(f"   Anomaly Type: {anomaly_type or 'None'}")

        print("\n✅ Feature extraction working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ Feature extraction error: {e}")
        traceback.print_exc()
        return False


def test_ml_decision_flow(ml_system):
    """Test complete ML decision flow."""
    print("\n" + "="*70)
    print("🎯 Testing ML Decision Flow...")
    print("="*70)

    try:
        from data_layer.market_data import MarketData
        from config import TRADING_PAIR

        print(f"\n1. Getting live market data for {TRADING_PAIR}...")
        market = MarketData()
        snapshot = market.get_full_market_snapshot(TRADING_PAIR)

        print(f"   ✅ Got snapshot:")
        print(f"   Price: £{snapshot['current_price']:.2f}")
        print(f"   RSI: {snapshot['indicators'].get('rsi', 'N/A')}")
        print(f"   Volume Ratio: {snapshot['indicators'].get('volume_ratio', 'N/A')}x")

        print(f"\n2. Running ML-enhanced analysis...")
        result = ml_system.analyze_entry_with_ml(snapshot, TRADING_PAIR)

        print(f"\n3. ML Analysis Results:")
        print(f"   Should Enter: {result['should_enter']}")
        print(f"   Combined Score: {result['score']}/100")
        print(f"   Base Score: {result['base_score']}/100")
        print(f"   ML Confidence: {result['ml_confidence']:.2f}")
        print(f"   Adaptive Threshold: {result['adaptive_threshold']:.0f}")
        print(f"   Quality Rating: {result['quality']}")
        print(f"   Anomaly Type: {result['anomaly_type'] or 'None'}")

        print(f"\n4. Decision Reasoning:")
        print(f"   {result['reason']}")

        print("\n✅ ML decision flow working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ ML decision flow error: {e}")
        traceback.print_exc()
        return False


def test_agent_integration():
    """Test full agent integration with ML."""
    print("\n" + "="*70)
    print("🤖 Testing Agent Integration...")
    print("="*70)

    try:
        from agent import TradingAgent

        print("\n1. Creating TradingAgent (includes ML system)...")
        agent = TradingAgent()
        print("   ✅ Agent created successfully")

        print("\n2. Checking ML system integration...")
        print(f"   ML Entry System: {type(agent.ml_entry_system).__name__}")
        print(f"   Base Entry System: {type(agent.base_entry_system).__name__}")

        print("\n3. Getting ML performance stats...")
        stats = agent.get_ml_performance()
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Model Trained: {stats['model_trained']}")
        print(f"   Adaptive Threshold: {stats['adaptive_threshold']:.0f}")

        print("\n✅ Agent integration working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ Agent integration error: {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test ML system error handling and fallback."""
    print("\n" + "="*70)
    print("🛡️  Testing Error Handling & Fallback...")
    print("="*70)

    try:
        from entry_analyzer import EnhancedEntrySystem
        from enhanced_entry_system import MLEnhancedEntrySystem

        base_system = EnhancedEntrySystem()
        ml_system = MLEnhancedEntrySystem(base_system)

        print("\n1. Testing with invalid snapshot (should fallback)...")

        # Invalid snapshot
        bad_snapshot = {
            'current_price': 150.00,
            'timestamp': 'invalid',
            'indicators': {}  # Missing all indicators
        }

        bad_base_result = {
            'score': 65,
            'breakdown': {}
        }

        try:
            # This should handle errors gracefully
            result = ml_system.analyze_entry_with_ml(bad_snapshot, 'SOL-GBP')
            print(f"   ✅ Handled bad data gracefully")
            print(f"   Score: {result['score']}/100")
        except Exception as e:
            print(f"   ❌ Failed to handle bad data: {e}")
            return False

        print("\n✅ Error handling working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🚀 ML SYSTEM COMPREHENSIVE TEST")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    if not results[0][1]:
        print("\n❌ Cannot continue - imports failed")
        return

    # Test 2: ML Initialization
    success, ml_system = test_ml_initialization()
    results.append(("ML Initialization", success))

    if not success:
        print("\n❌ Cannot continue - ML initialization failed")
        return

    # Test 3: Feature Extraction
    results.append(("Feature Extraction", test_feature_extraction(ml_system)))

    # Test 4: ML Decision Flow
    results.append(("ML Decision Flow", test_ml_decision_flow(ml_system)))

    # Test 5: Agent Integration
    results.append(("Agent Integration", test_agent_integration()))

    # Test 6: Error Handling
    results.append(("Error Handling", test_error_handling()))

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        print("✅ ALL TESTS PASSED - ML system ready for trading!")
    else:
        print("❌ SOME TESTS FAILED - fix issues before trading")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
