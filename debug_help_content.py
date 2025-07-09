#!/usr/bin/env python3
"""
Debug the help content to see what's actually being displayed
"""

import sys
import os
from unittest.mock import patch

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from philosopher_dinner.cli.interface import PhilosopherCLI

def debug_help_content():
    """Debug what help actually displays"""
    
    print("🔍 DEBUGGING HELP CONTENT")
    print("=" * 40)
    
    cli = PhilosopherCLI()
    
    if cli.console:
        print("Testing with Rich...")
        with patch.object(cli.console, 'print') as mock_print:
            cli._show_help()
            
            if mock_print.called:
                call_args = mock_print.call_args[0][0]
                print(f"Help content type: {type(call_args)}")
                print(f"Help content: {repr(call_args)}")
                print(f"Help content str: {str(call_args)}")
                
                # Check what's in the Panel
                if hasattr(call_args, 'renderable'):
                    print(f"Panel renderable: {call_args.renderable}")
                    
            else:
                print("Print was not called!")
    else:
        print("Rich not available")
    
    print("\nTesting without Rich...")
    cli_no_rich = PhilosopherCLI()
    cli_no_rich.console = None
    
    from io import StringIO
    captured_output = StringIO()
    
    with patch('sys.stdout', captured_output):
        cli_no_rich._show_help()
    
    output = captured_output.getvalue()
    print(f"No-Rich output: {repr(output)}")

if __name__ == "__main__":
    debug_help_content()