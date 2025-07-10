"""
Simplified Forum Management CLI (No LangGraph dependency)
Multi-forum interface for immediate testing while LangGraph installs.
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
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available, using basic CLI")

from ..forum.database import ForumDatabase, ForumMetadata
from ..forum.state import ForumMode, Message, MessageType
from ..agents.forum_creator import ForumCreationAgent
from ..agents.agent_factory import AgentFactory
from ..search.semantic_search import SemanticForumSearch


class SimpleForumManagerCLI:
    """
    Simplified multi-forum CLI that works without LangGraph.
    Demonstrates all the forum management features.
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.db = ForumDatabase()
        self.search_engine = SemanticForumSearch(self.db)
        self.forum_creator = ForumCreationAgent()
        
        # Current session state
        self.current_forum_id = None
        self.current_user = "user"
        
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
        """Start the simplified CLI application"""
        self._print_welcome()
        
        while True:
            try:
                if self.current_forum_id:
                    # In a forum - simple conversation mode
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
        """Print welcome message"""
        if self.console:
            welcome_text = """[bold blue]🏛️ Philosopher Dinner - Forum Manager[/bold blue]
[dim](Simplified version - install LangGraph for full AI conversations)[/dim]

[bold]Multi-Forum Philosophy Platform[/bold]

Test the new forum management system! Create forums, join discussions, 
and use semantic search to discover philosophical conversations.

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
            print("PHILOSOPHER DINNER - FORUM MANAGER (SIMPLIFIED)")
            print("=" * 60)
            print("Commands: create-forum, list-forums, join-forum, search-forums, help, quit")
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
        
        # Start interactive creation
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
                self._finalize_forum_creation()
                break
    
    def _finalize_forum_creation(self):
        """Finalize forum creation"""
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
            
            # Test agent creation (show spinning indicator)
            if metadata.participants:
                self._display_message("🤖 Creating philosopher agents...")
                self._test_agent_creation(metadata.participants)
            
            if self._confirm("Would you like to join this forum now?"):
                self._join_forum_by_id(forum_id)
        else:
            self._display_error_message("❌ Failed to create forum")
    
    def _test_agent_creation(self, participants: List[str]):
        """Test that agents can be created for the forum participants"""
        from ..agents.agent_factory import AgentFactory
        
        factory = AgentFactory()
        created_agents = []
        
        for participant_id in participants:
            if participant_id != "oracle":  # Skip oracle for now
                try:
                    if self.console:
                        self.console.print(f"  🧠 Creating {participant_id.replace('_', ' ').title()}...")
                    else:
                        print(f"  Creating {participant_id}...")
                    
                    agent = factory.create_agent(participant_id)
                    if agent:
                        created_agents.append(agent.name)
                    else:
                        if self.console:
                            self.console.print(f"  ⚠️ Could not create agent for {participant_id}")
                        else:
                            print(f"  Warning: Could not create {participant_id}")
                except Exception as e:
                    if self.console:
                        self.console.print(f"  ❌ Error creating {participant_id}: {e}")
                    else:
                        print(f"  Error creating {participant_id}: {e}")
        
        if created_agents:
            if self.console:
                self.console.print(f"✅ Successfully created agents: {', '.join(created_agents)}")
            else:
                print(f"Successfully created: {', '.join(created_agents)}")
        else:
            if self.console:
                self.console.print("⚠️ No agents could be created. Forum will work but without AI responses.")
            else:
                print("Warning: No agents created.")
    
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
        
        # Set as current forum
        self.current_forum_id = forum_id
        
        # Display join message
        self._display_forum_join_message(metadata)
        
        # Show summary if available
        summary = self.db.get_forum_summary(forum_id, "brief")
        if summary:
            self._display_forum_summary(summary)
        else:
            self._display_message("This forum is just getting started!")
    
    def _display_forum_join_message(self, metadata: ForumMetadata):
        """Display message when joining a forum"""
        participants = [p.replace("_", " ").title() for p in metadata.participants if p != "oracle"]
        
        if self.console:
            join_text = f"""[bold green]📍 Joined Forum: {metadata.name}[/bold green]

[bold]Participants:[/bold] {', '.join(participants)}
[bold]Mode:[/bold] {metadata.mode.value.title()}
[bold]Topic:[/bold] {metadata.description}

[dim]Note: This is the simplified interface. Install LangGraph for full AI conversations.
You can still test forum management features![/dim]

