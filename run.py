#!/usr/bin/env python3
"""
Simple script to run the Attendance Bot
"""

import os
import sys
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main function to run the bot"""
    try:
        # Import and run the bot
        from main import main as run_bot
        run_bot()
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 