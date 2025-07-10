"""
Enhanced Forum Management CLI
Multi-forum interface with forum creation, navigation, and management commands.
"""
import sys
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available, using basic CLI")

from ..forum.graph import PhilosopherForum
from ..forum.state import ForumConfig, ForumMode, Message, MessageType
from ..forum.database import ForumDatabase, ForumMetadata
from ..agents.forum_creator import ForumCreationAgent
from ..agents.agent_factory import AgentFactory
from ..search.semantic_search import SemanticForumSearch


class ForumManagerCLI:
    """
    Enhanced CLI for multi-forum management and conversations.
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.db = ForumDatabase()
        self.agent_factory = AgentFactory()
        self.forum_creator = ForumCreationAgent()
        self.search_engine = SemanticForumSearch(self.db)
        
        # Current session state
        self.current_forum = None
        self.current_forum_state = None
        self.current_user = "user"  # Simple user identification
        self.active_forums = {}  # Cache of active forum instances
        
        # Command handlers
        self.commands = {
            "create-forum": self._handle_create_forum,
            "list-forums": self._handle_list_forums,
            "join-forum": self._handle_join_forum,
            "leave-forum": self._handle_leave_forum,
            "delete-forum": self._handle_delete_forum,
            "search-forums": self._handle_search_forums,
            "help": self._handle_help,
            "quit": self._handle_quit,
            "exit": self._handle_quit
        }
    
    def start(self):
        """Start the enhanced CLI application"""
        self._print_welcome()
        
        while True:
            try:
                if self.current_forum:
                    # In a forum - handle conversation
                    self._run_forum_conversation()
                else:
                    # In main menu - handle commands
                    self._run_main_menu()
            except KeyboardInterrupt:
                self._print_goodbye()
                break
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]Error: {e}[/red]")
                else:
                    print(f"Error: {e}")
    
    def _print_welcome(self):
        """Print enhanced welcome message"""
        if self.console:
            welcome_text = """[bold blue]🏛️ Philosopher Dinner - Forum Manager[/bold blue]

[bold]Multi-Forum Philosophy Platform[/bold]

Create and join philosophical forums with AI embodiments of history's greatest thinkers.
Each forum is a unique space for exploring ideas with carefully curated philosophers.

[bold yellow]Available Commands:[/bold yellow]
• [cyan]create-forum[/cyan] - Create a new philosophical forum
• [cyan]list-forums[/cyan] - View all available forums  
• [cyan]join-forum <id>[/cyan] - Join an existing forum
• [cyan]search-forums <query>[/cyan] - Search forums by topic
• [cyan]help[/cyan] - Show detailed help
• [cyan]quit[/cyan] - Exit the application

