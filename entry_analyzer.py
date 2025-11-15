"""
ENHANCED ENTRY SYSTEM - Base Technical Analysis
================================================

Provides comprehensive technical analysis for entry decisions.
This is the base system that ML enhances.

Features:
- Multi-factor scoring (trend, momentum, volume, support/resistance, market regime)
- Technical indicator analysis
- Risk assessment
- Quality rating
"""

from data_layer.indicators import TechnicalIndicators
from datetime import datetime


class EnhancedEntrySystem:
    """
    Enhanced Entry Analysis System

    Provides comprehensive technical analysis for trading entry decisions.
    Combines multiple factors:
    1. Trend Analysis (EMA, MACD)
    2. Momentum (RSI, Stochastic)
    3. Volume Analysis
    4. Support/Resistance levels
    5. Market Regime (volatility, trend strength)
    """

    def __init__(self):
        self.indicators = TechnicalIndicators()

    def analyze_entry_opportunity(self, snapshot: dict, product_id: str) -> dict:
        """
        Analyze if current market conditions present a good entry opportunity.

        Args:
            snapshot: Market data snapshot with current_price and indicators
            product_id: Trading pair (e.g., 'SOL-GBP')

        Returns:
            dict with:
                - score: 0-100 overall entry quality score
                - breakdown: Scores for each component
                - reason: Human-readable explanation
                - should_enter: Boolean recommendation
                - confidence: 0-1 confidence level
        """
        # Handle None snapshot
        if snapshot is None:
            return {
                'score': 0,
                'breakdown': {},
                'reason': 'No market data available - check API credentials',
                'should_enter': False,
                'confidence': 0.0,
                'quality': 'CRITICAL_ERROR'
            }

        indicators = snapshot.get('indicators', {})
        current_price = snapshot.get('current_price', 0)

        # Initialize scoring
        total_score = 0
        max_score = 100
        breakdown = {}

        # 1. TREND ANALYSIS (0-25 points)
        trend_score, trend_details = self._analyze_trend(indicators, current_price)
        breakdown['trend'] = {'score': trend_score, 'details': trend_details}
        total_score += trend_score

        # 2. MOMENTUM ANALYSIS (0-25 points)
        momentum_score, momentum_details = self._analyze_momentum(indicators)
        breakdown['momentum'] = {'score': momentum_score, 'details': momentum_details}
        total_score += momentum_score

        # 3. VOLUME ANALYSIS (0-15 points)
        volume_score, volume_details = self._analyze_volume(indicators)
        breakdown['volume'] = {'score': volume_score, 'details': volume_details}
        total_score += volume_score

        # 4. SUPPORT/RESISTANCE (0-20 points)
        sr_score, sr_details = self._analyze_support_resistance(indicators, current_price)
        breakdown['support_resistance'] = {'score': sr_score, 'details': sr_details}
        total_score += sr_score

        # 5. MARKET REGIME (0-15 points)
        regime_score, regime_details = self._analyze_market_regime(indicators)
        breakdown['market_regime'] = {'score': regime_score, 'details': regime_details}
        total_score += regime_score

        # Build reason string
        reason = self._build_reason(breakdown)

        # Decision thresholds
        should_enter = total_score >= 70  # 70+ = good entry
        confidence = total_score / 100.0

        return {
            'score': int(total_score),
            'breakdown': breakdown,
            'reason': reason,
            'should_enter': should_enter,
            'confidence': confidence,
            'quality': self._get_quality_rating(total_score),
            'timestamp': snapshot.get('timestamp', datetime.now().isoformat())
        }

    def _analyze_trend(self, indicators: dict, current_price: float) -> tuple[int, str]:
        """
        Analyze trend strength and direction.

        Factors:
        - EMA alignment (10 > 50 = bullish)
        - MACD (positive = bullish)
        - Price position relative to EMAs

        Returns (score 0-25, details)
        """
        score = 0
        details = []

        ema_10 = indicators.get('ema_10', current_price)
        ema_50 = indicators.get('ema_50', current_price)
        macd_histogram = indicators.get('macd_histogram', 0)
        macd_line = indicators.get('macd_line', 0)

        # EMA alignment (0-10 points)
        if ema_10 > ema_50:
            ema_diff_pct = ((ema_10 - ema_50) / ema_50) * 100
            if ema_diff_pct > 2.0:
                score += 10
                details.append("Strong bullish EMA alignment")
            elif ema_diff_pct > 0.5:
                score += 7
                details.append("Moderate bullish EMA alignment")
            else:
                score += 4
                details.append("Weak bullish EMA alignment")
        else:
            details.append("Bearish EMA alignment")

        # MACD (0-10 points)
        if macd_histogram > 0 and macd_line > 0:
            score += 10
            details.append("MACD positive and rising")
        elif macd_histogram > 0:
            score += 6
            details.append("MACD rising but below signal")
        elif macd_line > 0:
            score += 4
            details.append("MACD positive but falling")
        else:
            details.append("MACD bearish")

        # Price vs EMAs (0-5 points)
        if current_price > ema_10 > ema_50:
            score += 5
            details.append("Price above both EMAs")
        elif current_price > ema_10:
            score += 3
            details.append("Price above fast EMA")

        return score, " | ".join(details)

    def _analyze_momentum(self, indicators: dict) -> tuple[int, str]:
        """
        Analyze momentum indicators.

        Factors:
        - RSI (30-70 = good, <30 = oversold opportunity)
        - Stochastic
        - ADX (trend strength)

        Returns (score 0-25, details)
        """
        score = 0
        details = []

        rsi = indicators.get('rsi', 50)
        stoch_k = indicators.get('stoch_k', 50)
        stoch_d = indicators.get('stoch_d', 50)
        adx = indicators.get('adx', 0)

        # RSI analysis (0-10 points)
        if 30 <= rsi <= 45:
            score += 10
            details.append(f"RSI oversold recovery ({rsi:.0f})")
        elif 45 < rsi <= 60:
            score += 8
            details.append(f"RSI bullish ({rsi:.0f})")
        elif rsi < 30:
            score += 7
            details.append(f"RSI oversold ({rsi:.0f})")
        elif 60 < rsi <= 70:
            score += 5
            details.append(f"RSI elevated ({rsi:.0f})")
        else:
            details.append(f"RSI overbought ({rsi:.0f})")

        # Stochastic (0-10 points)
        if stoch_k > stoch_d and stoch_k < 80:
            score += 8
            details.append("Stochastic bullish crossover")
        elif stoch_k > stoch_d:
            score += 5
            details.append("Stochastic rising")
        elif stoch_k < 20:
            score += 6
            details.append("Stochastic oversold")

        # ADX - trend strength (0-5 points)
        if adx > 25:
            score += 5
            details.append(f"Strong trend (ADX {adx:.0f})")
        elif adx > 20:
            score += 3
            details.append(f"Moderate trend (ADX {adx:.0f})")
        else:
            details.append(f"Weak trend (ADX {adx:.0f})")

        return score, " | ".join(details)

    def _analyze_volume(self, indicators: dict) -> tuple[int, str]:
        """
        Analyze volume conditions.

        Returns (score 0-15, details)
        """
        score = 0
        details = []

        volume_ratio = indicators.get('volume_ratio', 1.0)

        # Volume analysis (0-15 points)
        if volume_ratio > 1.5:
            score += 15
            details.append(f"High volume ({volume_ratio:.1f}x)")
        elif volume_ratio > 1.2:
            score += 12
            details.append(f"Above average volume ({volume_ratio:.1f}x)")
        elif volume_ratio > 0.8:
            score += 8
            details.append(f"Normal volume ({volume_ratio:.1f}x)")
        else:
            score += 3
            details.append(f"Low volume ({volume_ratio:.1f}x)")

        return score, " | ".join(details)

    def _analyze_support_resistance(self, indicators: dict, current_price: float) -> tuple[int, str]:
        """
        Analyze support/resistance levels.

        Returns (score 0-20, details)
        """
        score = 0
        details = []

        bb_position = indicators.get('bb_position', 50)
        bb_width = indicators.get('bb_width', 0)

        # Bollinger Band position (0-15 points)
        if bb_position < 20:
            score += 15
            details.append(f"Near lower BB ({bb_position:.0f}%) - support")
        elif bb_position < 40:
            score += 12
            details.append(f"Below mid BB ({bb_position:.0f}%)")
        elif bb_position < 60:
            score += 8
            details.append(f"Mid BB ({bb_position:.0f}%)")
        elif bb_position < 80:
            score += 5
            details.append(f"Above mid BB ({bb_position:.0f}%)")
        else:
            score += 2
            details.append(f"Near upper BB ({bb_position:.0f}%) - resistance")

        # Bollinger Band width (0-5 points) - volatility
        if bb_width > 4.0:
            score += 5
            details.append("High volatility")
        elif bb_width > 2.0:
            score += 3
            details.append("Normal volatility")
        else:
            details.append("Low volatility")

        return score, " | ".join(details)

    def _analyze_market_regime(self, indicators: dict) -> tuple[int, str]:
        """
        Analyze overall market regime.

        Returns (score 0-15, details)
        """
        score = 0
        details = []

        atr_pct = indicators.get('atr_pct', 0)
        price_change_pct = indicators.get('price_change_pct', 0)

        # ATR - volatility context (0-8 points)
        if 1.5 < atr_pct < 3.5:
            score += 8
            details.append(f"Healthy volatility ({atr_pct:.1f}%)")
        elif atr_pct > 3.5:
            score += 5
            details.append(f"High volatility ({atr_pct:.1f}%)")
        else:
            score += 3
            details.append(f"Low volatility ({atr_pct:.1f}%)")

        # Recent price action (0-7 points)
        if 0.5 < price_change_pct < 3.0:
            score += 7
            details.append(f"Positive momentum (+{price_change_pct:.1f}%)")
        elif price_change_pct > 3.0:
            score += 4
            details.append(f"Strong rally (+{price_change_pct:.1f}%)")
        elif price_change_pct > 0:
            score += 5
            details.append(f"Slight gain (+{price_change_pct:.1f}%)")
        elif price_change_pct < -2.0:
            score += 6
            details.append(f"Dip ({price_change_pct:.1f}%)")
        else:
            score += 3
            details.append(f"Slight decline ({price_change_pct:.1f}%)")

        return score, " | ".join(details)

    def _build_reason(self, breakdown: dict) -> str:
        """Build human-readable reason from breakdown."""
        reasons = []

        for category, data in breakdown.items():
            score = data['score']
            details = data.get('details', '')
            if score > 0:
                reasons.append(f"{category.replace('_', ' ').title()}: {details}")

        return " | ".join(reasons)

    def _get_quality_rating(self, score: float) -> str:
        """Convert score to quality rating."""
        if score >= 85:
            return "EXCELLENT"
        elif score >= 70:
            return "GOOD"
        elif score >= 50:
            return "FAIR"
        else:
            return "POOR"
