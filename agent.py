from llm_client import ClaudeClient
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
import json

class TradingAgent:
    def __init__(self):
        self.claude = ClaudeClient()
        self.system_prompt = """You are an expert trading analyst assistant. Your role is to:

1. Analyze market conditions when asked
2. Use available tools to gather data (prices, account info, etc.)
3. Provide clear, logical trading recommendations
4. Always explain your reasoning step-by-step
5. Consider risk management in every decision

You have access to tools to get market data and account information. Use them when needed.

When analyzing trades, consider:
- Current market price and trends
- Account balance and existing positions
- Risk management (never risk more than recommended limits)
- Entry and exit points

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
    
    def reset(self):
        """Clear conversation history."""
        self.claude.reset_conversation()