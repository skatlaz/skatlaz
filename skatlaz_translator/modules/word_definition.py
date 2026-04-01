import requests
import sys
import os
from typing import Optional, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class WordDefinition:
    def __init__(self):
        self.api_url_template = Config.DICTIONARY_API
    
    def get_definition(self, word: str, lang: str) -> Optional[Dict]:
        """
        Obtém definição e informações gramaticais da palavra
        lang: código do idioma ('en' para inglês, 'pt' para português)
        """
        # Mapeamento para API
        lang_map = {
            'eng': 'en',
            'pt': 'pt',
            'es': 'es',
            'fr': 'fr',
            'de': 'de'
        }
        
        api_lang = lang_map.get(lang, lang)
        url = self.api_url_template.format(lang=api_lang, word=word)
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return self._parse_definition(data[0])
            else:
                # Tenta com a API de inglês como fallback
                if api_lang != 'en':
                    return self.get_definition(word, 'eng')
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter definição: {e}")
            return None
    
    def _parse_definition(self, data: Dict) -> Dict:
        """Parseia os dados da API de dicionário"""
        result = {
            'word': data.get('word', ''),
            'meanings': [],
            'phonetic': data.get('phonetic', '')
        }
        
        for meaning in data.get('meanings', []):
            part_of_speech = meaning.get('partOfSpeech', '')
            
            for definition in meaning.get('definitions', [])[:2]:  # Pega até 2 definições
                result['meanings'].append({
                    'part_of_speech': part_of_speech,
                    'definition': definition.get('definition', ''),
                    'example': definition.get('example', '')
                })
        
        return result
    
    def get_word_type(self, word: str, lang: str) -> Optional[str]:
        """Obtém apenas o tipo gramatical da palavra"""
        definition_data = self.get_definition(word, lang)
        
        if definition_data and definition_data.get('meanings'):
            # Retorna o primeiro tipo gramatical encontrado
            return definition_data['meanings'][0]['part_of_speech']
        
        return None
