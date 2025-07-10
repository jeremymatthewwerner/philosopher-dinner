"""
Command line interface for the philosopher dinner forum.
Provides a rich terminal experience for conversations with AI philosophers.
"""
import sys
from typing import Dict, Any, List
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available, using basic CLI")

from ..forum.graph import PhilosopherForum
from ..forum.state import ForumConfig, ForumMode, Message, MessageType


class PhilosopherCLI:
    """
    Command line interface for philosopher conversations.
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.forum = None
        self.current_state = None
    
    def start(self):
        """Start the CLI application"""
        self._print_welcome()
        
        # Create or select forum
        forum_config = self._setup_forum()
        self.forum = PhilosopherForum(forum_config)
        
        # Start conversation
        self._run_conversation()
    
    def _print_welcome(self):
        """Print welcome message"""
        if self.console:
            welcome_panel = Panel(
                "[bold blue]Welcome to the Philosopher Dinner![/bold blue]\n\n"
                "Engage in deep philosophical discussions with AI agents\n"
                "embodying famous philosophers and thinkers.\n\n"
                "[italic]Type 'quit' to exit, 'help' for commands[/italic]",
                title="🏛️ Philosopher Dinner",
                border_style="blue"
            )
            self.console.print(welcome_panel)
        else:
            print("=" * 50)
            print("WELCOME TO THE PHILOSOPHER DINNER")
            print("=" * 50)
            print("Engage in philosophical discussions with AI philosophers")
            print("Type 'quit' to exit")
            print()
    
    def _setup_forum(self) -> ForumConfig:
        """Set up forum configuration"""
        if self.console:
            self.console.print("\n[bold]Forum Setup[/bold]")
        else:
            print("\nForum Setup")
        
        # For now, create a simple default forum
        forum_config = ForumConfig(
            forum_id="default_forum",
            name="Ancient Wisdom Forum",
            description="A place for philosophical discourse with ancient thinkers",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],  # Start with just Socrates
            created_at=datetime.now(),
            settings={}
        )
        
        if self.console:
            self.console.print(f"Created forum: [green]{forum_config['name']}[/green]")
            self.console.print(f"Mode: [yellow]{forum_config['mode'].value}[/yellow]")
            self.console.print(f"Participants: [cyan]{', '.join(forum_config['participants'])}[/cyan]")
        else:
            print(f"Created forum: {forum_config['name']}")
            print(f"Participants: {', '.join(forum_config['participants'])}")
        
        return forum_config
    
    def _run_conversation(self):
        """Main conversation loop"""
        if self.console:
            self.console.print("\n[bold green]Starting conversation...[/bold green]")
        else:
            print("\nStarting conversation...")
        
        # Get initial message
        initial_message = self._get_user_input("What would you like to discuss? ")
        
        if not initial_message or initial_message.lower() in ['quit', 'exit']:
            return
        
        # Handle help command during initial setup
        if initial_message.lower() == 'help':
            self._show_help()
            return self._run_conversation()  # Restart conversation after help
        
        # Start the conversation
        try:
            self.current_state = self.forum.start_conversation(initial_message)
            self._display_conversation()
            
            # Main conversation loop
            while True:
                user_input = self._get_user_input("\nYour response: ")
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit']:
                    self._print_goodbye()
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                # Continue conversation
                self.current_state = self.forum.continue_conversation(
                    self.current_state, 
                    user_input
                )
                self._display_conversation()
                
        except KeyboardInterrupt:
            self._print_goodbye()
        except Exception as e:
            print(f"Error: {e}")
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _display_conversation(self):
        """Display the current conversation state"""
        if not self.current_state or not self.current_state.get("messages"):
            return
        
        # Show only recent messages (last 5)
        recent_messages = self.current_state["messages"][-5:]
        
        if self.console:
            self._display_rich_conversation(recent_messages)
        else:
            self._display_simple_conversation(recent_messages)
    
    def _display_rich_conversation(self, messages: List[Message]):
        """Display conversation using Rich formatting"""
        for message in messages:
            # Create speaker label
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
            
            # Format timestamp
            timestamp = message["timestamp"].strftime("%H:%M:%S")
            
            # Create message panel
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
        """Display conversation using simple text formatting"""
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
    
    def _get_user_input(self, prompt: str) -> str:
        """Get user input with proper prompting"""
        if self.console:
            return Prompt.ask(prompt).strip()
        else:
            try:
                return input(prompt).strip()
            except EOFError:
                return "quit"
    
    def _show_help(self):
        """Show help information"""
        if self.console:
            help_text = """
[bold]Available Commands:[/bold]
• [cyan]help[/cyan] - Show this help message
• [cyan]quit[/cyan] or [cyan]exit[/cyan] - Exit the conversation
• Just type your message to continue the philosophical discussion!

[bold]Tips:[/bold]
• Ask questions to engage the philosophers
• Challenge their ideas and see how they respond
• Explore different philosophical topics
            """
            self.console.print(Panel(help_text, title="Help", border_style="yellow"))
        else:
            print("\nAvailable Commands:")
            print("  help - Show this help message")
            print("  quit or exit - Exit the conversation")
            print("\nJust type your message to continue the discussion!")
    
    def _print_goodbye(self):
        """Print goodbye message"""
        if self.console:
            goodbye = Panel(
                "[bold]Thank you for joining the philosophical discussion![/bold]\n\n"
                "Remember: 'The unexamined life is not worth living' - Socrates",
                title="Farewell",
                border_style="magenta"
            )
            self.console.print(goodbye)
        else:
            print("\nThank you for the philosophical discussion!")
            print("Remember: 'The unexamined life is not worth living' - Socrates")


def main():
    """Main entry point for the CLI"""
    cli = PhilosopherCLI()
    cli.start()


if __name__ == "__main__":
    main()