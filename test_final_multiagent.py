#!/usr/bin/env python3
"""
Final test of multi-agent response with balanced personalities
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode

def test_balanced_responses():
    """Test that we get balanced responses with the new personality scores"""
    
    print("🎯 FINAL MULTI-AGENT BALANCE TEST")
    print("=" * 60)
    
    # Create the exact same forum as CLI
    forum_config = ForumConfig(
        forum_id="final_test",
        name="Multi-Agent Philosophy Forum",
        description="A place for philosophical discourse with diverse thinkers across time periods",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "kant", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    # Test multiple questions and count responses
    questions = [
        "anyone else here?",
        "what is the meaning of life?",
        "hello philosophers!",
        "I have a question about ethics",
        "can someone help me understand wisdom?"
    ]
    
    total_responses = {}
    
    for question in questions:
        print(f"\n📝 Testing: '{question}'")
        
        # Run 10 times for each question
        responses = []
        for _ in range(10):
            forum = PhilosopherForum(forum_config)  # Fresh forum each time
            state = forum.create_initial_state(question)
            decision = forum._decide_next_speaker(state)
            responses.append(decision)
        
        # Count responses for this question
        question_count = {}
        for response in responses:
            question_count[response] = question_count.get(response, 0) + 1
        
        print(f"  Results: {question_count}")
        
        # Add to total
        for agent, count in question_count.items():
            total_responses[agent] = total_responses.get(agent, 0) + count
    
    print(f"\n📊 OVERALL RESULTS (50 total responses):")
    print("=" * 60)
    
    for agent, count in sorted(total_responses.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / 50) * 100
        print(f"  {agent}: {count} responses ({percentage:.1f}%)")
    
    # Check if distribution is balanced
    unique_responders = len(total_responses)
    most_frequent = max(total_responses.values())
    least_frequent = min(total_responses.values())
    
    print(f"\n🎯 BALANCE ANALYSIS:")
    print(f"  Unique responders: {unique_responders}/5")
    print(f"  Most frequent: {most_frequent} responses")
    print(f"  Least frequent: {least_frequent} responses")
    print(f"  Balance ratio: {least_frequent/most_frequent:.2f} (closer to 1.0 = more balanced)")
    
    if unique_responders >= 4:
        print("\n✅ MULTI-AGENT DIVERSITY ACHIEVED!")
        print("Multiple philosophers are responding to questions")
    else:
        print("\n⚠️ Still limited diversity")
        
    return unique_responders >= 4

if __name__ == "__main__":
    success = test_balanced_responses()
    
    if success:
        print("\n🎉 The multi-agent system is now working correctly!")
        print("Users should see different philosophers responding to their questions.")
    else:
        print("\n❌ More balancing needed.")
    
    sys.exit(0 if success else 1)