"""
CMS Scanner Module
Specialized scanner for detecting CMS platforms, plugins, and themes (WordPress focus)
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from utils.http_client import HTTPClient
from utils.helpers import is_wordpress_site


class CMSScanner:
    """Scanner for CMS detection and analysis"""
    
    def __init__(self):
        """Initialize CMS scanner"""
        self.http_client = HTTPClient()
        self.results = {}
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform CMS detection and analysis
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary containing CMS information
        """
        print(f"[*] Scanning CMS information for: {url}")
        
        results = {
            'url': url,
            'cms_detected': None,
            'wordpress': None,
            'joomla': None,
            'drupal': None
        }
        
        # Get initial page
        response = self.http_client.get(url)
        if not response:
            print("  [-] Failed to fetch website")
            return results
        
        html_content = response.text
        
        # Detect CMS type
        cms_type = self._detect_cms_type(html_content)
        results['cms_detected'] = cms_type
        
        # Perform specialized scanning based on CMS
        if cms_type == 'WordPress':
            results['wordpress'] = self._scan_wordpress(url, html_content)
        elif cms_type == 'Joomla':
            results['joomla'] = self._scan_joomla(url, html_content)
        elif cms_type == 'Drupal':
            results['drupal'] = self._scan_drupal(url, html_content)
        
        self.results = results
        return results
    
    def _detect_cms_type(self, html_content: str) -> str:
        """
        Detect CMS type from HTML content
        
        Args:
            html_content: HTML content of the page
            
        Returns:
            CMS name or 'Unknown'
        """
        print("  [+] Detecting CMS type...")
        
        # WordPress detection
        if is_wordpress_site(html_content):
            return 'WordPress'
        
        # Joomla detection
        if re.search(r'joomla', html_content, re.IGNORECASE) or \
           re.search(r'/components/com_', html_content):
            return 'Joomla'
        
        # Drupal detection
        if re.search(r'Drupal', html_content, re.IGNORECASE) or \
           re.search(r'/sites/default/', html_content):
            return 'Drupal'
        
        # Magento detection
        if re.search(r'Mage\.Cookies', html_content) or \
           re.search(r'/skin/frontend/', html_content):
            return 'Magento'
        
        # Shopify detection
        if re.search(r'cdn\.shopify\.com', html_content):
            return 'Shopify'
        
        # PrestaShop detection
        if re.search(r'prestashop', html_content, re.IGNORECASE):
            return 'PrestaShop'
        
        return 'Unknown'
    
    def _scan_wordpress(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Perform detailed WordPress scanning
        
        Args:
            url: Target URL
            html_content: HTML content
            
        Returns:
            Dictionary with WordPress information
        """
        print("  [+] Performing WordPress scan...")
        
        wp_info = {
            'version': self._detect_wp_version(url, html_content),
            'theme': self._detect_wp_theme(html_content),
            'plugins': self._detect_wp_plugins(html_content),
            'api_exposed': self._check_wp_api(url)
        }
        
        return wp_info
    
    def _detect_wp_version(self, url: str, html_content: str) -> str:
        """
        Detect WordPress version
        
        Args:
            url: Target URL
            html_content: HTML content
            
        Returns:
            WordPress version or 'Unknown'
        """
        try:
            # Check meta generator tag
            soup = BeautifulSoup(html_content, 'html.parser')
            generator = soup.find('meta', attrs={'name': 'generator'})
            
            if generator:
                content = generator.get('content', '')
                match = re.search(r'WordPress\s+([\d.]+)', content)
                if match:
                    return match.group(1)
            
            # Try to fetch readme.html
            readme_url = url.rstrip('/') + '/readme.html'
            response = self.http_client.get(readme_url)
            
            if response and response.status_code == 200:
                match = re.search(r'Version\s+([\d.]+)', response.text)
                if match:
                    return match.group(1)
            
            return 'Unknown'
        except Exception as e:
            print(f"  [-] Version detection failed: {e}")
            return 'Unknown'
    
    def _detect_wp_theme(self, html_content: str) -> Dict[str, Any]:
        """
        Detect WordPress theme
        
        Args:
            html_content: HTML content
            
        Returns:
            Dictionary with theme information
        """
        try:
            theme_info = {
                'name': 'Unknown',
                'path': None
            }
            
            # Look for theme directory in HTML
            match = re.search(r'/wp-content/themes/([^/\'"]+)', html_content)
            if match:
                theme_info['name'] = match.group(1)
                theme_info['path'] = f"/wp-content/themes/{match.group(1)}"
            
            return theme_info
        except Exception as e:
            print(f"  [-] Theme detection failed: {e}")
            return {'name': 'Unknown', 'path': None}
    
    def _detect_wp_plugins(self, html_content: str) -> List[str]:
        """
        Detect WordPress plugins
        
        Args:
            html_content: HTML content
            
        Returns:
            List of detected plugins
        """
        try:
            plugins = set()
            
            # Find plugin references in HTML
            plugin_matches = re.findall(r'/wp-content/plugins/([^/\'"]+)', html_content)
            
            for plugin in plugin_matches:
                if plugin and plugin not in ['', ' ']:
                    plugins.add(plugin)
            
            return list(plugins)
        except Exception as e:
            print(f"  [-] Plugin detection failed: {e}")
            return []
    
    def _check_wp_api(self, url: str) -> bool:
        """
        Check if WordPress REST API is accessible
        
        Args:
            url: Target URL
            
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            api_url = url.rstrip('/') + '/wp-json/'
            response = self.http_client.get(api_url)
            
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    def _scan_joomla(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Perform Joomla scanning
        
        Args:
            url: Target URL
            html_content: HTML content
            
        Returns:
            Dictionary with Joomla information
        """
        print("  [+] Performing Joomla scan...")
        
        joomla_info = {
            'version': 'Unknown',
            'components': [],
            'modules': []
        }
        
        try:
            # Detect components
            components = re.findall(r'/components/(com_[^/\'"]+)', html_content)
            joomla_info['components'] = list(set(components))
            
            # Detect modules
            modules = re.findall(r'/modules/(mod_[^/\'"]+)', html_content)
            joomla_info['modules'] = list(set(modules))
            
        except Exception as e:
            print(f"  [-] Joomla scan failed: {e}")
        
        return joomla_info
    
    def _scan_drupal(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Perform Drupal scanning
        
        Args:
            url: Target URL
            html_content: HTML content
            
        Returns:
            Dictionary with Drupal information
        """
        print("  [+] Performing Drupal scan...")
        
        drupal_info = {
            'version': 'Unknown',
            'modules': []
        }
        
        try:
            # Try to detect version from meta generator
            soup = BeautifulSoup(html_content, 'html.parser')
            generator = soup.find('meta', attrs={'name': 'generator'})
            
            if generator:
                content = generator.get('content', '')
                match = re.search(r'Drupal\s+([\d.]+)', content)
                if match:
                    drupal_info['version'] = match.group(1)
            
            # Detect modules
            modules = re.findall(r'/sites/[^/]+/modules/([^/\'"]+)', html_content)
            drupal_info['modules'] = list(set(modules))
            
        except Exception as e:
            print(f"  [-] Drupal scan failed: {e}")
        
        return drupal_info
