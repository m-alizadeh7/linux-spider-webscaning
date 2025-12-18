"""
URL Sampler Module
Provides intelligent URL sampling for efficient scanning
"""

from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
from enum import Enum
import re
from bs4 import BeautifulSoup
from utils.http_client import HTTPClient


class URLType(Enum):
    """Type of URL based on content"""
    HOMEPAGE = "homepage"
    ARTICLE = "article"
    PRODUCT = "product"
    CATEGORY = "category"
    PAGE = "page"
    OTHER = "other"


@dataclass
class SampledURL:
    """Represents a sampled URL"""
    url: str
    url_type: URLType
    depth: int = 0
    source: str = "crawl"  # sitemap, rss, crawl
    priority: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'type': self.url_type.value,
            'depth': self.depth,
            'source': self.source,
            'priority': self.priority
        }


@dataclass
class SamplerResult:
    """Result of URL sampling"""
    homepage: Optional[str] = None
    articles: List[SampledURL] = field(default_factory=list)
    products: List[SampledURL] = field(default_factory=list)
    categories: List[SampledURL] = field(default_factory=list)
    pages: List[SampledURL] = field(default_factory=list)
    all_urls: List[SampledURL] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'homepage': self.homepage,
            'articles': [u.to_dict() for u in self.articles],
            'products': [u.to_dict() for u in self.products],
            'categories': [u.to_dict() for u in self.categories],
            'pages': [u.to_dict() for u in self.pages],
            'total_urls': len(self.all_urls)
        }


