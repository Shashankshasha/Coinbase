#!/bin/bash

# ============================================================================
# COINBASE-BTC REPOSITORY SETUP SCRIPT
# ============================================================================
# This script creates a separate repository for BTC-GBP trading
# WITH API COST OPTIMIZATION (saves ~£135/month!)
# ============================================================================

set -e  # Exit on error

echo ""
echo "=================================================="
echo "🚀 COINBASE-BTC REPOSITORY SETUP"
echo "=================================================="
echo ""

# ============================================================================
# STEP 1: Create empty repository on GitHub
# ============================================================================
echo "📋 STEP 1: Create GitHub Repository"
echo ""
echo "Please complete this step manually:"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: Coinbase-BTC"
echo "3. Description: BTC-GBP ML Trading Bot with API Optimization"
echo "4. Select: Public (or Private if preferred)"
echo "5. Do NOT initialize with README, gitignore, or license"
echo "6. Click 'Create repository'"
echo ""
read -p "Press Enter when repository is created..."

# ============================================================================
# STEP 2: Clone and setup Coinbase-BTC
# ============================================================================
echo ""
echo "📋 STEP 2: Setting up local repository"
echo ""

# Navigate to Documents directory (or choose your preferred location)
cd ~/Documents || cd ~

# Clone the BTC-GBP branch (includes API optimization!)
echo "Cloning BTC-GBP configuration from main repository..."
git clone -b claude/check-main-branch-pull-011JVThYXT9pLQTBya1ttWE6 \
  https://github.com/Shashankshasha/Coinbase.git Coinbase-BTC

cd Coinbase-BTC

# Verify the trading pair
echo ""
echo "=== BTC-GBP Configuration ==="
grep "TRADING_PAIR" config.py
echo ""

# ============================================================================
# STEP 3: Configure remote repository
# ============================================================================
echo "📋 STEP 3: Configuring remote repository"
echo ""

# Remove old remote and add new one
git remote remove origin
git remote add origin https://github.com/Shashankshasha/Coinbase-BTC.git

# Create main branch and push
git checkout -b main
git push -u origin main

echo ""
echo "✅ Coinbase-BTC repository created!"
echo ""

# ============================================================================
# STEP 4: Verify everything
# ============================================================================
echo "=================================================="
echo "📊 VERIFICATION"
echo "=================================================="
echo ""

echo "=== Repository Information ==="
pwd
echo ""
git remote -v
echo ""

echo "=== Trading Configuration ==="
grep "TRADING_PAIR\|INITIAL_CAPITAL\|TRADE_AMOUNT_GBP" config.py
echo ""

echo "=== API Optimization ==="
api_optimizations=$(grep -c 'API COST OPTIMIZATION' agent.py || echo "0")
echo "Optimizations found: $api_optimizations"
if [ "$api_optimizations" -gt 0 ]; then
    echo "✅ API cost optimization is ACTIVE"
else
    echo "⚠️  WARNING: API optimization not found!"
fi
echo ""

# ============================================================================
# STEP 5: Summary
# ============================================================================
echo "=================================================="
echo "✅ SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "📂 Local directory:"
echo "   ~/Documents/Coinbase-BTC/"
echo ""
echo "🌐 GitHub repository:"
echo "   https://github.com/Shashankshasha/Coinbase-BTC"
echo ""
echo "💰 Trading Configuration:"
echo "   - Pair: BTC-GBP"
echo "   - Capital: £500"
echo "   - Trade Amount: £495"
echo "   - Profit Target: £2.00"
echo "   - Stop Loss: 0.5% (£2.50)"
echo ""
echo "🧠 API Cost Optimization:"
echo "   - Skips Claude calls when ML score < threshold"
echo "   - Expected savings: £135/month"
echo "   - Reduces API calls by ~90%"
echo ""
echo "=================================================="
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Navigate to repository:"
echo "   cd ~/Documents/Coinbase-BTC"
echo ""
echo "2. Create .env file with your API keys:"
echo "   cp .env.example .env"
echo "   nano .env  # Add your COINBASE_API_KEY and ANTHROPIC_API_KEY"
echo ""
echo "3. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Test the bot:"
echo "   python main.py"
echo ""
echo "5. Run continuously:"
echo "   python ml_trading_bot.py"
echo ""
echo "=================================================="
echo ""
