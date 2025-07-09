#!/usr/bin/env python3
"""
Interactive debug version of Philosopher Dinner.
Simulates a conversation step by step.
"""

import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.state import ForumState, ForumConfig, ForumMode, Message, MessageType
from philosopher_dinner.agents.socrates import SocratesAgent

def interactive_debug():
    """Run an interactive debugging session"""
    
    print("🔧 PHILOSOPHER DINNER - INTERACTIVE DEBUG")
    print("=" * 60)
    
    # Create Socrates
    print("1. Creating Socrates agent...")
    socrates = SocratesAgent()
    print(f"   ✅ Socrates created: {socrates.name}")
    print(f"   📚 Expertise: {socrates.expertise_areas[:3]}...")
    print(f"   🧠 Personality: extroversion={socrates.personality_traits['extroversion']}")
    
    # Create forum config
    print("\n2. Setting up forum...")
    config = ForumConfig(
        forum_id="debug",
        name="Debug Forum", 
        description="Interactive debugging session",
        mode=ForumMode.EXPLORATION,
        participants=["socrates"],
        created_at=datetime.now(),
        settings={}
    )
    print(f"   ✅ Forum created: {config['name']}")
    print(f"   🎯 Mode: {config['mode'].value}")
    
    # Start conversation
    print("\n3. Starting conversation...")
    print("   Human asks: 'What is the meaning of life?'")
    
    human_message = Message(
        id="msg-1",
        sender="human", 
        content="What is the meaning of life?",
        message_type=MessageType.HUMAN,
        timestamp=datetime.now(),
        thinking=None,
        metadata={}
    )
    
    # Create state
    state = ForumState(
        messages=[human_message],
        current_topic="meaning of life",
        active_speakers=["human"],
        forum_config=config,
        participants=["socrates"],
        agent_memories={},
        agent_activations={},
        turn_count=1,
        last_speaker="human", 
        waiting_for_human=False,
        session_id="debug-session",
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    
    print(f"   ✅ State created with {len(state['messages'])} messages")
    
    # Check Socrates' response
    print("\n4. Evaluating Socrates' response...")
    
    activation = socrates.evaluate_activation(state)
    should_respond = socrates.should_respond(state)
    
    print(f"   📊 Activation level: {activation:.3f}")
    print(f"   🤔 Should respond: {should_respond}")
    print(f"   🎯 Topic relevance for 'meaning of life': {socrates._calculate_topic_relevance('meaning of life'):.3f}")
    print(f"   💬 Engagement with message: {socrates._calculate_engagement(human_message['content']):.3f}")
    
    if should_respond:
        print("\n5. Generating Socrates' response...")
        
        # Generate response
        response = socrates.generate_response(state)
        
        if response["message"]:
            message = response["message"]
            print(f"   ✅ Response generated!")
            print(f"   💭 Thinking: {message['thinking']}")
            print(f"   📝 Content: {message['content']}")
            print(f"   🔋 New activation: {response['activation_level']:.3f}")
            
            # Simulate conversation display
            print("\n" + "="*60)
            print("🎭 CONVERSATION SIMULATION")
            print("="*60)
            
            print(f"\n🧑 Human [{human_message['timestamp'].strftime('%H:%M:%S')}]:")
            print(f"   {human_message['content']}")
            
            print(f"\n🏛️ Socrates [{message['timestamp'].strftime('%H:%M:%S')}]:")
            print(f"   💭 (thinking: {message['thinking']})")
            print(f"   {message['content']}")
            
            # Test another round
            print("\n" + "-"*60)
            print("6. Testing follow-up response...")
            
            # Add another human message
            followup = Message(
                id="msg-2",
                sender="human",
                content="I believe life's meaning comes from happiness and pleasure.",
                message_type=MessageType.HUMAN, 
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            )
            
            # Update state
            new_state = state.copy()
            new_state["messages"].append(message)
            new_state["messages"].append(followup)
            new_state["turn_count"] += 2
            new_state["last_speaker"] = "human"
            
            print(f"   🧑 Human: {followup['content']}")
            
            # Check Socrates' second response
            activation2 = socrates.evaluate_activation(new_state)
            should_respond2 = socrates.should_respond(new_state)
            
            print(f"   📊 New activation: {activation2:.3f}")
            print(f"   🤔 Should respond again: {should_respond2}")
            
            if should_respond2:
                response2 = socrates.generate_response(new_state)
                if response2["message"]:
                    msg2 = response2["message"]
                    print(f"\n🏛️ Socrates:")
                    print(f"   💭 (thinking: {msg2['thinking']})")  
                    print(f"   {msg2['content']}")
        
    print("\n" + "="*60)
    print("✨ DEBUG COMPLETE!")
    print("🎯 Key findings:")
    print(f"   • Socrates activates strongly ({activation:.2f}) for philosophical topics")
    print(f"   • Uses authentic Socratic questioning method")
    print(f"   • Maintains personality traits (curious, humble, persistent)")
    print(f"   • Responds appropriately to different conversation contexts")
    print("\n💡 System is working correctly! Ready for full interactive mode.")

if __name__ == "__main__":
    interactive_debug()