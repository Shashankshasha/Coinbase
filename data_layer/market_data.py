from data_layer.coinbase_client import CoinbaseClient
from data_layer.indicators import TechnicalIndicators
from config import TRADING_PAIR, RSI_PERIOD, EMA_FAST, EMA_SLOW
from datetime import datetime

class MarketData:
    """
    High-level interface for market data and analysis.
    """
    
    def __init__(self):
        self.coinbase = CoinbaseClient()
        self.indicators = TechnicalIndicators()
    
    def get_full_market_snapshot(self, product_id: str = None) -> dict:
        """
        Get complete market snapshot with price, candles, and indicators.
        
        Returns:
            dict: Complete market analysis
        """
        product_id = product_id or TRADING_PAIR
        
        print(f"\n📊 Fetching market data for {product_id}...")
        
        # Get current price
        price_data = self.coinbase.get_current_price(product_id)
        if not price_data:
            return None
        
        # Get candles (last 100 15-min candles = ~25 hours)
        candles = self.coinbase.get_candles(
            product_id=product_id,
            granularity="FIFTEEN_MINUTE",
            limit=100
        )
        
        if not candles:
            return None
        
        # Calculate indicators
        indicators = self.indicators.calculate_all(
            candles,
            rsi_period=RSI_PERIOD,
            ema_fast=EMA_FAST,
            ema_slow=EMA_SLOW
        )
        
        # Get signal strength
        signal = self.indicators.get_signal_strength(indicators)
        
        # Get account balance
        balances = self.coinbase.get_account_balance()
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'product_id': product_id,
            'current_price': price_data['price'],
            'balances': balances,
            'indicators': indicators,
            'signal': signal,
            'recent_candles': candles[-10:]  # Last 10 candles for context
        }
        
        print(f"✅ Market snapshot ready")
        print(f"   Price: £{price_data['price']:.2f}")
        print(f"   RSI: {indicators.get('rsi')}")
        print(f"   Signal: {signal['signal']} (strength: {signal['strength']})")
        
        return snapshot
    
    def format_for_claude(self, snapshot: dict) -> str:
        """
        Format market snapshot into a readable prompt for Claude.
        
        Returns:
            str: Formatted market analysis for Claude
        """
        if not snapshot:
            return "No market data available"
        
        indicators = snapshot['indicators']
        signal = snapshot['signal']
        balances = snapshot['balances']
        
        prompt = f"""
Current Market Analysis for {snapshot['product_id']}:

💰 PRICE & BALANCE:
- Current Price: £{snapshot['current_price']:.2f}
- Price Change: {indicators.get('price_change_pct', 0)}%
- Your GBP Balance: £{balances.get('GBP', 0):.2f}
- Your ETH Balance: {balances.get('ETH', 0):.6f} ETH

📊 TECHNICAL INDICATORS:
- RSI (14): {indicators.get('rsi')} {"🔴 Overbought" if indicators.get('rsi', 0) > 70 else "🟢 Oversold" if indicators.get('rsi', 0) < 30 else "⚪ Neutral"}
- EMA 10: £{indicators.get('ema_10', 0):.2f}
- EMA 50: £{indicators.get('ema_50', 0):.2f}
- EMA Cross: {indicators.get('ema_cross')} {"📈" if indicators.get('ema_cross') == 'bullish' else "📉"}
- MACD Line: {indicators.get('macd_line')}
- MACD Signal: {indicators.get('macd_signal')}
- MACD Histogram: {indicators.get('macd_histogram')}
- MACD Status: {indicators.get('macd_cross')}
- Volume Change: {indicators.get('volume_change_pct')}%

🎯 PRELIMINARY SIGNAL:
Signal: {signal['signal']}
Strength: {signal['strength']}
Reasons: {', '.join(signal['reasons'])}

📈 RECENT PRICE ACTION (Last 10 candles):
"""
        
        for i, candle in enumerate(snapshot['recent_candles'][-10:], 1):
            prompt += f"\n{i}. Close: £{candle['close']:.2f}, Volume: {candle['volume']:.2f}"
        
        return prompt