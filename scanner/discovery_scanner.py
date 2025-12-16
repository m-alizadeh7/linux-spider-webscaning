"""
Discovery Scanner Module
Phase 0: Discovery - Before any scan, discover site structure
Analyzes robots.txt, sitemap.xml, and performs limited crawl
"""

import re
import time
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class DiscoveryScanner:
    """Scanner for discovering website structure before deep scanning"""
    
    # Rate limiting settings
    CRAWL_DELAY = 1.0  # Default delay between requests (seconds)
    MAX_URLS_TO_CRAWL = 50  # Maximum URLs to discover
    REQUEST_TIMEOUT = 10
    
    # URL patterns to identify important pages
    MONEY_PAGE_PATTERNS = [
        r'/product', r'/shop', r'/buy', r'/cart', r'/checkout',
        r'/pricing', r'/plans', r'/subscribe', r'/order',
        r'/service', r'/booking', r'/reserve'
    ]
    
    ADMIN_PATTERNS = [
        r'/admin', r'/wp-admin', r'/dashboard', r'/cpanel',
        r'/manager', r'/login', r'/signin', r'/auth',
        r'/panel', r'/backend', r'/control'
    ]
    
    BLOG_PATTERNS = [
        r'/blog', r'/news', r'/article', r'/post',
        r'/category', r'/tag', r'/archive'
    ]
    
    def __init__(self):
        """Initialize discovery scanner"""
        self.results = {}
        self.discovered_urls: Set[str] = set()
        self.crawl_delay = self.CRAWL_DELAY
        
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform discovery scan on target URL
        
        Args:
            url: Base URL to scan
            
        Returns:
            Dictionary containing discovery results
        """
        print(f"[*] Discovery phase for: {url}")
        
        base_url = self._normalize_base_url(url)
        
        results = {
            'base_url': base_url,
            'robots_txt': self._analyze_robots_txt(base_url),
            'sitemap': self._analyze_sitemap(base_url),
            'discovered_urls': [],
            'categorized_urls': {
                'main_pages': [],
                'money_pages': [],
                'blog_pages': [],
                'admin_pages': [],
                'other_pages': []
            },
            'crawl_stats': {
                'total_discovered': 0,
                'crawl_delay': self.crawl_delay
            }
        }
        
        # Collect all discovered URLs
        self._collect_discovered_urls(results)
        
        # Categorize URLs
        results['categorized_urls'] = self._categorize_urls(list(self.discovered_urls), base_url)
        results['discovered_urls'] = list(self.discovered_urls)[:self.MAX_URLS_TO_CRAWL]
        results['crawl_stats']['total_discovered'] = len(self.discovered_urls)
        
        self.results = results
        return results
    
    def _normalize_base_url(self, url: str) -> str:
        """Normalize URL to base format"""
        parsed = urlparse(url)
        scheme = parsed.scheme or 'https'
        netloc = parsed.netloc or parsed.path.split('/')[0]
        return f"{scheme}://{netloc}"
    
    def _analyze_robots_txt(self, base_url: str) -> Dict[str, Any]:
        """
        Analyze robots.txt file
        
        Args:
            base_url: Base URL of the site
            
        Returns:
            Dictionary with robots.txt analysis
        """
        print("  [+] Analyzing robots.txt...")
        
        result = {
            'exists': False,
            'content': None,
            'user_agents': [],
            'disallowed_paths': [],
            'allowed_paths': [],
            'sitemaps': [],
            'crawl_delay': None,
            'security_insights': []
        }
        
        try:
            robots_url = f"{base_url}/robots.txt"
            req = Request(robots_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; LinuxSpider/1.4; +https://github.com/m-alizadeh7/linux-spider-webscaning)'
            })
            
            with urlopen(req, timeout=self.REQUEST_TIMEOUT) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
            result['exists'] = True
            result['content'] = content[:5000]  # Limit stored content
            
            # Parse robots.txt
            current_agent = '*'
            for line in content.split('\n'):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                lower_line = line.lower()
                
                if lower_line.startswith('user-agent:'):
                    current_agent = line.split(':', 1)[1].strip()
                    if current_agent not in result['user_agents']:
                        result['user_agents'].append(current_agent)
                        
                elif lower_line.startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        result['disallowed_paths'].append({
                            'path': path,
                            'user_agent': current_agent
                        })
                        # Add to discovered URLs
                        if not path.endswith('*'):
                            full_url = urljoin(base_url, path)
                            self.discovered_urls.add(full_url)
                            
                elif lower_line.startswith('allow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        result['allowed_paths'].append({
                            'path': path,
                            'user_agent': current_agent
                        })
                        
                elif lower_line.startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    # Handle case where : splits sitemap URL incorrectly
                    if sitemap_url.startswith('//'):
                        sitemap_url = 'https:' + sitemap_url
                    elif not sitemap_url.startswith('http'):
                        sitemap_url = 'https:' + line.split('Sitemap:', 1)[1].strip()
                    result['sitemaps'].append(sitemap_url)
                    
                elif lower_line.startswith('crawl-delay:'):
                    try:
                        delay = float(line.split(':', 1)[1].strip())
                        result['crawl_delay'] = delay
                        self.crawl_delay = max(delay, self.CRAWL_DELAY)
                    except ValueError:
                        pass
            
            # Security insights from robots.txt
            result['security_insights'] = self._analyze_robots_security(result['disallowed_paths'])
            
            print(f"    ✓ Found {len(result['disallowed_paths'])} disallowed paths, {len(result['sitemaps'])} sitemaps")
            
        except HTTPError as e:
            if e.code == 404:
                print("    ⚠ robots.txt not found")
                result['security_insights'].append({
                    'level': 'info',
                    'message': 'No robots.txt found - consider adding one for SEO'
                })
            else:
                print(f"    ⚠ robots.txt error: HTTP {e.code}")
        except Exception as e:
            print(f"    ⚠ robots.txt analysis failed: {e}")
        
        return result
    
    def _analyze_robots_security(self, disallowed: List[Dict]) -> List[Dict]:
        """Analyze disallowed paths for security insights"""
        insights = []
        
        sensitive_patterns = {
            r'/admin': 'Admin panel path exposed in robots.txt',
            r'/wp-admin': 'WordPress admin path exposed',
            r'/backup': 'Backup directory mentioned',
            r'/config': 'Configuration directory mentioned',
            r'/\.': 'Hidden files/directories mentioned',
            r'/api': 'API endpoints mentioned',
            r'/private': 'Private directory mentioned',
            r'/secret': 'Secret directory mentioned',
            r'/test': 'Test directory mentioned',
            r'/debug': 'Debug directory mentioned'
        }
        
        for item in disallowed:
            path = item['path'].lower()
            for pattern, message in sensitive_patterns.items():
                if re.search(pattern, path):
                    insights.append({
                        'level': 'warning',
                        'path': item['path'],
                        'message': message
                    })
                    break
        
        return insights
    
    def _analyze_sitemap(self, base_url: str) -> Dict[str, Any]:
        """
        Analyze sitemap.xml and discover URLs
        
        Args:
            base_url: Base URL of the site
            
        Returns:
            Dictionary with sitemap analysis
        """
        print("  [+] Analyzing sitemap.xml...")
        
        result = {
            'exists': False,
            'urls_count': 0,
            'sitemap_index': False,
            'sitemaps': [],
            'sample_urls': [],
            'last_modified': None,
            'url_patterns': {}
        }
        
        # Try common sitemap locations
        sitemap_locations = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemap/sitemap.xml",
            f"{base_url}/wp-sitemap.xml"
        ]
        
        # Add sitemaps from robots.txt
        if hasattr(self, 'results') and 'robots_txt' in self.results:
            sitemap_locations.extend(self.results['robots_txt'].get('sitemaps', []))
        
        for sitemap_url in sitemap_locations:
            try:
                urls = self._parse_sitemap(sitemap_url)
                if urls:
                    result['exists'] = True
                    result['urls_count'] = len(urls)
                    result['sample_urls'] = urls[:20]  # Store first 20
                    
                    # Add to discovered URLs
                    for url in urls[:self.MAX_URLS_TO_CRAWL]:
                        self.discovered_urls.add(url)
                    
                    # Analyze URL patterns
                    result['url_patterns'] = self._analyze_url_patterns(urls)
                    
                    print(f"    ✓ Found {len(urls)} URLs in sitemap")
                    break
                    
            except Exception as e:
                continue
        
        if not result['exists']:
            print("    ⚠ No sitemap found")
        
        return result
    
    def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Parse a sitemap XML and return list of URLs"""
        urls = []
        
        try:
            req = Request(sitemap_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; LinuxSpider/1.4)'
            })
            
            with urlopen(req, timeout=self.REQUEST_TIMEOUT) as response:
                content = response.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Handle namespace
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Check if it's a sitemap index
            sitemaps = root.findall('.//sm:sitemap/sm:loc', ns) or root.findall('.//sitemap/loc')
            if sitemaps:
                # It's a sitemap index, parse each sitemap
                for sitemap in sitemaps[:5]:  # Limit to 5 sub-sitemaps
                    sub_urls = self._parse_sitemap(sitemap.text)
                    urls.extend(sub_urls)
                    time.sleep(0.5)  # Be polite
            else:
                # Regular sitemap
                locs = root.findall('.//sm:url/sm:loc', ns) or root.findall('.//url/loc')
                for loc in locs:
                    if loc.text:
                        urls.append(loc.text)
            
        except ET.ParseError:
            # Try parsing as plain text (some sitemaps are malformed)
            pass
        except Exception:
            pass
        
        return urls
    
    def _analyze_url_patterns(self, urls: List[str]) -> Dict[str, int]:
        """Analyze URL patterns to understand site structure"""
        patterns = {}
        
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path
            
            # Extract first path segment
            segments = [s for s in path.split('/') if s]
            if segments:
                first_segment = f"/{segments[0]}"
                patterns[first_segment] = patterns.get(first_segment, 0) + 1
        
        # Sort by count
        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def _collect_discovered_urls(self, results: Dict) -> None:
        """Collect URLs from various sources"""
        base_url = results['base_url']
        
        # Add homepage
        self.discovered_urls.add(base_url)
        self.discovered_urls.add(f"{base_url}/")
        
        # Common important pages
        common_pages = [
            '/about', '/contact', '/services', '/products',
            '/blog', '/news', '/faq', '/privacy', '/terms',
            '/sitemap', '/search'
        ]
        
        for page in common_pages:
            self.discovered_urls.add(urljoin(base_url, page))
    
    def _categorize_urls(self, urls: List[str], base_url: str) -> Dict[str, List[str]]:
        """Categorize discovered URLs by type"""
        categorized = {
            'main_pages': [],
            'money_pages': [],
            'blog_pages': [],
            'admin_pages': [],
            'other_pages': []
        }
        
        for url in urls:
            path = urlparse(url).path.lower()
            
            # Check category
            if any(re.search(p, path) for p in self.ADMIN_PATTERNS):
                categorized['admin_pages'].append(url)
            elif any(re.search(p, path) for p in self.MONEY_PAGE_PATTERNS):
                categorized['money_pages'].append(url)
            elif any(re.search(p, path) for p in self.BLOG_PATTERNS):
                categorized['blog_pages'].append(url)
            elif path in ['/', '/about', '/contact', '/services', '/products', '/home']:
                categorized['main_pages'].append(url)
            else:
                categorized['other_pages'].append(url)
        
        # Limit each category
        for key in categorized:
            categorized[key] = categorized[key][:15]
        
        return categorized
    
    def get_priority_urls(self, count: int = 10) -> List[str]:
        """Get priority URLs for deep scanning"""
        priority = []
        
        if hasattr(self, 'results') and 'categorized_urls' in self.results:
            cats = self.results['categorized_urls']
            
            # Priority order: main > money > blog > admin > other
            for category in ['main_pages', 'money_pages', 'blog_pages', 'admin_pages', 'other_pages']:
                for url in cats.get(category, []):
                    if url not in priority:
                        priority.append(url)
                    if len(priority) >= count:
                        return priority
        
        return priority
