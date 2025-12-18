"""
Sitemap Discovery Module
Discovers and parses XML sitemaps from websites
"""

import re
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from datetime import datetime
from lxml import etree
from utils.http_client import HTTPClient


@dataclass
class SitemapURL:
    """Represents a URL from sitemap"""
    loc: str
    lastmod: Optional[str] = None
    changefreq: Optional[str] = None
    priority: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.loc,
            'lastmod': self.lastmod,
            'changefreq': self.changefreq,
            'priority': self.priority
        }


@dataclass
class SitemapResult:
    """Result of sitemap discovery"""
    found: bool = False
    sitemap_urls: List[str] = field(default_factory=list)
    urls: List[SitemapURL] = field(default_factory=list)
    total_urls: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'found': self.found,
            'sitemap_urls': self.sitemap_urls,
            'urls': [u.to_dict() for u in self.urls],
            'total_urls': self.total_urls,
            'errors': self.errors,
            'warnings': self.warnings
        }


class SitemapDiscovery:
    """
    Discovers and parses XML sitemaps
    
    Features:
    - Fetches /sitemap.xml and sitemap index
    - Respects robots.txt sitemap hints
    - Handles gzipped sitemaps
    - Parses sitemap index files recursively
    """
    
    # Common sitemap locations to check
    COMMON_PATHS = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap-index.xml',
        '/sitemaps.xml',
        '/sitemap1.xml',
        '/sitemap-posts.xml',
        '/sitemap-pages.xml',
        '/post-sitemap.xml',
        '/page-sitemap.xml',
        '/wp-sitemap.xml',
    ]
    
    # XML namespaces for sitemaps
    NAMESPACES = {
        'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xhtml': 'http://www.w3.org/1999/xhtml'
    }
    
    def __init__(self, max_urls: int = 1000, max_sitemaps: int = 20):
        """
        Initialize sitemap discovery
        
        Args:
            max_urls: Maximum URLs to collect
            max_sitemaps: Maximum sitemap files to process
        """
        self.http_client = HTTPClient(timeout=15)
        self.max_urls = max_urls
        self.max_sitemaps = max_sitemaps
    
    def discover(self, base_url: str) -> SitemapResult:
        """
        Discover sitemaps for a website
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            SitemapResult with discovered URLs
        """
        result = SitemapResult()
        parsed_url = urlparse(base_url)
        base = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Track processed sitemaps to avoid duplicates
        processed_sitemaps: Set[str] = set()
        sitemap_queue: List[str] = []
        
        print(f"  [+] Discovering sitemaps for {base}...")
        
        # First, check robots.txt for sitemap hints
        robots_sitemaps = self._get_sitemaps_from_robots(base)
        sitemap_queue.extend(robots_sitemaps)
        
        # Add common sitemap paths
        for path in self.COMMON_PATHS:
            sitemap_url = urljoin(base, path)
            if sitemap_url not in sitemap_queue:
                sitemap_queue.append(sitemap_url)
        
        # Process sitemap queue
        while sitemap_queue and len(processed_sitemaps) < self.max_sitemaps:
            sitemap_url = sitemap_queue.pop(0)
            
            if sitemap_url in processed_sitemaps:
                continue
            
            processed_sitemaps.add(sitemap_url)
            
            # Fetch and parse sitemap
            sitemap_data = self._fetch_sitemap(sitemap_url)
            
            if sitemap_data is None:
                continue
            
            result.found = True
            result.sitemap_urls.append(sitemap_url)
            
            # Check if it's a sitemap index
            if sitemap_data.get('is_index', False):
                # Add child sitemaps to queue
                for child_url in sitemap_data.get('sitemaps', []):
                    if child_url not in processed_sitemaps:
                        sitemap_queue.append(child_url)
            else:
                # Add URLs
                for url_data in sitemap_data.get('urls', []):
                    if len(result.urls) < self.max_urls:
                        result.urls.append(url_data)
        
        result.total_urls = len(result.urls)
        
        if result.found:
            print(f"  [+] Found {len(result.sitemap_urls)} sitemap(s) with {result.total_urls} URLs")
        else:
            print(f"  [-] No sitemaps found")
            result.warnings.append("No sitemap found at common locations")
        
        return result
    
    def _get_sitemaps_from_robots(self, base_url: str) -> List[str]:
        """
        Get sitemap URLs from robots.txt
        
        Args:
            base_url: Base URL
            
        Returns:
            List of sitemap URLs
        """
        sitemaps = []
        robots_url = urljoin(base_url, '/robots.txt')
        
        try:
            response = self.http_client.get(robots_url)
            if response and response.status_code == 200:
                content = response.text
                
                # Find Sitemap: directives (case-insensitive)
                for line in content.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        if sitemap_url:
                            sitemaps.append(sitemap_url)
        except Exception as e:
            pass  # Silently fail - robots.txt might not exist
        
        return sitemaps
    
    def _fetch_sitemap(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a sitemap
        
        Args:
            url: Sitemap URL
            
        Returns:
            Parsed sitemap data or None
        """
        try:
            # Handle gzipped sitemaps
            headers = {}
            if url.endswith('.gz'):
                headers['Accept-Encoding'] = 'gzip'
            
            response = self.http_client.get(url)
            
            if not response or response.status_code != 200:
                return None
            
            content = response.content
            
            # Try to parse as XML
            try:
                root = etree.fromstring(content)
            except etree.XMLSyntaxError:
                return None
            
            # Check if it's a sitemap index
            if root.tag.endswith('sitemapindex'):
                return self._parse_sitemap_index(root)
            elif root.tag.endswith('urlset'):
                return self._parse_urlset(root)
            
            return None
            
        except Exception as e:
            return None
    
    def _parse_sitemap_index(self, root: etree._Element) -> Dict[str, Any]:
        """Parse sitemap index XML"""
        sitemaps = []
        
        for sitemap in root.findall('.//sm:sitemap', self.NAMESPACES):
            loc = sitemap.find('sm:loc', self.NAMESPACES)
            if loc is not None and loc.text:
                sitemaps.append(loc.text.strip())
        
        # Also try without namespace (some sites don't use it)
        if not sitemaps:
            for sitemap in root.findall('.//sitemap'):
                loc = sitemap.find('loc')
                if loc is not None and loc.text:
                    sitemaps.append(loc.text.strip())
        
        return {
            'is_index': True,
            'sitemaps': sitemaps
        }
    
    def _parse_urlset(self, root: etree._Element) -> Dict[str, Any]:
        """Parse urlset XML"""
        urls = []
        
        for url in root.findall('.//sm:url', self.NAMESPACES):
            loc = url.find('sm:loc', self.NAMESPACES)
            if loc is not None and loc.text:
                sitemap_url = SitemapURL(loc=loc.text.strip())
                
                lastmod = url.find('sm:lastmod', self.NAMESPACES)
                if lastmod is not None and lastmod.text:
                    sitemap_url.lastmod = lastmod.text.strip()
                
                changefreq = url.find('sm:changefreq', self.NAMESPACES)
                if changefreq is not None and changefreq.text:
                    sitemap_url.changefreq = changefreq.text.strip()
                
                priority = url.find('sm:priority', self.NAMESPACES)
                if priority is not None and priority.text:
                    try:
                        sitemap_url.priority = float(priority.text.strip())
                    except ValueError:
                        pass
                
                urls.append(sitemap_url)
        
        # Also try without namespace
        if not urls:
            for url in root.findall('.//url'):
                loc = url.find('loc')
                if loc is not None and loc.text:
                    sitemap_url = SitemapURL(loc=loc.text.strip())
                    
                    lastmod = url.find('lastmod')
                    if lastmod is not None and lastmod.text:
                        sitemap_url.lastmod = lastmod.text.strip()
                    
                    changefreq = url.find('changefreq')
                    if changefreq is not None and changefreq.text:
                        sitemap_url.changefreq = changefreq.text.strip()
                    
                    priority = url.find('priority')
                    if priority is not None and priority.text:
                        try:
                            sitemap_url.priority = float(priority.text.strip())
                        except ValueError:
                            pass
                    
                    urls.append(sitemap_url)
        
        return {
            'is_index': False,
            'urls': urls
        }
    
    def get_urls_by_pattern(self, result: SitemapResult, pattern: str) -> List[SitemapURL]:
        """
        Filter URLs by regex pattern
        
        Args:
            result: SitemapResult to filter
            pattern: Regex pattern
            
        Returns:
            Filtered list of URLs
        """
        regex = re.compile(pattern, re.IGNORECASE)
        return [u for u in result.urls if regex.search(u.loc)]
