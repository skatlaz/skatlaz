"""
Web Scraper Module - Complete implementation
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, urljoin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class WebScraper:
    """Professional web scraping with multiple features"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.max_depth = 2
        self.visited_urls = set()
        
    def scrape(self, prompt: str) -> str:
        """Main scraping interface"""
        # Extract URL from prompt
        url = self._extract_url(prompt)
        
        if not url:
            return self._scrape_search_query(prompt)
        
        return self._scrape_url(url)
    
    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text"""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!$&\'()*+,;=:@/]*)??'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None
    
    def _scrape_url(self, url: str) -> str:
        """Scrape a specific URL"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else "No title"
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract metadata
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extract links
            links = self._extract_links(soup, url)
            
            result = f"""🌐 **Web Scraping Results**
📄 URL: {url}
📌 Title: {title}
📝 Description: {description[:200]}

📖 **Main Content:**
{content[:1500]}

🔗 **Important Links Found:**
{self._format_links(links[:10])}

**Statistics:**
- Total content length: {len(content)} characters
- Links found: {len(links)}
- Scraped at: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return result
            
        except requests.RequestException as e:
            return f"❌ Error scraping URL: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Try common content containers
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.post-content', '.entry-content', '.article-content',
            '[role="main"]', '.main-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(separator='\n', strip=True)
                    if len(text) > len(content):
                        content = text
                if content:
                    break
        
        # If no content found, get body text
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
        
        # Clean up text
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all links from page"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Skip non-http links
            if not full_url.startswith(('http://', 'https://')):
                continue
                
            links.append({
                'url': full_url,
                'text': text[:100] if text else 'No text',
                'domain': urlparse(full_url).netloc
            })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def _format_links(self, links: List[Dict]) -> str:
        """Format links for display"""
        if not links:
            return "No links found."
        
        result = ""
        for i, link in enumerate(links[:10], 1):
            result += f"{i}. [{link['text'][:50]}] - {link['url']}\n"
        
        return result
    
    def _scrape_search_query(self, query: str) -> str:
        """Scrape based on search query"""
        # Extract search terms
        search_terms = re.sub(r'(scrape|extract|get|from|web|site)', '', query, flags=re.IGNORECASE)
        search_terms = search_terms.strip()
        
        if not search_terms:
            return "Please specify what you want to scrape or provide a URL."
        
        # Use DuckDuckGo HTML search (no API key needed)
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={search_terms}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('div', class_='result')
            
            if not results:
                return f"No search results found for '{search_terms}'."
            
            output = f"🔍 **Search Results for: {search_terms}**\n\n"
            
            for i, result in enumerate(results[:5], 1):
                title_elem = result.find('a', class_='result__a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                # Extract description
                desc_elem = result.find('a', class_='result__snippet')
                description = desc_elem.get_text(strip=True) if desc_elem else "No description"
                
                output += f"{i}. **{title}**\n"
                output += f"   URL: {url}\n"
                output += f"   📝 {description[:200]}\n\n"
            
            output += "\n💡 To scrape any of these URLs, use: scrape [URL]"
            return output
            
        except Exception as e:
            return f"Error performing search: {str(e)}"
