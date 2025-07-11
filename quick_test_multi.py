#!/usr/bin/env python3
"""
Quick test to verify multi-agent response to general questions
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def test_general_question():
    """Test how agents respond to a general question like 'anyone else here?'"""
    
    print("🧪 Testing General Question: 'anyone else here?'")
    print("=" * 60)
    
    # Create forum
    forum_config = ForumConfig(
        forum_id="test_general",
        name="General Test",
        description="Testing general responses",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    print(f"🤖 Available agents: {list(forum.agents.keys())}")
    
    # Test agent activations for a general question
    test_message = "anyone else here?"
    state = forum.create_initial_state(test_message)
    
    print(f"\n📝 Testing message: '{test_message}'")
    print(f"🎯 Mention detection: {forum._detect_direct_mention(test_message)}")
    
    print(f"\n⚡ Agent Activations:")
    agent_scores = {}
    for agent_id, agent in forum.agents.items():
        activation = agent.evaluate_activation(state)
        should_respond = agent.should_respond(state)
        agent_scores[agent_id] = activation
        print(f"  {agent_id}: activation={activation:.2f}, should_respond={should_respond}")
    
    # Test decision logic
    decision = forum._decide_next_speaker(state)
    print(f"\n🎯 Decision: Next speaker should be '{decision}'")
    
    if decision in forum.agents:
        print(f"✅ {decision} selected to respond")
        best_score = max(agent_scores.values())
        print(f"📊 Highest activation: {best_score:.2f}")
    elif decision == "end":
        print("⚠️ Conversation ended (no one wants to speak)")
    else:
        print(f"❓ Unexpected decision: {decision}")
    
    return decision

def test_specific_mention():
    """Test response to specific mention"""
    
    print("\n🧪 Testing Specific Mention: 'hey aristotle!'")
    print("=" * 60)
    
    forum_config = ForumConfig(
        forum_id="test_mention", 
        name="Mention Test",
        description="Testing mentions",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    test_message = "hey aristotle!"
    state = forum.create_initial_state(test_message)
    
    print(f"📝 Testing message: '{test_message}'")
    print(f"🎯 Mention detection: {forum._detect_direct_mention(test_message)}")
    
    decision = forum._decide_next_speaker(state)
    print(f"🎯 Decision: '{decision}'")
    
    if decision == "aristotle":
        print("✅ Aristotle correctly selected for mention")
    else:
        print(f"❌ Expected aristotle, got {decision}")
    
    return decision

if __name__ == "__main__":
    print("🚀 QUICK MULTI-AGENT TESTS")
    print("=" * 70)
    
    general_result = test_general_question()
    mention_result = test_specific_mention()
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY:")
    print(f"  General question → {general_result}")
    print(f"  Specific mention → {mention_result}")
    
    if general_result != "socrates" and mention_result == "aristotle":
        print("🎉 Multi-agent system working correctly!")
    else:
        print("⚠️ Issues detected in multi-agent responses")