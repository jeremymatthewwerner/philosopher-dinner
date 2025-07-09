#!/usr/bin/env python3
"""
Your personal interactive chat with Socrates.
Run this and have a real conversation!
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def your_chat():
    """Your personal chat session with Socrates"""
    
    print("🏛️ WELCOME TO YOUR PERSONAL SOCRATIC DIALOGUE")
    print("=" * 55)
    print("You are now in a private conversation with Socrates.")
    print("Ask him anything about philosophy, life, death, virtue...")
    print("Type 'quit' when you're done.")
    print("=" * 55)
    
    # Create forum
    config = ForumConfig(
        forum_id="your_chat",
        name="Your Personal Philosophy Session",
        description="Private dialogue with Socrates",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(config)
    current_state = None
    
    print("\n🏛️ Socrates: Greetings, my friend! I am here to explore wisdom with you.")
    print("          What weighs upon your mind today?")
    
    while True:
        print("\n" + "-" * 50)
        try:
            # Get user input
            user_input = input("\n🧑 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🏛️ Socrates: Farewell, my friend! Remember - the unexamined life")
                print("          is not worth living. Continue to question everything!")
                break
            
            # Process with Socrates
            if current_state is None:
                current_state = forum.start_conversation(user_input)
            else:
                current_state = forum.continue_conversation(current_state, user_input)
            
            # Get Socrates' response
            agent_messages = [msg for msg in current_state["messages"] 
                             if msg["message_type"].value == "agent"]
            
            if agent_messages:
                latest = agent_messages[-1]
                
                print(f"\n🏛️ Socrates:")
                if latest.get("thinking"):
                    print(f"          💭 (thinking: {latest['thinking']})")
                print(f"          {latest['content']}")
                
                # Show activation level for fun
                activation = current_state.get("agent_activations", {}).get("socrates", 0)
                if activation > 0.7:
                    print(f"          [Socrates is very engaged! 🔥 {activation:.2f}]")
                elif activation > 0.5:
                    print(f"          [Socrates is interested 🤔 {activation:.2f}]")
            else:
                print("\n🏛️ Socrates: *contemplates in thoughtful silence*")
                
        except KeyboardInterrupt:
            print("\n\n🏛️ Socrates: Until we meet again in the realm of ideas...")
            break
        except EOFError:
            print("\n\n🏛️ Socrates: The dialogue continues in your mind, my friend.")
            break
        except Exception as e:
            print(f"\n⚠️  Something went awry: {e}")
            print("🏛️ Socrates: Even in confusion, we find opportunities to question!")
    
    # Show final summary
    if current_state:
        total_exchanges = len([msg for msg in current_state["messages"] 
                              if msg["sender"] == "human"])
        topic = current_state.get("current_topic", "philosophy")
        
        print(f"\n📊 Session Summary:")
        print(f"    • Topic explored: {topic}")
        print(f"    • Questions you asked: {total_exchanges}")
        print(f"    • Socratic responses: {len(agent_messages)}")
        
    print("\n✨ Thank you for this philosophical journey!")

if __name__ == "__main__":
    your_chat()