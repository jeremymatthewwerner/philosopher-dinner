#!/usr/bin/env python3
"""
REAL CLI execution tests that actually catch runtime failures
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_real_cli_startup():
    """Test that the CLI actually starts without errors"""
    
    print("🧪 Testing Real CLI Startup")
    print("=" * 50)
    
    # Test interface.py startup
    try:
        # Run the CLI as a module with a simple command and exit
        result = subprocess.run(
            [sys.executable, "-m", "philosopher_dinner.cli.interface"],
            input="help\nquit\n",
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode != 0:
            print(f"❌ CLI failed with return code: {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
            
        if "error" in result.stderr.lower() or "traceback" in result.stderr.lower():
            print(f"❌ CLI had errors:")
            print(result.stderr)
            return False
            
        print("✅ Basic CLI starts without errors")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ CLI timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run CLI: {e}")
        return False

def test_forum_join_and_message():
    """Test joining a forum and sending a message"""
    
    print("\n🧪 Testing Forum Join and Message")
    print("=" * 50)
    
    # First create a test forum
    from philosopher_dinner.forum.database import ForumDatabase
    from philosopher_dinner.forum.state import ForumConfig, ForumMode
    from datetime import datetime
    import uuid
    
    db = ForumDatabase()
    
    # Create a test forum
    test_forum_id = str(uuid.uuid4())[:8]
    forum_config = ForumConfig(
        forum_id=test_forum_id,
        name="Test Forum",
        description="Test forum for CLI testing",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche"],  # No 'user' or 'oracle'
        created_at=datetime.now(),
        settings={}
    )
    
    # Save to database
    from philosopher_dinner.forum.database import ForumMetadata
    
    metadata = ForumMetadata(
        forum_id=test_forum_id,
        name="Test Forum",
        description="Test forum for CLI testing", 
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche"],
        created_at=datetime.now(),
        creator="test_user",
        tags=[],
        is_private=False
    )
    
    db.create_forum(metadata)
    
    print(f"📝 Created test forum: {test_forum_id}")
    
    # Now test joining and sending message
    try:
        # Run forum CLI
        commands = f"join-forum {test_forum_id}\nwho is here?\nleave-forum\nquit\n"
        
        result = subprocess.run(
            [sys.executable, "-m", "philosopher_dinner.cli.forum_cli"],
            input=commands,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        output = result.stdout + result.stderr
        
        # Check for specific errors
        if "Recursion limit" in output:
            print("❌ Got recursion error!")
            print(f"Output: {output[:500]}...")
            return False
            
        if "Could not create agent" in output:
            print("❌ Agent creation failed!")
            print(f"Warning: {output[output.find('Warning'):output.find('Warning')+100]}")
            return False
            
        if "Error in conversation" in output:
            print("❌ Conversation error!")
            idx = output.find("Error in conversation")
            print(f"Error: {output[idx:idx+200]}")
            return False
            
        if result.returncode != 0:
            print(f"❌ Forum CLI failed with return code: {result.returncode}")
            return False
            
        print("✅ Forum join and message worked")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Forum CLI timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run forum CLI: {e}")
        return False
    finally:
        # Clean up test forum
        db.delete_forum(test_forum_id, "test_user")

def test_multi_agent_response():
    """Test that multiple agents actually respond"""
    
    print("\n🧪 Testing Multi-Agent Response")
    print("=" * 50)
    
    try:
        # Test basic interface with multi-agent question
        commands = "anyone else here?\nquit\n"
        
        result = subprocess.run(
            [sys.executable, "-m", "philosopher_dinner.cli.interface"],
            input=commands,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        output = result.stdout
        
        # Check who responded
        agents_found = []
        for agent in ["Socrates", "Aristotle", "Nietzsche", "Kant", "Confucius"]:
            if f"{agent} •" in output or f"[{agent}]" in output:
                agents_found.append(agent)
        
        print(f"🤖 Agents who responded: {agents_found}")
        
        if len(agents_found) == 0:
            print("❌ No agents responded!")
            return False
        elif len(agents_found) == 1:
            print(f"⚠️ Only {agents_found[0]} responded")
            return False
        else:
            print(f"✅ Multiple agents responded: {agents_found}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to test multi-agent: {e}")
        return False

def test_recursion_limit():
    """Test that recursion limits are properly enforced"""
    
    print("\n🧪 Testing Recursion Limit Handling")
    print("=" * 50)
    
    from philosopher_dinner.forum.graph import PhilosopherForum
    from philosopher_dinner.forum.state import ForumConfig, ForumMode, MessageType
    from datetime import datetime
    
    # Create a forum that might trigger recursion
    forum_config = ForumConfig(
        forum_id="recursion_test",
        name="Recursion Test",
        description="Test recursion limits",
        mode=ForumMode.EXPLORATION,
        participants=["socrates", "aristotle", "nietzsche", "kant", "confucius"],
        created_at=datetime.now(),
        settings={}
    )
    
    forum = PhilosopherForum(forum_config)
    
    try:
        # This should not cause infinite recursion
        state = forum.start_conversation("everyone please respond!")
        
        # Count agent messages
        agent_messages = [m for m in state.get("messages", []) if m["message_type"] == MessageType.AGENT]
        
        print(f"📊 Agent messages: {len(agent_messages)}")
        
        if len(agent_messages) > 5:
            print("❌ Too many agent messages - recursion limit not working")
            return False
        elif len(agent_messages) == 0:
            print("❌ No agent messages")
            return False
        else:
            print(f"✅ Recursion properly limited ({len(agent_messages)} messages)")
            return True
            
    except Exception as e:
        if "Recursion limit" in str(e):
            print(f"❌ Recursion error: {e}")
            return False
        else:
            print(f"❌ Unexpected error: {e}")
            return False

def run_all_real_tests():
    """Run all real CLI tests"""
    
    print("🚀 REAL CLI EXECUTION TESTS")
    print("=" * 60)
    print("Testing actual CLI execution to catch runtime failures...")
    print("=" * 60)
    
    tests = [
        test_real_cli_startup,
        test_forum_join_and_message,
        test_multi_agent_response,
        test_recursion_limit
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                errors.append(test.__name__)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
            errors.append(f"{test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 REAL TEST RESULTS:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    
    if errors:
        print("\n🐛 FAILURES:")
        for error in errors:
            print(f"  • {error}")
    
    print("\n" + "=" * 60)
    
    if failed == 0:
        print("🎉 All real tests passed!")
        print("The system actually works in practice!")
    else:
        print("❌ REAL FAILURES DETECTED!")
        print("The system has actual runtime issues that need fixing!")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_real_tests()
    sys.exit(0 if success else 1)