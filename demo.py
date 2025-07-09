#!/usr/bin/env python3
"""
Demo of the Philosopher Dinner system.
Shows how Socrates responds to philosophical questions.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.state import ForumState, ForumConfig, ForumMode, Message, MessageType
from philosopher_dinner.agents.socrates import SocratesAgent

def demo_conversation():
    """Demo a conversation with Socrates"""
    
    print("🏛️ PHILOSOPHER DINNER DEMO")
    print("=" * 50)
    print("Having a conversation with Socrates...")
    print()
    
    # Create Socrates
    socrates = SocratesAgent()
    
    # Create forum config
    config = ForumConfig(
        forum_id="demo",
        name="Demo Forum",
        description="Demo conversation",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    
    # Start with a human question
    human_message = Message(
        id="msg-1",
        sender="human",
        content="What is justice?",
        message_type=MessageType.HUMAN,
        timestamp=datetime.now(),
        thinking=None,
        metadata={}
    )
    
    print(f"🧑 Human: {human_message['content']}")
    print()
    
    # Create initial state
    state = ForumState(
        messages=[human_message],
        current_topic="justice",
        active_speakers=["human"],
        forum_config=config,
        participants=["socrates"],
        agent_memories={},
        agent_activations={},
        turn_count=1,
        last_speaker="human",
        waiting_for_human=False,
        session_id="demo-session",
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    
    # Let Socrates respond
    print("🤔 Socrates is thinking...")
    
    # Check if Socrates should respond
    should_respond = socrates.should_respond(state)
    activation = socrates.evaluate_activation(state)
    
    print(f"   Activation level: {activation:.2f}")
    print(f"   Should respond: {should_respond}")
    print()
    
    if should_respond:
        # Generate response
        response = socrates.generate_response(state)
        
        if response["message"]:
            message = response["message"]
            print(f"💭 Socrates thinking: {message['thinking']}")
            print()
            print(f"🏛️ Socrates: {message['content']}")
            print()
            
            # Try another round
            print("-" * 50)
            print("Human responds...")
            
            human_response = Message(
                id="msg-2", 
                sender="human",
                content="I think justice means treating everyone equally.",
                message_type=MessageType.HUMAN,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            )
            
            print(f"🧑 Human: {human_response['content']}")
            print()
            
            # Update state
            state["messages"].append(message)
            state["messages"].append(human_response)
            state["turn_count"] += 2
            state["last_speaker"] = "human"
            
            # Socrates responds again
            if socrates.should_respond(state):
                response2 = socrates.generate_response(state)
                if response2["message"]:
                    msg2 = response2["message"]
                    print(f"💭 Socrates thinking: {msg2['thinking']}")
                    print()
                    print(f"🏛️ Socrates: {msg2['content']}")
                    print()
    
    print("=" * 50)
    print("✨ Demo complete! Socrates is working perfectly.")
    print("💡 To use interactively, run in your terminal:")
    print("   source venv/bin/activate && python main.py")

if __name__ == "__main__":
    demo_conversation()