from tracking.database import TradingDatabase
from datetime import datetime
import json
import time


class TradeLogger:
    """
    Logs trades to database and provides reporting.
    FIXED: Handles missing/unknown trade_id properly
    """
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db = TradingDatabase(db_path)
    
    def log_trade(self, trade_result: dict) -> bool:
        """
        Log a trade execution result to the database.
        FIXED: Generates trade_id if missing or 'unknown'
        
        Args:
            trade_result: Result dict from TradeExecutor
        Returns:
            Success boolean
        """
        try:
            if not trade_result.get('executed'):
                print(f"⚠️  Trade not executed, skipping log")
                return False
            
            # ================================================================
            # FIX: Generate trade_id if missing or 'unknown'
            # ================================================================
            trade_id = trade_result.get('order_id')
            
            if not trade_id or trade_id == 'unknown':
                # Generate unique trade_id from timestamp
                trade_id = f"trade_{int(time.time() * 1000)}"
                trade_result['order_id'] = trade_id
                trade_result['trade_id'] = trade_id
                print(f"   ⚠️  Generated trade_id: {trade_id}")
            
            # Ensure trade_id is set
            if 'trade_id' not in trade_result:
                trade_result['trade_id'] = trade_id
            
            # ================================================================
            # Fix timestamp format if needed
            # ================================================================
            timestamp = trade_result.get('timestamp')
            if isinstance(timestamp, str):
                # Handle ISO format with 'Z' timezone
                timestamp = timestamp.replace('Z', '+00:00')
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except:
                    timestamp = datetime.now()
                trade_result['timestamp'] = timestamp
            elif not timestamp:
                trade_result['timestamp'] = datetime.now()
            
            # ================================================================
            # Add to database
            # ================================================================
            self.db.add_trade(trade_result)
            print(f"📝 Trade logged to database: {trade_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging trade: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_trade_history(self, product_id: str = None, limit: int = 10) -> list:
        """
        Get recent trade history.
        
        Args:
            product_id: Filter by product (optional)
            limit: Number of trades to return
        Returns:
            List of trade records
        """
        if product_id:
            trades = self.db.get_trades_by_product(product_id)
        else:
            trades = self.db.get_all_trades()
        
        return trades[:limit]
    
    def format_trade_history(self, trades: list) -> str:
        """
        Format trade history into readable string.
        """
        if not trades:
            return "No trades found"
        
        output = "\n" + "="*70 + "\n"
        output += "TRADE HISTORY\n"
        output += "="*70 + "\n\n"
        
        for trade in trades:
            status = "🟢" if trade.action == "BUY" else "🔴"
            pnl_str = ""
            
            if trade.profit_loss is not None:
                pnl_emoji = "💰" if trade.profit_loss > 0 else "📉"
                pnl_str = f" {pnl_emoji} P&L: £{trade.profit_loss:.2f} ({trade.profit_loss_pct:.2f}%)"
            
            output += f"{status} {trade.action} {trade.crypto_amount:.6f} {trade.product_id}\n"
            output += f"   Price: £{trade.price:.2f} | Amount: £{trade.amount_gbp:.2f} | Fee: £{trade.fee:.2f}\n"
            output += f"   Confidence: {trade.confidence:.0%} | Mode: {trade.mode}\n"
            output += f"   Time: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{pnl_str}\n"
            
            if trade.reasoning:
                output += f"   Reasoning: {trade.reasoning[:80]}...\n"
            
            output += "\n"
        
        return output
    
    def get_performance_summary(self) -> str:
        """
        Get overall performance summary.
        """
        pnl_data = self.db.get_total_pnl()
        
        output = "\n" + "="*70 + "\n"
        output += "PERFORMANCE SUMMARY\n"
        output += "="*70 + "\n\n"
        
        output += f"💰 Total P&L: £{pnl_data['total_pnl']:.2f}\n"
        output += f"📊 Total Trades: {pnl_data['total_trades']}\n"
        output += f"✅ Winning Trades: {pnl_data['winning_trades']}\n"
        output += f"❌ Losing Trades: {pnl_data['losing_trades']}\n"
        output += f"🎯 Win Rate: {pnl_data['win_rate']:.1f}%\n"
        
        if pnl_data['avg_profit'] > 0:
            output += f"📈 Avg Profit per Win: £{pnl_data['avg_profit']:.2f}\n"
        
        if pnl_data['avg_loss'] < 0:
            output += f"📉 Avg Loss per Loss: £{pnl_data['avg_loss']:.2f}\n"
        
        output += "="*70 + "\n"
        
        return output
    
    def close(self):
        """
        Close database connection.
        """
        self.db.close()