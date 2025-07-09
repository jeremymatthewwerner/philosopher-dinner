# 🏛️ Philosopher Dinner

A multi-agent philosophy forum using LangGraph where AI agents embody famous philosophers, mathematicians, and thinkers to engage in group discussions with humans.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 What is Philosopher Dinner?

Philosopher Dinner creates authentic philosophical conversations between humans and AI agents that embody historical thinkers. Each agent maintains their unique personality, expertise, and debate style while engaging in real-time discussions about life's deepest questions.

### ✨ Key Features

- **🧠 Authentic Philosophers**: AI agents embody real historical figures with accurate personalities and methods
- **🗣️ Socratic Dialogue**: Experience the famous Socratic method of questioning and inquiry
- **🎭 Multiple Forums**: Create different conversation spaces with various philosophical themes
- **🔄 Dynamic Participation**: Agents decide when to engage based on topic relevance and personality
- **💭 Visible Thinking**: See each philosopher's internal reasoning process
- **📚 Long-term Memory**: Agents remember past conversations and evolve their relationships
- **🎯 Forum Modes**: Choose between consensus-seeking, debate, or open exploration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/jeremymatthewwerner/philosopher-dinner.git
cd philosopher-dinner

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start Your First Philosophical Conversation

```bash
# Have a personal chat with Socrates
python your_interactive_chat.py
```

### Run Tests

```bash
# Quick test suite (recommended)
python autotest.py --quick

# Comprehensive test suite
python autotest.py --full

# Or run manually
cd tests
python test_runner_simple.py
```

**Example conversation:**
```
🧑 You: What is the meaning of life?

🏛️ Socrates: When you speak of life, human, what exactly do you mean by that? 
          For it seems to me that the unexamined life is not worth living.

🧑 You: I think life's meaning comes from happiness.

🏛️ Socrates: That is interesting, human. But tell me, how do you know this 
          about happiness? Can we not be deceived about what we think brings joy?
```

## 📖 Available Experiences

### 🎭 Interactive Chat
**File:** `your_interactive_chat.py`
- Personal one-on-one dialogue with Socrates
- Real-time questioning and responses
- Natural conversation flow
- Type 'quit' to end

### 🔍 Demonstration Mode
**File:** `demo.py`
- Scripted conversation examples
- Shows Socrates' reasoning process
- Perfect for understanding the system

### 🧪 Debug Mode
**File:** `debug_interactive.py`
- Step-by-step system analysis
- Activation levels and decision making
- Technical insights into agent behavior

### 🌐 Inline Testing
**File:** `interactive_inline.py`
- Programmable conversation interface
- Custom dialogue scripting
- Integration testing

## 🏗️ Architecture

### Core Components

- **🎯 LangGraph Orchestrator**: Manages multi-agent conversation flow
- **🧠 Agent System**: Individual philosopher implementations with authentic personalities
- **💾 State Management**: Persistent conversation memory and context
- **🎨 CLI Interface**: Rich terminal experience with formatted dialogue
- **📊 Activation System**: Dynamic participation based on relevance and personality

### Current Philosophers

#### 🏛️ Socrates (470-399 BCE)
- **Specialty**: Moral philosophy, ethics, the Socratic method
- **Personality**: Curious (0.95), humble (0.9), persistent (0.8)
- **Method**: Questions assumptions, seeks definitions, admits ignorance
- **Signature**: "I know that I know nothing"

*Coming Soon: Aristotle, Kant, Nietzsche, and the Oracle agent for fact-checking*

## 🔧 Technical Details

### Built With

