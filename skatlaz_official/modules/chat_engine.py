"""
Chat Engine Module - Handles intelligent conversations with multiple LLM backends
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from .utils import logger, load_config

class ChatEngine:
    """Multi-backend chat engine with fallback support"""
    
    def __init__(self):
        self.config = load_config()
        self.api_keys = self._load_api_keys()
        self.conversation_history = []
        self.current_backend = "local"
        
        # Available backends
        self.backends = {
            "local": self._local_chat,
            "openai": self._openai_chat,
            "anthropic": self._anthropic_chat,
            "deepseek": self._deepseek_chat,
            "huggingface": self._huggingface_chat
        }
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment and config"""
        keys = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "huggingface": os.getenv("HUGGINGFACE_API_KEY", ""),
            "mistral": os.getenv("MISTRAL_API_KEY", "")
        }
        
        # Try loading from config file
        config_path = os.path.expanduser("~/.skatlaz_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_keys = json.load(f)
                    keys.update(file_keys)
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
                
        return keys
    
    def chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Main chat method with intelligent backend selection"""
        
        # Add to history
        self.conversation_history.append({"role": "user", "content": prompt})
        
        # Select backend
        backend = self._select_backend()
        
        try:
            # Get response from selected backend
            response = self.backends[backend](prompt, context)
            
            # Add to history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            logger.error(f"Backend {backend} failed: {e}")
            # Try fallback
            return self._fallback_chat(prompt)
    
    def _select_backend(self) -> str:
        """Intelligently select best available backend"""
        # Check if specific backend is forced
        if self.current_backend in self.backends:
            return self.current_backend
            
        # Try to use the most capable available backend
        if self.api_keys["openai"]:
            return "openai"
        elif self.api_keys["anthropic"]:
            return "anthropic"
        elif self.api_keys["deepseek"]:
            return "deepseek"
        elif self.api_keys["huggingface"]:
            return "huggingface"
        else:
            return "local"
    
    def _local_chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Local model inference using transformers"""
        try:
            # Try to import transformers
            from transformers import pipeline
            
            # Use a small but capable model
            generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-small",
                max_length=200,
                pad_token_id=50256
            )
            
            response = generator(prompt, max_length=200, num_return_sequences=1)
            return response[0]['generated_text']
            
        except ImportError:
            return self._simple_chat(prompt)
        except Exception as e:
            logger.error(f"Local model error: {e}")
            return self._simple_chat(prompt)
    
    def _openai_chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Chat with OpenAI GPT"""
        if not self.api_keys["openai"]:
            return "OpenAI API key not configured."
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['openai']}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": "You are Skatlaz, a helpful AI assistant."}
            ]
            
            if context:
                messages.extend(context)
            else:
                messages.extend(self.conversation_history[-5:])  # Last 5 messages
                
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"OpenAI API error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"Error calling OpenAI: {str(e)}"
    
    def _anthropic_chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Chat with Anthropic Claude"""
        if not self.api_keys["anthropic"]:
            return "Anthropic API key not configured."
            
        try:
            headers = {
                "x-api-key": self.api_keys["anthropic"],
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                return f"Claude API error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return f"Error calling Claude: {str(e)}"
    
    def _deepseek_chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Chat with DeepSeek"""
        if not self.api_keys["deepseek"]:
            return "DeepSeek API key not configured."
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['deepseek']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"DeepSeek API error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return f"Error calling DeepSeek: {str(e)}"
    
    def _huggingface_chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Chat with Hugging Face models"""
        if not self.api_keys["huggingface"]:
            return "HuggingFace API key not configured."
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['huggingface']}"
            }
            
            # Use Mistral-7B or similar
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 500}},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()[0]["generated_text"]
            else:
                return f"HuggingFace API error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"HuggingFace error: {e}")
            return f"Error calling HuggingFace: {str(e)}"
    
    def _simple_chat(self, prompt: str) -> str:
        """Simple rule-based chat for fallback"""
        responses = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! I'm Skatlaz, your AI assistant.",
            "how are you": "I'm functioning well! Ready to assist you.",
            "help": "I can help with chat, search, stories, code, and more! Type /help for details.",
            "weather": "To get weather information, please specify a city.",
            "search": "What would you like me to search for?",
            "story": "Tell me what kind of story you'd like!",
            "code": "What programming language and functionality do you need?"
        }
        
        prompt_lower = prompt.lower()
        for key, response in responses.items():
            if key in prompt_lower:
                return response
                
        return f"I understand you're asking about: {prompt[:100]}... Let me help you with that. For full functionality, please install transformers and set up API keys."
    
    def _fallback_chat(self, prompt: str) -> str:
        """Fallback when all backends fail"""
        return f"I'm currently operating in limited mode. Your question: '{prompt[:100]}...'\n\nTo enable full features, please:\n1. Install transformers: pip install transformers torch\n2. Set up API keys for OpenAI, Anthropic, or DeepSeek\n3. Configure Hugging Face access"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
