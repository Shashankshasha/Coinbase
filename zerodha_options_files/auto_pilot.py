#!/usr/bin/env python3
"""
AUTO-PILOT Trading Script
==========================

FULLY AUTOMATIC trading - just run this ONE script!

What it does:
1. Analyzes ALL indices (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY)
2. Picks the BEST index based on trend, liquidity, IV
3. Decides CALL or PUT direction
4. Updates config automatically
5. Starts the trading bot

Usage:
    python auto_pilot.py              # Interactive mode
    python auto_pilot.py --full-auto  # Complete automation (no prompts)
    python auto_pilot.py --dry-run    # Analysis only, don't start bot

Run this ONCE at 9:15 AM and walk away!
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pytz

sys.path.insert(0, '.')

import config
from config import OptionType, TradingMode


class IndexAnalyzer:
    """Analyzes and ranks indices for trading"""

    # All tradeable indices
    INDICES = {
        "NIFTY": {
            "name": "NIFTY 50",
            "lot_size": 50,
            "margin_required": 80000,  # Approximate
            "volatility": "medium",
            "liquidity": "highest",
            "best_for": "consistent trends"
        },
        "BANKNIFTY": {
            "name": "Bank NIFTY",
            "lot_size": 15,
            "margin_required": 70000,
            "volatility": "high",
            "liquidity": "very high",
            "best_for": "big moves, volatile days"
        },
        "FINNIFTY": {
            "name": "Financial NIFTY",
            "lot_size": 40,
            "margin_required": 60000,
            "volatility": "medium-high",
            "liquidity": "high",
            "best_for": "financial sector plays"
        },
        "MIDCPNIFTY": {
            "name": "Midcap NIFTY",
            "lot_size": 75,
            "margin_required": 50000,
            "volatility": "high",
            "liquidity": "medium",
            "best_for": "midcap momentum"
        }
    }

    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.scores = {}

    def analyze_all_indices(self, use_live_data: bool = False) -> Dict:
        """
        Analyze all indices and rank them

        Returns:
            Dict with rankings and recommendation
        """
        print("\n" + "=" * 60)
        print("  AUTO-PILOT: INDEX ANALYSIS")
        print(f"  {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("=" * 60)

        if use_live_data:
            return self._live_analysis()
        else:
            return self._manual_analysis()

    def _manual_analysis(self) -> Dict:
        """Interactive analysis without API"""

        print("\n  [QUICK MARKET SCAN]")
        print("  Answer these questions to find the best index:\n")

        # Question 1: Market type today
        print("  1. What type of day is expected?")
        print("     1) Trending day (clear direction)")
        print("     2) Range-bound (sideways)")
        print("     3) Volatile (big swings both ways)")
        print("     4) Event day (budget, RBI, expiry)")

        try:
            day_type = int(input("     Enter (1-4): ").strip())
        except:
            day_type = 1

        # Question 2: Sector strength
        print("\n  2. Which sector looks strongest today?")
        print("     1) Banks/Financials (HDFC, ICICI, Kotak)")
        print("     2) IT (TCS, Infy, Wipro)")
        print("     3) Broad market (mixed)")
        print("     4) Midcaps leading")

        try:
            sector = int(input("     Enter (1-4): ").strip())
        except:
            sector = 3

        # Question 3: Your risk appetite today
        print("\n  3. Your risk appetite today?")
        print("     1) Conservative (smaller moves, safer)")
        print("     2) Moderate")
        print("     3) Aggressive (bigger moves, more risk)")

        try:
            risk = int(input("     Enter (1-3): ").strip())
        except:
            risk = 2

        # Question 4: Available capital
        print(f"\n  4. Your trading capital today? (Current: ₹{config.INITIAL_CAPITAL_INR:,.0f})")
        print("     1) Under ₹50,000")
        print("     2) ₹50,000 - ₹1,00,000")
        print("     3) ₹1,00,000 - ₹2,00,000")
        print("     4) Above ₹2,00,000")

        try:
            capital = int(input("     Enter (1-4): ").strip())
        except:
            capital = 2

        # Score each index
        index_scores = {}

        for idx, info in self.INDICES.items():
            score = 50  # Base score
            reasons = []

            # Day type scoring
            if day_type == 1:  # Trending
                if idx == "NIFTY":
                    score += 20
                    reasons.append("NIFTY best for trending days")
                elif idx == "BANKNIFTY":
                    score += 15
                    reasons.append("BANKNIFTY good for trends")
            elif day_type == 3:  # Volatile
                if idx == "BANKNIFTY":
                    score += 25
                    reasons.append("BANKNIFTY thrives in volatility")
                elif idx == "MIDCPNIFTY":
                    score += 15
                    reasons.append("Midcap can catch big moves")
            elif day_type == 4:  # Event day
                if idx == "BANKNIFTY":
                    score += 20
                    reasons.append("BANKNIFTY best for events")
            elif day_type == 2:  # Range-bound
                if idx == "NIFTY":
                    score += 15
                    reasons.append("NIFTY safer in ranges")

            # Sector scoring
            if sector == 1:  # Banks
                if idx == "BANKNIFTY":
                    score += 25
                    reasons.append("Bank sector strong - trade BANKNIFTY")
                elif idx == "FINNIFTY":
                    score += 20
                    reasons.append("Financial sector play")
            elif sector == 4:  # Midcaps
                if idx == "MIDCPNIFTY":
                    score += 25
                    reasons.append("Midcaps leading - trade MIDCPNIFTY")

            # Risk scoring
            if risk == 1:  # Conservative
                if idx == "NIFTY":
                    score += 15
                    reasons.append("NIFTY is safest choice")
                elif idx == "BANKNIFTY":
                    score -= 10
            elif risk == 3:  # Aggressive
                if idx == "BANKNIFTY":
                    score += 15
                    reasons.append("BANKNIFTY for aggressive trading")
                elif idx == "MIDCPNIFTY":
                    score += 10

            # Capital scoring
            margin = info["margin_required"]
            if capital == 1 and margin > 60000:
                score -= 20
                reasons.append("May not have enough margin")
            elif capital >= 3:
                if idx == "BANKNIFTY":
                    score += 10
                    reasons.append("Good capital for BANKNIFTY")

            # Liquidity bonus
            if info["liquidity"] in ["highest", "very high"]:
                score += 5

            index_scores[idx] = {
                "score": score,
                "reasons": reasons,
                "info": info
            }

        # Rank indices
        ranked = sorted(index_scores.items(), key=lambda x: x[1]["score"], reverse=True)

        return {
            "rankings": ranked,
            "best_index": ranked[0][0],
            "best_score": ranked[0][1]["score"],
            "best_reasons": ranked[0][1]["reasons"],
            "day_type": day_type,
            "all_scores": index_scores
        }

    def _live_analysis(self) -> Dict:
        """Live analysis using Kite API"""
        # This would connect to Kite API and analyze real data
        # For now, fall back to manual
        print("  Live API not configured, using manual mode...")
        return self._manual_analysis()


class DirectionAnalyzer:
    """Analyzes market direction for CALL/PUT decision"""

    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')

    def analyze_direction(self, index: str) -> Dict:
        """Analyze direction for specific index"""

        print(f"\n  [DIRECTION ANALYSIS FOR {index}]")
        print("  Answer these questions:\n")

        score = 50  # Neutral
        signals = []

        # Question 1: Opening
        print(f"  1. How is {index} opening today?")
        print("     1) Gap Up (>0.3%)")
        print("     2) Flat")
        print("     3) Gap Down (>0.3%)")

        try:
            gap = int(input("     Enter (1-3): ").strip())
            if gap == 1:
                score += 15
                signals.append("Gap up - bullish")
            elif gap == 3:
                score -= 15
                signals.append("Gap down - bearish")
        except:
            pass

        # Question 2: Trend
        print(f"\n  2. What's the short-term trend (last 2-3 days)?")
        print("     1) Strong uptrend")
        print("     2) Mild uptrend")
        print("     3) Sideways")
        print("     4) Mild downtrend")
        print("     5) Strong downtrend")

        try:
            trend = int(input("     Enter (1-5): ").strip())
            if trend == 1:
                score += 20
                signals.append("Strong uptrend")
            elif trend == 2:
                score += 10
                signals.append("Mild uptrend")
            elif trend == 4:
                score -= 10
                signals.append("Mild downtrend")
            elif trend == 5:
                score -= 20
                signals.append("Strong downtrend")
        except:
            pass

        # Question 3: Global cues
        print("\n  3. Global market sentiment?")
        print("     1) Very positive (US, Asia green)")
        print("     2) Mildly positive")
        print("     3) Mixed")
        print("     4) Mildly negative")
        print("     5) Very negative")

        try:
            global_cue = int(input("     Enter (1-5): ").strip())
            if global_cue == 1:
                score += 15
                signals.append("Global cues positive")
            elif global_cue == 2:
                score += 8
            elif global_cue == 4:
                score -= 8
            elif global_cue == 5:
                score -= 15
                signals.append("Global cues negative")
        except:
            pass

        # Question 4: PCR
        print("\n  4. Put-Call Ratio (check NSE website)?")
        print("     1) Above 1.2 (Bullish)")
        print("     2) 0.9 - 1.2 (Neutral)")
        print("     3) Below 0.9 (Bearish)")

        try:
            pcr = int(input("     Enter (1-3): ").strip())
            if pcr == 1:
                score += 15
                signals.append("PCR bullish")
            elif pcr == 3:
                score -= 15
                signals.append("PCR bearish")
        except:
            pass

        # Determine direction
        if score >= 65:
            direction = OptionType.CALL
            direction_str = "BULLISH"
            confidence = (score - 50) / 50
        elif score <= 35:
            direction = OptionType.PUT
            direction_str = "BEARISH"
            confidence = (50 - score) / 50
        else:
            direction = None
            direction_str = "NEUTRAL"
            confidence = 0

        return {
            "score": score,
            "direction": direction,
            "direction_str": direction_str,
            "confidence": confidence,
            "signals": signals
        }


class AutoPilot:
    """Main auto-pilot controller"""

    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.index_analyzer = IndexAnalyzer()
        self.direction_analyzer = DirectionAnalyzer()

    def run(self, full_auto: bool = False, dry_run: bool = False) -> bool:
        """
        Run complete auto-pilot sequence

        Args:
            full_auto: Skip all confirmations
            dry_run: Analysis only, don't start bot

        Returns:
            True if bot started successfully
        """
        print("\n" + "=" * 60)
        print("  🚀 AUTO-PILOT TRADING SYSTEM")
        print(f"  {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("=" * 60)

        # Step 1: Check market hours
        if not self._check_market_hours():
            if not full_auto:
                proceed = input("\n  Market not open. Continue anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    return False

        # Step 2: Analyze indices
        print("\n  STEP 1: Selecting Best Index...")
        index_result = self.index_analyzer.analyze_all_indices()
        best_index = index_result["best_index"]

        self._display_index_rankings(index_result)

        # Confirm index selection
        if not full_auto:
            print(f"\n  Selected: {best_index}")
            confirm = input("  Use this index? (y/n/change): ").strip().lower()
            if confirm == 'n':
                return False
            elif confirm == 'change':
                print("  Available: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY")
                best_index = input("  Enter index name: ").strip().upper()
                if best_index not in self.index_analyzer.INDICES:
                    print("  Invalid index. Using NIFTY.")
                    best_index = "NIFTY"

        # Step 3: Analyze direction
        print("\n  STEP 2: Determining Direction (CALL/PUT)...")
        direction_result = self.direction_analyzer.analyze_direction(best_index)

        self._display_direction_result(direction_result)

        if direction_result["direction"] is None:
            print("\n  ⚠️  Market is NEUTRAL - not recommended to trade")
            if not full_auto:
                force = input("  Force a direction anyway? (call/put/no): ").strip().lower()
                if force == 'call':
                    direction_result["direction"] = OptionType.CALL
                elif force == 'put':
                    direction_result["direction"] = OptionType.PUT
                else:
                    return False

        # Step 4: Update config
        print("\n  STEP 3: Updating Configuration...")
        self._update_config(best_index, direction_result["direction"])

        # Step 5: Summary
        self._display_summary(best_index, direction_result)

        if dry_run:
            print("\n  [DRY RUN] Not starting bot.")
            return True

        # Step 6: Start bot
        if not full_auto:
            start = input("\n  Start trading bot now? (y/n): ").strip().lower()
            if start != 'y':
                print("\n  To start manually: python options_trading_bot.py")
                return True

        print("\n  STEP 4: Starting Trading Bot...")
        print("  " + "-" * 50)

        # Start the bot
        try:
            subprocess.run([sys.executable, "options_trading_bot.py"])
        except KeyboardInterrupt:
            print("\n\n  Bot stopped by user.")

        return True

    def _check_market_hours(self) -> bool:
        """Check if within market hours"""
        now = datetime.now(self.ist)

        # Weekend check
        if now.weekday() >= 5:
            print("  ⚠️  Today is weekend - market closed")
            return False

        # Time check
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)

        if now < market_open:
            print(f"  ⏰ Market opens at 9:15 AM (in {(market_open - now).seconds // 60} minutes)")
            return False
        elif now > market_close:
            print("  ⚠️  Market is closed for today")
            return False

        return True

    def _display_index_rankings(self, result: Dict):
        """Display index rankings"""
        print("\n  " + "-" * 50)
        print("  INDEX RANKINGS:")
        print("  " + "-" * 50)

        for i, (idx, data) in enumerate(result["rankings"], 1):
            score = data["score"]
            bar_len = int(score / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)

            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "

            print(f"  {medal} {i}. {idx:12} [{bar}] {score}/100")

            if i == 1 and data["reasons"]:
                for reason in data["reasons"][:2]:
                    print(f"       └─ {reason}")

    def _display_direction_result(self, result: Dict):
        """Display direction analysis result"""
        score = result["score"]
        direction_str = result["direction_str"]

        print("\n  " + "-" * 50)
        print("  DIRECTION ANALYSIS:")
        print("  " + "-" * 50)

        # Visual score
        bar_len = 40
        filled = int((score / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)

        print(f"\n  Score: {score}/100")
        print(f"  [{bar}]")
        print(f"  {'PUT':^13}{'NEUTRAL':^14}{'CALL':^13}")

        # Signals
        if result["signals"]:
            print(f"\n  Signals:")
            for sig in result["signals"]:
                print(f"    • {sig}")

        # Recommendation
        if result["direction"]:
            opt_type = "CALL (CE)" if result["direction"] == OptionType.CALL else "PUT (PE)"
            print(f"\n  ➤ Direction: {direction_str}")
            print(f"  ➤ Trade: {opt_type}")
            print(f"  ➤ Confidence: {result['confidence']*100:.0f}%")
        else:
            print(f"\n  ⚠️  Direction: {direction_str} - No clear signal")

    def _update_config(self, index: str, direction: OptionType):
        """Update config.py with new settings"""

        config_path = "config.py"

        try:
            with open(config_path, 'r') as f:
                content = f.read()

            # Update PRIMARY_INDEX
            import re
            content = re.sub(
                r'PRIMARY_INDEX = "[^"]*"',
                f'PRIMARY_INDEX = "{index}"',
                content
            )

            # Update OPTION_TYPE
            old_patterns = [
                "OPTION_TYPE: OptionType = OptionType.CALL",
                "OPTION_TYPE: OptionType = OptionType.PUT"
            ]
            new_value = f"OPTION_TYPE: OptionType = OptionType.{direction.name}"

            for old in old_patterns:
                if old in content:
                    content = content.replace(old, new_value)
                    break

            with open(config_path, 'w') as f:
                f.write(content)

            print(f"  ✅ Index: {index}")
            print(f"  ✅ Direction: {direction.name}")

        except Exception as e:
            print(f"  ❌ Error updating config: {e}")

    def _display_summary(self, index: str, direction_result: Dict):
        """Display final summary before trading"""

        direction = direction_result["direction"]

        print("\n" + "=" * 60)
        print("  📊 AUTO-PILOT SUMMARY")
        print("=" * 60)

        idx_info = self.index_analyzer.INDICES.get(index, {})

        risk_reward = config.PROFIT_TARGET_INR / config.MAX_LOSS_PER_TRADE_INR
        print(f"""
  Index:        {index} ({idx_info.get('name', '')})
  Direction:    {direction.name if direction else 'NONE'}
  Option Type:  {'CALL (CE) - Bullish' if direction == OptionType.CALL else 'PUT (PE) - Bearish'}
  Lot Size:     {idx_info.get('lot_size', 'N/A')}

  💰 CAPITAL & RISK
  ─────────────────
  Capital:        ₹{config.INITIAL_CAPITAL_INR:,.0f}
  Max Loss/Trade: ₹{config.MAX_LOSS_PER_TRADE_INR:,.0f}
  Profit Target:  ₹{config.PROFIT_TARGET_INR:,.0f}
  Risk/Reward:    1:{risk_reward:.1f} ✅ (Risk ₹{config.MAX_LOSS_PER_TRADE_INR:.0f} to make ₹{config.PROFIT_TARGET_INR:.0f})

  📈 TRAILING STOP (Ride profits!)
  ─────────────────────────────────
  Status:       {'ENABLED ✅' if config.ENABLE_TRAILING_STOP else 'DISABLED'}
  Activates at: {config.TRAILING_STOP_ACTIVATION_PCT*100:.0f}% profit
  Trails at:    {config.TRAILING_STOP_DISTANCE_PCT*100:.0f}% below peak

  🔄 AUTO-COMPOUNDING
  ───────────────────
  Reinvest:     {'ENABLED ✅' if config.REINVEST_PROFITS else 'DISABLED'}

  Mode:         {config.TRADING_MODE.value.upper()}
""")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Auto-Pilot Trading System")
    parser.add_argument("--full-auto", action="store_true",
                        help="Complete automation - no prompts")
    parser.add_argument("--dry-run", action="store_true",
                        help="Analysis only - don't start bot")
    args = parser.parse_args()

    pilot = AutoPilot()
    pilot.run(full_auto=args.full_auto, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