[italic]Type a command to get started![/italic]"""
            
            welcome_panel = Panel(
                welcome_text,
                title="🎓 Welcome",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(welcome_panel)
        else:
            print("=" * 60)
            print("PHILOSOPHER DINNER - FORUM MANAGER")
            print("=" * 60)
            print("Multi-forum philosophy platform")
            print("\nCommands: create-forum, list-forums, join-forum, search-forums, help, quit")
            print()
    
    def _run_main_menu(self):
        """Run the main menu command loop"""
        if self.console:
            prompt_text = "[bold green]φ[/bold green] Command"
        else:
            prompt_text = "Command"
        
        user_input = self._get_user_input(prompt_text + ": ").strip()
        
        if not user_input:
            return
        
        # Parse command and arguments
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle command
        if command in self.commands:
            self.commands[command](args)
        else:
            self._handle_unknown_command(command, args)
    
    def _handle_create_forum(self, args: List[str]):
        """Handle forum creation command"""
        if self.console:
            self.console.print("[bold green]🆕 Creating New Forum[/bold green]")
            self.console.print("Let me guide you through the process...\n")
        else:
            print("Creating new forum...")
        
        # Start interactive creation process
        if args:
            initial_input = " ".join(args)
        else:
            initial_input = self._get_user_input("What topic would you like to explore? ")
        
        # Use forum creation agent
        response = self.forum_creator.start_forum_creation(initial_input)
        self._display_agent_message("Forum Creator", response)
        
        # Continue creation dialog
        while True:
            user_input = self._get_user_input("Your response: ")
            
            if user_input.lower() in ["quit", "cancel", "exit"]:
                self._display_message("Forum creation cancelled.")
                return
            
            response, is_complete = self.forum_creator.continue_creation_dialog(user_input)
            self._display_agent_message("Forum Creator", response)
            
            if is_complete:
                # Extract forum details and create it
                self._finalize_forum_creation()
                break
    
    def _finalize_forum_creation(self):
        """Finalize forum creation with database storage"""
        # Get details from forum creator
        draft = self.forum_creator.forum_draft
        
        if not draft:
            self._display_message("Error: No forum details available")
            return
        
        # Generate unique forum ID
        forum_id = str(uuid.uuid4())[:8]
        
        # Create metadata
        metadata = ForumMetadata(
            forum_id=forum_id,
            name=f"Discussion: {draft.get('topic', 'Philosophy')[:40]}...",
            description=draft.get('description', 'A philosophical discussion'),
            mode=draft.get('mode', ForumMode.EXPLORATION),
            participants=draft.get('participants', []),
            created_at=datetime.now(),
            creator=self.current_user,
            tags=draft.get('topic_hints', []),
            is_private=False
        )
        
        # Save to database
        if self.db.create_forum(metadata):
            self._display_success_message(f"✅ Forum created successfully! ID: {forum_id}")
            
            # Ask if user wants to join immediately
            if self._confirm("Would you like to join this forum now?"):
                self._join_forum_by_id(forum_id)
        else:
            self._display_error_message("❌ Failed to create forum")
    
    def _handle_list_forums(self, args: List[str]):
        """Handle list forums command"""
        forums = self.db.list_forums(user=self.current_user, include_private=True)
        
        if not forums:
            self._display_message("No forums available. Use 'create-forum' to create one!")
            return
        
        if self.console:
            self._display_forums_table(forums)
        else:
            self._display_forums_simple(forums)
    
    def _display_forums_table(self, forums: List[ForumMetadata]):
        """Display forums in a rich table"""
        table = Table(title="🏛️ Available Forums")
        
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="bold")
        table.add_column("Mode", style="yellow")
        table.add_column("Participants", style="green")
        table.add_column("Messages", justify="right")
        table.add_column("Last Activity", style="dim")
        
        for forum in forums:
            participants_str = ", ".join([p.replace("_", " ").title() for p in forum.participants if p != "oracle"])
            if len(participants_str) > 30:
                participants_str = participants_str[:27] + "..."
            
            last_activity = forum.last_activity.strftime("%m/%d %H:%M")
            
            table.add_row(
                forum.forum_id,
                forum.name,
                forum.mode.value.title(),
                participants_str,
                str(forum.message_count),
                last_activity
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Use 'join-forum <ID>' to join a forum[/dim]")
    
    def _display_forums_simple(self, forums: List[ForumMetadata]):
        """Display forums in simple text format"""
        print("\nAvailable Forums:")
        print("-" * 60)
        
        for forum in forums:
            participants = ", ".join([p.replace("_", " ").title() for p in forum.participants if p != "oracle"])
            print(f"ID: {forum.forum_id}")
            print(f"Name: {forum.name}")
            print(f"Participants: {participants}")
            print(f"Messages: {forum.message_count}")
            print("-" * 60)
        
        print("\nUse 'join-forum <ID>' to join a forum")
    
    def _handle_join_forum(self, args: List[str]):
        """Handle join forum command"""
        if not args:
            self._display_error_message("Please specify a forum ID: join-forum <id>")
            return
        
        forum_id = args[0]
        self._join_forum_by_id(forum_id)
    
    def _join_forum_by_id(self, forum_id: str):
        """Join a forum by ID"""
        # Get forum metadata
        metadata = self.db.get_forum(forum_id)
        if not metadata:
            self._display_error_message(f"Forum '{forum_id}' not found")
            return
        
        # Join forum in database
        if not self.db.join_forum(forum_id, self.current_user):
            self._display_error_message("Failed to join forum")
            return
        
        # Create forum instance if not cached
        if forum_id not in self.active_forums:
            forum_config = self.db.get_forum_config(forum_id)
            if not forum_config:
                self._display_error_message("Failed to load forum configuration")
                return
            
            self.active_forums[forum_id] = PhilosopherForum(forum_config)
        
        # Set as current forum
        self.current_forum = self.active_forums[forum_id]
        self.current_forum_id = forum_id
        
        # Display join message and summary
        self._display_forum_join_message(metadata)
        
        # Load and display forum history summary
        self._display_forum_summary(forum_id)
    
    def _display_forum_join_message(self, metadata: ForumMetadata):
        """Display message when joining a forum"""
        participants = [p.replace("_", " ").title() for p in metadata.participants if p != "oracle"]
        
        if self.console:
            join_text = f"""[bold green]📍 Joined Forum: {metadata.name}[/bold green]

