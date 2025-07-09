#!/usr/bin/env python3
"""
Test agent behavior and personality consistency.
Ensures agents respond authentically and maintain character.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from philosopher_dinner.agents.socrates import SocratesAgent
from philosopher_dinner.forum.state import ForumConfig, ForumMode, Message, MessageType


class TestSocratesAuthenticity:
    """Test Socrates agent behaves authentically"""
    
    def setup_method(self):
        """Set up test environment"""
        self.socrates = SocratesAgent()
        self.config = ForumConfig(
            forum_id="test",
            name="Test",
            description="Test",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
    
    def test_socrates_personality_traits(self):
        """Test Socrates has correct personality traits"""
        traits = self.socrates.personality_traits
        
        # Key Socratic traits
        assert traits["curiosity"] >= 0.9, "Socrates should be highly curious"
        assert traits["humility"] >= 0.8, "Socrates should be humble"
        assert traits["extroversion"] >= 0.7, "Socrates should be social"
        assert traits["openness"] >= 0.8, "Socrates should be open to ideas"
    
    def test_socrates_expertise_areas(self):
        """Test Socrates has correct expertise"""
        expertise = self.socrates.expertise_areas
        
        expected_areas = ["ethics", "moral philosophy", "virtue", "knowledge", "questioning method"]
        
        for area in expected_areas:
            assert area in expertise, f"Socrates should have expertise in {area}"
    
    def test_socrates_questioning_method(self):
        """Test Socrates uses questioning in responses"""
        
        # Create test state
        test_message = Message(
            id="test-1",
            sender="human",
            content="I know what justice is.",
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        test_state = {
            "messages": [test_message],
            "current_topic": "justice",
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
        
        response = self.socrates.generate_response(test_state)
        message_content = response["message"]["content"]
        
        # Should contain questions
        assert "?" in message_content, "Socrates should ask questions"
        
        # Should not make definitive claims
        claim_words = ["I know", "certainly", "definitely", "obviously"]
        for word in claim_words:
            assert word.lower() not in message_content.lower(), f"Socrates should not claim to know: {word}"
    
    def test_socrates_response_to_certainty(self):
        """Test Socrates challenges claims of certainty"""
        
        certainty_claims = [
            "I know that justice is fairness.",
            "Obviously, the good life is about pleasure.",
            "Clearly, virtue is just following rules.",
            "I am certain that wisdom means knowing facts."
        ]
        
        for claim in certainty_claims:
            test_message = Message(
                id="test-certainty",
                sender="human", 
                content=claim,
                message_type=MessageType.HUMAN,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            )
            
            test_state = {
                "messages": [test_message],
                "current_topic": "philosophy",
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
            
            # Socrates should be highly activated by certainty claims
            activation = self.socrates.evaluate_activation(test_state)
            assert activation > 0.6, f"Socrates should be activated by certainty: {claim}"
            
            # Should want to respond
            should_respond = self.socrates.should_respond(test_state)
            assert should_respond, f"Socrates should respond to certainty: {claim}"
    
    def test_socrates_humility_phrases(self):
        """Test Socrates uses humble phrases"""
        
        test_message = Message(
            id="test-1",
            sender="human",
            content="What do you think about wisdom?",
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
        
        # Generate multiple responses to test consistency
        humble_phrases_found = 0
        expected_phrases = [
            "I know that I know nothing",
            "I am curious",
            "Tell me",
            "Help me understand",
            "I wonder",
            "Can you help me"
        ]
        
        for i in range(5):  # Test multiple responses
            response = self.socrates.generate_response(test_state)
            content = response["message"]["content"]
            
            for phrase in expected_phrases:
                if phrase.lower() in content.lower():
                    humble_phrases_found += 1
                    break
        
        assert humble_phrases_found > 0, "Socrates should use humble phrases"


class TestAgentActivation:
    """Test agent activation and participation logic"""
    
    def setup_method(self):
        """Set up test environment"""
        self.socrates = SocratesAgent()
        self.config = ForumConfig(
            forum_id="test",
            name="Test",
            description="Test",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
    
    def test_topic_relevance_activation(self):
        """Test activation based on topic relevance"""
        
        # Test high relevance topics
        high_relevance_topics = ["ethics", "virtue", "justice", "knowledge", "wisdom"]
        
        for topic in high_relevance_topics:
            test_message = Message(
                id="test-topic",
                sender="human",
                content=f"Let's discuss {topic}",
                message_type=MessageType.HUMAN,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            )
            
            test_state = {
                "messages": [test_message],
                "current_topic": topic,
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
            
            activation = self.socrates.evaluate_activation(test_state)
            assert activation > 0.5, f"Should be activated by {topic}: {activation}"
    
    def test_no_spam_protection(self):
        """Test agent doesn't spam consecutive responses"""
        
        # Create state where Socrates spoke recently
        socrates_message = Message(
            id="socrates-1",
            sender="socrates",
            content="Previous response",
            message_type=MessageType.AGENT,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        human_message = Message(
            id="human-1", 
            sender="human",
            content="Follow up question",
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        test_state = {
            "messages": [socrates_message, human_message],
            "current_topic": "ethics",
            "active_speakers": ["socrates", "human"],
            "forum_config": self.config,
            "participants": ["socrates"],
            "agent_memories": {},
            "agent_activations": {},
            "turn_count": 2,
            "last_speaker": "human",
            "waiting_for_human": False,
            "session_id": "test",
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
        
        # Should not respond to own messages
        test_state["messages"] = [socrates_message]
        test_state["last_speaker"] = "socrates"
        should_respond = self.socrates.should_respond(test_state)
        assert not should_respond, "Should not respond to own messages"


def run_agent_tests():
    """Run all agent behavior tests and report results"""
    
    print("🎭 RUNNING AGENT BEHAVIOR TESTS")
    print("=" * 50)
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test classes to run
    test_classes = [
        TestSocratesAuthenticity(),
        TestAgentActivation()
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
    run_agent_tests()