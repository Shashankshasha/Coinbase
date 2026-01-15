#!/usr/bin/env python3
"""
Daily Market Analysis Script
=============================

Run this ONCE at market open (9:15-9:30 AM) to:
1. Analyze overall market trend
2. Check options chain sentiment
3. Recommend CALL or PUT for the day
4. Auto-update config if desired

Usage:
    python daily_analysis.py
    python daily_analysis.py --auto-set  # Auto-update config
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, Tuple
import pytz

# Add parent directory for imports
sys.path.insert(0, '.')

import config
from config import OptionType, TradingMode


class DailyMarketAnalyzer:
    """
    Analyzes market conditions to recommend CALL or PUT for the day.

    Factors considered:
    1. Previous day trend
    2. Gap up/down at open
    3. Global market cues
    4. Options chain sentiment (PCR, Max Pain)
    5. IV levels
    6. Technical indicators on daily timeframe
    """

    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.analysis_results = {}

    def run_analysis(self, kite_client=None) -> Dict:
        """
        Run comprehensive daily analysis

        Returns:
            Analysis results with recommendation
        """
        print("\n" + "=" * 60)
        print("  DAILY MARKET ANALYSIS")
        print(f"  {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("=" * 60)

        results = {
            "timestamp": datetime.now(self.ist).isoformat(),
            "index": config.PRIMARY_INDEX,
            "scores": {},
            "signals": [],
            "recommendation": None,
            "confidence": 0.0
        }

        # If no live data, use manual input mode
        if kite_client is None:
            results = self._manual_analysis()
        else:
            results = self._live_analysis(kite_client)

        return results

    def _manual_analysis(self) -> Dict:
        """Interactive manual analysis when API not available"""

        print("\n  [MANUAL ANALYSIS MODE]")
        print("  Answer the following questions:\n")

        score = 50  # Start neutral
        signals = []

        # Question 1: Previous day close
        print("  1. How did NIFTY close yesterday?")
        print("     1) Strong Green (>0.5%)")
        print("     2) Mild Green (0-0.5%)")
        print("     3) Flat")
        print("     4) Mild Red (0-0.5%)")
        print("     5) Strong Red (>0.5%)")

        try:
            prev_close = int(input("     Enter (1-5): ").strip())
            if prev_close == 1:
                score += 15
                signals.append("Previous day: Strong bullish close")
            elif prev_close == 2:
                score += 8
                signals.append("Previous day: Mild bullish")
            elif prev_close == 4:
                score -= 8
                signals.append("Previous day: Mild bearish")
            elif prev_close == 5:
                score -= 15
                signals.append("Previous day: Strong bearish close")
        except:
            pass

        # Question 2: Gap opening
        print("\n  2. How is the market opening today?")
        print("     1) Gap Up (>0.3%)")
        print("     2) Flat Open")
        print("     3) Gap Down (>0.3%)")

        try:
            gap = int(input("     Enter (1-3): ").strip())
            if gap == 1:
                score += 10
                signals.append("Gap up opening - bullish sentiment")
            elif gap == 3:
                score -= 10
                signals.append("Gap down opening - bearish sentiment")
        except:
            pass

        # Question 3: Global cues
        print("\n  3. How are global markets (US futures, SGX Nifty)?")
        print("     1) Strongly Positive (>0.5%)")
        print("     2) Mildly Positive")
        print("     3) Flat/Mixed")
        print("     4) Mildly Negative")
        print("     5) Strongly Negative (>0.5%)")

        try:
            global_cue = int(input("     Enter (1-5): ").strip())
            if global_cue == 1:
                score += 12
                signals.append("Global cues: Strongly positive")
            elif global_cue == 2:
                score += 6
                signals.append("Global cues: Mildly positive")
            elif global_cue == 4:
                score -= 6
                signals.append("Global cues: Mildly negative")
            elif global_cue == 5:
                score -= 12
                signals.append("Global cues: Strongly negative")
        except:
            pass

        # Question 4: PCR (Put-Call Ratio)
        print("\n  4. What is the current PCR (Put-Call Ratio)?")
        print("     Check: https://www.nseindia.com/option-chain")
        print("     1) Above 1.3 (Bullish)")
        print("     2) Between 1.0-1.3 (Neutral-Bullish)")
        print("     3) Between 0.8-1.0 (Neutral)")
        print("     4) Between 0.5-0.8 (Bearish)")
        print("     5) Below 0.5 (Strongly Bearish)")

        try:
            pcr = int(input("     Enter (1-5): ").strip())
            if pcr == 1:
                score += 15
                signals.append("PCR > 1.3: Strong put writing, bullish")
            elif pcr == 2:
                score += 8
                signals.append("PCR 1.0-1.3: Moderate bullish")
            elif pcr == 4:
                score -= 8
                signals.append("PCR 0.5-0.8: Bearish sentiment")
            elif pcr == 5:
                score -= 15
                signals.append("PCR < 0.5: Strong call writing, bearish")
        except:
            pass

        # Question 5: Max Pain vs Spot
        print("\n  5. Where is NIFTY spot vs Max Pain?")
        print("     1) Spot well BELOW Max Pain (>100 pts)")
        print("     2) Spot slightly below Max Pain")
        print("     3) Spot near Max Pain")
        print("     4) Spot slightly above Max Pain")
        print("     5) Spot well ABOVE Max Pain (>100 pts)")

        try:
            max_pain = int(input("     Enter (1-5): ").strip())
            if max_pain == 1:
                score += 10
                signals.append("Spot below Max Pain - likely to rise")
            elif max_pain == 5:
                score -= 10
                signals.append("Spot above Max Pain - likely to fall")
        except:
            pass

        # Question 6: Trend on daily chart
        print("\n  6. What's the trend on NIFTY daily chart?")
        print("     1) Strong Uptrend (higher highs)")
        print("     2) Mild Uptrend")
        print("     3) Sideways/Range-bound")
        print("     4) Mild Downtrend")
        print("     5) Strong Downtrend (lower lows)")

        try:
            trend = int(input("     Enter (1-5): ").strip())
            if trend == 1:
                score += 15
                signals.append("Daily chart: Strong uptrend")
            elif trend == 2:
                score += 8
                signals.append("Daily chart: Mild uptrend")
            elif trend == 4:
                score -= 8
                signals.append("Daily chart: Mild downtrend")
            elif trend == 5:
                score -= 15
                signals.append("Daily chart: Strong downtrend")
        except:
            pass

        # Question 7: VIX level
        print("\n  7. What is India VIX level?")
        print("     1) Below 12 (Low fear, bullish)")
        print("     2) 12-15 (Normal)")
        print("     3) 15-20 (Elevated)")
        print("     4) Above 20 (High fear, volatile)")

        try:
            vix = int(input("     Enter (1-4): ").strip())
            if vix == 1:
                score += 5
                signals.append("VIX low - calm market, favor trend")
            elif vix == 4:
                score -= 5
                signals.append("VIX high - volatile, be cautious")
        except:
            pass

        # Calculate recommendation
        score = max(0, min(100, score))

        if score >= 65:
            recommendation = OptionType.CALL
            confidence = (score - 50) / 50
            direction = "BULLISH"
        elif score <= 35:
            recommendation = OptionType.PUT
            confidence = (50 - score) / 50
            direction = "BEARISH"
        else:
            recommendation = None
            confidence = 0
            direction = "NEUTRAL"

        return {
            "timestamp": datetime.now(self.ist).isoformat(),
            "index": config.PRIMARY_INDEX,
            "score": score,
            "signals": signals,
            "recommendation": recommendation,
            "direction": direction,
            "confidence": confidence
        }

    def _live_analysis(self, kite_client) -> Dict:
        """Live analysis using Kite API data"""

        from data_layer import OptionsDataManager

        options_data = OptionsDataManager(kite_client)

        # Get market snapshot
        snapshot = options_data.get_market_snapshot(config.PRIMARY_INDEX)

        score = 50
        signals = []

        if snapshot:
            chain = snapshot.get("chain_analysis", {})

            # PCR analysis
            pcr = chain.get("pcr_oi", 1.0)
            if pcr > 1.3:
                score += 15
                signals.append(f"PCR {pcr:.2f}: Bullish (put writing)")
            elif pcr < 0.7:
                score -= 15
                signals.append(f"PCR {pcr:.2f}: Bearish (call writing)")

            # IV analysis
            iv_analysis = chain.get("iv_analysis", {})
            iv_skew = iv_analysis.get("iv_skew", 0)
            if iv_skew > 0.03:
                score -= 10
                signals.append("IV Skew: Put demand (bearish hedge)")
            elif iv_skew < -0.03:
                score += 10
                signals.append("IV Skew: Call demand (bullish)")

            # OI bias
            oi_analysis = chain.get("oi_analysis", {})
            if oi_analysis.get("oi_bias") == "bullish":
                score += 10
                signals.append("OI Analysis: Bullish bias")
            elif oi_analysis.get("oi_bias") == "bearish":
                score -= 10
                signals.append("OI Analysis: Bearish bias")

        # Determine recommendation
        score = max(0, min(100, score))

        if score >= 60:
            recommendation = OptionType.CALL
            confidence = (score - 50) / 50
            direction = "BULLISH"
        elif score <= 40:
            recommendation = OptionType.PUT
            confidence = (50 - score) / 50
            direction = "BEARISH"
        else:
            recommendation = None
            confidence = 0
            direction = "NEUTRAL"

        return {
            "timestamp": datetime.now(self.ist).isoformat(),
            "index": config.PRIMARY_INDEX,
            "score": score,
            "signals": signals,
            "recommendation": recommendation,
            "direction": direction,
            "confidence": confidence,
            "snapshot": snapshot
        }

    def display_results(self, results: Dict):
        """Display analysis results"""

        print("\n" + "=" * 60)
        print("  ANALYSIS RESULTS")
        print("=" * 60)

        score = results.get("score", 50)
        direction = results.get("direction", "NEUTRAL")
        confidence = results.get("confidence", 0)
        signals = results.get("signals", [])
        recommendation = results.get("recommendation")

        # Score visualization
        print(f"\n  SCORE: {score}/100")
        bar_length = 40
        filled = int((score / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}]")
        print(f"  {'BEARISH':^13}{'NEUTRAL':^14}{'BULLISH':^13}")

        # Signals
        print(f"\n  SIGNALS:")
        for signal in signals:
            print(f"    • {signal}")

        # Recommendation
        print("\n" + "-" * 60)
        if recommendation:
            rec_str = "CALL (CE)" if recommendation == OptionType.CALL else "PUT (PE)"
            print(f"\n  📊 RECOMMENDATION: Trade {rec_str}")
            print(f"  📈 DIRECTION: {direction}")
            print(f"  💪 CONFIDENCE: {confidence*100:.0f}%")
        else:
            print(f"\n  ⚠️  RECOMMENDATION: NO TRADE TODAY")
            print(f"     Market is NEUTRAL - wait for clearer direction")

        print("\n" + "=" * 60)

        return recommendation

    def update_config(self, recommendation: OptionType):
        """Update config.py with new OPTION_TYPE"""

        if recommendation is None:
            print("\n  ⚠️  No recommendation to apply")
            return False

        config_path = "config.py"

        try:
            with open(config_path, 'r') as f:
                content = f.read()

            # Find and replace OPTION_TYPE line
            old_call = "OPTION_TYPE: OptionType = OptionType.CALL"
            old_put = "OPTION_TYPE: OptionType = OptionType.PUT"

            new_value = f"OPTION_TYPE: OptionType = OptionType.{recommendation.name}"

            if old_call in content:
                content = content.replace(old_call, new_value)
            elif old_put in content:
                content = content.replace(old_put, new_value)

            with open(config_path, 'w') as f:
                f.write(content)

            print(f"\n  ✅ Config updated: OPTION_TYPE = {recommendation.name}")
            return True

        except Exception as e:
            print(f"\n  ❌ Error updating config: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Daily Market Analysis")
    parser.add_argument("--auto-set", action="store_true",
                        help="Automatically update config with recommendation")
    parser.add_argument("--live", action="store_true",
                        help="Use live Kite API data (requires credentials)")
    args = parser.parse_args()

    analyzer = DailyMarketAnalyzer()

    # Run analysis
    kite_client = None
    if args.live:
        try:
            from data_layer import create_kite_client
            kite_client = create_kite_client(
                config.KITE_API_KEY,
                config.KITE_API_SECRET,
                config.KITE_ACCESS_TOKEN,
                paper_trading=True
            )
        except Exception as e:
            print(f"  Could not connect to Kite API: {e}")
            print("  Falling back to manual mode...")

    results = analyzer.run_analysis(kite_client)
    recommendation = analyzer.display_results(results)

    # Auto-update config if requested
    if args.auto_set and recommendation:
        confirm = input("\n  Apply this recommendation to config.py? (y/n): ").strip().lower()
        if confirm == 'y':
            analyzer.update_config(recommendation)
    elif recommendation:
        print(f"\n  To apply manually, set in config.py:")
        print(f"  OPTION_TYPE = OptionType.{recommendation.name}")

    print("\n  Next step: python options_trading_bot.py")
    print("")


if __name__ == "__main__":
    main()
