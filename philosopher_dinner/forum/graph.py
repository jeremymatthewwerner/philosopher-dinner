"""
LangGraph orchestrator for the philosopher dinner forum.
Manages the flow of conversation between agents and humans.
"""
from typing import Dict, Any, List
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ForumState, ForumConfig, ForumMode, Message, MessageType
from ..agents.base_agent import BaseAgent
from ..agents.socrates import SocratesAgent


class PhilosopherForum:
    """
    Main orchestrator for philosopher conversations using LangGraph.
    Manages multiple agents and coordinates their interactions.
    """
    
    def __init__(self, forum_config: ForumConfig):
        self.forum_config = forum_config
        self.agents: Dict[str, BaseAgent] = {}
        self.graph = None
        self.memory = MemorySaver()
        
        # Initialize agents based on forum participants
        self._initialize_agents()
        
        # Build the LangGraph
        self._build_graph()
    
    def _initialize_agents(self):
        """Initialize agent instances based on forum configuration"""
        
        # For now, we'll manually create agents
        # Later this can be driven by configuration
        
        if "socrates" in self.forum_config["participants"]:
            self.agents["socrates"] = SocratesAgent()
        
        # TODO: Add more agents as we implement them
        # if "aristotle" in self.forum_config["participants"]:
        #     self.agents["aristotle"] = AristotleAgent()
        # if "oracle" in self.forum_config["participants"]:
        #     self.agents["oracle"] = OracleAgent()
    
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
        
        # Compile the graph
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
        if state["turn_count"] > 20:
            return "end"
        
        # Calculate who should speak next
        agent_scores = {}
        
        for agent_id, agent in self.agents.items():
            # Skip if agent spoke recently
            recent_messages = state["messages"][-2:] if len(state["messages"]) >= 2 else []
            if any(msg["sender"] == agent_id for msg in recent_messages):
                continue
                
            # Calculate activation score
            activation = agent.evaluate_activation(state)
            should_respond = agent.should_respond(state)
            
            if should_respond:
                agent_scores[agent_id] = activation
        
        # Choose the most activated agent
        if agent_scores:
            best_agent = max(agent_scores.keys(), key=lambda x: agent_scores[x])
            return best_agent
        
        # If no agent wants to speak, wait for human
        return "human"
    
    def _wait_for_human_input(self, state: ForumState) -> ForumState:
        """
        Node that waits for human input.
        In practice, this will be handled by the CLI interface.
        """
        updated_state = state.copy()
        updated_state["waiting_for_human"] = True
        return updated_state
    
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
            config={"configurable": {"thread_id": initial_state["session_id"]}}
        )
        
        return result
    
    def continue_conversation(self, state: ForumState, human_message: str = None) -> Dict[str, Any]:
        """Continue an existing conversation"""
        if human_message:
            state = self.add_human_message(state, human_message)
        
        # Continue the conversation
        result = self.graph.invoke(
            state,
            config={"configurable": {"thread_id": state["session_id"]}}
        )
        
        return result