from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET
import time

class CoinbaseClient:
    """
    Wrapper for Coinbase Advanced Trade API.
    FIXED for Cloud API Keys (JWT authentication)
    WITH RETRY LOGIC for connection errors
    """
    
    def __init__(self):
        # CRITICAL FIX: Handle newline encoding in private key
        api_secret = COINBASE_API_SECRET

        # Check if credentials are provided
        if not COINBASE_API_KEY or not COINBASE_API_SECRET:
            print("=" * 70)
            print("❌ MISSING COINBASE API CREDENTIALS")
            print("=" * 70)
            print("\nYour .env file is missing API credentials!")
            print("\nTo fix this:")
            print("1. Go to Coinbase Developer Portal: https://portal.cdp.coinbase.com/")
            print("2. Create a new API key (Cloud API)")
            print("3. Add to your .env file:")
            print("   COINBASE_API_KEY=organizations/your-org-id/apiKeys/your-key-id")
            print("   COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----\\n...\\n-----END EC PRIVATE KEY-----")
            print("\n⚠️  Note: Use double quotes and \\\\n for newlines in the private key")
            print("=" * 70)
            raise ValueError("Missing COINBASE_API_KEY or COINBASE_API_SECRET in .env file")

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
            print("✅ Coinbase API client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Coinbase client: {e}")
            print("Make sure you have:")
            print("  1. Correct Cloud API key format (organizations/...)")
            print("  2. Valid EC private key")
            print("  3. Latest coinbase SDK: pip install --upgrade coinbase-advanced-py")
            raise
    
    def _retry_request(self, func, *args, max_retries=3, **kwargs):
        """
        Wrapper to retry API requests on connection errors
        """
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except ConnectionResetError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)  # Exponential backoff: 2s, 4s, 6s
                    print(f"⚠️  Connection reset, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Failed after {max_retries} attempts: {e}")
                    return None
            except ConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    print(f"⚠️  Connection error, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Failed after {max_retries} attempts: {e}")
                    return None
            except Exception as e:
                # Don't retry on other errors (auth, validation, etc)
                error_msg = str(e).lower()
                if 'unauthenticated' in error_msg or 'authentication' in error_msg or 'unauthorized' in error_msg:
                    print(f"❌ Authentication Error: {e}")
                    print("⚠️  Check your API credentials in the .env file")
                    print("   Make sure COINBASE_API_KEY and COINBASE_API_SECRET are correct")
                else:
                    print(f"❌ Error: {e}")
                return None
    
    def get_current_price(self, product_id: str = "SOL-GBP") -> dict:
        """
        Get current spot price for a trading pair.
        WITH AUTOMATIC RETRY on connection errors
        
        Args:
            product_id: Trading pair (e.g., 'SOL-GBP', 'BTC-USD')
            
        Returns:
            dict: {"price": 2345.67, "product_id": "SOL-GBP"}
        """
        def _fetch():
            ticker = self.client.get_product(product_id)
            price = float(ticker['price'])
            return {
                "product_id": product_id,
                "price": price
            }
        
        return self._retry_request(_fetch)
    
    def get_candles(self, product_id: str = "SOL-GBP", granularity: str = "FIFTEEN_MINUTE", limit: int = 100) -> list:
        """
        Get historical candle data.
        WITH AUTOMATIC RETRY on connection errors
        
        Args:
            product_id: Trading pair
            granularity: Candle size - ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, 
                        ONE_HOUR, SIX_HOUR, ONE_DAY
            limit: Number of candles to fetch (max 300)
            
        Returns:
            list: List of candles with [timestamp, low, high, open, close, volume]
        """
        def _fetch():
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
        
        result = self._retry_request(_fetch)
        return result if result is not None else []
    
    def get_account_balance(self) -> dict:
        """
        Get account balances for all currencies.
        WITH AUTOMATIC RETRY on connection errors
        
        Returns:
            dict: {"GBP": 1000.50, "ETH": 0.5, ...}
        """
        def _fetch():
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
        
        result = self._retry_request(_fetch)
        return result if result is not None else {}
    
    def get_product_info(self, product_id: str = "SOL-GBP") -> dict:
        """
        Get detailed product information including fees.
        WITH AUTOMATIC RETRY on connection errors
        
        Returns:
            dict: Product details
        """
        def _fetch():
            product = self.client.get_product(product_id)
            return product
        
        result = self._retry_request(_fetch)
        return result if result is not None else {}