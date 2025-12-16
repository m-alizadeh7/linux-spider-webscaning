"""
CMS Scanner Module
Specialized scanner for detecting CMS platforms, plugins, and themes
Deep WordPress analysis with security and SEO insights
"""

import re
import json
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from utils.http_client import HTTPClient
from utils.helpers import is_wordpress_site


class CMSScanner:
    """Scanner for CMS detection and analysis with WordPress deep dive"""
    
    # Known WordPress plugins with SEO/Security importance
    IMPORTANT_PLUGINS = {
        # SEO Plugins
        'yoast-seo': {'category': 'SEO', 'importance': 'high', 'description': 'SEO optimization plugin'},
        'wordpress-seo': {'category': 'SEO', 'importance': 'high', 'description': 'Yoast SEO'},
        'all-in-one-seo-pack': {'category': 'SEO', 'importance': 'high', 'description': 'All in One SEO'},
        'rank-math-seo': {'category': 'SEO', 'importance': 'high', 'description': 'Rank Math SEO'},
        'seo-by-rank-math': {'category': 'SEO', 'importance': 'high', 'description': 'Rank Math SEO'},
        
        # Security Plugins
        'wordfence': {'category': 'Security', 'importance': 'high', 'description': 'Wordfence Security'},
        'sucuri-scanner': {'category': 'Security', 'importance': 'high', 'description': 'Sucuri Security'},
        'ithemes-security': {'category': 'Security', 'importance': 'high', 'description': 'iThemes Security'},
        'better-wp-security': {'category': 'Security', 'importance': 'high', 'description': 'iThemes Security'},
        'all-in-one-wp-security-and-firewall': {'category': 'Security', 'importance': 'high', 'description': 'All In One WP Security'},
        
        # Performance/Cache
        'wp-super-cache': {'category': 'Performance', 'importance': 'medium', 'description': 'WP Super Cache'},
        'w3-total-cache': {'category': 'Performance', 'importance': 'medium', 'description': 'W3 Total Cache'},
        'wp-rocket': {'category': 'Performance', 'importance': 'high', 'description': 'WP Rocket (Premium)'},
        'litespeed-cache': {'category': 'Performance', 'importance': 'high', 'description': 'LiteSpeed Cache'},
        'autoptimize': {'category': 'Performance', 'importance': 'medium', 'description': 'Autoptimize'},
        
        # Page Builders
        'elementor': {'category': 'Builder', 'importance': 'medium', 'description': 'Elementor Page Builder'},
        'js_composer': {'category': 'Builder', 'importance': 'medium', 'description': 'WPBakery Page Builder'},
        'beaver-builder': {'category': 'Builder', 'importance': 'medium', 'description': 'Beaver Builder'},
        'divi-builder': {'category': 'Builder', 'importance': 'medium', 'description': 'Divi Builder'},
        
        # E-commerce
        'woocommerce': {'category': 'E-commerce', 'importance': 'high', 'description': 'WooCommerce'},
        'easy-digital-downloads': {'category': 'E-commerce', 'importance': 'medium', 'description': 'Easy Digital Downloads'},
        
        # Forms
        'contact-form-7': {'category': 'Forms', 'importance': 'low', 'description': 'Contact Form 7'},
        'wpforms': {'category': 'Forms', 'importance': 'low', 'description': 'WPForms'},
        'wpforms-lite': {'category': 'Forms', 'importance': 'low', 'description': 'WPForms Lite'},
        'gravity-forms': {'category': 'Forms', 'importance': 'low', 'description': 'Gravity Forms'},
        
        # Analytics
        'google-analytics-for-wordpress': {'category': 'Analytics', 'importance': 'medium', 'description': 'MonsterInsights'},
        'google-site-kit': {'category': 'Analytics', 'importance': 'medium', 'description': 'Google Site Kit'},
        
        # Backup
        'updraftplus': {'category': 'Backup', 'importance': 'medium', 'description': 'UpdraftPlus Backup'},
        'duplicator': {'category': 'Backup', 'importance': 'medium', 'description': 'Duplicator'},
    }
    
    # Vulnerable plugin patterns
    VULNERABLE_PLUGINS = {
        'revslider': 'Revolution Slider - Check for updates (historically vulnerable)',
        'layerslider': 'LayerSlider - Check for updates',
        'timthumb': 'TimThumb - Deprecated, should be removed',
        'wp-file-manager': 'WP File Manager - Update immediately if using',
    }
    
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
            'cms_confidence': 0,
            'wordpress': None,
            'joomla': None,
            'drupal': None,
            'other_cms': None
        }
        
        # Get initial page
        response = self.http_client.get(url)
        if not response:
            print("  [-] Failed to fetch website")
            return results
        
        html_content = response.text
        headers = response.headers
        
        # Detect CMS type
        cms_type, confidence = self._detect_cms_type(html_content, headers)
        results['cms_detected'] = cms_type
        results['cms_confidence'] = confidence
        
        # Perform specialized scanning based on CMS
        if cms_type == 'WordPress':
            results['wordpress'] = self._scan_wordpress_deep(url, html_content)
        elif cms_type == 'Joomla':
            results['joomla'] = self._scan_joomla(url, html_content)
        elif cms_type == 'Drupal':
            results['drupal'] = self._scan_drupal(url, html_content)
        elif cms_type not in ['Unknown', None]:
            results['other_cms'] = {'name': cms_type, 'details': {}}
        
        self.results = results
        return results
    
    def _detect_cms_type(self, html_content: str, headers: Dict) -> tuple:
        """Detect CMS type with confidence level"""
        print("  [+] Detecting CMS type...")
        
        # WordPress detection (most thorough)
        wp_score = 0
        if is_wordpress_site(html_content):
            wp_score += 50
        if 'wp-content' in html_content:
            wp_score += 30
        if re.search(r'/wp-includes/', html_content):
            wp_score += 20
        if headers.get('X-Powered-By', '').lower().find('wordpress') >= 0:
            wp_score += 20
        if headers.get('Link', '').find('wp-json') >= 0:
            wp_score += 20
        
        if wp_score >= 50:
            return 'WordPress', min(wp_score, 100)
        
        # Joomla detection
        joomla_score = 0
        if re.search(r'/components/com_', html_content):
            joomla_score += 40
        if re.search(r'/media/jui/', html_content):
            joomla_score += 30
        if re.search(r'Joomla!', html_content):
            joomla_score += 30
        
        if joomla_score >= 40:
            return 'Joomla', min(joomla_score, 100)
        
        # Drupal detection
        drupal_score = 0
        if re.search(r'Drupal', html_content, re.IGNORECASE):
            drupal_score += 30
        if re.search(r'/sites/default/', html_content):
            drupal_score += 40
        if headers.get('X-Generator', '').find('Drupal') >= 0:
            drupal_score += 30
        
        if drupal_score >= 40:
            return 'Drupal', min(drupal_score, 100)
        
        # Other CMS detection
        if re.search(r'cdn\.shopify\.com', html_content):
            return 'Shopify', 90
        if re.search(r'Mage\.Cookies|/skin/frontend/', html_content):
            return 'Magento', 80
        if re.search(r'prestashop', html_content, re.IGNORECASE):
            return 'PrestaShop', 80
        if re.search(r'wix\.com', html_content):
            return 'Wix', 90
        if re.search(r'squarespace', html_content, re.IGNORECASE):
            return 'Squarespace', 90
        if re.search(r'webflow', html_content, re.IGNORECASE):
            return 'Webflow', 85
        
        return 'Unknown', 0
    
    def _scan_wordpress_deep(self, url: str, html_content: str) -> Dict[str, Any]:
        """Perform deep WordPress analysis"""
        print("  [+] Performing deep WordPress scan...")
        
        wp_info = {
            'version': self._detect_wp_version(url, html_content),
            'theme': self._detect_wp_theme_detailed(url, html_content),
            'plugins': self._detect_wp_plugins_detailed(url, html_content),
            'security': self._check_wp_security(url),
            'seo_config': self._check_wp_seo_config(html_content),
            'api': self._check_wp_api_detailed(url),
            'users': self._enumerate_wp_users(url),
            'recommendations': []
        }
        
        # Generate recommendations
        wp_info['recommendations'] = self._generate_wp_recommendations(wp_info)
        
        return wp_info
    
    def _detect_wp_version(self, url: str, html_content: str) -> Dict[str, Any]:
        """Detect WordPress version with security check"""
        version_info = {
            'version': 'Unknown',
            'method': None,
            'is_outdated': None,
            'security_note': None
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check meta generator
            generator = soup.find('meta', attrs={'name': 'generator'})
            if generator:
                content = generator.get('content', '')
                match = re.search(r'WordPress\s+([\d.]+)', content)
                if match:
                    version_info['version'] = match.group(1)
                    version_info['method'] = 'meta_generator'
                    version_info['security_note'] = 'Version exposed in meta tag - consider hiding'
            
            # Check RSS feed
            if version_info['version'] == 'Unknown':
                feed_url = url.rstrip('/') + '/feed/'
                response = self.http_client.get(feed_url)
                if response and response.status_code == 200:
                    match = re.search(r'<generator>.*WordPress.*?([\d.]+).*</generator>', response.text)
                    if match:
                        version_info['version'] = match.group(1)
                        version_info['method'] = 'rss_feed'
            
            # Check for outdated version (simplified check)
            if version_info['version'] != 'Unknown':
                major = version_info['version'].split('.')[0]
                if int(major) < 6:
                    version_info['is_outdated'] = True
                    version_info['security_note'] = 'WordPress version appears outdated - update recommended'
            
        except Exception as e:
            print(f"    ⚠ Version detection error: {e}")
        
        return version_info
    
    def _detect_wp_theme_detailed(self, url: str, html_content: str) -> Dict[str, Any]:
        """Detect WordPress theme with details"""
        theme_info = {
            'name': 'Unknown',
            'path': None,
            'parent_theme': None,
            'is_child_theme': False,
            'style_css': None
        }
        
        try:
            # Find theme from HTML
            match = re.search(r'/wp-content/themes/([^/\'"]+)', html_content)
            if match:
                theme_name = match.group(1)
                theme_info['name'] = theme_name
                theme_info['path'] = f"/wp-content/themes/{theme_name}"
                
                # Try to fetch style.css for more info
                style_url = f"{url.rstrip('/')}/wp-content/themes/{theme_name}/style.css"
                response = self.http_client.get(style_url)
                
                if response and response.status_code == 200:
                    css_content = response.text[:2000]
                    
                    # Parse theme headers
                    theme_name_match = re.search(r'Theme Name:\s*(.+)', css_content)
                    if theme_name_match:
                        theme_info['name'] = theme_name_match.group(1).strip()
                    
                    parent_match = re.search(r'Template:\s*(.+)', css_content)
                    if parent_match:
                        theme_info['is_child_theme'] = True
                        theme_info['parent_theme'] = parent_match.group(1).strip()
                    
                    version_match = re.search(r'Version:\s*([\d.]+)', css_content)
                    if version_match:
                        theme_info['version'] = version_match.group(1)
        
        except Exception as e:
            print(f"    ⚠ Theme detection error: {e}")
        
        return theme_info
    
    def _detect_wp_plugins_detailed(self, url: str, html_content: str) -> Dict[str, Any]:
        """Detect WordPress plugins with categorization"""
        plugins_info = {
            'detected': [],
            'by_category': {},
            'security_plugins': [],
            'seo_plugins': [],
            'vulnerable_warnings': [],
            'total_count': 0
        }
        
        try:
            detected_plugins = set()
            
            # Find from HTML
            plugin_matches = re.findall(r'/wp-content/plugins/([^/\'"]+)', html_content)
            for plugin in plugin_matches:
                if plugin and plugin not in ['', ' ']:
                    detected_plugins.add(plugin)
            
            # Categorize plugins
            for plugin in detected_plugins:
                plugin_lower = plugin.lower()
                
                plugin_data = {
                    'name': plugin,
                    'category': 'Other',
                    'importance': 'unknown',
                    'description': None
                }
                
                # Check if it's a known important plugin
                if plugin_lower in self.IMPORTANT_PLUGINS:
                    info = self.IMPORTANT_PLUGINS[plugin_lower]
                    plugin_data['category'] = info['category']
                    plugin_data['importance'] = info['importance']
                    plugin_data['description'] = info['description']
                    
                    if info['category'] == 'Security':
                        plugins_info['security_plugins'].append(plugin)
                    elif info['category'] == 'SEO':
                        plugins_info['seo_plugins'].append(plugin)
                
                # Check for known vulnerable plugins
                for vuln_plugin, warning in self.VULNERABLE_PLUGINS.items():
                    if vuln_plugin in plugin_lower:
                        plugins_info['vulnerable_warnings'].append({
                            'plugin': plugin,
                            'warning': warning
                        })
                
                plugins_info['detected'].append(plugin_data)
                
                # Group by category
                cat = plugin_data['category']
                if cat not in plugins_info['by_category']:
                    plugins_info['by_category'][cat] = []
                plugins_info['by_category'][cat].append(plugin)
            
            plugins_info['total_count'] = len(detected_plugins)
            
        except Exception as e:
            print(f"    ⚠ Plugin detection error: {e}")
        
        return plugins_info
    
    def _check_wp_security(self, url: str) -> Dict[str, Any]:
        """Check WordPress security configuration"""
        security = {
            'xmlrpc_enabled': None,
            'user_enumeration': None,
            'readme_exposed': None,
            'debug_log_exposed': None,
            'issues': [],
            'score': 100
        }
        
        try:
            base_url = url.rstrip('/')
            
            # Check XML-RPC
            xmlrpc_url = f"{base_url}/xmlrpc.php"
            response = self.http_client.post(xmlrpc_url, data='<methodCall><methodName>system.listMethods</methodName></methodCall>')
            if response and response.status_code == 200:
                security['xmlrpc_enabled'] = True
                security['issues'].append('XML-RPC is enabled - potential brute force vector')
                security['score'] -= 15
            
            # Check readme.html
            readme_url = f"{base_url}/readme.html"
            response = self.http_client.head(readme_url)
            if response and response.status_code == 200:
                security['readme_exposed'] = True
                security['issues'].append('readme.html exposed - reveals WordPress version')
                security['score'] -= 10
            
            # Check debug.log
            debug_url = f"{base_url}/wp-content/debug.log"
            response = self.http_client.head(debug_url)
            if response and response.status_code == 200:
                security['debug_log_exposed'] = True
                security['issues'].append('debug.log exposed - may contain sensitive info')
                security['score'] -= 25
            
        except Exception as e:
            print(f"    ⚠ Security check error: {e}")
        
        return security
    
    def _check_wp_seo_config(self, html_content: str) -> Dict[str, Any]:
        """Check WordPress SEO configuration"""
        seo = {
            'has_seo_plugin': False,
            'seo_plugin_name': None,
            'yoast_meta': False,
            'schema_markup': False,
            'og_tags': False
        }
        
        try:
            # Check for SEO plugin indicators
            if 'yoast' in html_content.lower():
                seo['has_seo_plugin'] = True
                seo['seo_plugin_name'] = 'Yoast SEO'
                seo['yoast_meta'] = True
            elif 'rank-math' in html_content.lower():
                seo['has_seo_plugin'] = True
                seo['seo_plugin_name'] = 'Rank Math'
            elif 'all-in-one-seo' in html_content.lower():
                seo['has_seo_plugin'] = True
                seo['seo_plugin_name'] = 'All in One SEO'
            
            # Check for schema markup
            if re.search(r'application/ld\+json', html_content):
                seo['schema_markup'] = True
            
            # Check for Open Graph tags
            if re.search(r'og:title|og:description', html_content):
                seo['og_tags'] = True
            
        except Exception:
            pass
        
        return seo
    
    def _check_wp_api_detailed(self, url: str) -> Dict[str, Any]:
        """Check WordPress REST API"""
        api_info = {
            'enabled': False,
            'exposed_endpoints': [],
            'user_endpoint': False
        }
        
        try:
            api_url = f"{url.rstrip('/')}/wp-json/"
            response = self.http_client.get(api_url)
            
            if response and response.status_code == 200:
                api_info['enabled'] = True
                
                try:
                    data = response.json()
                    if 'routes' in data:
                        api_info['exposed_endpoints'] = list(data['routes'].keys())[:20]
                except:
                    pass
                
                # Check user endpoint
                users_url = f"{url.rstrip('/')}/wp-json/wp/v2/users"
                user_response = self.http_client.get(users_url)
                if user_response and user_response.status_code == 200:
                    api_info['user_endpoint'] = True
            
        except Exception:
            pass
        
        return api_info
    
    def _enumerate_wp_users(self, url: str) -> List[Dict]:
        """Enumerate WordPress users (limited and ethical)"""
        users = []
        
        try:
            # Try author enumeration
            for i in range(1, 4):  # Only first 3 authors
                author_url = f"{url.rstrip('/')}/?author={i}"
                response = self.http_client.get(author_url, allow_redirects=True)
                
                if response and response.status_code == 200:
                    # Check for username in URL after redirect
                    if '/author/' in response.url:
                        match = re.search(r'/author/([^/]+)', response.url)
                        if match:
                            users.append({
                                'id': i,
                                'username': match.group(1)
                            })
        except:
            pass
        
        return users
    
    def _generate_wp_recommendations(self, wp_info: Dict) -> List[Dict]:
        """Generate WordPress-specific recommendations"""
        recommendations = []
        
        # Version recommendations
        if wp_info.get('version', {}).get('is_outdated'):
            recommendations.append({
                'priority': 1,
                'category': 'Security',
                'title': 'Update WordPress Core',
                'description': 'WordPress version is outdated. Update to latest version.'
            })
        
        # Security recommendations
        security = wp_info.get('security', {})
        if security.get('xmlrpc_enabled'):
            recommendations.append({
                'priority': 2,
                'category': 'Security',
                'title': 'Disable XML-RPC',
                'description': 'XML-RPC is enabled and can be exploited for brute force attacks.'
            })
        
        if security.get('debug_log_exposed'):
            recommendations.append({
                'priority': 1,
                'category': 'Security',
                'title': 'Secure Debug Log',
                'description': 'Debug log is publicly accessible. Block access or disable debug mode.'
            })
        
        # SEO recommendations
        seo = wp_info.get('seo_config', {})
        if not seo.get('has_seo_plugin'):
            recommendations.append({
                'priority': 2,
                'category': 'SEO',
                'title': 'Install SEO Plugin',
                'description': 'No SEO plugin detected. Consider Yoast SEO or Rank Math.'
            })
        
        if not seo.get('schema_markup'):
            recommendations.append({
                'priority': 3,
                'category': 'SEO',
                'title': 'Add Schema Markup',
                'description': 'No structured data detected. Add JSON-LD schema for better SEO.'
            })
        
        # Plugin recommendations
        plugins = wp_info.get('plugins', {})
        if not plugins.get('security_plugins'):
            recommendations.append({
                'priority': 2,
                'category': 'Security',
                'title': 'Install Security Plugin',
                'description': 'No security plugin detected. Consider Wordfence or Sucuri.'
            })
        
        for vuln in plugins.get('vulnerable_warnings', []):
            recommendations.append({
                'priority': 1,
                'category': 'Security',
                'title': f"Update {vuln['plugin']}",
                'description': vuln['warning']
            })
        
        return recommendations
    
    def _scan_joomla(self, url: str, html_content: str) -> Dict[str, Any]:
        """Perform Joomla scanning"""
        print("  [+] Performing Joomla scan...")
        
        joomla_info = {
            'version': 'Unknown',
            'components': [],
            'modules': [],
            'templates': []
        }
        
        try:
            components = re.findall(r'/components/(com_[^/\'"]+)', html_content)
            joomla_info['components'] = list(set(components))
            
            modules = re.findall(r'/modules/(mod_[^/\'"]+)', html_content)
            joomla_info['modules'] = list(set(modules))
            
            templates = re.findall(r'/templates/([^/\'"]+)', html_content)
            joomla_info['templates'] = list(set(templates))
            
        except Exception as e:
            print(f"  [-] Joomla scan failed: {e}")
        
        return joomla_info
    
    def _scan_drupal(self, url: str, html_content: str) -> Dict[str, Any]:
        """Perform Drupal scanning"""
        print("  [+] Performing Drupal scan...")
        
        drupal_info = {
            'version': 'Unknown',
            'modules': [],
            'themes': []
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            generator = soup.find('meta', attrs={'name': 'generator'})
            
            if generator:
                content = generator.get('content', '')
                match = re.search(r'Drupal\s+([\d.]+)', content)
                if match:
                    drupal_info['version'] = match.group(1)
            
            modules = re.findall(r'/sites/[^/]+/modules/([^/\'"]+)', html_content)
            drupal_info['modules'] = list(set(modules))
            
            themes = re.findall(r'/sites/[^/]+/themes/([^/\'"]+)', html_content)
            drupal_info['themes'] = list(set(themes))
            
        except Exception as e:
            print(f"  [-] Drupal scan failed: {e}")
        
        return drupal_info
