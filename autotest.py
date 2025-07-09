#!/usr/bin/env python3
"""
Automated testing orchestrator for Philosopher Dinner.
Provides multiple automation options for catching regressions.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from github_issue_manager import GitHubIssueManager

def run_command(cmd, description, cwd=None):
    """Run a command and handle output"""
    print(f"\n🔧 {description}")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def setup_pre_commit_hook():
    """Set up pre-commit hook for automatic testing"""
    print("🪝 Setting up pre-commit hook...")
    
    hook_path = Path(".git/hooks/pre-commit")
    
    if hook_path.exists():
        print("✅ Pre-commit hook already exists")
        return True
    
    hook_content = '''#!/bin/bash
# Pre-commit hook to run tests before committing

echo "🧪 Running pre-commit tests..."
echo "================================="

# Change to project directory
cd "$(git rev-parse --show-toplevel)"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the simple test suite
cd tests
python3 test_runner_simple.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed! Proceeding with commit."
    exit 0
else
    echo ""
    echo "❌ Tests failed! Commit aborted."
    echo "Fix the failing tests before committing."
    exit 1
fi'''
    
    try:
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        print("✅ Pre-commit hook installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install pre-commit hook: {e}")
        return False

def run_simple_tests():
    """Run the simple test suite"""
    return run_command(
        f"{sys.executable} test_runner_simple.py",
        "Running simple test suite",
        cwd="tests"
    )

def run_comprehensive_tests():
    """Run the comprehensive test suite"""
    return run_command(
        f"{sys.executable} run_all_tests.py",
        "Running comprehensive test suite",
        cwd="tests"
    )

def run_specific_test(test_name):
    """Run a specific test file"""
    return run_command(
        f"{sys.executable} {test_name}",
        f"Running {test_name}",
        cwd="tests"
    )

def start_file_watcher():
    """Start the file watcher for development"""
    print("🔍 Starting development file watcher...")
    print("This will watch for changes and automatically run tests.")
    print("Press Ctrl+C to stop.")
    
    try:
        subprocess.run([sys.executable, "watch_tests.py"])
    except KeyboardInterrupt:
        print("\n👋 File watcher stopped.")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Automated testing for Philosopher Dinner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autotest.py --quick              # Run quick tests
  python autotest.py --full               # Run all tests
  python autotest.py --watch              # Start file watcher
  python autotest.py --setup              # Set up pre-commit hook
  python autotest.py --test cli           # Run specific test
  python autotest.py --pre-commit         # Run pre-commit tests
        """
    )
    
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Run quick test suite"
    )
    
    parser.add_argument(
        "--full", 
        action="store_true",
        help="Run comprehensive test suite"
    )
    
    parser.add_argument(
        "--watch", 
        action="store_true",
        help="Start file watcher for development"
    )
    
    parser.add_argument(
        "--setup", 
        action="store_true",
        help="Set up pre-commit hook"
    )
    
    parser.add_argument(
        "--test", 
        type=str,
        help="Run specific test (e.g., 'cli', 'langgraph', 'agent')"
    )
    
    parser.add_argument(
        "--pre-commit", 
        action="store_true",
        help="Run pre-commit test sequence"
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🧪 PHILOSOPHER DINNER - AUTOMATED TESTING")
    print("=" * 50)
    
    success = True
    
    if args.setup:
        success = setup_pre_commit_hook() and success
    
    if args.quick or args.pre_commit:
        success = run_simple_tests() and success
    
    if args.full:
        success = run_comprehensive_tests() and success
    
    if args.test:
        test_files = {
            "cli": "test_cli_interactions.py",
            "langgraph": "test_langgraph_flows.py", 
            "agent": "test_agent_behavior.py"
        }
        
        test_file = test_files.get(args.test, f"test_{args.test}.py")
        success = run_specific_test(test_file) and success
    
    if args.watch:
        start_file_watcher()
    
    # Summary
    if not args.watch:
        print("\n" + "=" * 50)
        if success:
            print("🎉 All operations completed successfully!")
        else:
            print("❌ Some operations failed. Check output above.")
        print("=" * 50)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()