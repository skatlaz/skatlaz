import re
import sys
import os
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager

class DatabaseTranslator:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """
        Traduz texto usando o banco de dados local
        Retorna: {
            'translated_text': str,
            'method': str,  # 'exact_match', 'word_by_word', 'partial_match'
            'confidence': float,
            'unknown_words': list
        }
        """
        # Tokeniza o texto
        words = self._tokenize(text)
        
        translated_words = []
        unknown_words = []
        method_used = 'word_by_word'
        confidence_scores = []
        
        for word in words:
            # Limpa pontuação para busca
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Busca tradução exata
            translation = self.db.get_translation_from_db(clean_word, source_lang, target_lang)
            
            if translation:
                translated_words.append(translation)
                confidence_scores.append(1.0)
            else:
                # Tenta buscar palavras similares
                similar_words = self._find_similar_words(clean_word, source_lang)
                if similar_words:
                    # Pega a mais similar
                    best_match = similar_words[0]
                    translation = self.db.get_translation_from_db(best_match['word'], source_lang, target_lang)
                    if translation:
                        translated_words.append(translation)
                        confidence_scores.append(best_match['similarity'])
                        method_used = 'partial_match'
                    else:
                        translated_words.append(word)
                        unknown_words.append(word)
                        confidence_scores.append(0.0)
                else:
                    translated_words.append(word)
                    unknown_words.append(word)
                    confidence_scores.append(0.0)
        
        # Reconstrói o texto preservando pontuação
        translated_text = self._reconstruct_text(text, words, translated_words)
        
        # Calcula confiança média
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Registra no histórico
        self.db.add_translation_history(
            text, source_lang, target_lang, translated_text, method_used
        )
        
        return {
            'translated_text': translated_text,
            'method': method_used,
            'confidence': avg_confidence,
            'unknown_words': unknown_words
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza o texto em palavras e pontuação"""
        return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    
    def _reconstruct_text(self, original: str, tokens: List[str], translated_words: List[str]) -> str:
        """Reconstrói o texto com as palavras traduzidas"""
        result = []
        word_index = 0
        
        for token in tokens:
            if re.match(r'\w+', token, re.UNICODE):
                if word_index < len(translated_words):
                    result.append(translated_words[word_index])
                    word_index += 1
                else:
                    result.append(token)
            else:
                result.append(token)
        
        # Junta tudo, cuidando com espaços
        text_result = ''
        for i, part in enumerate(result):
            if i > 0 and not part[0] in '.,!?;:)]}' and not result[i-1][-1] in '([{':
                text_result += ' '
            text_result += part
        
        return text_result
    
    def _find_similar_words(self, word: str, lang: str, threshold: float = 0.6) -> List[Dict]:
        """Encontra palavras similares no banco de dados"""
        # Busca palavras que começam com o prefixo
        if lang == 'pt':
            similar = self.db.search_words_like('words_pt', word[:3])
        else:
            similar = self.db.search_words_like('words_eng', word[:3])
        
        # Calcula similaridade
        similarities = []
        for w in similar:
            similarity = SequenceMatcher(None, word.lower(), w['word'].lower()).ratio()
            if similarity >= threshold:
                similarities.append({
                    'word': w['word'],
                    'similarity': similarity
                })
        
        # Ordena por similaridade
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities
    
    def translate_phrase(self, phrase: str, source_lang: str, target_lang: str) -> Dict:
        """
        Traduz frase usando matching de frases completas
        """
        # Busca por frases completas no banco (implementar depois)
        return self.translate_text(phrase, source_lang, target_lang)
    
    def get_translation_suggestions(self, word: str, source_lang: str, target_lang: str, limit: int = 5) -> List[Dict]:
        """Obtém sugestões de tradução para uma palavra"""
        suggestions = []
        
        # Busca palavras similares
        similar_words = self._find_similar_words(word, source_lang, threshold=0.5)
        
        for similar in similar_words[:limit]:
            translation = self.db.get_translation_from_db(similar['word'], source_lang, target_lang)
            if translation:
                suggestions.append({
                    'original_word': similar['word'],
                    'translation': translation,
                    'similarity': similar['similarity']
                })
        
        return suggestions
