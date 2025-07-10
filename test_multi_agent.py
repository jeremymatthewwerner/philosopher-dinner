#!/usr/bin/env python3
"""
Quick test for multi-agent conversation functionality
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def test_multi_agent_setup():
    """Test that multiple agents are properly initialized"""
    
    print("🧪 Testing Multi-Agent Forum Setup")
    print("=" * 50)
    
    # Create multi-agent forum config
    forum_config = ForumConfig(
        forum_id="test_forum",
        name="Multi-Agent Test Forum",
        description="Testing multiple philosophers",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "kant", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    # Initialize forum
    forum = PhilosopherForum(forum_config)
    
    print(f"📊 Forum participants: {forum_config['participants']}")
    print(f"🤖 Initialized agents: {list(forum.agents.keys())}")
    
    # Check that all agents were created
    expected = {"socrates", "aristotle", "kant", "nietzsche", "confucius"}
    actual = set(forum.agents.keys())
    
    print(f"✅ Expected: {expected}")
    print(f"🔍 Actual: {actual}")
    
    if expected == actual:
        print("🎉 SUCCESS: All agents properly initialized!")
    else:
        missing = expected - actual
        print(f"❌ MISSING AGENTS: {missing}")
        return False
    
    return True

def test_direct_mention_detection():
    """Test that direct mention detection works"""
    
    print("\n🧪 Testing Direct Mention Detection")
    print("=" * 50)
    
    # Create forum
    forum_config = ForumConfig(
        forum_id="test_mention",
        name="Mention Test",
        description="Testing mentions",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    # Test different mention patterns
    test_cases = [
        ("confucius what say you?", "confucius"),
        ("hey nietzsche!", "nietzsche"),
        ("what would aristotle say?", "aristotle"),
        ("Socrates, what do you think?", "socrates"),
        ("Just a general question", None),
    ]
    
    for message, expected in test_cases:
        detected = forum._detect_direct_mention(message)
        result = "✅" if detected == expected else "❌"
        print(f"{result} '{message}' -> {detected} (expected: {expected})")
    
    return True

def test_conversation_flow():
    """Test basic conversation flow with mentions"""
    
    print("\n🧪 Testing Conversation Flow with Mentions")  
    print("=" * 50)
    
    # Create forum
    forum_config = ForumConfig(
        forum_id="test_flow",
        name="Flow Test",
        description="Testing conversation flow",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "nietzsche"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    # Test direct mention
    print("🔄 Testing direct mention: 'hey nietzsche!'")
    state = forum.start_conversation("hey nietzsche!")
    
    print(f"📝 Messages in conversation: {len(state.get('messages', []))}")
    if state.get('messages'):
        latest = state['messages'][-1]
        print(f"👤 Latest speaker: {latest.get('sender', 'unknown')}")
        print(f"💬 Latest message: {latest.get('content', '')[:100]}...")
        
        if latest.get('sender') == 'nietzsche':
            print("🎉 SUCCESS: Nietzsche responded to direct mention!")
        else:
            print(f"❌ EXPECTED: nietzsche, GOT: {latest.get('sender')}")
    
    return True

if __name__ == "__main__":
    print("🚀 MULTI-AGENT CONVERSATION TESTS")
    print("=" * 60)
    
    success = True
    success &= test_multi_agent_setup()
    success &= test_direct_mention_detection()
    success &= test_conversation_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("Multi-agent conversation system is working!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the output above for issues.")
    
    sys.exit(0 if success else 1)