"""
ENHANCED ENTRY SYSTEM - Multi-Factor Scoring Algorithm
Combines multiple signals for higher-confidence entries
"""

from data_layer.coinbase_client import CoinbaseClient
from datetime import datetime, timedelta
import statistics


class EnhancedEntrySystem:
    """
    Multi-Factor Scoring System for Trade Entries
    
    Scoring breakdown (100 points total):
    - Trend Alignment (30 pts): Multi-timeframe trend confirmation
    - Momentum (25 pts): RSI positioning and strength
    - Volume (20 pts): Volume confirmation
    - Support/Resistance (15 pts): Price location analysis
    - Market Regime (10 pts): Trending vs ranging detection
    
    Entry threshold: 70+ points (70% confidence)
    """
    
    def __init__(self):
        self.cb_client = CoinbaseClient()
        
        # Scoring thresholds
        self.MIN_SCORE = 70  # Out of 100
        self.EXCELLENT_SCORE = 85  # High confidence
        
        # Cache for support/resistance levels
        self.sr_levels = {}
        self.sr_cache_time = None
        self.SR_CACHE_DURATION = 3600  # 1 hour
        
        # Market regime cache
        self.market_regime = None
        self.regime_cache_time = None
        self.REGIME_CACHE_DURATION = 1800  # 30 minutes
    
    def analyze_entry_opportunity(self, snapshot: dict, product_id: str) -> dict:
        """
        Main entry point: Analyze if this is a good entry
        
        Returns:
        {
            'should_enter': bool,
            'confidence': float (0-1),
            'score': int (0-100),
            'breakdown': dict of individual scores,
            'reason': str
        }
        """
        try:
            score_breakdown = {}
            total_score = 0
            
            # 1. TREND ALIGNMENT (30 points max)
            trend_score, trend_details = self._score_trend_alignment(product_id)
            score_breakdown['trend'] = {
                'score': trend_score,
                'max': 30,
                'details': trend_details
            }
            total_score += trend_score
            
            # 2. MOMENTUM (25 points max)
            momentum_score, momentum_details = self._score_momentum(snapshot)
            score_breakdown['momentum'] = {
                'score': momentum_score,
                'max': 25,
                'details': momentum_details
            }
            total_score += momentum_score
            
            # 3. VOLUME (20 points max)
            volume_score, volume_details = self._score_volume(snapshot)
            score_breakdown['volume'] = {
                'score': volume_score,
                'max': 20,
                'details': volume_details
            }
            total_score += volume_score
            
            # 4. SUPPORT/RESISTANCE (15 points max)
            sr_score, sr_details = self._score_support_resistance(
                snapshot['current_price'], 
                product_id
            )
            score_breakdown['support_resistance'] = {
                'score': sr_score,
                'max': 15,
                'details': sr_details
            }
            total_score += sr_score
            
            # 5. MARKET REGIME (10 points max)
            regime_score, regime_details = self._score_market_regime(product_id, snapshot)
            score_breakdown['market_regime'] = {
                'score': regime_score,
                'max': 10,
                'details': regime_details
            }
            total_score += regime_score
            
            # Calculate confidence
            confidence = total_score / 100.0
            should_enter = total_score >= self.MIN_SCORE
            
            # Build reason string
            reason = self._build_reason_string(total_score, score_breakdown, should_enter)
            
            return {
                'should_enter': should_enter,
                'confidence': confidence,
                'score': total_score,
                'breakdown': score_breakdown,
                'reason': reason,
                'quality': self._get_quality_rating(total_score)
            }
            
        except Exception as e:
            print(f"   ⚠️ Error in entry analysis: {e}")
            return {
                'should_enter': False,
                'confidence': 0.0,
                'score': 0,
                'breakdown': {},
                'reason': f"Analysis error: {e}",
                'quality': 'ERROR'
            }
    
    def _score_trend_alignment(self, product_id: str) -> tuple[int, str]:
        """
        Score: 0-30 points
        Check if multiple timeframes agree on trend direction
        
        30 pts: All 3 timeframes bullish
        20 pts: 2 timeframes bullish
        10 pts: 1 timeframe bullish
        0 pts: No bullish timeframes
        """
        try:
            # Get different timeframe candles
            candles_1h = self.cb_client.get_candles(product_id, "ONE_HOUR", 24)
            candles_15m = self.cb_client.get_candles(product_id, "FIFTEEN_MINUTE", 32)
            candles_5m = self.cb_client.get_candles(product_id, "FIVE_MINUTE", 36)
            
            bullish_timeframes = 0
            timeframe_status = []
            
            # Check 1H trend (most important)
            if candles_1h and len(candles_1h) >= 10:
                if self._is_timeframe_bullish(candles_1h, lookback=10):
                    bullish_timeframes += 1
                    timeframe_status.append("1H✅")
                else:
                    timeframe_status.append("1H❌")
            
            # Check 15M trend
            if candles_15m and len(candles_15m) >= 12:
                if self._is_timeframe_bullish(candles_15m, lookback=12):
                    bullish_timeframes += 1
                    timeframe_status.append("15M✅")
                else:
                    timeframe_status.append("15M❌")
            
            # Check 5M trend
            if candles_5m and len(candles_5m) >= 12:
                if self._is_timeframe_bullish(candles_5m, lookback=12):
                    bullish_timeframes += 1
                    timeframe_status.append("5M✅")
                else:
                    timeframe_status.append("5M❌")
            
            # Score based on alignment
            if bullish_timeframes == 3:
                score = 30
                detail = f"Perfect alignment: {', '.join(timeframe_status)}"
            elif bullish_timeframes == 2:
                score = 20
                detail = f"Good alignment: {', '.join(timeframe_status)}"
            elif bullish_timeframes == 1:
                score = 10
                detail = f"Weak alignment: {', '.join(timeframe_status)}"
            else:
                score = 0
                detail = f"No alignment: {', '.join(timeframe_status)}"
            
            return score, detail
            
        except Exception as e:
            return 0, f"Error checking trends: {e}"
    
    def _is_timeframe_bullish(self, candles: list, lookback: int = 10) -> bool:
        """
        Determine if a timeframe is bullish using simple moving average crossover
        """
        if len(candles) < lookback:
            return False
        
        # Get recent closes
        closes = [c['close'] for c in candles[-lookback:]]
        
        # Short MA (last 1/3 of period)
        short_period = lookback // 3
        short_ma = sum(closes[-short_period:]) / short_period
        
        # Long MA (entire period)
        long_ma = sum(closes) / len(closes)
        
        # Current price
        current_price = closes[-1]
        
        # Bullish if:
        # 1. Short MA > Long MA (golden cross)
        # 2. Current price > Short MA (price above recent average)
        return short_ma > long_ma and current_price > short_ma
    
    def _score_momentum(self, snapshot: dict) -> tuple[int, str]:
        """
        Score: 0-25 points
        Evaluate RSI and momentum indicators
        
        25 pts: RSI in ideal zone (40-60) - balanced momentum
        20 pts: RSI slightly oversold (30-40) - bounce potential
        15 pts: RSI neutral but acceptable (60-70)
        10 pts: RSI very oversold (<30) - risky but potential
        5 pts: RSI overbought (70-80) - risky
        0 pts: RSI extremely overbought (>80) - avoid
        """
        indicators = snapshot.get('indicators', {})
        rsi = indicators.get('rsi', 50)
        macd_cross = indicators.get('macd_cross', '')
        
        # Base score from RSI
        if 40 <= rsi <= 60:
            score = 25
            rsi_rating = "ideal"
        elif 30 <= rsi < 40:
            score = 20
            rsi_rating = "slightly oversold (good)"
        elif 60 < rsi <= 70:
            score = 15
            rsi_rating = "acceptable"
        elif rsi < 30:
            score = 10
            rsi_rating = "very oversold (risky)"
        elif 70 < rsi <= 80:
            score = 5
            rsi_rating = "overbought (risky)"
        else:  # > 80
            score = 0
            rsi_rating = "extremely overbought (avoid)"
        
        # Bonus for bullish MACD
        macd_bonus = ""
        if macd_cross == 'bullish':
            score = min(score + 5, 25)  # Cap at 25
            macd_bonus = " +MACD✅"
        
        detail = f"RSI {rsi:.1f} ({rsi_rating}){macd_bonus}"
        
        return score, detail
    
    def _score_volume(self, snapshot: dict) -> tuple[int, str]:
        """
        Score: 0-20 points
        Volume confirmation is crucial for valid breakouts
        
        20 pts: Very high volume (>2x average)
        15 pts: High volume (1.5x - 2x average)
        10 pts: Above average (1.0x - 1.5x)
        5 pts: Average (0.8x - 1.0x)
        0 pts: Below average (<0.8x)
        """
        indicators = snapshot.get('indicators', {})
        volume_ratio = indicators.get('volume_ratio', 0)
        
        if volume_ratio >= 2.0:
            score = 20
            rating = "very high"
        elif volume_ratio >= 1.5:
            score = 15
            rating = "high"
        elif volume_ratio >= 1.0:
            score = 10
            rating = "above average"
        elif volume_ratio >= 0.8:
            score = 5
            rating = "average"
        else:
            score = 0
            rating = "low (warning)"
        
        detail = f"{volume_ratio:.1f}x average ({rating})"
        
        return score, detail
    
    def _score_support_resistance(self, current_price: float, product_id: str) -> tuple[int, str]:
        """
        Score: 0-15 points
        Buying near support levels increases success probability
        
        15 pts: At strong support (within 0.5%)
        10 pts: Near support (within 1%)
        5 pts: Between levels (neutral)
        0 pts: At resistance (bad entry)
        """
        try:
            # Get or calculate S/R levels (cached for performance)
            sr_levels = self._get_support_resistance_levels(product_id)
            
            if not sr_levels:
                return 5, "S/R levels unavailable"
            
            support_levels = sr_levels['support']
            resistance_levels = sr_levels['resistance']
            
            # Find nearest support and resistance
            nearest_support = max([s for s in support_levels if s < current_price], default=0)
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=float('inf'))
            
            # Calculate distances as percentages
            if nearest_support > 0:
                support_dist_pct = abs(current_price - nearest_support) / current_price * 100
            else:
                support_dist_pct = 100
            
            if nearest_resistance < float('inf'):
                resistance_dist_pct = abs(nearest_resistance - current_price) / current_price * 100
            else:
                resistance_dist_pct = 100
            
            # Score based on proximity to support
            if support_dist_pct <= 0.5:
                score = 15
                detail = f"At support £{nearest_support:.2f} ({support_dist_pct:.1f}%)"
            elif support_dist_pct <= 1.0:
                score = 10
                detail = f"Near support £{nearest_support:.2f} ({support_dist_pct:.1f}%)"
            elif resistance_dist_pct <= 0.5:
                score = 0
                detail = f"At resistance £{nearest_resistance:.2f} (avoid)"
            else:
                score = 5
                detail = f"Between levels ({support_dist_pct:.1f}% from support)"
            
            return score, detail
            
        except Exception as e:
            return 5, f"S/R error: {e}"
    
    def _get_support_resistance_levels(self, product_id: str) -> dict:
        """
        Calculate support and resistance levels from historical price action
        Uses pivot points and historical swing highs/lows
        """
        # Check cache
        now = datetime.now()
        if self.sr_cache_time and (now - self.sr_cache_time).total_seconds() < self.SR_CACHE_DURATION:
            if product_id in self.sr_levels:
                return self.sr_levels[product_id]
        
        try:
            # Get 7 days of hourly candles
            candles = self.cb_client.get_candles(product_id, "ONE_HOUR", 168)
            
            if not candles or len(candles) < 50:
                return None
            
            # Extract highs and lows
            highs = [c['high'] for c in candles]
            lows = [c['low'] for c in candles]
            closes = [c['close'] for c in candles]
            
            # Find swing highs and lows (local extrema)
            support_levels = []
            resistance_levels = []
            
            # Simple swing detection (look for peaks and valleys)
            for i in range(5, len(candles) - 5):
                # Swing high (resistance)
                if highs[i] == max(highs[i-5:i+5]):
                    resistance_levels.append(highs[i])
                
                # Swing low (support)
                if lows[i] == min(lows[i-5:i+5]):
                    support_levels.append(lows[i])
            
            # Add current price quartiles as additional levels
            current_price = closes[-1]
            price_range = max(highs) - min(lows)
            
            # Also add psychological levels (round numbers)
            psychological_levels = []
            base = int(current_price / 100) * 100
            for offset in [-200, -100, 0, 100, 200]:
                level = base + offset
                if min(lows) < level < max(highs):
                    psychological_levels.append(level)
            
            # Combine and filter to unique levels (within 0.5% tolerance)
            support_levels = self._cluster_levels(support_levels + psychological_levels)
            resistance_levels = self._cluster_levels(resistance_levels + psychological_levels)
            
            result = {
                'support': sorted(support_levels),
                'resistance': sorted(resistance_levels)
            }
            
            # Cache the result
            self.sr_levels[product_id] = result
            self.sr_cache_time = now
            
            return result
            
        except Exception as e:
            print(f"   Error calculating S/R levels: {e}")
            return None
    
    def _cluster_levels(self, levels: list, tolerance_pct: float = 0.5) -> list:
        """
        Cluster similar price levels together (within tolerance)
        Returns representative levels
        """
        if not levels:
            return []
        
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            # Check if this level is close to current cluster
            cluster_avg = sum(current_cluster) / len(current_cluster)
            distance_pct = abs(level - cluster_avg) / cluster_avg * 100
            
            if distance_pct <= tolerance_pct:
                current_cluster.append(level)
            else:
                # Save current cluster average and start new cluster
                clusters.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]
        
        # Don't forget the last cluster
        if current_cluster:
            clusters.append(sum(current_cluster) / len(current_cluster))
        
        return clusters
    
    def _score_market_regime(self, product_id: str, snapshot: dict) -> tuple[int, str]:
        """
        Score: 0-10 points
        Identify if market is trending or ranging
        
        10 pts: Clear regime (either trending or ranging)
        5 pts: Transitioning between regimes
        0 pts: Unclear regime
        """
        try:
            # Detect regime (cached for performance)
            regime = self._detect_market_regime(product_id)
            
            indicators = snapshot.get('indicators', {})
            ema_cross = indicators.get('ema_cross', '')
            
            if regime == 'trending':
                # In trending market, we want momentum signals
                if ema_cross == 'bullish':
                    score = 10
                    detail = "Trending market + bullish momentum"
                else:
                    score = 5
                    detail = "Trending market (wait for momentum)"
            
            elif regime == 'ranging':
                # In ranging market, we want oversold conditions
                rsi = indicators.get('rsi', 50)
                if rsi < 40:
                    score = 10
                    detail = "Ranging market + oversold (good for mean reversion)"
                else:
                    score = 5
                    detail = "Ranging market (wait for dip)"
            
            else:  # unclear
                score = 5
                detail = "Market regime unclear"
            
            return score, detail
            
        except Exception as e:
            return 5, f"Regime detection error: {e}"
    
    def _detect_market_regime(self, product_id: str) -> str:
        """
        Detect if market is trending or ranging
        
        Returns: 'trending', 'ranging', or 'unclear'
        """
        # Check cache
        now = datetime.now()
        if self.regime_cache_time and (now - self.regime_cache_time).total_seconds() < self.REGIME_CACHE_DURATION:
            if self.market_regime:
                return self.market_regime
        
        try:
            # Get recent hourly candles
            candles = self.cb_client.get_candles(product_id, "ONE_HOUR", 48)
            
            if not candles or len(candles) < 48:
                return 'unclear'
            
            closes = [c['close'] for c in candles]
            highs = [c['high'] for c in candles]
            lows = [c['low'] for c in candles]
            
            # Method 1: ADX (Average Directional Index) approximation
            # High ADX = trending, Low ADX = ranging
            
            # Calculate price range and average true range
            price_range = max(highs) - min(lows)
            avg_close = sum(closes) / len(closes)
            range_pct = (price_range / avg_close) * 100
            
            # Calculate trend strength (linear regression slope)
            x = list(range(len(closes)))
            x_mean = sum(x) / len(x)
            y_mean = sum(closes) / len(closes)
            
            numerator = sum((x[i] - x_mean) * (closes[i] - y_mean) for i in range(len(closes)))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(len(closes)))
            
            if denominator != 0:
                slope = numerator / denominator
                # Normalize slope as percentage of average price
                trend_strength = abs(slope) / avg_close * 100
            else:
                trend_strength = 0
            
            # Decision logic
            if trend_strength > 0.5 and range_pct > 5:
                regime = 'trending'
            elif range_pct < 4:
                regime = 'ranging'
            else:
                regime = 'unclear'
            
            # Cache result
            self.market_regime = regime
            self.regime_cache_time = now
            
            return regime
            
        except Exception as e:
            print(f"   Error detecting regime: {e}")
            return 'unclear'
    
    def _build_reason_string(self, total_score: int, breakdown: dict, should_enter: bool) -> str:
        """
        Build human-readable reason for the decision
        """
        if should_enter:
            # Highlight top contributors
            sorted_factors = sorted(
                breakdown.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            top_factors = []
            for factor, data in sorted_factors[:2]:  # Top 2
                if data['score'] > 0:
                    pct = (data['score'] / data['max']) * 100
                    top_factors.append(f"{factor.replace('_', ' ').title()} ({pct:.0f}%)")
            
            reason = f"STRONG ENTRY ({total_score}/100): " + ", ".join(top_factors)
        else:
            # Highlight what's missing
            sorted_factors = sorted(
                breakdown.items(),
                key=lambda x: x[1]['score']
            )
            
            weak_factors = []
            for factor, data in sorted_factors[:2]:  # Bottom 2
                pct = (data['score'] / data['max']) * 100
                if pct < 50:
                    weak_factors.append(f"{factor.replace('_', ' ').title()} weak ({pct:.0f}%)")
            
            reason = f"SKIP ({total_score}/100): " + ", ".join(weak_factors)
        
        return reason
    
    def _get_quality_rating(self, score: int) -> str:
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
    
    def print_detailed_analysis(self, analysis: dict):
        """
        Print detailed breakdown of the analysis
        """
        print(f"\n{'='*70}")
        print(f"🎯 ENHANCED ENTRY ANALYSIS")
        print(f"{'='*70}")
        
        print(f"\n📊 OVERALL SCORE: {analysis['score']}/100 ({analysis['quality']})")
        print(f"   Confidence: {analysis['confidence']*100:.1f}%")
        print(f"   Decision: {'✅ ENTER' if analysis['should_enter'] else '❌ SKIP'}")
        
        print(f"\n📋 BREAKDOWN:")
        for factor, data in analysis['breakdown'].items():
            score = data['score']
            max_score = data['max']
            pct = (score / max_score * 100) if max_score > 0 else 0
            
            # Visual bar
            filled = int(pct / 10)
            bar = '█' * filled + '░' * (10 - filled)
            
            print(f"\n   {factor.replace('_', ' ').title()}:")
            print(f"   {bar} {score}/{max_score} ({pct:.0f}%)")
            print(f"   └─ {data['details']}")
        
        print(f"\n💡 {analysis['reason']}")
        print(f"{'='*70}\n")