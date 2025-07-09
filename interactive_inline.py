#!/usr/bin/env python3
"""
Inline interactive version of Philosopher Dinner.
Simulates interactive conversation within this session.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

class InlinePhilosopherChat:
    """Interactive chat that can be run inline"""
    
    def __init__(self):
        # Create forum config
        config = ForumConfig(
            forum_id="inline_forum",
            name="Inline Philosophy Forum",
            description="Interactive chat session",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            settings={}
        )
        
        # Create the forum
        self.forum = PhilosopherForum(config)
        self.current_state = None
        
        print("🏛️ PHILOSOPHER DINNER - INLINE CHAT")
        print("=" * 50)
        print("Welcome! You're now chatting with Socrates.")
        print("Type your philosophical questions and see his responses!")
        print("=" * 50)
    
    def chat(self, human_message: str) -> str:
        """Send a message and get response"""
        
        print(f"\n🧑 You: {human_message}")
        
        if self.current_state is None:
            # Start new conversation
            self.current_state = self.forum.start_conversation(human_message)
        else:
            # Continue conversation
            self.current_state = self.forum.continue_conversation(self.current_state, human_message)
        
        # Get the latest agent response
        agent_messages = [msg for msg in self.current_state["messages"] 
                         if msg["message_type"].value == "agent"]
        
        if agent_messages:
            latest_response = agent_messages[-1]
            
            print(f"\n🏛️ Socrates:")
            if latest_response.get("thinking"):
                print(f"   💭 (thinking: {latest_response['thinking']})")
            print(f"   {latest_response['content']}")
            
            return latest_response['content']
        
        return "Socrates seems to be pondering in silence..."
    
    def show_conversation_summary(self):
        """Show summary of the conversation"""
        if self.current_state:
            total_messages = len(self.current_state["messages"])
            topic = self.current_state["current_topic"]
            turn_count = self.current_state["turn_count"]
            
            print(f"\n📊 Conversation Summary:")
            print(f"   Topic: {topic}")
            print(f"   Messages: {total_messages}")
            print(f"   Turns: {turn_count}")
            
            # Show Socrates' activation
            if "socrates" in self.current_state.get("agent_activations", {}):
                activation = self.current_state["agent_activations"]["socrates"]
                print(f"   Socrates activation: {activation:.2f}")

def run_interactive_demo():
    """Run a predefined interactive demo"""
    
    chat = InlinePhilosopherChat()
    
    # Demo conversation 1
    response1 = chat.chat("What is wisdom?")
    
    # Demo conversation 2  
    response2 = chat.chat("I think wisdom is knowing many facts.")
    
    # Demo conversation 3
    response3 = chat.chat("But how can I be certain that what I know is true?")
    
    # Show summary
    chat.show_conversation_summary()
    
    print("\n" + "=" * 50)
    print("🎯 DEMO COMPLETE!")
    print("\nYou can see how Socrates:")
    print("• Responds to each question with deeper questions")
    print("• Challenges assumptions about knowledge and wisdom")  
    print("• Uses his signature questioning method")
    print("• Maintains consistent philosophical character")
    
    return chat

def create_custom_chat():
    """Create a chat instance for custom interactions"""
    return InlinePhilosopherChat()

if __name__ == "__main__":
    # Run the demo
    demo_chat = run_interactive_demo()
    
    print("\n" + "=" * 50)
    print("🔧 INLINE USAGE:")
    print("To continue chatting, use:")
    print("demo_chat.chat('Your question here')")
    print("\nOr create a new chat:")
    print("my_chat = create_custom_chat()")
    print("my_chat.chat('Hello Socrates!')")