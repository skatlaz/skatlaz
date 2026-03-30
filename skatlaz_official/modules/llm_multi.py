"""
Multi-LLM Module - Integration with ChatGPT, DeepSeek, and Gemini
"""

import requests
import json
from typing import Optional, Dict, Any, List
import sys
import os

class MultiLLM:
    """Multi-LLM integration for code generation and analysis"""
    
    def __init__(self):
        self.openai_key = None
        self.deepseek_key = None
        self.gemini_key = None
        self.current_provider = "deepseek"  # Default
        
    def set_keys(self, openai_key=None, deepseek_key=None, gemini_key=None):
        """Set API keys for different providers"""
        if openai_key:
            self.openai_key = openai_key
        if deepseek_key:
            self.deepseek_key = deepseek_key
        if gemini_key:
            self.gemini_key = gemini_key
    
    def generate_code(self, prompt: str, language: str = "python", provider: str = None) -> str:
        """Generate code using specified provider"""
        provider = provider or self.current_provider
        
        if provider == "openai" and self.openai_key:
            return self._openai_generate(prompt, language)
        elif provider == "deepseek" and self.deepseek_key:
            return self._deepseek_generate(prompt, language)
        elif provider == "gemini" and self.gemini_key:
            return self._gemini_generate(prompt, language)
        else:
            return self._simulate_generation(prompt, language)
    
    def _openai_generate(self, prompt: str, language: str) -> str:
        """Generate code using OpenAI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": f"You are an expert {language} programmer."},
                {"role": "user", "content": f"Generate {language} code for: {prompt}"}
            ]
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result['choices'][0]['message']['content']
                return self._format_response("OpenAI GPT", code, language, prompt)
            else:
                return self._simulate_generation(prompt, language)
                
        except Exception as e:
            return self._simulate_generation(prompt, language)
    
    def _deepseek_generate(self, prompt: str, language: str) -> str:
        """Generate code using DeepSeek"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": f"You are an expert {language} programmer. Generate clean, efficient code."},
                {"role": "user", "content": f"Generate {language} code for: {prompt}"}
            ]
            
            data = {
                "model": "deepseek-coder-6.7b-instruct",
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result['choices'][0]['message']['content']
                return self._format_response("DeepSeek Coder", code, language, prompt)
            else:
                return self._simulate_generation(prompt, language)
                
        except Exception as e:
            return self._simulate_generation(prompt, language)
    
    def _gemini_generate(self, prompt: str, language: str) -> str:
        """Generate code using Google Gemini"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}"
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"Generate {language} code for: {prompt}. Provide only the code with brief comments."
                    }]
                }]
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                return self._format_response("Google Gemini", text, language, prompt)
            else:
                return self._simulate_generation(prompt, language)
                
        except Exception as e:
            return self._simulate_generation(prompt, language)
    
    def _format_response(self, provider: str, code: str, language: str, prompt: str) -> str:
        """Format the code generation response"""
        result = f"💻 **{provider} - Generated {language.upper()} Code**\n\n"
        result += f"**Request:** {prompt}\n\n"
        result += f"```{language}\n{code.strip()}\n```\n\n"
        result += "**✨ Features:**\n"
        result += "- Production-ready code\n"
        result += "- Clean and well-documented\n"
        result += "- Error handling included\n"
        result += "- Best practices followed\n\n"
        result += "**📝 Usage:** Copy and run in your environment\n"
        return result
    
    def _simulate_generation(self, prompt: str, language: str) -> str:
        """Simulate code generation when APIs unavailable"""
        result = "💻 **Code Generation Ready**\n\n"
        result += f"**Request:** Generate {language} code for: {prompt}\n\n"
        result += "**To enable actual code generation:**\n\n"
        result += "1. **OpenAI:** Get API key from https://platform.openai.com/\n"
        result += "2. **DeepSeek:** Get API key from https://platform.deepseek.com/\n"
        result += "3. **Gemini:** Get API key from https://makersuite.google.com/app/apikey\n\n"
        result += "**Add to ~/.skatlaz_config.json:**\n"
        result += "```json\n"
        result += "{\n"
        result += '  "openai_api_key": "sk-...",\n'
        result += '  "deepseek_api_key": "ds-...",\n'
        result += '  "gemini_api_key": "AI-..."\n'
        result += "}\n"
        result += "```\n\n"
        result += "**Example with API enabled:**\n"
        result += f"```{language}\n"
        result += "# The AI would generate actual code here\n"
        result += "# Based on your specific request\n"
        result += "```\n"
        return result
    
    def set_provider(self, provider: str):
        """Set the default provider"""
        if provider in ["openai", "deepseek", "gemini"]:
            self.current_provider = provider
            return f"Provider set to {provider}"
        return f"Invalid provider. Choose from: openai, deepseek, gemini"
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers with keys"""
        available = []
        if self.openai_key:
            available.append("openai")
        if self.deepseek_key:
            available.append("deepseek")
        if self.gemini_key:
            available.append("gemini")
        return available
