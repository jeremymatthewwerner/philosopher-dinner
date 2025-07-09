"""
Core state management for the philosopher dinner forum.
Using TypedDict for LangGraph state compatibility.
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ForumMode(Enum):
    """Different forum discussion modes"""
    CONSENSUS = "consensus"  # Seek common ground
    DEBATE = "debate"        # Competitive argumentation  
    EXPLORATION = "exploration"  # Open philosophical inquiry


class MessageType(Enum):
    """Types of messages in the forum"""
    HUMAN = "human"
    AGENT = "agent" 
    ORACLE = "oracle"
    SYSTEM = "system"


class Message(TypedDict):
    """Individual message in the conversation"""
    id: str
    sender: str
    content: str
    message_type: MessageType
    timestamp: datetime
    thinking: Optional[str]  # Agent's internal reasoning
    metadata: Dict[str, Any]


class AgentMemory(TypedDict):
    """Memory structure for individual agents"""
    agent_id: str
    personality_traits: Dict[str, float]
    conversation_history: List[Message]
    relationships: Dict[str, float]  # How agent views other agents
    topic_interests: Dict[str, float]
    last_active: datetime


class ForumConfig(TypedDict):
    """Configuration for a forum instance"""
    forum_id: str
    name: str
    description: str
    mode: ForumMode
    participants: List[str]  # Agent IDs
    created_at: datetime
    settings: Dict[str, Any]


class ForumState(TypedDict):
    """
    Main state object for LangGraph.
    This gets passed between all agent nodes.
    """
    # Current conversation
    messages: List[Message]
    current_topic: str
    active_speakers: List[str]
    
    # Forum configuration
    forum_config: ForumConfig
    participants: List[str]
    
    # Agent memories and states
    agent_memories: Dict[str, AgentMemory]
    agent_activations: Dict[str, float]  # Current activation levels
    
    # Conversation flow control
    turn_count: int
    last_speaker: Optional[str]
    waiting_for_human: bool
    
    # Metadata
    session_id: str
    created_at: datetime
    last_updated: datetime


class AgentResponse(TypedDict):
    """Response from an agent node"""
    message: Optional[Message]
    updated_memory: AgentMemory
    activation_level: float
    should_continue: bool
    metadata: Dict[str, Any]