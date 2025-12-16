"""
Helper functions for web scanning
"""

import re
import validators
from urllib.parse import urlparse
from typing import Optional


def normalize_url(url: str) -> Optional[str]:
    """
    Normalize and validate URL
    
    Args:
        url: Input URL string
        
    Returns:
        Normalized URL or None if invalid
    """
    # Add http:// if no scheme present
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Validate URL
    if not validators.url(url):
        return None
    
    return url


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL
    
    Args:
        url: Input URL
        
    Returns:
        Domain name or None if invalid
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return None


def is_wordpress_site(html_content: str) -> bool:
    """
    Check if site is running WordPress based on HTML content
    
    Args:
        html_content: HTML content of the page
        
    Returns:
        True if WordPress detected, False otherwise
    """
    wordpress_indicators = [
        r'wp-content',
        r'wp-includes',
        r'wordpress',
        r'wp-json',
        r'/wp-',
        r'generator.*WordPress'
    ]
    
    for indicator in wordpress_indicators:
        if re.search(indicator, html_content, re.IGNORECASE):
            return True
    
    return False


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.2f} PB"


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + '...'
