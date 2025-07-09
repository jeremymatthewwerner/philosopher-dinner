# Philosopher Dinner - System Architecture

## Overview
Multi-agent philosophy forum using LangGraph where AI agents embody famous philosophers, mathematicians, and thinkers to engage in group discussions with humans.

## System Architecture

### Core Components

#### 1. LangGraph Multi-Agent Orchestrator
- **Agent Nodes**: Each philosopher/thinker as a separate node
- **Collaboration Pattern**: Shared conversation state
- **Dynamic Control Flow**: Agents decide when to participate
- **State Management**: Persistent conversation and agent memories

#### 2. Agent Types

##### Philosopher Agents
- **Personas**: Historical figures (Socrates, Kant, Nietzsche, etc.)
- **Schools of Thought**: Stoicism, Existentialism, Utilitarianism
- **Cross-Disciplinary**: Mathematicians, economists, scientists
- **Behavior**: Authentic debate style, tone, participation patterns

##### Oracle Agent
- **Role**: Fact-checking and information retrieval
- **Capabilities**: Web search via MCP, authoritative information
- **Activation**: On-demand by any participant
- **Response Style**: Clear factual statements with uncertainty indicators

#### 3. Forum Management System
- **Forum Controller**: Manages multiple conversation spaces
- **Forum Modes**: 
  - Consensus: Seek common ground
  - Debate: Competitive argumentation
  - Exploration: Open philosophical inquiry
- **Persistence**: Each forum maintains independent state

#### 4. Memory Architecture

##### Short-term Memory
- **Conversation History**: Recent messages and context
- **Agent Working Memory**: Current thoughts and reasoning
- **Forum State**: Active participants, topic, mode

##### Long-term Memory (ChromaDB)
- **Agent Personalities**: Evolving character traits and positions
- **Conversation Archives**: Searchable discussion history
- **Relationship Dynamics**: How agents interact with each other
- **Topic Expertise**: Agent knowledge areas and interests

#### 5. CLI Interface
- **Rich Terminal UI**: Formatted conversation display
- **Real-time Updates**: Live agent responses
- **Human Controls**: Forum switching, mode changes, direct queries
- **Logging**: Comprehensive conversation transcripts

## LangGraph Implementation

### State Schema
```python
class ForumState(TypedDict):
    messages: List[Message]
    participants: List[str]
    forum_mode: str  # consensus, debate, exploration
    current_topic: str
    conversation_history: List[Message]
    agent_memories: Dict[str, AgentMemory]
    forum_config: ForumConfig
```

### Agent Node Structure
```python
class PhilosopherAgent:
    def __init__(self, persona: str, expertise: List[str]):
        self.persona = persona
        self.expertise = expertise
        self.memory = AgentMemory()
        self.activation_level = 0.5
    
    def process_message(self, state: ForumState) -> ForumState:
        # Determine if agent should respond
        # Generate response based on persona
        # Update agent memory
        # Return updated state
```

### Graph Flow
1. **Message Reception**: Human or agent input triggers state update
2. **Agent Activation**: Agents evaluate relevance and decide to participate
3. **Response Generation**: Active agents generate responses in character
4. **State Update**: New messages added to shared state
5. **Memory Storage**: Long-term memory updated in ChromaDB
6. **Cycle Continue**: Process repeats for next input

## Data Flow

### Input Processing
1. User input received via CLI
2. Message added to forum state
3. All agents evaluate message relevance
4. Agents with high activation generate responses
5. Responses added to conversation flow

### Memory Management
1. **Immediate**: Recent conversation in working memory
2. **Session**: Full conversation stored in forum state
3. **Persistent**: ChromaDB stores agent evolution and archives
4. **Retrieval**: Agents query memories for context and consistency

### Oracle Integration
1. **Trigger**: Any participant can invoke Oracle
2. **Research**: Oracle uses MCP to access web information
3. **Response**: Factual information with confidence indicators
4. **Integration**: Other agents can build on Oracle's information

## Technical Implementation

### Dependencies
- `langgraph`: Multi-agent orchestration
- `chromadb`: Vector database for memory
- `rich`: Terminal UI formatting
- `asyncio`: Async conversation handling
- `pydantic`: Data validation and schemas

### File Structure
```
philosopher_dinner/
├── agents/
│   ├── base_agent.py
│   ├── philosopher_agent.py
│   └── oracle_agent.py
├── forum/
│   ├── forum_controller.py
│   ├── state_management.py
│   └── memory_manager.py
├── cli/
│   ├── interface.py
│   └── conversation_display.py
├── config/
│   ├── personas.json
│   └── forum_templates.json
└── main.py
```

## Deployment Architecture

### Local Development
- Python virtual environment
- Local ChromaDB instance
- CLI interface for testing
- Git repository for version control

### Production Considerations
- Containerized deployment
- Scalable ChromaDB instance
- Web interface option
- Multi-user support

## Next Steps

1. **Core Implementation**: Build basic LangGraph structure
2. **Agent Development**: Create philosopher personas
3. **Memory Integration**: ChromaDB setup and integration
4. **CLI Interface**: Rich terminal experience
5. **Testing**: Multi-agent conversation scenarios
6. **Optimization**: Performance and response quality

---

*Architecture designed for educational exploration of multi-agent systems and philosophical discourse.*