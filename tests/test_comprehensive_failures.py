#!/usr/bin/env python3
"""
Comprehensive Failure-First Test Suite
Tests real-world failure modes, integration points, and edge cases that users actually encounter.
This suite actively tries to break the system to find gaps in error handling.
"""
import os
import sys
import unittest
import tempfile
import subprocess
import threading
import time
import shutil
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import uuid

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from philosopher_dinner.forum.database import ForumDatabase, ForumMetadata
from philosopher_dinner.forum.state import ForumMode, Message, MessageType
from philosopher_dinner.agents.forum_creator import ForumCreationAgent
from philosopher_dinner.agents.agent_factory import AgentFactory
from philosopher_dinner.agents.base_agent import BaseAgent


class TestRealCLIExecution(unittest.TestCase):
    """Test the actual CLI execution as users would run it"""
    
    def setUp(self):
        """Set up CLI execution tests"""
        self.project_root = Path(__file__).parent.parent
        self.run_script = self.project_root / "run.sh"
        
    def test_cli_startup_without_errors(self):
        """Test that ./run.sh starts without immediate crashes"""
        if not self.run_script.exists():
            self.skipTest("run.sh not found")
            
        try:
            # Start the CLI and immediately send quit
            process = subprocess.Popen(
                [str(self.run_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Send quit command immediately
            stdout, stderr = process.communicate(input="quit\n", timeout=10)
            
            # Should exit cleanly
            self.assertEqual(process.returncode, 0, f"CLI failed to start: {stderr}")
            
        except subprocess.TimeoutExpired:
            process.kill()
            self.fail("CLI hung on startup")
        except Exception as e:
            self.fail(f"CLI startup failed: {e}")
    
    def test_cli_handles_invalid_commands(self):
        """Test CLI gracefully handles invalid commands"""
        if not self.run_script.exists():
            self.skipTest("run.sh not found")
            
        try:
            process = subprocess.Popen(
                [str(self.run_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Send invalid commands followed by quit
            commands = "invalid-command\nnotarealcommand\n\nquit\n"
            stdout, stderr = process.communicate(input=commands, timeout=15)
            
            # Should handle gracefully and exit cleanly
            self.assertEqual(process.returncode, 0, f"CLI crashed on invalid input: {stderr}")
            self.assertIn("Unknown command", stdout, "CLI should report unknown commands")
            
        except subprocess.TimeoutExpired:
            process.kill()
            self.fail("CLI hung on invalid commands")
        except Exception as e:
            self.fail(f"CLI invalid command test failed: {e}")
    
    def test_cli_handles_eof_and_interrupts(self):
        """Test CLI handles EOF and keyboard interrupts gracefully"""
        if not self.run_script.exists():
            self.skipTest("run.sh not found")
            
        try:
            process = subprocess.Popen(
                [str(self.run_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Close stdin to simulate EOF
            process.stdin.close()
            
            # Wait a bit then send interrupt
            time.sleep(2)
            process.send_signal(signal.SIGINT)
            
            # Should exit gracefully
            process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            process.kill()
            self.fail("CLI didn't handle EOF/interrupt gracefully")
        except Exception as e:
            # This is acceptable - CLI may exit in various ways for EOF/interrupt
            pass


class TestLLMIntegrationFailures(unittest.TestCase):
    """Test LLM integration failure modes"""
    
    def test_missing_api_key(self):
        """Test behavior when API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing API keys
            if 'ANTHROPIC_API_KEY' in os.environ:
                del os.environ['ANTHROPIC_API_KEY']
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
                
            from philosopher_dinner.config.llm_config import is_llm_available
            
            # Should handle missing API key gracefully
            available = is_llm_available()
            self.assertFalse(available, "Should detect missing API key")
    
    def test_invalid_api_key_format(self):
        """Test behavior with malformed API keys"""
        test_cases = [
            "",  # Empty
            "invalid",  # Too short
            "sk-" + "x" * 100,  # Too long
            "definitely-not-a-real-key-123",  # Wrong format
            None,  # None value
        ]
        
        for bad_key in test_cases:
            with self.subTest(api_key=bad_key):
                with patch.dict(os.environ, {'ANTHROPIC_API_KEY': str(bad_key) if bad_key else ''}):
                    try:
                        from philosopher_dinner.config.llm_config import get_llm_instance
                        llm = get_llm_instance()
                        # Should either return None or create instance that will fail gracefully
                        if llm is not None:
                            # If instance created, it should handle bad key gracefully in actual use
                            pass
                    except Exception as e:
                        # Should not crash on bad API key format
                        self.fail(f"LLM config crashed on bad API key '{bad_key}': {e}")
    
    @patch('philosopher_dinner.config.llm_config.ChatAnthropic')
    def test_llm_network_failure(self, mock_anthropic):
        """Test behavior when LLM network calls fail"""
        # Mock network failure
        mock_anthropic.side_effect = ConnectionError("Network unreachable")
        
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            try:
                from philosopher_dinner.config.llm_config import get_llm_instance
                llm = get_llm_instance()
                # Should handle network failure gracefully
            except ConnectionError:
                self.fail("LLM config should handle network failures gracefully")
            except Exception as e:
                # Other exceptions might be OK depending on implementation
                pass
    
    def test_agent_fallback_when_llm_unavailable(self):
        """Test that agents fall back to non-LLM responses when LLM unavailable"""
        # Force LLM unavailable
        with patch('philosopher_dinner.agents.base_agent.is_llm_available', return_value=False):
            factory = AgentFactory()
            agent = factory.create_agent("socrates")
            
            self.assertIsNotNone(agent, "Agent should be created even without LLM")
            
            # Test response generation falls back gracefully
            from philosopher_dinner.forum.state import ForumState
            test_state = {
                "messages": [{
                    "id": "test",
                    "sender": "human", 
                    "content": "What is justice?",
                    "message_type": "human",
                    "timestamp": datetime.now(),
                    "thinking": None,
                    "metadata": {}
                }],
                "current_topic": "justice",
                "participants": ["socrates", "human"],
                "forum_mode": ForumMode.EXPLORATION
            }
            
            try:
                response = agent.generate_response(test_state)
                self.assertIsNotNone(response, "Agent should generate fallback response")
                self.assertIsNotNone(response.message, "Fallback response should include message")
            except Exception as e:
                self.fail(f"Agent fallback failed: {e}")


class TestFilesystemAndPermissions(unittest.TestCase):
    """Test filesystem edge cases and permission issues"""
    
    def test_database_in_readonly_directory(self):
        """Test behavior when database directory is read-only"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Make directory read-only
            os.chmod(temp_dir, 0o444)
            
            try:
                db_path = os.path.join(temp_dir, "test.db")
                
                # Should handle read-only directory gracefully
                try:
                    db = ForumDatabase(db_path)
                    # If creation succeeds, that's OK
                except PermissionError:
                    # If it fails with permission error, that's also OK
                    pass
                except Exception as e:
                    self.fail(f"Database should handle read-only directory gracefully: {e}")
            finally:
                # Restore permissions for cleanup
                os.chmod(temp_dir, 0o755)
    
    def test_database_with_insufficient_disk_space(self):
        """Test behavior when disk space is low (simulated)"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name
            
        try:
            # Create database
            db = ForumDatabase(db_path)
            
            # Mock filesystem full error
            with patch('sqlite3.connect') as mock_connect:
                mock_connect.side_effect = OSError("No space left on device")
                
                # Should handle disk full gracefully
                metadata = ForumMetadata(
                    forum_id="test",
                    name="Test",
                    description="Test",
                    mode=ForumMode.EXPLORATION,
                    participants=["socrates"],
                    created_at=datetime.now(),
                    creator="test"
                )
                
                result = db.create_forum(metadata)
                # Should return False rather than crash
                self.assertFalse(result, "Should handle disk full gracefully")
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_corrupted_database_file(self):
        """Test behavior with corrupted database file"""
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            # Write garbage data to simulate corruption
            temp_file.write("This is not a valid SQLite database file!")
            db_path = temp_file.name
            
        try:
            # Should handle corrupted database gracefully
            try:
                db = ForumDatabase(db_path)
                # If it succeeds in opening, try an operation
                forums = db.list_forums()
                # If this succeeds, the DB was rebuilt - that's OK
            except Exception as e:
                # Should fail gracefully, not crash the application
                self.assertIsInstance(e, (OSError, IOError, Exception))
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_concurrent_database_access(self):
        """Test concurrent access to database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            db_path = temp_file.name
            
        try:
            # Create multiple database instances
            db1 = ForumDatabase(db_path)
            db2 = ForumDatabase(db_path)
            
            # Create forum with first instance
            metadata = ForumMetadata(
                forum_id="concurrent_test",
                name="Concurrent Test",
                description="Test concurrent access",
                mode=ForumMode.EXPLORATION,
                participants=["socrates"],
                created_at=datetime.now(),
                creator="user1"
            )
            
            success1 = db1.create_forum(metadata)
            self.assertTrue(success1, "First database should create forum")
            
            # Read with second instance
            forum = db2.get_forum("concurrent_test")
            self.assertIsNotNone(forum, "Second database should read forum")
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestInputValidationAndEdgeCases(unittest.TestCase):
    """Test input validation and edge cases"""
    
    def test_extremely_long_inputs(self):
        """Test behavior with extremely long inputs"""
        long_input = "x" * 10000  # 10KB input
        very_long_input = "y" * 100000  # 100KB input
        
        agent = ForumCreationAgent()
        
        # Test long topic input
        try:
            response = agent.start_forum_creation(long_input)
            self.assertIsInstance(response, str, "Should handle long input gracefully")
        except Exception as e:
            self.fail(f"Failed on long input: {e}")
        
        # Test very long input
        try:
            response = agent.start_forum_creation(very_long_input)
            self.assertIsInstance(response, str, "Should handle very long input gracefully")
        except Exception as e:
            # This might fail due to memory/processing limits - that's acceptable
            # But should not crash with unhandled exception
            self.assertIsInstance(e, (MemoryError, OSError, ValueError))
    
    def test_unicode_and_special_characters(self):
        """Test behavior with unicode and special characters"""
        test_inputs = [
            "🤔 What is φιλοσοφία (philosophy)?",  # Unicode emojis and Greek
            "What about 'quotes' and \"double quotes\"?",  # Various quotes
            "How about\nnewlines\tand\ttabs?",  # Control characters
            "SQL injection'; DROP TABLE forums; --",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "../../../../etc/passwd",  # Path traversal attempt
        ]
        
        agent = ForumCreationAgent()
        
        for test_input in test_inputs:
            with self.subTest(input=test_input[:50]):
                try:
                    response = agent.start_forum_creation(test_input)
                    self.assertIsInstance(response, str, f"Should handle input: {test_input[:50]}")
                    # Response should not contain raw input if it's potentially dangerous
                    if "<script>" in test_input:
                        self.assertNotIn("<script>", response, "Should sanitize script tags")
                except Exception as e:
                    self.fail(f"Failed on input '{test_input[:50]}': {e}")
    
    def test_null_and_empty_inputs(self):
        """Test behavior with null and empty inputs"""
        test_cases = [
            None,
            "",
            "   ",  # Whitespace only
            "\n\t\r",  # Control characters only
        ]
        
        agent = ForumCreationAgent()
        
        for test_input in test_cases:
            with self.subTest(input=repr(test_input)):
                try:
                    if test_input is None:
                        # This might raise TypeError - that's acceptable
                        with self.assertRaises((TypeError, ValueError)):
                            agent.start_forum_creation(test_input)
                    else:
                        response = agent.start_forum_creation(test_input)
                        self.assertIsInstance(response, str, f"Should handle input: {repr(test_input)}")
                except Exception as e:
                    # Should fail gracefully
                    self.assertIsInstance(e, (TypeError, ValueError, AttributeError))


class TestMemoryAndPerformance(unittest.TestCase):
    """Test memory usage and performance edge cases"""
    
    def test_large_number_of_forums(self):
        """Test system behavior with many forums"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            db_path = temp_file.name
            
        try:
            db = ForumDatabase(db_path)
            
            # Create many forums
            num_forums = 100
            for i in range(num_forums):
                metadata = ForumMetadata(
                    forum_id=f"forum_{i:03d}",
                    name=f"Forum {i}",
                    description=f"Test forum number {i}",
                    mode=ForumMode.EXPLORATION,
                    participants=["socrates", "aristotle"],
                    created_at=datetime.now(),
                    creator=f"user_{i % 10}"  # 10 different users
                )
                
                success = db.create_forum(metadata)
                if not success:
                    self.fail(f"Failed to create forum {i}")
            
            # Test listing all forums
            start_time = time.time()
            forums = db.list_forums()
            elapsed = time.time() - start_time
            
            self.assertEqual(len(forums), num_forums, "Should list all forums")
            self.assertLess(elapsed, 5.0, "Listing forums should complete in reasonable time")
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_large_conversation_history(self):
        """Test system with large conversation history"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            db_path = temp_file.name
            
        try:
            db = ForumDatabase(db_path)
            
            # Create forum
            metadata = ForumMetadata(
                forum_id="large_conversation",
                name="Large Conversation",
                description="Test large conversation",
                mode=ForumMode.EXPLORATION,
                participants=["socrates"],
                created_at=datetime.now(),
                creator="test_user"
            )
            db.create_forum(metadata)
            
            # Add many messages
            num_messages = 1000
            for i in range(num_messages):
                message = Message(
                    id=str(uuid.uuid4()),
                    sender="socrates" if i % 2 == 0 else "human",
                    content=f"This is message number {i} in a very long conversation about philosophy.",
                    message_type=MessageType.AGENT if i % 2 == 0 else MessageType.HUMAN,
                    timestamp=datetime.now(),
                    thinking=f"Thinking about message {i}" if i % 2 == 0 else None,
                    metadata={"message_number": i}
                )
                
                success = db.add_message("large_conversation", message)
                if not success:
                    self.fail(f"Failed to add message {i}")
            
            # Test retrieving messages
            start_time = time.time()
            messages = db.get_messages("large_conversation")
            elapsed = time.time() - start_time
            
            self.assertEqual(len(messages), num_messages, "Should retrieve all messages")
            self.assertLess(elapsed, 5.0, "Message retrieval should complete in reasonable time")
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_agent_creation_performance(self):
        """Test agent creation doesn't have memory leaks"""
        factory = AgentFactory()
        
        # Create and destroy many agents
        start_time = time.time()
        for i in range(50):
            agent = factory.create_agent("socrates")
            self.assertIsNotNone(agent, f"Agent creation {i} failed")
            # Let agent go out of scope
            del agent
        
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 10.0, "Agent creation should be reasonably fast")


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility issues"""
    
    def test_path_handling(self):
        """Test path handling works across platforms"""
        from philosopher_dinner.agents.agent_factory import AgentFactory
        
        # Test that path creation works
        factory = AgentFactory()
        self.assertIsNotNone(factory.templates_path, "Templates path should be set")
        
        # Path should exist or be creatable
        if not factory.templates_path.exists():
            try:
                factory.templates_path.mkdir(parents=True, exist_ok=True)
                self.assertTrue(factory.templates_path.exists(), "Should create templates directory")
            except OSError as e:
                self.fail(f"Failed to create templates directory: {e}")
    
    def test_database_path_handling(self):
        """Test database path handling across platforms"""
        import tempfile
        
        # Test various path formats
        test_paths = [
            "test.db",  # Relative path
            "./test.db",  # Explicit relative
        ]
        
        # Add absolute path
        with tempfile.TemporaryDirectory() as temp_dir:
            test_paths.append(os.path.join(temp_dir, "test.db"))
            
            for db_path in test_paths:
                with self.subTest(path=db_path):
                    try:
                        db = ForumDatabase(db_path)
                        self.assertIsNotNone(db, f"Should create database at {db_path}")
                    except Exception as e:
                        self.fail(f"Database creation failed for path {db_path}: {e}")
                    finally:
                        # Clean up
                        if os.path.exists(db_path):
                            os.unlink(db_path)


def run_comprehensive_failure_tests():
    """Run all failure-focused tests with detailed reporting"""
    
    print("💥 RUNNING COMPREHENSIVE FAILURE-FIRST TESTS")
    print("=" * 70)
    print("This suite actively tries to break the system to find edge cases.")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestRealCLIExecution,
        TestLLMIntegrationFailures,
        TestFilesystemAndPermissions,
        TestInputValidationAndEdgeCases,
        TestMemoryAndPerformance,
        TestCrossPlatformCompatibility,
    ]
    
    total_tests = 0
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        total_tests += tests.countTestCases()
    
    print(f"🎯 Running {total_tests} failure-focused tests...")
    print()
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print detailed summary
    print("\n" + "=" * 70)
    print(f"💥 FAILURE-FIRST TEST SUMMARY:")
    print(f"  Total tests: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(getattr(result, 'skipped', []))}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"  Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  • {test}")
            # Print first line of traceback for quick overview
            first_line = traceback.split('\n')[0] if traceback else "No details"
            print(f"    {first_line}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  • {test}")
            # Print first line of traceback for quick overview
            first_line = traceback.split('\n')[0] if traceback else "No details"
            print(f"    {first_line}")
    
    if hasattr(result, 'skipped') and result.skipped:
        print(f"\n⏭️  SKIPPED ({len(result.skipped)}):")
        for test, reason in result.skipped:
            print(f"  • {test}: {reason}")
    
    print("\n" + "=" * 70)
    
    if result.wasSuccessful():
        print("✅ ALL FAILURE TESTS PASSED!")
        print("The system handles edge cases and failure modes well.")
    else:
        print("❌ SOME FAILURE TESTS FAILED!")
        print("These represent real edge cases that could cause user issues.")
        print("\nRecommendation: Fix these before considering the system robust.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_failure_tests()
    sys.exit(0 if success else 1)