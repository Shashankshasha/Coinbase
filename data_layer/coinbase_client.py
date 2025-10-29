from coinbase.rest import RESTClient
from coinbase import jwt_generator
from config import COINBASE_API_KEY, COINBASE_API_SECRET
import json

class CoinbaseClient:
    """
    Wrapper for Coinbase Advanced Trade API.
    FIXED for Cloud API Keys (JWT authentication)
    """
    
    def __init__(self):
        # CRITICAL FIX: Handle newline encoding in private key
        api_secret = COINBASE_API_SECRET
        
        # Convert literal \n to actual newlines if needed
        if api_secret and '\\n' in api_secret:
            api_secret = api_secret.replace('\\n', '\n')
        
        # For Cloud API keys, we need to initialize differently
        # The SDK handles JWT generation internally when given proper credentials
        try:
            self.client = RESTClient(
                api_key=COINBASE_API_KEY,
                api_secret=api_secret
            )
        except Exception as e:
            print(f"❌ Error initializing Coinbase client: {e}")
            print("Make sure you have:")
            print("  1. Correct Cloud API key format (organizations/...)")
            print("  2. Valid EC private key")
            print("  3. Latest coinbase SDK: pip install --upgrade coinbase-advanced-py")
            raise
    
    def get_current_price(self, product_id: str = "SOL-GBP") -> dict:
        """
        Get current spot price for a trading pair.
        
        Args:
            product_id: Trading pair (e.g., 'SOL-GBP', 'BTC-USD')
            
        Returns:
            dict: {"price": 2345.67, "product_id": "SOL-GBP"}
        """
        try:
            ticker = self.client.get_product(product_id)
            price = float(ticker['price'])
            
            return {
                "product_id": product_id,
                "price": price
            }
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def get_candles(self, product_id: str = "SOL-GBP", granularity: str = "FIFTEEN_MINUTE", limit: int = 100) -> list:
        """
        Get historical candle data.
        
        Args:
            product_id: Trading pair
            granularity: Candle size - ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, 
                        ONE_HOUR, SIX_HOUR, ONE_DAY
            limit: Number of candles to fetch (max 300)
            
        Returns:
            list: List of candles with [timestamp, low, high, open, close, volume]
        """
        try:
            import time
            
            # Calculate start and end times based on limit
            granularity_seconds = {
                "ONE_MINUTE": 60,
                "FIVE_MINUTE": 300,
                "FIFTEEN_MINUTE": 900,
                "THIRTY_MINUTE": 1800,
                "ONE_HOUR": 3600,
                "TWO_HOUR": 7200,
                "SIX_HOUR": 21600,
                "ONE_DAY": 86400,
            }
            
            seconds = granularity_seconds.get(granularity, 900)
            end_time = int(time.time())
            start_time = end_time - (seconds * limit)
            
            response = self.client.get_candles(
                product_id=product_id,
                start=str(start_time),
                end=str(end_time),
                granularity=granularity
            )
            
            # The response is an object, not a dict - access candles attribute directly
            candles = response.candles if hasattr(response, 'candles') else []
            
            # Parse candles into easier format
            parsed_candles = []
            for candle in candles:
                parsed_candles.append({
                    'timestamp': int(candle.start),
                    'open': float(candle.open),
                    'high': float(candle.high),
                    'low': float(candle.low),
                    'close': float(candle.close),
                    'volume': float(candle.volume)
                })
            
            # Sort by timestamp (oldest first)
            parsed_candles.sort(key=lambda x: x['timestamp'])
            
            return parsed_candles
            
        except Exception as e:
            print(f"Error fetching candles: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_account_balance(self) -> dict:
        """
        Get account balances for all currencies.
        
        Returns:
            dict: {"GBP": 1000.50, "ETH": 0.5, ...}
        """
        try:
            response = self.client.get_accounts()
            
            # Get accounts from response
            if hasattr(response, 'accounts'):
                accounts = response.accounts
            elif isinstance(response, dict):
                accounts = response.get('accounts', [])
            else:
                accounts = []
            
            balances = {}
            for account in accounts:
                try:
                    # Try dict access first (most common)
                    if isinstance(account, dict):
                        currency = account.get('currency')
                        available_balance = account.get('available_balance', {})
                        available = float(available_balance.get('value', 0))
                    else:
                        # Try object access
                        currency = getattr(account, 'currency', None)
                        available_balance = getattr(account, 'available_balance', None)
                        if isinstance(available_balance, dict):
                            available = float(available_balance.get('value', 0))
                        else:
                            available = float(getattr(available_balance, 'value', 0))
                    
                    if available > 0 and currency:
                        balances[currency] = available
                except Exception as e:
                    # Skip accounts that can't be parsed
                    continue
            
            return balances
            
        except Exception as e:
            print(f"Error fetching balances: {e}")
            # Return empty dict on error - not critical for trading analysis
            return {}
    
    def get_product_info(self, product_id: str = "SOL-GBP") -> dict:
        """
        Get detailed product information including fees.
        
        Returns:
            dict: Product details
        """
        try:
            product = self.client.get_product(product_id)
            return product
        except Exception as e:
            print(f"Error fetching product info: {e}")
            return {}