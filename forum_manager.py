#!/usr/bin/env python3
"""
Philosopher Dinner Forum Manager
Enhanced multi-forum philosophy platform with AI thinkers

Main entry point for the forum management system.
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from philosopher_dinner.cli.forum_cli import ForumManagerCLI
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def main():
    """Main entry point for the Forum Manager"""
    
    print("🏛️ Philosopher Dinner - Forum Manager")
    print("=" * 50)
    
    try:
        # Initialize and start the CLI
        cli = ForumManagerCLI()
        cli.start()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye from the philosophical forums!")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()