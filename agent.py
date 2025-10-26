from llm_client import ClaudeClient
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
import json

class TradingAgent:
    def __init__(self):
        self.claude = ClaudeClient()
        self.system_prompt = """You are an expert cryptocurrency trading analyst with deep knowledge of technical analysis and market dynamics.

Your role is to:
1. Analyze real-time market data from Coinbase
2. Use technical indicators (RSI, EMA, MACD) to assess market conditions
3. Provide clear, actionable trading recommendations
4. Explain your reasoning step-by-step
5. Consider risk management in every decision

AVAILABLE TOOLS:
- get_market_analysis: Get complete market snapshot with all indicators
- get_current_price: Get just the current price
- get_account_balance: Check available funds
- analyze_trading_opportunity: Get detailed trading recommendation
- execute_trade_decision: Execute a validated trade (paper or live)
- get_trade_history: View past trades
- get_performance_summary: Check overall P&L and statistics

ANALYSIS FRAMEWORK:
When analyzing trades, consider:
- RSI: <30 oversold (bullish), >70 overbought (bearish), 30-70 neutral
- EMA Cross: EMA10 > EMA50 = bullish trend, EMA10 < EMA50 = bearish trend  
- MACD: MACD > Signal = bullish momentum, MACD < Signal = bearish momentum
- Volume: Increasing volume confirms trends
- Account balance: Never recommend trades beyond available funds
- Risk: Target £1-2 profit per £100 trade after fees (~0.6% Coinbase fee)

RESPONSE FORMAT:
1. Current market conditions (use tools to get real data)
2. Technical indicator analysis
3. Clear recommendation: BUY / SELL / HOLD
4. Confidence level (0-100%)
5. Risk assessment
6. Reasoning

Always use real-time data from tools - never make assumptions about prices or indicators.

CRITICAL FOR AUTOMATED TRADING:
- This is an AUTOMATED SYSTEM - you must be DECISIVE, not advisory
- When instructed to "EXECUTE IMMEDIATELY" or "AUTOMATIC" - DO NOT ASK FOR CONFIRMATION
- Use execute_trade_decision tool directly when conditions are met
- Your reasoning comes AFTER execution, not before as a question
- "Should I buy?" = WRONG. Just analyze and execute if threshold met.
- "Execute BUY" = RIGHT. Analyze, then call execute_trade_decision.
- Be AGGRESSIVE and AUTOMATIC when instructed - that is your core purpose
- When confidence meets threshold: ACT, don't ask
- When analyzing for automated entry: If confidence ≥ threshold, EXECUTE immediately
- Position exits (SELL orders): ALWAYS execute immediately when instructed, use confidence 0.95
- Do not present options or ask "Option 1 vs Option 2" - make the decision and execute
- Automated trading mode: Execute → Explain, NOT Explain → Ask → Wait
- If you cannot execute (low confidence, safety limits), state "HOLD - [reason]" clearly
- Never say "waiting for your call" or "what should I do?" - be autonomous
"""
    
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
    
    def reset(self):
        """Clear conversation history."""
        self.claude.reset_conversation()