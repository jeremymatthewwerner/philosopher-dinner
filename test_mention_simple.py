#!/usr/bin/env python3
"""
Simple test for mention detection without LangGraph
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def test_basic_functionality():
    """Test basic setup without triggering LangGraph execution"""
    
    print("🧪 Testing Basic Multi-Agent Setup")
    print("=" * 50)
    
    # Create multi-agent forum config
    forum_config = ForumConfig(
        forum_id="test_basic",
        name="Basic Test",
        description="Testing basic functionality",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    # Initialize forum
    forum = PhilosopherForum(forum_config)
    
    print(f"🤖 Agents created: {list(forum.agents.keys())}")
    
    # Test mention detection directly
    test_messages = [
        "confucius what say you?",
        "hey nietzsche!",
        "what would socrates say?",
        "general question about happiness"
    ]
    
    print("\n🔍 Testing Mention Detection:")
    for msg in test_messages:
        detected = forum._detect_direct_mention(msg)
        print(f"  '{msg}' -> {detected}")
    
    # Test agent info
    print("\n📋 Agent Information:")
    for agent_id, agent in forum.agents.items():
        era = getattr(agent, 'era', 'Ancient Greece')
        print(f"  {agent_id}: {agent.name} ({era})")
        print(f"    Expertise: {', '.join(agent.expertise_areas[:3])}...")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()
    print("\n✅ Basic functionality test completed!")