[italic]Type messages to add to the discussion, or 'leave-forum' to exit.[/italic]"""
            
            self.console.print(Panel(join_text, border_style="green"))
        else:
            print(f"\n--- Joined Forum: {metadata.name} ---")
            print(f"Participants: {', '.join(participants)}")
            print(f"Mode: {metadata.mode.value.title()}")
    
    def _display_forum_summary(self, summary: str):
        """Display forum summary"""
        if self.console:
            summary_panel = Panel(
                summary,
                title="📜 Forum Summary",
                border_style="blue"
            )
            self.console.print(summary_panel)
        else:
            print(f"--- Forum Summary ---")
            print(summary)
            print("-" * 40)
    
    def _handle_leave_forum(self, args: List[str]):
        """Handle leave forum command"""
        if not self.current_forum_id:
            self._display_message("You are not currently in a forum.")
            return
        
        # Update database
        self.db.leave_forum(self.current_forum_id, self.current_user)
        
        # Clear current forum
        forum_name = self.db.get_forum(self.current_forum_id).name
        self.current_forum_id = None
        
        self._display_success_message(f"✅ Left forum: {forum_name}")
    
    def _handle_delete_forum(self, args: List[str]):
        """Handle delete forum command"""
        if not args:
            self._display_error_message("Please specify a forum ID: delete-forum <id>")
            return
        
        forum_id = args[0]
        metadata = self.db.get_forum(forum_id)
        if not metadata:
            self._display_error_message(f"Forum '{forum_id}' not found")
            return
        
        if not self._confirm(f"Are you sure you want to delete '{metadata.name}'?"):
            return
        
        if self.db.delete_forum(forum_id, self.current_user):
            self._display_success_message(f"✅ Forum '{metadata.name}' deleted")
            if self.current_forum_id == forum_id:
                self.current_forum_id = None
        else:
            self._display_error_message("❌ Failed to delete forum (you must be the creator)")
    
    def _handle_search_forums(self, args: List[str]):
        """Handle search forums command"""
        if not args:
            query = self._get_user_input("Enter search query: ")
        else:
            query = " ".join(args)
        
        if not query:
            return
        
        # Use semantic search
        results = self.search_engine.search(query, user=self.current_user, max_results=10)
        
        if not results:
            analytics = self.search_engine.get_search_analytics(query)
            suggestions = self.search_engine.suggest_search_terms(query)
            self._display_no_results_with_suggestions(query, analytics, suggestions)
            return
        
        self._display_search_results(results, query)
    
    def _display_search_results(self, results: List, query: str):
        """Display search results"""
        if self.console:
            table = Table(title=f"🔍 Search Results for '{query}'")
            table.add_column("ID", style="cyan")
            table.add_column("Forum", style="bold")
            table.add_column("Relevance", style="yellow")
            table.add_column("Participants", style="green")
            
            for result in results:
                confidence_pct = int(result.confidence * 100)
                confidence_display = f"{confidence_pct}%"
                
                participants = [p.replace("_", " ").title() for p in result.forum.participants[:3] if p != "oracle"]
                participants_str = ", ".join(participants)
                
                table.add_row(
                    result.forum.forum_id,
                    result.forum.name[:40],
                    confidence_display,
                    participants_str
                )
            
            self.console.print(table)
        else:
            print(f"\nSearch results for '{query}':")
            for result in results:
                print(f"ID: {result.forum.forum_id}")
                print(f"Forum: {result.forum.name}")
                print(f"Relevance: {int(result.confidence * 100)}%")
                print("-" * 40)
    
    def _display_no_results_with_suggestions(self, query: str, analytics: Dict, suggestions: List[str]):
        """Display no results with suggestions"""
        if self.console:
            text = f"No forums found for '{query}'\n\n"
            if suggestions:
                text += "Try: " + ", ".join(suggestions[:3])
            self.console.print(Panel(text, title="Search Results", border_style="yellow"))
        else:
            print(f"No forums found for '{query}'")
            if suggestions:
                print("Try:", ", ".join(suggestions[:3]))
    
    def _run_forum_conversation(self):
        """Simple conversation mode (no AI responses)"""
        if self.console:
            prompt_text = f"[bold blue]💬[/bold blue] Message"
        else:
            prompt_text = "Message"
        
        user_input = self._get_user_input(prompt_text + ": ").strip()
        
        if not user_input:
            return
        
        if user_input.lower() == "leave-forum":
            self._handle_leave_forum([])
            return
        elif user_input.lower() == "help":
            self._display_forum_help()
            return
        elif user_input.lower() in ["quit", "exit"]:
            self._handle_quit([])
            return
        
        # Add user message to database
        message = Message(
            id=str(uuid.uuid4()),
            sender=self.current_user,
            content=user_input,
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        self.db.add_message(self.current_forum_id, message)
        
        self._display_success_message("✅ Message added to forum discussion!")
        self._display_message("[dim]Install LangGraph to see AI philosopher responses[/dim]")
    
    def _display_forum_help(self):
        """Display forum help"""
        help_text = """[bold]Forum Commands:[/bold]
