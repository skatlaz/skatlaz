# advanced_crawler.py
#pip install playwright beautifulsoup4 requests pillow chromium

# advanced_crawler.py
import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
import json
import re
from collections import Counter
from typing import Set, Dict, List
import base64
from PIL import Image
import io
import os

class AdvancedSiteAnalyzer:
    def __init__(self, url: str, max_pages: int = 30, max_depth: int = 2):
        self.seed_url = url
        self.domain = urlparse(url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.queue: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.results = {
            'site': self.domain,
            'description': '',
            'sections': [],
            'thumbnail': None,
            'thumbnail_path': None,
            'breadcrumbs': [],
            'search_results': [],
            'internal_pages': [],
            'content_index': {}
        }
        
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> Set[str]:
        return {
            'a', 'e', 'o', 'que', 'de', 'da', 'do', 'em', 'um', 'para', 'com',
            'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos',
            'como', 'mas', 'ao', 'ele', 'das', 'seu', 'sua', 'ou', 'quando',
            'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até',
            'isso', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem'
        }
    
    async def analyze(self, keyword: str = None):
        print(f"🚀 Iniciando crawler em {self.seed_url}")
        
        self.queue.append({
            'url': self.seed_url,
            'depth': 0,
            'parent': None
        })
        
        while self.queue and len(self.visited) < self.max_pages:
            item = self.queue.pop(0)
            
            if item['url'] in self.visited:
                continue
            
            self.visited.add(item['url'])
            print(f"📄 Processando ({len(self.visited)}/{self.max_pages}): {item['url']}")
            
            try:
                page_data = await self.process_page(item['url'], item['depth'])
                
                if item['depth'] == 0:
                    self.results['description'] = page_data['description']
                    self.results['breadcrumbs'] = page_data['breadcrumbs']
                    self.results['sections'] = page_data['sections']
                
                self.results['internal_pages'].append({
                    'url': item['url'],
                    'depth': item['depth'],
                    'title': page_data['title'],
                    'word_count': page_data['word_count']
                })
                
                self.index_content(item['url'], page_data)
                
                if item['depth'] < self.max_depth:
                    for link in page_data['internal_links']:
                        if (link not in self.visited and 
                            not any(q['url'] == link for q in self.queue) and
                            len(self.visited) + len(self.queue) < self.max_pages):
                            self.queue.append({
                                'url': link,
                                'depth': item['depth'] + 1,
                                'parent': item['url']
                            })
            
            except Exception as e:
                print(f"❌ Erro ao processar {item['url']}: {str(e)}")
        
        # Gera thumbnail da página principal
        print("📸 Gerando thumbnail do site...")
        self.results['thumbnail'] = await self.generate_thumbnail()
        
        if keyword:
            self.results['search_results'] = self.search_in_index(keyword)
        
        print(f"✅ Crawler finalizado. {len(self.visited)} páginas processadas.")
        return self.results
    
    async def process_page(self, url: str, depth: int) -> Dict:
        response = self.session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'noscript', 'iframe']):
            tag.decompose()
        
        main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile('content')) or soup.body
        text_content = main_content.get_text() if main_content else ''
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        title = ''
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '')
        
        description = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        if not description:
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                description = og_desc.get('content', '')
        
        breadcrumbs = self.extract_breadcrumbs(soup)
        
        sections = []
        if depth == 0:
            sections = self.extract_sections(soup)
        
        internal_links = self.extract_internal_links(soup, url)
        word_count = len(text_content.split())
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'breadcrumbs': breadcrumbs,
            'sections': sections,
            'internal_links': internal_links,
            'text_content': text_content[:10000],
            'word_count': word_count
        }
    
    async def generate_thumbnail(self):
        """Gera thumbnail GIF 420x420 da página principal"""
        browser = None
        try:
            print("  → Iniciando navegador headless...")
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            print(f"  → Navegando para {self.seed_url}...")
            await page.goto(self.seed_url, wait_until="networkidle", timeout=30000)
            
            # Aguarda um pouco mais
            await page.wait_for_timeout(2000)
            
            print("  → Capturando screenshot...")
            screenshot = await page.screenshot(type='png')
            
            await browser.close()
            
            print("  → Convertendo para GIF 420x420...")
            img = Image.open(io.BytesIO(screenshot))
            
            # Redimensiona mantendo proporção e corta para 420x420
            img.thumbnail((420, 420), Image.Resampling.LANCZOS)
            
            # Cria imagem quadrada 420x420 com fundo branco se necessário
            final_img = Image.new('RGB', (420, 420), (255, 255, 255))
            x = (420 - img.width) // 2
            y = (420 - img.height) // 2
            final_img.paste(img, (x, y))
            
            # Salva como GIF
            output_path = f"thumbnail-{int(asyncio.get_event_loop().time())}.gif"
            final_img.save(output_path, format='GIF')
            
            # Converte para base64
            with open(output_path, 'rb') as f:
                base64_str = base64.b64encode(f.read()).decode()
            
            self.results['thumbnail_path'] = output_path
            
            print(f"  ✅ Thumbnail salvo em: {output_path}")
            
            return f"data:image/gif;base64,{base64_str}"
            
        except Exception as e:
            print(f"  ❌ Erro ao gerar thumbnail: {str(e)}")
            if browser:
                await browser.close()
            return None
    
    def extract_breadcrumbs(self, soup: BeautifulSoup) -> List[Dict]:
        items = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
                    for item in data.get('itemListElement', []):
                        items.append({
                            'name': item.get('name', ''),
                            'url': item.get('item', '')
                        })
            except:
                pass
        
        if not items:
            breadcrumb_selectors = ['nav[aria-label="breadcrumb"]', '.breadcrumb', '.breadcrumbs']
            for selector in breadcrumb_selectors:
                nav = soup.select_one(selector)
                if nav:
                    for a in nav.find_all('a'):
                        items.append({
                            'name': a.get_text(strip=True),
                            'url': a.get('href', '')
                        })
                    break
        
        return items
    
    def extract_sections(self, soup: BeautifulSoup) -> List[Dict]:
        sections = []
        seen = set()
        
        nav_selectors = ['header', 'nav', '.menu', '.nav', '.navbar']
        for selector in nav_selectors:
            for nav in soup.select(selector):
                for a in nav.find_all('a', href=True):
                    href = a.get('href')
                    text = a.get_text(strip=True)
                    
                    if (href and text and href not in seen and 
                        len(text) > 1 and len(text) < 50 and
                        self.domain in href):
                        
                        seen.add(href)
                        full_url = urljoin(self.seed_url, href)
                        sections.append({
                            'name': text,
                            'url': full_url
                        })
        
        return sections[:20]
    
    def extract_internal_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            try:
                full_url = urljoin(current_url, href)
                parsed = urlparse(full_url)
                
                if (parsed.netloc == self.domain and 
                    not any(ext in full_url for ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip'])):
                    links.add(full_url.split('#')[0])
            except:
                pass
        
        return list(links)
    
    def index_content(self, url: str, page_data: Dict):
        words = re.findall(r'\b[a-záéíóúâêôãõç]{4,}\b', page_data['text_content'].lower())
        words = [w for w in words if w not in self.stopwords]
        
        word_freq = Counter(words)
        top_words = [{'word': w, 'count': c} for w, c in word_freq.most_common(20)]
        
        self.results['content_index'][url] = {
            'title': page_data['title'],
            'url': url,
            'top_words': top_words,
            'text_snippet': page_data['text_content'][:500],
            'word_count': page_data['word_count']
        }
    
    def search_in_index(self, keyword: str) -> List[Dict]:
        results = []
        keyword_lower = keyword.lower()
        keyword_words = [w for w in keyword_lower.split() if len(w) > 2]
        
        for url, data in self.results['content_index'].items():
            score = 0
            matched_words = []
            
            if keyword_lower in data['title'].lower():
                score += 10
                matched_words.append('título')
            
            for word in keyword_words:
                for tw in data['top_words']:
                    if word in tw['word']:
                        score += 3
                        matched_words.append(word)
                        break
            
            snippet_lower = data['text_snippet'].lower()
            for word in keyword_words:
                if word in snippet_lower:
                    score += 1
            
            if score > 0:
                snippet = self.generate_snippet(data['text_snippet'], keyword_lower)
                
                results.append({
                    'title': data['title'],
                    'url': url,
                    'score': score,
                    'matched_words': list(set(matched_words)),
                    'snippet': snippet
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:15]
    
    def generate_snippet(self, text: str, keyword: str, max_length: int = 200) -> str:
        text_lower = text.lower()
        index = text_lower.find(keyword)
        
        if index == -1:
            snippet = text[:max_length]
            return snippet + ('...' if len(text) > max_length else '')
        
        start = max(0, index - 100)
        end = min(len(text), index + len(keyword) + 100)
        snippet = text[start:end]
        
        if start > 0:
            snippet = '...' + snippet
        if end < len(text):
            snippet = snippet + '...'
        
        snippet = re.sub(f'({re.escape(keyword)})', r'<strong>\1</strong>', snippet, flags=re.IGNORECASE)
        
        return snippet
    
    def get_stats(self) -> Dict:
        return {
            'pages_crawled': len(self.visited),
            'max_pages': self.max_pages,
            'max_depth': self.max_depth,
            'domain': self.domain,
            'thumbnail_generated': bool(self.results['thumbnail']),
            'thumbnail_path': self.results.get('thumbnail_path'),
            'indexed_terms': sum(len(data['top_words']) for data in self.results['content_index'].values())
        }


async def main():
    analyzer = AdvancedSiteAnalyzer('https://www.uol.com.br', max_pages=15, max_depth=2)
    
    result = await analyzer.analyze('notícias')
    
    print("\n📊 STATS:")
    stats = analyzer.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🏠 SITE INFO:")
    print(f"Site: {result['site']}")
    print(f"Descrição: {result['description'][:200]}...")
    print(f"Thumbnail: {'✅ Gerado com sucesso' if result['thumbnail'] else '❌ Falha na geração'}")
    if result.get('thumbnail_path'):
        print(f"Arquivo thumbnail: {result['thumbnail_path']}")
    
    print("\n🔗 DEFAULT SECTIONS:")
    for section in result['sections'][:10]:
        print(f"  - {section['name']}: {section['url']}")
    
    if result['search_results']:
        print("\n🔍 SEARCH RESULTS:")
        for i, res in enumerate(result['search_results'][:5], 1):
            print(f"\n{i}. {res['title']}")
            print(f"   URL: {res['url']}")
            print(f"   Score: {res['score']}")
            print(f"   Snippet: {res['snippet'][:150]}...")
    
    # Salva resultado
    with open('crawler-result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n✅ Results saved on crawler-result.json")

if __name__ == '__main__':
    asyncio.run(main())
