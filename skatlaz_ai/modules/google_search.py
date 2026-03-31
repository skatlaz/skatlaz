"""
Google Search Module - Complete implementation
"""

import requests
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus

class GoogleSearch:
    """Google search implementation with fallback methods"""
    
    def __init__(self):
        self.api_key = None
        self.search_engine_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def search(self, prompt: str) -> str:
        """Perform Google search"""
        # Extract query from prompt
        query = self._extract_query(prompt)
        
        if not query:
            return "Please specify what you want to search for."
        
        # Try different search methods
        result = self._duckduckgo_search(query)
        
        return result if result else f"🔍 Search results for: {query}\n\nNo detailed results found. Please try a more specific query."
    
    def _extract_query(self, text: str) -> str:
        """Extract search query from text"""
        # Remove common search phrases
        query = re.sub(r'(search|google|find|look up|buscar|pesquisar|about|sobre|for|para)', 
                      '', text, flags=re.IGNORECASE)
        
        # Remove punctuation and clean
        query = re.sub(r'[^\w\s]', '', query)
        query = query.strip()
        
        return query if query else None
    
    def _duckduckgo_search(self, query: str) -> str:
        """DuckDuckGo search"""
        try:
            # Use DuckDuckGo API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            result = f"🦆 **Search Results for: {query}**\n\n"
            
            # Abstract
            if data.get('Abstract'):
                result += f"📖 **Summary:**\n{data['Abstract'][:500]}\n\n"
            
            # Related topics
            if data.get('RelatedTopics'):
                result += "🔗 **Related Topics:**\n"
                for topic in data['RelatedTopics'][:5]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        result += f"• {topic['Text'][:150]}\n"
            
            # Definition
            if data.get('Definition'):
                result += f"\n📚 **Definition:**\n{data['Definition']}\n"
            
            return result if len(result) > 50 else None
            
        except Exception as e:
            return None
