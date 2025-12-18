"""
Technical SEO Module
Analyzes technical SEO factors
"""

from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
import time
import re

from bs4 import BeautifulSoup
from utils.http_client import HTTPClient


@dataclass
class TechnicalSEOResult:
    """Result of technical SEO analysis"""
    url: str = ""
    status_code: int = 0
    redirect_chain: List[str] = field(default_factory=list)
    redirect_count: int = 0
    is_https: bool = False
    has_www_redirect: bool = False
    canonical_url: Optional[str] = None
    canonical_matches: bool = True
    robots_txt_exists: bool = False
    robots_txt_issues: List[str] = field(default_factory=list)
    sitemap_exists: bool = False
    sitemap_in_robots: bool = False
    meta_robots: Optional[str] = None
    is_indexable: bool = True
    hreflang_present: bool = False
    hreflang_tags: List[Dict[str, str]] = field(default_factory=list)
    page_size_bytes: int = 0
    ttfb_ms: float = 0.0
    load_time_ms: float = 0.0
    mobile_viewport: bool = False
    
    # Issues and recommendations
    issues: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    passed: List[str] = field(default_factory=list)
    
    # Score
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'status_code': self.status_code,
            'redirect_chain': self.redirect_chain,
            'redirect_count': self.redirect_count,
            'is_https': self.is_https,
            'canonical_url': self.canonical_url,
            'canonical_matches': self.canonical_matches,
            'robots_txt_exists': self.robots_txt_exists,
            'robots_txt_issues': self.robots_txt_issues,
            'sitemap_exists': self.sitemap_exists,
            'sitemap_in_robots': self.sitemap_in_robots,
            'meta_robots': self.meta_robots,
            'is_indexable': self.is_indexable,
            'hreflang_present': self.hreflang_present,
            'hreflang_count': len(self.hreflang_tags),
            'page_size_bytes': self.page_size_bytes,
            'page_size_kb': round(self.page_size_bytes / 1024, 2),
            'ttfb_ms': round(self.ttfb_ms, 2),
            'load_time_ms': round(self.load_time_ms, 2),
            'mobile_viewport': self.mobile_viewport,
            'issues': self.issues,
            'warnings': self.warnings,
            'passed': self.passed,
            'score': self.score
        }


