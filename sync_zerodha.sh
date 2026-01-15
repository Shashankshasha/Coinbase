#!/bin/bash
# Auto-sync ZerodhaOptionsBot files
# Run this once on your Mac: bash sync_zerodha.sh

set -e

COINBASE_DIR="$HOME/ai/Coinbase"
ZERODHA_DIR="$HOME/ZerodhaOptionsBot"
BRANCH="claude/options-trading-bot-wUa0n"

echo "🔄 Syncing ZerodhaOptionsBot files..."

# Step 1: Pull latest from Coinbase
echo "📥 Pulling from Coinbase..."
cd "$COINBASE_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Step 2: Copy files to ZerodhaOptionsBot
echo "📋 Copying files..."
cp zerodha_options_files/config.py "$ZERODHA_DIR/"
cp zerodha_options_files/auto_pilot.py "$ZERODHA_DIR/"
cp zerodha_options_files/config_20k.py "$ZERODHA_DIR/"
cp zerodha_options_files/daily_analysis.py "$ZERODHA_DIR/"

# Step 3: Commit and push ZerodhaOptionsBot
echo "📤 Pushing to ZerodhaOptionsBot..."
cd "$ZERODHA_DIR"
git add .
git commit -m "Add auto-pilot + optimize for ₹20K capital with 1:2 risk/reward

- config.py: Updated with 1:2 risk/reward ratio (₹500 risk, ₹1000 target)
- auto_pilot.py: Full automation - picks best index + direction
- config_20k.py: Reference config for ₹20K capital
- daily_analysis.py: Morning CALL/PUT recommendation script
- Trailing stop: 1% below peak
- Auto-compounding enabled"

git push origin main

echo ""
echo "✅ Done! ZerodhaOptionsBot is now updated."
echo ""
echo "Files synced:"
echo "  - config.py (optimized settings)"
echo "  - auto_pilot.py (full automation)"
echo "  - config_20k.py (reference config)"
echo "  - daily_analysis.py (morning analysis)"
