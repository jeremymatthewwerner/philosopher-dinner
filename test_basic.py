#!/usr/bin/env python3
"""
Test the basic structure without LangGraph dependencies.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_structure():
    """Test that our basic classes work"""
    
    # Test state creation
    from philosopher_dinner.forum.state import ForumState, ForumConfig, ForumMode, Message, MessageType
    
    # Create a simple forum config
    config = ForumConfig(
        forum_id="test",
        name="Test Forum",
        description="Testing",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    
    print("✅ ForumConfig created successfully")
    
    # Test message creation
    message = Message(
        id="test-1",
        sender="human",
        content="Hello, Socrates!",
        message_type=MessageType.HUMAN,
        timestamp=datetime.now(),
        thinking=None,
        metadata={}
    )
    
    print("✅ Message created successfully")
    
    # Test Socrates agent
    from philosopher_dinner.agents.socrates import SocratesAgent
    
    socrates = SocratesAgent()
    print(f"✅ Socrates agent created: {socrates.name}")
    print(f"   Expertise: {socrates.expertise_areas[:3]}...")
    print(f"   Personality: {socrates.personality_traits}")
    
    # Test basic activation
    test_state = ForumState(
        messages=[message],
        current_topic="wisdom",
        active_speakers=[],
        forum_config=config,
        participants=["socrates"],
        agent_memories={},
        agent_activations={},
        turn_count=1,
        last_speaker="human",
        waiting_for_human=False,
        session_id="test-session",
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    
    activation = socrates.evaluate_activation(test_state)
    print(f"✅ Socrates activation level: {activation:.2f}")
    
    should_respond = socrates.should_respond(test_state)
    print(f"✅ Should Socrates respond? {should_respond}")
    
    print("\n🎉 Basic structure test passed!")
    print("Ready to test with LangGraph when dependencies are installed.")

if __name__ == "__main__":
    test_basic_structure()