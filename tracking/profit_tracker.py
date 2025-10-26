from tracking.database import TradingDatabase

class ProfitTracker:
    """
    Tracks and calculates profit/loss for trades.
    """
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db = TradingDatabase(db_path)
    
    def calculate_pnl(self, entry_trade, exit_trade) -> dict:
        """
        Calculate P&L between entry and exit trades.
        
        Args:
            entry_trade: BUY trade
            exit_trade: SELL trade
            
        Returns:
            P&L calculation
        """
        entry_cost = entry_trade['amount_gbp'] + entry_trade['fee']
        exit_revenue = exit_trade['amount_gbp'] - exit_trade['fee']
        
        profit_loss = exit_revenue - entry_cost
        profit_loss_pct = (profit_loss / entry_cost) * 100
        
        return {
            'entry_cost': entry_cost,
            'exit_revenue': exit_revenue,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
            'entry_price': entry_trade['price'],
            'exit_price': exit_trade['price']
        }
    
    def close_position_with_pnl(self, product_id: str, exit_price: float, exit_amount_gbp: float):
        """
        Close an open position and calculate P&L.
        """
        position = self.db.get_open_position(product_id)
        
        if not position:
            return None
        
        # Calculate P&L
        entry_cost = position.amount_gbp + position.fee
        exit_fee = exit_amount_gbp * 0.006  # 0.6% fee
        exit_revenue = exit_amount_gbp - exit_fee
        
        profit_loss = exit_revenue - entry_cost
        
        # Update database
        self.db.close_position(product_id, exit_price, profit_loss)
        
        return {
            'entry_price': position.price,
            'exit_price': exit_price,
            'profit_loss': profit_loss,
            'profit_loss_pct': (profit_loss / entry_cost) * 100
        }