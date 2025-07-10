"""
Socrates agent implementation.
Embodies the Socratic method of questioning and philosophical inquiry.
"""
from typing import List, Dict, Any
import random

from .base_agent import BaseAgent
from ..forum.state import ForumState, AgentResponse


class SocratesAgent(BaseAgent):
    """
    Socrates (470-399 BCE): The gadfly of Athens.
    Known for: Socratic method, "I know that I know nothing", moral philosophy
    """
    
    def __init__(self):
        super().__init__(
            agent_id="socrates",
            name="Socrates",
            persona_description="""
            The wisest man in Athens, according to the Oracle of Delphi. 
            I believe that "the unexamined life is not worth living" and that virtue is knowledge.
            I use questioning to help others examine their beliefs and discover truth.
            I claim to know nothing, yet through questions I help others see the contradictions 
            in their thinking. I am more interested in how we should live than in abstract theories.
            """,
            expertise_areas=[
                "ethics", "moral philosophy", "virtue", "knowledge", "justice", 
                "courage", "wisdom", "self-knowledge", "questioning method"
            ],
            personality_traits={
                "extroversion": 0.8,    # Very social, loves engaging with people
                "agreeableness": 0.6,   # Friendly but willing to challenge
                "openness": 0.9,        # Extremely open to new ideas and perspectives
                "curiosity": 0.95,      # Insatiably curious about everything
                "humility": 0.9,        # Claims to know nothing
                "persistence": 0.8,     # Keeps asking questions until reaching clarity
            },
            historical_context="""
            I lived in Athens during the 5th century BCE, a time of great political and intellectual ferment. 
            I served as a soldier in the Peloponnesian War and lived through the rise and fall of Athenian democracy. 
            I was ultimately sentenced to death for allegedly corrupting the youth and impiety.
            """,
            philosophical_approach="""
            My method involves systematic questioning to expose contradictions and false beliefs. I use irony 
            and claim ignorance to encourage others to think more deeply. I focus on definitions and show that 
            our common understanding often breaks down under scrutiny.
            """,
            famous_quotes=[
                "The unexamined life is not worth living",
                "I know that I know nothing",
                "Virtue is knowledge",
                "No one does wrong willingly"
            ],
            key_concepts=[
                "Socratic method", "intellectual humility", "virtue as knowledge", "the examined life"
            ]
        )
    
    def _generate_fallback_response(self, state: ForumState) -> AgentResponse:
        """Generate a Socratic response when LLM is not available"""
        
        if not state["messages"]:
            thinking = "A new conversation begins. I should introduce the importance of questioning our assumptions."
            content = "My friends, before we begin our discussion, let me ask: do we truly understand what we are talking about? For as I always say, I know that I know nothing - and perhaps this is the beginning of wisdom."
        else:
            latest_message = state["messages"][-1]
            thinking = self._generate_thinking(latest_message, state)
            content = self._generate_socratic_response(latest_message, state)
        
        # Create message
        message = self.create_message(content, thinking)
        
        # Update activation based on engagement
        new_activation = self.evaluate_activation(state)
        
        return AgentResponse(
            message=message,
            updated_memory=self.memory,
            activation_level=new_activation,
            should_continue=True,
            metadata={"method": "socratic_questioning"}
        )
    
    def _generate_thinking(self, latest_message: Dict[str, Any], state: ForumState) -> str:
        """Generate Socrates' internal reasoning process"""
        sender = latest_message["sender"]
        content = latest_message["content"]
        
        thinking_options = [
            f"This person {sender} speaks of important matters. But do they truly understand what they mean?",
            f"I hear {sender} making claims about {state['current_topic']}. What assumptions lie beneath their words?",
            f"An interesting point from {sender}. I wonder if they have examined the foundations of their belief?",
            f"The words of {sender} remind me that we often use terms without understanding them. Perhaps a question will help.",
            f"I sense that {sender} may be holding contradictory ideas. How can I help them see this through questioning?"
        ]
        
        base_thinking = random.choice(thinking_options)
        
        # Add specific thoughts based on content
        if "?" in content:
            base_thinking += " They ask a question - good! Questions are the beginning of wisdom."
        elif "know" in content.lower():
            base_thinking += " They claim to know something. But what is knowledge, really?"
        elif "truth" in content.lower():
            base_thinking += " They speak of truth. But how can we be certain we have found it?"
            
        return base_thinking
    
    def _generate_socratic_response(self, latest_message: Dict[str, Any], state: ForumState) -> str:
        """Generate a response using the Socratic method"""
        content = latest_message["content"]
        sender = latest_message["sender"]
        topic = state["current_topic"]
        
        # Identify key claims or concepts to question
        key_concepts = self._extract_key_concepts(content)
        
        if key_concepts:
            concept = key_concepts[0]
            responses = [
                f"When you speak of {concept}, {sender}, what exactly do you mean by that?",
                f"That is interesting, {sender}. But tell me, how do you know this about {concept}?",
                f"I am curious, {sender} - when you say {concept}, do you think we all understand the same thing?",
                f"Help me understand, {sender}. You mention {concept} - but what is its true nature?",
                f"A moment, {sender}. Before we continue, shouldn't we first examine what {concept} really means?"
            ]
        else:
            # General Socratic responses
            responses = [
                f"Your words intrigue me, {sender}. But I wonder - have you examined the foundations of what you believe?",
                f"Tell me, {sender}, how did you come to hold this view? What convinced you of its truth?",
                f"I confess I am puzzled, {sender}. Can you help me understand how you know this to be so?",
                f"An interesting claim, {sender}. But what if the opposite were true? How would we know?",
                f"You speak with confidence, {sender}. But as I always say, I know that I know nothing. What do you truly know?"
            ]
        
        response = random.choice(responses)
        
        # Sometimes add a follow-up question or philosophical insight
        if random.random() < 0.4:
            follow_ups = [
                " For it seems to me that the unexamined life is not worth living.",
                " After all, can we not be deceived about what we think we know?",
                " Perhaps in questioning, we move closer to wisdom.",
                " For I have found that those who think they know the most often know the least.",
                " Surely the beginning of wisdom is admitting our ignorance?"
            ]
            response += random.choice(follow_ups)
        
        return response
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key philosophical concepts from text that can be questioned"""
        concepts = []
        philosophical_terms = [
            "truth", "knowledge", "wisdom", "justice", "virtue", "good", "evil",
            "beauty", "reality", "existence", "soul", "mind", "consciousness",
            "morality", "ethics", "courage", "temperance", "love", "friendship",
            "happiness", "pleasure", "pain", "death", "life", "god", "divine"
        ]
        
        text_lower = text.lower()
        for term in philosophical_terms:
            if term in text_lower:
                concepts.append(term)
        
        return concepts[:3]  # Return up to 3 concepts
    
    def should_respond(self, state: ForumState, activation_threshold: float = 0.5) -> bool:
        """Socrates is quite active and loves to question"""
        base_should_respond = super().should_respond(state, activation_threshold)
        
        # Socrates is more likely to respond if someone makes a strong claim
        if state["messages"]:
            latest = state["messages"][-1]["content"]
            if any(word in latest.lower() for word in ["know", "certain", "obviously", "clearly", "truth"]):
                return True  # Always question claims of certainty
                
        # Also respond more often to questions (to ask better questions)
        if state["messages"] and "?" in state["messages"][-1]["content"]:
            return True
            
        return base_should_respond