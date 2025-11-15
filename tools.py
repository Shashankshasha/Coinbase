from data_layer.market_data import MarketData
from datetime import datetime
from execution.trade_executor import TradeExecutor
from tracking.trade_logger import TradeLogger

# Initialize market data client
market = MarketData()

def get_market_analysis(product_id: str = "BTC-GBP") -> dict:
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


def get_current_price(symbol: str = "BTC-GBP") -> dict:
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


def analyze_trading_opportunity(product_id: str = "BTC-GBP", trade_amount: float = 100.0) -> dict:
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

# Initialize executor and logger
executor = TradeExecutor()
logger = TradeLogger()

def execute_trade_decision(
    action: str,
    product_id: str = "BTC-GBP",
    confidence: float = 0.75,
    reasoning: str = "",
    trade_amount: float = 50.0
) -> dict:
    """
    Execute a trading decision (BUY or SELL).
    Validates, executes, and logs the trade.
    """
    try:
        # Execute the trade
        result = executor.execute_trade(
            action=action,
            product_id=product_id,
            confidence=confidence,
            reasoning=reasoning,
            trade_amount=trade_amount
        )
        
        # Log if executed
        if result.get('executed'):
            logger.log_trade(result)
        
        return result
        
    except Exception as e:
        return {"error": f"Error executing trade: {str(e)}"}


def get_trade_history(product_id: str = None, limit: int = 5) -> dict:
    """
    Get recent trade history.
    """
    try:
        trades = logger.get_trade_history(product_id, limit)
        formatted = logger.format_trade_history(trades)
        
        return {
            "success": True,
            "count": len(trades),
            "formatted_history": formatted
        }
    except Exception as e:
        return {"error": f"Error fetching history: {str(e)}"}


def get_performance_summary() -> dict:
    """
    Get overall trading performance summary.
    """
    try:
        summary = logger.get_performance_summary()
        pnl_data = logger.db.get_total_pnl()
        
        return {
            "success": True,
            "summary": summary,
            "stats": pnl_data
        }
    except Exception as e:
        return {"error": f"Error fetching performance: {str(e)}"}


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
                    "description": "The trading pair symbol, e.g., 'BTC-GBP', 'SOL-GBP', 'ETH-GBP'",
                    "default": "BTC-GBP"
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
                    "description": "The trading pair symbol, e.g., 'BTC-GBP', 'SOL-GBP', 'ETH-GBP'",
                    "default": "BTC-GBP"
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
                    "description": "The trading pair to analyze, e.g., 'BTC-GBP', 'SOL-GBP', 'ETH-GBP'",
                    "default": "BTC-GBP"
                },
                "trade_amount": {
                    "type": "number",
                    "description": "Amount in GBP to potentially trade",
                    "default": 100.0
                }
            }
        }
    },
    {
        "name": "execute_trade_decision",
        "description": "Execute a trading decision (BUY or SELL). This will validate the trade against safety rules, execute it (paper or live mode), and log it to the database. Use this after analyzing the market and deciding on a trade.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Trade action: 'BUY' or 'SELL'",
                    "enum": ["BUY", "SELL"]
                },
                "product_id": {
                    "type": "string",
                    "description": "Trading pair, e.g., 'BTC-GBP', 'SOL-GBP', 'ETH-GBP'",
                    "default": "BTC-GBP"
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence level (0.0 to 1.0)",
                    "minimum": 0,
                    "maximum": 1
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation of why this trade is recommended"
                },
                "trade_amount": {
                    "type": "number",
                    "description": "Amount in GBP to trade",
                    "default": 50.0
                }
            },
            "required": ["action", "confidence", "reasoning"]
        }
    },
    {
        "name": "get_trade_history",
        "description": "Get recent trade history with details",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Filter by trading pair (optional)"
                },
                "limit": {
                    "type": "number",
                    "description": "Number of trades to return",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "get_performance_summary",
        "description": "Get overall trading performance summary including P&L, win rate, and statistics",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

# Tool execution mapping
TOOL_FUNCTIONS = {
    "get_market_analysis": get_market_analysis,
    "get_current_price": get_current_price,
    "get_account_balance": get_account_balance,
    "analyze_trading_opportunity": analyze_trading_opportunity,
    "execute_trade_decision": execute_trade_decision,
    "get_trade_history": get_trade_history,
    "get_performance_summary": get_performance_summary
}