class TechnicalSEO:
    """
    Analyzes technical SEO factors
    
    Checks:
    - Status codes and redirects
    - HTTPS
    - Canonical URLs
    - robots.txt and sitemap
    - meta robots
    - hreflang
    - Page size and TTFB
    - Mobile viewport
    """
    
    def __init__(self):
        """Initialize technical SEO analyzer"""
        self.http_client = HTTPClient(timeout=15)
    
    def analyze(self, url: str) -> TechnicalSEOResult:
        """
        Perform technical SEO analysis
        
        Args:
            url: Target URL
            
        Returns:
            TechnicalSEOResult
        """
        result = TechnicalSEOResult(url=url)
        
        print(f"  [+] Analyzing technical SEO for {url}...")
        
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Check HTTPS
        result.is_https = parsed.scheme == 'https'
        if result.is_https:
            result.passed.append("Site uses HTTPS")
        else:
            result.issues.append({
                'issue': 'Site not using HTTPS',
                'impact': 'HIGH',
                'fix': 'Install SSL certificate and redirect HTTP to HTTPS'
            })
        
        # Fetch page and measure performance
        start_time = time.time()
        response = self.http_client.get(url, allow_redirects=False)
        result.ttfb_ms = (time.time() - start_time) * 1000
        
        if not response:
            result.issues.append({
                'issue': 'Failed to fetch page',
                'impact': 'CRITICAL',
                'fix': 'Check if site is accessible'
            })
            return result
        
        # Follow redirects manually to track chain
        redirect_chain = []
        current_response = response
        current_url = url
        
        while current_response.is_redirect and len(redirect_chain) < 10:
            redirect_chain.append(current_url)
            current_url = current_response.headers.get('Location', '')
            if current_url:
                current_url = urljoin(current_url if current_url.startswith('http') else url, current_url)
                current_response = self.http_client.get(current_url, allow_redirects=False)
                if not current_response:
                    break
            else:
                break
        
        # Get final response
        if redirect_chain:
            result.redirect_chain = redirect_chain
            result.redirect_count = len(redirect_chain)
            final_response = self.http_client.get(url)
            if final_response:
                response = final_response
        
        result.status_code = response.status_code
        end_time = time.time()
        result.load_time_ms = (end_time - start_time) * 1000
        result.page_size_bytes = len(response.content)
        
        # Check redirect issues
        if result.redirect_count > 2:
            result.warnings.append({
                'issue': f'Long redirect chain ({result.redirect_count} redirects)',
                'impact': 'MEDIUM',
                'fix': 'Reduce redirect chain to 1-2 hops maximum'
            })
        elif result.redirect_count == 0:
            result.passed.append("No unnecessary redirects")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check canonical
        canonical = soup.find('link', rel='canonical')
        if canonical:
            result.canonical_url = canonical.get('href', '')
            if result.canonical_url:
                result.canonical_matches = self._urls_match(url, result.canonical_url)
                if result.canonical_matches:
                    result.passed.append("Canonical URL properly set")
                else:
                    result.warnings.append({
                        'issue': 'Canonical URL differs from page URL',
                        'impact': 'MEDIUM',
                        'fix': f'Canonical points to: {result.canonical_url}'
                    })
        else:
            result.warnings.append({
                'issue': 'No canonical URL specified',
                'impact': 'MEDIUM',
                'fix': 'Add <link rel="canonical" href="..."> tag'
            })
        
        # Check meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        if meta_robots:
            result.meta_robots = meta_robots.get('content', '')
            if 'noindex' in result.meta_robots.lower():
                result.is_indexable = False
                result.warnings.append({
                    'issue': 'Page has noindex directive',
                    'impact': 'HIGH',
                    'fix': 'Remove noindex if page should be indexed'
                })
        else:
            result.passed.append("No blocking meta robots")
        
        # Check hreflang
        hreflang_links = soup.find_all('link', rel='alternate', hreflang=True)
        if hreflang_links:
            result.hreflang_present = True
            for link in hreflang_links:
                result.hreflang_tags.append({
                    'hreflang': link.get('hreflang', ''),
                    'href': link.get('href', '')
                })
            result.passed.append(f"Hreflang tags present ({len(hreflang_links)} languages)")
        
        # Check mobile viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            result.mobile_viewport = True
            result.passed.append("Mobile viewport meta tag present")
        else:
            result.issues.append({
                'issue': 'Missing viewport meta tag',
                'impact': 'HIGH',
                'fix': 'Add <meta name="viewport" content="width=device-width, initial-scale=1">'
            })
        
        # Check robots.txt
        self._check_robots_txt(base_url, result)
        
        # Check sitemap
        self._check_sitemap(base_url, result)
        
        # Check page size
        if result.page_size_bytes > 3 * 1024 * 1024:  # > 3MB
            result.issues.append({
                'issue': f'Page size too large ({result.page_size_bytes / 1024:.0f} KB)',
                'impact': 'HIGH',
                'fix': 'Optimize images and reduce page size'
            })
        elif result.page_size_bytes > 1024 * 1024:  # > 1MB
            result.warnings.append({
                'issue': f'Page size is large ({result.page_size_bytes / 1024:.0f} KB)',
                'impact': 'MEDIUM',
                'fix': 'Consider optimizing page resources'
            })
        else:
            result.passed.append(f"Page size OK ({result.page_size_bytes / 1024:.0f} KB)")
        
        # Check TTFB
        if result.ttfb_ms > 1000:
            result.issues.append({
                'issue': f'Slow TTFB ({result.ttfb_ms:.0f}ms)',
                'impact': 'HIGH',
                'fix': 'Optimize server response time, use caching'
            })
        elif result.ttfb_ms > 500:
            result.warnings.append({
                'issue': f'TTFB could be better ({result.ttfb_ms:.0f}ms)',
                'impact': 'MEDIUM',
                'fix': 'Consider server-side caching'
            })
        else:
            result.passed.append(f"Good TTFB ({result.ttfb_ms:.0f}ms)")
        
        # Calculate score
        result.score = self._calculate_score(result)
        
        return result
    
    def _check_robots_txt(self, base_url: str, result: TechnicalSEOResult):
        """Check robots.txt"""
        robots_url = urljoin(base_url, '/robots.txt')
        
        try:
            response = self.http_client.get(robots_url)
            if response and response.status_code == 200:
                result.robots_txt_exists = True
                content = response.text
                
                # Check for common issues
                if 'Disallow: /' in content and 'Allow:' not in content:
                    result.robots_txt_issues.append('robots.txt may be blocking entire site')
                    result.warnings.append({
                        'issue': 'robots.txt may be blocking entire site',
                        'impact': 'CRITICAL',
                        'fix': 'Review Disallow directives in robots.txt'
                    })
                
                # Check for sitemap reference
                if 'sitemap:' in content.lower():
                    result.sitemap_in_robots = True
                
                result.passed.append("robots.txt exists")
            else:
                result.warnings.append({
                    'issue': 'robots.txt not found',
                    'impact': 'LOW',
                    'fix': 'Create robots.txt file'
                })
        except Exception as e:
            pass
    
    def _check_sitemap(self, base_url: str, result: TechnicalSEOResult):
        """Check sitemap.xml"""
        sitemap_url = urljoin(base_url, '/sitemap.xml')
        
        try:
            response = self.http_client.get(sitemap_url)
            if response and response.status_code == 200:
                result.sitemap_exists = True
                result.passed.append("sitemap.xml exists")
                
                if not result.sitemap_in_robots:
                    result.warnings.append({
                        'issue': 'Sitemap not referenced in robots.txt',
                        'impact': 'LOW',
                        'fix': 'Add Sitemap: directive to robots.txt'
                    })
            else:
                result.warnings.append({
                    'issue': 'sitemap.xml not found',
                    'impact': 'MEDIUM',
                    'fix': 'Create XML sitemap and submit to search engines'
                })
        except Exception as e:
            pass
    
    def _urls_match(self, url1: str, url2: str) -> bool:
        """Check if two URLs are equivalent"""
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Normalize paths
        path1 = parsed1.path.rstrip('/')
        path2 = parsed2.path.rstrip('/')
        
        return (parsed1.netloc == parsed2.netloc and 
                path1 == path2)
    
    def _calculate_score(self, result: TechnicalSEOResult) -> float:
        """Calculate technical SEO score"""
        score = 100.0
        
        # Deductions
        for issue in result.issues:
            impact = issue.get('impact', 'MEDIUM')
            if impact == 'CRITICAL':
                score -= 25
            elif impact == 'HIGH':
                score -= 15
            elif impact == 'MEDIUM':
                score -= 10
            else:
                score -= 5
        
        for warning in result.warnings:
            impact = warning.get('impact', 'LOW')
            if impact == 'HIGH':
                score -= 10
            elif impact == 'MEDIUM':
                score -= 5
            else:
                score -= 2
        
        return max(0, min(100, score))
    
    def analyze_multiple(self, urls: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple URLs for duplicate content
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            Analysis results including duplicate detection
        """
        results = {
            'pages': [],
            'duplicate_titles': [],
            'duplicate_descriptions': [],
            'issues': []
        }
        
        titles = {}
        descriptions = {}
        
        for url in urls[:20]:  # Limit to 20 pages
            try:
                response = self.http_client.get(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Get title
                    title_tag = soup.find('title')
                    title = title_tag.get_text().strip() if title_tag else ''
                    
                    # Get description
                    desc_tag = soup.find('meta', attrs={'name': 'description'})
                    description = desc_tag.get('content', '').strip() if desc_tag else ''
                    
                    results['pages'].append({
                        'url': url,
                        'title': title,
                        'description': description
                    })
                    
                    # Track duplicates
                    if title:
                        if title in titles:
                            titles[title].append(url)
                        else:
                            titles[title] = [url]
                    
                    if description:
                        if description in descriptions:
                            descriptions[description].append(url)
                        else:
                            descriptions[description] = [url]
                            
            except Exception as e:
                pass
        
        # Find duplicates
        for title, urls in titles.items():
            if len(urls) > 1:
                results['duplicate_titles'].append({
                    'title': title,
                    'urls': urls,
                    'count': len(urls)
                })
        
        for desc, urls in descriptions.items():
            if len(urls) > 1:
                results['duplicate_descriptions'].append({
                    'description': desc[:100] + '...' if len(desc) > 100 else desc,
                    'urls': urls,
                    'count': len(urls)
                })
        
        if results['duplicate_titles']:
            results['issues'].append({
                'issue': f"{len(results['duplicate_titles'])} duplicate title(s) found",
                'impact': 'MEDIUM',
                'fix': 'Create unique titles for each page'
            })
        
        if results['duplicate_descriptions']:
            results['issues'].append({
                'issue': f"{len(results['duplicate_descriptions'])} duplicate description(s) found",
                'impact': 'MEDIUM',
                'fix': 'Create unique meta descriptions for each page'
            })
        
        return results
