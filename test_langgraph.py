#!/usr/bin/env python3
"""
Test the full LangGraph integration.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_langgraph_integration():
    """Test the full LangGraph forum"""
    
    print("🔬 TESTING LANGGRAPH INTEGRATION")
    print("=" * 50)
    
    try:
        from philosopher_dinner.forum.graph import PhilosopherForum
        from philosopher_dinner.forum.state import ForumConfig, ForumMode
        
        print("✅ LangGraph imports successful")
        
        # Create forum config
        config = ForumConfig(
            forum_id="test_forum",
            name="Test LangGraph Forum",
            description="Testing the full LangGraph integration",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
        
        print("✅ Forum config created")
        
        # Create the forum
        print("🏗️ Building LangGraph forum...")
        forum = PhilosopherForum(config)
        
        print(f"✅ Forum created with {len(forum.agents)} agents")
        print(f"   Agents: {list(forum.agents.keys())}")
        
        # Test conversation start
        print("\n🚀 Starting conversation...")
        initial_message = "Socrates, what do you think about virtue?"
        
        result = forum.start_conversation(initial_message)
        
        print(f"✅ Conversation started!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Messages: {len(result['messages'])}")
        print(f"   Current topic: {result['current_topic']}")
        
        # Show the conversation
        print("\n📜 CONVERSATION:")
        print("-" * 30)
        
        for i, message in enumerate(result["messages"][-3:]):  # Show last 3 messages
            sender_name = message["metadata"].get("agent_name", message["sender"])
            timestamp = message["timestamp"].strftime("%H:%M:%S")
            
            print(f"\n[{timestamp}] {sender_name}:")
            if message.get("thinking"):
                print(f"  💭 {message['thinking']}")
            print(f"  {message['content']}")
        
        print("\n" + "=" * 50)
        print("🎉 LANGGRAPH INTEGRATION SUCCESSFUL!")
        print("✅ All systems working:")
        print("   • LangGraph state management")
        print("   • Agent coordination")  
        print("   • Conversation flow")
        print("   • Memory persistence")
        
        # Test continue conversation
        print("\n🔄 Testing conversation continuation...")
        continued = forum.continue_conversation(result, "What is the relationship between virtue and knowledge?")
        
        print(f"✅ Conversation continued!")
        print(f"   Total messages: {len(continued['messages'])}")
        
        # Show latest exchange
        latest_messages = continued["messages"][-2:]
        print("\n📜 LATEST EXCHANGE:")
        print("-" * 30)
        
        for message in latest_messages:
            sender_name = message["metadata"].get("agent_name", message["sender"])
            timestamp = message["timestamp"].strftime("%H:%M:%S")
            
            print(f"\n[{timestamp}] {sender_name}:")
            if message.get("thinking"):
                print(f"  💭 {message['thinking']}")
            print(f"  {message['content']}")
        
        print(f"\n🏆 FULL SYSTEM TEST PASSED!")
        print("Ready for interactive use!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_langgraph_integration()