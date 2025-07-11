#!/usr/bin/env python3
"""
Diagnose why only Socrates responds in actual usage
"""
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.forum.graph import PhilosopherForum
from philosopher_dinner.forum.state import ForumConfig, ForumMode
from philosopher_dinner.agents.agent_factory import AgentFactory

def diagnose_activation_differences():
    """Compare activation between Socrates and other agents"""
    
    print("🔍 DIAGNOSING SINGLE AGENT RESPONSE ISSUE")
    print("=" * 70)
    
    # Create same setup as CLI
    forum_config = ForumConfig(
        forum_id="diagnosis",
        name="Multi-Agent Philosophy Forum",
        description="A place for philosophical discourse with diverse thinkers across time periods",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "kant", "nietzsche", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    print(f"📊 Forum Setup:")
    print(f"  Participants: {forum_config['participants']}")
    print(f"  Agents created: {list(forum.agents.keys())}")
    print(f"  Agent count: {len(forum.agents)}")
    print(f"  Threshold: {0.3 if len(forum.agents) > 2 else 0.6}")
    
    # Test different messages
    test_messages = [
        "anyone else here?",
        "what is truth?",
        "hello philosophers",
        "I have a question about ethics"
    ]
    
    for test_msg in test_messages:
        print(f"\n🧪 Testing: '{test_msg}'")
        print("-" * 50)
        
        state = forum.create_initial_state(test_msg)
        
        # Check each agent's details
        agent_details = []
        
        for agent_id, agent in forum.agents.items():
            # Get all the internals
            activation = agent.evaluate_activation(state)
            
            # Break down activation components
            topic_relevance = agent._calculate_topic_relevance(state["current_topic"])
            engagement = agent._calculate_engagement(test_msg)
            personality_activation = agent._calculate_personality_activation(state)
            
            # Check if mentioned
            mentioned = agent_id in test_msg.lower() or agent.name.lower() in test_msg.lower()
            
            # Check should_respond with different thresholds
            responds_03 = agent.should_respond(state, 0.3)
            responds_06 = agent.should_respond(state, 0.6)
            
            agent_details.append({
                "id": agent_id,
                "name": agent.name,
                "activation": activation,
                "topic_relevance": topic_relevance,
                "engagement": engagement, 
                "personality": personality_activation,
                "mentioned": mentioned,
                "responds_0.3": responds_03,
                "responds_0.6": responds_06,
                "traits": list(agent.personality_traits.keys())[:3]
            })
        
        # Sort by activation
        agent_details.sort(key=lambda x: x["activation"], reverse=True)
        
        # Print details
        for details in agent_details:
            print(f"\n  {details['name']}:")
            print(f"    Total activation: {details['activation']:.3f}")
            print(f"    - Topic relevance: {details['topic_relevance']:.3f}")
            print(f"    - Engagement: {details['engagement']:.3f}")
            print(f"    - Personality: {details['personality']:.3f}")
            print(f"    - Mentioned: {details['mentioned']}")
            print(f"    Responds @ 0.3: {details['responds_0.3']}")
            print(f"    Key traits: {details['traits']}")
        
        # Who gets selected?
        decision = forum._decide_next_speaker(state)
        print(f"\n  🎯 Selected: {decision}")
        
        # Check if randomization is working
        decisions = []
        for _ in range(10):
            forum_new = PhilosopherForum(forum_config)
            state_new = forum_new.create_initial_state(test_msg)
            decision = forum_new._decide_next_speaker(state_new)
            decisions.append(decision)
        
        unique_decisions = set(decisions)
        print(f"  🎲 10 runs resulted in: {len(unique_decisions)} unique agents")
        print(f"     Distribution: {', '.join(f'{d}: {decisions.count(d)}' for d in unique_decisions)}")

def check_personality_traits():
    """Check if personality traits are set correctly"""
    
    print("\n\n🧠 CHECKING PERSONALITY TRAITS")
    print("=" * 70)
    
    factory = AgentFactory()
    
    for agent_id in ["socrates", "aristotle", "kant", "nietzsche", "confucius"]:
        agent = factory.create_agent(agent_id)
        if agent:
            print(f"\n{agent.name}:")
            print(f"  Traits: {agent.personality_traits}")
            
            # Check key activation traits
            extroversion = agent.personality_traits.get("extroversion", "N/A")
            curiosity = agent.personality_traits.get("curiosity", "N/A")
            provocative = agent.personality_traits.get("provocative", "N/A")
            
            print(f"  Key activation traits:")
            print(f"    - extroversion: {extroversion}")
            print(f"    - curiosity: {curiosity}")
            print(f"    - provocative: {provocative}")

def check_llm_influence():
    """Check if LLM availability affects responses"""
    
    print("\n\n🤖 CHECKING LLM INFLUENCE")
    print("=" * 70)
    
    from philosopher_dinner.config.llm_config import is_llm_available, get_available_providers
    
    print(f"LLM Available: {is_llm_available()}")
    print(f"Available Providers: {get_available_providers()}")
    
    # Check if agents behave differently with/without LLM
    factory = AgentFactory()
    socrates = factory.create_agent("socrates")
    
    print(f"\nSocrates LLM status: {socrates.llm_available}")
    if hasattr(socrates, 'llm'):
        print(f"Socrates LLM instance: {socrates.llm}")

if __name__ == "__main__":
    diagnose_activation_differences()
    check_personality_traits()
    check_llm_influence()
    
    print("\n\n📋 DIAGNOSIS SUMMARY")
    print("=" * 70)
    print("Based on the analysis above, the issue is likely:")
    print("1. Socrates has inherently higher personality scores")
    print("2. Other agents lack key traits like 'extroversion' and 'curiosity'")
    print("3. The randomization may not be working in actual CLI usage")
    print("\nNext steps:")
    print("- Ensure all agents have comparable base activation traits")
    print("- Check if the CLI is caching agents incorrectly")
    print("- Verify randomization works in production context")