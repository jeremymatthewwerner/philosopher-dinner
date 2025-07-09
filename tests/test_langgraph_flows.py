#!/usr/bin/env python3
"""
Test LangGraph conversation flows and state management.
Catches bugs like recursion issues and state corruption.
"""

import sys
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode, Message, MessageType
from philosopher_dinner.agents.socrates import SocratesAgent


class TestLangGraphFlows:
    """Test LangGraph conversation flows"""
    
    def setup_method(self):
        """Set up test environment"""
        self.config = ForumConfig(
            forum_id="test_forum",
            name="Test Forum",
            description="Testing forum",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
    
    def test_forum_initialization(self):
        """Test forum creates correctly"""
        forum = PhilosopherForum(self.config)
        
        assert forum.forum_config == self.config
        assert "socrates" in forum.agents
        assert isinstance(forum.agents["socrates"], SocratesAgent)
        assert forum.graph is not None
    
    def test_conversation_start_no_recursion(self):
        """Test conversation starts without infinite recursion"""
        forum = PhilosopherForum(self.config)
        
        # This should complete without recursion error
        try:
            result = forum.start_conversation("What is virtue?")
            
            # Basic validations
            assert "session_id" in result
            assert "messages" in result
            assert len(result["messages"]) >= 1  # At least human message
            
            # Check for proper termination
            assert result.get("turn_count", 0) <= 10  # Should not exceed limit
            
        except Exception as e:
            if "recursion" in str(e).lower():
                pytest.fail(f"Recursion error detected: {e}")
            else:
                raise
    
    def test_conversation_continuation_limits(self):
        """Test conversation doesn't run forever"""
        forum = PhilosopherForum(self.config)
        
        # Start conversation
        state = forum.start_conversation("Test question")
        
        # Try to continue many times
        for i in range(15):  # More than the 10 turn limit
            try:
                state = forum.continue_conversation(state, f"Follow up {i}")
                
                # Should not exceed turn limit
                if state.get("turn_count", 0) > 10:
                    pytest.fail(f"Turn count exceeded limit: {state['turn_count']}")
                    
            except Exception as e:
                if "recursion" in str(e).lower():
                    pytest.fail(f"Recursion error on turn {i}: {e}")
                # Other errors might be expected at limits
                break
    
    def test_agent_response_generation(self):
        """Test agent generates valid responses"""
        forum = PhilosopherForum(self.config)
        socrates = forum.agents["socrates"]
        
        # Create test state
        test_message = Message(
            id="test-1",
            sender="human",
            content="What is wisdom?",
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        test_state = {
            "messages": [test_message],
            "current_topic": "wisdom",
            "active_speakers": ["human"],
            "forum_config": self.config,
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
        
        # Test response generation
        response = socrates.generate_response(test_state)
        
        assert response["message"] is not None
        assert response["message"]["content"] != ""
        assert response["message"]["sender"] == "socrates"
        assert response["message"]["message_type"] == MessageType.AGENT
        assert response["activation_level"] >= 0.0
        assert response["activation_level"] <= 1.0
    
    def test_coordinator_decision_making(self):
        """Test coordinator makes valid decisions"""
        forum = PhilosopherForum(self.config)
        
        # Test with human message
        state_with_human = {
            "messages": [Message(
                id="test-1",
                sender="human", 
                content="Test",
                message_type=MessageType.HUMAN,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            )],
            "turn_count": 1,
            "waiting_for_human": False
        }
        
        decision = forum._decide_next_speaker(state_with_human)
        valid_decisions = ["socrates", "human", "end"]
        assert decision in valid_decisions
        
        # Test with agent message (should end)
        state_with_agent = {
            "messages": [Message(
                id="test-2",
                sender="socrates",
                content="Test response", 
                message_type=MessageType.AGENT,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            )],
            "turn_count": 2,
            "waiting_for_human": False
        }
        
        decision = forum._decide_next_speaker(state_with_agent)
        assert decision == "end"
    
    def test_state_persistence(self):
        """Test state is properly maintained"""
        forum = PhilosopherForum(self.config)
        
        # Start conversation
        initial_state = forum.start_conversation("Test persistence")
        
        # Check initial state structure
        required_keys = [
            "messages", "current_topic", "active_speakers", "forum_config",
            "participants", "agent_memories", "agent_activations", 
            "turn_count", "session_id", "created_at", "last_updated"
        ]
        
        for key in required_keys:
            assert key in initial_state, f"Missing required key: {key}"
        
        # Continue conversation
        continued_state = forum.continue_conversation(initial_state, "Follow up")
        
        # Check state evolution
        assert continued_state["session_id"] == initial_state["session_id"]
        assert len(continued_state["messages"]) >= len(initial_state["messages"])
        assert continued_state["turn_count"] >= initial_state["turn_count"]


class TestErrorScenarios:
    """Test error handling in LangGraph flows"""
    
    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        config = ForumConfig(
            forum_id="test",
            name="Test",
            description="Test", 
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
        
        forum = PhilosopherForum(config)
        
        # Test with empty message
        result = forum.start_conversation("")
        assert "messages" in result
        assert len(result["messages"]) >= 1
    
    def test_invalid_state_recovery(self):
        """Test recovery from invalid state"""
        config = ForumConfig(
            forum_id="test",
            name="Test",
            description="Test",
            mode=ForumMode.EXPLORATION, 
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
        
        forum = PhilosopherForum(config)
        
        # Create invalid state
        invalid_state = {
            "messages": [],
            "turn_count": 100,  # Exceeds limit
            "session_id": "test"
        }
        
        # Should handle gracefully
        try:
            result = forum.continue_conversation(invalid_state, "Test recovery")
            # Should not crash
            assert "messages" in result
        except Exception as e:
            # Should not be recursion error
            assert "recursion" not in str(e).lower()


def run_langgraph_tests():
    """Run all LangGraph tests and report results"""
    
    print("🔄 RUNNING LANGGRAPH FLOW TESTS")
    print("=" * 50)
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test classes to run
    test_classes = [
        TestLangGraphFlows(),
        TestErrorScenarios()
    ]
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 Testing {class_name}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                # Setup if needed
                if hasattr(test_class, 'setup_method'):
                    test_class.setup_method()
                
                # Run test
                test_method = getattr(test_class, method_name)
                test_method()
                
                print(f"  ✅ {method_name}")
                test_results["passed"] += 1
                
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                test_results["failed"] += 1
                test_results["errors"].append(f"{class_name}.{method_name}: {e}")
    
    # Report results
    print(f"\n📊 TEST RESULTS:")
    print(f"  ✅ Passed: {test_results['passed']}")
    print(f"  ❌ Failed: {test_results['failed']}")
    
    if test_results["errors"]:
        print(f"\n🐛 ERRORS FOUND:")
        for error in test_results["errors"]:
            print(f"  • {error}")
    
    return test_results


if __name__ == "__main__":
    run_langgraph_tests()