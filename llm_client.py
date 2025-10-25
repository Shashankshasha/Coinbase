import anthropic
from config import ANTHROPIC_API_KEY, MODEL_NAME

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation_history = []
    
    def chat(self, user_message, system_prompt=None, tools=None):
        """
        Send a message to Claude and get a response.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare the API call
        kwargs = {
            "model": MODEL_NAME,
            "max_tokens": 4096,
            "messages": self.conversation_history
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        if tools:
            kwargs["tools"] = tools
        
        # Call Claude
        response = self.client.messages.create(**kwargs)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        return response
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []