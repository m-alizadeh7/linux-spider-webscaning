"""
Content Scanner Module
Integrated scanner for content discovery, extraction, and advanced SEO analysis
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from utils.http_client import HTTPClient

# Content discovery
from scanner.content.sitemap_discovery import SitemapDiscovery
from scanner.content.rss_discovery import RSSDiscovery
from scanner.content.url_sampler import URLSampler, URLType
from scanner.content.article_extractor import ArticleExtractor
from scanner.content.product_extractor import ProductExtractor

# SEO analysis
from scanner.seo.schema_validator import SchemaValidator
from scanner.seo.technical import TechnicalSEO
from scanner.seo.onpage import OnPageSEO


class ContentScanner:
    """
    Integrated scanner for content discovery and advanced SEO analysis
    
    Features:
    - Sitemap and RSS discovery
    - Article extraction
    - Product extraction
    - Schema validation
    - Technical SEO analysis
    - On-page SEO analysis
    """
    
    def __init__(self, max_articles: int = 20, max_products: int = 20):
        """
        Initialize content scanner
        
        Args:
            max_articles: Maximum articles to analyze
            max_products: Maximum products to analyze
        """
        self.http_client = HTTPClient(timeout=15)
        self.max_articles = max_articles
        self.max_products = max_products
        
        # Initialize sub-scanners
        self.sitemap_discovery = SitemapDiscovery()
        self.rss_discovery = RSSDiscovery()
        self.url_sampler = URLSampler()
        self.article_extractor = ArticleExtractor()
        self.product_extractor = ProductExtractor()
        self.schema_validator = SchemaValidator()
        self.technical_seo = TechnicalSEO()
        self.onpage_seo = OnPageSEO()
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive content discovery and SEO scan
        
        Args:
            url: Target URL
            
        Returns:
            Complete scan results
        """
        results = {
            'url': url,
            'discovery': {},
            'articles': {},
            'products': {},
            'schema_validation': {},
            'technical_seo': {},
            'onpage_seo': {},
            'summary': {}
        }
        
        print(f"[*] Starting content scan for: {url}")
        
        # Get homepage HTML for initial analysis
        response = self.http_client.get(url)
        homepage_html = response.text if response else None
        
        # 1. Discover sitemaps
        print(f"\n[*] Phase 1: Content Discovery")
        sitemap_result = self.sitemap_discovery.discover(url)
        results['discovery']['sitemap'] = sitemap_result.to_dict()
        
        # 2. Discover RSS feeds
        rss_result = self.rss_discovery.discover(url, homepage_html)
        results['discovery']['rss'] = rss_result.to_dict()
        
        # 3. Sample URLs for analysis
        sitemap_urls = [u.loc for u in sitemap_result.urls] if sitemap_result.found else []
        rss_urls = [item.url for item in rss_result.items] if rss_result.found else []
        
        sampled = self.url_sampler.sample(
            url, 
            sitemap_urls=sitemap_urls,
            rss_urls=rss_urls
        )
        results['discovery']['sampled_urls'] = sampled.to_dict()
        
        # 4. Extract articles
        print(f"\n[*] Phase 2: Article Extraction")
        article_urls = [u.url for u in sampled.articles[:self.max_articles]]
        
        if article_urls:
            articles_result = self.article_extractor.extract_from_urls(article_urls)
            results['articles'] = articles_result.to_dict()
        else:
            print("  [-] No article URLs found to analyze")
            results['articles'] = {'total_found': 0, 'articles': []}
        
        # 5. Extract products
        print(f"\n[*] Phase 3: Product Extraction")
        product_urls = [u.url for u in sampled.products[:self.max_products]]
        
        if product_urls:
            products_result = self.product_extractor.extract_from_urls(product_urls)
            results['products'] = products_result.to_dict()
        else:
            print("  [-] No product URLs found to analyze")
            results['products'] = {'total_found': 0, 'products': []}
        
        # 6. Validate schema on homepage
        print(f"\n[*] Phase 4: Schema Validation")
        if homepage_html:
            schema_result = self.schema_validator.validate(homepage_html)
            results['schema_validation'] = schema_result.to_dict()
        else:
            results['schema_validation'] = {'error': 'Could not fetch homepage'}
        
        # 7. Technical SEO analysis
        print(f"\n[*] Phase 5: Technical SEO Analysis")
        technical_result = self.technical_seo.analyze(url)
        results['technical_seo'] = technical_result.to_dict()
        
        # 8. On-page SEO analysis of homepage
        print(f"\n[*] Phase 6: On-Page SEO Analysis")
        onpage_result = self.onpage_seo.analyze(url, homepage_html)
        results['onpage_seo'] = onpage_result.to_dict()
        
        # 9. Generate summary
        results['summary'] = self._generate_summary(results)
        
        print(f"\n[+] Content scan completed!")
        
        return results
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary"""
        summary = {
            'content_found': {
                'sitemaps': len(results['discovery'].get('sitemap', {}).get('sitemap_urls', [])),
                'sitemap_urls': results['discovery'].get('sitemap', {}).get('total_urls', 0),
                'rss_feeds': len(results['discovery'].get('rss', {}).get('feed_urls', [])),
                'rss_items': results['discovery'].get('rss', {}).get('total_items', 0),
            },
            'articles': {
                'total': results['articles'].get('total_found', 0),
                'with_schema': results['articles'].get('with_schema', 0),
                'indexable': results['articles'].get('indexable_count', 0),
                'thin_content': results['articles'].get('thin_content_count', 0),
            },
            'products': {
                'total': results['products'].get('total_found', 0),
                'with_schema': results['products'].get('with_schema', 0),
                'with_price': results['products'].get('with_price', 0),
                'with_availability': results['products'].get('with_availability', 0),
            },
            'scores': {
                'technical_seo': results['technical_seo'].get('score', 0),
                'onpage_seo': results['onpage_seo'].get('score', 0),
                'schema_coverage': results['schema_validation'].get('coverage_score', 0),
            },
            'issues_count': {
                'technical': len(results['technical_seo'].get('issues', [])),
                'onpage': len(results['onpage_seo'].get('issues', [])),
                'schema': len(results['schema_validation'].get('errors', [])),
            }
        }
        
        # Calculate overall score
        scores = summary['scores']
        summary['overall_score'] = round(
            (scores['technical_seo'] * 0.35 + 
             scores['onpage_seo'] * 0.35 + 
             scores['schema_coverage'] * 0.30)
        )
        
        return summary
    
    def quick_scan(self, url: str) -> Dict[str, Any]:
        """
        Perform a quick scan (homepage only)
        
        Args:
            url: Target URL
            
        Returns:
            Quick scan results
        """
        results = {}
        
        print(f"[*] Quick scan for: {url}")
        
        response = self.http_client.get(url)
        if not response:
            return {'error': 'Failed to fetch URL'}
        
        html_content = response.text
        
        # Schema validation
        schema_result = self.schema_validator.validate(html_content)
        results['schema'] = schema_result.to_dict()
        
        # Technical SEO
        technical_result = self.technical_seo.analyze(url)
        results['technical'] = technical_result.to_dict()
        
        # On-page SEO
        onpage_result = self.onpage_seo.analyze(url, html_content)
        results['onpage'] = onpage_result.to_dict()
        
        # Quick summary
        results['summary'] = {
            'technical_score': technical_result.score,
            'onpage_score': onpage_result.score,
            'schema_score': schema_result.coverage_score,
            'total_issues': (
                len(technical_result.issues) + 
                len(onpage_result.issues) + 
                len(schema_result.errors)
            )
        }
        
        return results
    
    def scan_articles_only(self, url: str) -> Dict[str, Any]:
        """Scan for articles only"""
        print(f"[*] Scanning articles for: {url}")
        
        response = self.http_client.get(url)
        homepage_html = response.text if response else None
        
        # Discover content sources
        sitemap_result = self.sitemap_discovery.discover(url)
        rss_result = self.rss_discovery.discover(url, homepage_html)
        
        sitemap_urls = [u.loc for u in sitemap_result.urls] if sitemap_result.found else []
        rss_urls = [item.url for item in rss_result.items] if rss_result.found else []
        
        sampled = self.url_sampler.sample(url, sitemap_urls=sitemap_urls, rss_urls=rss_urls)
        
        article_urls = [u.url for u in sampled.articles[:self.max_articles]]
        
        if article_urls:
            return self.article_extractor.extract_from_urls(article_urls).to_dict()
        
        return {'total_found': 0, 'articles': []}
    
    def scan_products_only(self, url: str) -> Dict[str, Any]:
        """Scan for products only"""
        print(f"[*] Scanning products for: {url}")
        
        sitemap_result = self.sitemap_discovery.discover(url)
        
        sitemap_urls = [u.loc for u in sitemap_result.urls] if sitemap_result.found else []
        
        sampled = self.url_sampler.sample(url, sitemap_urls=sitemap_urls)
        
        product_urls = [u.url for u in sampled.products[:self.max_products]]
        
        if product_urls:
            return self.product_extractor.extract_from_urls(product_urls).to_dict()
        
        return {'total_found': 0, 'products': []}
