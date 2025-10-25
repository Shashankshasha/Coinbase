from data_layer.market_data import MarketData
from datetime import datetime

# Initialize market data client
market = MarketData()

def get_market_analysis(product_id: str = "ETH-GBP") -> dict:
    """
    Get complete market analysis with real data from Coinbase.
    Includes price, indicators, signals, and recent candles.
    """
    try:
        snapshot = market.get_full_market_snapshot(product_id)
        
        if not snapshot:
            return {"error": "Failed to fetch market data"}
        
        return {
            "timestamp": snapshot['timestamp'],
            "product_id": snapshot['product_id'],
            "current_price": snapshot['current_price'],
            "balances": snapshot['balances'],
            "indicators": snapshot['indicators'],
            "signal": snapshot['signal'],
            "summary": f"ETH is at £{snapshot['current_price']:.2f}. RSI: {snapshot['indicators'].get('rsi')}, Signal: {snapshot['signal']['signal']}"
        }
    except Exception as e:
        return {"error": f"Error fetching market data: {str(e)}"}


def get_current_price(symbol: str = "ETH-GBP") -> dict:
    """
    Get current price for a trading pair.
    """
    try:
        price_data = market.coinbase.get_current_price(symbol)
        return {
            "symbol": symbol,
            "price": price_data['price'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Error fetching price: {str(e)}"}


def get_account_balance() -> dict:
    """
    Get current account balance from Coinbase.
    """
    try:
        balances = market.coinbase.get_account_balance()
        return {
            "balances": balances,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Error fetching balance: {str(e)}"}


def analyze_trading_opportunity(product_id: str = "ETH-GBP", trade_amount: float = 100.0) -> dict:
    """
    Analyze if there's a good trading opportunity right now.
    Returns detailed analysis with recommendation.
    """
    try:
        snapshot = market.get_full_market_snapshot(product_id)
        
        if not snapshot:
            return {"error": "Failed to fetch market data"}
        
        indicators = snapshot['indicators']
        signal = snapshot['signal']
        price = snapshot['current_price']
        balance = snapshot['balances'].get('GBP', 0)
        
        # Calculate potential position
        shares = trade_amount / price
        
        analysis = {
            "recommendation": signal['signal'],
            "confidence": signal['strength'],
            "current_price": price,
            "available_balance": balance,
            "trade_amount": trade_amount,
            "estimated_shares": round(shares, 6),
            "indicators": indicators,
            "reasons": signal['reasons'],
            "risk_assessment": "LOW" if signal['strength'] < 0.5 else "MEDIUM" if signal['strength'] < 0.8 else "HIGH"
        }
        
        return analysis
        
    except Exception as e:
        return {"error": f"Error analyzing opportunity: {str(e)}"}


# Tool definitions for Claude (in Anthropic's format)
TOOL_DEFINITIONS = [
    {
        "name": "get_market_analysis",
        "description": "Get complete market analysis including price, technical indicators (RSI, EMA, MACD), trading signals, and recent price action for a cryptocurrency pair",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The trading pair symbol, e.g., 'ETH-GBP', 'BTC-USD'",
                    "default": "ETH-GBP"
                }
            }
        }
    },
    {
        "name": "get_current_price",
        "description": "Get the current spot price for a cryptocurrency trading pair",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The trading pair symbol, e.g., 'ETH-GBP'",
                    "default": "ETH-GBP"
                }
            }
        }
    },
    {
        "name": "get_account_balance",
        "description": "Get current account balances for all currencies in the Coinbase account",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "analyze_trading_opportunity",
        "description": "Analyze current market conditions and provide a trading recommendation with confidence level, risk assessment, and detailed reasoning",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The trading pair to analyze, e.g., 'ETH-GBP'",
                    "default": "ETH-GBP"
                },
                "trade_amount": {
                    "type": "number",
                    "description": "Amount in GBP to potentially trade",
                    "default": 100.0
                }
            }
        }
    }
]

# Tool execution mapping
TOOL_FUNCTIONS = {
    "get_market_analysis": get_market_analysis,
    "get_current_price": get_current_price,
    "get_account_balance": get_account_balance,
    "analyze_trading_opportunity": analyze_trading_opportunity
}