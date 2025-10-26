import hmac
import hashlib
import time
import requests
import json
from config import COINBASE_API_KEY, COINBASE_API_SECRET

class OrderManager:
    """
    Handles order placement on Coinbase.
    FIXED: Proper precision handling for different cryptocurrencies
    ADDED: Order history lookup functionality
    EXPANDED: Support for more crypto pairs
    """
    
    def __init__(self):
        self.api_key = COINBASE_API_KEY
        self.api_secret = COINBASE_API_SECRET
        self.api_url = "https://api.coinbase.com/api/v3/brokerage"
    
    def _generate_client_order_id(self):
        """Generate unique client order ID."""
        return f"order_{int(time.time() * 1000)}"
    
    def _sign_request(self, method, path, body=""):
        """
        Sign API request using HMAC SHA256.
        """
        timestamp = str(int(time.time()))
        message = f"{timestamp}{method}{path}{body}"
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, json_data=None, params=None):
        """
        Make authenticated request to Coinbase API.
        """
        path = endpoint.replace(self.api_url, "")
        body = json.dumps(json_data) if json_data else ""
        
        headers = self._sign_request(method, path, body)
        
        try:
            if method == "GET":
                response = requests.get(endpoint, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(endpoint, headers=headers, json=json_data)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def place_market_buy(self, product_id, amount_gbp):
        """
        Place a market buy order.
        
        Args:
            product_id: e.g., 'SOL-GBP', 'BTC-GBP', 'ETH-GBP'
            amount_gbp: Amount in GBP to spend
            
        Returns:
            Order result with success status
        """
        try:
            order_config = {
                "market_market_ioc": {
                    "quote_size": str(round(amount_gbp, 2))
                }
            }
            
            payload = {
                "client_order_id": self._generate_client_order_id(),
                "product_id": product_id,
                "side": "BUY",
                "order_configuration": order_config
            }
            
            endpoint = f"{self.api_url}/orders"
            response = self._make_request("POST", endpoint, json_data=payload)
            
            if response and response.get("success"):
                return {
                    "success": True,
                    "order_id": response.get("order_id"),
                    "raw_response": response
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error_response", {}).get("message", "Unknown error"),
                    "error_response": response.get("error_response"),
                    "raw_response": str(response)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def place_market_sell(self, product_id, crypto_amount):
        """
        Place a market sell order.
        FIXED: Proper precision rounding for different cryptocurrencies
        EXPANDED: Support for all major cryptos
        
        Args:
            product_id: e.g., 'SOL-GBP', 'BTC-GBP', etc.
            crypto_amount: Amount of crypto to sell
            
        Returns:
            Order result with success status
        """
        try:
            # EXPANDED PRECISION MAP - Coinbase requirements per crypto
            precision_map = {
                # Major coins
                'BTC': 8,      # Bitcoin - 8 decimals
                'ETH': 6,      # Ethereum - 6 decimals
                
                # Layer 1s
                'SOL': 3,      # Solana - 3 decimals
                'ADA': 2,      # Cardano - 2 decimals
                'DOT': 4,      # Polkadot - 4 decimals
                'AVAX': 4,     # Avalanche - 4 decimals
                'ATOM': 4,     # Cosmos - 4 decimals
                'NEAR': 4,     # Near - 4 decimals
                'ALGO': 2,     # Algorand - 2 decimals
                
                # Layer 2s & Scaling
                'MATIC': 2,    # Polygon - 2 decimals
                'ARB': 4,      # Arbitrum - 4 decimals
                'OP': 4,       # Optimism - 4 decimals
                
                # Meme/High supply coins
                'DOGE': 0,     # Dogecoin - whole numbers
                'SHIB': 0,     # Shiba Inu - whole numbers
                'PEPE': 0,     # Pepe - whole numbers
                
                # DeFi tokens
                'UNI': 4,      # Uniswap - 4 decimals
                'LINK': 4,     # Chainlink - 4 decimals
                'AAVE': 4,     # Aave - 4 decimals
                'MKR': 6,      # Maker - 6 decimals
                'SNX': 4,      # Synthetix - 4 decimals
                'COMP': 6,     # Compound - 6 decimals
                
                # Alternative L1s
                'XRP': 2,      # Ripple - 2 decimals
                'XLM': 2,      # Stellar - 2 decimals
                'TRX': 0,      # Tron - whole numbers
                'VET': 0,      # VeChain - whole numbers
                
                # Stablecoins
                'USDT': 2,     # Tether - 2 decimals
                'USDC': 2,     # USD Coin - 2 decimals
                'DAI': 6,      # Dai - 6 decimals
                'BUSD': 2,     # Binance USD - 2 decimals
                
                # Other popular
                'LTC': 6,      # Litecoin - 6 decimals
                'BCH': 6,      # Bitcoin Cash - 6 decimals
                'ETC': 6,      # Ethereum Classic - 6 decimals
                'FIL': 4,      # Filecoin - 4 decimals
                'ICP': 4,      # Internet Computer - 4 decimals
                'APT': 4,      # Aptos - 4 decimals
                'SUI': 4,      # Sui - 4 decimals
            }
            
            # Extract crypto symbol (e.g., 'SOL' from 'SOL-GBP')
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
            
            # Create order configuration
            order_config = {
                "market_market_ioc": {
                    "base_size": str(rounded_amount)
                }
            }
            
            payload = {
                "client_order_id": self._generate_client_order_id(),
                "product_id": product_id,
                "side": "SELL",
                "order_configuration": order_config
            }
            
            endpoint = f"{self.api_url}/orders"
            response = self._make_request("POST", endpoint, json_data=payload)
            
            if response and response.get("success"):
                return {
                    "success": True,
                    "order_id": response.get("order_id"),
                    "crypto_amount": rounded_amount,
                    "raw_response": response
                }
            else:
                error_response = response.get("error_response", {})
                error_msg = error_response.get("message", "Unknown error")
                error_code = error_response.get("error", "UNKNOWN")
                
                print(f"❌ Coinbase Error: {error_code} - {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "error_code": error_code,
                    "error_response": error_response,
                    "raw_response": str(response)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_recent_orders(self, product_id=None, limit=50):
        """
        Get recent filled orders from Coinbase.
        
        Args:
            product_id: Filter by product (optional, e.g., 'SOL-GBP')
            limit: Number of orders to fetch (1-1000)
            
        Returns:
            List of recent orders with details
        """
        try:
            endpoint = f"{self.api_url}/orders/historical/batch"
            
            params = {
                "limit": str(min(limit, 1000)),
                "order_status": "FILLED"
            }
            
            if product_id:
                params["product_id"] = product_id
            
            response = self._make_request("GET", endpoint, params=params)
            
            if not response or not response.get("orders"):
                print(f"   ⚠️ No order history found")
                return []
            
            orders = []
            for order in response.get("orders", []):
                try:
                    side = order.get("side", "").upper()
                    filled_size = float(order.get("filled_size", 0))
                    avg_price = float(order.get("average_filled_price", 0))
                    total_value = float(order.get("total_value_after_fees", 0))
                    created_time = order.get("created_time", "")
                    
                    orders.append({
                        "order_id": order.get("order_id"),
                        "product_id": order.get("product_id"),
                        "side": side,
                        "size": filled_size,
                        "price": avg_price,
                        "cost": abs(total_value),
                        "timestamp": created_time
                    })
                except (ValueError, TypeError):
                    continue
            
            print(f"   📊 Found {len(orders)} filled orders")
            return orders
            
        except Exception as e:
            print(f"   ⚠️ Error fetching order history: {e}")
            return []
    
    def get_order_details(self, order_id):
        """
        Get details of a specific order.
        
        Args:
            order_id: The order ID to fetch
            
        Returns:
            Order details dict
        """
        try:
            endpoint = f"{self.api_url}/orders/historical/{order_id}"
            response = self._make_request("GET", endpoint)
            
            if response and response.get("order"):
                return {
                    "success": True,
                    "order": response.get("order")
                }
            else:
                return {
                    "success": False,
                    "error": "Order not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }