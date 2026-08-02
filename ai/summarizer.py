"""
AI Document Summarization - Free, local text summarization
Uses simple extractive summarization (no API calls needed)
"""

import re
import math
from collections import Counter
from typing import List, Dict


class DocumentSummarizer:
    """Free local document summarization using extractive methods"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'for', 'nor', 'on', 'at', 'to', 'by',
            'in', 'of', 'with', 'without', 'about', 'for', 'from', 'into', 'through',
            'during', 'including', 'etc', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall'
        }
    
    def summarize(self, text: str, num_sentences: int = 5) -> str:
        """
        Summarize text using extractive summarization
        
        Args:
            text: Input text to summarize
            num_sentences: Number of sentences in summary
        
        Returns:
            Summary text
        """
        if not text or len(text.strip()) < 100:
            return text
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        # Calculate word frequencies
        word_freq = self._calculate_word_frequencies(text)
        
        # Score sentences
        sentence_scores = self._score_sentences(sentences, word_freq)
        
        # Select top sentences
        selected_indices = sorted(
            range(len(sentence_scores)),
            key=lambda i: sentence_scores[i],
            reverse=True
        )[:num_sentences]
        
        # Sort selected sentences by original order
        selected_indices.sort()
        
        # Build summary
        summary = ' '.join([sentences[i] for i in selected_indices])
        
        return summary
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_word_frequencies(self, text: str) -> Dict[str, float]:
        """Calculate normalized word frequencies"""
        words = re.findall(r'\w+', text.lower())
        
        # Filter stop words
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        if not filtered_words:
            return {}
        
        # Count frequencies
        freq = Counter(filtered_words)
        
        # Normalize
        max_freq = max(freq.values()) if freq else 1
        normalized = {word: freq[word] / max_freq for word in freq}
        
        return normalized
    
    def _score_sentences(self, sentences: List[str], word_freq: Dict[str, float]) -> List[float]:
        """Score sentences based on word frequencies"""
        scores = []
        
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            score = sum([word_freq.get(w, 0) for w in words if w not in self.stop_words])
            
            # Boost sentences with more words
            if len(words) > 0:
                score = score / math.sqrt(len(words))
            
            scores.append(score)
        
        return scores
    
    def get_quick_summary(self, text: str) -> str:
        """Get a very short summary (2-3 sentences)"""
        return self.summarize(text, 3)
    
    def get_full_summary(self, text: str) -> str:
        """Get a longer summary (8-10 sentences)"""
        return self.summarize(text, 8)