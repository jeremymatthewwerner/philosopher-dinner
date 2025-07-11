"""
LangGraph orchestrator for the philosopher dinner forum.
Manages the flow of conversation between agents and humans.
Enhanced with multi-forum support and dynamic agent loading.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ForumState, ForumConfig, ForumMode, Message, MessageType
from .database import ForumDatabase, ParticipantEvent
from ..agents.base_agent import BaseAgent
from ..agents.socrates import SocratesAgent
from ..agents.agent_factory import AgentFactory


class PhilosopherForum:
    """
    Main orchestrator for philosopher conversations using LangGraph.
    Manages multiple agents and coordinates their interactions.
    Enhanced with multi-forum support and dynamic agent loading.
    """
    
    def __init__(self, forum_config: ForumConfig, database: Optional[ForumDatabase] = None):
        self.forum_config = forum_config
        self.agents: Dict[str, BaseAgent] = {}
        self.graph = None
        self.memory = MemorySaver()
        self.database = database or ForumDatabase()
        self.agent_factory = AgentFactory()
        
        # Initialize agents based on forum participants
        self._initialize_agents()
        
        # Build the LangGraph
        self._build_graph()
    
    def _initialize_agents(self):
        """Initialize agent instances based on forum configuration using AgentFactory"""
        
        # Create all agents dynamically using the factory
        for participant_id in self.forum_config["participants"]:
            # Skip non-philosopher participants
            if participant_id in ["oracle", "user", "human"]:
                continue
            
            agent = self.agent_factory.create_agent(participant_id)
            if agent:
                self.agents[participant_id] = agent
            else:
                print(f"Warning: Could not create agent for '{participant_id}'")
        
        # Always ensure we have at least Socrates
        if "socrates" not in self.agents and "socrates" in self.forum_config["participants"]:
            self.agents["socrates"] = SocratesAgent()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(ForumState)
        
        # Add agent nodes
        for agent_id, agent in self.agents.items():
            workflow.add_node(agent_id, agent.process_message)
        
        # Add special nodes
        workflow.add_node("coordinator", self._coordinate_conversation)
        workflow.add_node("human_input", self._wait_for_human_input)
        
        # Define the flow
        workflow.set_entry_point("coordinator")
        
        # From coordinator, decide who should speak next
        workflow.add_conditional_edges(
            "coordinator",
            self._decide_next_speaker,
            {
                "human": "human_input",
                "end": END,
                **{agent_id: agent_id for agent_id in self.agents.keys()}
            }
        )
        
        # From any agent, go back to coordinator
        for agent_id in self.agents.keys():
            workflow.add_edge(agent_id, "coordinator")
        
        # From human input, go to coordinator
        workflow.add_edge("human_input", "coordinator")
        
        # Compile the graph with recursion limit
        self.graph = workflow.compile(checkpointer=self.memory)
    
    def _coordinate_conversation(self, state: ForumState) -> ForumState:
        """
        Coordinator node that manages conversation flow and determines next steps.
        """
        current_time = datetime.now()
        
        # Update state metadata
        updated_state = state.copy()
        updated_state["last_updated"] = current_time
        
        # Initialize agent memories if not present
        for agent_id in self.agents.keys():
            if agent_id not in updated_state["agent_memories"]:
                updated_state["agent_memories"][agent_id] = self.agents[agent_id].memory
            if agent_id not in updated_state["agent_activations"]:
                updated_state["agent_activations"][agent_id] = 0.5
        
        # Update current topic if needed
        if updated_state["messages"]:
            latest_message = updated_state["messages"][-1]
            if latest_message["message_type"] == MessageType.HUMAN:
                # Extract topic from human message (simplified)
                updated_state["current_topic"] = self._extract_topic(latest_message["content"])
        
        return updated_state
    
    def _decide_next_speaker(self, state: ForumState) -> str:
        """
        Decide who should speak next based on agent activations and conversation flow.
        """
        # If waiting for human input
        if state.get("waiting_for_human", False):
            return "human"
        
        # If conversation is too long, end it
        if state["turn_count"] > 10:  # Reduced from 20 to prevent long loops
            return "end"
        
        # If we just had an agent response, end the conversation for now
        # This prevents infinite loops - each conversation is one human->agent exchange
        if state["messages"] and state["messages"][-1]["message_type"] == MessageType.AGENT:
            return "end"
        
        # Check for direct mentions in the latest message
        if state["messages"]:
            latest_message = state["messages"][-1]
            if latest_message["message_type"] == MessageType.HUMAN:
                mentioned_agent = self._detect_direct_mention(latest_message["content"])
                if mentioned_agent and mentioned_agent in self.agents:
                    return mentioned_agent
        
        # Calculate who should speak next
        agent_scores = {}
        
        # Use lower threshold for multi-agent conversations to encourage diversity
        activation_threshold = 0.3 if len(self.agents) > 2 else 0.6
        
        for agent_id, agent in self.agents.items():
            # Skip if agent spoke recently
            recent_messages = state["messages"][-2:] if len(state["messages"]) >= 2 else []
            if any(msg["sender"] == agent_id for msg in recent_messages):
                continue
                
            # Calculate activation score
            activation = agent.evaluate_activation(state)
            should_respond = agent.should_respond(state, activation_threshold)
            
            if should_respond:
                agent_scores[agent_id] = activation
        
        # Choose the most activated agent with some variety for multi-agent conversations
        if agent_scores:
            if len(agent_scores) == 1:
                # Only one agent wants to respond
                return list(agent_scores.keys())[0]
            else:
                # Multiple agents want to respond - add some variety
                # Check who spoke last to encourage turn-taking
                last_speakers = []
                for msg in reversed(state["messages"][-5:]):  # Last 5 messages
                    if msg["message_type"] == MessageType.AGENT:
                        last_speakers.append(msg["sender"])
                
                # For new conversations, add some variety by not always picking the highest scorer
                if not last_speakers and len(agent_scores) > 1:
                    # For brand new conversations, use weighted random selection
                    import random
                    
                    # Sort agents by activation but add some randomness
                    sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
                    
                    # Give higher weight to top agents but allow others to speak too
                    # Top agent gets 40% chance, second gets 30%, others split the rest
                    if len(sorted_agents) >= 2:
                        rand = random.random()
                        if rand < 0.4:
                            return sorted_agents[0][0]  # Highest activation
                        elif rand < 0.7:
                            return sorted_agents[1][0]  # Second highest
                        else:
                            # Random choice from the rest
                            remaining = sorted_agents[2:] if len(sorted_agents) > 2 else [sorted_agents[0]]
                            return random.choice(remaining)[0]
                    else:
                        return sorted_agents[0][0]
                
                # Prefer agents who haven't spoken recently
                available_agents = [
                    agent_id for agent_id in agent_scores.keys() 
                    if agent_id not in last_speakers[:2]  # Not in last 2 speakers
                ]
                
                if available_agents:
                    # Choose best among agents who haven't spoken recently
                    best_agent = max(available_agents, key=lambda x: agent_scores[x])
                    return best_agent
                else:
                    # All agents spoke recently, choose the most activated
                    best_agent = max(agent_scores.keys(), key=lambda x: agent_scores[x])
                    return best_agent
        
        # If no agent wants to speak with normal threshold, try with even lower threshold
        if not agent_scores and len(self.agents) > 1:
            for agent_id, agent in self.agents.items():
                recent_messages = state["messages"][-2:] if len(state["messages"]) >= 2 else []
                if any(msg["sender"] == agent_id for msg in recent_messages):
                    continue
                activation = agent.evaluate_activation(state)
                if activation > 0.2:  # Very low threshold as fallback
                    agent_scores[agent_id] = activation
            
            if agent_scores:
                best_agent = max(agent_scores.keys(), key=lambda x: agent_scores[x])
                return best_agent
        
        # If still no agent wants to speak, end conversation
        return "end"
    
    def _wait_for_human_input(self, state: ForumState) -> ForumState:
        """
        Node that waits for human input.
        In practice, this will be handled by the CLI interface.
        """
        updated_state = state.copy()
        updated_state["waiting_for_human"] = True
        return updated_state
    
    def _detect_direct_mention(self, message_content: str) -> Optional[str]:
        """
        Detect if a specific philosopher is directly mentioned in a message.
        Returns the agent_id if found, None otherwise.
        """
        content_lower = message_content.lower()
        
        # Map of names to agent IDs (including variations)
        name_mappings = {
            "socrates": "socrates",
            "aristotle": "aristotle", 
            "kant": "kant",
            "immanuel kant": "kant",
            "nietzsche": "nietzsche",
            "friedrich nietzsche": "nietzsche",
            "confucius": "confucius",
            "plato": "plato"
        }
        
        # Check for direct mentions with various patterns
        mention_patterns = [
            # Direct address patterns
            "{name} what say you",
            "{name} what do you think",
            "hey {name}",
            "{name}!",
            "{name},",
            "{name}?",
            # Question patterns
            "what would {name} say",
            "how would {name} respond",
            "{name}'s view",
            "ask {name}"
        ]
        
        for name, agent_id in name_mappings.items():
            # Check if the philosopher's name appears in the message
            if name in content_lower:
                # Check for direct mention patterns
                for pattern in mention_patterns:
                    formatted_pattern = pattern.format(name=name)
                    if formatted_pattern in content_lower:
                        return agent_id
                
                # Also check if the name appears at the beginning (direct address)
                if content_lower.startswith(name) or content_lower.startswith(f"hey {name}"):
                    return agent_id
        
        return None
    
    def _extract_topic(self, message_content: str) -> str:
        """
        Extract the main topic from a message.
        Simplified implementation for now.
        """
        # Simple keyword extraction
        philosophical_topics = [
            "truth", "reality", "existence", "knowledge", "wisdom",
            "ethics", "morality", "justice", "virtue", "good", "evil",
            "beauty", "love", "friendship", "happiness", "death",
            "consciousness", "mind", "soul", "god", "divine"
        ]
        
        content_lower = message_content.lower()
        for topic in philosophical_topics:
            if topic in content_lower:
                return topic
                
        # Default topic
        return "philosophical discussion"
    
    def create_initial_state(self, initial_message: str = None) -> ForumState:
        """Create the initial state for a new conversation"""
        session_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        initial_state = ForumState(
            messages=[],
            current_topic="introduction",
            active_speakers=[],
            forum_config=self.forum_config,
            participants=list(self.agents.keys()),
            agent_memories={},
            agent_activations={},
            turn_count=0,
            last_speaker=None,
            waiting_for_human=False,
            session_id=session_id,
            created_at=current_time,
            last_updated=current_time
        )
        
        # Add initial human message if provided
        if initial_message:
            human_message = Message(
                id=str(uuid.uuid4()),
                sender="human",
                content=initial_message,
                message_type=MessageType.HUMAN,
                timestamp=current_time,
                thinking=None,
                metadata={}
            )
            initial_state["messages"].append(human_message)
            initial_state["current_topic"] = self._extract_topic(initial_message)
        
        return initial_state
    
    def add_human_message(self, state: ForumState, message: str) -> ForumState:
        """Add a human message to the conversation state"""
        updated_state = state.copy()
        
        human_message = Message(
            id=str(uuid.uuid4()),
            sender="human",
            content=message,
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        updated_state["messages"].append(human_message)
        updated_state["waiting_for_human"] = False
        updated_state["current_topic"] = self._extract_topic(message)
        updated_state["turn_count"] += 1
        
        return updated_state
    
    def start_conversation(self, initial_message: str = None) -> Dict[str, Any]:
        """Start a new conversation and return the initial state"""
        initial_state = self.create_initial_state(initial_message)
        
        # Run one step to get initial agent responses
        result = self.graph.invoke(
            initial_state,
            config={
                "configurable": {"thread_id": initial_state["session_id"]},
                "recursion_limit": 25  # Reasonable limit for multi-agent conversations
            }
        )
        
        return result
    
    def continue_conversation(self, state: ForumState, human_message: str = None) -> Dict[str, Any]:
        """Continue an existing conversation"""
        if human_message:
            state = self.add_human_message(state, human_message)
        
        # Continue the conversation
        result = self.graph.invoke(
            state,
            config={
                "configurable": {"thread_id": state["session_id"]},
                "recursion_limit": 25  # Reasonable limit for multi-agent conversations
            }
        )
        
        return result
    
    def add_participant_join_message(self, state: ForumState, participant: str) -> ForumState:
        """Add a system message when a participant joins the forum"""
        updated_state = state.copy()
        
        join_message = Message(
            id=str(uuid.uuid4()),
            sender="system",
            content=f"📍 {participant.replace('_', ' ').title()} has joined the conversation",
            message_type=MessageType.SYSTEM,
            timestamp=datetime.now(),
            thinking=None,
            metadata={"event_type": "participant_join", "participant": participant}
        )
        
        updated_state["messages"].append(join_message)
        
        # Add to database if available
        if self.database:
            self.database.add_message(self.forum_config["forum_id"], join_message)
        
        return updated_state
    
    def add_participant_leave_message(self, state: ForumState, participant: str) -> ForumState:
        """Add a system message when a participant leaves the forum"""
        updated_state = state.copy()
        
        leave_message = Message(
            id=str(uuid.uuid4()),
            sender="system",
            content=f"👋 {participant.replace('_', ' ').title()} has left the conversation",
            message_type=MessageType.SYSTEM,
            timestamp=datetime.now(),
            thinking=None,
            metadata={"event_type": "participant_leave", "participant": participant}
        )
        
        updated_state["messages"].append(leave_message)
        
        # Add to database if available
        if self.database:
            self.database.add_message(self.forum_config["forum_id"], leave_message)
        
        return updated_state
    
    def get_forum_history(self, limit: int = None, offset: int = 0) -> List[Message]:
        """Get forum conversation history from database"""
        if self.database:
            return self.database.get_messages(self.forum_config["forum_id"], limit, offset)
        return []
    
    def get_participant_events(self) -> List[ParticipantEvent]:
        """Get participant join/leave events for this forum"""
        if self.database:
            return self.database.get_participant_events(self.forum_config["forum_id"])
        return []
    
    def save_forum_summary(self, summary: str, summary_type: str = "brief") -> bool:
        """Save a generated summary for this forum"""
        if self.database:
            return self.database.save_forum_summary(
                self.forum_config["forum_id"], 
                summary_type, 
                summary
            )
        return False
    
    def get_forum_summary(self, summary_type: str = "brief") -> Optional[str]:
        """Get a saved summary for this forum"""
        if self.database:
            return self.database.get_forum_summary(self.forum_config["forum_id"], summary_type)
        return None