[bold]Participants:[/bold] {', '.join(participants)} + Oracle
[bold]Mode:[/bold] {metadata.mode.value.title()}
[bold]Topic:[/bold] {metadata.description}

[italic]You are now in the forum. Type messages to participate in the discussion.
Use 'leave-forum' to exit, or 'help' for more commands.[/italic]"""
            
            self.console.print(Panel(join_text, border_style="green"))
        else:
            print(f"\n--- Joined Forum: {metadata.name} ---")
            print(f"Participants: {', '.join(participants)}")
            print(f"Mode: {metadata.mode.value.title()}")
            print(f"Topic: {metadata.description}")
            print("\nYou can now participate in the discussion.")
    
    def _display_forum_summary(self, forum_id: str):
        """Display forum history summary"""
        # Get existing summary or generate one
        summary = self.db.get_forum_summary(forum_id, "brief")
        
        if not summary:
            # Generate summary from recent messages
            summary = self._generate_forum_summary(forum_id)
            if summary:
                self.db.save_forum_summary(forum_id, "brief", summary)
        
        if summary:
            if self.console:
                summary_panel = Panel(
                    summary,
                    title="📜 Forum Summary",
                    border_style="blue",
                    padding=(1, 1)
                )
                self.console.print(summary_panel)
            else:
                print(f"\n--- Forum Summary ---")
                print(summary)
                print("-" * 40)
    
    def _generate_forum_summary(self, forum_id: str) -> Optional[str]:
        """Generate a brief summary of the forum discussion"""
        messages = self.db.get_messages(forum_id, limit=20)
        
        if not messages:
            return "This forum is just getting started. Be the first to share your thoughts!"
        
        # Simple summary generation
        participants = set(msg["sender"] for msg in messages if msg["message_type"] == MessageType.AGENT)
        topics = self._extract_discussion_topics(messages)
        
        summary_parts = []
        summary_parts.append(f"This forum has {len(messages)} messages from {len(participants)} thinkers.")
        
        if topics:
            summary_parts.append(f"Main topics: {', '.join(topics[:3])}.")
        
        if messages:
            latest = messages[-1]
            summary_parts.append(f"Latest discussion from {latest['sender']}: \"{latest['content'][:100]}...\"")
        
        return " ".join(summary_parts)
    
    def _extract_discussion_topics(self, messages: List[Message]) -> List[str]:
        """Extract main topics from discussion"""
        # Simple keyword extraction
        philosophical_terms = ["justice", "truth", "virtue", "knowledge", "reality", "ethics", "freedom", "consciousness"]
        
        content = " ".join([msg["content"].lower() for msg in messages])
        found_topics = [term for term in philosophical_terms if term in content]
        
        return found_topics[:5]
    
    def _handle_leave_forum(self, args: List[str]):
        """Handle leave forum command"""
        if not self.current_forum:
            self._display_message("You are not currently in a forum.")
            return
        
        # Update database
        self.db.leave_forum(self.current_forum_id, self.current_user)
        
        # Clear current forum
        forum_name = self.db.get_forum(self.current_forum_id).name
        self.current_forum = None
        self.current_forum_state = None
        
        self._display_success_message(f"✅ Left forum: {forum_name}")
    
    def _handle_delete_forum(self, args: List[str]):
        """Handle delete forum command"""
        if not args:
            self._display_error_message("Please specify a forum ID: delete-forum <id>")
            return
        
        forum_id = args[0]
        
        # Get forum info
        metadata = self.db.get_forum(forum_id)
        if not metadata:
            self._display_error_message(f"Forum '{forum_id}' not found")
            return
        
        # Confirm deletion
        if not self._confirm(f"Are you sure you want to delete '{metadata.name}'? This cannot be undone."):
            return
        
        # Delete forum
        if self.db.delete_forum(forum_id, self.current_user):
            self._display_success_message(f"✅ Forum '{metadata.name}' deleted")
            
            # If we were in the deleted forum, leave it
            if self.current_forum and self.current_forum_id == forum_id:
                self.current_forum = None
                self.current_forum_state = None
        else:
            self._display_error_message("❌ Failed to delete forum (you must be the creator)")
    
    def _handle_search_forums(self, args: List[str]):
        """Handle search forums command with enhanced semantic search"""
        if not args:
            query = self._get_user_input("Enter search query: ")
        else:
            query = " ".join(args)
        
        if not query:
            return
        
        # Use semantic search engine
        search_results = self.search_engine.search(query, user=self.current_user, max_results=10)
        
        if not search_results:
            # Show search analytics and suggestions
            analytics = self.search_engine.get_search_analytics(query)
            suggestions = self.search_engine.suggest_search_terms(query)
            
            self._display_no_results_with_suggestions(query, analytics, suggestions)
            return
        
        # Display enhanced results
        if self.console:
            self._display_semantic_search_results(search_results, query)
        else:
            self._display_search_results_simple_semantic(search_results, query)
    
    def _display_search_results(self, results: List[Tuple[ForumMetadata, float]], query: str):
        """Display search results in rich format"""
        table = Table(title=f"🔍 Search Results for '{query}'")
        
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Relevance", style="yellow")
        table.add_column("Participants", style="green")
        table.add_column("Messages")
        
        for metadata, score in results:
            confidence = "🟢 High" if score > 0.7 else "🟡 Medium" if score > 0.4 else "🔴 Low"
            participants = ", ".join([p.replace("_", " ").title() for p in metadata.participants[:3] if p != "oracle"])
            
            table.add_row(
                metadata.forum_id,
                metadata.name[:40],
                confidence,
                participants,
                str(metadata.message_count)
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Use 'join-forum <ID>' to join a forum[/dim]")
    
    def _display_semantic_search_results(self, results: List, query: str):
        """Display enhanced semantic search results"""
        table = Table(title=f"🧠 Semantic Search Results for '{query}'")
        
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Forum", style="bold", width=30)
        table.add_column("Relevance", style="yellow", width=12)
        table.add_column("Match Type", style="green", width=12)
        table.add_column("Participants", style="blue", width=25)
        table.add_column("Snippets", style="dim", width=30)
        
        for result in results:
            # Confidence visualization
            confidence_pct = int(result.confidence * 100)
            if confidence_pct >= 80:
                confidence_display = f"🟢 {confidence_pct}%"
            elif confidence_pct >= 60:
                confidence_display = f"🟡 {confidence_pct}%"
            elif confidence_pct >= 40:
                confidence_display = f"🟠 {confidence_pct}%"
            else:
                confidence_display = f"🔴 {confidence_pct}%"
            
            # Participants display
            participants = [p.replace("_", " ").title() for p in result.forum.participants[:3] if p != "oracle"]
            participants_str = ", ".join(participants)
            if len(result.forum.participants) > 3:
                participants_str += "..."
            
            # Snippets display
            snippets_str = "; ".join(result.matching_snippets[:2])
            if len(snippets_str) > 30:
                snippets_str = snippets_str[:27] + "..."
            
            table.add_row(
                result.forum.forum_id,
                result.forum.name[:30] + ("..." if len(result.forum.name) > 30 else ""),
                confidence_display,
                result.relevance_type.title(),
                participants_str,
                snippets_str
            )
        
        self.console.print(table)
        
        # Show search analytics
        analytics = self.search_engine.get_search_analytics(query)
        if analytics["detected_concepts"] or analytics["mentioned_philosophers"]:
            self.console.print(f"\n[dim]🔍 Search Analysis:[/dim]")
            if analytics["detected_concepts"]:
                concepts = ", ".join(analytics["detected_concepts"].keys())
                self.console.print(f"[dim]📚 Concepts: {concepts}[/dim]")
            if analytics["mentioned_philosophers"]:
                philosophers = ", ".join([p.title() for p in analytics["mentioned_philosophers"]])
                self.console.print(f"[dim]👤 Philosophers: {philosophers}[/dim]")
        
        self.console.print(f"\n[dim]Use 'join-forum <ID>' to join a forum[/dim]")
    
    def _display_no_results_with_suggestions(self, query: str, analytics: Dict, suggestions: List[str]):
        """Display no results message with helpful suggestions"""
        if self.console:
            no_results_text = f"[yellow]No forums found matching '[bold]{query}[/bold]'[/yellow]\n\n"
            
            if analytics["detected_concepts"]:
                concepts = ", ".join(analytics["detected_concepts"].keys())
                no_results_text += f"[dim]I detected these concepts: {concepts}[/dim]\n"
            
            if suggestions:
                no_results_text += f"[bold]💡 Did you mean:[/bold]\n"
                for suggestion in suggestions[:5]:
                    no_results_text += f"• [cyan]{suggestion}[/cyan]\n"
                no_results_text += "\n"
            
            no_results_text += f"[bold]💭 Try these search strategies:[/bold]\n"
            no_results_text += f"• Search by philosopher: [cyan]'socrates justice'[/cyan]\n"
            no_results_text += f"• Search by concept: [cyan]'what is virtue'[/cyan]\n"
            no_results_text += f"• Search by topic: [cyan]'free will determinism'[/cyan]\n"
            no_results_text += f"• Create a new forum: [cyan]'create-forum {query}'[/cyan]"
            
            panel = Panel(no_results_text, title="Search Results", border_style="yellow")
            self.console.print(panel)
        else:
            print(f"No forums found matching '{query}'")
            if suggestions:
                print("Did you mean:", ", ".join(suggestions[:3]))
    
    def _display_search_results_simple_semantic(self, results: List, query: str):
        """Display semantic search results in simple format"""
        print(f"\nSemantic search results for '{query}':")
        print("-" * 60)
        
        for result in results:
            confidence_pct = int(result.confidence * 100)
            participants = ", ".join([p.replace("_", " ").title() for p in result.forum.participants[:3] if p != "oracle"])
            
            print(f"ID: {result.forum.forum_id}")
            print(f"Forum: {result.forum.name}")
            print(f"Relevance: {confidence_pct}% ({result.relevance_type})")
            print(f"Participants: {participants}")
            if result.matching_snippets:
                print(f"Matches: {'; '.join(result.matching_snippets[:2])}")
            print("-" * 60)
    
    def _display_search_results_simple(self, results: List[Tuple[ForumMetadata, float]], query: str):
        """Display search results in simple format"""
        print(f"\nSearch results for '{query}':")
        print("-" * 50)
        
        for metadata, score in results:
            confidence = "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
            participants = ", ".join([p.replace("_", " ").title() for p in metadata.participants[:3] if p != "oracle"])
            
            print(f"ID: {metadata.forum_id}")
            print(f"Name: {metadata.name}")
            print(f"Relevance: {confidence}")
            print(f"Participants: {participants}")
            print(f"Messages: {metadata.message_count}")
            print("-" * 50)
    
    def _run_forum_conversation(self):
        """Run conversation within a forum"""
        if self.console:
            prompt_text = f"[bold blue]🏛️[/bold blue] Message"
        else:
            prompt_text = "Message"
        
        user_input = self._get_user_input(prompt_text + ": ").strip()
        
        if not user_input:
            return
        
        # Check for forum commands
        if user_input.lower() == "leave-forum":
            self._handle_leave_forum([])
            return
        elif user_input.lower() == "help":
            self._display_forum_help()
            return
        elif user_input.lower() in ["quit", "exit"]:
            self._handle_quit([])
            return
        
        # Process as conversation message
        self._process_forum_message(user_input)
    
    def _process_forum_message(self, user_input: str):
        """Process a message within the forum"""
        try:
            # Start or continue conversation
            if not self.current_forum_state:
                self.current_forum_state = self.current_forum.start_conversation(user_input)
            else:
                self.current_forum_state = self.current_forum.continue_conversation(
                    self.current_forum_state, user_input
                )
            
            # Save messages to database
            self._save_forum_messages()
            
            # Display conversation
            self._display_conversation()
            
        except Exception as e:
            self._display_error_message(f"Error in conversation: {e}")
    
    def _save_forum_messages(self):
        """Save new messages to the database"""
        if not self.current_forum_state or not self.current_forum_state.get("messages"):
            return
        
        # Save each message (the database will handle duplicates)
        for message in self.current_forum_state["messages"]:
            self.db.add_message(self.current_forum_id, message)
    
    def _display_conversation(self):
        """Display the current conversation"""
        if not self.current_forum_state or not self.current_forum_state.get("messages"):
            return
        
        # Show recent messages
        recent_messages = self.current_forum_state["messages"][-3:]
        
        if self.console:
            self._display_rich_conversation(recent_messages)
        else:
            self._display_simple_conversation(recent_messages)
    
    def _display_rich_conversation(self, messages: List[Message]):
        """Display conversation using Rich formatting"""
        for message in messages:
            if message["message_type"] == MessageType.HUMAN:
                speaker = "[bold blue]You[/bold blue]"
                style = "blue"
            elif message["message_type"] == MessageType.AGENT:
                agent_name = message["metadata"].get("agent_name", message["sender"])
                speaker = f"[bold green]{agent_name}[/bold green]"
                style = "green"
            else:
                speaker = f"[bold yellow]{message['sender']}[/bold yellow]"
                style = "yellow"
            
            timestamp = message["timestamp"].strftime("%H:%M:%S")
            content = message["content"]
            
            if message.get("thinking"):
                content = f"[italic dim]{message['thinking']}[/italic dim]\n\n{content}"
            
            panel = Panel(
                content,
                title=f"{speaker} • {timestamp}",
                border_style=style,
                padding=(0, 1)
            )
            
            self.console.print(panel)
    
    def _display_simple_conversation(self, messages: List[Message]):
        """Display conversation using simple text"""
        for message in messages:
            timestamp = message["timestamp"].strftime("%H:%M:%S")
            
            if message["message_type"] == MessageType.HUMAN:
                speaker = "You"
            elif message["message_type"] == MessageType.AGENT:
                speaker = message["metadata"].get("agent_name", message["sender"])
            else:
                speaker = message["sender"]
            
            print(f"\n[{timestamp}] {speaker}:")
            
            if message.get("thinking"):
                print(f"  (thinking: {message['thinking']})")
            
            print(f"  {message['content']}")
    
    def _display_forum_help(self):
        """Display help for forum commands"""
        if self.console:
            help_text = """[bold]Forum Commands:[/bold]
