"""
Security Scanner Module
Performs security analysis including headers, SSL, common vulnerabilities
"""

import re
import socket
from urllib.parse import urlparse
from typing import Dict, Any, List
from utils.http_client import HTTPClient


class SecurityScanner:
    """Scanner for security analysis"""
    
    def __init__(self):
        """Initialize security scanner"""
        self.http_client = HTTPClient()
        self.results = {}
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive security scan
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary containing security findings
        """
        print(f"[*] Scanning security for: {url}")
        
        results = {
            'url': url,
            'security_headers': self._check_security_headers(url),
            'ssl_analysis': self._analyze_ssl(url),
            'common_files': self._check_common_files(url),
            'information_disclosure': self._check_information_disclosure(url),
            'port_scan': self._basic_port_scan(url),
            'security_score': 0
        }
        
        # Calculate security score
        results['security_score'] = self._calculate_security_score(results)
        
        self.results = results
        return results
    
    def _check_security_headers(self, url: str) -> Dict[str, Any]:
        """
        Check for security-related HTTP headers
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with header analysis
        """
        try:
            print("  [+] Checking security headers...")
            response = self.http_client.get(url)
            
            if not response:
                return {'error': 'Failed to fetch headers'}
            
            headers = response.headers
            
            security_headers = {
                'Strict-Transport-Security': {
                    'present': 'Strict-Transport-Security' in headers,
                    'value': headers.get('Strict-Transport-Security', None),
                    'recommendation': 'Enable HSTS to enforce HTTPS'
                },
                'X-Frame-Options': {
                    'present': 'X-Frame-Options' in headers,
                    'value': headers.get('X-Frame-Options', None),
                    'recommendation': 'Set to DENY or SAMEORIGIN to prevent clickjacking'
                },
                'X-Content-Type-Options': {
                    'present': 'X-Content-Type-Options' in headers,
                    'value': headers.get('X-Content-Type-Options', None),
                    'recommendation': 'Set to nosniff to prevent MIME-type sniffing'
                },
                'X-XSS-Protection': {
                    'present': 'X-XSS-Protection' in headers,
                    'value': headers.get('X-XSS-Protection', None),
                    'recommendation': 'Enable XSS protection (though CSP is preferred)'
                },
                'Content-Security-Policy': {
                    'present': 'Content-Security-Policy' in headers,
                    'value': headers.get('Content-Security-Policy', None),
                    'recommendation': 'Implement CSP to prevent XSS and injection attacks'
                },
                'Referrer-Policy': {
                    'present': 'Referrer-Policy' in headers,
                    'value': headers.get('Referrer-Policy', None),
                    'recommendation': 'Set referrer policy to control information leakage'
                },
                'Permissions-Policy': {
                    'present': 'Permissions-Policy' in headers,
                    'value': headers.get('Permissions-Policy', None),
                    'recommendation': 'Control browser features and APIs'
                }
            }
            
            return security_headers
        except Exception as e:
            print(f"  [-] Security header check failed: {e}")
            return {'error': str(e)}
    
    def _analyze_ssl(self, url: str) -> Dict[str, Any]:
        """
        Analyze SSL/TLS configuration
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with SSL analysis
        """
        try:
            print("  [+] Analyzing SSL/TLS...")
            
            if not url.startswith('https://'):
                return {
                    'https_enabled': False,
                    'warning': 'Website does not use HTTPS - all traffic is unencrypted',
                    'recommendation': 'Enable HTTPS to encrypt data in transit'
                }
            
            parsed = urlparse(url)
            hostname = parsed.netloc
            
            import ssl
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        'https_enabled': True,
                        'protocol_version': version,
                        'cipher_suite': cipher[0] if cipher else 'Unknown',
                        'key_exchange': cipher[1] if cipher and len(cipher) > 1 else 'Unknown',
                        'encryption_bits': cipher[2] if cipher and len(cipher) > 2 else 'Unknown',
                        'recommendation': self._get_ssl_recommendation(version)
                    }
        except Exception as e:
            print(f"  [-] SSL analysis failed: {e}")
            return {
                'https_enabled': url.startswith('https://'),
                'error': str(e)
            }
    
    def _get_ssl_recommendation(self, version: str) -> str:
        """Get SSL/TLS version recommendation"""
        if version in ['TLSv1.3', 'TLSv1.2']:
            return 'SSL/TLS configuration is good'
        elif version == 'TLSv1.1':
            return 'Consider upgrading to TLS 1.2 or 1.3'
        else:
            return 'CRITICAL: Upgrade SSL/TLS version immediately - current version is insecure'
    
    def _check_common_files(self, url: str) -> Dict[str, bool]:
        """
        Check for common sensitive files
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with file accessibility results
        """
        try:
            print("  [+] Checking for sensitive files...")
            
            base_url = url.rstrip('/')
            common_files = [
                '/robots.txt',
                '/sitemap.xml',
                '/.git/config',
                '/.env',
                '/phpinfo.php',
                '/admin',
                '/wp-admin',
                '/administrator',
                '/backup',
                '/.htaccess',
                '/config.php',
                '/configuration.php',
                '/readme.html',
                '/license.txt'
            ]
            
            results = {}
            for file_path in common_files:
                file_url = base_url + file_path
                response = self.http_client.head(file_url)
                
                if response and response.status_code == 200:
                    results[file_path] = True
                else:
                    results[file_path] = False
            
            return results
        except Exception as e:
            print(f"  [-] Common files check failed: {e}")
            return {}
    
    def _check_information_disclosure(self, url: str) -> Dict[str, Any]:
        """
        Check for information disclosure issues
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with findings
        """
        try:
            print("  [+] Checking for information disclosure...")
            
            response = self.http_client.get(url)
            if not response:
                return {'error': 'Failed to fetch page'}
            
            issues = []
            headers = response.headers
            
            # Check Server header
            if 'Server' in headers:
                server = headers['Server']
                if re.search(r'[\d.]+', server):  # Contains version number
                    issues.append(f"Server version disclosed: {server}")
            
            # Check X-Powered-By
            if 'X-Powered-By' in headers:
                powered_by = headers['X-Powered-By']
                issues.append(f"Technology stack disclosed: {powered_by}")
            
            # Check for error messages in HTML
            html_content = response.text.lower()
            error_patterns = [
                r'sql syntax',
                r'mysql error',
                r'warning:.*line \d+',
                r'fatal error',
                r'undefined index',
                r'stack trace'
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, html_content):
                    issues.append(f"Potential error message exposure detected: {pattern}")
                    break
            
            # Check for directory listing
            if re.search(r'Index of /', html_content):
                issues.append("Directory listing may be enabled")
            
            return {
                'issues_found': len(issues),
                'issues': issues
            }
        except Exception as e:
            print(f"  [-] Information disclosure check failed: {e}")
            return {'error': str(e)}
    
    def _basic_port_scan(self, url: str) -> Dict[str, Any]:
        """
        Perform basic port scan on common ports
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with open ports
        """
        try:
            print("  [+] Performing basic port scan...")
            
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]  # Remove port if present
            
            # Common ports to check
            common_ports = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080, 8443]
            open_ports = []
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((hostname, port))
                
                if result == 0:
                    open_ports.append(port)
                
                sock.close()
            
            return {
                'open_ports': open_ports,
                'total_scanned': len(common_ports)
            }
        except Exception as e:
            print(f"  [-] Port scan failed: {e}")
            return {'error': str(e)}
    
    def _calculate_security_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall security score (0-100)
        
        Args:
            results: Security scan results
            
        Returns:
            Security score
        """
        try:
            score = 100
            
            # Check security headers (-5 points each missing)
            if 'security_headers' in results and isinstance(results['security_headers'], dict):
                for header, info in results['security_headers'].items():
                    if isinstance(info, dict) and not info.get('present', False):
                        score -= 5
            
            # Check SSL (-20 if not enabled)
            if 'ssl_analysis' in results:
                if not results['ssl_analysis'].get('https_enabled', False):
                    score -= 20
            
            # Check information disclosure (-10 if issues found)
            if 'information_disclosure' in results:
                issues = results['information_disclosure'].get('issues_found', 0)
                if issues > 0:
                    score -= min(10, issues * 3)
            
            # Ensure score is between 0 and 100
            return max(0, min(100, score))
        except Exception:
            return 0
