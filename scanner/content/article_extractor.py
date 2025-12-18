"""
Article Extractor Module
Extracts article information from websites using JSON-LD, RSS, and HTML heuristics
"""

from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
from datetime import datetime
import re
import json

from bs4 import BeautifulSoup

try:
    import extruct
    EXTRUCT_AVAILABLE = True
except ImportError:
    EXTRUCT_AVAILABLE = False

from utils.http_client import HTTPClient


@dataclass
class ArticleData:
    """Represents extracted article data"""
    title: str
    url: str
    date_published: Optional[str] = None
    date_modified: Optional[str] = None
    author: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    word_count: int = 0
    h1_count: int = 0
    h2_count: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_description_length: int = 0
    canonical: Optional[str] = None
    indexable: bool = True
    status_code: int = 200
    has_schema: bool = False
    schema_type: Optional[str] = None
    image_url: Optional[str] = None
    reading_time_minutes: int = 0
    
    # SEO issues
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'date_published': self.date_published,
            'date_modified': self.date_modified,
            'author': self.author,
            'categories': self.categories,
            'tags': self.tags,
            'word_count': self.word_count,
            'h1_count': self.h1_count,
            'h2_count': self.h2_count,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'meta_description_length': self.meta_description_length,
            'canonical': self.canonical,
            'indexable': self.indexable,
            'status_code': self.status_code,
            'has_schema': self.has_schema,
            'schema_type': self.schema_type,
            'image_url': self.image_url,
            'reading_time_minutes': self.reading_time_minutes,
            'issues': self.issues,
            'warnings': self.warnings
        }


@dataclass
class ArticleExtractionResult:
    """Result of article extraction"""
    total_found: int = 0
    articles: List[ArticleData] = field(default_factory=list)
    with_schema: int = 0
    indexable_count: int = 0
    thin_content_count: int = 0
    missing_meta_count: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_found': self.total_found,
            'articles': [a.to_dict() for a in self.articles],
            'with_schema': self.with_schema,
            'with_schema_percent': round(self.with_schema / self.total_found * 100, 1) if self.total_found > 0 else 0,
            'indexable_count': self.indexable_count,
            'indexable_percent': round(self.indexable_count / self.total_found * 100, 1) if self.total_found > 0 else 0,
            'thin_content_count': self.thin_content_count,
            'thin_content_percent': round(self.thin_content_count / self.total_found * 100, 1) if self.total_found > 0 else 0,
            'missing_meta_count': self.missing_meta_count,
            'errors': self.errors
        }


