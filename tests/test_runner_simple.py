#!/usr/bin/env python3
"""
Simple test runner that works around CLI input issues
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode
from philosopher_dinner.agents.socrates import SocratesAgent
from philosopher_dinner.cli.interface import PhilosopherCLI


def test_help_command():
    """Test help command works"""
    print("🔧 Testing help command...")
    
    cli = PhilosopherCLI()
    
    # Test help display
    from unittest.mock import patch
    from io import StringIO
    
    if cli.console:
        with patch.object(cli.console, 'print') as mock_print:
            cli._show_help()
            assert mock_print.called, "Help should display with Rich"
    
    # Test without rich
    cli_no_rich = PhilosopherCLI()
    cli_no_rich.console = None
    
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli_no_rich._show_help()
    
    output = captured_output.getvalue()
    assert "help" in output.lower(), "Help should contain help info"
    
    print("  ✅ Help command works correctly")


def test_langgraph_integration():
    """Test LangGraph integration doesn't have recursion issues"""
    print("🔄 Testing LangGraph integration...")
    
    config = ForumConfig(
        forum_id="test_forum",
        name="Test Forum",
        description="Test",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(config)
    
    # Test conversation without recursion
    result = forum.start_conversation("What is virtue?")
    
    assert "session_id" in result, "Should create session"
    assert "messages" in result, "Should have messages"
    assert result["turn_count"] <= 10, "Should not exceed turn limit"
    
    print("  ✅ LangGraph integration works without recursion")


def test_socrates_authenticity():
    """Test Socrates behaves authentically"""
    print("🏛️ Testing Socrates authenticity...")
    
    socrates = SocratesAgent()
    
    # Test personality traits
    assert socrates.personality_traits["curiosity"] >= 0.9, "Should be curious"
    assert socrates.personality_traits["humility"] >= 0.8, "Should be humble"
    
    # Test expertise
    assert "ethics" in socrates.expertise_areas, "Should know ethics"
    assert "virtue" in socrates.expertise_areas, "Should know virtue"
    
    # Test response to certainty claims
    from philosopher_dinner.forum.state import Message, MessageType
    
    test_message = Message(
        id="test-1",
        sender="human",
        content="I know that justice is fairness.",
        message_type=MessageType.HUMAN,
        timestamp=datetime.now(),
        thinking=None,
        metadata={}
    )
    
    config = ForumConfig(
        forum_id="test",
        name="Test",
        description="Test",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    
    test_state = {
        "messages": [test_message],
        "current_topic": "justice",
        "active_speakers": ["human"],
        "forum_config": config,
        "participants": ["socrates"],
        "agent_memories": {},
        "agent_activations": {},
        "turn_count": 1,
        "last_speaker": "human",
        "waiting_for_human": False,
        "session_id": "test",
        "created_at": datetime.now(),
        "last_updated": datetime.now()
    }
    
    # Should be activated by certainty claims
    activation = socrates.evaluate_activation(test_state)
    assert activation > 0.5, "Should be activated by certainty claims"
    
    # Should want to respond
    should_respond = socrates.should_respond(test_state)
    assert should_respond, "Should respond to certainty claims"
    
    # Response should contain questions
    response = socrates.generate_response(test_state)
    assert "?" in response["message"]["content"], "Should ask questions"
    
    print("  ✅ Socrates behaves authentically")


def test_full_conversation_flow():
    """Test full conversation flow"""
    print("💬 Testing full conversation flow...")
    
    config = ForumConfig(
        forum_id="test_flow",
        name="Test Flow",
        description="Test",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(config)
    
    # Test conversation sequence
    messages = [
        "What is virtue?",
        "I think virtue is doing good deeds.",
        "But how do we know what is good?"
    ]
    
    state = None
    for message in messages:
        if state is None:
            state = forum.start_conversation(message)
        else:
            state = forum.continue_conversation(state, message)
        
        # Validate state
        assert "messages" in state, "Should maintain messages"
        assert "session_id" in state, "Should maintain session"
        assert state["turn_count"] <= 10, "Should not exceed limits"
    
    print("  ✅ Full conversation flow works")


def run_simple_tests():
    """Run all simple tests"""
    
    print("🧪 PHILOSOPHER DINNER - SIMPLE TEST SUITE")
    print("=" * 60)
    print("Testing core functionality without complex mocking...")
    print("=" * 60)
    
    tests = [
        test_help_command,
        test_langgraph_integration,
        test_socrates_authenticity,
        test_full_conversation_flow
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1
            errors.append(f"{test.__name__}: {e}")
    
    print(f"\n📊 RESULTS:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    
    if errors:
        print(f"\n🐛 ERRORS:")
        for error in errors:
            print(f"  • {error}")
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("  System is working correctly!")
    
    return failed == 0


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)