- **[LangGraph](https://langchain-ai.github.io/langgraph/)**: Multi-agent orchestration framework
- **[LangChain](https://langchain.com/)**: LLM application framework
- **[Rich](https://rich.readthedocs.io/)**: Beautiful terminal interfaces
- **[ChromaDB](https://www.trychroma.com/)**: Vector database for long-term memory *(planned)*
- **[Pydantic](https://pydantic.dev/)**: Data validation and settings management

### System Requirements

- **Memory**: 4GB+ RAM recommended
- **Storage**: 500MB for dependencies
- **Network**: Internet connection for LLM APIs *(when integrated)*

## 🎓 Educational Value

This project demonstrates cutting-edge concepts in:

- **Multi-Agent Systems**: Coordination and communication between AI agents
- **LangGraph Patterns**: State machines and conversation flow management
- **Personality Modeling**: Authentic historical character representation
- **Philosophical AI**: Using AI to explore deep questions and thinking methods
- **Dynamic Activation**: Context-aware agent participation
- **Memory Systems**: Long-term conversation persistence and evolution

## 🗺️ Roadmap

### Phase 1: Core Foundation ✅
- [x] Socrates agent with authentic Socratic method
- [x] LangGraph orchestration system
- [x] Interactive CLI interfaces
- [x] State management and memory
- [x] Testing and debugging tools

### Phase 2: Multi-Agent Expansion 🔄
- [ ] Aristotle agent (systematic philosophy)
- [ ] Oracle agent (fact-checking and information)
- [ ] Forum management system
- [ ] Multiple conversation modes

### Phase 3: Advanced Features 📋
- [ ] Kant agent (categorical imperatives)
- [ ] Nietzsche agent (existentialism, critiques)
- [ ] ChromaDB integration for persistent memory
- [ ] Web interface option
- [ ] Cross-disciplinary thinkers (mathematicians, economists)

### Phase 4: Production Features 📋
- [ ] Multi-user support
- [ ] Conversation export and sharing
- [ ] Educational curriculum integration
- [ ] Performance optimization
- [ ] Mobile-friendly interfaces

## 🤝 Contributing

We welcome contributions! Whether you're interested in:

- **🧠 Adding new philosophers** with authentic personalities
- **🔧 Improving the conversation engine**
- **🎨 Enhancing the user interface**
- **📚 Expanding educational features**
- **🐛 Bug fixes and optimizations**

### Development Setup

```bash
# Clone and setup
git clone https://github.com/jeremymatthewwerner/philosopher-dinner.git
cd philosopher-dinner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up automated testing
python autotest.py --setup

# Start development with auto-testing
python autotest.py --watch

# Or run tests manually
python autotest.py --quick
```

## 🤖 Automated Testing & CI/CD

### Continuous Integration Features

**🔄 Automatic Test Running:**
- **Pre-commit Hook**: Tests run automatically before each commit
- **File Watcher**: Tests run automatically when files change during development
- **GitHub Actions**: Tests run automatically on push/pull requests

**⚡ Quick Commands:**
```bash
# Set up pre-commit hook (run once)
python autotest.py --setup

# Development mode with auto-testing
python autotest.py --watch

# Run tests manually
python autotest.py --quick      # Fast test suite
python autotest.py --full       # Comprehensive tests
python autotest.py --test cli   # Specific test category

# Enhanced testing with GitHub issue tracking
python enhanced_test_runner.py

# Start issue monitoring agent
python issue_monitoring_agent.py --once    # Run once
python issue_monitoring_agent.py           # Continuous monitoring
```

**🧪 Test Categories:**
- **CLI Tests**: User interface and command handling
- **LangGraph Tests**: Conversation flow and agent coordination
- **Agent Tests**: Philosopher authenticity and behavior
- **Integration Tests**: Full system end-to-end testing

**📊 Regression Prevention:**
- Catches bugs before users encounter them
- Prevents infinite recursion issues
- Validates help command functionality
- Ensures conversation flow integrity

**🤖 Automated Bug Tracking:**
- Automatically files GitHub issues when tests fail
- Monitors issues and attempts automatic fixes
- Resolves issues when bugs are fixed
- Tracks bug lifecycle and resolution metrics

## 📚 Learn More

### Philosophy Resources
- [Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/)
- [Internet Encyclopedia of Philosophy](https://iep.utm.edu/)
- [The Socratic Method](https://en.wikipedia.org/wiki/Socratic_method)

### Technical Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)
- [Conversational AI](https://en.wikipedia.org/wiki/Conversational_artificial_intelligence)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Plato** and other ancient sources for preserving Socratic dialogues
- **LangChain team** for the powerful LangGraph framework
- **Philosophy educators** worldwide who inspired this educational approach
- **Open source community** for the tools that made this possible

---

*"The unexamined life is not worth living."* - Socrates

**Start your philosophical journey today!** 🏛️✨

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/jeremymatthewwerner/philosopher-dinner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jeremymatthewwerner/philosopher-dinner/discussions)
- **Documentation**: This README and inline code comments

---

**Made with ❤️ for philosophy and AI education**