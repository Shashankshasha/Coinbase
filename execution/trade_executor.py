from execution.order_manager import OrderManager
from decision_engine.validator import DecisionValidator
from data_layer.market_data import MarketData
from config import TRADING_MODE, TRADE_AMOUNT_GBP
from datetime import datetime
import json

class TradeExecutor:
    """
    Executes trades based on validated decisions.
    Handles both paper trading (simulation) and live trading.
    FIXED: Proper SELL logic using actual crypto balance
    """
    
    def __init__(self):
        self.order_manager = OrderManager()
        self.validator = DecisionValidator()
        self.market_data = MarketData()
        self.paper_trades = []  # Store paper trades for testing
    
    def execute_trade(
        self,
        action: str,
        product_id: str,
        confidence: float,
        reasoning: str,
        trade_amount: float = None
    ) -> dict:
        """
        Execute a trade (paper or live based on config).
        
        Args:
            action: 'BUY' or 'SELL'
            product_id: Trading pair (e.g., 'SOL-GBP')
            confidence: Confidence level (0-1)
            reasoning: Claude's reasoning for the trade
            trade_amount: Amount in GBP (default from config)
            
        Returns:
            Execution result with details
        """
        trade_amount = trade_amount or TRADE_AMOUNT_GBP
        
        print(f"\n{'='*60}")
        print(f"🎯 TRADE EXECUTION REQUEST")
        print(f"{'='*60}")
        print(f"Action: {action}")
        print(f"Product: {product_id}")
        print(f"Amount: £{trade_amount:.2f}")
        print(f"Confidence: {confidence:.0%}")
        print(f"Mode: {TRADING_MODE}")
        print(f"{'='*60}\n")
        
        # Get current market data
        snapshot = self.market_data.get_full_market_snapshot(product_id)
        if not snapshot:
            return {"success": False, "error": "Failed to fetch market data"}
        
        current_price = snapshot['current_price']
        available_balance = snapshot['balances'].get('GBP', 0)
        
        # Validate the trade
        validation = self.validator.validate_trade(
            action=action,
            product_id=product_id,
            confidence=confidence,
            trade_amount=trade_amount,
            available_balance=available_balance
        )
        
        print(self.validator.format_validation_report(validation))
        
        # If not approved, return validation result
        if not validation["approved"]:
            return {
                "success": False,
                "executed": False,
                "validation": validation,
                "message": validation["summary"]
            }
        
        # Execute based on trading mode
        if TRADING_MODE == "paper":
            result = self._execute_paper_trade(
                action, product_id, trade_amount, current_price, confidence, reasoning
            )
        else:
            result = self._execute_live_trade(
                action, product_id, trade_amount, current_price, snapshot
            )
        
        # Record execution if successful
        if result["success"]:
            crypto_amount = trade_amount / current_price if action == "BUY" else result.get("crypto_amount", 0)
            self.validator.record_execution(product_id, action, crypto_amount, current_price)
        
        return result
    
    def _execute_paper_trade(
        self,
        action: str,
        product_id: str,
        amount_gbp: float,
        price: float,
        confidence: float,
        reasoning: str
    ) -> dict:
        """
        Simulate a trade (paper trading).
        """
        crypto_amount = amount_gbp / price
        fee = amount_gbp * 0.006  # 0.6% Coinbase fee
        
        paper_trade = {
            "success": True,
            "executed": True,
            "mode": "PAPER",
            "action": action,
            "product_id": product_id,
            "amount_gbp": amount_gbp,
            "crypto_amount": crypto_amount,
            "price": price,
            "fee": fee,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "trade_id": f"paper_{int(datetime.now().timestamp())}"
        }
        
        self.paper_trades.append(paper_trade)
        
        print(f"\n📄 PAPER TRADE EXECUTED")
        print(f"{'='*60}")
        print(f"✅ {action} {crypto_amount:.6f} {product_id.split('-')[0]}")
        print(f"💰 Price: £{price:.2f}")
        print(f"💵 Total: £{amount_gbp:.2f}")
        print(f"💸 Fee: £{fee:.2f}")
        print(f"🎯 Confidence: {confidence:.0%}")
        print(f"📝 Trade ID: {paper_trade['trade_id']}")
        print(f"{'='*60}\n")
        
        return paper_trade
    
    def _execute_live_trade(
        self,
        action: str,
        product_id: str,
        amount_gbp: float,
        price: float,
        snapshot: dict = None
    ) -> dict:
        """
        Execute a real trade on Coinbase.
        FIXED: For SELL orders, uses actual crypto balance from Coinbase
        """
        print(f"\n⚠️  EXECUTING LIVE TRADE ON COINBASE ⚠️\n")
        
        if action == "BUY":
            # BUY: Use specified GBP amount
            order_result = self.order_manager.place_market_buy(product_id, amount_gbp)
            
        elif action == "SELL":
            # SELL: Use actual crypto balance from Coinbase (not calculated from GBP!)
            # This prevents precision errors and ensures we sell what we actually have
            
            # Get actual crypto balance
            crypto_symbol = product_id.split('-')[0]
            if snapshot and 'balances' in snapshot:
                actual_crypto_balance = snapshot['balances'].get(crypto_symbol, 0)
            else:
                # Fetch fresh snapshot if not provided
                fresh_snapshot = self.market_data.get_full_market_snapshot(product_id)
                actual_crypto_balance = fresh_snapshot['balances'].get(crypto_symbol, 0)
            
            print(f"💰 Selling actual balance: {actual_crypto_balance:.6f} {crypto_symbol}")
            
            if actual_crypto_balance <= 0:
                return {
                    "success": False,
                    "error": f"No {crypto_symbol} balance to sell",
                    "executed": False
                }
            
            # Pass the actual crypto amount to sell
            order_result = self.order_manager.place_market_sell(
                product_id, 
                crypto_amount=actual_crypto_balance
            )
        else:
            return {"success": False, "error": "Invalid action"}
        
        # Process result
        if order_result.get("success"):
            print(f"\n✅ LIVE TRADE EXECUTED")
            print(f"{'='*60}")
            print(f"Order ID: {order_result.get('order_id')}")
            print(f"Action: {action}")
            print(f"Product: {product_id}")
            if action == "BUY":
                print(f"Amount: £{amount_gbp:.2f}")
            else:
                crypto_symbol = product_id.split('-')[0]
                actual_amount = order_result.get('crypto_amount', 0)
                print(f"Sold: {actual_amount:.6f} {crypto_symbol}")
            print(f"{'='*60}\n")
        else:
            print(f"\n❌ TRADE FAILED: {order_result.get('error')}\n")
            error_response = order_result.get('error_response', {})
            if error_response:
                print(f"   Error Code: {error_response.get('error', 'Unknown')}")
                print(f"   Message: {error_response.get('message', 'No message')}")
        
        return {
            "success": order_result.get("success", False),
            "executed": order_result.get("success", False),
            "mode": "LIVE",
            "action": action,
            "product_id": product_id,
            "amount_gbp": amount_gbp,
            "order_id": order_result.get("order_id"),
            "timestamp": datetime.now().isoformat(),
            **order_result
        }
    
    def get_paper_trades(self) -> list:
        """
        Get all paper trades.
        """
        return self.paper_trades
    
    def get_current_position(self, product_id: str) -> dict:
        """
        Get current open position.
        """
        return self.validator.get_current_position(product_id)