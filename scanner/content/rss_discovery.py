"""
RSS/Atom Feed Discovery Module
Discovers and parses RSS/Atom feeds from websites
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from datetime import datetime
import re

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

from bs4 import BeautifulSoup
from utils.http_client import HTTPClient


@dataclass
class FeedItem:
    """Represents an item from RSS/Atom feed"""
    title: str
    url: str
    published: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'published': self.published,
            'author': self.author,
            'summary': self.summary,
            'categories': self.categories
        }


@dataclass
class FeedResult:
    """Result of RSS/Atom discovery"""
    found: bool = False
    feed_urls: List[str] = field(default_factory=list)
    feed_type: Optional[str] = None  # rss, atom
    title: Optional[str] = None
    description: Optional[str] = None
    items: List[FeedItem] = field(default_factory=list)
    total_items: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'found': self.found,
            'feed_urls': self.feed_urls,
            'feed_type': self.feed_type,
            'title': self.title,
            'description': self.description,
            'items': [i.to_dict() for i in self.items],
            'total_items': self.total_items,
            'errors': self.errors,
            'warnings': self.warnings
        }


class RSSDiscovery:
    """
    Discovers and parses RSS/Atom feeds
    
    Features:
    - Auto-discovers feed URLs from HTML
    - Checks common feed paths
    - Parses RSS 2.0 and Atom feeds
    """
    
    # Common RSS/Atom paths to check
    COMMON_PATHS = [
        '/feed',
        '/feed/',
        '/rss',
        '/rss/',
        '/rss.xml',
        '/atom.xml',
        '/feed.xml',
        '/index.xml',
        '/feeds/posts/default',
        '/blog/feed',
        '/blog/rss',
        '/?feed=rss2',
        '/feed/rss/',
        '/feed/atom/',
    ]
    
    def __init__(self, max_items: int = 100):
        """
        Initialize RSS discovery
        
        Args:
            max_items: Maximum items to collect from feeds
        """
        self.http_client = HTTPClient(timeout=15)
        self.max_items = max_items
        
        if not FEEDPARSER_AVAILABLE:
            print("  [!] feedparser not installed - RSS parsing will be limited")
    
    def discover(self, base_url: str, html_content: str = None) -> FeedResult:
        """
        Discover RSS/Atom feeds for a website
        
        Args:
            base_url: Base URL of the website
            html_content: Optional HTML content for link discovery
            
        Returns:
            FeedResult with discovered feed items
        """
        result = FeedResult()
        parsed_url = urlparse(base_url)
        base = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        feed_urls_to_check = []
        
        print(f"  [+] Discovering RSS/Atom feeds for {base}...")
        
        # First, try to discover from HTML <link> tags
        if html_content:
            discovered = self._discover_from_html(html_content, base)
            feed_urls_to_check.extend(discovered)
        else:
            # Fetch homepage to look for feed links
            response = self.http_client.get(base_url)
            if response and response.status_code == 200:
                discovered = self._discover_from_html(response.text, base)
                feed_urls_to_check.extend(discovered)
        
        # Add common paths
        for path in self.COMMON_PATHS:
            feed_url = urljoin(base, path)
            if feed_url not in feed_urls_to_check:
                feed_urls_to_check.append(feed_url)
        
        # Try each feed URL
        for feed_url in feed_urls_to_check:
            if result.found and len(result.items) >= self.max_items:
                break
            
            feed_data = self._fetch_and_parse_feed(feed_url)
            
            if feed_data:
                result.found = True
                result.feed_urls.append(feed_url)
                
                if not result.title:
                    result.title = feed_data.get('title')
                if not result.description:
                    result.description = feed_data.get('description')
                if not result.feed_type:
                    result.feed_type = feed_data.get('type')
                
                for item in feed_data.get('items', []):
                    if len(result.items) < self.max_items:
                        result.items.append(item)
        
        result.total_items = len(result.items)
        
        if result.found:
            print(f"  [+] Found {len(result.feed_urls)} feed(s) with {result.total_items} items")
        else:
            print(f"  [-] No RSS/Atom feeds found")
            result.warnings.append("No RSS or Atom feed found at common locations")
        
        return result
    
    def _discover_from_html(self, html_content: str, base_url: str) -> List[str]:
        """
        Discover feed URLs from HTML link tags
        
        Args:
            html_content: HTML content
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of feed URLs
        """
        feed_urls = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for RSS/Atom link tags
            feed_link_types = [
                'application/rss+xml',
                'application/atom+xml',
                'application/rdf+xml',
                'application/xml',
                'text/xml'
            ]
            
            for link in soup.find_all('link', rel=re.compile(r'alternate', re.I)):
                link_type = link.get('type', '').lower()
                href = link.get('href', '')
                
                if any(ft in link_type for ft in feed_link_types) and href:
                    feed_url = urljoin(base_url, href)
                    if feed_url not in feed_urls:
                        feed_urls.append(feed_url)
            
        except Exception as e:
            pass
        
        return feed_urls
    
    def _fetch_and_parse_feed(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a feed
        
        Args:
            url: Feed URL
            
        Returns:
            Parsed feed data or None
        """
        try:
            response = self.http_client.get(url)
            
            if not response or response.status_code != 200:
                return None
            
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Check if it's likely a feed
            if not any(ft in content_type for ft in ['xml', 'rss', 'atom', 'feed']):
                # Check content for XML indicators
                content_start = response.text[:500].lower()
                if '<rss' not in content_start and '<feed' not in content_start and '<?xml' not in content_start:
                    return None
            
            if FEEDPARSER_AVAILABLE:
                return self._parse_with_feedparser(response.content, url)
            else:
                return self._parse_manually(response.text, url)
            
        except Exception as e:
            return None
    
    def _parse_with_feedparser(self, content: bytes, url: str) -> Optional[Dict[str, Any]]:
        """Parse feed using feedparser library"""
        try:
            parsed = feedparser.parse(content)
            
            if parsed.bozo and not parsed.entries:
                return None
            
            # Determine feed type
            feed_type = 'rss'
            if hasattr(parsed, 'version') and 'atom' in str(parsed.version).lower():
                feed_type = 'atom'
            
            items = []
            for entry in parsed.entries:
                item = FeedItem(
                    title=entry.get('title', 'No Title'),
                    url=entry.get('link', '')
                )
                
                # Published date
                if 'published' in entry:
                    item.published = entry.published
                elif 'updated' in entry:
                    item.published = entry.updated
                
                # Author
                if 'author' in entry:
                    item.author = entry.author
                elif 'authors' in entry and entry.authors:
                    item.author = entry.authors[0].get('name', '')
                
                # Summary
                if 'summary' in entry:
                    item.summary = entry.summary[:500] if len(entry.summary) > 500 else entry.summary
                
                # Categories
                if 'tags' in entry:
                    item.categories = [t.get('term', '') for t in entry.tags if t.get('term')]
                
                items.append(item)
            
            return {
                'type': feed_type,
                'title': parsed.feed.get('title', ''),
                'description': parsed.feed.get('description', ''),
                'items': items
            }
            
        except Exception as e:
            return None
    
    def _parse_manually(self, content: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse feed manually without feedparser"""
        try:
            soup = BeautifulSoup(content, 'xml')
            
            items = []
            feed_type = 'rss'
            title = ''
            description = ''
            
            # Try RSS format
            channel = soup.find('channel')
            if channel:
                title = channel.find('title')
                title = title.get_text() if title else ''
                
                desc = channel.find('description')
                description = desc.get_text() if desc else ''
                
                for item in channel.find_all('item'):
                    item_title = item.find('title')
                    item_link = item.find('link')
                    
                    feed_item = FeedItem(
                        title=item_title.get_text() if item_title else 'No Title',
                        url=item_link.get_text() if item_link else ''
                    )
                    
                    pub_date = item.find('pubDate')
                    if pub_date:
                        feed_item.published = pub_date.get_text()
                    
                    author = item.find('author') or item.find('dc:creator')
                    if author:
                        feed_item.author = author.get_text()
                    
                    desc = item.find('description')
                    if desc:
                        text = desc.get_text()
                        feed_item.summary = text[:500] if len(text) > 500 else text
                    
                    items.append(feed_item)
            
            # Try Atom format
            feed = soup.find('feed')
            if feed and not items:
                feed_type = 'atom'
                
                title_tag = feed.find('title')
                title = title_tag.get_text() if title_tag else ''
                
                subtitle = feed.find('subtitle')
                description = subtitle.get_text() if subtitle else ''
                
                for entry in feed.find_all('entry'):
                    entry_title = entry.find('title')
                    entry_link = entry.find('link', href=True)
                    
                    feed_item = FeedItem(
                        title=entry_title.get_text() if entry_title else 'No Title',
                        url=entry_link['href'] if entry_link else ''
                    )
                    
                    published = entry.find('published') or entry.find('updated')
                    if published:
                        feed_item.published = published.get_text()
                    
                    author = entry.find('author')
                    if author:
                        name = author.find('name')
                        feed_item.author = name.get_text() if name else ''
                    
                    summary = entry.find('summary') or entry.find('content')
                    if summary:
                        text = summary.get_text()
                        feed_item.summary = text[:500] if len(text) > 500 else text
                    
                    items.append(feed_item)
            
            if items:
                return {
                    'type': feed_type,
                    'title': title,
                    'description': description,
                    'items': items
                }
            
            return None
            
        except Exception as e:
            return None
