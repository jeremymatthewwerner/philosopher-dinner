#!/usr/bin/env python3
"""
Comprehensive tests for the Forum Management System
Tests database operations, agent creation, search functionality, and CLI commands.
"""
import os
import sys
import unittest
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from philosopher_dinner.forum.database import ForumDatabase, ForumMetadata, ParticipantEvent
from philosopher_dinner.forum.state import ForumMode, Message, MessageType
from philosopher_dinner.agents.forum_creator import ForumCreationAgent, ThinkerSuggestion
from philosopher_dinner.agents.agent_factory import AgentFactory, DynamicPhilosopherAgent
from philosopher_dinner.search.semantic_search import SemanticForumSearch, SearchResult


class TestForumDatabase(unittest.TestCase):
    """Test the forum database functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ForumDatabase(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def test_create_forum(self):
        """Test forum creation"""
        metadata = ForumMetadata(
            forum_id="test123",
            name="Test Forum",
            description="A test forum",
            mode=ForumMode.EXPLORATION,
            participants=["socrates", "oracle"],
            created_at=datetime.now(),
            creator="testuser"
        )
        
        # Create forum
        success = self.db.create_forum(metadata)
        self.assertTrue(success)
        
        # Verify forum exists
        retrieved = self.db.get_forum("test123")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Forum")
        self.assertEqual(retrieved.mode, ForumMode.EXPLORATION)
        self.assertIn("socrates", retrieved.participants)
    
    def test_list_forums(self):
        """Test forum listing"""
        # Create multiple forums
        for i in range(3):
            metadata = ForumMetadata(
                forum_id=f"forum{i}",
                name=f"Forum {i}",
                description=f"Test forum {i}",
                mode=ForumMode.EXPLORATION,
                participants=["socrates"],
                created_at=datetime.now(),
                creator="testuser"
            )
            self.db.create_forum(metadata)
        
        # List forums
        forums = self.db.list_forums()
        self.assertEqual(len(forums), 3)
        
        # Test user filtering
        forums_filtered = self.db.list_forums(user="testuser")
        self.assertEqual(len(forums_filtered), 3)
        
        forums_filtered = self.db.list_forums(user="otheruser")
        self.assertEqual(len(forums_filtered), 3)  # Public forums visible to all
    
    def test_join_leave_forum(self):
        """Test joining and leaving forums"""
        # Create forum
        metadata = ForumMetadata(
            forum_id="join_test",
            name="Join Test Forum",
            description="Test joining",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            creator="testuser"
        )
        self.db.create_forum(metadata)
        
        # Join forum
        success = self.db.join_forum("join_test", "newuser")
        self.assertTrue(success)
        
        # Verify participant added
        forum = self.db.get_forum("join_test")
        self.assertIn("newuser", forum.participants)
        
        # Leave forum
        success = self.db.leave_forum("join_test", "newuser")
        self.assertTrue(success)
        
        # Verify participant removed
        forum = self.db.get_forum("join_test")
        self.assertNotIn("newuser", forum.participants)
    
    def test_delete_forum(self):
        """Test forum deletion"""
        # Create forum
        metadata = ForumMetadata(
            forum_id="delete_test",
            name="Delete Test",
            description="Test deletion",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            creator="testuser"
        )
        self.db.create_forum(metadata)
        
        # Try to delete as non-creator (should fail)
        success = self.db.delete_forum("delete_test", "otheruser")
        self.assertFalse(success)
        
        # Delete as creator (should succeed)
        success = self.db.delete_forum("delete_test", "testuser")
        self.assertTrue(success)
        
        # Verify forum deleted
        forum = self.db.get_forum("delete_test")
        self.assertIsNone(forum)
    
    def test_messages(self):
        """Test message storage and retrieval"""
        # Create forum
        metadata = ForumMetadata(
            forum_id="msg_test",
            name="Message Test",
            description="Test messages",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            creator="testuser"
        )
        self.db.create_forum(metadata)
        
        # Add messages
        message1 = Message(
            id=str(uuid.uuid4()),
            sender="human",
            content="Hello philosophers",
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        
        message2 = Message(
            id=str(uuid.uuid4()),
            sender="socrates",
            content="Greetings! What shall we explore?",
            message_type=MessageType.AGENT,
            timestamp=datetime.now(),
            thinking="They seem eager to learn",
            metadata={"agent_name": "Socrates"}
        )
        
        # Add messages to database
        self.assertTrue(self.db.add_message("msg_test", message1))
        self.assertTrue(self.db.add_message("msg_test", message2))
        
        # Retrieve messages
        messages = self.db.get_messages("msg_test")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["content"], "Hello philosophers")
        self.assertEqual(messages[1]["sender"], "socrates")
    
    def test_forum_summaries(self):
        """Test forum summary storage"""
        # Create forum
        metadata = ForumMetadata(
            forum_id="summary_test",
            name="Summary Test",
            description="Test summaries",
            mode=ForumMode.EXPLORATION,
            participants=["socrates"],
            created_at=datetime.now(),
            creator="testuser"
        )
        self.db.create_forum(metadata)
        
        # Save summary
        summary = "This forum explores the nature of knowledge and truth."
        success = self.db.save_forum_summary("summary_test", "brief", summary)
        self.assertTrue(success)
        
        # Retrieve summary
        retrieved_summary = self.db.get_forum_summary("summary_test", "brief")
        self.assertEqual(retrieved_summary, summary)


class TestForumCreationAgent(unittest.TestCase):
    """Test the forum creation agent"""
    
    def setUp(self):
        """Set up test agent"""
        self.agent = ForumCreationAgent()
    
    def test_thinker_suggestions(self):
        """Test thinker suggestion generation"""
        # Test ethics-related query
        suggestions = self.agent._generate_thinker_suggestions("What is moral virtue?")
        self.assertGreater(len(suggestions), 0)
        
        # Should include ethics experts
        suggestion_names = [s.name for s in suggestions]
        self.assertTrue(any("Aristotle" in name or "Kant" in name for name in suggestion_names))
    
    def test_forum_mode_suggestion(self):
        """Test forum mode suggestion"""
        # Debate question
        mode = self.agent._suggest_forum_mode("Which is better: virtue ethics vs deontology?")
        self.assertEqual(mode, ForumMode.DEBATE)
        
        # Exploration question
        mode = self.agent._suggest_forum_mode("What is the nature of reality?")
        self.assertEqual(mode, ForumMode.EXPLORATION)
    
    def test_topic_keyword_extraction(self):
        """Test topic keyword extraction"""
        keywords = self.agent._extract_topic_keywords("What is justice and morality in society?")
        self.assertIn("justice", keywords)
        self.assertIn("morality", keywords)
    
    def test_creation_dialog_flow(self):
        """Test the creation dialog flow"""
        # Start creation
        response = self.agent.start_forum_creation("I want to discuss ethics")
        self.assertIn("ethics", response.lower())
        
        # Process topic input
        response, is_complete = self.agent.continue_creation_dialog("What makes an action morally right?")
        self.assertFalse(is_complete)
        self.assertIn("thinker", response.lower())


class TestAgentFactory(unittest.TestCase):
    """Test the agent factory and dynamic agent creation"""
    
    def setUp(self):
        """Set up test factory"""
        self.factory = AgentFactory()
    
    def test_create_socrates_agent(self):
        """Test creating Socrates agent"""
        agent = self.factory.create_agent("socrates")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "Socrates")
        self.assertIn("ethics", agent.expertise_areas)
    
    def test_create_dynamic_agent(self):
        """Test creating dynamic philosopher agents"""
        # Test Aristotle
        agent = self.factory.create_agent("aristotle")
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, DynamicPhilosopherAgent)
        self.assertEqual(agent.name, "Aristotle")
        self.assertIn("ethics", agent.expertise_areas)
        
        # Test Kant
        agent = self.factory.create_agent("kant")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "Immanuel Kant")
        self.assertIn("moral_philosophy", agent.expertise_areas)
    
    def test_get_available_agents(self):
        """Test getting list of available agents"""
        agents = self.factory.get_available_agents()
        self.assertIn("socrates", agents)
        self.assertIn("aristotle", agents)
        self.assertIn("kant", agents)
        self.assertIn("plato", agents)
    
    def test_get_agent_info(self):
        """Test getting agent information"""
        info = self.factory.get_agent_info("kant")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "Immanuel Kant")
        self.assertIn("moral_philosophy", info["expertise"])
    
    def test_create_agents_for_forum(self):
        """Test creating multiple agents for a forum"""
        participant_ids = ["socrates", "aristotle", "kant"]
        agents = self.factory.create_agents_for_forum(participant_ids)
        
        self.assertEqual(len(agents), 3)
        self.assertIn("socrates", agents)
        self.assertIn("aristotle", agents)
        self.assertIn("kant", agents)


class TestSemanticSearch(unittest.TestCase):
    """Test the semantic search functionality"""
    
    def setUp(self):
        """Set up test search engine"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ForumDatabase(self.temp_db.name)
        self.search = SemanticForumSearch(self.db)
        
        # Create test forums
        self._create_test_forums()
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def _create_test_forums(self):
        """Create test forums with different themes"""
        forums = [
            {
                "forum_id": "ethics1",
                "name": "Virtue Ethics Discussion",
                "description": "Exploring Aristotelian virtue ethics and moral character",
                "participants": ["aristotle", "socrates"],
                "tags": ["ethics", "virtue", "character"]
            },
            {
                "forum_id": "mind1", 
                "name": "Mind-Body Problem",
                "description": "Descartes and the relationship between mind and body",
                "participants": ["descartes", "hume"],
                "tags": ["consciousness", "mind", "body"]
            },
            {
                "forum_id": "justice1",
                "name": "What is Justice?",
                "description": "Plato's Republic and theories of justice",
                "participants": ["plato", "aristotle"],
                "tags": ["justice", "politics", "society"]
            }
        ]
        
        for forum_data in forums:
            metadata = ForumMetadata(
                forum_id=forum_data["forum_id"],
                name=forum_data["name"],
                description=forum_data["description"],
                mode=ForumMode.EXPLORATION,
                participants=forum_data["participants"],
                created_at=datetime.now(),
                creator="testuser",
                tags=forum_data["tags"]
            )
            self.db.create_forum(metadata)
    
    def test_concept_extraction(self):
        """Test philosophical concept extraction"""
        concepts = self.search._extract_concepts("What is virtue and moral character?")
        self.assertIn("ethics", concepts)
        self.assertTrue(concepts["ethics"] > 0)
    
    def test_philosopher_extraction(self):
        """Test philosopher name extraction"""
        philosophers = self.search._extract_philosophers("I want to discuss Kant's categorical imperative")
        self.assertIn("kant", philosophers)
        
        philosophers = self.search._extract_philosophers("What did Immanuel Kant think about duty?")
        self.assertIn("kant", philosophers)
    
    def test_search_by_concept(self):
        """Test searching by philosophical concept"""
        results = self.search.search("virtue ethics")
        self.assertGreater(len(results), 0)
        
        # Should find the virtue ethics forum
        found_virtue_forum = any(r.forum.forum_id == "ethics1" for r in results)
        self.assertTrue(found_virtue_forum)
        
        # Check confidence scoring
        virtue_result = next(r for r in results if r.forum.forum_id == "ethics1")
        self.assertGreater(virtue_result.confidence, 0.5)
    
    def test_search_by_philosopher(self):
        """Test searching by philosopher name"""
        results = self.search.search("descartes mind")
        self.assertGreater(len(results), 0)
        
        # Should find the mind-body forum
        found_mind_forum = any(r.forum.forum_id == "mind1" for r in results)
        self.assertTrue(found_mind_forum)
    
    def test_search_by_title(self):
        """Test searching by forum title"""
        results = self.search.search("justice")
        self.assertGreater(len(results), 0)
        
        # Should find the justice forum
        found_justice_forum = any(r.forum.forum_id == "justice1" for r in results)
        self.assertTrue(found_justice_forum)
    
    def test_search_suggestions(self):
        """Test search term suggestions"""
        suggestions = self.search.suggest_search_terms("eth")
        self.assertIn("ethics", suggestions)
        
        suggestions = self.search.suggest_search_terms("kant")
        self.assertTrue(any("kant" in s.lower() for s in suggestions))
    
    def test_search_analytics(self):
        """Test search analytics"""
        analytics = self.search.get_search_analytics("What is virtue according to Aristotle?")
        
        self.assertIn("detected_concepts", analytics)
        self.assertIn("mentioned_philosophers", analytics)
        self.assertIn("aristotle", analytics["mentioned_philosophers"])
        self.assertIn("ethics", analytics["detected_concepts"])
    
    def test_no_results_handling(self):
        """Test handling of searches with no results"""
        results = self.search.search("quantum mechanics")
        self.assertEqual(len(results), 0)  # Should be no philosophy forums about quantum mechanics


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete forum management system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ForumDatabase(self.temp_db.name)
        self.factory = AgentFactory()
        self.search = SemanticForumSearch(self.db)
    
    def tearDown(self):
        """Clean up integration test environment"""
        os.unlink(self.temp_db.name)
    
    def test_end_to_end_forum_creation(self):
        """Test complete forum creation workflow"""
        # Create forum metadata
        metadata = ForumMetadata(
            forum_id="integration_test",
            name="Integration Test Forum",
            description="Testing the complete workflow",
            mode=ForumMode.EXPLORATION,
            participants=["socrates", "aristotle", "kant"],
            created_at=datetime.now(),
            creator="testuser"
        )
        
        # Create forum in database
        success = self.db.create_forum(metadata)
        self.assertTrue(success)
        
        # Create agents for forum
        agents = self.factory.create_agents_for_forum(metadata.participants)
        self.assertEqual(len(agents), 3)
        
        # Add some messages
        messages = [
            Message(
                id=str(uuid.uuid4()),
                sender="human",
                content="What is the highest virtue?",
                message_type=MessageType.HUMAN,
                timestamp=datetime.now(),
                thinking=None,
                metadata={}
            ),
            Message(
                id=str(uuid.uuid4()),
                sender="aristotle",
                content="I believe the highest virtue is eudaimonia - human flourishing through excellent character.",
                message_type=MessageType.AGENT,
                timestamp=datetime.now(),
                thinking="This connects to my Nicomachean Ethics",
                metadata={"agent_name": "Aristotle"}
            )
        ]
        
        for message in messages:
            self.db.add_message("integration_test", message)
        
        # Test search finds the forum
        results = self.search.search("virtue aristotle")
        found_forum = any(r.forum.forum_id == "integration_test" for r in results)
        self.assertTrue(found_forum)
        
        # Test forum retrieval
        retrieved_forum = self.db.get_forum("integration_test")
        self.assertIsNotNone(retrieved_forum)
        self.assertEqual(len(retrieved_forum.participants), 3)
        
        # Test message retrieval
        retrieved_messages = self.db.get_messages("integration_test")
        self.assertEqual(len(retrieved_messages), 2)
    
    def test_forum_lifecycle(self):
        """Test complete forum lifecycle"""
        # Create
        metadata = ForumMetadata(
            forum_id="lifecycle_test",
            name="Lifecycle Test",
            description="Testing forum lifecycle",
            mode=ForumMode.DEBATE,
            participants=["socrates"],
            created_at=datetime.now(),
            creator="testuser"
        )
        self.db.create_forum(metadata)
        
        # Join
        self.db.join_forum("lifecycle_test", "newuser")
        forum = self.db.get_forum("lifecycle_test")
        self.assertIn("newuser", forum.participants)
        
        # Add content
        message = Message(
            id=str(uuid.uuid4()),
            sender="newuser",
            content="This is a test message",
            message_type=MessageType.HUMAN,
            timestamp=datetime.now(),
            thinking=None,
            metadata={}
        )
        self.db.add_message("lifecycle_test", message)
        
        # Leave
        self.db.leave_forum("lifecycle_test", "newuser")
        forum = self.db.get_forum("lifecycle_test")
        self.assertNotIn("newuser", forum.participants)
        
        # Delete
        success = self.db.delete_forum("lifecycle_test", "testuser")
        self.assertTrue(success)
        
        forum = self.db.get_forum("lifecycle_test")
        self.assertIsNone(forum)
    
    def test_cli_instantiation(self):
        """Test that CLI components can be instantiated without errors"""
        from philosopher_dinner.cli.simple_forum_cli import SimpleForumManagerCLI
        
        # This should not throw any TypeError about abstract methods
        try:
            cli = SimpleForumManagerCLI()
            self.assertIsNotNone(cli.forum_creator)
            self.assertIsInstance(cli.forum_creator, ForumCreationAgent)
        except TypeError as e:
            if "abstract method" in str(e):
                self.fail(f"CLI instantiation failed due to abstract method error: {e}")
            else:
                raise  # Re-raise if it's a different TypeError


def run_comprehensive_tests():
    """Run all tests with detailed output"""
    
    print("🧪 RUNNING COMPREHENSIVE FORUM MANAGEMENT TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestForumDatabase,
        TestForumCreationAgent,
        TestAgentFactory,
        TestSemanticSearch,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ ALL TESTS PASSED! The forum management system is working correctly.")
    else:
        print(f"\n❌ SOME TESTS FAILED. Please review the issues above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)