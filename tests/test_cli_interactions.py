#!/usr/bin/env python3
"""
Test CLI interactions and user commands.
Catches bugs like the 'help' command issue.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from philosopher_dinner.cli.interface import PhilosopherCLI


class TestCLIInteractions:
    """Test CLI user interaction scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.cli = PhilosopherCLI()
    
    def test_help_command_functionality(self):
        """Test that help command actually shows help"""
        
        # Mock console output
        with patch.object(self.cli, 'console') as mock_console:
            # Mock the console.print method
            mock_console.print = MagicMock()
            
            # Call show_help method
            self.cli._show_help()
            
            # Verify help was displayed
            assert mock_console.print.called, "Help should display content"
            
            # Get the call arguments
            call_args = mock_console.print.call_args[0]
            panel_obj = call_args[0] if call_args else None
            
            # For Rich Panel, check the renderable content
            if panel_obj and hasattr(panel_obj, 'renderable'):
                help_content = str(panel_obj.renderable)
            else:
                help_content = str(panel_obj) if panel_obj else ""
            
            # Verify help contains expected information
            assert "help" in help_content.lower(), "Help should mention 'help' command"
            assert "quit" in help_content.lower(), "Help should mention 'quit' command" 
            assert "exit" in help_content.lower(), "Help should mention 'exit' command"
    
    def test_help_command_without_rich(self):
        """Test help command when Rich library isn't available"""
        
        # Create CLI without Rich
        cli_no_rich = PhilosopherCLI()
        cli_no_rich.console = None
        
        # Capture stdout
        captured_output = StringIO()
        
        with patch('sys.stdout', captured_output):
            cli_no_rich._show_help()
        
        output = captured_output.getvalue()
        
        # Verify basic help is shown even without Rich
        assert "help" in output.lower(), "Help should work without Rich"
        assert "quit" in output.lower(), "Help should mention quit command"
    
    def test_user_input_validation(self):
        """Test handling of various user inputs"""
        
        # Test empty input
        with patch('builtins.input', return_value=''):
            result = self.cli._get_user_input("Test: ")
            assert result == "", "Empty input should return empty string"
        
        # Test whitespace input  
        with patch('builtins.input', return_value='   '):
            result = self.cli._get_user_input("Test: ")
            assert result == "", "Whitespace should be stripped to empty"
        
        # Test normal input
        with patch('builtins.input', return_value='hello world'):
            result = self.cli._get_user_input("Test: ")
            assert result == "hello world", "Normal input should be preserved"
        
        # Test EOFError handling
        with patch('builtins.input', side_effect=EOFError):
            result = self.cli._get_user_input("Test: ")
            assert result == "quit", "EOFError should return 'quit'"
    
    def test_quit_command_variations(self):
        """Test different ways to quit the application"""
        
        quit_commands = ['quit', 'exit', 'QUIT', 'EXIT', 'Quit', 'Exit']
        
        for cmd in quit_commands:
            # Mock the conversation setup to avoid actual forum creation
            with patch.object(self.cli, '_setup_forum'), \
                 patch.object(self.cli, 'forum'), \
                 patch('builtins.input', side_effect=[cmd]):
                
                # Mock print functions to avoid output
                with patch('builtins.print'), \
                     patch.object(self.cli, '_print_goodbye'):
                    
                    try:
                        self.cli._run_conversation()
                    except SystemExit:
                        pass  # Expected for quit commands
    
    def test_conversation_flow_commands(self):
        """Test special commands during conversation"""
        
        # Mock forum and state
        mock_forum = MagicMock()
        mock_state = {"messages": [], "session_id": "test"}
        
        with patch.object(self.cli, 'forum', mock_forum), \
             patch.object(self.cli, 'current_state', mock_state), \
             patch.object(self.cli, '_setup_forum'), \
             patch('builtins.input', side_effect=['help', 'quit']):
            
            # Mock methods to avoid actual output
            with patch.object(self.cli, '_show_help') as mock_help, \
                 patch.object(self.cli, '_print_goodbye'), \
                 patch('builtins.print'):
                
                try:
                    self.cli._run_conversation()
                except SystemExit:
                    pass
                
                # Verify help was called
                mock_help.assert_called_once()


class TestCLIErrorHandling:
    """Test error handling scenarios"""
    
    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of Ctrl+C"""
        
        cli = PhilosopherCLI()
        
        with patch.object(cli, '_setup_forum'), \
             patch('builtins.input', side_effect=KeyboardInterrupt):
            
            with patch.object(cli, '_print_goodbye') as mock_goodbye:
                cli._run_conversation()
                mock_goodbye.assert_called_once()
    
    def test_import_error_handling(self):
        """Test behavior when dependencies are missing"""
        
        # This would test the RICH_AVAILABLE flag behavior
        # For now, we verify the flag exists and works
        from philosopher_dinner.cli.interface import RICH_AVAILABLE
        
        assert isinstance(RICH_AVAILABLE, bool), "RICH_AVAILABLE should be boolean"


class TestConversationState:
    """Test conversation state management"""
    
    def test_empty_conversation_display(self):
        """Test displaying conversation with no messages"""
        
        cli = PhilosopherCLI()
        cli.current_state = None
        
        # Should not crash when displaying empty conversation
        with patch('builtins.print'):
            cli._display_conversation()
    
    def test_conversation_with_messages(self):
        """Test displaying conversation with messages"""
        
        from philosopher_dinner.forum.state import Message, MessageType
        from datetime import datetime
        
        cli = PhilosopherCLI()
        
        # Create test messages
        test_messages = [
            Message(
                id="test-1",
                sender="human", 
                content="Test question",
                message_type=MessageType.HUMAN,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            ),
            Message(
                id="test-2",
                sender="socrates",
                content="Test response", 
                message_type=MessageType.AGENT,
                timestamp=datetime.now(),
                thinking="Test thinking",
                metadata={"agent_name": "Socrates"}
            )
        ]
        
        cli.current_state = {"messages": test_messages}
        
        # Should not crash when displaying messages
        with patch('builtins.print'):
            cli._display_conversation()


def run_cli_tests():
    """Run all CLI tests and report results"""
    
    print("🧪 RUNNING CLI INTERACTION TESTS")
    print("=" * 50)
    
    test_results = {
        "passed": 0,
        "failed": 0, 
        "errors": []
    }
    
    # Test classes to run
    test_classes = [
        TestCLIInteractions(),
        TestCLIErrorHandling(), 
        TestConversationState()
    ]
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 Testing {class_name}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                # Setup if needed
                if hasattr(test_class, 'setup_method'):
                    test_class.setup_method()
                
                # Run test
                test_method = getattr(test_class, method_name)
                test_method()
                
                print(f"  ✅ {method_name}")
                test_results["passed"] += 1
                
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                test_results["failed"] += 1
                test_results["errors"].append(f"{class_name}.{method_name}: {e}")
    
    # Report results
    print(f"\n📊 TEST RESULTS:")
    print(f"  ✅ Passed: {test_results['passed']}")
    print(f"  ❌ Failed: {test_results['failed']}")
    
    if test_results["errors"]:
        print(f"\n🐛 ERRORS FOUND:")
        for error in test_results["errors"]:
            print(f"  • {error}")
    
    return test_results


if __name__ == "__main__":
    run_cli_tests()