• Type your message to participate in the discussion
• [cyan]leave-forum[/cyan] - Leave the current forum
• [cyan]help[/cyan] - Show this help
• [cyan]quit[/cyan] - Exit the application

[bold]Discussion Tips:[/bold]
• Ask questions to engage the philosophers
• Challenge ideas and see how they respond
• Explore different philosophical perspectives"""
            
            self.console.print(Panel(help_text, title="Help", border_style="yellow"))
        else:
            print("\nForum Commands:")
            print("  - Type your message to participate")
            print("  - leave-forum - Leave current forum")
            print("  - help - Show this help")
            print("  - quit - Exit application")
    
    def _handle_help(self, args: List[str]):
        """Handle help command"""
        if self.console:
            help_text = """[bold yellow]Philosopher Dinner Commands:[/bold yellow]

[bold]Forum Management:[/bold]
• [cyan]create-forum[/cyan] - Create a new philosophical forum
• [cyan]list-forums[/cyan] - View all available forums
• [cyan]join-forum <id>[/cyan] - Join an existing forum
• [cyan]leave-forum[/cyan] - Leave the current forum
• [cyan]delete-forum <id>[/cyan] - Delete a forum (creators only)
• [cyan]search-forums <query>[/cyan] - Search forums by topic

[bold]General:[/bold]
• [cyan]help[/cyan] - Show this help message
• [cyan]quit[/cyan] or [cyan]exit[/cyan] - Exit the application

