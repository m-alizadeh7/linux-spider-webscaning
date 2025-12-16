"""
Domain Scanner Module
Scans domain information including registration, expiration dates, and DNS records
"""

import whois
import socket
import dns.resolver
from datetime import datetime
from typing import Dict, Any, Optional, List


class DomainScanner:
    """Scanner for domain-related information"""
    
    def __init__(self):
        """Initialize domain scanner"""
        self.results = {}
    
    def scan(self, domain: str) -> Dict[str, Any]:
        """
        Perform comprehensive domain scan
        
        Args:
            domain: Domain name to scan
            
        Returns:
            Dictionary containing scan results
        """
        print(f"[*] Scanning domain information for: {domain}")
        
        results = {
            'domain': domain,
            'whois': self._get_whois_info(domain),
            'dns': self._get_dns_info(domain),
            'ip_addresses': self._get_ip_addresses(domain)
        }
        
        self.results = results
        return results
    
    def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """
        Get WHOIS information for domain
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary with WHOIS data
        """
        try:
            print("  [+] Fetching WHOIS information...")
            w = whois.whois(domain)
            
            # Parse dates
            creation_date = self._parse_date(w.creation_date)
            expiration_date = self._parse_date(w.expiration_date)
            updated_date = self._parse_date(w.updated_date)
            
            # Calculate days until expiration
            days_until_expiration = None
            if expiration_date:
                days_until_expiration = (expiration_date - datetime.now()).days
            
            return {
                'registrar': w.registrar if hasattr(w, 'registrar') else 'Unknown',
                'creation_date': creation_date.strftime('%Y-%m-%d') if creation_date else 'Unknown',
                'expiration_date': expiration_date.strftime('%Y-%m-%d') if expiration_date else 'Unknown',
                'updated_date': updated_date.strftime('%Y-%m-%d') if updated_date else 'Unknown',
                'days_until_expiration': days_until_expiration,
                'name_servers': w.name_servers if hasattr(w, 'name_servers') else [],
                'status': w.status if hasattr(w, 'status') else [],
                'emails': w.emails if hasattr(w, 'emails') else [],
                'org': w.org if hasattr(w, 'org') else 'Unknown'
            }
        except Exception as e:
            print(f"  [-] WHOIS lookup failed: {e}")
            return {
                'error': str(e),
                'registrar': 'Unknown',
                'creation_date': 'Unknown',
                'expiration_date': 'Unknown',
                'updated_date': 'Unknown',
                'days_until_expiration': None,
                'name_servers': [],
                'status': [],
                'emails': [],
                'org': 'Unknown'
            }
    
    def _get_dns_info(self, domain: str) -> Dict[str, List[str]]:
        """
        Get DNS records for domain
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary with DNS records
        """
        print("  [+] Fetching DNS records...")
        dns_info = {
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'CNAME': []
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                for rdata in answers:
                    if record_type == 'MX':
                        dns_info[record_type].append(f"{rdata.preference} {rdata.exchange}")
                    else:
                        dns_info[record_type].append(str(rdata))
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                print(f"  [-] Domain {domain} does not exist")
                break
            except Exception as e:
                print(f"  [-] Error fetching {record_type} records: {e}")
        
        return dns_info
    
    def _get_ip_addresses(self, domain: str) -> List[str]:
        """
        Get IP addresses for domain
        
        Args:
            domain: Domain name
            
        Returns:
            List of IP addresses
        """
        try:
            print("  [+] Resolving IP addresses...")
            ip_addresses = []
            
            # Get IPv4 addresses
            try:
                ipv4_info = socket.getaddrinfo(domain, None, socket.AF_INET)
                for info in ipv4_info:
                    ip = info[4][0]
                    if ip not in ip_addresses:
                        ip_addresses.append(ip)
            except socket.gaierror:
                pass
            
            # Get IPv6 addresses
            try:
                ipv6_info = socket.getaddrinfo(domain, None, socket.AF_INET6)
                for info in ipv6_info:
                    ip = info[4][0]
                    if ip not in ip_addresses:
                        ip_addresses.append(ip)
            except socket.gaierror:
                pass
            
            return ip_addresses
        except Exception as e:
            print(f"  [-] IP resolution failed: {e}")
            return []
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """
        Parse date value from WHOIS data
        
        Args:
            date_value: Date value (can be datetime, list, or string)
            
        Returns:
            Parsed datetime object or None
        """
        if not date_value:
            return None
        
        if isinstance(date_value, list):
            date_value = date_value[0]
        
        if isinstance(date_value, datetime):
            return date_value
        
        return None
