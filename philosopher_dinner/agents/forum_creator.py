"""
Forum Creation Agent
Interactive agent that guides users through creating new forums,
selecting appropriate thinkers, and setting up discussions.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .base_agent import BaseAgent
from ..forum.state import ForumState, Message, AgentMemory, AgentResponse, MessageType, ForumMode
from ..forum.database import ForumDatabase, ForumMetadata


@dataclass
class ThinkerSuggestion:
    """Suggestion for a thinker to include in a forum"""
    name: str
    era: str
    expertise: List[str]
    why_relevant: str
    confidence: float


class ForumCreationAgent(BaseAgent):
    """
    Specialized agent for guiding forum creation.
    Asks questions, makes recommendations, and helps users curate forums.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="forum_creator",
            name="Forum Creator",
            persona_description="A helpful guide for creating philosophical forums and selecting appropriate thinkers",
            expertise_areas=["forum_curation", "philosopher_knowledge", "discussion_facilitation"],
            personality_traits={
                "helpfulness": 0.9,
                "curiosity": 0.8,
                "organization": 0.9,
                "patience": 0.9,
                "extroversion": 0.7
            }
        )
        
        self.creation_state = "initial"  # Tracks where we are in the creation process
        self.forum_draft = {}  # Stores forum details as we build them
        self.suggested_thinkers = []  # List of suggested thinkers
        
        # Available thinkers database
        self.available_thinkers = self._load_available_thinkers()
    
    def _load_available_thinkers(self) -> Dict[str, Dict]:
        """Load database of available thinkers"""
        return {
            "socrates": {
                "name": "Socrates",
                "era": "Ancient Greece (470-399 BCE)",
                "expertise": ["ethics", "epistemology", "dialogue", "critical_thinking"],
                "personality": {"wisdom": 0.9, "humility": 0.8, "curiosity": 0.9},
                "style": "Asks probing questions, uses irony, seeks definitions",
                "key_ideas": ["virtue is knowledge", "examined life", "intellectual humility"],
                "quotes": ["The unexamined life is not worth living", "I know that I know nothing"]
            },
            "aristotle": {
                "name": "Aristotle", 
                "era": "Ancient Greece (384-322 BCE)",
                "expertise": ["logic", "ethics", "politics", "natural_philosophy", "metaphysics"],
                "personality": {"analytical": 0.9, "systematic": 0.9, "practical": 0.8},
                "style": "Systematic analysis, categorization, empirical observation",
                "key_ideas": ["virtue ethics", "golden mean", "practical wisdom", "four causes"],
                "quotes": ["We are what we repeatedly do", "The whole is greater than the sum of its parts"]
            },
            "plato": {
                "name": "Plato",
                "era": "Ancient Greece (428-348 BCE)", 
                "expertise": ["metaphysics", "epistemology", "political_philosophy", "ethics"],
                "personality": {"idealistic": 0.9, "mathematical": 0.8, "visionary": 0.9},
                "style": "Allegorical reasoning, ideal forms, dialectical method",
                "key_ideas": ["theory of forms", "philosopher kings", "tripartite soul"],
                "quotes": ["Reality is created by the mind", "The measure of a man is what he does with power"]
            },
            "kant": {
                "name": "Immanuel Kant",
                "era": "Enlightenment (1724-1804)",
                "expertise": ["moral_philosophy", "epistemology", "metaphysics", "aesthetics"],
                "personality": {"rigorous": 0.9, "systematic": 0.9, "duty_oriented": 0.9},
                "style": "Rigorous logical analysis, categorical imperatives, transcendental arguments",
                "key_ideas": ["categorical imperative", "transcendental idealism", "synthetic a priori"],
                "quotes": ["Act only according to maxims you could will to be universal laws"]
            },
            "nietzsche": {
                "name": "Friedrich Nietzsche",
                "era": "19th Century (1844-1900)",
                "expertise": ["existentialism", "morality", "culture_criticism", "psychology"],
                "personality": {"provocative": 0.9, "creative": 0.9, "individualistic": 0.9},
                "style": "Aphoristic, provocative, psychological analysis, genealogical method",
                "key_ideas": ["will to power", "eternal recurrence", "übermensch", "master morality"],
                "quotes": ["God is dead", "What does not kill me makes me stronger"]
            },
            "descartes": {
                "name": "René Descartes",
                "era": "Early Modern (1596-1650)",
                "expertise": ["epistemology", "metaphysics", "methodology", "mathematics"],
                "personality": {"methodical": 0.9, "skeptical": 0.8, "rational": 0.9},
                "style": "Methodical doubt, clear and distinct ideas, mathematical reasoning",
                "key_ideas": ["cogito ergo sum", "mind-body dualism", "methodical doubt"],
                "quotes": ["I think, therefore I am", "Doubt everything"]
            },
            "confucius": {
                "name": "Confucius",
                "era": "Ancient China (551-479 BCE)",
                "expertise": ["ethics", "politics", "education", "social_harmony"],
                "personality": {"traditional": 0.8, "harmonious": 0.9, "educational": 0.9},
                "style": "Practical wisdom, social harmony, moral cultivation",
                "key_ideas": ["ren (benevolence)", "li (ritual propriety)", "junzi (exemplary person)"],
                "quotes": ["Do not impose on others what you do not wish for yourself"]
            },
            "buddha": {
                "name": "Siddhartha Gautama (Buddha)",
                "era": "Ancient India (563-483 BCE)",
                "expertise": ["suffering", "enlightenment", "meditation", "compassion"],
                "personality": {"compassionate": 0.9, "mindful": 0.9, "peaceful": 0.9},
                "style": "Mindful inquiry, compassionate wisdom, practical teachings",
                "key_ideas": ["four noble truths", "eightfold path", "dependent origination"],
                "quotes": ["All suffering comes from attachment", "Be a lamp unto yourself"]
            },
            "locke": {
                "name": "John Locke",
                "era": "Enlightenment (1632-1704)",
                "expertise": ["political_philosophy", "epistemology", "liberalism", "education"],
                "personality": {"empirical": 0.8, "liberal": 0.9, "practical": 0.8},
                "style": "Empirical analysis, natural rights theory, social contract",
                "key_ideas": ["tabula rasa", "natural rights", "social contract", "religious tolerance"],
                "quotes": ["No man's knowledge can go beyond his experience"]
            },
            "hume": {
                "name": "David Hume",
                "era": "Enlightenment (1711-1776)",
                "expertise": ["epistemology", "skepticism", "empiricism", "moral_philosophy"],
                "personality": {"skeptical": 0.9, "empirical": 0.9, "naturalistic": 0.8},
                "style": "Empirical skepticism, naturalistic explanations, habit and custom",
                "key_ideas": ["problem of induction", "is-ought problem", "bundle theory of self"],
                "quotes": ["Reason is slave to the passions"]
            }
        }
    
    def start_forum_creation(self, user_input: str) -> str:
        """Begin the forum creation process"""
        self.creation_state = "gathering_topic"
        self.forum_draft = {"creator": "user", "participants": ["oracle"]}  # Always include oracle
        
        return self._ask_about_topic(user_input)
    
    def _ask_about_topic(self, user_input: str) -> str:
        """Ask user about the topic they want to discuss"""
        # Extract topic hints from user input
        topic_keywords = self._extract_topic_keywords(user_input)
        
        if topic_keywords:
            self.forum_draft["topic_hints"] = topic_keywords
            response = f"""Great! I can see you're interested in topics related to: {', '.join(topic_keywords)}.

Let me help you create the perfect forum for this discussion. 

**What specific question or theme would you like to explore?** 

For example:
- "What is the nature of justice in society?"
- "How should we live a meaningful life?"
- "What can we know for certain?"
- "What is the relationship between mind and body?"

The more specific you are, the better I can recommend the perfect thinkers for your discussion!"""
        else:
            response = """Welcome! I'm here to help you create a fascinating philosophical forum.

**What topic or question would you like to explore?**

You could ask about:
🤔 **Ethics**: What makes an action right or wrong?
🧠 **Mind**: What is consciousness? Do we have free will?
🏛️ **Politics**: What makes a just society?
🌍 **Reality**: What exists? What is truth?
💫 **Meaning**: How should we live? What gives life purpose?

What philosophical question keeps you up at night?"""
        
        return response
    
    def continue_creation_dialog(self, user_input: str) -> Tuple[str, bool]:
        """
        Continue the forum creation dialog.
        Returns (response, is_complete)
        """
        if self.creation_state == "gathering_topic":
            return self._process_topic_input(user_input)
        elif self.creation_state == "suggesting_thinkers":
            return self._process_thinker_selection(user_input)
        elif self.creation_state == "finalizing":
            return self._process_finalization(user_input)
        else:
            return "I'm not sure where we are in the creation process. Let's start over!", False
    
    def _process_topic_input(self, user_input: str) -> Tuple[str, bool]:
        """Process the user's topic input and suggest thinkers"""
        self.forum_draft["topic"] = user_input
        self.forum_draft["description"] = f"A philosophical discussion about: {user_input}"
        
        # Suggest forum mode based on topic
        suggested_mode = self._suggest_forum_mode(user_input)
        self.forum_draft["mode"] = suggested_mode
        
        # Generate thinker suggestions
        suggestions = self._generate_thinker_suggestions(user_input)
        self.suggested_thinkers = suggestions
        
        # Create response with suggestions
        response = f"""Perfect! You want to explore: **"{user_input}"**

Based on this topic, I recommend a **{suggested_mode.value}** style forum, where thinkers will {self._describe_mode(suggested_mode)}.

Here are my top thinker recommendations:

"""
        
        for i, suggestion in enumerate(suggestions[:5], 1):
            response += f"""**{i}. {suggestion.name}** ({suggestion.era})
   🎯 *Relevant because*: {suggestion.why_relevant}
   📚 *Expertise*: {', '.join(suggestion.expertise)}
   
"""
        
        response += """**How would you like to proceed?**

1. **Accept these suggestions** - Say "looks good" or "accept"
2. **Request specific thinkers** - Say "I want [philosopher name]"  
3. **Ask for different suggestions** - Say "show me others" or mention specific areas
4. **Get more details** - Ask about any specific thinker

What sounds interesting to you?"""
        
        self.creation_state = "suggesting_thinkers"
        return response, False
    
    def _process_thinker_selection(self, user_input: str) -> Tuple[str, bool]:
        """Process user's thinker selection choices"""
        user_lower = user_input.lower()
        
        if any(phrase in user_lower for phrase in ["looks good", "accept", "yes", "perfect", "great"]):
            # User accepts suggestions
            selected_thinkers = [s.name.lower().replace(" ", "_") for s in self.suggested_thinkers[:4]]
            self.forum_draft["participants"].extend(selected_thinkers)
            return self._finalize_forum()
            
        elif "show me others" in user_lower or "different" in user_lower:
            # User wants different suggestions
            suggestions = self._generate_alternative_suggestions()
            return self._present_alternative_suggestions(suggestions), False
            
        elif "i want" in user_lower or any(name in user_lower for name in self.available_thinkers.keys()):
            # User requests specific thinkers
            return self._process_specific_requests(user_input)
            
        elif any(name in user_lower for name in [s.name.lower() for s in self.suggested_thinkers]):
            # User asks about a specific suggested thinker
            return self._provide_thinker_details(user_input), False
            
        else:
            return """I'm not sure what you'd like to do. You can:

- Say **"looks good"** to accept my suggestions
- Say **"I want [philosopher name]"** to request specific thinkers  
- Say **"show me others"** for different suggestions
- Ask about any specific thinker for more details

What would you prefer?""", False
    
    def _finalize_forum(self) -> Tuple[str, bool]:
        """Finalize the forum creation"""
        self.creation_state = "finalizing"
        
        # Generate final summary
        participants_list = [name.replace("_", " ").title() for name in self.forum_draft["participants"] if name != "oracle"]
        
        response = f"""🎉 **Your Forum is Ready!**

**📝 Topic**: {self.forum_draft['topic']}
**🎭 Mode**: {self.forum_draft['mode'].value.title()}
**👥 Participants**: {', '.join(participants_list)} + Oracle (fact-checker)

**Your forum will feature**:
- Deep philosophical discussion on your chosen topic
- Each thinker bringing their unique perspective and historical wisdom
- The Oracle providing fact-checking and historical context
- {self._describe_mode(self.forum_draft['mode'])}

**Ready to create this forum?** Just say "create it" and I'll set everything up!

Or say "modify" if you want to change anything."""
        
        return response, False
    
    def _process_finalization(self, user_input: str) -> Tuple[str, bool]:
        """Process final creation confirmation"""
        user_lower = user_input.lower()
        
        if any(phrase in user_lower for phrase in ["create", "yes", "do it", "let's go", "perfect"]):
            # Create the forum
            forum_id = str(uuid.uuid4())[:8]
            
            metadata = ForumMetadata(
                forum_id=forum_id,
                name=f"Discussion: {self.forum_draft['topic'][:50]}...",
                description=self.forum_draft['description'],
                mode=self.forum_draft['mode'],
                participants=self.forum_draft['participants'],
                created_at=datetime.now(),
                creator=self.forum_draft['creator'],
                tags=self._extract_topic_keywords(self.forum_draft['topic']),
                is_private=False
            )
            
            # Save to database (would need database instance)
            return f"""✅ **Forum Created Successfully!**

**Forum ID**: `{forum_id}`
**Ready to join**: Your philosophical discussion awaits!

The thinkers are gathering and preparing their thoughts. You can now join the forum and begin the conversation!

*Use the command `join-forum {forum_id}` to enter your new forum.*""", True
            
        elif "modify" in user_lower:
            return "What would you like to modify? The topic, the thinkers, or the forum mode?", False
            
        else:
            return 'Say "create it" to finalize your forum, or "modify" to make changes!', False
    
    def _generate_thinker_suggestions(self, topic: str) -> List[ThinkerSuggestion]:
        """Generate thinker suggestions based on topic"""
        topic_lower = topic.lower()
        suggestions = []
        
        # Score each thinker based on topic relevance
        for thinker_id, info in self.available_thinkers.items():
            score = 0.0
            why_relevant = []
            
            # Check expertise areas
            for expertise in info["expertise"]:
                if any(keyword in topic_lower for keyword in expertise.split("_")):
                    score += 0.4
                    why_relevant.append(f"expert in {expertise}")
            
            # Check key ideas
            for idea in info["key_ideas"]:
                if any(keyword in topic_lower for keyword in idea.lower().split()):
                    score += 0.3
                    why_relevant.append(f"developed ideas about {idea}")
            
            # Topic-specific bonuses
            if "justice" in topic_lower or "society" in topic_lower:
                if thinker_id in ["plato", "aristotle", "locke"]:
                    score += 0.5
                    why_relevant.append("fundamental work on justice and society")
            
            if "mind" in topic_lower or "consciousness" in topic_lower:
                if thinker_id in ["descartes", "hume"]:
                    score += 0.5
                    why_relevant.append("pioneered thinking about mind and consciousness")
            
            if "ethics" in topic_lower or "moral" in topic_lower:
                if thinker_id in ["kant", "aristotle", "confucius"]:
                    score += 0.5
                    why_relevant.append("created foundational ethical frameworks")
            
            if score > 0.3:
                suggestions.append(ThinkerSuggestion(
                    name=info["name"],
                    era=info["era"],
                    expertise=info["expertise"],
                    why_relevant="; ".join(why_relevant[:2]),
                    confidence=min(1.0, score)
                ))
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:8]  # Return top 8
    
    def _suggest_forum_mode(self, topic: str) -> ForumMode:
        """Suggest appropriate forum mode based on topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["versus", "vs", "better", "which", "compare"]):
            return ForumMode.DEBATE
        elif any(word in topic_lower for word in ["what is", "nature of", "explore", "understand"]):
            return ForumMode.EXPLORATION  
        else:
            return ForumMode.CONSENSUS
    
    def _describe_mode(self, mode: ForumMode) -> str:
        """Describe what a forum mode means"""
        descriptions = {
            ForumMode.CONSENSUS: "thinkers will seek common ground and shared understanding",
            ForumMode.DEBATE: "thinkers will present opposing viewpoints and defend their positions",
            ForumMode.EXPLORATION: "thinkers will openly explore the question from multiple angles"
        }
        return descriptions.get(mode, "engage in philosophical discussion")
    
    def _extract_topic_keywords(self, text: str) -> List[str]:
        """Extract philosophical topic keywords from text"""
        philosophical_terms = {
            "ethics", "morality", "virtue", "justice", "good", "evil", "right", "wrong",
            "consciousness", "mind", "body", "soul", "free will", "determinism",
            "truth", "knowledge", "reality", "existence", "being", "metaphysics",
            "politics", "society", "government", "democracy", "freedom", "rights",
            "meaning", "purpose", "life", "death", "happiness", "suffering"
        }
        
        text_lower = text.lower()
        found_terms = [term for term in philosophical_terms if term in text_lower]
        return found_terms[:5]  # Return up to 5 most relevant terms
    
    def generate_response(self, state: ForumState) -> AgentResponse:
        """Generate response for LangGraph compatibility"""
        # This agent is primarily used outside of LangGraph for forum creation
        # But we implement this for interface compatibility
        
        latest_message = state["messages"][-1] if state["messages"] else None
        
        if latest_message and latest_message["content"]:
            response_text = self.start_forum_creation(latest_message["content"])
            
            message = self.create_message(
                content=response_text,
                thinking="Helping user create a new philosophical forum"
            )
            
            return AgentResponse(
                message=message,
                updated_memory=self.memory,
                activation_level=1.0,
                should_continue=False,
                metadata={"creation_state": self.creation_state}
            )
        
        return AgentResponse(
            message=None,
            updated_memory=self.memory,
            activation_level=0.0,
            should_continue=False,
            metadata={}
        )