[bold]Usage Examples:[/bold]
• [dim]create-forum What is justice?[/dim]
• [dim]join-forum abc123[/dim]
• [dim]search-forums ethics morality[/dim]

[italic]When in a forum, simply type messages to participate![/italic]"""
            
            self.console.print(Panel(help_text, title="Help", border_style="yellow"))
        else:
            print("\nPhilosopher Dinner Commands:")
            print("  create-forum - Create new forum")
            print("  list-forums - View available forums")
            print("  join-forum <id> - Join a forum")
            print("  leave-forum - Leave current forum")
            print("  delete-forum <id> - Delete a forum")
            print("  search-forums <query> - Search forums")
            print("  help - Show this help")
            print("  quit - Exit")
    
    def _handle_quit(self, args: List[str]):
        """Handle quit command"""
        if self.current_forum:
            if self._confirm("You are currently in a forum. Are you sure you want to quit?"):
                self._print_goodbye()
                sys.exit(0)
        else:
            self._print_goodbye()
            sys.exit(0)
    
    def _handle_unknown_command(self, command: str, args: List[str]):
        """Handle unknown commands"""
        self._display_error_message(f"Unknown command: '{command}'. Type 'help' for available commands.")
    
    def _get_user_input(self, prompt: str) -> str:
        """Get user input with proper prompting"""
        if self.console:
            return Prompt.ask(prompt).strip()
        else:
            try:
                return input(f"{prompt}: ").strip()
            except EOFError:
                return "quit"
    
    def _confirm(self, message: str) -> bool:
        """Get confirmation from user"""
        if self.console:
            return Confirm.ask(message)
        else:
            response = input(f"{message} (y/n): ").strip().lower()
            return response in ["y", "yes"]
    
    def _display_message(self, message: str):
        """Display a general message"""
        if self.console:
            self.console.print(message)
        else:
            print(message)
    
    def _display_success_message(self, message: str):
        """Display a success message"""
        if self.console:
            self.console.print(f"[green]{message}[/green]")
        else:
            print(message)
    
    def _display_error_message(self, message: str):
        """Display an error message"""
        if self.console:
            self.console.print(f"[red]{message}[/red]")
        else:
            print(f"Error: {message}")
    
    def _display_agent_message(self, agent_name: str, message: str):
        """Display a message from an agent"""
        if self.console:
            panel = Panel(
                message,
                title=f"[bold green]{agent_name}[/bold green]",
                border_style="green",
                padding=(1, 1)
            )
            self.console.print(panel)
        else:
            print(f"\n{agent_name}:")
            print(message)
            print()
    
    def _print_goodbye(self):
        """Print goodbye message"""
        if self.console:
            goodbye = Panel(
                "[bold]Thank you for exploring philosophy with us![/bold]\n\n"
                "Remember: 'The unexamined life is not worth living' - Socrates\n\n"
                "[italic]May your philosophical journey continue...[/italic]",
                title="Farewell from the Forum",
                border_style="magenta"
            )
            self.console.print(goodbye)
        else:
            print("\nThank you for the philosophical discussions!")
            print("Remember: 'The unexamined life is not worth living' - Socrates")


def main():
    """Main entry point for the enhanced CLI"""
    cli = ForumManagerCLI()
    cli.start()


if __name__ == "__main__":
    main()