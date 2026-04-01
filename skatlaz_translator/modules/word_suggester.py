import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager

class WordSuggester:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def suggest_words(self, word_pattern: str, lang: str = None, limit: int = 10):
        """
        Sugere palavras baseado em um padrão
        lang: 'pt', 'eng' ou None para todos
        """
        suggestions = []
        
        if lang is None or lang == 'pt':
            pt_results = self.db.search_words_like('words_pt', word_pattern)
            for result in pt_results[:limit]:
                suggestions.append({
                    'word': result['word'],
                    'lang': 'pt',
                    'type': result['word_type'],
                    'definition': result['definition']
                })
        
        if lang is None or lang == 'eng':
            eng_results = self.db.search_words_like('words_eng', word_pattern)
            for result in eng_results[:limit]:
                suggestions.append({
                    'word': result['word'],
                    'lang': 'eng',
                    'type': result['word_type'],
                    'definition': result['definition']
                })
        
        # Limita o número total de sugestões
        return suggestions[:limit]
    
    def suggest_translations(self, word_pattern: str, target_lang: str, limit: int = 10):
        """Sugere traduções para um padrão de palavra"""
        translations = self.db.search_words_like('word_translate', word_pattern, target_lang)
        
        suggestions = []
        for trans in translations[:limit]:
            suggestions.append({
                'word': trans['word'],
                'translation': trans['word_lang'],
                'lang': trans['lang']
            })
        
        return suggestions
    
    def get_similar_words(self, word: str, lang: str = 'pt', max_distance: int = 2):
        """
        Encontra palavras similares usando busca difusa
        (Implementação simples, pode ser melhorada com Levenshtein)
        """
        from difflib import get_close_matches
        
        if lang == 'pt':
            all_words = self.db.search_words_like('words_pt', '%')
        else:
            all_words = self.db.search_words_like('words_eng', '%')
        
        word_list = [w['word'] for w in all_words]
        similar = get_close_matches(word, word_list, n=10, cutoff=0.6)
        
        return similar
