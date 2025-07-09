# Claude Context Memory

## Project: Philosopher Dinner
Multi-agent philosophy forum using LangGraph where AI agents embody famous philosophers, mathematicians, and thinkers to engage in group discussions.

## Current Progress
- ✅ Created specifications (SPECIFICATION.md, PROJECT_SPEC.md)
- ✅ Researched LangGraph multi-agent patterns (LANGGRAPH_RESEARCH.md)
- ✅ Set up GitHub repo: https://github.com/jeremymatthewwerner/philosopher-dinner
- ✅ Configured development environment (VS Code, venv, requirements.txt)
- ✅ Configured Claude Code settings for maximum permissions
- ✅ Designed system architecture (ARCHITECTURE.md)
- ✅ Built core LangGraph structure with state management
- ✅ Implemented Socrates agent with authentic personality and Socratic method
- ✅ Created LangGraph orchestrator for conversation flow
- ✅ Built CLI interface for human-agent interaction
- ✅ Tested basic functionality - all core components working!
- 🔄 **NEXT**: Install dependencies and test full LangGraph integration

## Key Design Decisions
- **Framework**: LangGraph for multi-agent coordination
- **Agents**: 3-5 philosophers per forum + Oracle agent for fact-checking
- **Participation**: Organic with smart coordination, topic-based activation
- **Memory**: ChromaDB for long-term storage + conversation memory
- **Forum Modes**: Consensus, Debate, or Exploration
- **Personas**: Historical figures, schools of thought, cross-disciplinary thinkers

## Technical Stack
- LangGraph: Graph-based multi-agent orchestration
- ChromaDB: Local vector database for memory
- MCP: Tool access and research
- Python CLI: Rich terminal interface

## Current Session Context
Working on system architecture design after completing research and specifications. User prefers maximum automation/permissions in Claude Code settings.