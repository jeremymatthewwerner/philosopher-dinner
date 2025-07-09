#!/usr/bin/env python3
"""
Enhanced test runner with GitHub issue integration.
Automatically files issues for bugs and resolves them when fixed.
"""

import sys
import os
import traceback
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from github_issue_manager import GitHubIssueManager
from tests.test_runner_simple import (
    test_help_command, test_langgraph_integration, 
    test_socrates_authenticity, test_full_conversation_flow
)

class EnhancedTestRunner:
    """Enhanced test runner with GitHub issue integration"""
    
    def __init__(self):
        self.issue_manager = GitHubIssueManager()
        self.test_results = {}
        
    def run_test_with_issue_tracking(self, test_func, test_name: str) -> Tuple[bool, str, str]:
        """Run a test and track issues if it fails"""
        
        try:
            # Capture stdout/stderr during test execution
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                test_func()
            
            # Test passed
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            # Check if this test was previously failing and is now passing
            self.issue_manager.check_resolved_bugs({test_name: {"status": "passed"}})
            
            return True, stdout_content, stderr_content
            
        except Exception as e:
            # Test failed
            error_message = str(e)
            traceback_str = traceback.format_exc()
            
            # File a GitHub issue for this bug
            context = {
                "test_function": test_func.__name__,
                "test_module": test_func.__module__,
                "timestamp": datetime.now().isoformat(),
                "traceback": traceback_str
            }
            
            self.issue_manager.create_bug_issue(
                test_name=test_name,
                error_message=error_message,
                test_output=traceback_str,
                context=context
            )
            
            return False, "", error_message
    
    def run_all_tests(self) -> Dict:
        """Run all tests with GitHub issue tracking"""
        
        print("🧪 PHILOSOPHER DINNER - ENHANCED TEST SUITE")
        print("=" * 60)
        print("Testing with GitHub issue tracking...")
        print("=" * 60)
        
        tests = [
            (test_help_command, "test_help_command"),
            (test_langgraph_integration, "test_langgraph_integration"),
            (test_socrates_authenticity, "test_socrates_authenticity"),
            (test_full_conversation_flow, "test_full_conversation_flow")
        ]
        
        results = {
            "passed": 0,
            "failed": 0,
            "tests": {},
            "errors": []
        }
        
        for test_func, test_name in tests:
            print(f"\n🔧 Running {test_name}...")
            
            success, stdout, stderr = self.run_test_with_issue_tracking(test_func, test_name)
            
            if success:
                print(f"  ✅ {test_name} passed")
                results["passed"] += 1
                results["tests"][test_name] = {
                    "status": "passed",
                    "stdout": stdout,
                    "stderr": stderr
                }
            else:
                print(f"  ❌ {test_name} failed: {stderr}")
                results["failed"] += 1
                results["tests"][test_name] = {
                    "status": "failed",
                    "error": stderr,
                    "stdout": stdout
                }
                results["errors"].append(f"{test_name}: {stderr}")
        
        # Show results
        print(f"\n📊 TEST RESULTS:")
        print(f"  ✅ Passed: {results['passed']}")
        print(f"  ❌ Failed: {results['failed']}")
        
        # Show bug statistics
        stats = self.issue_manager.get_bug_statistics()
        print(f"\n📊 BUG TRACKING STATISTICS:")
        print(f"  🐛 Total bugs found: {stats['total_bugs_found']}")
        print(f"  📋 Currently tracked: {stats['currently_tracked']}")
        print(f"  ✅ Resolved bugs: {stats['resolved_bugs']}")
        print(f"  📈 Resolution rate: {stats['resolution_rate']:.2%}")
        
        if results["errors"]:
            print(f"\n🐛 ERRORS (GitHub issues created):")
            for error in results["errors"]:
                print(f"  • {error}")
        else:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("  System is working correctly!")
        
        return results
    
    def check_and_resolve_bugs(self):
        """Check if any previously tracked bugs are now resolved"""
        print("\n🔍 Checking for resolved bugs...")
        
        # Run tests to get current status
        test_results = {}
        tests = [
            (test_help_command, "test_help_command"),
            (test_langgraph_integration, "test_langgraph_integration"),
            (test_socrates_authenticity, "test_socrates_authenticity"),
            (test_full_conversation_flow, "test_full_conversation_flow")
        ]
        
        for test_func, test_name in tests:
            try:
                test_func()
                test_results[test_name] = {"status": "passed"}
            except Exception:
                test_results[test_name] = {"status": "failed"}
        
        # Check for resolved bugs
        resolved_issues = self.issue_manager.check_resolved_bugs(test_results)
        
        if resolved_issues:
            print(f"✅ Resolved {len(resolved_issues)} GitHub issues:")
            for issue_num in resolved_issues:
                print(f"  • Issue #{issue_num}")
        else:
            print("  No bugs to resolve.")


def main():
    """Main function"""
    runner = EnhancedTestRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-resolved":
        runner.check_and_resolve_bugs()
    else:
        results = runner.run_all_tests()
        
        # Return appropriate exit code
        sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()