#!/usr/bin/env python3
"""
Debug the recursion issue
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode, MessageType

def debug_recursion():
    """Debug why recursion happens"""
    
    print("🔍 Debugging Recursion Issue")
    print("=" * 50)
    
    forum_config = ForumConfig(
        forum_id="debug",
        name="Debug Forum",
        description="Debug",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle"],  # Just 2 agents
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    print(f"🤖 Agents: {list(forum.agents.keys())}")
    
    # Create initial state
    state = forum.create_initial_state("hello philosophers")
    
    print(f"\n📊 Initial State:")
    print(f"  Messages: {len(state['messages'])}")
    print(f"  Turn count: {state['turn_count']}")
    print(f"  Waiting for human: {state['waiting_for_human']}")
    
    # Manually step through decision process
    print(f"\n🎯 Decision Process:")
    
    for i in range(10):  # Limit iterations
        decision = forum._decide_next_speaker(state)
        print(f"  Step {i+1}: Next speaker = {decision}")
        
        if decision == "end":
            print("  ✅ Conversation ended properly")
            break
        elif decision == "human":
            print("  ⏸️ Waiting for human")
            break
        elif decision in forum.agents:
            # Simulate agent response
            agent = forum.agents[decision]
            activation = agent.evaluate_activation(state)
            threshold = 0.3 if len(forum.agents) > 2 else 0.6
            should_respond = agent.should_respond(state, threshold)
            
            print(f"    {decision}: activation={activation:.2f}, threshold={threshold}, should_respond={should_respond}")
            
            if should_respond:
                print(f"    {decision} is responding...")
                # Add a dummy message to simulate response
                from philosopher_dinner.forum.state import Message
                import uuid
                
                msg = Message(
                    id=str(uuid.uuid4()),
                    sender=decision,
                    content=f"Response from {decision}",
                    message_type=MessageType.AGENT,
                    timestamp=datetime.now(),
                    thinking=None,
                    metadata={}
                )
                state["messages"].append(msg)
                state["turn_count"] += 1
                state["last_speaker"] = decision
            else:
                print(f"    {decision} doesn't want to respond")
                break
        else:
            print(f"  ❓ Unknown decision: {decision}")
            break
    
    print(f"\n📊 Final State:")
    print(f"  Messages: {len(state['messages'])}")
    print(f"  Turn count: {state['turn_count']}")
    print(f"  Agent messages: {sum(1 for m in state['messages'] if m['message_type'] == MessageType.AGENT)}")
    
    # Check why it doesn't end
    if state["messages"] and state["messages"][-1]["message_type"] == MessageType.AGENT:
        print("\n✅ Last message is from agent - should end")
    else:
        print("\n❌ Last message is NOT from agent")
    
    return state

if __name__ == "__main__":
    debug_recursion()