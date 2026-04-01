import sys
import os
import uuid
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from modules.dictionary_importer import DictionaryImporter
from modules.db_translator import DatabaseTranslator
from modules.translator import Translator as ExternalTranslator
from modules.word_suggester import WordSuggester
from modules.word_definition import WordDefinition

class SkatlazTranslator:
    def __init__(self):
        self.db = DatabaseManager()
        self.importer = DictionaryImporter(self.db)
        self.db_translator = DatabaseTranslator(self.db)
        self.external_translator = ExternalTranslator()
        self.suggester = WordSuggester(self.db)
        self.definition = WordDefinition()
    
    def import_dictionaries(self):
        """Importa todos os dicionários do diretório lang (usa API externa)"""
        print("Iniciando importação de dicionários...")
        self.importer.scan_and_import()
        print("Importação concluída!")
    
    def translate(self, text: str, source_lang: str, target_lang: str, use_external: bool = False):
        """
        Traduz texto usando o tradutor próprio (baseado em banco de dados)
        Se use_external = True, usa API externa como fallback
        """
        print(f"Traduzindo '{text}' de {source_lang} para {target_lang}...")
        
        # Tenta usar o tradutor próprio primeiro
        result = self.db_translator.translate_text(text, source_lang, target_lang)
        
        # Se a confiança for baixa e tiver palavras desconhecidas, tenta API externa
        if use_external and (result['confidence'] < 0.5 or result['unknown_words']):
            print("Confiança baixa, tentando API externa...")
            external_result = self.external_translator.translate(text, source_lang, target_lang)
            
            if external_result:
                print(f"Tradução (API externa): {external_result}")
                return {
                    'translated_text': external_result,
                    'method': 'external_api',
                    'confidence': 1.0
                }
        
        print(f"Tradução: {result['translated_text']}")
        print(f"Método: {result['method']}")
        print(f"Confiança: {result['confidence']:.2%}")
        
        if result['unknown_words']:
            print(f"Palavras não encontradas: {', '.join(result['unknown_words'])}")
        
        return result
    
    def suggest_words(self, pattern: str, lang: str = None):
        """Sugere palavras baseado em um padrão"""
        print(f"Buscando sugestões para '{pattern}'...")
        suggestions = self.suggester.suggest_words(pattern, lang)
        
        if suggestions:
            print("\nSugestões encontradas:")
            for i, sugg in enumerate(suggestions, 1):
                print(f"{i}. {sugg['word']} ({sugg['lang']}) - {sugg.get('definition', 'Sem definição')}")
        else:
            print("Nenhuma sugestão encontrada.")
        
        return suggestions
    
    def get_word_info(self, word: str, lang: str):
        """Obtém informações detalhadas de uma palavra"""
        print(f"Buscando informações para '{word}'...")
        info = self.definition.get_definition(word, lang)
        
        if info:
            print(f"\nPalavra: {info['word']}")
            print(f"Fonética: {info.get('phonetic', 'N/A')}")
            print("\nSignificados:")
            for meaning in info['meanings']:
                print(f"  • {meaning['part_of_speech']}: {meaning['definition']}")
                if meaning.get('example'):
                    print(f"    Exemplo: {meaning['example']}")
        else:
            print("Informações não encontradas.")
        
        return info
    
    def show_stats(self):
        """Mostra estatísticas do sistema"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM words_pt')
        pt_count = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM words_eng')
        eng_count = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM word_translate')
        trans_count = cursor.fetchone()['total']
        
        conn.close()
        
        print("\n=== Estatísticas do Sistema ===")
        print(f"Palavras em português: {pt_count}")
        print(f"Palavras em inglês: {eng_count}")
        print(f"Traduções registradas: {trans_count}")
    
    def interactive_mode(self):
        """Modo interativo"""
        print("\n=== Skatlaz Translator ===\n")
        
        while True:
            print("\nOpções:")
            print("1. Importar dicionários (usa API externa)")
            print("2. Traduzir palavra/frase (tradutor próprio)")
            print("3. Traduzir com API externa (fallback)")
            print("4. Buscar sugestões de palavras")
            print("5. Buscar definição e informações")
            print("6. Ver estatísticas")
            print("7. Sair")
            
            option = input("\nEscolha uma opção: ").strip()
            
            if option == '1':
                self.import_dictionaries()
            
            elif option == '2':
                text = input("Digite o texto: ").strip()
                source = input("Idioma de origem (pt/eng/es): ").strip()
                target = input("Idioma de destino (pt/eng/es): ").strip()
                self.translate(text, source, target, use_external=False)
            
            elif option == '3':
                text = input("Digite o texto: ").strip()
                source = input("Idioma de origem (pt/eng/es): ").strip()
                target = input("Idioma de destino (pt/eng/es): ").strip()
                self.translate(text, source, target, use_external=True)
            
            elif option == '4':
                pattern = input("Digite o padrão de busca: ").strip()
                lang = input("Idioma (pt/eng, ou enter para todos): ").strip()
                self.suggest_words(pattern, lang if lang else None)
            
            elif option == '5':
                word = input("Digite a palavra: ").strip()
                lang = input("Idioma (pt/eng/es): ").strip()
                self.get_word_info(word, lang)
            
            elif option == '6':
                self.show_stats()
            
            elif option == '7':
                print("Saindo...")
                break
            
            else:
                print("Opção inválida!")

def main():
    parser = argparse.ArgumentParser(description='Skatlaz Translator')
    parser.add_argument('command', nargs='?', help='Comando a executar')
    parser.add_argument('args', nargs='*', help='Argumentos do comando')
    parser.add_argument('--api', action='store_true', help='Iniciar servidor API')
    
    args = parser.parse_args()
    
    translator = SkatlazTranslator()
    
    if args.api:
        # Inicia o servidor API
        from api import run_api
        print("Iniciando servidor API em http://{}:{}".format(Config.API_HOST, Config.API_PORT))
        run_api()
    elif args.command == 'import':
        translator.import_dictionaries()
    elif args.command == 'translate' and len(args.args) >= 3:
        result = translator.translate(args.args[0], args.args[1], args.args[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == 'suggest' and len(args.args) >= 1:
        lang = args.args[1] if len(args.args) > 1 else None
        translator.suggest_words(args.args[0], lang)
    elif args.command == 'info' and len(args.args) >= 2:
        translator.get_word_info(args.args[0], args.args[1])
    elif args.command == 'stats':
        translator.show_stats()
    else:
        # Modo interativo
        translator.interactive_mode()

if __name__ == "__main__":
    main()
