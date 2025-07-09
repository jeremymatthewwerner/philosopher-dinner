#!/usr/bin/env python3
"""
Demo script to show the automated bug tracking system in action.
Creates a test bug, files an issue, then fixes it to demonstrate the full cycle.
"""

import os
import sys
import time
from datetime import datetime
from github_issue_manager import GitHubIssueManager

def demonstrate_bug_tracking():
    """Demonstrate the complete bug tracking and resolution cycle"""
    
    print("🧪 AUTOMATED BUG TRACKING DEMONSTRATION")
    print("=" * 60)
    
    # Initialize the issue manager
    issue_manager = GitHubIssueManager()
    
    # Step 1: Simulate a bug discovery
    print("\n1️⃣ SIMULATING BUG DISCOVERY")
    print("-" * 40)
    
    test_name = "demo_test_failure"
    error_message = "AssertionError: Demo test intentionally failed"
    test_output = """
Traceback (most recent call last):
  File "demo_test.py", line 10, in test_demo
    assert False, "Demo test intentionally failed"
AssertionError: Demo test intentionally failed
"""
    
    context = {
        "test_type": "demo",
        "component": "demonstration",
        "severity": "low",
        "created_by": "demo_script"
    }
    
    # Create a bug issue
    print("📝 Filing GitHub issue for discovered bug...")
    issue_number = issue_manager.create_bug_issue(
        test_name=test_name,
        error_message=error_message,
        test_output=test_output,
        context=context
    )
    
    if issue_number:
        print(f"✅ Successfully filed issue #{issue_number}")
    else:
        print("❌ Failed to file issue (GitHub CLI may not be configured)")
        print("💡 To test with real GitHub integration:")
        print("   1. Install GitHub CLI: brew install gh")
        print("   2. Authenticate: gh auth login")
        print("   3. Run this demo again")
    
    # Step 2: Show bug statistics
    print("\n2️⃣ BUG TRACKING STATISTICS")
    print("-" * 40)
    
    stats = issue_manager.get_bug_statistics()
    print(f"🐛 Total bugs found: {stats['total_bugs_found']}")
    print(f"📋 Currently tracked: {stats['currently_tracked']}")  
    print(f"✅ Resolved bugs: {stats['resolved_bugs']}")
    print(f"📈 Resolution rate: {stats['resolution_rate']:.2%}")
    
    # Step 3: List tracked bugs
    print("\n3️⃣ TRACKED BUGS")
    print("-" * 40)
    
    bugs = issue_manager.list_tracked_bugs()
    if bugs:
        for bug in bugs:
            print(f"📋 Issue #{bug['issue_number']} - {bug['test_name']}")
            print(f"    Error: {bug['error_message'][:50]}...")
            print(f"    Created: {bug['created_at']}")
    else:
        print("📝 No bugs currently tracked")
    
    # Step 4: Simulate bug resolution
    print("\n4️⃣ SIMULATING BUG RESOLUTION")
    print("-" * 40)
    
    if issue_number:
        print("🔧 Simulating test fix...")
        time.sleep(2)  # Simulate fix time
        
        # Resolve the bug
        print("✅ Resolving GitHub issue...")
        resolved = issue_manager.resolve_bug_issue(test_name, issue_number)
        
        if resolved:
            print(f"✅ Successfully resolved issue #{issue_number}")
        else:
            print("❌ Failed to resolve issue (GitHub CLI may not be configured)")
    
    # Step 5: Show final statistics
    print("\n5️⃣ FINAL STATISTICS")
    print("-" * 40)
    
    final_stats = issue_manager.get_bug_statistics()
    print(f"🐛 Total bugs found: {final_stats['total_bugs_found']}")
    print(f"📋 Currently tracked: {final_stats['currently_tracked']}")
    print(f"✅ Resolved bugs: {final_stats['resolved_bugs']}")
    print(f"📈 Resolution rate: {final_stats['resolution_rate']:.2%}")
    
    # Step 6: Show resolved bugs
    print("\n6️⃣ RESOLVED BUGS")
    print("-" * 40)
    
    resolved_bugs = issue_manager.list_resolved_bugs()
    if resolved_bugs:
        for bug in resolved_bugs:
            print(f"✅ Issue #{bug['issue_number']} - {bug['test_name']}")
            print(f"    Error: {bug['error_message'][:50]}...")
            print(f"    Created: {bug['created_at']}")
            print(f"    Resolved: {bug['resolved_at']}")
    else:
        print("📝 No resolved bugs yet")
    
    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("The automated bug tracking system:")
    print("✅ Discovered a bug and filed a GitHub issue")
    print("✅ Tracked the bug in the local database")
    print("✅ Resolved the issue when the bug was fixed")
    print("✅ Maintained statistics and metrics")
    print("\nIn a real scenario, this would happen automatically")
    print("when tests fail and when they start passing again!")

def show_system_overview():
    """Show an overview of the entire automated system"""
    
    print("\n🚀 AUTOMATED BUG TRACKING SYSTEM OVERVIEW")
    print("=" * 60)
    
    components = [
        {
            "name": "GitHub Issue Manager",
            "file": "github_issue_manager.py",
            "description": "Files and manages GitHub issues for bugs"
        },
        {
            "name": "Enhanced Test Runner", 
            "file": "enhanced_test_runner.py",
            "description": "Runs tests with automatic issue filing"
        },
        {
            "name": "Issue Monitoring Agent",
            "file": "issue_monitoring_agent.py", 
            "description": "Monitors and attempts to fix GitHub issues"
        },
        {
            "name": "Automated Testing System",
            "file": "autotest.py",
            "description": "Orchestrates all testing operations"
        }
    ]
    
    print("\n📋 SYSTEM COMPONENTS:")
    for component in components:
        print(f"  🔧 {component['name']}")
        print(f"     File: {component['file']}")
        print(f"     Role: {component['description']}")
        print()
    
    print("🔄 AUTOMATED WORKFLOWS:")
    print("  1. Tests run automatically on code changes")
    print("  2. Failed tests trigger GitHub issue creation")
    print("  3. Issue monitoring agent watches for new issues")
    print("  4. Agent attempts automatic fixes")
    print("  5. Resolved bugs automatically close issues")
    print("  6. System tracks metrics and statistics")
    
    print("\n💡 USAGE EXAMPLES:")
    print("  # Run enhanced tests with issue tracking")
    print("  python3 enhanced_test_runner.py")
    print()
    print("  # Start issue monitoring agent")
    print("  python3 issue_monitoring_agent.py --once")
    print()
    print("  # View bug statistics")
    print("  python3 github_issue_manager.py --stats")

if __name__ == "__main__":
    demonstrate_bug_tracking()
    show_system_overview()