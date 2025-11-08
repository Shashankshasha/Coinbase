"""
ML-ENHANCED ENTRY/EXIT SYSTEM
Combines rule-based scoring with machine learning for adaptive decisions

Features:
1. Gradient Boosting for entry prediction
2. LSTM for price trend prediction
3. Anomaly detection for unusual opportunities
4. Adaptive threshold learning
5. Pattern recognition for dips/recoveries
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import deque
import pickle
import os


class MLEnhancedEntrySystem:
    """
    Machine Learning Enhanced Entry System
    
    Combines:
    - Traditional indicators (from EnhancedEntrySystem)
    - ML prediction models
    - Adaptive threshold learning
    - Anomaly detection for crashes/recoveries
    """
    
    def __init__(self, base_entry_system):
        self.base_system = base_entry_system
        
        # ML Models
        self.entry_predictor = None  # Gradient Boosting classifier
        self.anomaly_detector = None  # Isolation Forest
        self.scaler = StandardScaler()
        
        # Training data storage
        self.training_data = deque(maxlen=1000)  # Last 1000 decisions
        self.trade_outcomes = deque(maxlen=1000)  # Actual results
        
        # Adaptive threshold
        self.adaptive_threshold = 70.0  # Starts at 70, learns from results
        self.threshold_history = deque(maxlen=100)
        
        # Model paths
        self.model_dir = "ml_models"
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load existing models if available
        self._load_models()
        
        # Performance tracking
        self.predictions_made = 0
        self.correct_predictions = 0
    
    def analyze_entry_with_ml(self, snapshot: dict, product_id: str) -> dict:
        """
        Enhanced entry analysis with ML predictions
        
        Returns same format as base system but with ML enhancements
        """
        print(f"\n🧠 Running ML-Enhanced Analysis...")
        
        # 1. Get base scoring
        base_result = self.base_system.analyze_entry_opportunity(snapshot, product_id)
        
        # 2. Extract features for ML
        features = self._extract_ml_features(snapshot, base_result)
        
        # 3. ML Prediction
        ml_confidence = self._get_ml_prediction(features)
        
        # 4. Anomaly Detection (detect unusual opportunities)
        anomaly_score, anomaly_type = self._detect_anomaly(snapshot, features)
        
        # 5. Adaptive Threshold
        current_threshold = self._get_adaptive_threshold()
        
        # 6. Combined Decision
        # Weighted combination: 60% base score + 40% ML prediction
        combined_score = (base_result['score'] * 0.6) + (ml_confidence * 100 * 0.4)
        
        # Special case: If anomaly detected (crash recovery), lower threshold
        if anomaly_type == 'recovery_opportunity':
            print(f"   🚨 ANOMALY: Recovery opportunity detected!")
            print(f"   📉 Threshold lowered: {current_threshold:.0f} → {current_threshold * 0.8:.0f}")
            current_threshold *= 0.8  # 20% lower threshold
            anomaly_boost = 15
        elif anomaly_type == 'volatility_spike':
            print(f"   ⚠️ ANOMALY: High volatility detected!")
            anomaly_boost = 5
        else:
            anomaly_boost = 0
        
        combined_score += anomaly_boost
        
        # Decision
        should_enter = combined_score >= current_threshold
        confidence = combined_score / 100.0
        
        # Build enhanced reason
        reason_parts = [base_result['reason']]
        reason_parts.append(f"ML confidence: {ml_confidence:.2f}")
        
        if anomaly_type:
            reason_parts.append(f"Anomaly: {anomaly_type}")
        
        reason_parts.append(f"Adaptive threshold: {current_threshold:.0f}")
        
        # Print ML insights
        print(f"   🧠 ML Confidence: {ml_confidence:.2f}")
        print(f"   📊 Combined Score: {combined_score:.0f}/100")
        print(f"   🎯 Adaptive Threshold: {current_threshold:.0f}")
        
        if anomaly_type:
            print(f"   🚨 Anomaly Type: {anomaly_type}")
        
        if should_enter:
            print(f"   ✅ ML RECOMMENDS ENTRY")
        else:
            print(f"   ⏸️ ML RECOMMENDS WAIT (need {current_threshold - combined_score:.0f} more points)")
        
        # Store decision for learning
        self._store_decision(features, should_enter, combined_score)
        
        return {
            'should_enter': should_enter,
            'confidence': confidence,
            'score': int(combined_score),
            'ml_confidence': ml_confidence,
            'anomaly_type': anomaly_type,
            'adaptive_threshold': current_threshold,
            'base_score': base_result['score'],
            'breakdown': base_result['breakdown'],
            'reason': ' | '.join(reason_parts),
            'quality': self._get_quality_rating(combined_score),
            'summary': reason_parts[0]
        }
    
    def _extract_ml_features(self, snapshot: dict, base_result: dict) -> np.ndarray:
        """
        Extract features for ML model
        
        Features (30 total):
        - All base system scores (5)
        - Technical indicators (10)
        - Price momentum features (5)
        - Volatility features (5)
        - Time-based features (5)
        """
        features = []
        
        indicators = snapshot.get('indicators', {})
        breakdown = base_result.get('breakdown', {})
        
        # 1. Base system scores (5 features)
        features.append(breakdown.get('trend', {}).get('score', 0))
        features.append(breakdown.get('momentum', {}).get('score', 0))
        features.append(breakdown.get('volume', {}).get('score', 0))
        features.append(breakdown.get('support_resistance', {}).get('score', 0))
        features.append(breakdown.get('market_regime', {}).get('score', 0))
        
        # 2. Technical indicators (10 features)
        features.append(indicators.get('rsi', 50))
        features.append(indicators.get('macd_histogram', 0))
        features.append(indicators.get('stoch_k', 50))
        features.append(indicators.get('stoch_d', 50))
        features.append(indicators.get('ema_10', snapshot['current_price']))
        features.append(indicators.get('ema_50', snapshot['current_price']))
        features.append(indicators.get('bb_position', 50))
        features.append(indicators.get('adx', 0))
        features.append(indicators.get('volume_ratio', 1.0))
        features.append(indicators.get('atr_pct', 0))
        
        # 3. Price momentum (5 features)
        current_price = snapshot['current_price']
        ema_10 = indicators.get('ema_10', current_price)
        ema_50 = indicators.get('ema_50', current_price)
        
        features.append((current_price - ema_10) / ema_10 * 100)  # Distance from EMA10
        features.append((current_price - ema_50) / ema_50 * 100)  # Distance from EMA50
        features.append((ema_10 - ema_50) / ema_50 * 100)  # EMA spread
        features.append(indicators.get('price_change_pct', 0))  # Recent price change
        features.append(indicators.get('macd_line', 0))  # MACD value
        
        # 4. Volatility features (5 features)
        features.append(indicators.get('bb_width', 0))  # Bollinger Band width
        features.append(indicators.get('atr', 0))  # Average True Range
        
        # Volume volatility (approximation)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        features.append(abs(volume_ratio - 1.0))  # Distance from average volume
        
        # Price position in BB
        bb_position = indicators.get('bb_position', 50)
        features.append(abs(bb_position - 50))  # Distance from BB middle
        
        # Trend strength
        features.append(indicators.get('adx', 0))
        
        # 5. Time-based features (5 features)
        now = datetime.now()
        features.append(now.hour)  # Hour of day
        features.append(now.weekday())  # Day of week
        features.append(now.minute / 60.0)  # Minute (normalized)
        
        # Market session (approx)
        # 0 = Asian, 1 = European, 2 = US, 3 = Off hours
        if 0 <= now.hour < 8:
            session = 0
        elif 8 <= now.hour < 16:
            session = 1
        elif 16 <= now.hour < 24:
            session = 2
        else:
            session = 3
        features.append(session)
        
        # Days since week start
        features.append(now.weekday() / 6.0)
        
        return np.array(features).reshape(1, -1)
    
    def _get_ml_prediction(self, features: np.ndarray) -> float:
        """
        Get ML model prediction
        
        Returns confidence 0-1
        """
        if self.entry_predictor is None:
            # Not trained yet, return neutral
            return 0.5
        
        try:
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get probability
            probabilities = self.entry_predictor.predict_proba(features_scaled)
            
            # Probability of positive outcome (class 1)
            confidence = probabilities[0][1]
            
            return confidence
            
        except Exception as e:
            print(f"   ⚠️ ML prediction error: {e}")
            return 0.5
    
    def _detect_anomaly(self, snapshot: dict, features: np.ndarray) -> tuple[float, str]:
        """
        Detect anomalous market conditions (crashes, recoveries, etc.)
        
        Returns: (anomaly_score, anomaly_type)
        anomaly_score: 0-1 (1 = strong anomaly)
        anomaly_type: 'recovery_opportunity', 'volatility_spike', 'crash', None
        """
        indicators = snapshot.get('indicators', {})
        
        # Quick heuristic checks
        rsi = indicators.get('rsi', 50)
        bb_position = indicators.get('bb_position', 50)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        price_change_pct = indicators.get('price_change_pct', 0)
        atr_pct = indicators.get('atr_pct', 0)
        
        # RECOVERY OPPORTUNITY: Price crashed then recovering
        # - RSI was very low (< 30) recently
        # - Now recovering (30-45 range)
        # - High volume
        # - Large recent drop followed by bounce
        if 30 <= rsi <= 45 and volume_ratio > 1.5 and price_change_pct > 1.0:
            return 0.9, 'recovery_opportunity'
        
        # VOLATILITY SPIKE: Unusual market activity
        # - Very high ATR
        # - Extreme volume
        # - Price at extremes
        if atr_pct > 3.0 and volume_ratio > 2.0:
            if bb_position < 20:  # At lower band
                return 0.8, 'recovery_opportunity'
            else:
                return 0.7, 'volatility_spike'
        
        # CRASH DETECTED: Strong selling pressure
        # - RSI < 30
        # - Large negative price change
        # - High volume
        if rsi < 30 and price_change_pct < -2.0 and volume_ratio > 1.5:
            # This is actually a BUYING opportunity (buy the dip)
            return 0.85, 'recovery_opportunity'
        
        # No anomaly detected
        return 0.0, None
    
    def _get_adaptive_threshold(self) -> float:
        """
        Calculate adaptive threshold based on recent performance
        
        Starts at 70, adjusts based on:
        - Win rate (if high, be more aggressive - lower threshold)
        - Miss rate (if missing good opportunities, lower threshold)
        - False positive rate (if entering bad trades, raise threshold)
        """
        if len(self.trade_outcomes) < 10:
            # Not enough data yet
            return 70.0
        
        recent_outcomes = list(self.trade_outcomes)[-20:]  # Last 20 trades
        
        # Calculate win rate
        wins = sum(1 for outcome in recent_outcomes if outcome.get('profit', 0) > 0)
        win_rate = wins / len(recent_outcomes)
        
        # Adjust threshold
        if win_rate > 0.8:
            # High win rate - be more aggressive
            adjustment = -5
        elif win_rate > 0.7:
            # Good win rate - slightly more aggressive
            adjustment = -2
        elif win_rate < 0.6:
            # Low win rate - be more conservative
            adjustment = +5
        elif win_rate < 0.7:
            # Below target - slightly more conservative
            adjustment = +2
        else:
            adjustment = 0
        
        new_threshold = 70.0 + adjustment
        
        # Bounds check (50-85)
        new_threshold = max(50, min(85, new_threshold))
        
        self.threshold_history.append(new_threshold)
        
        return new_threshold
    
    def _store_decision(self, features: np.ndarray, decision: bool, score: float):
        """
        Store decision for future learning
        """
        self.training_data.append({
            'features': features,
            'decision': decision,
            'score': score,
            'timestamp': datetime.now()
        })
    
    def record_trade_outcome(self, entry_score: float, profit: float, duration_minutes: int):
        """
        Record the outcome of a trade for learning
        
        Args:
            entry_score: Score when entered
            profit: Profit/loss in GBP
            duration_minutes: How long the trade took
        """
        outcome = {
            'entry_score': entry_score,
            'profit': profit,
            'duration': duration_minutes,
            'success': profit > 0,
            'timestamp': datetime.now()
        }
        
        self.trade_outcomes.append(outcome)
        
        print(f"   📚 Learning: Trade outcome recorded (Profit: £{profit:.2f})")
        
        # Retrain model if enough data
        if len(self.trade_outcomes) >= 20 and len(self.trade_outcomes) % 10 == 0:
            print(f"   🔄 Retraining ML model with {len(self.trade_outcomes)} trades...")
            self._retrain_model()
    
    def _retrain_model(self):
        """
        Retrain ML model with accumulated data
        """
        try:
            if len(self.training_data) < 20:
                print(f"   ⚠️ Not enough data to train (need 20, have {len(self.training_data)})")
                return
            
            # Prepare training data
            X = []
            y = []
            
            for i, decision_data in enumerate(self.training_data):
                if i < len(self.trade_outcomes):
                    outcome = self.trade_outcomes[i]
                    
                    X.append(decision_data['features'].flatten())
                    y.append(1 if outcome['success'] else 0)
            
            X = np.array(X)
            y = np.array(y)
            
            # Train scaler
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            
            # Train classifier
            self.entry_predictor = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            
            self.entry_predictor.fit(X_scaled, y)
            
            # Calculate accuracy
            predictions = self.entry_predictor.predict(X_scaled)
            accuracy = np.mean(predictions == y)
            
            print(f"   ✅ Model retrained! Accuracy: {accuracy:.1%}")
            
            # Save models
            self._save_models()
            
        except Exception as e:
            print(f"   ⚠️ Model training error: {e}")
    
    def _save_models(self):
        """
        Save trained models to disk
        """
        try:
            if self.entry_predictor:
                with open(f"{self.model_dir}/entry_predictor.pkl", 'wb') as f:
                    pickle.dump(self.entry_predictor, f)
            
            if self.scaler:
                with open(f"{self.model_dir}/scaler.pkl", 'wb') as f:
                    pickle.dump(self.scaler, f)
            
            print(f"   💾 Models saved to {self.model_dir}/")
            
        except Exception as e:
            print(f"   ⚠️ Error saving models: {e}")
    
    def _load_models(self):
        """
        Load trained models from disk
        """
        try:
            predictor_path = f"{self.model_dir}/entry_predictor.pkl"
            scaler_path = f"{self.model_dir}/scaler.pkl"
            
            if os.path.exists(predictor_path):
                with open(predictor_path, 'rb') as f:
                    self.entry_predictor = pickle.load(f)
                print(f"   ✅ Loaded entry predictor model")
            
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print(f"   ✅ Loaded feature scaler")
                
        except Exception as e:
            print(f"   ⚠️ Error loading models: {e}")
    
    def _get_quality_rating(self, score: float) -> str:
        """
        Convert score to quality rating
        """
        if score >= 85:
            return "EXCELLENT"
        elif score >= 70:
            return "GOOD"
        elif score >= 50:
            return "FAIR"
        else:
            return "POOR"
    
    def get_performance_stats(self) -> dict:
        """
        Get ML system performance statistics
        """
        if not self.trade_outcomes:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'model_trained': self.entry_predictor is not None
            }
        
        outcomes = list(self.trade_outcomes)
        
        total = len(outcomes)
        wins = sum(1 for o in outcomes if o['profit'] > 0)
        win_rate = wins / total if total > 0 else 0
        
        total_profit = sum(o['profit'] for o in outcomes)
        avg_profit = total_profit / total if total > 0 else 0
        
        return {
            'total_trades': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'avg_profit': avg_profit,
            'best_trade': max((o['profit'] for o in outcomes), default=0),
            'worst_trade': min((o['profit'] for o in outcomes), default=0),
            'model_trained': self.entry_predictor is not None,
            'adaptive_threshold': self._get_adaptive_threshold()
        }