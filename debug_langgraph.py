#!/usr/bin/env python3
"""
Debug LangGraph flow to understand recursion issue
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def debug_simple_case():
    """Debug with just one agent to isolate the issue"""
    
    print("🔍 Debugging Simple Case (Socrates Only)")
    print("=" * 50)
    
    # Create single-agent forum first 
    forum_config = ForumConfig(
        forum_id="debug_simple",
        name="Debug Simple",
        description="Debug with one agent",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],  # Just one agent
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    print(f"🤖 Agents: {list(forum.agents.keys())}")
    
    # Create initial state manually and inspect it
    initial_state = forum.create_initial_state("What is virtue?")
    
    print(f"📊 Initial state keys: {list(initial_state.keys())}")
    print(f"📝 Messages: {len(initial_state['messages'])}")
    print(f"🔄 Turn count: {initial_state['turn_count']}")
    print(f"👤 Waiting for human: {initial_state['waiting_for_human']}")
    
    # Test decision making manually
    decision = forum._decide_next_speaker(initial_state)
    print(f"🎯 Next speaker decision: {decision}")
    
    if decision == "socrates":
        print("✅ Correctly identified Socrates should speak")
    elif decision == "end":
        print("⚠️ Conversation ended immediately")
    else:
        print(f"❓ Unexpected decision: {decision}")
    
    return True

def debug_mention_case():
    """Debug mention detection with multiple agents"""
    
    print("\n🔍 Debugging Mention Case (Multiple Agents)")
    print("=" * 50)
    
    # Create multi-agent forum
    forum_config = ForumConfig(
        forum_id="debug_mention",
        name="Debug Mention",
        description="Debug mention detection",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "nietzsche"],  # Two agents
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    # Test mention detection
    initial_state = forum.create_initial_state("hey nietzsche!")
    
    print(f"🤖 Agents: {list(forum.agents.keys())}")
    print(f"📝 Initial message: {initial_state['messages'][0]['content']}")
    
    # Test mention detection
    mention = forum._detect_direct_mention("hey nietzsche!")
    print(f"🎯 Detected mention: {mention}")
    
    # Test decision making
    decision = forum._decide_next_speaker(initial_state)
    print(f"🎯 Next speaker decision: {decision}")
    
    # Check agent activations
    for agent_id, agent in forum.agents.items():
        activation = agent.evaluate_activation(initial_state)
        should_respond = agent.should_respond(initial_state)
        print(f"  {agent_id}: activation={activation:.2f}, should_respond={should_respond}")
    
    return True

if __name__ == "__main__":
    debug_simple_case()
    debug_mention_case()
    print("\n✅ Debug analysis completed!")