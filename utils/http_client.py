"""
HTTP Client with random User-Agent support for web scanning
"""

import random
import requests
from typing import Optional, Dict, Any


class HTTPClient:
    """HTTP client with randomized User-Agent headers"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    ]
    
    def __init__(self, timeout: int = 10):
        """
        Initialize HTTP client
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
    
    def _get_random_user_agent(self) -> str:
        """Get a random User-Agent string"""
        return random.choice(self.USER_AGENTS)
    
    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get headers with random User-Agent
        
        Args:
            custom_headers: Additional custom headers
            
        Returns:
            Dictionary of headers
        """
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Perform GET request with random User-Agent
        
        Args:
            url: Target URL
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            Response object or None if failed
        """
        try:
            headers = self._get_headers(kwargs.pop('headers', None))
            kwargs.setdefault('timeout', self.timeout)
            kwargs.setdefault('allow_redirects', True)
            
            response = self.session.get(url, headers=headers, **kwargs)
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Perform POST request with random User-Agent
        
        Args:
            url: Target URL
            **kwargs: Additional arguments for requests.post()
            
        Returns:
            Response object or None if failed
        """
        try:
            headers = self._get_headers(kwargs.pop('headers', None))
            kwargs.setdefault('timeout', self.timeout)
            
            response = self.session.post(url, headers=headers, **kwargs)
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def head(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Perform HEAD request with random User-Agent
        
        Args:
            url: Target URL
            **kwargs: Additional arguments for requests.head()
            
        Returns:
            Response object or None if failed
        """
        try:
            headers = self._get_headers(kwargs.pop('headers', None))
            kwargs.setdefault('timeout', self.timeout)
            
            response = self.session.head(url, headers=headers, **kwargs)
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
