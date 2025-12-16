"""
Technology Scanner Module
Detects technologies, frameworks, and libraries used by the website
"""

import re
import builtwith
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Set
from utils.http_client import HTTPClient


class TechnologyScanner:
    """Scanner for detecting web technologies"""
    
    def __init__(self):
        """Initialize technology scanner"""
        self.http_client = HTTPClient()
        self.results = {}
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform technology detection scan
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary containing detected technologies
        """
        print(f"[*] Scanning technologies for: {url}")
        
        results = {
            'url': url,
            'builtwith_analysis': self._analyze_with_builtwith(url),
            'manual_detection': self._manual_detection(url),
            'javascript_libraries': self._detect_js_libraries(url),
            'meta_generators': self._detect_meta_generators(url)
        }
        
        self.results = results
        return results
    
    def _analyze_with_builtwith(self, url: str) -> Dict[str, List[str]]:
        """
        Use BuiltWith library for technology detection
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with detected technologies
        """
        try:
            print("  [+] Analyzing with BuiltWith...")
            tech_data = builtwith.parse(url)
            return tech_data
        except Exception as e:
            print(f"  [-] BuiltWith analysis failed: {e}")
            return {}
    
    def _manual_detection(self, url: str) -> Dict[str, List[str]]:
        """
        Manual technology detection from HTML content
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with detected technologies
        """
        try:
            print("  [+] Performing manual detection...")
            response = self.http_client.get(url)
            
            if not response or not response.content:
                return {}
            
            html_content = response.text
            detected = {
                'cms': [],
                'frameworks': [],
                'analytics': [],
                'advertising': [],
                'cdn': [],
                'web_servers': [],
                'programming_languages': []
            }
            
            # CMS Detection patterns
            cms_patterns = {
                'WordPress': [r'wp-content', r'wp-includes', r'/wp-json/'],
                'Joomla': [r'/components/com_', r'Joomla!'],
                'Drupal': [r'Drupal', r'/sites/default/'],
                'Magento': [r'Mage.Cookies', r'/skin/frontend/'],
                'Shopify': [r'cdn.shopify.com', r'Shopify'],
                'Wix': [r'wix.com', r'_wix'],
                'Squarespace': [r'squarespace'],
                'PrestaShop': [r'prestashop']
            }
            
            for cms, patterns in cms_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        if cms not in detected['cms']:
                            detected['cms'].append(cms)
                        break
            
            # Framework Detection
            framework_patterns = {
                'React': [r'react', r'_react'],
                'Vue.js': [r'vue\.js', r'__vue__'],
                'Angular': [r'angular', r'ng-'],
                'Bootstrap': [r'bootstrap'],
                'jQuery': [r'jquery'],
                'Next.js': [r'_next'],
                'Nuxt.js': [r'__nuxt'],
                'Laravel': [r'laravel_session'],
                'Django': [r'csrftoken', r'django'],
                'Flask': [r'flask']
            }
            
            for framework, patterns in framework_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        if framework not in detected['frameworks']:
                            detected['frameworks'].append(framework)
                        break
            
            # Analytics Detection
            analytics_patterns = {
                'Google Analytics': [r'google-analytics\.com', r'ga\.js'],
                'Google Tag Manager': [r'googletagmanager\.com'],
                'Facebook Pixel': [r'facebook\.net.*fbevents'],
                'Hotjar': [r'hotjar\.com'],
                'Matomo': [r'matomo', r'piwik']
            }
            
            for tool, patterns in analytics_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        if tool not in detected['analytics']:
                            detected['analytics'].append(tool)
                        break
            
            # CDN Detection
            cdn_patterns = {
                'Cloudflare': [r'cloudflare', r'cf-ray'],
                'Amazon CloudFront': [r'cloudfront\.net'],
                'Akamai': [r'akamai'],
                'Fastly': [r'fastly'],
                'MaxCDN': [r'maxcdn']
            }
            
            for cdn, patterns in cdn_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        if cdn not in detected['cdn']:
                            detected['cdn'].append(cdn)
                        break
            
            # Check headers for additional info
            headers = response.headers
            if 'Server' in headers:
                detected['web_servers'].append(headers['Server'])
            if 'X-Powered-By' in headers:
                detected['programming_languages'].append(headers['X-Powered-By'])
            
            return detected
        except Exception as e:
            print(f"  [-] Manual detection failed: {e}")
            return {}
    
    def _detect_js_libraries(self, url: str) -> List[str]:
        """
        Detect JavaScript libraries used
        
        Args:
            url: Target URL
            
        Returns:
            List of detected JavaScript libraries
        """
        try:
            print("  [+] Detecting JavaScript libraries...")
            response = self.http_client.get(url)
            
            if not response:
                return []
            
            html_content = response.text
            libraries = set()
            
            # Common JS library patterns
            js_patterns = {
                'jQuery': r'jquery[.-](\d+\.)*\d+',
                'React': r'react[.-](\d+\.)*\d+',
                'Vue.js': r'vue[.-](\d+\.)*\d+',
                'Angular': r'angular[.-](\d+\.)*\d+',
                'Lodash': r'lodash[.-](\d+\.)*\d+',
                'Moment.js': r'moment[.-](\d+\.)*\d+',
                'Chart.js': r'chart[.-](\d+\.)*\d+',
                'D3.js': r'd3[.-](\d+\.)*\d+',
                'Three.js': r'three[.-](\d+\.)*\d+',
                'GSAP': r'gsap[.-](\d+\.)*\d+',
                'Axios': r'axios[.-](\d+\.)*\d+',
                'Swiper': r'swiper[.-](\d+\.)*\d+',
                'Slick': r'slick[.-](\d+\.)*\d+',
            }
            
            for lib, pattern in js_patterns.items():
                if re.search(pattern, html_content, re.IGNORECASE):
                    libraries.add(lib)
            
            return list(libraries)
        except Exception as e:
            print(f"  [-] JS library detection failed: {e}")
            return []
    
    def _detect_meta_generators(self, url: str) -> List[str]:
        """
        Detect generator meta tags
        
        Args:
            url: Target URL
            
        Returns:
            List of detected generators
        """
        try:
            print("  [+] Detecting meta generators...")
            response = self.http_client.get(url)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            generators = []
            
            # Find generator meta tags
            meta_tags = soup.find_all('meta', attrs={'name': 'generator'})
            for tag in meta_tags:
                content = tag.get('content', '')
                if content:
                    generators.append(content)
            
            return generators
        except Exception as e:
            print(f"  [-] Meta generator detection failed: {e}")
            return []
