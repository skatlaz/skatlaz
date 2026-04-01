```markdown
# Skatlaz Translator - Intelligent Translation System

![Skatlaz Translator](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A complete translation system with a custom database-based translator, RESTful API, and interactive interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [How to Use](#how-to-use)
  - [Interactive Mode](#interactive-mode)
  - [Command Line](#command-line)
  - [API Server](#api-server)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Overview

Skatlaz Translator is a translation system that combines:
- **Custom translator** based on local database (does not depend on external APIs for translations)
- **Intelligent import** using free APIs only during initial registration
- **Complete RESTful API** for integration with other systems
- **Interactive web interface** for testing and demonstration
- **Suggestion system** with fuzzy search
- **Definitions and grammatical information** for words

## ✨ Features

### Custom Translator
- ✅ Database-based translation
- ✅ Translation cache for better performance
- ✅ Confidence system based on similarity
- ✅ External API fallback when needed
- ✅ Support for multiple languages (Portuguese, English, Spanish, French, German, Italian, Japanese, Chinese)
- ✅ Preserves punctuation and formatting

### Database System
- ✅ SQLite database with optimized indexes
- ✅ Translation history tracking
- ✅ Most used words statistics
- ✅ Word type classification (noun, verb, adjective, etc.)
- ✅ Examples, synonyms, and antonyms storage

### Import System
- ✅ Automatic scanning of dictionary files
- ✅ External API usage only during import
- ✅ Definitions and grammatical data fetching
- ✅ Translations to all supported languages
- ✅ Rate limiting to respect API limits

### RESTful API
- ✅ Complete REST endpoints
- ✅ CORS support for web applications
- ✅ JSON responses with detailed information
- ✅ Health check endpoint
- ✅ Interactive Swagger-like web interface

### Word Suggestions
- ✅ LIKE-based search patterns
- ✅ Fuzzy matching with similarity scoring
- ✅ Support for different languages
- ✅ Limited results for performance

### Definition System
- ✅ Integration with free dictionary APIs
- ✅ Part of speech identification
- ✅ Examples and usage contexts
- ✅ Fallback to English dictionary when needed

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Skatlaz Translator                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Interactive │  │  Command    │  │     REST API        │ │
│  │    Mode     │  │   Line      │  │   (Flask Server)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Core Modules                           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ • Database Translator (Local)  • External Translator   │ │
│  │ • Dictionary Importer          • Word Suggester        │ │
│  │ • Word Definition              • Database Manager      │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              SQLite Database                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ • words_pt      • words_eng      • word_translate      │ │
│  │ • phrases       • translation_history                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/skatlaz_translator.git
cd skatlaz_translator
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Prepare Dictionary Files
Create your dictionary files in the `lang` directory:
```
lang/
├── pt/
│   └── words.txt
├── eng/
│   └── words.txt
└── es/
    └── words.txt
```

Each `words.txt` should contain one word per line:
```
house
car
love
happiness
work
computer
```

### Step 4: Import Dictionaries
```bash
python main.py import
```

## 📁 Project Structure

```
skatlaz_translator/
├── main.py                    # Main application entry point
├── api.py                     # REST API server
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── database/
│   ├── __init__.py
│   └── db_manager.py          # Database operations
├── modules/
│   ├── __init__.py
│   ├── db_translator.py       # Database-based translator
│   ├── translator.py          # External API translator
│   ├── dictionary_importer.py # Dictionary import module
│   ├── word_suggester.py      # Word suggestion module
│   └── word_definition.py     # Word definition module
└── lang/                      # Dictionary files directory
    ├── pt/
    │   └── words.txt
    ├── eng/
    │   └── words.txt
    └── es/
        └── words.txt
```

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
class Config:
    DATABASE_PATH = 'translator.db'           # SQLite database file
    LANG_DIR = 'lang'                         # Dictionary files directory
    
    # External APIs (used only during import)
    TRANSLATION_API = 'https://api.mymemory.translated.net/get'
    DICTIONARY_API = 'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}'
    
    # Supported languages
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
    
    # API server settings
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    API_DEBUG = True
```

