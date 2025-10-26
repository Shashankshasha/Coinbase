from apscheduler.schedulers.blocking import BlockingScheduler
from agent import TradingAgent

def run_trading_cycle():
    """Run one trading analysis cycle."""
    agent = TradingAgent()
    
    query = """Analyze ETH/GBP market. If confidence >75%, execute a £50 trade. 
    Otherwise explain why you're waiting."""
    
    response = agent.run(query)
    print(response)
    agent.reset()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_trading_cycle, 'interval', minutes=15)
    
    print("🤖 Trading bot running every 15 minutes...")
    print("Press Ctrl+C to stop")
    
    scheduler.start()