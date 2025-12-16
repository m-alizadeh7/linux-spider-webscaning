"""
SEO Scanner Module
Analyzes SEO-related factors and website structure
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse
from utils.http_client import HTTPClient


class SEOScanner:
    """Scanner for SEO analysis"""
    
    def __init__(self):
        """Initialize SEO scanner"""
        self.http_client = HTTPClient()
        self.results = {}
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive SEO scan
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary containing SEO analysis
        """
        print(f"[*] Scanning SEO for: {url}")
        
        # Get page content
        response = self.http_client.get(url)
        if not response:
            print("  [-] Failed to fetch website")
            return {'error': 'Failed to fetch website'}
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        results = {
            'url': url,
            'meta_tags': self._analyze_meta_tags(soup),
            'headings': self._analyze_headings(soup),
            'content_analysis': self._analyze_content(soup, html_content),
            'links': self._analyze_links(soup, url),
            'images': self._analyze_images(soup),
            'performance': self._analyze_performance(response),
            'mobile_friendly': self._check_mobile_friendly(soup),
            'structured_data': self._check_structured_data(soup, html_content),
            'seo_score': 0
        }
        
        # Calculate SEO score
        results['seo_score'] = self._calculate_seo_score(results)
        
        self.results = results
        return results
    
    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Analyze meta tags
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with meta tag analysis
        """
        try:
            print("  [+] Analyzing meta tags...")
            
            # Title tag
            title_tag = soup.find('title')
            title = title_tag.get_text() if title_tag else None
            title_length = len(title) if title else 0
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else None
            desc_length = len(description) if description else 0
            
            # Meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '') if meta_keywords else None
            
            # Open Graph tags
            og_tags = {}
            for og in soup.find_all('meta', property=re.compile(r'^og:')):
                og_tags[og.get('property')] = og.get('content', '')
            
            # Twitter Card tags
            twitter_tags = {}
            for twitter in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
                twitter_tags[twitter.get('name')] = twitter.get('content', '')
            
            # Canonical URL
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            canonical_url = canonical.get('href', '') if canonical else None
            
            # Robots meta tag
            robots = soup.find('meta', attrs={'name': 'robots'})
            robots_content = robots.get('content', '') if robots else None
            
            return {
                'title': {
                    'content': title,
                    'length': title_length,
                    'optimal': 30 <= title_length <= 60,
                    'recommendation': 'Title should be 30-60 characters' if not (30 <= title_length <= 60) else 'Good'
                },
                'description': {
                    'content': description,
                    'length': desc_length,
                    'optimal': 120 <= desc_length <= 160,
                    'recommendation': 'Description should be 120-160 characters' if not (120 <= desc_length <= 160) else 'Good'
                },
                'keywords': keywords,
                'canonical': canonical_url,
                'robots': robots_content,
                'open_graph': og_tags,
                'twitter_cards': twitter_tags
            }
        except Exception as e:
            print(f"  [-] Meta tag analysis failed: {e}")
            return {}
    
    def _analyze_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Analyze heading structure
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with heading analysis
        """
        try:
            print("  [+] Analyzing heading structure...")
            
            headings = {
                'h1': [],
                'h2': [],
                'h3': [],
                'h4': [],
                'h5': [],
                'h6': []
            }
            
            for level in range(1, 7):
                tags = soup.find_all(f'h{level}')
                headings[f'h{level}'] = [tag.get_text().strip() for tag in tags]
            
            h1_count = len(headings['h1'])
            
            return {
                'structure': headings,
                'h1_count': h1_count,
                'h1_optimal': h1_count == 1,
                'recommendation': 'Should have exactly one H1 tag' if h1_count != 1 else 'Good',
                'total_headings': sum(len(h) for h in headings.values())
            }
        except Exception as e:
            print(f"  [-] Heading analysis failed: {e}")
            return {}
    
    def _analyze_content(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """
        Analyze page content
        
        Args:
            soup: BeautifulSoup object
            html_content: Raw HTML content
            
        Returns:
            Dictionary with content analysis
        """
        try:
            print("  [+] Analyzing content...")
            
            # Get text content
            text_content = soup.get_text()
            words = text_content.split()
            word_count = len(words)
            
            # Calculate text to HTML ratio
            text_size = len(text_content)
            html_size = len(html_content)
            text_ratio = (text_size / html_size * 100) if html_size > 0 else 0
            
            # Check for language attribute
            html_tag = soup.find('html')
            lang = html_tag.get('lang', None) if html_tag else None
            
            return {
                'word_count': word_count,
                'text_to_html_ratio': round(text_ratio, 2),
                'language': lang,
                'recommendations': self._get_content_recommendations(word_count, text_ratio, lang)
            }
        except Exception as e:
            print(f"  [-] Content analysis failed: {e}")
            return {}
    
    def _get_content_recommendations(self, word_count: int, text_ratio: float, lang: str) -> List[str]:
        """Get content recommendations"""
        recommendations = []
        
        if word_count < 300:
            recommendations.append("Content is too short. Aim for at least 300 words")
        elif word_count > 2500:
            recommendations.append("Consider breaking content into multiple pages")
        
        if text_ratio < 25:
            recommendations.append("Low text to HTML ratio. Add more content or reduce HTML")
        
        if not lang:
            recommendations.append("Add lang attribute to HTML tag for better accessibility")
        
        if not recommendations:
            recommendations.append("Content metrics look good")
        
        return recommendations
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """
        Analyze internal and external links
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL of the site
            
        Returns:
            Dictionary with link analysis
        """
        try:
            print("  [+] Analyzing links...")
            
            all_links = soup.find_all('a', href=True)
            internal_links = []
            external_links = []
            broken_links = []
            
            base_domain = urlparse(base_url).netloc
            
            for link in all_links:
                href = link.get('href', '')
                
                # Skip empty, javascript, and anchor links
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                
                # Make absolute URL
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                
                if parsed.netloc == base_domain or not parsed.netloc:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            
            return {
                'total_links': len(all_links),
                'internal_links': len(set(internal_links)),
                'external_links': len(set(external_links)),
                'recommendations': self._get_link_recommendations(len(internal_links), len(external_links))
            }
        except Exception as e:
            print(f"  [-] Link analysis failed: {e}")
            return {}
    
    def _get_link_recommendations(self, internal_count: int, external_count: int) -> List[str]:
        """Get link recommendations"""
        recommendations = []
        
        if internal_count == 0:
            recommendations.append("No internal links found. Add internal linking structure")
        elif internal_count < 5:
            recommendations.append("Consider adding more internal links")
        
        if external_count > internal_count * 2:
            recommendations.append("Too many external links compared to internal links")
        
        if not recommendations:
            recommendations.append("Link structure looks good")
        
        return recommendations
    
    def _analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Analyze images
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with image analysis
        """
        try:
            print("  [+] Analyzing images...")
            
            images = soup.find_all('img')
            total_images = len(images)
            images_with_alt = sum(1 for img in images if img.get('alt'))
            images_without_alt = total_images - images_with_alt
            
            return {
                'total_images': total_images,
                'images_with_alt': images_with_alt,
                'images_without_alt': images_without_alt,
                'alt_tag_percentage': round((images_with_alt / total_images * 100) if total_images > 0 else 0, 2),
                'recommendation': 'All images should have alt attributes' if images_without_alt > 0 else 'Good'
            }
        except Exception as e:
            print(f"  [-] Image analysis failed: {e}")
            return {}
    
    def _analyze_performance(self, response) -> Dict[str, Any]:
        """
        Analyze performance metrics
        
        Args:
            response: HTTP response object
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            print("  [+] Analyzing performance...")
            
            load_time = response.elapsed.total_seconds()
            page_size = len(response.content)
            
            return {
                'load_time': round(load_time, 2),
                'page_size_bytes': page_size,
                'page_size_readable': self._format_bytes(page_size),
                'recommendations': self._get_performance_recommendations(load_time, page_size)
            }
        except Exception as e:
            print(f"  [-] Performance analysis failed: {e}")
            return {}
    
    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def _get_performance_recommendations(self, load_time: float, page_size: int) -> List[str]:
        """Get performance recommendations"""
        recommendations = []
        
        if load_time > 3:
            recommendations.append("Page load time is slow (>3 seconds). Consider optimization")
        elif load_time > 2:
            recommendations.append("Page load time could be improved")
        
        if page_size > 3 * 1024 * 1024:  # 3MB
            recommendations.append("Page size is large (>3MB). Consider optimization")
        
        if not recommendations:
            recommendations.append("Performance metrics look good")
        
        return recommendations
    
    def _check_mobile_friendly(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Check mobile-friendliness
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with mobile-friendly analysis
        """
        try:
            print("  [+] Checking mobile-friendliness...")
            
            # Check viewport meta tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            has_viewport = viewport is not None
            
            # Check for responsive indicators
            has_media_queries = False
            for style in soup.find_all('style'):
                if '@media' in style.get_text():
                    has_media_queries = True
                    break
            
            return {
                'has_viewport_meta': has_viewport,
                'viewport_content': viewport.get('content', '') if viewport else None,
                'has_media_queries': has_media_queries,
                'recommendation': 'Add viewport meta tag' if not has_viewport else 'Mobile-friendly indicators present'
            }
        except Exception as e:
            print(f"  [-] Mobile-friendly check failed: {e}")
            return {}
    
    def _check_structured_data(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """
        Check for structured data (Schema.org, JSON-LD)
        
        Args:
            soup: BeautifulSoup object
            html_content: Raw HTML content
            
        Returns:
            Dictionary with structured data findings
        """
        try:
            print("  [+] Checking structured data...")
            
            # Check for JSON-LD
            jsonld_scripts = soup.find_all('script', type='application/ld+json')
            has_jsonld = len(jsonld_scripts) > 0
            
            # Check for microdata
            has_microdata = bool(soup.find_all(attrs={'itemtype': True}))
            
            # Check for RDFa
            has_rdfa = bool(soup.find_all(attrs={'vocab': True}))
            
            return {
                'has_structured_data': has_jsonld or has_microdata or has_rdfa,
                'json_ld': has_jsonld,
                'json_ld_count': len(jsonld_scripts),
                'microdata': has_microdata,
                'rdfa': has_rdfa,
                'recommendation': 'Add structured data for better search engine understanding' if not (has_jsonld or has_microdata or has_rdfa) else 'Structured data present'
            }
        except Exception as e:
            print(f"  [-] Structured data check failed: {e}")
            return {}
    
    def _calculate_seo_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall SEO score (0-100)
        
        Args:
            results: SEO scan results
            
        Returns:
            SEO score
        """
        try:
            score = 100
            
            # Meta tags (30 points)
            if 'meta_tags' in results:
                meta = results['meta_tags']
                if not meta.get('title', {}).get('optimal', False):
                    score -= 10
                if not meta.get('description', {}).get('optimal', False):
                    score -= 10
                if not meta.get('canonical'):
                    score -= 5
                if not meta.get('open_graph'):
                    score -= 5
            
            # Headings (15 points)
            if 'headings' in results:
                if not results['headings'].get('h1_optimal', False):
                    score -= 15
            
            # Images (10 points)
            if 'images' in results:
                alt_percentage = results['images'].get('alt_tag_percentage', 0)
                if alt_percentage < 100:
                    score -= (100 - alt_percentage) / 10
            
            # Mobile-friendly (15 points)
            if 'mobile_friendly' in results:
                if not results['mobile_friendly'].get('has_viewport_meta', False):
                    score -= 15
            
            # Structured data (10 points)
            if 'structured_data' in results:
                if not results['structured_data'].get('has_structured_data', False):
                    score -= 10
            
            # Content (10 points)
            if 'content_analysis' in results:
                word_count = results['content_analysis'].get('word_count', 0)
                if word_count < 300:
                    score -= 10
            
            # Performance (10 points)
            if 'performance' in results:
                load_time = results['performance'].get('load_time', 0)
                if load_time > 3:
                    score -= 10
                elif load_time > 2:
                    score -= 5
            
            return max(0, min(100, int(score)))
        except Exception:
            return 0
