#!/usr/bin/env python3
"""
Test the help command bug fix
"""

import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.cli.interface import PhilosopherCLI

def test_help_command_fixed():
    """Test that help command now works correctly"""
    
    print("🔧 TESTING HELP COMMAND FIX")
    print("=" * 40)
    
    # Test 1: Help command with Rich
    print("\n1. Testing help with Rich...")
    cli = PhilosopherCLI()
    
    if cli.console:
        with patch.object(cli.console, 'print') as mock_print:
            cli._show_help()
            
            # Check that print was called
            assert mock_print.called, "Help should call console.print"
            
            # Check the content
            call_args = mock_print.call_args[0][0]
            
            # For Rich Panel, check the renderable content
            if hasattr(call_args, 'renderable'):
                help_content = str(call_args.renderable)
            else:
                help_content = str(call_args)
            
            assert "help" in help_content.lower(), "Help should mention 'help' command"
            assert "quit" in help_content.lower(), "Help should mention 'quit' command"
            assert "exit" in help_content.lower(), "Help should mention 'exit' command"
            
            print("  ✅ Help displays correctly with Rich")
    else:
        print("  ⚠️  Rich not available, skipping Rich test")
    
    # Test 2: Help command without Rich
    print("\n2. Testing help without Rich...")
    cli_no_rich = PhilosopherCLI()
    cli_no_rich.console = None
    
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli_no_rich._show_help()
    
    output = captured_output.getvalue()
    
    assert len(output) > 0, "Help should produce output"
    assert "help" in output.lower(), "Help should mention 'help' command"
    assert "quit" in output.lower(), "Help should mention 'quit' command"
    
    print("  ✅ Help displays correctly without Rich")
    
    # Test 3: Help command in conversation flow
    print("\n3. Testing help in conversation flow...")
    
    cli = PhilosopherCLI()
    
    # Mock the forum setup and other methods to isolate help testing
    with patch.object(cli, '_setup_forum') as mock_setup, \
         patch.object(cli, 'forum', MagicMock()), \
         patch.object(cli, '_show_help') as mock_show_help:
        
        # Simulate user typing 'help' then 'quit'
        with patch('builtins.input', side_effect=['help', 'quit']):
            with patch('builtins.print'):  # Suppress output
                try:
                    cli._run_conversation()
                except SystemExit:
                    pass  # Expected when quitting
        
        # Check that help was called
        assert mock_show_help.called, "Help should be called when user types 'help'"
        print("  ✅ Help command handled in conversation flow")
    
    print("\n🎉 ALL HELP TESTS PASSED!")
    print("The help command bug has been fixed!")

if __name__ == "__main__":
    test_help_command_fixed()