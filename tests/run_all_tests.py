#!/usr/bin/env python3
"""
Comprehensive test runner for the Philosopher Dinner system.
Automatically finds and reports bugs before users encounter them.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_dependencies import main as run_dependency_tests
from test_cli_interactions import run_cli_tests
from test_langgraph_flows import run_langgraph_tests 
from test_agent_behavior import run_agent_tests
from test_real_cli_execution import run_all_real_tests


def run_integration_tests():
    """Run integration tests that combine multiple components"""
    
    print("🔗 RUNNING INTEGRATION TESTS")
    print("=" * 50)
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    try:
        # Test full conversation flow
        print("\n📋 Testing full conversation flow...")
        
        from philosopher_dinner.forum.graph import PhilosopherForum
        from philosopher_dinner.forum.state import ForumConfig, ForumMode
        
        config = ForumConfig(
            forum_id="integration_test",
            name="Integration Test Forum",
            description="Testing end-to-end flow",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
        
        forum = PhilosopherForum(config)
        
        # Test conversation sequence
        test_messages = [
            "What is virtue?",
            "I think virtue is doing good deeds.",
            "But how do we know what is good?",
            "Can we be virtuous without wisdom?"
        ]
        
        state = None
        for i, message in enumerate(test_messages):
            if state is None:
                state = forum.start_conversation(message)
            else:
                state = forum.continue_conversation(state, message)
            
            # Validate state integrity
            assert "messages" in state
            assert "session_id" in state
            assert state["turn_count"] <= 10
            
            print(f"  ✅ Message {i+1}: {message[:30]}...")
            test_results["passed"] += 1
        
        print(f"  ✅ Full conversation flow completed")
        test_results["passed"] += 1
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Integration: {e}")
    
    return test_results


def run_user_scenario_tests():
    """Test realistic user scenarios"""
    
    print("👤 RUNNING USER SCENARIO TESTS")
    print("=" * 50)
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test the specific bug reported by user
    print("\n🐛 Testing reported help command bug...")
    
    try:
        from philosopher_dinner.cli.interface import PhilosopherCLI
        from unittest.mock import patch
        
        cli = PhilosopherCLI()
        
        # Test help command with Rich
        if cli.console:
            with patch.object(cli.console, 'print') as mock_print:
                cli._show_help()
                
                # Should have been called
                assert mock_print.called, "Help should display with Rich"
                print("  ✅ Help command works with Rich")
                test_results["passed"] += 1
        
        # Test help command without Rich
        cli_no_rich = PhilosopherCLI()
        cli_no_rich.console = None
        
        from io import StringIO
        captured_output = StringIO()
        
        with patch('sys.stdout', captured_output):
            cli_no_rich._show_help()
        
        output = captured_output.getvalue()
        assert len(output) > 0, "Help should display without Rich"
        assert "help" in output.lower(), "Help should contain help info"
        
        print("  ✅ Help command works without Rich")
        test_results["passed"] += 1
        
    except Exception as e:
        print(f"  ❌ Help command test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Help command: {e}")
    
    # Test other user scenarios
    scenarios = [
        ("Empty input handling", ""),
        ("Quit command", "quit"),
        ("Exit command", "exit"),
        ("Long philosophical question", "What is the relationship between virtue, knowledge, and the good life according to different philosophical traditions?")
    ]
    
    for scenario_name, input_text in scenarios:
        try:
            print(f"\n📋 Testing {scenario_name}...")
            
            # Test with CLI input processing
            cli = PhilosopherCLI()
            
            with patch('builtins.input', return_value=input_text):
                result = cli._get_user_input("Test: ")
                
                if input_text in ["quit", "exit"]:
                    # Should handle quit commands
                    pass
                elif input_text == "":
                    # Should handle empty input
                    assert result == ""
                else:
                    # Should preserve normal input
                    assert result == input_text
            
            print(f"  ✅ {scenario_name}")
            test_results["passed"] += 1
            
        except Exception as e:
            print(f"  ❌ {scenario_name}: {e}")
            test_results["failed"] += 1
            test_results["errors"].append(f"{scenario_name}: {e}")
    
    return test_results


def generate_test_report(all_results):
    """Generate comprehensive test report"""
    
    total_passed = sum(result["passed"] for result in all_results)
    total_failed = sum(result["failed"] for result in all_results)
    total_errors = []
    
    for result in all_results:
        total_errors.extend(result["errors"])
    
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    print(f"📊 Overall Results:")
    print(f"  ✅ Total Passed: {total_passed}")
    print(f"  ❌ Total Failed: {total_failed}")
    print(f"  🎯 Success Rate: {total_passed/(total_passed+total_failed)*100:.1f}%")
    
    if total_errors:
        print(f"\n🐛 BUGS FOUND ({len(total_errors)}):")
        for i, error in enumerate(total_errors, 1):
            print(f"  {i}. {error}")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        print("  1. Fix the identified bugs before user release")
        print("  2. Run tests again after fixes")
        print("  3. Consider adding more edge case tests")
        print("  4. Implement continuous integration")
    else:
        print(f"\n🎉 NO BUGS FOUND!")
        print("  All tests passed - system is ready for users")
    
    return {
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "success_rate": total_passed/(total_passed+total_failed)*100 if (total_passed+total_failed) > 0 else 0
    }


def main():
    """Run the complete test suite"""
    
    print("🚀 PHILOSOPHER DINNER - AUTOMATED TEST SUITE")
    print("=" * 60)
    print("Finding bugs before users encounter them...")
    print("=" * 60)
    
    # Run all test suites
    all_results = []
    
    # FIRST: Check dependencies (must pass before running other tests)
    print("\n" + "=" * 60)
    dep_result = run_dependency_tests()
    if dep_result != 0:
        print("\n❌ CRITICAL: Dependency check failed!")
        print("   Cannot run other tests until dependencies are fixed.")
        return 1
    print("=" * 60 + "\n")
    
    # Component tests
    all_results.append(run_cli_tests())
    all_results.append(run_langgraph_tests())
    all_results.append(run_agent_tests())
    
    # Integration tests
    all_results.append(run_integration_tests())
    
    # User scenario tests
    all_results.append(run_user_scenario_tests())
    
    # Real CLI execution tests
    print("\n" + "=" * 60)
    real_test_results = {"passed": 0, "failed": 0, "errors": []}
    if run_all_real_tests():
        real_test_results["passed"] = 4  # 4 real tests
    else:
        real_test_results["failed"] = 4
        real_test_results["errors"].append("Real CLI execution failures")
    all_results.append(real_test_results)
    print("=" * 60)
    
    # Generate final report
    report = generate_test_report(all_results)
    
    # Return exit code based on results
    return 0 if report["total_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())