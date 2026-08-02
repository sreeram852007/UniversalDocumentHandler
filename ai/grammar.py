"""
AI Grammar Checker - Free offline grammar and spelling check
"""

import re
from typing import List, Tuple


class GrammarChecker:
    """Simple grammar and spelling checker using rules"""
    
    # Common grammar rules
    GRAMMAR_RULES = [
        # Subject-verb agreement
        (r'\b(I|You|We|They)\s+([a-z]+)s\b', r'\1 \2'),
        (r'\b(He|She|It)\s+([a-z]+?)(?<!s)\b', r'\1 \2s'),
        
        # Article usage
        (r'\ban\s+([aeiou])', r'a \1'),  # Fix: a before consonant
        (r'\ba\s+([aeiou])', r'an \1'),  # Fix: an before vowel
        
        # Common misspellings
        (r'\bteh\b', 'the'),
        (r'\badn\b', 'and'),
        (r'\bu\b', 'you'),
        (r'\br\b', 'are'),
        (r'\b4\b', 'for'),
        (r'\b2\b', 'to'),
        (r'\bwanna\b', 'want to'),
        (r'\bgonna\b', 'going to'),
        
        # Double spaces
        (r'\s{2,}', ' '),
        
        # Sentence capitalization
        (r'(\.\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper()),
        (r'(^\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper()),
    ]
    
    def __init__(self):
        self.common_errors = {
            'teh': 'the',
            'adn': 'and',
            'u': 'you',
            'r': 'are',
            '4': 'for',
            '2': 'to',
            'wanna': 'want to',
            'gonna': 'going to',
            'ur': 'your',
            'btw': 'by the way',
            'idk': 'I don\'t know',
            'imo': 'in my opinion',
            'lol': 'laugh out loud',
        }
    
    def check(self, text: str) -> Tuple[str, List[str]]:
        """
        Check and correct grammar
        
        Args:
            text: Text to check
        
        Returns:
            Tuple of (corrected_text, list_of_suggestions)
        """
        corrections = []
        corrected = text
        
        # Apply grammar rules
        for pattern, replacement in self.GRAMMAR_RULES:
            if callable(replacement):
                corrected = re.sub(pattern, replacement, corrected)
            else:
                corrected = re.sub(pattern, replacement, corrected)
        
        # Check for common misspellings
        for error, correction in self.common_errors.items():
            if error in corrected.lower():
                # Simple replace with case sensitivity
                corrected = corrected.replace(error, correction)
                corrections.append(f"Fixed: '{error}' -> '{correction}'")
        
        # Check for repeated words
        repeated = re.findall(r'\b(\w+)\s+\1\b', corrected)
        for word in repeated:
            corrections.append(f"Repeated word: '{word} {word}'")
            corrected = re.sub(r'\b' + word + r'\s+' + word + r'\b', word, corrected)
        
        # Check for sentence fragments
        sentences = re.split(r'[.!?]\s+', corrected)
        for sentence in sentences:
            if sentence and len(sentence.split()) < 3:
                corrections.append(f"Possible sentence fragment: '{sentence}'")
        
        return corrected, corrections
    
    def get_suggestions(self, text: str) -> List[str]:
        """Get list of grammar suggestions without correcting"""
        _, suggestions = self.check(text)
        return suggestions
    
    def get_corrected_text(self, text: str) -> str:
        """Get corrected text without suggestions list"""
        corrected, _ = self.check(text)
        return corrected