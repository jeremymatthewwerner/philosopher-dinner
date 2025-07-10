#!/usr/bin/env python3
"""
Main entry point for the Philosopher Dinner application.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point - now uses the enhanced Forum Manager"""
    print("🏛️ Starting Philosopher Dinner...")
    
    # Check if user wants the old single-forum interface
    if len(sys.argv) > 1 and sys.argv[1] == "--classic":
        print("Using classic single-forum interface...")
        try:
            from philosopher_dinner.cli.interface import main as cli_main
            cli_main()
        except ImportError as e:
            print(f"Import error: {e}")
            print("Make sure you have installed the required dependencies:")
            print("pip install langgraph langchain rich")
            return 1
    else:
        # Try the full forum system first, fall back to simplified
        print("Using enhanced multi-forum system...")
        try:
            from philosopher_dinner.cli.forum_cli import main as forum_cli_main
            forum_cli_main()
        except ImportError as e:
            print(f"LangGraph not available, using simplified forum manager...")
            print("Install LangGraph for full AI conversations: pip install langgraph")
            try:
                from philosopher_dinner.cli.simple_forum_cli import main as simple_cli_main
                simple_cli_main()
            except ImportError as e2:
                print(f"Import error: {e2}")
                print("Make sure you have installed: pip install rich")
                return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())