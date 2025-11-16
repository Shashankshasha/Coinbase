from llm_client import ClaudeClient
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
from entry_analyzer import EnhancedEntrySystem
from enhanced_entry_system import MLEnhancedEntrySystem
from config import TRADING_PAIR, MIN_CONFIDENCE
import json


class TradingAgent:
    """
    ML-Enhanced Trading Agent
    
    NEW FEATURES:
    - Integrates ML-enhanced entry system
    - Adaptive threshold learning
    - Anomaly detection for opportunities
    - Continuous learning from trade outcomes
    """
    
    def __init__(self):
        self.claude = ClaudeClient()
        
        # ML-Enhanced Entry System
        print("🧠 Initializing ML-Enhanced Entry System...")
        self.base_entry_system = EnhancedEntrySystem()
        self.ml_entry_system = MLEnhancedEntrySystem(self.base_entry_system)
        print("✅ ML System ready!")
        
        # Track current trade for learning
        self.current_trade = None
        
        self.system_prompt = """You are an expert trading analyst assistant with ML-enhanced decision support. Your role is to:

1. Analyze market conditions using both traditional indicators AND machine learning predictions
2. Use available tools to gather data (prices, account info, market analysis)
3. Provide clear, logical trading recommendations enhanced by ML insights
4. Always explain your reasoning step-by-step
5. Consider risk management in every decision
6. Leverage adaptive thresholds based on historical performance

You have access to:
- Market data tools (prices, indicators, technical analysis)
- ML-enhanced entry/exit system (learns from outcomes)
- Anomaly detection (catches unusual opportunities like flash crashes)
- Adaptive confidence thresholds (adjusts based on win rate)

When analyzing trades, consider:
- Current market price and trends
- Account balance and existing positions
- Risk management (never risk more than recommended limits)
- Entry and exit points
- ML confidence score (0-1) and reasoning
- Anomaly signals (recovery opportunities, volatility spikes)
- Adaptive threshold (may be lower than 70% if conditions warrant)

NEW: The ML system can detect unusual opportunities like:
- Crash recoveries (sharp drop followed by bounce)
- Volatility spikes (unusual market activity)
- Pattern recognition (similar to past winning trades)

When ML confidence is high AND anomaly detected, you may recommend entry even if traditional score is 60-69.

Always be honest about uncertainty and limitations of analysis."""

    def run(self, user_query: str) -> str:
        """
        Main agent loop - handles tool calling automatically.
        """
        print(f"\n🤖 Agent received: {user_query}\n")
        
        response = self.claude.chat(
            user_message=user_query,
            system_prompt=self.system_prompt,
            tools=TOOL_DEFINITIONS
        )
        
        # Handle tool calls in a loop until Claude is done
        while response.stop_reason == "tool_use":
            print("🔧 Claude wants to use tools...\n")
            
            # Execute all tool calls in this response
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_id = content_block.id
                    
                    print(f"   Calling: {tool_name}")
                    print(f"   Input: {tool_input}\n")
                    
                    # Execute the tool
                    tool_function = TOOL_FUNCTIONS[tool_name]
                    result = tool_function(**tool_input)
                    
                    print(f"   Result: {result}\n")
                    
                    # Format result for Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(result)
                    })
            
            # Send tool results back to Claude
            response = self.claude.chat(
                user_message=tool_results,
                tools=TOOL_DEFINITIONS
            )
        
        # Extract final text response
        final_response = ""
        for content_block in response.content:
            if hasattr(content_block, "text"):
                final_response += content_block.text
        
        return final_response
    
    def run_auto_buy_with_ml(self, snapshot: dict) -> dict:
        """
        Automatic buy decision with ML enhancement.

        This replaces the old run_auto_buy() method.

        Returns:
            dict with decision, confidence, reasoning, and execution details
        """
        print(f"\n🤖 ML-ENHANCED AUTO-BUY SCAN\n")

        # Get ML-enhanced analysis
        ml_result = self.ml_entry_system.analyze_entry_with_ml(snapshot, TRADING_PAIR)

        # Display ML analysis
        print(f"\n🧠 Running ML-Enhanced Analysis...")
        print(f"   🧠 ML Confidence: {ml_result['ml_confidence']:.2f}")
        print(f"   📊 Combined Score: {ml_result['score']}/100")
        print(f"   🎯 Adaptive Threshold: {ml_result['adaptive_threshold']:.0f}")

        # ================================================================
        # 💰 API COST OPTIMIZATION - Skip Claude call when clearly HOLD
        # ================================================================
        # Only call Claude API when there's a real decision to make:
        # - ML recommends entry (score >= threshold), OR
        # - Anomaly detected (potential opportunity), OR
        # - Score is close to threshold (within 5 points)
        # ================================================================

        should_call_claude = (
            ml_result['should_enter'] or  # ML says BUY
            ml_result['anomaly_type'] is not None or  # Anomaly detected
            (ml_result['score'] >= ml_result['adaptive_threshold'] - 5)  # Close to threshold
        )

        if not should_call_claude:
            # ML clearly says HOLD - skip expensive API call
            print(f"   ⏸️ ML RECOMMENDS WAIT (need {ml_result['adaptive_threshold'] - ml_result['score']:.0f} more points)")
            print(f"\n⏸️  ML recommends HOLD")
            print(f"   ML Score: {ml_result['score']}/100")
            print(f"   Confidence: {ml_result['confidence']*100:.1f}%")
            print(f"\n💰 API call skipped! Score {ml_result['score']} < threshold {ml_result['adaptive_threshold']:.0f}")

            return {
                'action': 'HOLD',
                'executed': False,
                'confidence': ml_result['confidence'],
                'ml_score': ml_result['score'],
                'reasoning': f"ML score ({ml_result['score']}/100) below threshold ({ml_result['adaptive_threshold']:.0f}). {ml_result['reason']}",
                'ml_reasoning': ml_result['reason'],
                'api_call_skipped': True
            }

        # ================================================================
        # ML score is high or anomaly detected - worth asking Claude
        # ================================================================
        if ml_result['should_enter']:
            print(f"   ✅ ML TRIGGERED BUY!")
        else:
            print(f"   ⚠️  ML MARGINAL (close to threshold or anomaly)")

        print(f"   ML Score: {ml_result['score']}/100")
        print(f"   Base Score: {ml_result['base_score']}/100")
        print(f"   Confidence: {ml_result['confidence']*100:.1f}%")
        print(f"\n🤖 Calling Claude API for final decision...")

        # Build prompt for Claude with ML insights
        ml_context = f"""
ML-Enhanced Market Analysis for {TRADING_PAIR}:

TRADITIONAL ANALYSIS:
- Base Score: {ml_result['base_score']}/100
- Breakdown: {json.dumps(ml_result.get('breakdown', {}), indent=2)}

ML ENHANCEMENTS:
- ML Confidence: {ml_result['ml_confidence']:.2f} ({ml_result['ml_confidence']*100:.0f}%)
- Combined Score: {ml_result['score']}/100
- Adaptive Threshold: {ml_result['adaptive_threshold']:.0f}
- Quality Rating: {ml_result['quality']}

ANOMALY DETECTION:
- Anomaly Type: {ml_result['anomaly_type'] or 'None detected'}
- Anomaly Score: {ml_result.get('anomaly_score', 0):.2f}

ML RECOMMENDATION:
- Should Enter: {ml_result['should_enter']}
- Overall Confidence: {ml_result['confidence']:.2f}
- Reasoning: {ml_result['reason']}

Current Market State:
- Price: £{snapshot['current_price']:.2f}
- RSI: {snapshot['indicators'].get('rsi', 'N/A')}
- Volume Ratio: {snapshot['indicators'].get('volume_ratio', 'N/A')}x

YOUR TASK:
Based on this ML-enhanced analysis, should we execute a BUY order?

Consider:
1. ML combined score ({ml_result['score']}/100) vs adaptive threshold ({ml_result['adaptive_threshold']:.0f})
2. Anomaly detection results
3. Traditional indicator breakdown
4. Risk management (only risk what we can afford to lose)

If ML recommends entry (score >= threshold) and confidence >= {MIN_CONFIDENCE}:
→ Respond: "EXECUTE BUY - [brief reasoning including ML insights]"

If not recommended:
→ Respond: "HOLD - [specific reasons why, referencing ML score and threshold]"

Be decisive. This is automated trading.
"""

        # Get Claude's decision with ML context
        claude_response = self.run(ml_context)

        print(f"\n🧠 ML Insights: {ml_result['reason']}")
        
        # Parse decision
        if "EXECUTE BUY" in claude_response.upper():
            # Prepare execution result
            result = {
                'action': 'BUY',
                'executed': True,
                'confidence': ml_result['confidence'],
                'ml_score': ml_result['score'],
                'base_score': ml_result['base_score'],
                'adaptive_threshold': ml_result['adaptive_threshold'],
                'anomaly_type': ml_result['anomaly_type'],
                'reasoning': claude_response,
                'ml_reasoning': ml_result['reason'],
                'entry_price': snapshot['current_price'],
                'entry_time': snapshot['timestamp']
            }
            
            # Store for learning
            self.current_trade = {
                'entry_score': ml_result['score'],
                'entry_price': snapshot['current_price'],
                'entry_time': snapshot['timestamp']
            }
            
            return result
        else:
            return {
                'action': 'HOLD',
                'executed': False,
                'confidence': ml_result['confidence'],
                'ml_score': ml_result['score'],
                'reasoning': claude_response,
                'ml_reasoning': ml_result['reason']
            }
    
    def run_auto_sell_with_ml(self, exit_conditions: dict) -> dict:
        """
        Automatic sell decision - no ML needed here (profit target driven).
        
        But we DO record the outcome for ML learning.
        """
        print(f"\n🤖 AUTO-SELL DECISION\n")
        
        # Build context
        sell_context = f"""
Position Exit Analysis:

Current State:
- Entry Price: £{exit_conditions['entry_price']:.2f}
- Current Price: £{exit_conditions['current_price']:.2f}
- Target Price: £{exit_conditions['target_price']:.2f}
- Stop Loss: £{exit_conditions['stop_loss_price']:.2f}
- Current P&L: £{exit_conditions['expected_profit']:+.2f}

Exit Conditions:
- Should Exit: {exit_conditions['should_exit']}
- Reason: {exit_conditions['reason']}

YOUR TASK:
Should we SELL now?

If exit conditions met (profit target OR stop loss):
→ Respond: "EXECUTE SELL - [reasoning]"

Otherwise:
→ Respond: "HOLD - [reasoning]"
"""
        
        # Get Claude's decision
        claude_response = self.run(sell_context)
        
        # Parse decision
        if "EXECUTE SELL" in claude_response.upper():
            result = {
                'action': 'SELL',
                'executed': True,
                'profit': exit_conditions['expected_profit'],
                'exit_price': exit_conditions['current_price'],
                'reasoning': claude_response
            }
            
            # Record outcome for ML learning
            if self.current_trade:
                self._record_trade_outcome(result)
            
            return result
        else:
            return {
                'action': 'HOLD',
                'executed': False,
                'reasoning': claude_response
            }
    
    def _record_trade_outcome(self, sell_result: dict):
        """
        Record completed trade outcome to ML system for learning.
        """
        if not self.current_trade:
            return
        
        from datetime import datetime
        
        entry_score = self.current_trade.get('entry_score', 0)
        profit = sell_result.get('profit', 0)
        
        # Calculate duration
        entry_time = self.current_trade.get('entry_time')
        if entry_time:
            try:
                entry_dt = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
                exit_dt = datetime.now()
                duration_minutes = int((exit_dt - entry_dt).total_seconds() / 60)
            except:
                duration_minutes = 0
        else:
            duration_minutes = 0
        
        # Feed back to ML system
        print(f"\n📚 Recording trade outcome for ML learning...")
        self.ml_entry_system.record_trade_outcome(
            entry_score=entry_score,
            profit=profit,
            duration_minutes=duration_minutes
        )
        
        # Clear current trade
        self.current_trade = None
        
        # Show ML performance stats
        self._show_ml_stats()
    
    def _show_ml_stats(self):
        """
        Display ML system performance statistics.
        """
        stats = self.ml_entry_system.get_performance_stats()
        
        print(f"\n📊 ML PERFORMANCE STATS:")
        print(f"   Total Trades: {stats['total_trades']}")
        
        if stats['total_trades'] > 0:
            print(f"   Wins: {stats['wins']} | Losses: {stats['losses']}")
            print(f"   Win Rate: {stats['win_rate']:.1%}")
            print(f"   Avg Profit: £{stats['avg_profit']:.2f}")
            print(f"   Total Profit: £{stats['total_profit']:.2f}")
            print(f"   Best Trade: £{stats['best_trade']:.2f}")
            print(f"   Worst Trade: £{stats['worst_trade']:.2f}")
        
        print(f"   Model Trained: {stats['model_trained']}")
        print(f"   Adaptive Threshold: {stats['adaptive_threshold']:.0f}")
        
        if stats['model_trained']:
            print(f"   🧠 ML model is ACTIVE and learning!")
        else:
            print(f"   ⏳ ML model training after 20 trades...")
    
    def get_ml_performance(self) -> dict:
        """
        Get detailed ML performance metrics.
        
        Returns:
            dict with performance statistics
        """
        return self.ml_entry_system.get_performance_stats()
    
    def reset(self):
        """Clear conversation history."""
        self.claude.reset_conversation()
    
    # =========================================================================
    # LEGACY METHODS (Keep for backward compatibility)
    # =========================================================================
    
    def run_auto_buy(self) -> dict:
        """
        Legacy method - redirects to ML-enhanced version.
        
        This maintains backward compatibility with existing code.
        """
        from data_layer.market_data import MarketData
        
        market = MarketData()
        snapshot = market.get_full_market_snapshot(TRADING_PAIR)
        
        return self.run_auto_buy_with_ml(snapshot)
    
    def run_auto_sell(self, exit_conditions: dict) -> dict:
        """
        Legacy method - redirects to ML-enhanced version.
        """
        return self.run_auto_sell_with_ml(exit_conditions)