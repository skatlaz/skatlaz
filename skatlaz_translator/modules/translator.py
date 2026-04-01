import requests
import time
from typing import Optional, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class Translator:
    def __init__(self):
        self.api_url = Config.TRANSLATION_API
        self.last_request = 0
        self.min_interval = 1  # 1 segundo entre requisições
    
    def _wait_for_rate_limit(self):
        """Aguarda para não exceder o limite da API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request = time.time()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Traduz texto usando a API gratuita MyMemory
        source_lang: código do idioma de origem (ex: 'pt')
        target_lang: código do idioma de destino (ex: 'eng')
        """
        self._wait_for_rate_limit()
        
        # Mapeamento de idiomas para a API
        lang_map = {
            'pt': 'pt',
            'eng': 'en',
            'es': 'es',
            'fr': 'fr',
            'de': 'de'
        }
        
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        try:
            params = {
                'q': text,
                'langpair': f'{source}|{target}'
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'responseData' in data and 'translatedText' in data['responseData']:
                return data['responseData']['translatedText']
            
            return None
            
        except Exception as e:
            print(f"Erro na tradução: {e}")
            return None
    
    def translate_to_all_languages(self, text: str, source_lang: str) -> Dict[str, str]:
        """Traduz texto para todos os idiomas suportados"""
        translations = {}
        
        for target_lang in Config.SUPPORTED_LANGUAGES.keys():
            if target_lang != source_lang:
                translated = self.translate(text, source_lang, target_lang)
                if translated:
                    translations[target_lang] = translated
        
        return translations