class URLSampler:
    """
    Intelligent URL sampler for website analysis
    
    Features:
    - Classifies URLs by type (article, product, category, etc.)
    - Samples top-N URLs per type
    - Avoids crawling entire website
    - Uses sitemaps and RSS as primary sources
    """
    
    # URL patterns for classification
    ARTICLE_PATTERNS = [
        r'/blog/',
        r'/news/',
        r'/article/',
        r'/post/',
        r'/\d{4}/\d{2}/',  # Date patterns like /2024/01/
        r'/\d{4}/\d{2}/\d{2}/',
        r'-news',
        r'-article',
        r'/p/',
    ]
    
    PRODUCT_PATTERNS = [
        r'/product/',
        r'/products/',
        r'/shop/',
        r'/store/',
        r'/item/',
        r'/p/',
        r'/pd/',
        r'/buy/',
        r'/goods/',
        r'-p-\d+',
        r'/catalog/',
    ]
    
    CATEGORY_PATTERNS = [
        r'/category/',
        r'/categories/',
        r'/cat/',
        r'/c/',
        r'/collection/',
        r'/collections/',
        r'/tag/',
        r'/tags/',
        r'/topic/',
        r'/archive/',
    ]
    
    PAGE_PATTERNS = [
        r'/about',
        r'/contact',
        r'/faq',
        r'/help',
        r'/terms',
        r'/privacy',
        r'/policy',
        r'/page/',
    ]
    
    # Patterns to skip
    SKIP_PATTERNS = [
        r'/cdn-cgi/',
        r'/wp-content/',
        r'/wp-includes/',
        r'/wp-admin/',
        r'/admin/',
        r'/login',
        r'/logout',
        r'/register',
        r'/cart',
        r'/checkout',
        r'/account',
        r'\.(jpg|jpeg|png|gif|svg|css|js|pdf|zip|woff|woff2)$',
        r'/feed/',
        r'/rss',
        r'/sitemap',
        r'#',
        r'\?',
    ]
    
    def __init__(self, max_per_type: int = 10, max_depth: int = 2):
        """
        Initialize URL sampler
        
        Args:
            max_per_type: Maximum URLs to sample per type
            max_depth: Maximum crawl depth
        """
        self.http_client = HTTPClient(timeout=10)
        self.max_per_type = max_per_type
        self.max_depth = max_depth
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns"""
        return {
            'article': [re.compile(p, re.I) for p in self.ARTICLE_PATTERNS],
            'product': [re.compile(p, re.I) for p in self.PRODUCT_PATTERNS],
            'category': [re.compile(p, re.I) for p in self.CATEGORY_PATTERNS],
            'page': [re.compile(p, re.I) for p in self.PAGE_PATTERNS],
            'skip': [re.compile(p, re.I) for p in self.SKIP_PATTERNS],
        }
    
    def sample(self, base_url: str, sitemap_urls: List[str] = None,
               rss_urls: List[str] = None, max_crawl: int = 50) -> SamplerResult:
        """
        Sample URLs from a website
        
        Args:
            base_url: Base URL
            sitemap_urls: URLs from sitemap discovery
            rss_urls: URLs from RSS discovery
            max_crawl: Maximum URLs to crawl from homepage
            
        Returns:
            SamplerResult with sampled URLs
        """
        result = SamplerResult(homepage=base_url)
        seen_urls: Set[str] = set()
        
        print(f"  [+] Sampling URLs from {base_url}...")
        
        # Process sitemap URLs first (highest priority)
        if sitemap_urls:
            for url in sitemap_urls:
                if len(result.all_urls) >= self.max_per_type * 5:
                    break
                self._classify_and_add(url, result, seen_urls, source='sitemap')
        
        # Process RSS URLs
        if rss_urls:
            for url in rss_urls:
                if len(result.articles) >= self.max_per_type:
                    break
                self._classify_and_add(url, result, seen_urls, source='rss', force_type=URLType.ARTICLE)
        
        # Crawl homepage for additional URLs if needed
        if (len(result.articles) < self.max_per_type or 
            len(result.products) < self.max_per_type):
            crawled_urls = self._crawl_for_urls(base_url, max_crawl, seen_urls)
            for url in crawled_urls:
                self._classify_and_add(url, result, seen_urls, source='crawl')
        
        # Sort by priority
        result.articles.sort(key=lambda x: x.priority, reverse=True)
        result.products.sort(key=lambda x: x.priority, reverse=True)
        result.categories.sort(key=lambda x: x.priority, reverse=True)
        result.pages.sort(key=lambda x: x.priority, reverse=True)
        
        # Trim to max
        result.articles = result.articles[:self.max_per_type]
        result.products = result.products[:self.max_per_type]
        result.categories = result.categories[:self.max_per_type]
        result.pages = result.pages[:self.max_per_type]
        
        print(f"  [+] Sampled: {len(result.articles)} articles, {len(result.products)} products, "
              f"{len(result.categories)} categories, {len(result.pages)} pages")
        
        return result
    
    def _classify_url(self, url: str) -> URLType:
        """
        Classify URL by type based on patterns
        
        Args:
            url: URL to classify
            
        Returns:
            URLType
        """
        # Check if should skip
        for pattern in self._compiled_patterns['skip']:
            if pattern.search(url):
                return URLType.OTHER
        
        # Check patterns in priority order
        for pattern in self._compiled_patterns['product']:
            if pattern.search(url):
                return URLType.PRODUCT
        
        for pattern in self._compiled_patterns['article']:
            if pattern.search(url):
                return URLType.ARTICLE
        
        for pattern in self._compiled_patterns['category']:
            if pattern.search(url):
                return URLType.CATEGORY
        
        for pattern in self._compiled_patterns['page']:
            if pattern.search(url):
                return URLType.PAGE
        
        return URLType.OTHER
    
    def _classify_and_add(self, url: str, result: SamplerResult, seen: Set[str],
                          source: str = 'crawl', force_type: URLType = None,
                          depth: int = 0, priority: float = 0.5):
        """
        Classify and add URL to appropriate list
        
        Args:
            url: URL to add
            result: SamplerResult to update
            seen: Set of seen URLs
            source: Source of URL
            force_type: Force URL type (skip classification)
            depth: Crawl depth
            priority: URL priority
        """
        if url in seen:
            return
        
        seen.add(url)
        
        url_type = force_type or self._classify_url(url)
        
        if url_type == URLType.OTHER:
            return
        
        sampled = SampledURL(
            url=url,
            url_type=url_type,
            depth=depth,
            source=source,
            priority=priority
        )
        
        result.all_urls.append(sampled)
        
        if url_type == URLType.ARTICLE:
            result.articles.append(sampled)
        elif url_type == URLType.PRODUCT:
            result.products.append(sampled)
        elif url_type == URLType.CATEGORY:
            result.categories.append(sampled)
        elif url_type == URLType.PAGE:
            result.pages.append(sampled)
    
    def _crawl_for_urls(self, base_url: str, max_urls: int, seen: Set[str]) -> List[str]:
        """
        Light crawl to discover URLs
        
        Args:
            base_url: Base URL
            max_urls: Maximum URLs to find
            seen: Already seen URLs
            
        Returns:
            List of discovered URLs
        """
        discovered = []
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        try:
            response = self.http_client.get(base_url)
            if not response or response.status_code != 200:
                return discovered
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                if len(discovered) >= max_urls:
                    break
                
                href = link.get('href', '')
                
                # Skip empty or javascript links
                if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    continue
                
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                
                # Parse and validate
                parsed = urlparse(full_url)
                
                # Only same domain
                if parsed.netloc != base_domain:
                    continue
                
                # Normalize URL (remove fragment, trailing slash)
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                normalized = normalized.rstrip('/')
                
                if normalized not in seen and normalized not in discovered:
                    discovered.append(normalized)
        
        except Exception as e:
            pass
        
        return discovered
    
    def get_sample_by_type(self, result: SamplerResult, url_type: URLType, 
                           count: int = None) -> List[SampledURL]:
        """
        Get sampled URLs by type
        
        Args:
            result: SamplerResult
            url_type: Type to filter
            count: Maximum count (None = all)
            
        Returns:
            List of SampledURL
        """
        if url_type == URLType.ARTICLE:
            urls = result.articles
        elif url_type == URLType.PRODUCT:
            urls = result.products
        elif url_type == URLType.CATEGORY:
            urls = result.categories
        elif url_type == URLType.PAGE:
            urls = result.pages
        else:
            urls = result.all_urls
        
        if count:
            return urls[:count]
        return urls
