"""
LLM-powered Base Agent
Enhanced base agent that uses real LLMs to generate philosophical responses.
"""
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from .base_agent import BaseAgent
from ..forum.state import ForumState, AgentResponse
from ..config.llm_config import get_llm_instance, is_llm_available


class LLMAgent(BaseAgent):
    """Base agent class that uses real LLMs for responses"""
    
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
        super().__init__(agent_id, name, persona_description, expertise_areas, personality_traits)
        
        # Enhanced philosopher-specific attributes
        self.historical_context = historical_context
        self.philosophical_approach = philosophical_approach
        self.famous_quotes = famous_quotes or []
        self.key_concepts = key_concepts or []
        
        # Initialize LLM
        self.llm = get_llm_instance()
        self.llm_available = is_llm_available() and self.llm is not None
        
        # Create the system prompt template
        self.system_prompt = self._create_system_prompt()
        
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
        """Generate an authentic philosophical response using LLM"""
        
        if not self.llm_available:
            # Fallback to basic response if LLM not available
            return self._generate_fallback_response(state)
        
        try:
            # Prepare conversation context
            conversation_context = self._prepare_conversation_context(state)
            
            # Create the prompt
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=conversation_context)
            ]
            
            # Generate response using LLM
            response = self.llm.invoke(messages)
            
            # Extract thinking process (can be enhanced later)
            thinking = f"Considering this from my perspective as {self.name}, drawing on my expertise in {', '.join(self.expertise_areas[:2])}."
            
            # Create agent response
            message = self.create_message(
                content=response.content,
                thinking=thinking
            )
            
            return AgentResponse(
                message=message,
                updated_memory=self.memory,
                activation_level=1.0,  # High activation when using LLM
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
    
    def _generate_fallback_response(self, state: ForumState) -> AgentResponse:
        """Generate a basic response when LLM is not available"""
        
        if not state["messages"]:
            content = f"I am {self.name}. My approach to philosophy emphasizes {', '.join(self.expertise_areas[:2])}. I'm eager to explore these ideas with you."
        else:
            content = f"As {self.name}, I find this discussion intriguing. Let me consider this from the perspective of my work in {self.expertise_areas[0]}..."
        
        thinking = f"Fallback response generated for {self.name} (LLM not available)"
        
        message = self.create_message(content=content, thinking=thinking)
        
        return AgentResponse(
            message=message,
            updated_memory=self.memory,
            activation_level=0.5,  # Lower activation for fallback
            should_continue=True,
            metadata={"llm_generated": False, "fallback": True}
        )