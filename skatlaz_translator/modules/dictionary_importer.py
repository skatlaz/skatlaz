import os
import sys
import uuid
from typing import List, Dict
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from modules.translator import Translator
from modules.word_definition import WordDefinition
from config import Config

class DictionaryImporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.translator = Translator()  # Usa API externa APENAS na importação
        self.definition_fetcher = WordDefinition()
    
    def scan_and_import(self):
        """Varre o diretório lang e importa todos os arquivos .txt"""
        lang_dir = Config.LANG_DIR
        
        if not os.path.exists(lang_dir):
            print(f"Diretório {lang_dir} não encontrado!")
            return
        
        for lang_code in os.listdir(lang_dir):
            lang_path = os.path.join(lang_dir, lang_code)
            
            if os.path.isdir(lang_path):
                words_file = os.path.join(lang_path, 'words.txt')
                
                if os.path.exists(words_file):
                    print(f"Importando palavras do idioma: {lang_code}")
                    self.import_words_from_file(words_file, lang_code)
    
    def import_words_from_file(self, file_path: str, lang_code: str):
        """Importa palavras de um arquivo .txt"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                words = [line.strip() for line in file if line.strip()]
            
            total_words = len(words)
            print(f"Total de palavras a importar: {total_words}")
            
            for i, word in enumerate(words, 1):
                print(f"Processando ({i}/{total_words}): {word}")
                
                # Busca definição usando API (apenas na importação)
                definition_data = self.definition_fetcher.get_definition(word, lang_code)
                word_type = None
                definition = None
                examples = None
                synonyms = None
                antonyms = None
                
                if definition_data:
                    if definition_data.get('meanings'):
                        word_type = definition_data['meanings'][0]['part_of_speech']
                        definition = definition_data['meanings'][0]['definition']
                        if definition_data['meanings'][0].get('example'):
                            examples = definition_data['meanings'][0]['example']
                
                # Adiciona ao banco de dados baseado no idioma
                guid = None
                if lang_code == 'pt':
                    guid = self.db.add_word_pt(word, word_type, definition, examples, synonyms, antonyms)
                elif lang_code == 'eng':
                    guid = str(uuid.uuid4())
                    self.db.add_word_eng(guid, word, 'placeholder', word_type, definition, examples, synonyms, antonyms)
                else:
                    # Para outros idiomas, cria na tabela de traduções
                    guid = str(uuid.uuid4())
                    self.db.add_translation(guid, lang_code, word, word)
                
                # Traduz para todos os outros idiomas usando API (apenas na importação)
                if guid and lang_code == 'pt':
                    self.translate_and_save(guid, word, lang_code)
                
                # Pequena pausa para não sobrecarregar APIs
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Erro ao importar arquivo {file_path}: {e}")
    
    def translate_and_save(self, word_guid: str, word: str, source_lang: str):
        """Traduz a palavra para todos os idiomas usando API (apenas importação)"""
        translations = self.translator.translate_to_all_languages(word, source_lang)
        
        for target_lang, translated_word in translations.items():
            if translated_word:
                # Salva a tradução no cache
                self.db.add_translation(word_guid, target_lang, word, translated_word)
                
                # Se o idioma de destino for inglês, também adiciona na tabela words_eng
                if target_lang == 'eng':
                    definition_data = self.definition_fetcher.get_definition(translated_word, 'eng')
                    word_type = None
                    definition = None
                    examples = None
                    
                    if definition_data and definition_data.get('meanings'):
                        word_type = definition_data['meanings'][0]['part_of_speech']
                        definition = definition_data['meanings'][0]['definition']
                        if definition_data['meanings'][0].get('example'):
                            examples = definition_data['meanings'][0]['example']
                    
                    eng_guid = str(uuid.uuid4())
                    self.db.add_word_eng(eng_guid, translated_word, word_guid, word_type, definition, examples)
                
                print(f"  Tradução para {target_lang}: {translated_word}")
