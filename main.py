from agent import TradingAgent

def main():
    print("=" * 60)
    print("🚀 Trading Agent Started (Paper Trading Mode)")
    print("=" * 60)
    print("\nType 'quit' or 'exit' to stop\n")
    
    agent = TradingAgent()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Shutting down agent. Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Run the agent
            response = agent.run(user_input)
            
            print(f"\n🤖 Agent: {response}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue

if __name__ == "__main__":
    main()