## 🎯 How to Use

### Interactive Mode

Launch the interactive menu:
```bash
python main.py
```

Interactive menu options:
```
=== Skatlaz Translator ===

Options:
1. Import dictionaries (uses external API)
2. Translate text (custom translator)
3. Translate with external API (fallback)
4. Search word suggestions
5. Search definition and information
6. View statistics
7. Exit
```

### Command Line

#### Import Dictionaries
```bash
python main.py import
```

#### Translate Text
```bash
python main.py translate "hello world" eng pt
```

#### Search Suggestions
```bash
python main.py suggest "hou" eng
```

#### Get Word Information
```bash
python main.py info "house" eng
```

#### View Statistics
```bash
python main.py stats
```

### API Server

Start the API server:
```bash
python main.py --api
```

Access the interactive web interface:
```
http://localhost:5000
```

## 🔌 API Endpoints

### GET `/`
Interactive web interface for testing the API.

### POST `/api/translate`
Translate text using the custom database-based translator.

**Request Body:**
```json
{
    "text": "hello world",
    "source_lang": "eng",
    "target_lang": "pt"
}
```

**Response:**
```json
{
    "success": true,
    "original_text": "hello world",
    "translated_text": "olá mundo",
    "method": "word_by_word",
    "confidence": 0.85,
    "unknown_words": [],
    "source_lang": "eng",
    "target_lang": "pt"
}
```

### POST `/api/translate/external`
Translate text using external API (fallback).

**Request Body:**
```json
{
    "text": "hello world",
    "source_lang": "eng",
    "target_lang": "pt"
}
```

### GET `/api/suggest`
Get word suggestions based on pattern.

**Parameters:**
- `word`: Search pattern (required)
- `lang`: Language filter (optional: pt/eng)

**Example:**
```
GET /api/suggest?word=hou&lang=eng
```

**Response:**
```json
{
    "success": true,
    "word": "hou",
    "lang": "eng",
    "suggestions": [
        {
            "word": "house",
            "lang": "eng",
            "definition": "a building for human habitation"
        },
        {
            "word": "hour",
            "lang": "eng",
            "definition": "a period of time equal to 60 minutes"
        }
    ]
}
```

### GET `/api/definition`
Get word definition and grammatical information.

**Parameters:**
- `word`: Word to define (required)
- `lang`: Language (required: pt/eng/es/fr/de)

**Example:**
```
GET /api/definition?word=house&lang=eng
```

**Response:**
```json
{
    "success": true,
    "word": "house",
    "lang": "eng",
    "word_type": "noun",
    "definition": "a building for human habitation",
    "full_data": {
        "word": "house",
        "phonetic": "/haʊs/",
        "meanings": [
            {
                "part_of_speech": "noun",
                "definition": "a building for human habitation",
                "example": "my house is small"
            }
        ]
    }
}
```

### GET `/api/stats`
Get system statistics.

**Response:**
```json
{
    "success": true,
    "total_words_pt": 1250,
    "total_words_eng": 980,
    "total_words": 2230,
    "total_translations": 8750,
    "total_queries": 342
}
```

### GET `/api/most-used`
Get most frequently used words.

**Parameters:**
- `lang`: Language (optional: pt/eng, default: pt)
- `limit`: Number of results (optional, default: 10)

**Example:**
```
GET /api/most-used?lang=eng&limit=5
```

**Response:**
```json
{
    "success": true,
    "lang": "eng",
    "words": [
        {
            "word": "house",
            "frequency": 45,
            "word_type": "noun"
        },
        {
            "word": "car",
            "frequency": 32,
            "word_type": "noun"
        }
    ]
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0"
}
```

## 🗄️ Database

The system uses SQLite with the following tables:

