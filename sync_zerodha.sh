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
cp zerodha_options_files/load_env.py "$ZERODHA_DIR/"
cp zerodha_options_files/.env.example "$ZERODHA_DIR/"

# Add .env to gitignore if not already there
if ! grep -q "^\.env$" "$ZERODHA_DIR/.gitignore" 2>/dev/null; then
    echo ".env" >> "$ZERODHA_DIR/.gitignore"
fi

# Step 3: Commit and push ZerodhaOptionsBot
echo "📤 Pushing to ZerodhaOptionsBot..."
cd "$ZERODHA_DIR"
git add .
git commit -m "Update bot with secure credentials and env loader

- config.py: Uses env vars for API credentials (secure)
- load_env.py: Auto-loads .env file
- .env.example: Template for credentials
- .gitignore: Excludes .env from commits
- auto_pilot.py: Full automation script
- daily_analysis.py: Morning CALL/PUT analysis"

git push origin main

echo ""
echo "✅ Done! ZerodhaOptionsBot is now updated."
echo ""
echo "Files synced:"
echo "  - config.py (optimized settings)"
echo "  - auto_pilot.py (full automation)"
echo "  - config_20k.py (reference config)"
echo "  - daily_analysis.py (morning analysis)"
echo "  - load_env.py (credentials loader)"
echo "  - .env.example (template)"
echo ""
echo "⚠️  Create .env file with your credentials:"
echo "  cd ~/ZerodhaOptionsBot"
echo "  cp .env.example .env"
echo "  # Edit .env with your actual keys"
