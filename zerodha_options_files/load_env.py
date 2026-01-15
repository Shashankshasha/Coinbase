"""
Load environment variables from .env file
Add this import at the top of any script that needs credentials
"""

import os
from pathlib import Path

def load_env():
    """Load .env file from project root"""
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print("WARNING: .env file not found!")
        print("Create one with:")
        print("  KITE_API_KEY=your_key")
        print("  KITE_API_SECRET=your_secret")
        print("  ANTHROPIC_API_KEY=your_claude_key")
        return False

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

    print("Environment variables loaded from .env")
    return True

# Auto-load when imported
load_env()
