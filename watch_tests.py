#!/usr/bin/env python3
"""
Development file watcher that automatically runs tests when code changes.
Provides immediate feedback during development.
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

def get_file_mtime(file_path):
    """Get file modification time"""
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0

def scan_directory(directory, extensions=None):
    """Scan directory for files with specific extensions"""
    if extensions is None:
        extensions = ['.py']
    
    files = {}
    for root, dirs, filenames in os.walk(directory):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, filename)
                files[file_path] = get_file_mtime(file_path)
    
    return files

def run_tests():
    """Run the test suite"""
    print(f"\n🧪 Running tests at {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Change to tests directory
    original_dir = os.getcwd()
    test_dir = os.path.join(original_dir, 'tests')
    
    if not os.path.exists(test_dir):
        print("❌ Tests directory not found!")
        return False
    
    os.chdir(test_dir)
    
    try:
        # Run simple test suite
        result = subprocess.run([
            sys.executable, 'test_runner_simple.py'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print("\n✅ Tests passed! Watching for changes...")
        else:
            print("\n❌ Tests failed! Fix issues and save to re-run...")
        
        return success
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main file watcher loop"""
    print("🔍 PHILOSOPHER DINNER - DEVELOPMENT TEST WATCHER")
    print("=" * 60)
    print("Watching for Python file changes...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Directories to watch
    watch_dirs = [
        'philosopher_dinner',
        'tests'
    ]
    
    # Get initial file states
    current_files = {}
    for directory in watch_dirs:
        if os.path.exists(directory):
            current_files.update(scan_directory(directory))
    
    print(f"📁 Watching {len(current_files)} Python files in {len(watch_dirs)} directories")
    
    # Run tests initially
    run_tests()
    
    try:
        while True:
            time.sleep(1)  # Check every second
            
            # Check for file changes
            new_files = {}
            for directory in watch_dirs:
                if os.path.exists(directory):
                    new_files.update(scan_directory(directory))
            
            # Find changed files
            changed_files = []
            
            # Check for modified files
            for file_path, mtime in new_files.items():
                if file_path in current_files:
                    if mtime > current_files[file_path]:
                        changed_files.append(file_path)
                else:
                    # New file
                    changed_files.append(file_path)
            
            # Check for deleted files
            for file_path in current_files:
                if file_path not in new_files:
                    changed_files.append(file_path)
            
            if changed_files:
                print(f"\n📝 File changes detected:")
                for file_path in changed_files:
                    relative_path = os.path.relpath(file_path)
                    print(f"  • {relative_path}")
                
                # Update file states
                current_files = new_files
                
                # Run tests
                run_tests()
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopping file watcher...")
        print("Happy coding! 🚀")

if __name__ == "__main__":
    main()