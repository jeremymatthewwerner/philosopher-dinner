#!/usr/bin/env python3
"""
Test the actual CLI to see if diversity is working
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.cli.interface import PhilosopherCLI
from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def test_cli_setup():
    """Test what the CLI actually sets up"""
    
    print("🧪 Testing CLI Setup")
    print("=" * 50)
    
    cli = PhilosopherCLI()
    
    # Check what forum config the CLI creates
    forum_config = cli._setup_forum()
    
    print(f"📋 Forum Config:")
    print(f"  Name: {forum_config['name']}")
    print(f"  Participants: {forum_config['participants']}")
    print(f"  Mode: {forum_config['mode']}")
    
    # Create the forum as CLI does
    forum = PhilosopherForum(forum_config)
    
    print(f"\n🤖 Actual Agents Created:")
    for agent_id, agent in forum.agents.items():
        print(f"  - {agent_id}: {agent.name}")
    
    # Test a few messages
    test_messages = [
        "anyone else here?",
        "what is the meaning of life?",
        "hello philosophers!"
    ]
    
    print(f"\n🎯 Testing Agent Selection:")
    for msg in test_messages:
        state = forum.create_initial_state(msg)
        decision = forum._decide_next_speaker(state)
        print(f"  '{msg}' → {decision}")
    
    return len(forum.agents)

def test_multiple_runs():
    """Test multiple runs to see if we get variety"""
    
    print("\n🧪 Testing Multiple Runs for Variety")
    print("=" * 50)
    
    forum_config = ForumConfig(
        forum_id="test_variety",
        name="Multi-Agent Philosophy Forum",
        description="A place for philosophical discourse with diverse thinkers across time periods",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "kant", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    # Test the same question multiple times
    results = {}
    test_msg = "anyone else here?"
    
    print(f"Testing '{test_msg}' 10 times:")
    for i in range(10):
        forum = PhilosopherForum(forum_config)  # Fresh forum each time
        state = forum.create_initial_state(test_msg)
        decision = forum._decide_next_speaker(state)
        results[decision] = results.get(decision, 0) + 1
    
    print("\n📊 Response Distribution:")
    for agent, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {agent}: {count} times ({count*10}%)")
    
    if len(results) > 1:
        print("\n✅ Multiple agents are responding!")
    else:
        print("\n❌ Only one agent responding")
    
    return len(results)

def check_activation_details():
    """Check detailed activation for each agent"""
    
    print("\n🧪 Detailed Activation Analysis")
    print("=" * 50)
    
    forum_config = ForumConfig(
        forum_id="test_activation",
        name="Test Forum",
        description="Test",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "kant", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    state = forum.create_initial_state("anyone else here?")
    
    print("📊 Agent Activation Details:")
    print(f"  Threshold: 0.3 (for {len(forum.agents)} agents)")
    
    activations = {}
    for agent_id, agent in forum.agents.items():
        activation = agent.evaluate_activation(state)
        should_respond = agent.should_respond(state, 0.3)
        activations[agent_id] = activation
        
        print(f"\n  {agent_id}:")
        print(f"    Activation: {activation:.3f}")
        print(f"    Should Respond: {should_respond}")
        print(f"    Personality: {list(agent.personality_traits.keys())[:3]}...")
    
    # Show who would be chosen
    decision = forum._decide_next_speaker(state)
    print(f"\n🎯 Selected: {decision}")
    
    return decision

if __name__ == "__main__":
    print("🚀 CLI DIVERSITY TESTING")
    print("=" * 70)
    
    agent_count = test_cli_setup()
    variety_count = test_multiple_runs()
    selected = check_activation_details()
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY:")
    print(f"  Agents in CLI: {agent_count}")
    print(f"  Unique responders: {variety_count}")
    print(f"  Selected agent: {selected}")
    
    if variety_count > 1:
        print("\n🎉 Multi-agent diversity is working!")
        print("If you're still seeing only Socrates, try:")
        print("  1. Restart the CLI application")
        print("  2. Make sure you're using the latest code")
        print("  3. Check if there are any database errors")
    else:
        print("\n⚠️ Still seeing single-agent responses")
        print("There may be an issue with the current setup")