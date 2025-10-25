import pandas as pd
import talib
import numpy as np

class TechnicalIndicators:
    """
    Calculate technical indicators from candle data using TA-Lib.
    """
    
    @staticmethod
    def calculate_all(candles: list, rsi_period: int = 14, ema_fast: int = 10, ema_slow: int = 50) -> dict:
        """
        Calculate all technical indicators from candle data.
        
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
        volume = df['volume'].values
        
        # Calculate RSI
        rsi = talib.RSI(close, timeperiod=rsi_period)
        
        # Calculate EMAs
        ema_10 = talib.EMA(close, timeperiod=ema_fast)
        ema_50 = talib.EMA(close, timeperiod=ema_slow)
        
        # Calculate MACD
        macd_line, macd_signal, macd_histogram = talib.MACD(
            close, 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        
        # Get latest values (handle NaN)
        current_rsi = float(rsi[-1]) if not np.isnan(rsi[-1]) else None
        current_ema_10 = float(ema_10[-1]) if not np.isnan(ema_10[-1]) else None
        current_ema_50 = float(ema_50[-1]) if not np.isnan(ema_50[-1]) else None
        
        current_macd = float(macd_line[-1]) if not np.isnan(macd_line[-1]) else None
        current_signal = float(macd_signal[-1]) if not np.isnan(macd_signal[-1]) else None
        current_histogram = float(macd_histogram[-1]) if not np.isnan(macd_histogram[-1]) else None
        
        # Calculate volume change
        volume_change = ((volume[-1] - volume[-2]) / volume[-2] * 100) if len(volume) > 1 else 0
        
        # Current price and change
        current_price = float(close[-1])
        price_change_pct = ((close[-1] - close[-2]) / close[-2] * 100) if len(close) > 1 else 0
        
        return {
            'current_price': current_price,
            'price_change_pct': round(price_change_pct, 2),
            'rsi': round(current_rsi, 2) if current_rsi else None,
            'ema_10': round(current_ema_10, 2) if current_ema_10 else None,
            'ema_50': round(current_ema_50, 2) if current_ema_50 else None,
            'ema_cross': 'bullish' if current_ema_10 and current_ema_50 and current_ema_10 > current_ema_50 else 'bearish',
            'macd_line': round(current_macd, 2) if current_macd else None,
            'macd_signal': round(current_signal, 2) if current_signal else None,
            'macd_histogram': round(current_histogram, 2) if current_histogram else None,
            'macd_cross': 'bullish' if current_macd and current_signal and current_macd > current_signal else 'bearish',
            'volume_change_pct': round(volume_change, 2)
        }
    
    @staticmethod
    def get_signal_strength(indicators: dict) -> dict:
        """
        Analyze indicators and return signal strength.
        
        Returns:
            dict: {"signal": "BUY/SELL/HOLD", "strength": 0-1, "reasons": [...]}
        """
        if not indicators:
            return {"signal": "HOLD", "strength": 0, "reasons": ["Insufficient data"]}
        
        signals = []
        reasons = []
        
        # RSI signals
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                signals.append(1)  # Oversold - bullish
                reasons.append(f"RSI oversold at {rsi}")
            elif rsi > 70:
                signals.append(-1)  # Overbought - bearish
                reasons.append(f"RSI overbought at {rsi}")
            else:
                signals.append(0)
                reasons.append(f"RSI neutral at {rsi}")
        
        # EMA cross signals
        if indicators.get('ema_cross') == 'bullish':
            signals.append(1)
            reasons.append("EMA bullish cross (10 > 50)")
        elif indicators.get('ema_cross') == 'bearish':
            signals.append(-1)
            reasons.append("EMA bearish cross (10 < 50)")
        
        # MACD signals
        if indicators.get('macd_cross') == 'bullish':
            signals.append(1)
            reasons.append("MACD bullish cross")
        elif indicators.get('macd_cross') == 'bearish':
            signals.append(-1)
            reasons.append("MACD bearish cross")
        
        # Calculate overall signal
        if not signals:
            return {"signal": "HOLD", "strength": 0, "reasons": ["No clear signals"]}
        
        avg_signal = sum(signals) / len(signals)
        
        if avg_signal > 0.3:
            signal = "BUY"
        elif avg_signal < -0.3:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        strength = abs(avg_signal)
        
        return {
            "signal": signal,
            "strength": round(strength, 2),
            "reasons": reasons
        }