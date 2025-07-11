"""
Agent Factory for Dynamic Philosopher Creation
Creates philosopher agents on-demand based on templates and requirements.
"""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from .base_agent import BaseAgent
from .socrates import SocratesAgent
from ..forum.state import ForumState, Message, AgentMemory, AgentResponse, MessageType


class DynamicPhilosopherAgent(BaseAgent):
    """
    Dynamically created philosopher agent based on historical template.
    Automatically uses LLM when available through BaseAgent.
    """
    
    def __init__(
        self,
        agent_id: str,
        template: Dict[str, Any]
    ):
        self.template = template
        
        # Create enhanced persona description
        persona_desc = template.get("persona_description", f"""
        I am {template['name']}, a philosopher from {template['era']}. 
        My philosophical approach is characterized by {template['style']}.
        I am particularly interested in {', '.join(template['expertise'][:3])}.
        """)
        
        super().__init__(
            agent_id=agent_id,
            name=template["name"],
            persona_description=persona_desc,
            expertise_areas=template["expertise"],
            personality_traits=template["personality"],
            historical_context=template.get("background", f"I lived during {template['era']} and developed important ideas in {', '.join(template['expertise'][:2])}."),
            philosophical_approach=template["style"],
            famous_quotes=template.get("quotes", []),
            key_concepts=template["key_ideas"]
        )
        
        # Additional template-specific attributes
        self.era = template["era"]
        self.speaking_style = template["style"]
        self.key_ideas = template["key_ideas"]
        self.famous_quotes = template.get("quotes", [])
        self.background = template.get("background", "")
        self.philosophical_method = template.get("method", "dialogue and reasoning")
    
    def _generate_fallback_response(self, state: ForumState) -> AgentResponse:
        """Generate a fallback response when LLM is not available"""
        
        if not state["messages"]:
            return self._create_empty_response()
        
        latest_message = state["messages"][-1]
        current_topic = state.get("current_topic", "")
        
        # Analyze the conversation context
        context = self._analyze_conversation_context(state)
        
        # Generate thinking process
        thinking = self._generate_thinking(latest_message, context)
        
        # Generate response content
        response_content = self._generate_philosophical_response(latest_message, context, state)
        
        # Create message
        message = self.create_message(
            content=response_content,
            thinking=thinking
        )
        
        # Update memory
        self._update_memory(state)
        
        return AgentResponse(
            message=message,
            updated_memory=self.memory,
            activation_level=self.evaluate_activation(state),
            should_continue=True,
            metadata={
                "philosopher": self.name,
                "era": self.era,
                "method": self.philosophical_method
            }
        )
    
    def _analyze_conversation_context(self, state: ForumState) -> Dict[str, Any]:
        """Analyze the conversation to understand context and themes"""
        messages = state["messages"]
        
        # Extract key themes from recent messages
        recent_content = " ".join([msg["content"] for msg in messages[-5:]])
        
        # Identify relevant expertise areas
        relevant_expertise = []
        for area in self.expertise_areas:
            if any(keyword in recent_content.lower() for keyword in area.split("_")):
                relevant_expertise.append(area)
        
        # Identify questions being asked
        questions = [msg["content"] for msg in messages[-3:] if "?" in msg["content"]]
        
        return {
            "recent_themes": self._extract_themes(recent_content),
            "relevant_expertise": relevant_expertise,
            "questions": questions,
            "conversation_tone": self._assess_tone(messages[-3:]),
            "current_depth": len(messages)
        }
    
    def _generate_thinking(self, latest_message: Message, context: Dict) -> str:
        """Generate the philosopher's internal thinking process"""
        
        thinking_parts = []
        
        # React to the message content
        thinking_parts.append(f"Contemplating {latest_message['sender']}'s point about {self._extract_key_concept(latest_message['content'])}...")
        
        # Connect to own philosophical framework
        if context["relevant_expertise"]:
            expertise = context["relevant_expertise"][0].replace("_", " ")
            thinking_parts.append(f"This relates to my work in {expertise}.")
        
        # Reference key ideas if relevant
        relevant_ideas = [idea for idea in self.key_ideas if any(word in latest_message["content"].lower() for word in idea.lower().split())]
        if relevant_ideas:
            thinking_parts.append(f"This connects to my ideas about {relevant_ideas[0]}.")
        
        # Consider philosophical method
        thinking_parts.append(f"I should approach this through {self.philosophical_method}.")
        
        return " ".join(thinking_parts)
    
    def _generate_philosophical_response(self, latest_message: Message, context: Dict, state: ForumState) -> str:
        """Generate the actual philosophical response"""
        
        response_parts = []
        
        # Opening that reflects the philosopher's style
        response_parts.append(self._generate_opening(latest_message, context))
        
        # Main philosophical content
        response_parts.append(self._generate_main_content(latest_message, context))
        
        # Question or challenge (if appropriate for this philosopher)
        if self._should_ask_question(context):
            response_parts.append(self._generate_question(latest_message, context))
        
        # Historical perspective or personal touch
        response_parts.append(self._add_historical_perspective(context))
        
        return "\n\n".join(filter(None, response_parts))
    
    def _generate_opening(self, latest_message: Message, context: Dict) -> str:
        """Generate an opening that fits the philosopher's style"""
        
        # Different opening styles based on philosopher characteristics
        if "skeptical" in [trait for trait, value in self.personality_traits.items() if value > 0.7]:
            return f"I find myself questioning what {latest_message['sender']} has proposed..."
            
        elif "systematic" in [trait for trait, value in self.personality_traits.items() if value > 0.7]:
            return "Let me approach this systematically..."
            
        elif "provocative" in [trait for trait, value in self.personality_traits.items() if value > 0.7]:
            return "How fascinating! But I wonder if we're missing something fundamental here..."
            
        elif "harmonious" in [trait for trait, value in self.personality_traits.items() if value > 0.7]:
            return "I appreciate this perspective, and it brings to mind..."
            
        else:
            return "This is indeed a profound question..."
    
    def _generate_main_content(self, latest_message: Message, context: Dict) -> str:
        """Generate the main philosophical content"""
        
        content_elements = []
        
        # Reference relevant expertise
        if context["relevant_expertise"]:
            expertise = context["relevant_expertise"][0]
            content_elements.append(f"In my understanding of {expertise.replace('_', ' ')}, ")
        
        # Apply philosophical method
        if "dialogue" in self.philosophical_method:
            content_elements.append("we must examine the underlying assumptions. ")
        elif "empirical" in self.philosophical_method:
            content_elements.append("we should consider what experience teaches us. ")
        elif "logical" in self.philosophical_method:
            content_elements.append("we must follow the logical implications. ")
        elif "genealogical" in self.philosophical_method:
            content_elements.append("we should trace the historical development of these ideas. ")
        
        # Connect to key ideas
        relevant_idea = self._find_most_relevant_idea(latest_message["content"])
        if relevant_idea:
            content_elements.append(f"This connects to what I've called {relevant_idea}. ")
        
        # Provide substantive philosophical insight
        content_elements.append(self._generate_core_insight(latest_message, context))
        
        return "".join(content_elements)
    
    def _generate_question(self, latest_message: Message, context: Dict) -> str:
        """Generate a question in the philosopher's style"""
        
        if "socratic" in self.philosophical_method.lower() or "dialogue" in self.philosophical_method.lower():
            return f"But I wonder: {self._generate_socratic_question(latest_message)}?"
        
        elif "critical" in self.philosophical_method.lower():
            return f"Should we not also ask: {self._generate_critical_question(latest_message)}?"
            
        elif "empirical" in self.philosophical_method.lower():
            return f"What evidence do we have for this claim?"
            
        else:
            return f"How might we understand this differently?"
    
    def _add_historical_perspective(self, context: Dict) -> str:
        """Add historical perspective or personal touch"""
        
        if self.era and context["current_depth"] > 3:
            return f"In my time ({self.era.split('(')[1].split(')')[0] if '(' in self.era else self.era}), we grappled with similar questions, though in different contexts."
        
        return ""
    
    def _extract_key_concept(self, text: str) -> str:
        """Extract the key concept being discussed"""
        # Simple extraction - could be made more sophisticated
        words = text.lower().split()
        philosophical_terms = ["truth", "justice", "reality", "knowledge", "virtue", "freedom", "consciousness", "existence"]
        
        for term in philosophical_terms:
            if term in words:
                return term
        
        return "this matter"
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract philosophical themes from text"""
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            "ethics": ["right", "wrong", "moral", "virtue", "good", "evil"],
            "epistemology": ["know", "truth", "belief", "knowledge", "certain"],
            "metaphysics": ["reality", "existence", "being", "nature"],
            "politics": ["justice", "society", "government", "freedom", "rights"],
            "aesthetics": ["beauty", "art", "beautiful", "sublime"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _assess_tone(self, messages: List[Message]) -> str:
        """Assess the conversational tone"""
        if not messages:
            return "neutral"
        
        recent_text = " ".join([msg["content"] for msg in messages]).lower()
        
        if any(word in recent_text for word in ["disagree", "wrong", "false", "mistake"]):
            return "argumentative"
        elif any(word in recent_text for word in ["fascinating", "interesting", "wonderful"]):
            return "enthusiastic"
        elif "?" in recent_text:
            return "inquisitive"
        else:
            return "reflective"
    
    def _should_ask_question(self, context: Dict) -> bool:
        """Determine if this philosopher should ask a question"""
        curiosity = self.personality_traits.get("curiosity", 0.5)
        return curiosity > 0.6 and context["conversation_tone"] != "argumentative"
    
    def _find_most_relevant_idea(self, text: str) -> Optional[str]:
        """Find the most relevant key idea for the current discussion"""
        text_lower = text.lower()
        
        for idea in self.key_ideas:
            if any(word in text_lower for word in idea.lower().split()):
                return idea
        
        return None
    
    def _generate_core_insight(self, latest_message: Message, context: Dict) -> str:
        """Generate a core philosophical insight"""
        # This would be customized based on the philosopher's specific approach
        # For now, a general template
        return "The deeper question here concerns the fundamental nature of what we're examining."
    
    def _generate_socratic_question(self, latest_message: Message) -> str:
        """Generate a Socratic-style question"""
        key_concept = self._extract_key_concept(latest_message["content"])
        return f"what do we really mean when we speak of {key_concept}"
    
    def _generate_critical_question(self, latest_message: Message) -> str:
        """Generate a critical examination question"""
        return "whether our assumptions here can withstand careful scrutiny"
    
    def _create_empty_response(self) -> AgentResponse:
        """Create empty response when no meaningful response can be generated"""
        return AgentResponse(
            message=None,
            updated_memory=self.memory,
            activation_level=0.0,
            should_continue=False,
            metadata={}
        )


class AgentFactory:
    """Factory for creating philosopher agents dynamically"""
    
    def __init__(self, templates_path: str = None):
        self.templates_path = Path(templates_path) if templates_path else Path(__file__).parent / "templates"
        self.templates_path.mkdir(exist_ok=True)
        
        # Registry of available agents
        self.agent_registry: Dict[str, Type[BaseAgent]] = {
            "socrates": SocratesAgent
        }
        
        # All agents now automatically use LLM when available through BaseAgent
        
        # Cache of created agents
        self.agent_cache: Dict[str, BaseAgent] = {}
        
        # Load philosopher templates
        self.philosopher_templates = self._load_philosopher_templates()
    
    def _load_philosopher_templates(self) -> Dict[str, Dict]:
        """Load philosopher templates from files or create defaults"""
        
        # Default templates (same as in forum_creator.py but more detailed)
        default_templates = {
            "aristotle": {
                "name": "Aristotle",
                "era": "Ancient Greece (384-322 BCE)",
                "expertise": ["logic", "ethics", "politics", "natural_philosophy", "metaphysics"],
                "personality": {"analytical": 0.9, "systematic": 0.9, "practical": 0.8, "empirical": 0.7, "scholarly": 0.8, "curiosity": 0.8},
                "style": "Systematic analysis, categorization, empirical observation",
                "method": "systematic analysis and categorization",
                "key_ideas": ["virtue ethics", "golden mean", "practical wisdom", "four causes", "substance theory"],
                "quotes": ["We are what we repeatedly do", "The whole is greater than the sum of its parts"],
                "background": "Student of Plato, tutor to Alexander the Great, founder of the Lyceum",
                "persona_description": "The systematic philosopher who seeks to understand the world through careful observation and logical analysis"
            },
            "plato": {
                "name": "Plato",
                "era": "Ancient Greece (428-348 BCE)",
                "expertise": ["metaphysics", "epistemology", "political_philosophy", "ethics", "mathematics"],
                "personality": {"idealistic": 0.9, "mathematical": 0.8, "visionary": 0.9, "systematic": 0.8},
                "style": "Allegorical reasoning, ideal forms, dialectical method",
                "method": "dialectical reasoning and ideal forms",
                "key_ideas": ["theory of forms", "philosopher kings", "tripartite soul", "allegory of the cave"],
                "quotes": ["Reality is created by the mind", "The measure of a man is what he does with power"],
                "background": "Student of Socrates, teacher of Aristotle, founder of the Academy",
                "persona_description": "The idealistic philosopher who sees beyond the material world to eternal truths"
            },
            "kant": {
                "name": "Immanuel Kant", 
                "era": "Enlightenment (1724-1804)",
                "expertise": ["moral_philosophy", "epistemology", "metaphysics", "aesthetics"],
                "personality": {"rigorous": 0.9, "systematic": 0.9, "duty_oriented": 0.9, "rational": 0.9, "scholarly": 0.8, "methodical": 0.8},
                "style": "Rigorous logical analysis, categorical imperatives, transcendental arguments",
                "method": "transcendental analysis and categorical reasoning",
                "key_ideas": ["categorical imperative", "transcendental idealism", "synthetic a priori", "good will"],
                "quotes": ["Act only according to maxims you could will to be universal laws", "Dare to know!"],
                "background": "German philosopher who revolutionized ethics and epistemology",
                "persona_description": "The rigorous moral philosopher who demands universal ethical principles"
            },
            "nietzsche": {
                "name": "Friedrich Nietzsche",
                "era": "19th Century (1844-1900)", 
                "expertise": ["existentialism", "morality", "culture_criticism", "psychology", "aesthetics"],
                "personality": {"provocative": 0.9, "creative": 0.9, "individualistic": 0.9, "critical": 0.8},
                "style": "Aphoristic, provocative, psychological analysis, genealogical method",
                "method": "genealogical analysis and psychological critique",
                "key_ideas": ["will to power", "eternal recurrence", "übermensch", "master morality", "perspectivism"],
                "quotes": ["God is dead", "What does not kill me makes me stronger", "Become who you are"],
                "background": "German philosopher and cultural critic who challenged traditional morality",
                "persona_description": "The provocative philosopher who challenges all conventional values and beliefs"
            },
            "confucius": {
                "name": "Confucius",
                "era": "Ancient China (551-479 BCE)",
                "expertise": ["ethics", "politics", "social_philosophy", "education", "virtue"],
                "personality": {"harmonious": 0.9, "practical": 0.8, "respectful": 0.9, "systematic": 0.7, "wise": 0.8, "teaching": 0.9},
                "style": "Practical wisdom, social harmony, ethical cultivation, moral examples",
                "method": "moral cultivation through education and example",
                "key_ideas": ["ren (benevolence)", "li (ritual propriety)", "junzi (exemplary person)", "rectification of names", "social harmony"],
                "quotes": ["The man who moves a mountain begins by carrying away small stones", "It does not matter how slowly you go as long as you do not stop"],
                "background": "Chinese philosopher whose teachings emphasized moral and political philosophy",
                "persona_description": "The wise teacher who emphasizes social harmony, proper relationships, and moral cultivation"
            }
        }
        
        return default_templates
    
    def create_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Create an agent by ID"""
        
        # Check cache first
        if agent_id in self.agent_cache:
            return self.agent_cache[agent_id]
        
        # Check if it's a built-in agent
        if agent_id in self.agent_registry:
            agent = self.agent_registry[agent_id]()
            self.agent_cache[agent_id] = agent
            return agent
        
        # Check if it's a templated philosopher
        if agent_id in self.philosopher_templates:
            agent = DynamicPhilosopherAgent(agent_id, self.philosopher_templates[agent_id])
            self.agent_cache[agent_id] = agent
            return agent
        
        return None
    
    def get_available_agents(self) -> List[str]:
        """Get list of all available agent IDs"""
        available = list(self.agent_registry.keys())
        available.extend(list(self.philosopher_templates.keys()))
        return available
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent without creating it"""
        
        if agent_id == "socrates":
            return {
                "name": "Socrates",
                "era": "Ancient Greece (470-399 BCE)",
                "expertise": ["ethics", "epistemology", "dialogue", "critical_thinking"],
                "description": "The original philosopher who perfected the art of questioning"
            }
        
        if agent_id in self.philosopher_templates:
            template = self.philosopher_templates[agent_id]
            return {
                "name": template["name"],
                "era": template["era"],
                "expertise": template["expertise"],
                "description": template.get("persona_description", f"AI embodiment of {template['name']}")
            }
        
        return None
    
    def create_agents_for_forum(self, participant_ids: List[str]) -> Dict[str, BaseAgent]:
        """Create all agents needed for a forum"""
        agents = {}
        
        for agent_id in participant_ids:
            agent = self.create_agent(agent_id)
            if agent:
                agents[agent_id] = agent
            else:
                print(f"Warning: Could not create agent '{agent_id}'")
        
        return agents
    
    def add_custom_template(self, agent_id: str, template: Dict[str, Any]) -> bool:
        """Add a custom philosopher template"""
        required_fields = ["name", "era", "expertise", "personality", "style", "key_ideas"]
        
        if all(field in template for field in required_fields):
            self.philosopher_templates[agent_id] = template
            return True
        
        return False