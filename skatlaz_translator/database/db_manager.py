import sqlite3
import uuid
from datetime import datetime
import os
import sys
from typing import List, Dict, Optional, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Obtém uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path, **Config.DB_CONFIG)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializa as tabelas do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela para palavras em português
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words_pt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT UNIQUE NOT NULL,
                word TEXT NOT NULL,
                word_type TEXT,
                definition TEXT,
                examples TEXT,
                synonyms TEXT,
                antonyms TEXT,
                frequency INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para palavras em inglês
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words_eng (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT UNIQUE NOT NULL,
                word TEXT NOT NULL,
                word_fk TEXT NOT NULL,
                word_type TEXT,
                definition TEXT,
                examples TEXT,
                synonyms TEXT,
                antonyms TEXT,
                frequency INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_fk) REFERENCES words_pt(guid)
            )
        ''')
        
        # Tabela para traduções (cache de traduções)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_translate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_guid TEXT NOT NULL,
                lang TEXT NOT NULL,
                word TEXT NOT NULL,
                word_lang TEXT NOT NULL,
                confidence FLOAT DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_guid) REFERENCES words_pt(guid),
                UNIQUE(word_guid, lang)
            )
        ''')
        
        # Tabela para frases/expressões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT UNIQUE NOT NULL,
                phrase TEXT NOT NULL,
                lang TEXT NOT NULL,
                translation_guid TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para histórico de traduções
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                source_lang TEXT NOT NULL,
                target_lang TEXT NOT NULL,
                translated_text TEXT,
                translation_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices para melhor performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_pt_word ON words_pt(word)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_eng_word ON words_eng(word)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_translate_word_guid ON word_translate(word_guid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_translate_lang ON word_translate(lang)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrases_lang ON phrases(lang)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_created ON translation_history(created_at)')
        
        conn.commit()
        conn.close()
    
    def add_word_pt(self, word, word_type=None, definition=None, examples=None, synonyms=None, antonyms=None):
        """Adiciona uma palavra na tabela de português"""
        guid = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO words_pt (guid, word, word_type, definition, examples, synonyms, antonyms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (guid, word, word_type, definition, examples, synonyms, antonyms))
            conn.commit()
            return guid
        except sqlite3.IntegrityError:
            # Palavra já existe, buscar o guid existente e atualizar frequência
            cursor.execute('SELECT guid FROM words_pt WHERE word = ?', (word,))
            result = cursor.fetchone()
            if result:
                cursor.execute('UPDATE words_pt SET frequency = frequency + 1, updated_at = CURRENT_TIMESTAMP WHERE guid = ?', (result['guid'],))
                conn.commit()
            return result['guid'] if result else None
        finally:
            conn.close()
    
    def add_word_eng(self, guid, word, word_fk, word_type=None, definition=None, examples=None, synonyms=None, antonyms=None):
        """Adiciona uma palavra na tabela de inglês"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO words_eng (guid, word, word_fk, word_type, definition, examples, synonyms, antonyms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (guid, word, word_fk, word_type, definition, examples, synonyms, antonyms))
            conn.commit()
        except sqlite3.IntegrityError:
            cursor.execute('UPDATE words_eng SET frequency = frequency + 1, updated_at = CURRENT_TIMESTAMP WHERE word = ?', (word,))
            conn.commit()
        finally:
            conn.close()
    
    def add_translation(self, word_guid, lang, word, word_lang, confidence=1.0):
        """Adiciona ou atualiza uma tradução"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO word_translate (word_guid, lang, word, word_lang, confidence, usage_count)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(word_guid, lang) DO UPDATE SET
                    word_lang = excluded.word_lang,
                    confidence = (confidence + excluded.confidence) / 2,
                    usage_count = usage_count + 1,
                    updated_at = CURRENT_TIMESTAMP
            ''', (word_guid, lang, word, word_lang, confidence))
            conn.commit()
        finally:
            conn.close()
    
    def get_translation_from_db(self, word: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Busca tradução no banco de dados local"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if source_lang == 'pt':
                # Busca a palavra em português
                cursor.execute('SELECT guid FROM words_pt WHERE word = ?', (word,))
                result = cursor.fetchone()
                
                if result:
                    # Busca a tradução para o idioma alvo
                    cursor.execute('''
                        SELECT word_lang FROM word_translate 
                        WHERE word_guid = ? AND lang = ?
                    ''', (result['guid'], target_lang))
                    translation = cursor.fetchone()
                    
                    if translation:
                        # Atualiza contador de uso
                        cursor.execute('''
                            UPDATE word_translate SET usage_count = usage_count + 1 
                            WHERE word_guid = ? AND lang = ?
                        ''', (result['guid'], target_lang))
                        conn.commit()
                        return translation['word_lang']
            
            elif target_lang == 'pt':
                # Busca a palavra no idioma de origem e depois a tradução para português
                # Isso requer uma busca reversa
                cursor.execute('''
                    SELECT wt.word_lang FROM word_translate wt
                    INNER JOIN words_pt wp ON wt.word_guid = wp.guid
                    WHERE wt.lang = ? AND wt.word_lang = ?
                ''', (source_lang, word))
                result = cursor.fetchone()
                
                if result:
                    return result['word_lang']
            
            return None
            
        finally:
            conn.close()
    
    def get_word_by_guid(self, guid):
        """Busca palavra por GUID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM words_pt WHERE guid = ?', (guid,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_translations(self, word_guid):
        """Busca todas as traduções de uma palavra"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM word_translate WHERE word_guid = ? ORDER BY usage_count DESC
        ''', (word_guid,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_words_like(self, table, word_pattern, lang=None):
        """Busca palavras com LIKE"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if table == 'words_pt':
            query = "SELECT * FROM words_pt WHERE word LIKE ? ORDER BY word"
            cursor.execute(query, (f'%{word_pattern}%',))
        elif table == 'words_eng':
            query = "SELECT * FROM words_eng WHERE word LIKE ? ORDER BY word"
            cursor.execute(query, (f'%{word_pattern}%',))
        elif table == 'word_translate' and lang:
            query = "SELECT * FROM word_translate WHERE word LIKE ? AND lang = ? ORDER BY word"
            cursor.execute(query, (f'%{word_pattern}%', lang))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_translation_history(self, source_text, source_lang, target_lang, translated_text, method):
        """Registra histórico de tradução"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO translation_history (source_text, source_lang, target_lang, translated_text, translation_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_text, source_lang, target_lang, translated_text, method))
        conn.commit()
        conn.close()
    
    def get_most_used_words(self, lang='pt', limit=50):
        """Obtém as palavras mais usadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if lang == 'pt':
            cursor.execute('''
                SELECT word, frequency, word_type FROM words_pt 
                ORDER BY frequency DESC LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT word, frequency, word_type FROM words_eng 
                ORDER BY frequency DESC LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
