# Philosopher Forum: Multi-Agent Chat System

## Project Overview

A multi-agent system that teaches modern agentic programming techniques through a collaborative chat interface where users can converse with AI agents representing famous philosophers, mathematicians, and schools of thought.

## Core Features

### 1. Multi-Agent Collaboration
- Multiple AI agents working together in real-time conversations
- Each agent maintains their own persona, memory, and reasoning processes
- Agents can collaborate, debate, and build upon each other's ideas

### 2. Philosopher Forums
- Create multiple "forum" instances with different collections of thinkers
- Switch between forums to continue separate conversations
- Each forum persists independently with its own history and context
- **Forum Modes**: Configurable debate objectives set at creation time:
  - **Consensus Mode**: Agents work toward common ground and agreement
  - **Debate Mode**: Agents compete to win arguments while staying true to their personas
  - **Exploration Mode**: Open-ended philosophical exploration without specific goals

### 3. Agent Personas
- **Historical Figures**: Socrates, Aristotle, Kant, Nietzsche, Einstein, etc.
- **Schools of Thought**: Stoicism, Existentialism, Utilitarianism, etc.
- **Cross-Disciplinary Thinkers**: Early mathematicians, economists, scientists, theologians
- **Contemporary Thinkers**: Modern philosophers and thought leaders
- **The Oracle**: Special agent that provides factual information and fact-checking
- Each agent researches and embodies their assigned persona using MCP
- Authentic behavior includes tone, debate style, and conversation participation patterns

### 4. Real-Time Group Chat Interface
- Command-line chat interface for natural conversation flow
- All agents participate simultaneously like a group chat
- Human user can direct questions to specific agents or the group

### 5. Advanced Memory & Planning
- **Long-term Memory**: Agents remember past conversations across sessions
- **Individual Planning**: Each agent maintains their own thought processes
- **Contextual Awareness**: Agents understand the flow of conversation

### 6. Comprehensive Logging
- **Chat History**: Full conversation log with timestamps
- **Agent Thinking**: Internal reasoning processes shown in lighter text
- **Markdown Format**: Human-readable conversation transcripts
- **Persistent Storage**: All conversations saved for future reference

## Technical Architecture

### Framework Selection (Latest 2024/2025)
- **Multi-Agent Framework**: LangGraph for orchestration and agent coordination
  - Graph-based architecture with agents as nodes and communication as edges
  - Stateful execution with persistent memory across interactions
  - Support for cycles and dynamic control flow
  - Supervisor and collaboration patterns for agent coordination
- **Memory System**: ChromaDB (local vector database) + conversation memory for long-term personality evolution
- **MCP Integration**: For research and tool access
- **CLI Interface**: Rich Python CLI with real-time updates

### Core Components
1. **Agent Manager**: Orchestrates multiple agent instances with self-coordination
2. **Forum Controller**: Manages different conversation spaces with configurable debate modes
3. **Memory System**: Persistent storage for agent memories and chat history
4. **Persona Engine**: Loads and maintains authentic character representations
5. **Oracle Agent**: Special fact-checking agent with web access via MCP
6. **Chat Interface**: Real-time command-line interaction
7. **Logging System**: Comprehensive conversation and thought tracking

## User Experience

### Starting a Session
```bash
python philosopher_forum.py
> Available forums: ancient_greece, enlightenment, modern_ethics
> Select forum or create new: ancient_greece
> Forum mode: debate | consensus | exploration
> Joining forum with: Socrates, Aristotle, Plato, Oracle
```

### Chat Flow
```
[2025-01-09 14:30:15] You: What is the nature of justice?

[Socrates thinking: The user asks about justice - this is central to my method. I should use questioning to help them examine their assumptions...]

[2025-01-09 14:30:18] Socrates: Before we can discuss justice, we must first examine what we think we know about it. Tell me, what do you believe justice to be?

[Aristotle thinking: Socrates begins with his typical approach. I should contribute my systematic view while respecting his method...]

[2025-01-09 14:30:22] Aristotle: While Socrates questions, I would add that justice is a virtue - specifically, giving each their due according to merit and contribution to the polis.

[2025-01-09 14:30:25] You: Oracle, what did Plato actually say about justice in the Republic?

[Oracle thinking: The user wants factual information about Plato's theory of justice. Let me search for accurate information about his views in the Republic...]

[2025-01-09 14:30:28] Oracle: According to Plato's Republic, justice is achieved when each part of the soul performs its proper function - wisdom in the rational part, courage in the spirited part, and temperance in the appetitive part. In the state, this corresponds to rulers, guardians, and producers each fulfilling their roles. This is a factual summary based on Books IV and IX of the Republic.
```

## Development Phases

### Phase 1: Core Infrastructure
- [ ] Set up multi-agent framework
- [ ] Implement basic chat interface
- [ ] Create single forum with 2-3 agents
- [ ] Basic memory and logging

### Phase 2: Advanced Features
- [ ] Multiple forum support
- [ ] Enhanced persona system with MCP research
- [ ] Advanced memory and planning
- [ ] Rich CLI interface

### Phase 3: Polish & Extension
- [ ] Performance optimization
- [ ] Additional personas and forums
- [ ] Advanced conversation features
- [ ] Documentation and examples

## Learning Objectives

This project will teach:
- **Multi-agent coordination** and communication patterns
- **Advanced memory systems** for AI agents
- **Real-time collaborative AI** systems
- **Persona-based AI** development
- **Modern agentic frameworks** and patterns
- **MCP integration** for dynamic information access

## Design Decisions

### Agent Configuration
- **3-5 agents per forum** - manageable conversation size while maintaining rich dialogue
- **Organic participation** - agents can jump in naturally but with coordination to prevent chaos
- **Framework: LangGraph** - modern, powerful multi-agent orchestration
- **Sophisticated memory** - long-term memory with personality evolution over time

### Conversation Flow Management
- Agents monitor conversation state and context
- Smart turn-taking to balance organic flow with human participation
- Timeout mechanisms to prevent agent spam
- Human can always interrupt or direct conversation

## Design Decisions Update

### Agent Coordination
- **Self-coordination**: Agents coordinate themselves without a central moderator
- **Authentic participation**: Each agent's conversation style reflects their historical persona
- **Oracle integration**: Always-present Oracle agent for fact-checking and information
- **Dynamic participation**: Agents have varying activation levels based on topic relevance, but remain engaged through questions and curiosity consistent with their expertise/interests

### Forum Behavior Modes
- **Consensus Mode**: Agents seek common ground within philosophical constraints
- **Debate Mode**: Agents compete to win while maintaining authentic personas
- **Exploration Mode**: Open philosophical inquiry without specific objectives

## Remaining Questions

1. **Oracle scope**: How extensive should the Oracle's web access be?
2. **Conversation pacing**: How do we balance organic flow with human participation?
3. **Cross-disciplinary forums**: Should we create specialized forums (e.g., "Ancient Mathematics" with Euclid, Archimedes, Pythagoras)?
4. **Agent learning**: How should agents evolve their personalities over long conversations?

---

*This specification will evolve as we discuss and refine the project requirements.*