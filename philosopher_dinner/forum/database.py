"""
Forum Database and Persistence Layer
Handles storage and retrieval of forums, conversations, and participant history.
"""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from .state import ForumConfig, ForumMode, Message, MessageType


class ForumMetadata:
    """Metadata for a forum"""
    def __init__(
        self,
        forum_id: str,
        name: str,
        description: str,
        mode: ForumMode,
        participants: List[str],
        created_at: datetime,
        creator: str,
        tags: List[str] = None,
        is_private: bool = False
    ):
        self.forum_id = forum_id
        self.name = name
        self.description = description
        self.mode = mode
        self.participants = participants
        self.created_at = created_at
        self.creator = creator
        self.tags = tags or []
        self.is_private = is_private
        self.last_activity = created_at
        self.message_count = 0


class ParticipantEvent:
    """Event for tracking participant join/leave actions"""
    def __init__(
        self,
        event_type: str,  # "join" or "leave"
        participant: str,
        timestamp: datetime,
        forum_id: str,
        message: str = None
    ):
        self.event_type = event_type
        self.participant = participant
        self.timestamp = timestamp
        self.forum_id = forum_id
        self.message = message or f"{participant} {event_type}ed the forum"


class ForumDatabase:
    """Database for managing multiple forums and their conversations"""
    
    def __init__(self, db_path: str = "forums.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables"""
        with self._get_connection() as conn:
            # Forums table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forums (
                    forum_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    mode TEXT NOT NULL,
                    participants TEXT,  -- JSON array
                    created_at TEXT NOT NULL,
                    creator TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    is_private INTEGER DEFAULT 0,
                    last_activity TEXT,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            # Messages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    forum_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    thinking TEXT,
                    metadata TEXT,  -- JSON
                    FOREIGN KEY (forum_id) REFERENCES forums (forum_id)
                )
            """)
            
            # Participant events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS participant_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    forum_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    participant TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    message TEXT,
                    FOREIGN KEY (forum_id) REFERENCES forums (forum_id)
                )
            """)
            
            # Forum summaries table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forum_summaries (
                    forum_id TEXT NOT NULL,
                    summary_type TEXT NOT NULL,  -- 'brief', 'detailed'
                    content TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    message_count_at_generation INTEGER NOT NULL,
                    PRIMARY KEY (forum_id, summary_type),
                    FOREIGN KEY (forum_id) REFERENCES forums (forum_id)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_forum(self, metadata: ForumMetadata) -> bool:
        """Create a new forum"""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO forums (
                        forum_id, name, description, mode, participants, 
                        created_at, creator, tags, is_private, last_activity, message_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.forum_id,
                    metadata.name,
                    metadata.description,
                    metadata.mode.value,
                    json.dumps(metadata.participants),
                    metadata.created_at.isoformat(),
                    metadata.creator,
                    json.dumps(metadata.tags),
                    int(metadata.is_private),
                    metadata.last_activity.isoformat(),
                    metadata.message_count
                ))
                
                # Add creator join event
                self._add_participant_event(
                    conn,
                    ParticipantEvent("join", metadata.creator, metadata.created_at, metadata.forum_id)
                )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error creating forum: {e}")
            return False
    
    def get_forum(self, forum_id: str) -> Optional[ForumMetadata]:
        """Get forum metadata by ID"""
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM forums WHERE forum_id = ?", (forum_id,)
                ).fetchone()
                
                if row:
                    return ForumMetadata(
                        forum_id=row["forum_id"],
                        name=row["name"],
                        description=row["description"],
                        mode=ForumMode(row["mode"]),
                        participants=json.loads(row["participants"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        creator=row["creator"],
                        tags=json.loads(row["tags"]),
                        is_private=bool(row["is_private"])
                    )
        except sqlite3.Error as e:
            print(f"Error getting forum: {e}")
        return None
    
    def list_forums(self, user: str = None, include_private: bool = False) -> List[ForumMetadata]:
        """List all available forums"""
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM forums"
                params = []
                
                if not include_private:
                    query += " WHERE is_private = 0"
                
                if user:
                    if "WHERE" in query:
                        query += " AND (creator = ? OR participants LIKE ?)"
                    else:
                        query += " WHERE (creator = ? OR participants LIKE ?)"
                    params.extend([user, f'%"{user}"%'])
                
                query += " ORDER BY last_activity DESC"
                
                rows = conn.execute(query, params).fetchall()
                
                forums = []
                for row in rows:
                    metadata = ForumMetadata(
                        forum_id=row["forum_id"],
                        name=row["name"],
                        description=row["description"],
                        mode=ForumMode(row["mode"]),
                        participants=json.loads(row["participants"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        creator=row["creator"],
                        tags=json.loads(row["tags"]),
                        is_private=bool(row["is_private"])
                    )
                    metadata.last_activity = datetime.fromisoformat(row["last_activity"])
                    metadata.message_count = row["message_count"]
                    forums.append(metadata)
                
                return forums
        except sqlite3.Error as e:
            print(f"Error listing forums: {e}")
        return []
    
    def delete_forum(self, forum_id: str, user: str) -> bool:
        """Delete a forum (only by creator)"""
        try:
            with self._get_connection() as conn:
                # Check if user is the creator
                row = conn.execute(
                    "SELECT creator FROM forums WHERE forum_id = ?", (forum_id,)
                ).fetchone()
                
                if not row or row["creator"] != user:
                    return False
                
                # Delete all related data
                conn.execute("DELETE FROM forum_summaries WHERE forum_id = ?", (forum_id,))
                conn.execute("DELETE FROM participant_events WHERE forum_id = ?", (forum_id,))
                conn.execute("DELETE FROM messages WHERE forum_id = ?", (forum_id,))
                conn.execute("DELETE FROM forums WHERE forum_id = ?", (forum_id,))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error deleting forum: {e}")
        return False
    
    def join_forum(self, forum_id: str, participant: str) -> bool:
        """Add participant to forum"""
        try:
            with self._get_connection() as conn:
                # Get current participants
                row = conn.execute(
                    "SELECT participants FROM forums WHERE forum_id = ?", (forum_id,)
                ).fetchone()
                
                if not row:
                    return False
                
                participants = json.loads(row["participants"])
                if participant not in participants:
                    participants.append(participant)
                    
                    # Update participants list
                    conn.execute(
                        "UPDATE forums SET participants = ?, last_activity = ? WHERE forum_id = ?",
                        (json.dumps(participants), datetime.now().isoformat(), forum_id)
                    )
                    
                    # Add join event
                    self._add_participant_event(
                        conn,
                        ParticipantEvent("join", participant, datetime.now(), forum_id)
                    )
                    
                    conn.commit()
                
                return True
        except sqlite3.Error as e:
            print(f"Error joining forum: {e}")
        return False
    
    def leave_forum(self, forum_id: str, participant: str) -> bool:
        """Remove participant from forum"""
        try:
            with self._get_connection() as conn:
                # Get current participants
                row = conn.execute(
                    "SELECT participants FROM forums WHERE forum_id = ?", (forum_id,)
                ).fetchone()
                
                if not row:
                    return False
                
                participants = json.loads(row["participants"])
                if participant in participants:
                    participants.remove(participant)
                    
                    # Update participants list
                    conn.execute(
                        "UPDATE forums SET participants = ?, last_activity = ? WHERE forum_id = ?",
                        (json.dumps(participants), datetime.now().isoformat(), forum_id)
                    )
                    
                    # Add leave event
                    self._add_participant_event(
                        conn,
                        ParticipantEvent("leave", participant, datetime.now(), forum_id)
                    )
                    
                    conn.commit()
                
                return True
        except sqlite3.Error as e:
            print(f"Error leaving forum: {e}")
        return False
    
    def add_message(self, forum_id: str, message: Message) -> bool:
        """Add a message to a forum"""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO messages (
                        message_id, forum_id, sender, content, message_type,
                        timestamp, thinking, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message["id"],
                    forum_id,
                    message["sender"],
                    message["content"],
                    message["message_type"].value,
                    message["timestamp"].isoformat(),
                    message.get("thinking"),
                    json.dumps(message["metadata"])
                ))
                
                # Update forum activity and message count
                conn.execute("""
                    UPDATE forums 
                    SET last_activity = ?, message_count = message_count + 1
                    WHERE forum_id = ?
                """, (message["timestamp"].isoformat(), forum_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding message: {e}")
        return False
    
    def get_messages(self, forum_id: str, limit: int = None, offset: int = 0) -> List[Message]:
        """Get messages from a forum"""
        try:
            with self._get_connection() as conn:
                query = """
                    SELECT * FROM messages 
                    WHERE forum_id = ? 
                    ORDER BY timestamp ASC
                """
                params = [forum_id]
                
                if limit:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                
                rows = conn.execute(query, params).fetchall()
                
                messages = []
                for row in rows:
                    message = Message(
                        id=row["message_id"],
                        sender=row["sender"],
                        content=row["content"],
                        message_type=MessageType(row["message_type"]),
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        thinking=row["thinking"],
                        metadata=json.loads(row["metadata"])
                    )
                    messages.append(message)
                
                return messages
        except sqlite3.Error as e:
            print(f"Error getting messages: {e}")
        return []
    
    def get_participant_events(self, forum_id: str) -> List[ParticipantEvent]:
        """Get participant join/leave events for a forum"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute("""
                    SELECT * FROM participant_events 
                    WHERE forum_id = ? 
                    ORDER BY timestamp ASC
                """, (forum_id,)).fetchall()
                
                events = []
                for row in rows:
                    event = ParticipantEvent(
                        event_type=row["event_type"],
                        participant=row["participant"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        forum_id=row["forum_id"],
                        message=row["message"]
                    )
                    events.append(event)
                
                return events
        except sqlite3.Error as e:
            print(f"Error getting participant events: {e}")
        return []
    
    def save_forum_summary(self, forum_id: str, summary_type: str, content: str) -> bool:
        """Save a generated summary for a forum"""
        try:
            with self._get_connection() as conn:
                # Get current message count
                row = conn.execute(
                    "SELECT message_count FROM forums WHERE forum_id = ?", (forum_id,)
                ).fetchone()
                
                if not row:
                    return False
                
                message_count = row["message_count"]
                
                conn.execute("""
                    INSERT OR REPLACE INTO forum_summaries 
                    (forum_id, summary_type, content, generated_at, message_count_at_generation)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    forum_id,
                    summary_type,
                    content,
                    datetime.now().isoformat(),
                    message_count
                ))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error saving forum summary: {e}")
        return False
    
    def get_forum_summary(self, forum_id: str, summary_type: str = "brief") -> Optional[str]:
        """Get a saved summary for a forum"""
        try:
            with self._get_connection() as conn:
                row = conn.execute("""
                    SELECT content FROM forum_summaries 
                    WHERE forum_id = ? AND summary_type = ?
                """, (forum_id, summary_type)).fetchone()
                
                return row["content"] if row else None
        except sqlite3.Error as e:
            print(f"Error getting forum summary: {e}")
        return None
    
    def search_forums(self, query: str, user: str = None) -> List[Tuple[ForumMetadata, float]]:
        """Search forums by name, description, and content (simple text search)"""
        try:
            query_lower = query.lower()
            forums = self.list_forums(user=user, include_private=True)
            results = []
            
            for forum in forums:
                score = 0.0
                
                # Check forum name and description
                if query_lower in forum.name.lower():
                    score += 0.5
                if query_lower in forum.description.lower():
                    score += 0.3
                
                # Check tags
                for tag in forum.tags:
                    if query_lower in tag.lower():
                        score += 0.2
                
                # Check recent messages
                recent_messages = self.get_messages(forum.forum_id, limit=50)
                message_matches = sum(
                    1 for msg in recent_messages 
                    if query_lower in msg["content"].lower()
                )
                if message_matches > 0:
                    score += min(0.4, message_matches * 0.1)
                
                if score > 0:
                    results.append((forum, score))
            
            # Sort by score
            results.sort(key=lambda x: x[1], reverse=True)
            return results
            
        except Exception as e:
            print(f"Error searching forums: {e}")
        return []
    
    def _add_participant_event(self, conn, event: ParticipantEvent):
        """Add a participant event to the database"""
        conn.execute("""
            INSERT INTO participant_events (
                forum_id, event_type, participant, timestamp, message
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            event.forum_id,
            event.event_type,
            event.participant,
            event.timestamp.isoformat(),
            event.message
        ))
    
    def get_forum_config(self, forum_id: str) -> Optional[ForumConfig]:
        """Convert forum metadata to ForumConfig for LangGraph compatibility"""
        metadata = self.get_forum(forum_id)
        if not metadata:
            return None
        
        return ForumConfig(
            forum_id=metadata.forum_id,
            name=metadata.name,
            description=metadata.description,
            mode=metadata.mode,
            participants=metadata.participants,
            created_at=metadata.created_at,
            settings={"creator": metadata.creator, "tags": metadata.tags}
        )