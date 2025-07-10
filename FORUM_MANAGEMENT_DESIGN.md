# Forum Management System Design

## Overview
Transform the philosopher dinner from a single-forum system to a comprehensive multi-forum platform with intelligent management, dynamic agent creation, and natural language search.

## Core Components

### 1. Forum Database Layer
- **ForumDatabase**: Persistent storage for multiple forums
- **Forum lifecycle**: create, join, leave, delete, archive
- **Forum history**: Complete conversation logs with metadata
- **User participation tracking**: Join/leave events, activity logs

### 2. Forum Creation Agent
- **Interactive dialog**: Guides user through forum setup
- **Thinker selection**: Intelligent recommendations based on topics
- **Agent creation**: Dynamic instantiation of new philosopher agents
- **Configuration**: Forum mode, participants, settings

### 3. Dynamic Agent System
- **Agent registry**: Directory of available philosophers/thinkers
- **Dynamic loading**: Create agents on-demand from templates
- **Agent templates**: Standardized personality/expertise definitions
- **Oracle integration**: Always included in forums for fact-checking

### 4. CLI Command System
- `create-forum`: Interactive forum creation with agent guidance
- `join-forum <forum_id>`: Join existing forum with history summary
- `leave-forum`: Exit current forum
- `delete-forum <forum_id>`: Remove forum (with confirmation)
- `list-forums`: Show available forums
- `search-forums <query>`: Natural language forum search

### 5. Forum History & Summarization
- **Private summaries**: Generated when joining forums
- **Scrollable history**: Access to complete conversation logs
- **Join/leave notifications**: System messages for participant changes
- **Contextual onboarding**: New participants get relevant background

### 6. Natural Language Search
- **Vector similarity**: Semantic search across forum content
- **Confidence scoring**: Relevance ratings for search results
- **Topic extraction**: Identify main themes and discussions
- **Smart filtering**: Search by participants, timeframe, topics

## Data Models

### Extended Forum Models
```python
class ForumMetadata(TypedDict):
    forum_id: str
    name: str
    description: str
    mode: ForumMode
    participants: List[str]
    created_at: datetime
    last_activity: datetime
    message_count: int
    creator: str
    tags: List[str]
    is_private: bool

class ForumHistory(TypedDict):
    forum_id: str
    messages: List[Message]
    participant_events: List[ParticipantEvent]
    summaries: Dict[str, str]  # Generated summaries
    
class ParticipantEvent(TypedDict):
    event_type: str  # "join", "leave"
    participant: str
    timestamp: datetime
    forum_id: str
```

### Agent Registry
```python
class ThinkerTemplate(TypedDict):
    thinker_id: str
    name: str
    era: str
    expertise_areas: List[str]
    personality_traits: Dict[str, float]
    speaking_style: str
    key_ideas: List[str]
    famous_quotes: List[str]
    
class AgentRegistry:
    """Registry of available thinkers and their templates"""
    def get_available_thinkers() -> List[ThinkerTemplate]
    def create_agent(thinker_id: str) -> BaseAgent
    def search_thinkers(query: str) -> List[ThinkerTemplate]
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. **Forum Database**: Persistent storage system
2. **Extended state models**: Multi-forum support
3. **Basic CLI commands**: create, join, leave, delete

### Phase 2: Interactive Creation
1. **Forum Creation Agent**: Dialog-based forum setup
2. **Thinker selection**: Interactive philosopher choosing
3. **Dynamic agent creation**: On-demand agent instantiation

### Phase 3: Enhanced Experience
1. **Forum history**: Summaries and scrolling
2. **Join/leave logging**: Participant tracking
3. **Multi-forum CLI**: Navigation between forums

### Phase 4: Advanced Features
1. **Natural language search**: Semantic forum discovery
2. **Smart recommendations**: Forum and participant suggestions
3. **Analytics**: Usage patterns and engagement metrics

## Technical Architecture

### Storage Layer
- **SQLite database**: Forum metadata and history
- **JSON files**: Agent templates and configurations
- **Vector database**: Embeddings for semantic search

### Agent System
- **Factory pattern**: Dynamic agent creation
- **Template system**: Standardized philosopher definitions
- **Registry pattern**: Available thinker catalog

### CLI Architecture
- **Command routing**: Multi-command support
- **State management**: Current forum tracking
- **Rich formatting**: Enhanced user experience

## Security & Privacy
- **Forum access control**: Private/public forums
- **User authentication**: Simple user identification
- **Data persistence**: Secure storage of conversations
- **Audit logging**: Track all forum operations

## Integration Points
- **Existing LangGraph**: Maintain current conversation flow
- **Current agents**: Extend existing Socrates agent
- **State management**: Enhance current state system
- **CLI interface**: Extend current Rich-based interface