class ArticleExtractor:
    """
    Extracts article information from websites
    
    Extraction priority:
    1. JSON-LD types: Article, NewsArticle, BlogPosting
    2. RSS/Atom items
    3. HTML heuristics (cards, <article>, meta tags)
    """
    
    # Article schema types
    ARTICLE_TYPES = [
        'Article',
        'NewsArticle', 
        'BlogPosting',
        'TechArticle',
        'ScholarlyArticle',
        'SocialMediaPosting',
        'Report',
        'WebPage'  # Sometimes used for articles
    ]
    
    # Minimum word count for non-thin content
    MIN_WORD_COUNT = 300
    
    def __init__(self):
        """Initialize article extractor"""
        self.http_client = HTTPClient(timeout=15)
        
        if not EXTRUCT_AVAILABLE:
            print("  [!] extruct not installed - JSON-LD extraction will be limited")
    
    def extract_from_urls(self, urls: List[str], max_articles: int = 50) -> ArticleExtractionResult:
        """
        Extract articles from a list of URLs
        
        Args:
            urls: List of URLs to extract from
            max_articles: Maximum articles to extract
            
        Returns:
            ArticleExtractionResult
        """
        result = ArticleExtractionResult()
        
        print(f"  [+] Extracting articles from {len(urls)} URLs...")
        
        for url in urls[:max_articles]:
            try:
                article = self.extract_single(url)
                if article:
                    result.articles.append(article)
                    
                    if article.has_schema:
                        result.with_schema += 1
                    if article.indexable:
                        result.indexable_count += 1
                    if article.word_count < self.MIN_WORD_COUNT:
                        result.thin_content_count += 1
                    if not article.meta_description:
                        result.missing_meta_count += 1
                        
            except Exception as e:
                result.errors.append(f"{url}: {str(e)}")
        
        result.total_found = len(result.articles)
        
        print(f"  [+] Extracted {result.total_found} articles")
        
        return result
    
    def extract_single(self, url: str) -> Optional[ArticleData]:
        """
        Extract article data from a single URL
        
        Args:
            url: Article URL
            
        Returns:
            ArticleData or None
        """
        try:
            response = self.http_client.get(url)
            
            if not response:
                return None
            
            article = ArticleData(
                title='',
                url=url,
                status_code=response.status_code
            )
            
            if response.status_code != 200:
                article.indexable = False
                article.issues.append(f"Non-200 status code: {response.status_code}")
                return article
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try JSON-LD extraction first
            schema_data = self._extract_from_jsonld(html_content, soup)
            if schema_data:
                article.has_schema = True
                article.schema_type = schema_data.get('type')
                article.title = schema_data.get('title', '')
                article.date_published = schema_data.get('datePublished')
                article.date_modified = schema_data.get('dateModified')
                article.author = schema_data.get('author')
                article.image_url = schema_data.get('image')
            
            # Extract from HTML (fills in gaps)
            self._extract_from_html(soup, article, url)
            
            # Analyze content
            self._analyze_content(soup, article)
            
            # Check indexability
            self._check_indexability(soup, article)
            
            # Calculate reading time
            if article.word_count > 0:
                article.reading_time_minutes = max(1, article.word_count // 200)
            
            # Generate issues and warnings
            self._generate_issues(article)
            
            return article
            
        except Exception as e:
            return None
    
    def _extract_from_jsonld(self, html_content: str, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract article data from JSON-LD"""
        
        if EXTRUCT_AVAILABLE:
            return self._extract_with_extruct(html_content)
        else:
            return self._extract_jsonld_manually(soup)
    
    def _extract_with_extruct(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Extract using extruct library"""
        try:
            data = extruct.extract(html_content, syntaxes=['json-ld'])
            
            for item in data.get('json-ld', []):
                item_type = item.get('@type', '')
                
                # Handle list types
                if isinstance(item_type, list):
                    item_type = item_type[0] if item_type else ''
                
                if item_type in self.ARTICLE_TYPES:
                    result = {
                        'type': item_type,
                        'title': item.get('headline') or item.get('name', ''),
                        'datePublished': item.get('datePublished'),
                        'dateModified': item.get('dateModified'),
                    }
                    
                    # Author extraction
                    author = item.get('author')
                    if author:
                        if isinstance(author, list):
                            author = author[0]
                        if isinstance(author, dict):
                            result['author'] = author.get('name', '')
                        else:
                            result['author'] = str(author)
                    
                    # Image extraction
                    image = item.get('image')
                    if image:
                        if isinstance(image, list):
                            image = image[0]
                        if isinstance(image, dict):
                            result['image'] = image.get('url', '')
                        else:
                            result['image'] = str(image)
                    
                    return result
            
            return None
            
        except Exception as e:
            return None
    
    def _extract_jsonld_manually(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract JSON-LD manually without extruct"""
        try:
            for script in soup.find_all('script', type='application/ld+json'):
                content = script.string
                if not content:
                    continue
                
                try:
                    data = json.loads(content)
                    
                    # Handle @graph structure
                    if isinstance(data, dict) and '@graph' in data:
                        items = data['@graph']
                    elif isinstance(data, list):
                        items = data
                    else:
                        items = [data]
                    
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        
                        item_type = item.get('@type', '')
                        if isinstance(item_type, list):
                            item_type = item_type[0] if item_type else ''
                        
                        if item_type in self.ARTICLE_TYPES:
                            result = {
                                'type': item_type,
                                'title': item.get('headline') or item.get('name', ''),
                                'datePublished': item.get('datePublished'),
                                'dateModified': item.get('dateModified'),
                            }
                            
                            author = item.get('author')
                            if author:
                                if isinstance(author, list):
                                    author = author[0]
                                if isinstance(author, dict):
                                    result['author'] = author.get('name', '')
                                else:
                                    result['author'] = str(author)
                            
                            return result
                
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def _extract_from_html(self, soup: BeautifulSoup, article: ArticleData, base_url: str):
        """Extract article data from HTML"""
        
        # Title
        if not article.title:
            # Try <title> tag
            title_tag = soup.find('title')
            if title_tag:
                article.meta_title = title_tag.get_text().strip()
                article.title = article.meta_title
            
            # Try <h1>
            h1 = soup.find('h1')
            if h1:
                article.title = h1.get_text().strip()
        else:
            title_tag = soup.find('title')
            if title_tag:
                article.meta_title = title_tag.get_text().strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            article.meta_description = meta_desc.get('content', '')
            article.meta_description_length = len(article.meta_description)
        
        # Canonical
        canonical = soup.find('link', rel='canonical')
        if canonical:
            article.canonical = canonical.get('href', '')
        
        # Author from meta tags
        if not article.author:
            author_meta = soup.find('meta', attrs={'name': 'author'})
            if author_meta:
                article.author = author_meta.get('content', '')
        
        # Categories/Tags from meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
            if keywords:
                article.tags = [k.strip() for k in keywords.split(',') if k.strip()]
        
        # Try to get date from HTML
        if not article.date_published:
            # Common date patterns
            date_selectors = [
                ('time', {'datetime': True}),
                ('span', {'class': re.compile(r'date|time|published', re.I)}),
                ('p', {'class': re.compile(r'date|time|published', re.I)}),
                ('div', {'class': re.compile(r'date|time|published', re.I)}),
            ]
            
            for tag, attrs in date_selectors:
                element = soup.find(tag, attrs)
                if element:
                    if element.get('datetime'):
                        article.date_published = element.get('datetime')
                    else:
                        article.date_published = element.get_text().strip()
                    break
    
    def _analyze_content(self, soup: BeautifulSoup, article: ArticleData):
        """Analyze article content"""
        
        # Count headings
        article.h1_count = len(soup.find_all('h1'))
        article.h2_count = len(soup.find_all('h2'))
        
        # Word count - try article tag first, then main, then body
        content_element = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find('div', class_=re.compile(r'content|article|post|entry', re.I)) or
            soup.find('body')
        )
        
        if content_element:
            # Remove scripts, styles, nav, footer
            for tag in content_element.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            text = content_element.get_text(separator=' ', strip=True)
            words = text.split()
            article.word_count = len(words)
    
    def _check_indexability(self, soup: BeautifulSoup, article: ArticleData):
        """Check if page is indexable"""
        
        # Check meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        if meta_robots:
            content = meta_robots.get('content', '').lower()
            if 'noindex' in content:
                article.indexable = False
                article.issues.append("Page has noindex directive")
        
        # Check X-Robots-Tag would require response headers (not available here)
        
        # Check canonical pointing elsewhere
        if article.canonical and article.canonical != article.url:
            # Normalize URLs for comparison
            parsed_canonical = urlparse(article.canonical)
            parsed_url = urlparse(article.url)
            
            if parsed_canonical.path != parsed_url.path:
                article.warnings.append("Canonical points to different URL")
    
    def _generate_issues(self, article: ArticleData):
        """Generate SEO issues and warnings"""
        
        # Title issues
        if not article.title:
            article.issues.append("Missing title")
        elif len(article.title) < 30:
            article.warnings.append("Title too short (< 30 chars)")
        elif len(article.title) > 60:
            article.warnings.append("Title too long (> 60 chars)")
        
        # Meta description issues
        if not article.meta_description:
            article.issues.append("Missing meta description")
        elif article.meta_description_length < 120:
            article.warnings.append("Meta description too short (< 120 chars)")
        elif article.meta_description_length > 160:
            article.warnings.append("Meta description too long (> 160 chars)")
        
        # H1 issues
        if article.h1_count == 0:
            article.issues.append("Missing H1 tag")
        elif article.h1_count > 1:
            article.warnings.append(f"Multiple H1 tags ({article.h1_count})")
        
        # Content issues
        if article.word_count < self.MIN_WORD_COUNT:
            article.warnings.append(f"Thin content ({article.word_count} words)")
        
        # Schema issues
        if not article.has_schema:
            article.warnings.append("No Article schema markup")
        
        # Date issues
        if not article.date_published:
            article.warnings.append("Missing published date")
        
        # Author issues
        if not article.author:
            article.warnings.append("Missing author information")
    
    def extract_from_rss(self, feed_items: List[Dict[str, Any]]) -> List[ArticleData]:
        """
        Create ArticleData from RSS feed items
        
        Args:
            feed_items: List of feed items (from RSSDiscovery)
            
        Returns:
            List of ArticleData (partial data)
        """
        articles = []
        
        for item in feed_items:
            article = ArticleData(
                title=item.get('title', ''),
                url=item.get('url', ''),
                date_published=item.get('published'),
                author=item.get('author'),
                categories=item.get('categories', [])
            )
            articles.append(article)
        
        return articles
