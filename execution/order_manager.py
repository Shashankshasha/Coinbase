from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET
import time


class OrderManager:
    """
    Handles order placement on Coinbase using Advanced Trade API.
    Uses official Coinbase SDK for proper JWT authentication with Cloud API keys.
    """
    
    def __init__(self):
        # Fix newlines in private key
        api_secret = COINBASE_API_SECRET
        if api_secret and '\\n' in api_secret:
            api_secret = api_secret.replace('\\n', '\n')
        
        # Initialize SDK client - handles JWT authentication automatically
        self.client = RESTClient(
            api_key=COINBASE_API_KEY,
            api_secret=api_secret
        )
    
    def _generate_client_order_id(self):
        """Generate unique client order ID."""
        return f"order_{int(time.time() * 1000)}"
    
    def place_market_buy(self, product_id: str, amount_gbp: float) -> dict:
        """
        Place a market buy order.
        
        Args:
            product_id: e.g., 'SOL-GBP', 'BTC-GBP', 'ETH-GBP'
            amount_gbp: Amount in GBP to spend
            
        Returns:
            Order result with success status
        """
        try:
            print(f"💰 Buying {product_id} with £{amount_gbp:.2f}")
            
            # Use SDK's market_order_buy method (handles JWT internally)
            order = self.client.market_order_buy(
                client_order_id=self._generate_client_order_id(),
                product_id=product_id,
                quote_size=str(round(amount_gbp, 2))
            )
            
            # Parse response
            if hasattr(order, 'success') and order.success:
                order_id = order.order_id if hasattr(order, 'order_id') else 'unknown'
                
                print(f"✅ BUY order placed: {order_id}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "product_id": product_id,
                    "side": "BUY",
                    "amount_gbp": amount_gbp
                }
            else:
                # Handle error
                error_msg = "Unknown error"
                if hasattr(order, 'error_response'):
                    error_response = order.error_response
                    if isinstance(error_response, dict):
                        error_msg = error_response.get('message', str(error_response))
                    else:
                        error_msg = str(error_response)
                
                print(f"❌ BUY failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "error_response": getattr(order, 'error_response', {})
                }
                
        except Exception as e:
            print(f"❌ Exception during BUY: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def place_market_sell(self, product_id: str, crypto_amount: float) -> dict:
        """
        Place a market sell order.
        
        Args:
            product_id: e.g., 'SOL-GBP', 'BTC-GBP', etc.
            crypto_amount: Amount of crypto to sell
            
        Returns:
            Order result with success status
        """
        try:
            # PRECISION MAP - Coinbase requirements per crypto
            precision_map = {
                # Major coins
                'BTC': 8, 'ETH': 6,
                
                # Layer 1s
                'SOL': 3, 'ADA': 2, 'DOT': 4, 'AVAX': 4, 'ATOM': 4,
                'NEAR': 4, 'ALGO': 2,
                
                # Layer 2s
                'MATIC': 2, 'ARB': 4, 'OP': 4,
                
                # Meme coins
                'DOGE': 0, 'SHIB': 0, 'PEPE': 0,
                
                # DeFi
                'UNI': 4, 'LINK': 4, 'AAVE': 4, 'MKR': 6, 'SNX': 4, 'COMP': 6,
                
                # Alternative L1s
                'XRP': 2, 'XLM': 2, 'TRX': 0, 'VET': 0,
                
                # Stablecoins
                'USDT': 2, 'USDC': 2, 'DAI': 6, 'BUSD': 2,
                
                # Other
                'LTC': 6, 'BCH': 6, 'ETC': 6, 'FIL': 4, 'ICP': 4,
                'APT': 4, 'SUI': 4,
            }
            
            # Extract crypto symbol
            crypto_symbol = product_id.split('-')[0].upper()
            
            # Get precision (default 4 if not in map)
            precision = precision_map.get(crypto_symbol, 4)
            
            # Round to appropriate precision
            rounded_amount = round(crypto_amount, precision)
            
            print(f"💰 Selling {crypto_symbol}: {crypto_amount:.10f} → {rounded_amount} (precision: {precision})")
            
            if rounded_amount <= 0:
                return {
                    "success": False,
                    "error": f"Invalid sell amount after rounding: {rounded_amount}"
                }
            
            # Use SDK's market_order_sell method (handles JWT internally)
            order = self.client.market_order_sell(
                client_order_id=self._generate_client_order_id(),
                product_id=product_id,
                base_size=str(rounded_amount)
            )
            
            # Parse response
            if hasattr(order, 'success') and order.success:
                order_id = order.order_id if hasattr(order, 'order_id') else 'unknown'
                
                print(f"✅ SELL order placed: {order_id}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "product_id": product_id,
                    "side": "SELL",
                    "crypto_amount": rounded_amount
                }
            else:
                # Handle error
                error_msg = "Unknown error"
                error_code = "UNKNOWN"
                
                if hasattr(order, 'error_response'):
                    error_response = order.error_response
                    if isinstance(error_response, dict):
                        error_msg = error_response.get('message', str(error_response))
                        error_code = error_response.get('error', 'UNKNOWN')
                    else:
                        error_msg = str(error_response)
                
                print(f"❌ Coinbase Error: {error_code} - {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "error_code": error_code,
                    "error_response": getattr(order, 'error_response', {})
                }
                
        except Exception as e:
            print(f"❌ Exception during SELL: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_recent_orders(self, product_id=None, limit=50):
        """
        Get recent filled orders from Coinbase.
        
        Args:
            product_id: Filter by product (optional)
            limit: Number of orders to fetch (1-1000)
            
        Returns:
            List of recent orders
        """
        try:
            # Use SDK to get orders
            orders_list = self.client.list_orders(
                product_id=product_id,
                order_status=["FILLED"],
                limit=min(limit, 1000)
            )
            
            if not orders_list or not hasattr(orders_list, 'orders'):
                print(f"   ⚠️ No order history found")
                return []
            
            parsed_orders = []
            for order in orders_list.orders:
                try:
                    side = order.side if hasattr(order, 'side') else 'UNKNOWN'
                    filled_size = float(order.filled_size) if hasattr(order, 'filled_size') else 0
                    avg_price = float(order.average_filled_price) if hasattr(order, 'average_filled_price') else 0
                    
                    parsed_orders.append({
                        "order_id": order.order_id if hasattr(order, 'order_id') else None,
                        "product_id": order.product_id if hasattr(order, 'product_id') else None,
                        "side": side,
                        "size": filled_size,
                        "price": avg_price,
                        "timestamp": order.created_time if hasattr(order, 'created_time') else None
                    })
                except (ValueError, TypeError, AttributeError):
                    continue
            
            print(f"   📊 Found {len(parsed_orders)} filled orders")
            return parsed_orders
            
        except Exception as e:
            print(f"   ⚠️ Error fetching order history: {e}")
            return []