import pandas as pd
import talib
import numpy as np

class TechnicalIndicators:
    """
    ENHANCED Technical Indicators with 15+ indicators for powerful analysis.
    
    NEW ADDITIONS:
    - Bollinger Bands (volatility + overbought/oversold)
    - Stochastic Oscillator (momentum)
    - ATR (volatility measurement)
    - ADX (trend strength)
    - OBV (volume momentum)
    - CCI (Commodity Channel Index)
    - Williams %R (momentum)
    - Parabolic SAR (trend reversal)
    - Money Flow Index (volume-weighted RSI)
    - Weighted signal scoring
    """
    
    @staticmethod
    def calculate_all(
        candles: list, 
        rsi_period: int = 14, 
        ema_fast: int = 10, 
        ema_slow: int = 50
    ) -> dict:
        """
        Calculate ALL technical indicators from candle data.
        
        Args:
            candles: List of candle dicts with OHLCV data
            rsi_period: Period for RSI calculation
            ema_fast: Fast EMA period
            ema_slow: Slow EMA period
            
        Returns:
            dict: All calculated indicators
        """
        if not candles or len(candles) < max(rsi_period, ema_slow):
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(candles)
        
        # Convert to numpy arrays for talib
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        open_price = df['open'].values
        volume = df['volume'].values
        
        # ====================================================================
        # MOMENTUM INDICATORS
        # ====================================================================
        
        # RSI (14 period)
        rsi = talib.RSI(close, timeperiod=rsi_period)
        
        # Stochastic Oscillator (shows momentum + overbought/oversold)
        slowk, slowd = talib.STOCH(
            high, low, close,
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        
        # Williams %R (another momentum indicator)
        willr = talib.WILLR(high, low, close, timeperiod=14)
        
        # CCI - Commodity Channel Index
        cci = talib.CCI(high, low, close, timeperiod=14)
        
        # MFI - Money Flow Index (volume-weighted RSI)
        mfi = talib.MFI(high, low, close, volume, timeperiod=14)
        
        # ====================================================================
        # TREND INDICATORS
        # ====================================================================
        
        # EMAs (existing)
        ema_10 = talib.EMA(close, timeperiod=ema_fast)
        ema_50 = talib.EMA(close, timeperiod=ema_slow)
        ema_200 = talib.EMA(close, timeperiod=200)  # Long-term trend
        
        # MACD (existing)
        macd_line, macd_signal, macd_histogram = talib.MACD(
            close, 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        
        # ADX - Average Directional Index (trend strength)
        adx = talib.ADX(high, low, close, timeperiod=14)
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
        
        # Parabolic SAR (trend reversal points)
        sar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
        
        # ====================================================================
        # VOLATILITY INDICATORS
        # ====================================================================
        
        # Bollinger Bands (volatility + support/resistance)
        bb_upper, bb_middle, bb_lower = talib.BBANDS(
            close,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )
        
        # ATR - Average True Range (volatility measurement)
        atr = talib.ATR(high, low, close, timeperiod=14)
        
        # ====================================================================
        # VOLUME INDICATORS
        # ====================================================================
        
        # OBV - On Balance Volume (volume momentum)
        obv = talib.OBV(close, volume)
        
        # Volume change
        volume_change = ((volume[-1] - volume[-2]) / volume[-2] * 100) if len(volume) > 1 else 0
        
        # Average volume (20 period)
        avg_volume = np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume)
        volume_ratio = volume[-1] / avg_volume if avg_volume > 0 else 1
        
        # ====================================================================
        # EXTRACT CURRENT VALUES (with NaN handling)
        # ====================================================================
        
        current_price = float(close[-1])
        price_change_pct = ((close[-1] - close[-2]) / close[-2] * 100) if len(close) > 1 else 0
        
        # Safe extraction helper
        def safe_float(arr, idx=-1, default=None):
            try:
                val = arr[idx]
                return float(val) if not np.isnan(val) else default
            except:
                return default
        
        # Momentum indicators
        current_rsi = safe_float(rsi)
        current_stoch_k = safe_float(slowk)
        current_stoch_d = safe_float(slowd)
        current_willr = safe_float(willr)
        current_cci = safe_float(cci)
        current_mfi = safe_float(mfi)
        
        # Trend indicators
        current_ema_10 = safe_float(ema_10)
        current_ema_50 = safe_float(ema_50)
        current_ema_200 = safe_float(ema_200)
        current_macd = safe_float(macd_line)
        current_macd_signal = safe_float(macd_signal)
        current_macd_hist = safe_float(macd_histogram)
        current_adx = safe_float(adx)
        current_plus_di = safe_float(plus_di)
        current_minus_di = safe_float(minus_di)
        current_sar = safe_float(sar)
        
        # Volatility indicators
        current_bb_upper = safe_float(bb_upper)
        current_bb_middle = safe_float(bb_middle)
        current_bb_lower = safe_float(bb_lower)
        current_atr = safe_float(atr)
        
        # Volume indicators
        current_obv = safe_float(obv)
        prev_obv = safe_float(obv, -2)
        obv_trend = 'rising' if current_obv and prev_obv and current_obv > prev_obv else 'falling'
        
        # ====================================================================
        # CALCULATE DERIVED METRICS
        # ====================================================================
        
        # Bollinger Band position (where price is in the band)
        bb_position = None
        bb_width = None
        if current_bb_upper and current_bb_lower and current_bb_middle:
            bb_width = ((current_bb_upper - current_bb_lower) / current_bb_middle) * 100
            bb_position = ((current_price - current_bb_lower) / (current_bb_upper - current_bb_lower)) * 100
        
        # EMA alignment (all EMAs trending same direction?)
        ema_alignment = None
        if current_ema_10 and current_ema_50 and current_ema_200:
            if current_ema_10 > current_ema_50 > current_ema_200:
                ema_alignment = 'bullish'
            elif current_ema_10 < current_ema_50 < current_ema_200:
                ema_alignment = 'bearish'
            else:
                ema_alignment = 'mixed'
        
        # Trend strength classification
        trend_strength = None
        if current_adx:
            if current_adx < 25:
                trend_strength = 'weak'
            elif current_adx < 50:
                trend_strength = 'moderate'
            else:
                trend_strength = 'strong'
        
        # ====================================================================
        # RETURN ALL INDICATORS
        # ====================================================================
        
        return {
            # Price
            'current_price': current_price,
            'price_change_pct': round(price_change_pct, 2),
            
            # Momentum Indicators
            'rsi': round(current_rsi, 2) if current_rsi else None,
            'stoch_k': round(current_stoch_k, 2) if current_stoch_k else None,
            'stoch_d': round(current_stoch_d, 2) if current_stoch_d else None,
            'willr': round(current_willr, 2) if current_willr else None,
            'cci': round(current_cci, 2) if current_cci else None,
            'mfi': round(current_mfi, 2) if current_mfi else None,
            
            # Trend Indicators
            'ema_10': round(current_ema_10, 2) if current_ema_10 else None,
            'ema_50': round(current_ema_50, 2) if current_ema_50 else None,
            'ema_200': round(current_ema_200, 2) if current_ema_200 else None,
            'ema_cross': 'bullish' if current_ema_10 and current_ema_50 and current_ema_10 > current_ema_50 else 'bearish',
            'ema_alignment': ema_alignment,
            
            'macd_line': round(current_macd, 2) if current_macd else None,
            'macd_signal': round(current_macd_signal, 2) if current_macd_signal else None,
            'macd_histogram': round(current_macd_hist, 2) if current_macd_hist else None,
            'macd_cross': 'bullish' if current_macd and current_macd_signal and current_macd > current_macd_signal else 'bearish',
            
            'adx': round(current_adx, 2) if current_adx else None,
            'plus_di': round(current_plus_di, 2) if current_plus_di else None,
            'minus_di': round(current_minus_di, 2) if current_minus_di else None,
            'trend_strength': trend_strength,
            
            'sar': round(current_sar, 2) if current_sar else None,
            'sar_position': 'bullish' if current_sar and current_sar < current_price else 'bearish',
            
            # Volatility Indicators
            'bb_upper': round(current_bb_upper, 2) if current_bb_upper else None,
            'bb_middle': round(current_bb_middle, 2) if current_bb_middle else None,
            'bb_lower': round(current_bb_lower, 2) if current_bb_lower else None,
            'bb_position': round(bb_position, 2) if bb_position else None,
            'bb_width': round(bb_width, 2) if bb_width else None,
            
            'atr': round(current_atr, 2) if current_atr else None,
            'atr_pct': round((current_atr / current_price) * 100, 2) if current_atr else None,
            
            # Volume Indicators
            'volume_change_pct': round(volume_change, 2),
            'volume_ratio': round(volume_ratio, 2),
            'obv': int(current_obv) if current_obv else None,
            'obv_trend': obv_trend
        }
    
    @staticmethod
    def get_signal_strength(indicators: dict) -> dict:
        """
        ENHANCED signal analysis with weighted scoring.
        
        Analyzes 15+ indicators with intelligent weighting:
        - Momentum indicators: 30% weight
        - Trend indicators: 40% weight
        - Volatility indicators: 20% weight
        - Volume indicators: 10% weight
        
        Returns:
            dict: {"signal": "BUY/SELL/HOLD", "strength": 0-1, "reasons": [...], "score": int}
        """
        if not indicators:
            return {"signal": "HOLD", "strength": 0.0, "reasons": ["Insufficient data"], "score": 0}
        
        signals = []
        reasons = []
        weights = []
        
        # ================================================================
        # MOMENTUM SIGNALS (30% weight)
        # ================================================================
        
        # RSI (weight: 10%)
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                signals.append(1.0)
                weights.append(10)
                reasons.append(f"💚 RSI oversold ({rsi}) - Strong BUY signal")
            elif rsi < 40:
                signals.append(0.5)
                weights.append(10)
                reasons.append(f"🟢 RSI low ({rsi}) - Moderate BUY signal")
            elif rsi > 70:
                signals.append(-1.0)
                weights.append(10)
                reasons.append(f"💔 RSI overbought ({rsi}) - Strong SELL signal")
            elif rsi > 60:
                signals.append(-0.5)
                weights.append(10)
                reasons.append(f"🔴 RSI high ({rsi}) - Moderate SELL signal")
            else:
                signals.append(0)
                weights.append(10)
                reasons.append(f"⚪ RSI neutral ({rsi})")
        
        # Stochastic (weight: 10%)
        stoch_k = indicators.get('stoch_k')
        stoch_d = indicators.get('stoch_d')
        if stoch_k and stoch_d:
            if stoch_k < 20 and stoch_k > stoch_d:
                signals.append(1.0)
                weights.append(10)
                reasons.append(f"💚 Stochastic oversold + bullish cross - BUY")
            elif stoch_k > 80 and stoch_k < stoch_d:
                signals.append(-1.0)
                weights.append(10)
                reasons.append(f"💔 Stochastic overbought + bearish cross - SELL")
            elif stoch_k < 20:
                signals.append(0.5)
                weights.append(10)
                reasons.append(f"🟢 Stochastic oversold ({stoch_k:.0f})")
            elif stoch_k > 80:
                signals.append(-0.5)
                weights.append(10)
                reasons.append(f"🔴 Stochastic overbought ({stoch_k:.0f})")
        
        # MFI - Money Flow Index (weight: 10%)
        mfi = indicators.get('mfi')
        if mfi:
            if mfi < 20:
                signals.append(1.0)
                weights.append(10)
                reasons.append(f"💚 MFI oversold ({mfi:.0f}) - Strong buying pressure")
            elif mfi > 80:
                signals.append(-1.0)
                weights.append(10)
                reasons.append(f"💔 MFI overbought ({mfi:.0f}) - Strong selling pressure")
        
        # ================================================================
        # TREND SIGNALS (40% weight - MOST IMPORTANT)
        # ================================================================
        
        # EMA Cross (weight: 15%)
        if indicators.get('ema_cross') == 'bullish':
            signals.append(1.0)
            weights.append(15)
            reasons.append("💚 EMA bullish (10 > 50)")
        else:
            signals.append(-1.0)
            weights.append(15)
            reasons.append("💔 EMA bearish (10 < 50)")
        
        # EMA Alignment (weight: 10%)
        ema_alignment = indicators.get('ema_alignment')
        if ema_alignment == 'bullish':
            signals.append(1.0)
            weights.append(10)
            reasons.append("💚 All EMAs aligned bullish")
        elif ema_alignment == 'bearish':
            signals.append(-1.0)
            weights.append(10)
            reasons.append("💔 All EMAs aligned bearish")
        
        # MACD (weight: 10%)
        if indicators.get('macd_cross') == 'bullish':
            signals.append(1.0)
            weights.append(10)
            reasons.append("💚 MACD bullish cross")
        else:
            signals.append(-1.0)
            weights.append(10)
            reasons.append("💔 MACD bearish cross")
        
        # ADX Trend Strength (weight: 5%)
        adx = indicators.get('adx')
        trend_strength = indicators.get('trend_strength')
        if adx and adx > 25:
            # Strong trend exists - weight current direction heavily
            plus_di = indicators.get('plus_di', 0)
            minus_di = indicators.get('minus_di', 0)
            if plus_di > minus_di:
                signals.append(0.5)
                weights.append(5)
                reasons.append(f"🟢 Strong uptrend (ADX: {adx:.0f})")
            else:
                signals.append(-0.5)
                weights.append(5)
                reasons.append(f"🔴 Strong downtrend (ADX: {adx:.0f})")
        
        # ================================================================
        # VOLATILITY SIGNALS (20% weight)
        # ================================================================
        
        # Bollinger Bands (weight: 15%)
        bb_position = indicators.get('bb_position')
        if bb_position:
            if bb_position < 20:
                signals.append(1.0)
                weights.append(15)
                reasons.append(f"💚 Price at lower BB ({bb_position:.0f}%) - Oversold")
            elif bb_position > 80:
                signals.append(-1.0)
                weights.append(15)
                reasons.append(f"💔 Price at upper BB ({bb_position:.0f}%) - Overbought")
            elif bb_position < 40:
                signals.append(0.5)
                weights.append(15)
                reasons.append(f"🟢 Price below middle BB ({bb_position:.0f}%)")
            elif bb_position > 60:
                signals.append(-0.5)
                weights.append(15)
                reasons.append(f"🔴 Price above middle BB ({bb_position:.0f}%)")
        
        # ATR Volatility (weight: 5%)
        atr_pct = indicators.get('atr_pct')
        if atr_pct:
            if atr_pct < 2:
                reasons.append(f"⚪ Low volatility (ATR: {atr_pct:.1f}%) - Caution")
            elif atr_pct > 5:
                reasons.append(f"⚠️ High volatility (ATR: {atr_pct:.1f}%) - Risk")
        
        # ================================================================
        # VOLUME SIGNALS (10% weight)
        # ================================================================
        
        # Volume Ratio (weight: 5%)
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 1.5:
            signals.append(0.5 if indicators.get('price_change_pct', 0) > 0 else -0.5)
            weights.append(5)
            reasons.append(f"💪 High volume ({volume_ratio:.1f}x avg) - Strong move")
        elif volume_ratio < 0.5:
            reasons.append(f"⚪ Low volume ({volume_ratio:.1f}x avg) - Weak move")
        
        # OBV Trend (weight: 5%)
        obv_trend = indicators.get('obv_trend')
        if obv_trend == 'rising':
            signals.append(0.5)
            weights.append(5)
            reasons.append("💚 OBV rising - Buying pressure")
        elif obv_trend == 'falling':
            signals.append(-0.5)
            weights.append(5)
            reasons.append("💔 OBV falling - Selling pressure")
        
        # ================================================================
        # CALCULATE WEIGHTED SCORE
        # ================================================================
        
        if not signals:
            return {"signal": "HOLD", "strength": 0.0, "reasons": ["No clear signals"], "score": 0}
        
        # Weighted average
        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(signals, weights)) / total_weight if total_weight > 0 else 0
        
        # Convert to 0-100 score
        score = int((weighted_score + 1) * 50)  # -1 to 1 → 0 to 100
        
        # Determine signal
        if weighted_score > 0.3:
            signal = "BUY"
            strength = abs(weighted_score)
        elif weighted_score < -0.3:
            signal = "SELL"
            strength = abs(weighted_score)
        else:
            signal = "HOLD"
            strength = abs(weighted_score)
        
        return {
            "signal": signal,
            "strength": round(strength, 2),
            "score": score,  # 0-100 scale
            "reasons": reasons,
            "confidence": round(strength * 100, 0)  # Percentage
        }