"""
On-Page SEO Module
Analyzes on-page SEO factors for articles and products
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from dataclasses import dataclass, field
import re

from bs4 import BeautifulSoup
from utils.http_client import HTTPClient


@dataclass
class OnPageSEOResult:
    """Result of on-page SEO analysis"""
    url: str = ""
    
    # Title analysis
    title: str = ""
    title_length: int = 0
    title_optimal: bool = False
    
    # Meta description
    meta_description: str = ""
    meta_description_length: int = 0
    meta_description_optimal: bool = False
    
    # Headings
    h1_count: int = 0
    h1_content: List[str] = field(default_factory=list)
    h1_optimal: bool = False
    h2_count: int = 0
    h3_count: int = 0
    heading_hierarchy_valid: bool = True
    
    # Content
    word_count: int = 0
    paragraph_count: int = 0
    avg_paragraph_length: float = 0.0
    is_thin_content: bool = False
    
    # Links
    internal_links_count: int = 0
    external_links_count: int = 0
    nofollow_links_count: int = 0
    
    # Images
    total_images: int = 0
    images_with_alt: int = 0
    images_missing_alt: int = 0
    alt_coverage_percent: float = 0.0
    
    # Keyword analysis (basic)
    title_in_h1: bool = False
    
    # Issues and score
    issues: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    passed: List[str] = field(default_factory=list)
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'title': {
                'content': self.title,
                'length': self.title_length,
                'optimal': self.title_optimal
            },
            'meta_description': {
                'content': self.meta_description[:200] if self.meta_description else '',
                'length': self.meta_description_length,
                'optimal': self.meta_description_optimal
            },
            'headings': {
                'h1_count': self.h1_count,
                'h1_content': self.h1_content[:3],  # First 3 H1s
                'h1_optimal': self.h1_optimal,
                'h2_count': self.h2_count,
                'h3_count': self.h3_count,
                'hierarchy_valid': self.heading_hierarchy_valid
            },
            'content': {
                'word_count': self.word_count,
                'paragraph_count': self.paragraph_count,
                'is_thin_content': self.is_thin_content
            },
            'links': {
                'internal': self.internal_links_count,
                'external': self.external_links_count,
                'nofollow': self.nofollow_links_count
            },
            'images': {
                'total': self.total_images,
                'with_alt': self.images_with_alt,
                'missing_alt': self.images_missing_alt,
                'alt_coverage_percent': self.alt_coverage_percent
            },
            'issues': self.issues,
            'warnings': self.warnings,
            'passed': self.passed,
            'score': self.score
        }


class OnPageSEO:
    """
    Analyzes on-page SEO factors
    
    Checks:
    - Title length and optimization
    - Meta description length
    - H1 (single, matching title)
    - Heading hierarchy
    - Internal links count
    - Images alt coverage
    - Thin content detection
    """
    
    # Optimal ranges
    TITLE_MIN = 30
    TITLE_MAX = 60
    DESC_MIN = 120
    DESC_MAX = 160
    MIN_WORD_COUNT = 300
    
    def __init__(self):
        """Initialize on-page SEO analyzer"""
        self.http_client = HTTPClient(timeout=15)
    
    def analyze(self, url: str, html_content: str = None) -> OnPageSEOResult:
        """
        Perform on-page SEO analysis
        
        Args:
            url: Target URL
            html_content: Optional HTML content (fetches if not provided)
            
        Returns:
            OnPageSEOResult
        """
        result = OnPageSEOResult(url=url)
        
        # Fetch if not provided
        if not html_content:
            response = self.http_client.get(url)
            if not response or response.status_code != 200:
                result.issues.append({
                    'issue': 'Failed to fetch page',
                    'impact': 'CRITICAL',
                    'fix': 'Check if page is accessible'
                })
                return result
            html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        parsed_url = urlparse(url)
        
        # Analyze title
        self._analyze_title(soup, result)
        
        # Analyze meta description
        self._analyze_meta_description(soup, result)
        
        # Analyze headings
        self._analyze_headings(soup, result)
        
        # Analyze content
        self._analyze_content(soup, result)
        
        # Analyze links
        self._analyze_links(soup, result, parsed_url.netloc)
        
        # Analyze images
        self._analyze_images(soup, result)
        
        # Check title/H1 relationship
        self._check_title_h1_match(result)
        
        # Calculate score
        result.score = self._calculate_score(result)
        
        return result
    
    def _analyze_title(self, soup: BeautifulSoup, result: OnPageSEOResult):
        """Analyze title tag"""
        title_tag = soup.find('title')
        
        if title_tag:
            result.title = title_tag.get_text().strip()
            result.title_length = len(result.title)
            result.title_optimal = self.TITLE_MIN <= result.title_length <= self.TITLE_MAX
            
            if result.title_length == 0:
                result.issues.append({
                    'issue': 'Empty title tag',
                    'impact': 'HIGH',
                    'fix': 'Add descriptive title for the page'
                })
            elif result.title_length < self.TITLE_MIN:
                result.warnings.append({
                    'issue': f'Title too short ({result.title_length} chars)',
                    'impact': 'MEDIUM',
                    'fix': f'Aim for {self.TITLE_MIN}-{self.TITLE_MAX} characters'
                })
            elif result.title_length > self.TITLE_MAX:
                result.warnings.append({
                    'issue': f'Title too long ({result.title_length} chars)',
                    'impact': 'MEDIUM',
                    'fix': f'Aim for {self.TITLE_MIN}-{self.TITLE_MAX} characters'
                })
            else:
                result.passed.append(f"Title length optimal ({result.title_length} chars)")
        else:
            result.issues.append({
                'issue': 'Missing title tag',
                'impact': 'HIGH',
                'fix': 'Add <title> tag in the <head> section'
            })
    
    def _analyze_meta_description(self, soup: BeautifulSoup, result: OnPageSEOResult):
        """Analyze meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if meta_desc:
            result.meta_description = meta_desc.get('content', '').strip()
            result.meta_description_length = len(result.meta_description)
            result.meta_description_optimal = self.DESC_MIN <= result.meta_description_length <= self.DESC_MAX
            
            if result.meta_description_length == 0:
                result.issues.append({
                    'issue': 'Empty meta description',
                    'impact': 'MEDIUM',
                    'fix': 'Add descriptive meta description'
                })
            elif result.meta_description_length < self.DESC_MIN:
                result.warnings.append({
                    'issue': f'Meta description too short ({result.meta_description_length} chars)',
                    'impact': 'LOW',
                    'fix': f'Aim for {self.DESC_MIN}-{self.DESC_MAX} characters'
                })
            elif result.meta_description_length > self.DESC_MAX:
                result.warnings.append({
                    'issue': f'Meta description too long ({result.meta_description_length} chars)',
                    'impact': 'LOW',
                    'fix': f'Aim for {self.DESC_MIN}-{self.DESC_MAX} characters'
                })
            else:
                result.passed.append(f"Meta description length optimal ({result.meta_description_length} chars)")
        else:
            result.issues.append({
                'issue': 'Missing meta description',
                'impact': 'MEDIUM',
                'fix': 'Add <meta name="description" content="..."> tag'
            })
    
    def _analyze_headings(self, soup: BeautifulSoup, result: OnPageSEOResult):
        """Analyze heading structure"""
        # Count headings
        h1_tags = soup.find_all('h1')
        result.h1_count = len(h1_tags)
        result.h1_content = [h.get_text().strip()[:100] for h in h1_tags]
        
        result.h2_count = len(soup.find_all('h2'))
        result.h3_count = len(soup.find_all('h3'))
        
        # Check H1
        if result.h1_count == 0:
            result.issues.append({
                'issue': 'Missing H1 tag',
                'impact': 'HIGH',
                'fix': 'Add one H1 tag as main heading'
            })
        elif result.h1_count == 1:
            result.h1_optimal = True
            result.passed.append("Single H1 tag (optimal)")
        else:
            result.warnings.append({
                'issue': f'Multiple H1 tags ({result.h1_count})',
                'impact': 'MEDIUM',
                'fix': 'Use only one H1 per page'
            })
        
        # Check heading hierarchy
        self._check_heading_hierarchy(soup, result)
    
    def _check_heading_hierarchy(self, soup: BeautifulSoup, result: OnPageSEOResult):
        """Check if heading hierarchy is valid"""
        headings = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(tag.name[1])
            headings.append(level)
        
        if not headings:
            return
        
        # Check for skipped levels
        for i in range(1, len(headings)):
            if headings[i] > headings[i-1] + 1:
                result.heading_hierarchy_valid = False
                result.warnings.append({
                    'issue': 'Heading hierarchy has skipped levels',
                    'impact': 'LOW',
                    'fix': 'Use sequential heading levels (H1 → H2 → H3)'
                })
                break
        
        if result.heading_hierarchy_valid and len(headings) > 1:
            result.passed.append("Heading hierarchy is valid")
    
    def _analyze_content(self, soup: BeautifulSoup, result: OnPageSEOResult):
        """Analyze page content"""
        # Get main content area
        content_element = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find('div', class_=re.compile(r'content|article|post|entry', re.I)) or
            soup.find('body')
        )
        
        if not content_element:
            return
        
        # Clone to avoid modifying original
        content = BeautifulSoup(str(content_element), 'html.parser')
        
        # Remove non-content elements
        for tag in content.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            tag.decompose()
        
        # Count paragraphs
        paragraphs = content.find_all('p')
        result.paragraph_count = len(paragraphs)
        
        # Word count
        text = content.get_text(separator=' ', strip=True)
        words = text.split()
        result.word_count = len(words)
        
        # Average paragraph length
        if result.paragraph_count > 0:
            para_words = sum(len(p.get_text().split()) for p in paragraphs)
            result.avg_paragraph_length = para_words / result.paragraph_count
        
        # Thin content check
        if result.word_count < self.MIN_WORD_COUNT:
            result.is_thin_content = True
            result.warnings.append({
                'issue': f'Thin content ({result.word_count} words)',
                'impact': 'MEDIUM',
                'fix': f'Aim for at least {self.MIN_WORD_COUNT} words for in-depth content'
            })
        else:
            result.passed.append(f"Good content length ({result.word_count} words)")
    
    def _analyze_links(self, soup: BeautifulSoup, result: OnPageSEOResult, domain: str):
        """Analyze internal and external links"""
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            rel = link.get('rel', [])
            
            # Skip non-http links
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            # Check if internal or external
            parsed = urlparse(href)
            
            if not parsed.netloc or domain in parsed.netloc:
                result.internal_links_count += 1
            else:
                result.external_links_count += 1
            
            # Check nofollow
            if 'nofollow' in rel:
                result.nofollow_links_count += 1
        
        # Link recommendations
        if result.internal_links_count < 3:
            result.warnings.append({
                'issue': f'Few internal links ({result.internal_links_count})',
                'impact': 'LOW',
                'fix': 'Add more internal links to related content'
            })
        else:
            result.passed.append(f"Good internal linking ({result.internal_links_count} links)")
    
    def _analyze_images(self, soup: BeautifulSoup, result: OnPageSEOResult):
        """Analyze images for alt text"""
        images = soup.find_all('img')
        result.total_images = len(images)
        
        for img in images:
            alt = img.get('alt', '')
            src = img.get('src', '')
            
            # Skip tracking pixels and icons
            if src and any(x in src.lower() for x in ['pixel', 'tracking', '.gif', 'icon', 'logo']):
                result.total_images -= 1
                continue
            
            if alt and alt.strip():
                result.images_with_alt += 1
            else:
                result.images_missing_alt += 1
        
        # Calculate coverage
        if result.total_images > 0:
            result.alt_coverage_percent = (result.images_with_alt / result.total_images) * 100
            
            if result.images_missing_alt > 0:
                result.warnings.append({
                    'issue': f'{result.images_missing_alt} image(s) missing alt text',
                    'impact': 'MEDIUM',
                    'fix': 'Add descriptive alt text to all images'
                })
            else:
                result.passed.append("All images have alt text")
    
    def _check_title_h1_match(self, result: OnPageSEOResult):
        """Check if title and H1 are aligned"""
        if result.title and result.h1_content:
            h1_text = result.h1_content[0].lower()
            title_text = result.title.lower()
            
            # Check for significant word overlap
            title_words = set(title_text.split())
            h1_words = set(h1_text.split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are'}
            title_words -= stop_words
            h1_words -= stop_words
            
            if title_words and h1_words:
                overlap = len(title_words & h1_words) / min(len(title_words), len(h1_words))
                result.title_in_h1 = overlap > 0.5
    
    def _calculate_score(self, result: OnPageSEOResult) -> float:
        """Calculate on-page SEO score"""
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
    
    def analyze_batch(self, urls: List[str], max_pages: int = 10) -> Dict[str, Any]:
        """
        Analyze multiple pages
        
        Args:
            urls: List of URLs
            max_pages: Maximum pages to analyze
            
        Returns:
            Aggregated results
        """
        results = {
            'pages': [],
            'summary': {
                'avg_title_length': 0,
                'avg_description_length': 0,
                'avg_word_count': 0,
                'pages_with_h1_issues': 0,
                'thin_content_pages': 0,
                'missing_alt_images': 0,
                'avg_score': 0
            }
        }
        
        total_title_len = 0
        total_desc_len = 0
        total_words = 0
        total_score = 0
        
        for url in urls[:max_pages]:
            page_result = self.analyze(url)
            results['pages'].append(page_result.to_dict())
            
            total_title_len += page_result.title_length
            total_desc_len += page_result.meta_description_length
            total_words += page_result.word_count
            total_score += page_result.score
            
            if not page_result.h1_optimal:
                results['summary']['pages_with_h1_issues'] += 1
            if page_result.is_thin_content:
                results['summary']['thin_content_pages'] += 1
            results['summary']['missing_alt_images'] += page_result.images_missing_alt
        
        n = len(results['pages'])
        if n > 0:
            results['summary']['avg_title_length'] = round(total_title_len / n, 1)
            results['summary']['avg_description_length'] = round(total_desc_len / n, 1)
            results['summary']['avg_word_count'] = round(total_words / n, 1)
            results['summary']['avg_score'] = round(total_score / n, 1)
        
        return results
