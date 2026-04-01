import os

class Config:
    DATABASE_PATH = 'translator.db'
    LANG_DIR = 'lang'
    
    # APIs gratuitas - Usadas APENAS no dictionary_importer
    TRANSLATION_API = 'https://api.mymemory.translated.net/get'
    DICTIONARY_API = 'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}'
    
    # API alternativa (LibreTranslate - pode ser self-hosted)
    LIBRETRANSLATE_API = 'https://translate.argosopentech.com/translate'
    
    # Idiomas suportados
    SUPPORTED_LANGUAGES = {
        'pt': 'português',
        'eng': 'inglês',
        'es': 'espanhol',
        'fr': 'francês',
        'de': 'alemão',
        'it': 'italiano',
        'ja': 'japonês',
        'zh': 'chinês'
    }
    
    # Mapeamento para APIs
    API_LANG_MAP = {
        'pt': 'pt',
        'eng': 'en',
        'es': 'es',
        'fr': 'fr',
        'de': 'de',
        'it': 'it',
        'ja': 'ja',
        'zh': 'zh'
    }
    
    # Configurações do banco de dados
    DB_CONFIG = {
        'check_same_thread': False
    }
    
    # Configurações do servidor API
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    API_DEBUG = True