### words_pt
Portuguese words table
- `id`: Auto-increment primary key
- `guid`: Unique identifier (UUID)
- `word`: The word in Portuguese
- `word_type`: Part of speech (noun, verb, adjective, etc.)
- `definition`: Word definition
- `examples`: Usage examples
- `synonyms`: Related words
- `antonyms`: Opposite words
- `frequency`: Usage counter
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### words_eng
English words table
- Similar structure to words_pt
- `word_fk`: Foreign key to Portuguese word GUID

### word_translate
Translation cache table
- `word_guid`: Reference to source word
- `lang`: Target language code
- `word`: Source word
- `word_lang`: Translated word
- `confidence`: Translation confidence score
- `usage_count`: Number of times used
- `created_at`, `updated_at`: Timestamps

### translation_history
Translation query history
- `source_text`: Original text
- `source_lang`: Source language
- `target_lang`: Target language
- `translated_text`: Translated result
- `translation_method`: Method used (word_by_word, partial_match, etc.)
- `created_at`: Query timestamp

## 💡 Examples

### Example 1: Importing Dictionaries
```bash
$ python main.py import

Iniciando importação de dicionários...
Importando palavras do idioma: pt
Total de palavras a importar: 10
Processando (1/10): casa
  Tradução para eng: house
  Tradução para es: casa
  Tradução para fr: maison
Processando (2/10): carro
  Tradução para eng: car
  Tradução para es: coche
  Tradução para fr: voiture
...
Importação concluída!
```

### Example 2: Translating Text
```bash
$ python main.py translate "eu tenho uma casa grande" pt eng

Traduzindo 'eu tenho uma casa grande' de pt para eng...
Tradução: i have a big house
Método: word_by_word
Confiança: 95.00%
```

### Example 3: Using API
```bash
# Start the API server
$ python main.py --api

# In another terminal, make a request
$ curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"hello world","source_lang":"eng","target_lang":"pt"}'

{
    "success": true,
    "original_text": "hello world",
    "translated_text": "olá mundo",
    "method": "word_by_word",
    "confidence": 0.95,
    "unknown_words": [],
    "source_lang": "eng",
    "target_lang": "pt"
}
```

### Example 4: Searching Suggestions
```bash
$ curl "http://localhost:5000/api/suggest?word=hou&lang=eng"

{
    "success": true,
    "word": "hou",
    "lang": "eng",
    "suggestions": [
        {"word": "house", "lang": "eng", "definition": "a building for human habitation"},
        {"word": "hour", "lang": "eng", "definition": "a period of time equal to 60 minutes"}
    ]
}
```

## 🔧 Troubleshooting

### Database Locked Error
**Problem:** `sqlite3.OperationalError: database is locked`

**Solution:** Ensure no other processes are accessing the database. Restart the application.

### Import Fails with API Errors
**Problem:** External API calls fail during import

**Solution:** 
1. Check your internet connection
2. Verify API endpoints are accessible
3. The system will continue with available translations
4. You can retry the import later

### Translation Quality Issues
**Problem:** Low confidence translations

**Solution:**
1. Import more dictionary words
2. Use the suggestion system to verify words
3. Add custom translations directly to the database
4. Use external API fallback for critical translations

### API Server Won't Start
**Problem:** Port 5000 already in use

**Solution:**
```bash
# Change port in config.py
API_PORT = 5001

# Or kill the process using the port
lsof -i :5000
kill -9 <PID>
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to new functions
- Update README.md with new features
- Add tests for new functionality
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MyMemory API](https://mymemory.translated.net/) for translation services during import
- [Free Dictionary API](https://dictionaryapi.dev/) for word definitions
- [Flask](https://flask.palletsprojects.com/) for the REST API framework
- [SQLite](https://www.sqlite.org/) for the embedded database

## 📧 Contact

For questions, suggestions, or issues:
- Open an issue on GitHub
- Email: support@skatlaz.com
- Documentation: https://docs.skatlaz.com

---

**Made with ❤️ by Skatlaz Team**
