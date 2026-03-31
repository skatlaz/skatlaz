#!/usr/bin/env python3
"""
Skatlaz AI - Mini Perplexity + AutoGPT + RAG Assistant System
A comprehensive AI assistant with modular architecture
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add modules directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from modules.chat_engine import ChatEngine
from modules.web_scraper import WebScraper
from modules.google_search import GoogleSearch
from modules.vector_memory import VectorMemory
from modules.agents import AgentSwarm
from modules.weather_api import WeatherAPI
from modules.content_generator import ContentGenerator
from modules.reasoning import ReasoningPipeline
from modules.learning_loop import LearningLoop
from modules.huggingface_apps import HuggingFaceApps
from modules.utils import logger, config

class SkatlazAI:
    """Main Skatlaz AI Assistant System"""
    
    def __init__(self):
        """Initialize all modules"""
        print("🤖 Skatlaz Iniciando...")
        
        # Initialize all modules
        self.chat_engine = ChatEngine()
        self.web_scraper = WebScraper()
        self.google_search = GoogleSearch()
        self.vector_memory = VectorMemory()
        self.agent_swarm = AgentSwarm()
        self.weather_api = WeatherAPI()
        self.content_generator = ContentGenerator()
        self.reasoning = ReasoningPipeline()
        self.learning_loop = LearningLoop()
        self.hf_apps = HuggingFaceApps()
        
        # Conversation history
        self.conversation_history = []
        self.current_mode = "chat"
        
        print("✅ Skatlaz AI inicializado com sucesso!")
        print("🎯 Modos disponíveis: chat, search, story, code, reason, agent, rag")
        
    def process_prompt(self, prompt: str, max_length: int = 255) -> str:
        """Process user prompt with intelligent routing"""
        
        # Truncate if needed
        if len(prompt) > max_length:
            prompt = prompt[:max_length]
            print(f"⚠️ Prompt truncado para {max_length} caracteres")
        
        print("🤖 Skatlaz pensando...")
        
        # Analyze prompt intent
        intent = self._analyze_intent(prompt)
        
        # Route to appropriate module based on intent
        try:
            if intent == "weather":
                return self.weather_api.get_weather(prompt)
                
            elif intent == "search":
                return self.google_search.search(prompt)
                
            elif intent == "web_scrape":
                return self.web_scraper.scrape(prompt)
                
            elif intent == "story":
                return self.content_generator.generate_story(prompt)
                
            elif intent == "article":
                return self.content_generator.generate_article(prompt)
                
            elif intent == "code":
                return self.content_generator.generate_code(prompt)
                
            elif intent == "image":
                return self.hf_apps.generate_image(prompt)
                
            elif intent == "text_gen":
                return self.hf_apps.generate_text(prompt)
                
            elif intent == "translation":
                return self.hf_apps.translate(prompt)
                
            elif intent == "summarize":
                return self.hf_apps.summarize(prompt)
                
            elif intent == "reason":
                return self.reasoning.reason(prompt)
                
            elif intent == "agent":
                return self.agent_swarm.process(prompt)
                
            elif intent == "rag":
                return self.vector_memory.query(prompt)
                
            else:
                # Default to chat with learning
                response = self.chat_engine.chat(prompt)
                self.learning_loop.record_interaction(prompt, response)
                return response
                
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return f"❌ Error: {str(e)}\n\nFalling back to chat mode..."
    
    def _analyze_intent(self, prompt: str) -> str:
        """Analyze prompt to determine intent"""
        prompt_lower = prompt.lower()
        
        # Intent mapping
        intents = {
            "weather": ["weather", "tempo", "clima", "previsão", "temperature", "rain"],
            "search": ["search", "buscar", "google", "find", "encontrar", "look up"],
            "web_scrape": ["scrape", "extract", "crawler", "website content", "page content"],
            "story": ["story", "história", "conto", "tale", "narrative", "fiction"],
            "article": ["article", "artigo", "blog post", "research", "paper"],
            "code": ["code", "código", "program", "script", "function", "class"],
            "image": ["image", "imagem", "picture", "photo", "generate image", "create image"],
            "text_gen": ["generate text", "creative writing", "poem", "poesia"],
            "translation": ["translate", "traduzir", "language", "idioma"],
            "summarize": ["summarize", "resumir", "summary", "brief"],
            "reason": ["reason", "think", "logic", "analyze", "analisar", "deduce"],
            "agent": ["agent", "autonomous", "task", "execute", "perform"],
            "rag": ["memory", "remember", "recall", "document", "knowledge base"]
        }
        
        for intent, keywords in intents.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return intent
                
        return "chat"
    
    def interactive_mode(self):
        """Run interactive chat mode"""
        print("\n" + "="*60)
        print("🎯 Skatlaz AI Interactive Mode")
        print("="*60)
        print("Comandos especiais:")
        print("  /mode [chat|search|story|code|agent|rag] - Change mode")
        print("  /help - Show this help")
        print("  /clear - Clear conversation")
        print("  /exit - Exit program")
        print("="*60 + "\n")
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 Você: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith("/"):
                    if user_input == "/exit":
                        print("👋 Até logo!")
                        break
                    elif user_input == "/clear":
                        self.conversation_history = []
                        print("✅ Conversa limpa!")
                        continue
                    elif user_input == "/help":
                        self._show_help()
                        continue
                    elif user_input.startswith("/mode"):
                        parts = user_input.split()
                        if len(parts) > 1:
                            self.current_mode = parts[1]
                            print(f"✅ Modo alterado para: {self.current_mode}")
                        else:
                            print(f"Modo atual: {self.current_mode}")
                        continue
                
                # Process prompt
                response = self.process_prompt(user_input)
                
                # Store in history
                self.conversation_history.append({
                    "user": user_input,
                    "assistant": response,
                    "mode": self.current_mode,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Display response
                print(f"\n🤖 Skatlaz: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Programa interrompido. Até logo!")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
                logger.error(f"Interactive mode error: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
📚 **Skatlaz AI - Guia de Uso**

🎯 **Modos de Operação:**
  - chat: Conversa normal com IA
  - search: Busca na web
  - story: Geração de histórias
  - code: Geração de código
  - agent: Agentes autônomos
  - rag: Memória vetorial

🔧 **Comandos:**
  /mode [modo] - Mudar modo de operação
  /clear - Limpar histórico
  /help - Mostrar esta ajuda
  /exit - Sair do programa

💡 **Exemplos:**
  - "Qual a previsão do tempo em São Paulo?"
  - "Crie uma história sobre um robô no espaço"
  - "Busque sobre inteligência artificial"
  - "Gere um código Python para calcular fibonacci"
  - "Analise logicamente: se A>B e B>C, então A>C?"
  
✨ **Recursos Especiais:**
  - Memória de longo prazo (RAG)
  - Agentes multi-função
  - Raciocínio lógico
  - Geração de imagens
  - Tradução automática
        """
        print(help_text)

def main():
    """Main entry point"""
    try:
        # Create config directory if needed
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("memory").mkdir(exist_ok=True)
        
        # Initialize and run
        skatlaz = SkatlazAI()
        skatlaz.interactive_mode()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
