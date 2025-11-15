from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from datetime import datetime
import os
import time

Base = declarative_base()

class Trade(Base):
    """
    Trade record in the database.
    """
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    # Trade details
    action = Column(String, nullable=False)  # BUY or SELL
    product_id = Column(String, nullable=False)
    mode = Column(String, nullable=False)  # PAPER or LIVE
    
    # Amounts
    amount_gbp = Column(Float, nullable=False)
    crypto_amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    
    # Decision info
    confidence = Column(Float, nullable=False)
    reasoning = Column(String)
    
    # Execution info
    executed = Column(Boolean, default=True)
    order_id = Column(String, nullable=True)
    
    # P&L (filled when position closed)
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    profit_loss_pct = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<Trade {self.trade_id}: {self.action} {self.crypto_amount:.6f} {self.product_id} @ £{self.price:.2f}>"


class TradingDatabase:
    """
    Manages the SQLite database for trade records.
    """
    
    def __init__(self, db_path: str = "trading_bot.db"):
        """
        Initialize database connection.

        THREAD-SAFE: Uses scoped_session for multi-threaded access

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create engine with thread-safe settings for SQLite
        # - check_same_thread=False: Allow access from multiple threads
        # - NullPool: Don't pool connections (each thread gets its own)
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False},
            poolclass=NullPool,
            echo=False
        )

        Base.metadata.create_all(self.engine)

        # Use scoped_session for thread-local sessions
        # Each thread will get its own session automatically
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        self.session = self.Session()
    
    def record_trade(
        self,
        product_id: str,
        action: str,
        price: float,
        crypto_amount: float,
        amount_gbp: float,
        fee: float,
        confidence: float = 0.0,
        reasoning: str = "",
        mode: str = "LIVE",
        order_id: str = None
    ) -> Trade:
        """
        Record a trade to the database.
        Simplified method for direct trade recording.
        
        Args:
            product_id: Trading pair (e.g., 'SOL-GBP')
            action: 'BUY' or 'SELL'
            price: Price per unit
            crypto_amount: Amount of cryptocurrency
            amount_gbp: Total GBP amount
            fee: Trading fee
            confidence: Confidence level (0-1)
            reasoning: Reason for trade
            mode: 'PAPER' or 'LIVE'
            order_id: Exchange order ID (optional)
            
        Returns:
            Trade object
        """
        # Generate unique trade ID
        trade_id = f"{action.lower()}_{product_id}_{int(time.time() * 1000)}"
        
        trade = Trade(
            trade_id=trade_id,
            timestamp=datetime.now(),
            action=action,
            product_id=product_id,
            mode=mode,
            amount_gbp=amount_gbp,
            crypto_amount=crypto_amount,
            price=price,
            fee=fee,
            confidence=confidence,
            reasoning=reasoning,
            executed=True,
            order_id=order_id
        )
        
        self.session.add(trade)
        self.session.commit()
        return trade
    
    def add_trade(self, trade_data: dict) -> Trade:
        """
        Add a new trade to the database.
        
        Args:
            trade_data: Dictionary with trade details
            
        Returns:
            Trade object
        """
        trade = Trade(
            trade_id=trade_data.get('trade_id'),
            timestamp=datetime.fromisoformat(trade_data.get('timestamp', datetime.now().isoformat())),
            action=trade_data.get('action'),
            product_id=trade_data.get('product_id'),
            mode=trade_data.get('mode', 'PAPER'),
            amount_gbp=trade_data.get('amount_gbp'),
            crypto_amount=trade_data.get('crypto_amount'),
            price=trade_data.get('price'),
            fee=trade_data.get('fee', 0),
            confidence=trade_data.get('confidence'),
            reasoning=trade_data.get('reasoning', ''),
            executed=trade_data.get('executed', True),
            order_id=trade_data.get('order_id')
        )
        
        self.session.add(trade)
        self.session.commit()
        return trade
    
    def get_all_trades(self) -> list:
        """
        Get all trades.
        """
        return self.session.query(Trade).order_by(Trade.timestamp.desc()).all()
    
    def get_trades_by_product(self, product_id: str) -> list:
        """
        Get trades for a specific product.
        """
        return self.session.query(Trade).filter_by(product_id=product_id).order_by(Trade.timestamp.desc()).all()
    
    def get_open_position(self, product_id: str) -> Trade:
        """
        Get the most recent BUY trade without a matching SELL (open position).
        """
        # Get all trades for this product
        trades = self.session.query(Trade).filter_by(
            product_id=product_id
        ).order_by(Trade.timestamp.desc()).all()
        
        # Simple logic: if last trade was BUY and profit_loss is None, it's open
        if trades and trades[0].action == 'BUY' and trades[0].profit_loss is None:
            return trades[0]
        return None
    
    def close_position(self, product_id: str, exit_price: float, profit_loss: float):
        """
        Mark an open position as closed with P&L.
        """
        position = self.get_open_position(product_id)
        if position:
            position.exit_price = exit_price
            position.profit_loss = profit_loss
            position.profit_loss_pct = (profit_loss / position.amount_gbp) * 100
            self.session.commit()
    
    def get_total_pnl(self) -> dict:
        """
        Calculate total profit/loss across all closed positions.
        """
        trades = self.session.query(Trade).filter(Trade.profit_loss.isnot(None)).all()
        
        total_pnl = sum(t.profit_loss for t in trades)
        winning_trades = [t for t in trades if t.profit_loss > 0]
        losing_trades = [t for t in trades if t.profit_loss < 0]
        
        return {
            'total_pnl': total_pnl,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) * 100 if trades else 0,
            'avg_profit': sum(t.profit_loss for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t.profit_loss for t in losing_trades) / len(losing_trades) if losing_trades else 0
        }
    
    def get_session(self):
        """
        Get or create a thread-local session.

        Returns:
            Session: Thread-local SQLAlchemy session
        """
        return self.Session()

    def close(self):
        """
        Close database connection and remove scoped session.
        """
        self.Session.remove()  # Remove thread-local session
        self.engine.dispose()  # Close all connections