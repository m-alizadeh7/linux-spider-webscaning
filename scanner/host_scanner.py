"""
Host Scanner Module
Scans hosting information including server details, headers, and infrastructure
"""

import socket
from typing import Dict, Any, List, Optional
from utils.http_client import HTTPClient


class HostScanner:
    """Scanner for hosting and infrastructure information"""
    
    def __init__(self):
        """Initialize host scanner"""
        self.http_client = HTTPClient()
        self.results = {}
    
    def scan(self, url: str, domain: str) -> Dict[str, Any]:
        """
        Perform comprehensive host scan
        
        Args:
            url: Target URL
            domain: Domain name
            
        Returns:
            Dictionary containing scan results
        """
        print(f"[*] Scanning hosting information for: {url}")
        
        results = {
            'url': url,
            'domain': domain,
            'http_headers': self._get_http_headers(url),
            'server_info': self._get_server_info(url),
            'ssl_info': self._get_ssl_info(url),
            'response_info': self._get_response_info(url)
        }
        
        self.results = results
        return results
    
    def _get_http_headers(self, url: str) -> Dict[str, str]:
        """
        Get HTTP headers from server
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary of HTTP headers
        """
        try:
            print("  [+] Fetching HTTP headers...")
            response = self.http_client.head(url)
            
            if response:
                return dict(response.headers)
            else:
                # Try GET if HEAD fails
                response = self.http_client.get(url)
                if response:
                    return dict(response.headers)
            
            return {}
        except Exception as e:
            print(f"  [-] Failed to get headers: {e}")
            return {}
    
    def _get_server_info(self, url: str) -> Dict[str, Any]:
        """
        Extract server information from headers
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with server details
        """
        try:
            print("  [+] Analyzing server information...")
            headers = self._get_http_headers(url)
            
            return {
                'server': headers.get('Server', 'Unknown'),
                'powered_by': headers.get('X-Powered-By', 'Unknown'),
                'content_type': headers.get('Content-Type', 'Unknown'),
                'cache_control': headers.get('Cache-Control', 'Not set'),
                'strict_transport_security': headers.get('Strict-Transport-Security', 'Not set'),
                'x_frame_options': headers.get('X-Frame-Options', 'Not set'),
                'x_content_type_options': headers.get('X-Content-Type-Options', 'Not set'),
                'x_xss_protection': headers.get('X-XSS-Protection', 'Not set'),
                'content_security_policy': headers.get('Content-Security-Policy', 'Not set')
            }
        except Exception as e:
            print(f"  [-] Failed to analyze server info: {e}")
            return {
                'server': 'Unknown',
                'powered_by': 'Unknown',
                'error': str(e)
            }
    
    def _get_ssl_info(self, url: str) -> Dict[str, Any]:
        """
        Get SSL/TLS certificate information
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with SSL info
        """
        try:
            if not url.startswith('https://'):
                return {
                    'enabled': False,
                    'message': 'Site does not use HTTPS'
                }
            
            print("  [+] Checking SSL/TLS configuration...")
            
            # Extract hostname
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.netloc
            
            import ssl
            import OpenSSL
            
            # Get certificate
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert = OpenSSL.crypto.load_certificate(
                        OpenSSL.crypto.FILETYPE_ASN1, cert_der
                    )
                    
                    return {
                        'enabled': True,
                        'version': ssock.version(),
                        'cipher': ssock.cipher(),
                        'issuer': dict(cert.get_issuer().get_components()),
                        'subject': dict(cert.get_subject().get_components()),
                        'not_before': cert.get_notBefore().decode('utf-8'),
                        'not_after': cert.get_notAfter().decode('utf-8'),
                        'has_expired': cert.has_expired()
                    }
        except Exception as e:
            print(f"  [-] SSL check failed: {e}")
            return {
                'enabled': url.startswith('https://'),
                'error': str(e)
            }
    
    def _get_response_info(self, url: str) -> Dict[str, Any]:
        """
        Get response information
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with response details
        """
        try:
            print("  [+] Analyzing response characteristics...")
            response = self.http_client.get(url)
            
            if not response:
                return {'error': 'Failed to get response'}
            
            return {
                'status_code': response.status_code,
                'status_text': response.reason,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content),
                'encoding': response.encoding,
                'redirects': len(response.history),
                'final_url': response.url
            }
        except Exception as e:
            print(f"  [-] Response analysis failed: {e}")
            return {'error': str(e)}
