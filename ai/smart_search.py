"""
AI Smart Search - Semantic search and intelligent document navigation
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import math


class SmartSearch:
    """Intelligent document search with relevance ranking"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'for', 'nor', 'on', 'at', 'to', 'by',
            'in', 'of', 'with', 'without', 'about', 'for', 'from', 'into', 'through',
            'during', 'including', 'etc', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall'
        }
    
    def search(self, text: str, query: str) -> List[Dict]:
        """
        Search for query in text with relevance ranking
        
        Args:
            text: Full text to search in
            query: Search query
        
        Returns:
            List of results with context and relevance scores
        """
        if not query or not text:
            return []
        
        # Split into paragraphs/sentences
        paragraphs = self._split_paragraphs(text)
        
        # Preprocess query
        query_words = self._preprocess(query)
        
        results = []
        
        for i, para in enumerate(paragraphs):
            # Calculate relevance score
            score = self._calculate_relevance(para, query_words)
            
            if score > 0:
                # Find exact matches
                matches = self._find_matches(para, query)
                results.append({
                    'paragraph_index': i,
                    'text': para,
                    'score': score,
                    'matches': matches,
                    'context': self._get_context(para, query, 50)
                })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _preprocess(self, text: str) -> List[str]:
        """Preprocess text for search"""
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 1]
    
    def _calculate_relevance(self, paragraph: str, query_words: List[str]) -> float:
        """Calculate relevance score between paragraph and query"""
        para_words = self._preprocess(paragraph)
        
        if not para_words or not query_words:
            return 0.0
        
        # Count matches
        matches = 0
        for qw in query_words:
            if qw in para_words:
                matches += 1
        
        # Calculate TF-IDF like score
        if matches == 0:
            return 0.0
        
        # Score based on match density and proximity
        match_score = matches / len(query_words)
        
        # Boost score for phrase matching
        phrase_score = 0
        for i in range(len(para_words) - len(query_words) + 1):
            if para_words[i:i+len(query_words)] == query_words:
                phrase_score += 1
        
        # Combine scores
        total_score = match_score * 0.7 + (phrase_score * 0.3)
        
        # Normalize
        return min(1.0, total_score)
    
    def _find_matches(self, paragraph: str, query: str) -> List[str]:
        """Find exact matches of query in paragraph"""
        matches = []
        words = paragraph.split()
        query_words = query.split()
        
        for i in range(len(words) - len(query_words) + 1):
            if ' '.join(words[i:i+len(query_words)]).lower() == query.lower():
                matches.append(' '.join(words[i:i+len(query_words)]))
        
        return matches
    
    def _get_context(self, paragraph: str, query: str, context_length: int = 50) -> str:
        """Get surrounding context for matches"""
        query_lower = query.lower()
        para_lower = paragraph.lower()
        
        # Find query position
        pos = para_lower.find(query_lower)
        
        if pos == -1:
            return paragraph[:context_length * 2] + '...'
        
        # Get surrounding text
        start = max(0, pos - context_length)
        end = min(len(paragraph), pos + len(query) + context_length)
        
        context = paragraph[start:end]
        
        # Add ellipsis
        if start > 0:
            context = '...' + context
        if end < len(paragraph):
            context = context + '...'
        
        return context
    
    def highlight_matches(self, text: str, query: str) -> str:
        """Highlight query matches in text"""
        if not query:
            return text
        
        # Simple case-insensitive replacement
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(r'<b>\g<0></b>', text)