• Type your message to add to the discussion
• [cyan]leave-forum[/cyan] - Leave the current forum
• [cyan]help[/cyan] - Show this help
• [cyan]quit[/cyan] - Exit the application"""
        
        if self.console:
            self.console.print(Panel(help_text, title="Help", border_style="yellow"))
        else:
            print("\nForum Commands:")
            print("  leave-forum - Leave current forum")
            print("  help - Show help")
            print("  quit - Exit")
    
    def _handle_help(self, args: List[str]):
        """Handle help command"""
        help_text = """[bold yellow]Forum Manager Commands:[/bold yellow]

[bold]Forum Management:[/bold]
• [cyan]create-forum[/cyan] - Create a new forum with guided assistance
• [cyan]list-forums[/cyan] - View all available forums
• [cyan]join-forum <id>[/cyan] - Join an existing forum
• [cyan]leave-forum[/cyan] - Leave the current forum
• [cyan]delete-forum <id>[/cyan] - Delete a forum (creators only)
• [cyan]search-forums <query>[/cyan] - Search forums by topic

[bold]Examples:[/bold]
• [dim]create-forum What is justice?[/dim]
• [dim]search-forums virtue ethics[/dim]
• [dim]join-forum abc123[/dim]

[italic]This is the simplified interface for testing forum management.
Install LangGraph for full AI philosopher conversations![/italic]"""
        
        if self.console:
            self.console.print(Panel(help_text, title="Help", border_style="yellow"))
        else:
            print("\nForum Manager Commands:")
            print("  create-forum - Create new forum")
            print("  list-forums - View forums")
            print("  join-forum <id> - Join forum")
            print("  search-forums <query> - Search forums")
    
    def _handle_quit(self, args: List[str]):
        """Handle quit command"""
        self._print_goodbye()
        sys.exit(0)
    
    def _handle_unknown_command(self, command: str, args: List[str]):
        """Handle unknown commands"""
        self._display_error_message(f"Unknown command: '{command}'. Type 'help' for available commands.")
    
    def _get_user_input(self, prompt: str) -> str:
        """Get user input"""
        if self.console:
            return Prompt.ask(prompt).strip()
        else:
            return input(f"{prompt}: ").strip()
    
    def _confirm(self, message: str) -> bool:
        """Get confirmation"""
        if self.console:
            return Confirm.ask(message)
        else:
            response = input(f"{message} (y/n): ").strip().lower()
            return response in ["y", "yes"]
    
    def _display_message(self, message: str):
        """Display message"""
        if self.console:
            self.console.print(message)
        else:
            print(message)
    
    def _display_success_message(self, message: str):
        """Display success message"""
        if self.console:
            self.console.print(f"[green]{message}[/green]")
        else:
            print(message)
    
    def _display_error_message(self, message: str):
        """Display error message"""
        if self.console:
            self.console.print(f"[red]{message}[/red]")
        else:
            print(f"Error: {message}")
    
    def _display_agent_message(self, agent_name: str, message: str):
        """Display agent message"""
        if self.console:
            panel = Panel(message, title=f"[bold green]{agent_name}[/bold green]", border_style="green")
            self.console.print(panel)
        else:
            print(f"\n{agent_name}:")
            print(message)
    
    def _print_goodbye(self):
        """Print goodbye message"""
        if self.console:
            goodbye = Panel(
                "[bold]Thank you for testing the Forum Management System![/bold]\n\n"
                "Install LangGraph to unlock full AI philosopher conversations.\n\n"
                "[italic]May your philosophical journey continue...[/italic]",
                title="Farewell",
                border_style="magenta"
            )
            self.console.print(goodbye)
        else:
            print("\nThank you for testing the Forum Management System!")


def main():
    """Main entry point for simplified CLI"""
    cli = SimpleForumManagerCLI()
    cli.start()


if __name__ == "__main__":
    main()