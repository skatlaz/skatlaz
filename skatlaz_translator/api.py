from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.db_manager import DatabaseManager
from modules.db_translator import DatabaseTranslator
from modules.translator import Translator as ExternalTranslator
from modules.word_suggester import WordSuggester
from modules.word_definition import WordDefinition
from config import Config

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Inicializa módulos
db = DatabaseManager()
db_translator = DatabaseTranslator(db)
external_translator = ExternalTranslator()
suggester = WordSuggester(db)
definition = WordDefinition()

# Template HTML para a página principal
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skatlaz Translator API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .api-section {
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        .api-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .endpoint {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: monospace;
        }
        .method {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
        .url { color: #333; }
        .description {
            margin-top: 10px;
            color: #666;
        }
        .try-it {
            margin-top: 15px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 8px;
        }
        input, textarea, select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin: 5px;
            font-family: monospace;
        }
        button {
            padding: 8px 15px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #5a67d8;
        }
        .result {
            margin-top: 10px;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 4px;
            display: none;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 28px;
            font-weight: bold;
        }
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Skatlaz Translator API</h1>
        <p class="subtitle">Sistema de tradução inteligente com banco de dados local</p>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalWords">0</div>
                <div class="stat-label">Palavras no Banco</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalTranslations">0</div>
                <div class="stat-label">Traduções Registradas</div>
            </div>
        </div>
        
        <div class="api-section">
            <div class="api-title">📝 Tradução</div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/translate</span>
            </div>
            <div class="description">
                Traduz texto usando o banco de dados local (tradutor próprio)
            </div>
            <div class="try-it">
                <h4>Testar:</h4>
                <textarea id="translateText" rows="2" cols="40" placeholder="Texto para traduzir...">casa bonita</textarea>
                <select id="sourceLang">
                    <option value="pt">Português</option>
                    <option value="eng">Inglês</option>
                    <option value="es">Espanhol</option>
                </select>
                <select id="targetLang">
                    <option value="eng">Inglês</option>
                    <option value="pt">Português</option>
                    <option value="es">Espanhol</option>
                </select>
                <button onclick="testTranslate()">Traduzir</button>
                <div id="translateResult" class="result"></div>
            </div>
        </div>
        
        <div class="api-section">
            <div class="api-title">🔍 Sugestões</div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/suggest?word=palavra&lang=pt</span>
            </div>
            <div class="try-it">
                <h4>Testar:</h4>
                <input type="text" id="suggestWord" placeholder="Palavra para buscar...">
                <select id="suggestLang">
                    <option value="pt">Português</option>
                    <option value="eng">Inglês</option>
                </select>
                <button onclick="testSuggest()">Buscar</button>
                <div id="suggestResult" class="result"></div>
            </div>
        </div>
        
        <div class="api-section">
            <div class="api-title">📖 Definição</div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/definition?word=casa&lang=pt</span>
            </div>
            <div class="try-it">
                <h4>Testar:</h4>
                <input type="text" id="defWord" placeholder="Palavra para definir...">
                <select id="defLang">
                    <option value="pt">Português</option>
                    <option value="eng">Inglês</option>
                </select>
                <button onclick="testDefinition()">Definir</button>
                <div id="defResult" class="result"></div>
            </div>
        </div>
        
        <div class="api-section">
            <div class="api-title">📊 Estatísticas</div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/stats</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/most-used?lang=pt&limit=10</span>
            </div>
        </div>
    </div>
    
    <script>
        async function testTranslate() {
            const text = document.getElementById('translateText').value;
            const source = document.getElementById('sourceLang').value;
            const target = document.getElementById('targetLang').value;
            
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    text: text,
                    source_lang: source,
                    target_lang: target
                })
            });
            const data = await response.json();
            
            const resultDiv = document.getElementById('translateResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
                <strong>Tradução:</strong> ${data.translated_text}<br>
                <strong>Método:</strong> ${data.method}<br>
                <strong>Confiança:</strong> ${(data.confidence * 100).toFixed(1)}%<br>
                ${data.unknown_words.length ? `<strong>Palavras desconhecidas:</strong> ${data.unknown_words.join(', ')}` : ''}
            `;
        }
        
        async function testSuggest() {
            const word = document.getElementById('suggestWord').value;
            const lang = document.getElementById('suggestLang').value;
            
            const response = await fetch(`/api/suggest?word=${word}&lang=${lang}`);
            const data = await response.json();
            
            const resultDiv = document.getElementById('suggestResult');
            resultDiv.style.display = 'block';
            if (data.suggestions && data.suggestions.length) {
                resultDiv.innerHTML = '<strong>Sugestões:</strong><br>' + 
                    data.suggestions.map(s => `${s.word} (${s.lang})`).join('<br>');
            } else {
                resultDiv.innerHTML = 'Nenhuma sugestão encontrada.';
            }
        }
        
        async function testDefinition() {
            const word = document.getElementById('defWord').value;
            const lang = document.getElementById('defLang').value;
            
            const response = await fetch(`/api/definition?word=${word}&lang=${lang}`);
            const data = await response.json();
            
            const resultDiv = document.getElementById('defResult');
            resultDiv.style.display = 'block';
            if (data.definition) {
                resultDiv.innerHTML = `
                    <strong>Palavra:</strong> ${data.word}<br>
                    <strong>Tipo:</strong> ${data.word_type || 'N/A'}<br>
                    <strong>Definição:</strong> ${data.definition || 'N/A'}
                `;
            } else {
                resultDiv.innerHTML = 'Definição não encontrada.';
            }
        }
        
        async function loadStats() {
            const response = await fetch('/api/stats');
            const data = await response.json();
            document.getElementById('totalWords').textContent = data.total_words || 0;
            document.getElementById('totalTranslations').textContent = data.total_translations || 0;
        }
        
        loadStats();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Página inicial com documentação da API"""
    return render_template_string(INDEX_HTML)

@app.route('/api/translate', methods=['POST'])
def translate():
    """
    Endpoint de tradução
    POST /api/translate
    Body: {
        "text": "texto para traduzir",
        "source_lang": "pt",
        "target_lang": "eng"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Texto não fornecido'}), 400
        
        text = data['text']
        source_lang = data.get('source_lang', 'pt')
        target_lang = data.get('target_lang', 'eng')
        
        # Traduz usando o banco de dados local
        result = db_translator.translate_text(text, source_lang, target_lang)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': result['translated_text'],
            'method': result['method'],
            'confidence': result['confidence'],
            'unknown_words': result['unknown_words'],
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate/external', methods=['POST'])
def translate_external():
    """
    Endpoint de tradução usando API externa (fallback)
    POST /api/translate/external
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'pt')
        target_lang = data.get('target_lang', 'eng')
        
        translation = external_translator.translate(text, source_lang, target_lang)
        
        if translation:
            return jsonify({
                'success': True,
                'translated_text': translation,
                'method': 'external_api'
            })
        else:
            return jsonify({'error': 'Falha na tradução externa'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggest', methods=['GET'])
def suggest():
    """
    Endpoint de sugestões
    GET /api/suggest?word=casa&lang=pt
    """
    try:
        word = request.args.get('word', '')
        lang = request.args.get('lang', 'pt')
        
        if not word:
            return jsonify({'error': 'Palavra não fornecida'}), 400
        
        suggestions = suggester.suggest_words(word, lang, limit=10)
        
        return jsonify({
            'success': True,
            'word': word,
            'lang': lang,
            'suggestions': [dict(s) for s in suggestions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/definition', methods=['GET'])
def get_definition():
    """
    Endpoint de definição
    GET /api/definition?word=casa&lang=pt
    """
    try:
        word = request.args.get('word', '')
        lang = request.args.get('lang', 'pt')
        
        if not word:
            return jsonify({'error': 'Palavra não fornecida'}), 400
        
        # Mapeia para o formato da API
        api_lang = Config.API_LANG_MAP.get(lang, 'en')
        
        definition_data = definition.get_definition(word, api_lang)
        
        if definition_data:
            return jsonify({
                'success': True,
                'word': word,
                'lang': lang,
                'word_type': definition_data.get('meanings', [{}])[0].get('part_of_speech'),
                'definition': definition_data.get('meanings', [{}])[0].get('definition'),
                'full_data': definition_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Definição não encontrada'
            }), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Estatísticas do sistema"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Total de palavras
        cursor.execute('SELECT COUNT(*) as total FROM words_pt')
        total_pt = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM words_eng')
        total_eng = cursor.fetchone()['total']
        
        # Total de traduções
        cursor.execute('SELECT COUNT(*) as total FROM word_translate')
        total_translations = cursor.fetchone()['total']
        
        # Total de consultas no histórico
        cursor.execute('SELECT COUNT(*) as total FROM translation_history')
        total_queries = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_words_pt': total_pt,
            'total_words_eng': total_eng,
            'total_words': total_pt + total_eng,
            'total_translations': total_translations,
            'total_queries': total_queries
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/most-used', methods=['GET'])
def most_used():
    """Palavras mais usadas"""
    try:
        lang = request.args.get('lang', 'pt')
        limit = int(request.args.get('limit', 10))
        
        words = db.get_most_used_words(lang, limit)
        
        return jsonify({
            'success': True,
            'lang': lang,
            'words': [dict(w) for w in words]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'version': '1.0.0'
    })

def run_api():
    """Inicia o servidor API"""
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.API_DEBUG
    )

if __name__ == '__main__':
    run_api()
