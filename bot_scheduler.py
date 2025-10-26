import subprocess
import datetime
import time
import psutil
import os

# ✅ Path to your bot file
BOT_PATH = "/Users/shashanksingh/ai/first_ai_agent/beast_mode_bot.py"

# ✅ Trading window
START_HOUR = 9      # 9 AM UK time
STOP_HOUR = 22      # 10 PM UK time
TRADING_DAYS = [1, 2, 3, 4]  # Tue–Fri (0=Mon, 6=Sun)

def is_bot_running():
    """Check if beast_mode_bot.py is already running."""
    for proc in psutil.process_iter(['cmdline']):
        if proc.info['cmdline'] and 'beast_mode_bot.py' in proc.info['cmdline']:
            return True
    return False

def start_bot():
    """Start the trading bot."""
    print(f"[{datetime.datetime.now()}] 🚀 Starting trading bot...")
    subprocess.Popen(["python3", BOT_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_bot():
    """Stop the trading bot."""
    print(f"[{datetime.datetime.now()}] 🛑 Stopping trading bot...")
    for proc in psutil.process_iter(['pid', 'cmdline']):
        if proc.info['cmdline'] and 'beast_mode_bot.py' in proc.info['cmdline']:
            proc.kill()

print("📅 Scheduler started — watching trading hours...")

while True:
    now = datetime.datetime.now()
    day = now.weekday()
    hour = now.hour

    if day in TRADING_DAYS and START_HOUR <= hour < STOP_HOUR:
        if not is_bot_running():
            start_bot()
    else:
        if is_bot_running():
            stop_bot()

    time.sleep(60)  # check every minute
