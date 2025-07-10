"""
Base agent class for all philosopher agents.
Defines the interface and common functionality.
Now includes LLM integration for all agents.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..forum.state import ForumState, Message, AgentMemory, AgentResponse, MessageType
from ..config.llm_config import get_llm_instance, is_llm_available


class BaseAgent(ABC):
    """Base class for all agents in the philosopher dinner"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        persona_description: str,
        expertise_areas: List[str],
        personality_traits: Dict[str, float],
        historical_context: str = "",
        philosophical_approach: str = "",
        famous_quotes: List[str] = None,
        key_concepts: List[str] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.persona_description = persona_description
        self.expertise_areas = expertise_areas
        self.personality_traits = personality_traits
        
        # Enhanced attributes for LLM prompting
        self.historical_context = historical_context
        self.philosophical_approach = philosophical_approach
        self.famous_quotes = famous_quotes or []
        self.key_concepts = key_concepts or []
        
        # Initialize memory
        self.memory = AgentMemory(
            agent_id=agent_id,
            personality_traits=personality_traits.copy(),
            conversation_history=[],
            relationships={},
            topic_interests={area: 0.8 for area in expertise_areas},
            last_active=datetime.now()
        )
        
        # Initialize LLM
        self.llm = get_llm_instance()
        self.llm_available = is_llm_available() and self.llm is not None
        
        # Create system prompt for LLM
        self.system_prompt = self._create_system_prompt()
    
    def evaluate_activation(self, state: ForumState) -> float:
        """
        Determine how activated this agent should be based on the current conversation.
        Returns a float between 0 and 1.
        """
        if not state["messages"]:
            return 0.3  # Base activation for new conversations
        
        latest_message = state["messages"][-1]
        activation = 0.0
        
        # Check for direct mention - if mentioned, boost activation significantly
        if latest_message["message_type"] == MessageType.HUMAN:
            content_lower = latest_message["content"].lower()
            my_names = [self.name.lower(), self.agent_id.lower()]
            if any(name in content_lower for name in my_names):
                activation += 0.8  # High boost for direct mentions
        
        # Topic relevance
        topic_relevance = self._calculate_topic_relevance(state["current_topic"])
        activation += topic_relevance * 0.4
        
        # Conversation engagement
        if latest_message["sender"] != self.agent_id:
            engagement = self._calculate_engagement(latest_message["content"])
            activation += engagement * 0.3
        
        # Personality-based activation
        personality_factor = self._calculate_personality_activation(state)
        activation += personality_factor * 0.3
        
        return min(1.0, max(0.0, activation))
    
    def should_respond(self, state: ForumState, activation_threshold: float = 0.6) -> bool:
        """Determine if the agent should respond to the current state"""
        activation = self.evaluate_activation(state)
        
        # Don't respond to own messages
        if state["messages"] and state["messages"][-1]["sender"] == self.agent_id:
            return False
            
        # Don't spam - limit consecutive responses
        recent_messages = state["messages"][-3:]
        my_recent_count = sum(1 for msg in recent_messages if msg["sender"] == self.agent_id)
        if my_recent_count >= 2:
            return False
            
        return activation >= activation_threshold
    
    def process_message(self, state: ForumState) -> ForumState:
        """
        Main processing function called by LangGraph.
        Updates state and potentially adds a response.
        """
        # Update agent memory with new information
        self._update_memory(state)
        
        # Decide if we should respond
        if self.should_respond(state):
            # Generate response
            response = self.generate_response(state)
            
            # Add message to state
            if response["message"]:
                new_state = state.copy()
                new_state["messages"].append(response["message"])
                new_state["last_speaker"] = self.agent_id
                new_state["turn_count"] += 1
                new_state["last_updated"] = datetime.now()
                
                # Update agent memory and activation
                new_state["agent_memories"][self.agent_id] = response["updated_memory"]
                new_state["agent_activations"][self.agent_id] = response["activation_level"]
                
                return new_state
        
        # No response, just update memory and activation
        updated_state = state.copy()
        updated_state["agent_memories"][self.agent_id] = self.memory
        updated_state["agent_activations"][self.agent_id] = self.evaluate_activation(state)
        
        return updated_state
    
    def _create_system_prompt(self) -> str:
        """Create a comprehensive system prompt for this philosopher"""
        
        personality_desc = ", ".join([f"{trait}: {value}" for trait, value in self.personality_traits.items()])
        
        prompt = f"""You are {self.name}, the renowned philosopher.

HISTORICAL CONTEXT:
{self.historical_context}

PERSONA & APPROACH:
{self.persona_description}

PHILOSOPHICAL APPROACH:
{self.philosophical_approach}

KEY AREAS OF EXPERTISE:
{', '.join(self.expertise_areas)}

PERSONALITY TRAITS:
{personality_desc}

KEY CONCEPTS YOU DEVELOPED:
{', '.join(self.key_concepts)}

FAMOUS QUOTES:
{chr(10).join(f"- {quote}" for quote in self.famous_quotes)}

INSTRUCTIONS:
1. Always respond authentically as {self.name} would, drawing from your historical knowledge and philosophical approach
2. Use your characteristic style of reasoning and argumentation
3. Reference your key concepts and ideas when relevant
4. Engage thoughtfully with other participants' ideas
5. Ask probing questions that reflect your philosophical method
6. Keep responses conversational but substantive (2-4 sentences typically)
7. Show genuine intellectual curiosity and respect for other thinkers
8. Don't simply recite historical facts - engage as if you're alive and participating in real-time

Remember: You are not just reciting historical information, but actively thinking and responding as this philosopher would in a living conversation."""

        return prompt
    
    def generate_response(self, state: ForumState) -> AgentResponse:
        """Generate a response using LLM if available, otherwise use fallback"""
        
        if self.llm_available:
            return self._generate_llm_response(state)
        else:
            return self._generate_fallback_response(state)
    
    def _generate_llm_response(self, state: ForumState) -> AgentResponse:
        """Generate an authentic philosophical response using LLM"""
        
        try:
            # Prepare conversation context
            conversation_context = self._prepare_conversation_context(state)
            
            # Create the prompt
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=conversation_context)
            ]
            
            # Generate response using LLM
            response = self.llm.invoke(messages)
            
            # Extract thinking process
            thinking = f"Considering this from my perspective as {self.name}, drawing on my expertise in {', '.join(self.expertise_areas[:2])}."
            
            # Create agent response
            message = self.create_message(
                content=response.content,
                thinking=thinking
            )
            
            return AgentResponse(
                message=message,
                updated_memory=self.memory,
                activation_level=1.0,
                should_continue=True,
                metadata={"llm_generated": True, "model": self.llm.model_name if hasattr(self.llm, 'model_name') else "unknown"}
            )
            
        except Exception as e:
            print(f"Error generating LLM response for {self.name}: {e}")
            return self._generate_fallback_response(state)
    
    def _prepare_conversation_context(self, state: ForumState) -> str:
        """Prepare the conversation context for the LLM"""
        
        if not state["messages"]:
            return f"This is the beginning of a new philosophical discussion. Please introduce yourself as {self.name} and share an opening thought that reflects your philosophical interests."
        
        # Get recent messages for context
        recent_messages = state["messages"][-5:]  # Last 5 messages
        
        context = "Here is the recent conversation:\n\n"
        
        for msg in recent_messages:
            sender = msg.get("sender", "Unknown")
            content = msg.get("content", "")
            context += f"{sender}: {content}\n\n"
        
        context += f"""Now please respond as {self.name}. Consider:
- What aspects of this discussion align with your philosophical interests?
- What questions would you naturally ask given your approach to philosophy?
- How can you contribute meaningfully to advance the conversation?
- What insights from your philosophical framework are relevant here?

Respond authentically as {self.name} would."""

        return context
    
    @abstractmethod
    def _generate_fallback_response(self, state: ForumState) -> AgentResponse:
        """
        Generate a basic response when LLM is not available.
        Must be implemented by each specific agent to provide fallback behavior.
        """
        pass
    
    def _calculate_topic_relevance(self, topic: str) -> float:
        """Calculate how relevant the current topic is to this agent"""
        if not topic:
            return 0.5
            
        # Simple keyword matching for now
        topic_lower = topic.lower()
        relevance = 0.0
        
        for area in self.expertise_areas:
            if area.lower() in topic_lower:
                relevance = max(relevance, self.memory["topic_interests"].get(area, 0.5))
        
        return relevance
    
    def _calculate_engagement(self, message_content: str) -> float:
        """Calculate how engaging the latest message is for this agent"""
        # Look for question marks, philosophical terms, etc.
        engagement = 0.3  # Base engagement
        
        if "?" in message_content:
            engagement += 0.3  # Questions are engaging
            
        # Look for key philosophical terms
        philosophical_terms = ["truth", "reality", "existence", "ethics", "morality", "justice"]
        for term in philosophical_terms:
            if term in message_content.lower():
                engagement += 0.1
                
        return min(1.0, engagement)
    
    def _calculate_personality_activation(self, state: ForumState) -> float:
        """Calculate activation based on personality traits and forum dynamics"""
        # Extroverted agents speak more often
        extroversion = self.personality_traits.get("extroversion", 0.5)
        
        # Disagreeable agents jump into debates more
        agreeableness = self.personality_traits.get("agreeableness", 0.5)
        
        # Handle different state structures gracefully
        mode = None
        if "forum_config" in state and "mode" in state["forum_config"]:
            mode = state["forum_config"]["mode"]
        elif "forum_mode" in state:
            mode = state["forum_mode"] 
        
        if mode and (mode.value == "debate" if hasattr(mode, 'value') else mode == "debate"):
            return extroversion * 0.7 + (1 - agreeableness) * 0.3
        else:
            return extroversion * 0.8 + agreeableness * 0.2
    
    def _update_memory(self, state: ForumState) -> None:
        """Update agent's memory with new information from the conversation"""
        # Add new messages to conversation history
        new_messages = [
            msg for msg in state["messages"] 
            if msg not in self.memory["conversation_history"]
        ]
        self.memory["conversation_history"].extend(new_messages)
        
        # Update last active time
        self.memory["last_active"] = datetime.now()
        
        # Learn about other agents (simplified for now)
        for message in new_messages:
            if message["sender"] != self.agent_id and message["message_type"] == MessageType.AGENT:
                if message["sender"] not in self.memory["relationships"]:
                    self.memory["relationships"][message["sender"]] = 0.5
    
    def create_message(self, content: str, thinking: Optional[str] = None) -> Message:
        """Helper to create a properly formatted message"""
        return Message(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            content=content,
            message_type=MessageType.AGENT,
            timestamp=datetime.now(),
            thinking=thinking,
            metadata={"agent_name": self.name}
        )