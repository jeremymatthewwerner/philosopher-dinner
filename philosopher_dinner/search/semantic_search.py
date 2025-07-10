"""
Semantic Search Engine for Forums
Advanced natural language search across forum content with confidence scoring.
"""
import re
import math
from typing import List, Dict, Tuple, Optional, Set, Any
from datetime import datetime
from collections import Counter
from dataclasses import dataclass

from ..forum.database import ForumDatabase, ForumMetadata


@dataclass
class SearchResult:
    """A search result with metadata and confidence scoring"""
    forum: ForumMetadata
    confidence: float
    relevance_type: str  # "title", "content", "participant", "topic"
    matching_snippets: List[str]
    match_count: int


class SemanticForumSearch:
    """
    Advanced semantic search engine for philosophical forums.
    Uses TF-IDF, keyword matching, and philosophical domain knowledge.
    """
    
    def __init__(self, database: ForumDatabase):
        self.database = database
        
        # Philosophical domain knowledge
        self.philosophical_concepts = {
            "ethics": ["moral", "virtue", "good", "evil", "right", "wrong", "duty", "justice", "fairness"],
            "epistemology": ["knowledge", "truth", "belief", "certainty", "doubt", "experience", "reason"],
            "metaphysics": ["reality", "existence", "being", "substance", "causation", "identity", "time"],
            "aesthetics": ["beauty", "art", "sublime", "taste", "judgment", "creative", "harmony"],
            "logic": ["argument", "premise", "conclusion", "valid", "sound", "fallacy", "reasoning"],
            "politics": ["state", "government", "freedom", "liberty", "authority", "power", "society"],
            "consciousness": ["mind", "awareness", "perception", "thought", "consciousness", "self"],
            "religion": ["god", "divine", "sacred", "faith", "belief", "spiritual", "transcendent"]
        }
        
        # Expand concepts with synonyms and related terms
        self.concept_expansions = {
            "justice": ["fairness", "equity", "righteousness", "law", "order"],
            "truth": ["reality", "fact", "verity", "accuracy", "honesty"],
            "beauty": ["aesthetic", "attractive", "sublime", "elegant", "harmony"],
            "freedom": ["liberty", "autonomy", "independence", "free will", "choice"],
            "consciousness": ["awareness", "mind", "thought", "perception", "cognition"],
            "virtue": ["excellence", "moral", "character", "goodness", "integrity"],
            "knowledge": ["understanding", "wisdom", "learning", "cognition", "insight"]
        }
        
        # Philosopher specializations for enhanced matching
        self.philosopher_expertise = {
            "socrates": ["knowledge", "virtue", "ethics", "questioning", "dialogue"],
            "plato": ["reality", "forms", "justice", "politics", "knowledge"],
            "aristotle": ["virtue", "logic", "categories", "politics", "happiness"],
            "kant": ["duty", "categorical imperative", "reason", "morality", "knowledge"],
            "nietzsche": ["power", "morality", "culture", "individualism", "perspectivism"],
            "descartes": ["mind", "body", "doubt", "certainty", "method"],
            "hume": ["experience", "causation", "induction", "skepticism", "emotion"],
            "locke": ["experience", "government", "property", "tolerance", "education"],
            "confucius": ["virtue", "harmony", "education", "tradition", "society"],
            "buddha": ["suffering", "enlightenment", "compassion", "mindfulness", "peace"]
        }
    
    def search(self, query: str, user: str = None, max_results: int = 10) -> List[SearchResult]:
        """
        Perform comprehensive semantic search across forums.
        
        Args:
            query: Natural language search query
            user: User performing search (for access control)
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        # Normalize and analyze query
        normalized_query = self._normalize_query(query)
        query_concepts = self._extract_concepts(normalized_query)
        query_philosophers = self._extract_philosophers(normalized_query)
        
        # Get all accessible forums
        forums = self.database.list_forums(user=user, include_private=True)
        
        if not forums:
            return []
        
        # Score each forum
        results = []
        for forum in forums:
            result = self._score_forum(forum, normalized_query, query_concepts, query_philosophers)
            if result.confidence > 0.1:  # Only include relevant results
                results.append(result)
        
        # Sort by confidence and return top results
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:max_results]
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the search query"""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove punctuation except question marks (they're meaningful)
        normalized = re.sub(r'[^\w\s\?]', ' ', normalized)
        
        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _extract_concepts(self, query: str) -> Dict[str, float]:
        """Extract philosophical concepts from query with confidence scores"""
        concepts = {}
        query_words = set(query.split())
        
        # Direct concept matching
        for concept, keywords in self.philosophical_concepts.items():
            matches = sum(1 for keyword in keywords if keyword in query)
            if matches > 0:
                concepts[concept] = matches / len(keywords)
        
        # Expansion matching
        for main_concept, expansions in self.concept_expansions.items():
            if main_concept in query:
                concepts[main_concept] = concepts.get(main_concept, 0) + 1.0
            
            expansion_matches = sum(1 for exp in expansions if exp in query)
            if expansion_matches > 0:
                concepts[main_concept] = concepts.get(main_concept, 0) + (expansion_matches * 0.7)
        
        return concepts
    
    def _extract_philosophers(self, query: str) -> List[str]:
        """Extract philosopher names mentioned in query"""
        philosophers = []
        
        # Check for explicit philosopher names
        for philosopher in self.philosopher_expertise.keys():
            if philosopher in query:
                philosophers.append(philosopher)
        
        # Check for full names
        full_names = {
            "immanuel kant": "kant",
            "friedrich nietzsche": "nietzsche", 
            "rene descartes": "descartes",
            "david hume": "hume",
            "john locke": "locke"
        }
        
        for full_name, short_name in full_names.items():
            if full_name in query:
                philosophers.append(short_name)
        
        return philosophers
    
    def _score_forum(
        self, 
        forum: ForumMetadata, 
        query: str, 
        query_concepts: Dict[str, float],
        query_philosophers: List[str]
    ) -> SearchResult:
        """Score a forum's relevance to the search query"""
        
        total_score = 0.0
        relevance_types = []
        matching_snippets = []
        match_count = 0
        
        # Score 1: Title and description matching
        title_score = self._score_text_match(forum.name.lower(), query)
        desc_score = self._score_text_match(forum.description.lower(), query)
        
        if title_score > 0:
            total_score += title_score * 0.4  # Title matches are very important
            relevance_types.append("title")
            matching_snippets.append(f"Title: {forum.name}")
            match_count += 1
        
        if desc_score > 0:
            total_score += desc_score * 0.3  # Description matches are important
            relevance_types.append("content")
            matching_snippets.append(f"Description: {forum.description}")
            match_count += 1
        
        # Score 2: Participant matching
        participant_score = 0.0
        for participant in forum.participants:
            if participant in query_philosophers:
                participant_score += 1.0
                relevance_types.append("participant")
                matching_snippets.append(f"Participant: {participant.replace('_', ' ').title()}")
                match_count += 1
            
            # Check if query concepts match participant expertise
            if participant in self.philosopher_expertise:
                expertise = self.philosopher_expertise[participant]
                for concept, weight in query_concepts.items():
                    if concept in expertise:
                        participant_score += weight * 0.3
        
        total_score += participant_score * 0.2
        
        # Score 3: Tag matching
        tag_score = 0.0
        for tag in forum.tags:
            if tag.lower() in query:
                tag_score += 1.0
                relevance_types.append("topic")
                matching_snippets.append(f"Topic: {tag}")
                match_count += 1
        
        total_score += tag_score * 0.2
        
        # Score 4: Content analysis from recent messages
        content_score = self._score_forum_content(forum, query, query_concepts)
        total_score += content_score * 0.3
        
        if content_score > 0:
            relevance_types.append("content")
            match_count += 1
        
        # Score 5: Concept-based scoring
        concept_score = 0.0
        for concept, weight in query_concepts.items():
            # Check if forum participants are experts in this concept
            for participant in forum.participants:
                if participant in self.philosopher_expertise:
                    expertise = self.philosopher_expertise[participant]
                    if concept in expertise:
                        concept_score += weight * 0.5
        
        total_score += concept_score * 0.1
        
        # Normalize score (0-1 range)
        final_confidence = min(1.0, total_score)
        
        # Determine primary relevance type
        primary_relevance = relevance_types[0] if relevance_types else "general"
        
        return SearchResult(
            forum=forum,
            confidence=final_confidence,
            relevance_type=primary_relevance,
            matching_snippets=matching_snippets[:3],  # Top 3 snippets
            match_count=match_count
        )
    
    def _score_text_match(self, text: str, query: str) -> float:
        """Score how well text matches query using TF-IDF-like approach"""
        if not text or not query:
            return 0.0
        
        query_words = query.split()
        text_words = text.split()
        
        if not query_words or not text_words:
            return 0.0
        
        # Calculate term frequency
        text_freq = Counter(text_words)
        total_words = len(text_words)
        
        score = 0.0
        matched_terms = 0
        
        for query_word in query_words:
            if query_word in text_freq:
                # Term frequency score
                tf = text_freq[query_word] / total_words
                score += tf
                matched_terms += 1
        
        # Boost score for higher match ratio
        match_ratio = matched_terms / len(query_words)
        score *= (1 + match_ratio)
        
        return score
    
    def _score_forum_content(
        self, 
        forum: ForumMetadata, 
        query: str, 
        query_concepts: Dict[str, float]
    ) -> float:
        """Score forum based on actual message content"""
        # Get recent messages for content analysis
        messages = self.database.get_messages(forum.forum_id, limit=20)
        
        if not messages:
            return 0.0
        
        # Combine all message content
        content = " ".join([msg["content"].lower() for msg in messages])
        
        # Score based on query match
        content_score = self._score_text_match(content, query)
        
        # Boost score for concept matches in content
        concept_boost = 0.0
        for concept, weight in query_concepts.items():
            concept_keywords = self.philosophical_concepts.get(concept, [])
            for keyword in concept_keywords:
                if keyword in content:
                    concept_boost += weight * 0.1
        
        return content_score + concept_boost
    
    def suggest_search_terms(self, partial_query: str) -> List[str]:
        """Suggest search terms based on partial input"""
        suggestions = []
        partial = partial_query.lower()
        
        # Suggest philosophical concepts
        for concept in self.philosophical_concepts.keys():
            if concept.startswith(partial) or partial in concept:
                suggestions.append(concept)
        
        # Suggest philosopher names
        for philosopher in self.philosopher_expertise.keys():
            if philosopher.startswith(partial) or partial in philosopher:
                suggestions.append(philosopher.replace('_', ' ').title())
        
        # Suggest expanded terms
        for main_concept, expansions in self.concept_expansions.items():
            if main_concept.startswith(partial):
                suggestions.append(main_concept)
            for expansion in expansions:
                if expansion.startswith(partial):
                    suggestions.append(expansion)
        
        return sorted(set(suggestions))[:10]  # Return top 10 unique suggestions
    
    def get_search_analytics(self, query: str) -> Dict[str, Any]:
        """Get analytics about a search query"""
        normalized_query = self._normalize_query(query)
        concepts = self._extract_concepts(normalized_query)
        philosophers = self._extract_philosophers(normalized_query)
        
        return {
            "normalized_query": normalized_query,
            "detected_concepts": concepts,
            "mentioned_philosophers": philosophers,
            "complexity_score": len(concepts) + len(philosophers),
            "query_type": self._classify_query(normalized_query)
        }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of search query"""
        if "?" in query:
            return "question"
        elif any(word in query for word in ["vs", "versus", "compared to", "difference"]):
            return "comparison"
        elif any(word in query for word in ["what is", "define", "meaning"]):
            return "definition"
        elif any(philosopher in query for philosopher in self.philosopher_expertise.keys()):
            return "philosopher-specific"
        else:
            return "general"