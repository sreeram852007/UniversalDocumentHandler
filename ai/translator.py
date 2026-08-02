"""
AI Translation - Simple free translation using dictionaries
(No API calls, completely offline)
"""

import json
import os
from typing import Dict, List


class DocumentTranslator:
    """Free offline translation using built-in dictionaries"""
    
    # Simple translation dictionaries (English to other languages)
    TRANSLATIONS = {
        'en_to_es': {
            'hello': 'hola',
            'goodbye': 'adiós',
            'thank you': 'gracias',
            'yes': 'sí',
            'no': 'no',
            'please': 'por favor',
            'document': 'documento',
            'file': 'archivo',
            'data': 'datos',
            'analysis': 'análisis',
            'report': 'informe',
            'summary': 'resumen',
            # Add more words as needed
        },
        'en_to_fr': {
            'hello': 'bonjour',
            'goodbye': 'au revoir',
            'thank you': 'merci',
            'yes': 'oui',
            'no': 'non',
            'please': 's\'il vous plaît',
            'document': 'document',
            'file': 'fichier',
            'data': 'données',
            'analysis': 'analyse',
            'report': 'rapport',
            'summary': 'résumé',
        },
        'en_to_de': {
            'hello': 'hallo',
            'goodbye': 'auf wiedersehen',
            'thank you': 'danke',
            'yes': 'ja',
            'no': 'nein',
            'please': 'bitte',
            'document': 'dokument',
            'file': 'datei',
            'data': 'daten',
            'analysis': 'analyse',
            'report': 'bericht',
            'summary': 'zusammenfassung',
        }
    }
    
    def __init__(self):
        self.supported_languages = ['Spanish', 'French', 'German']
        self.language_codes = {
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de'
        }
    
    def translate(self, text: str, target_language: str) -> str:
        """
        Translate text to target language
        
        Args:
            text: Input text
            target_language: Language to translate to
        
        Returns:
            Translated text
        """
        lang_code = self.language_codes.get(target_language)
        if not lang_code:
            return text
        
        # Simple word-by-word translation
        words = text.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = word.strip('.,!?;:')
            translated = self._translate_word(clean_word, lang_code)
            
            # Preserve punctuation
            if word != clean_word:
                translated += word[-1] if word[-1] in '.,!?;:' else ''
            
            translated_words.append(translated)
        
        return ' '.join(translated_words)
    
    def _translate_word(self, word: str, lang_code: str) -> str:
        """Translate a single word"""
        dict_key = f'en_to_{lang_code}'
        
        if dict_key in self.TRANSLATIONS:
            translation_dict = self.TRANSLATIONS[dict_key]
            
            # Check if word exists (case insensitive)
            lower_word = word.lower()
            if lower_word in translation_dict:
                translated = translation_dict[lower_word]
                # Preserve capitalization
                if word[0].isupper():
                    translated = translated.capitalize()
                return translated
        
        # Return original word if not found
        return word
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages