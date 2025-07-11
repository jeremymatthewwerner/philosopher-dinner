#!/usr/bin/env python3
"""
Test the new lower threshold for multi-agent conversations
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def test_threshold_logic():
    """Test threshold logic with different numbers of agents"""
    
    print("🧪 Testing Threshold Logic")
    print("=" * 50)
    
    # Test with 4 agents (should use 0.4 threshold)
    forum_config = ForumConfig(
        forum_id="test_multi",
        name="Multi Test",
        description="Testing with multiple agents",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    state = forum.create_initial_state("anyone else here?")
    
    print(f"🤖 Agents: {len(forum.agents)} → threshold should be 0.3")
    
    # Test each agent's should_respond with different thresholds
    print(f"\n⚡ Agent Responses with Different Thresholds:")
    for agent_id, agent in forum.agents.items():
        activation = agent.evaluate_activation(state)
        responds_06 = agent.should_respond(state, 0.6)
        responds_03 = agent.should_respond(state, 0.3)
        responds_02 = agent.should_respond(state, 0.2)
        print(f"  {agent_id}: activation={activation:.2f}")
        print(f"    @ 0.6: {responds_06}, @ 0.3: {responds_03}, @ 0.2: {responds_02}")
    
    # Test the actual decision logic
    decision = forum._decide_next_speaker(state)
    print(f"\n🎯 Decision with new logic: {decision}")
    
    return decision

def test_different_questions():
    """Test with different types of questions to see variety"""
    
    questions = [
        "What is truth?",
        "How should we live?", 
        "What is justice?",
        "What is the meaning of life?",
        "Anyone have thoughts on virtue?"
    ]
    
    print(f"\n🧪 Testing Question Variety")
    print("=" * 50)
    
    forum_config = ForumConfig(
        forum_id="test_variety",
        name="Variety Test", 
        description="Testing question variety",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    responses = {}
    for question in questions:
        forum = PhilosopherForum(forum_config)  # Fresh forum for each question
        state = forum.create_initial_state(question)
        decision = forum._decide_next_speaker(state)
        responses[question] = decision
        print(f"'{question}' → {decision}")
    
    # Count unique responders
    unique_responders = set(responses.values())
    print(f"\n📊 Unique responders: {len(unique_responders)} ({unique_responders})")
    
    if len(unique_responders) > 1:
        print("✅ Multiple agents responding to different questions!")
    else:
        print("⚠️ Only one agent responding to all questions")
    
    return len(unique_responders)

if __name__ == "__main__":
    print("🚀 THRESHOLD TESTING")
    print("=" * 60)
    
    decision = test_threshold_logic()
    variety = test_different_questions()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"  Decision: {decision}")
    print(f"  Variety: {variety} unique responders")
    
    if variety > 1:
        print("🎉 Multi-agent diversity achieved!")
    else:
        print("⚠️ Still getting single-agent responses")