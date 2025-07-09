#!/usr/bin/env python3
"""
Main entry point for the Philosopher Dinner application.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    try:
        from philosopher_dinner.cli.interface import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install langgraph langchain rich")
        return 1
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())