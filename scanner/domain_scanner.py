"""
Domain Scanner Module
Scans domain information including registration, expiration dates, and DNS records
Multi-source WHOIS with RDAP, CLI, and python-whois fallback
"""

import whois
import socket
import dns.resolver
import subprocess
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class DomainScanner:
    """Scanner for domain-related information with multi-source WHOIS"""
    
    # RDAP Bootstrap servers for different TLDs
    RDAP_SERVERS = {
        'com': 'https://rdap.verisign.com/com/v1/domain/',
        'net': 'https://rdap.verisign.com/net/v1/domain/',
        'org': 'https://rdap.publicinterestregistry.org/rdap/domain/',
        'io': 'https://rdap.nic.io/domain/',
        'ir': None,  # Iran doesn't have RDAP
        'default': 'https://rdap.org/domain/'
    }
    
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
            'whois': self._get_whois_multi_source(domain),
            'dns': self._get_dns_info(domain),
            'ip_addresses': self._get_ip_addresses(domain),
            'infrastructure': self._get_infrastructure_info(domain)
        }
        
        self.results = results
        return results
    
    def _get_whois_multi_source(self, domain: str) -> Dict[str, Any]:
        """
        Get WHOIS information using multiple sources with confidence level
        
        Sources (in order of priority):
        1. RDAP (most reliable, structured data)
        2. System whois CLI
        3. python-whois library (fallback)
        """
        print("  [+] Fetching WHOIS information (multi-source)...")
        
        whois_data = None
        source = None
        confidence = 0
        
        # Try RDAP first (most reliable)
        rdap_result = self._try_rdap(domain)
        if rdap_result and not rdap_result.get('error'):
            whois_data = rdap_result
            source = 'RDAP'
            confidence = 95
            print(f"    ✓ RDAP lookup successful (confidence: {confidence}%)")
        
        # Try system whois CLI
        if not whois_data or confidence < 80:
            cli_result = self._try_whois_cli(domain)
            if cli_result and not cli_result.get('error'):
                if not whois_data:
                    whois_data = cli_result
                    source = 'CLI'
                    confidence = 85
                else:
                    whois_data = self._merge_whois_data(whois_data, cli_result)
                    confidence = min(98, confidence + 5)
                print(f"    ✓ CLI whois lookup successful (confidence: {confidence}%)")
        
        # Try python-whois as fallback
        if not whois_data or confidence < 70:
            py_result = self._try_python_whois(domain)
            if py_result and not py_result.get('error'):
                if not whois_data:
                    whois_data = py_result
                    source = 'python-whois'
                    confidence = 75
                else:
                    whois_data = self._merge_whois_data(whois_data, py_result)
                    confidence = min(98, confidence + 3)
                print(f"    ✓ python-whois lookup successful (confidence: {confidence}%)")
        
        if not whois_data:
            return {
                'error': 'All WHOIS sources failed',
                'source': None,
                'confidence': 0,
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
        
        whois_data['source'] = source
        whois_data['confidence'] = confidence
        
        return whois_data
    
    def _try_rdap(self, domain: str) -> Optional[Dict[str, Any]]:
        """Try RDAP lookup for domain"""
        try:
            tld = domain.split('.')[-1].lower()
            rdap_url = self.RDAP_SERVERS.get(tld, self.RDAP_SERVERS['default'])
            
            if not rdap_url:
                return None
            
            url = f"{rdap_url}{domain}"
            req = Request(url, headers={'Accept': 'application/rdap+json'})
            
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            return self._parse_rdap_response(data)
            
        except (URLError, HTTPError, json.JSONDecodeError, Exception) as e:
            print(f"    ⚠ RDAP lookup failed: {e}")
            return None
    
    def _parse_rdap_response(self, data: Dict) -> Dict[str, Any]:
        """Parse RDAP JSON response into standard format"""
        result = {
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
        
        # Get registrar
        for entity in data.get('entities', []):
            roles = entity.get('roles', [])
            if 'registrar' in roles:
                vcard = entity.get('vcardArray', [])
                if len(vcard) > 1:
                    for item in vcard[1]:
                        if item[0] == 'fn':
                            result['registrar'] = item[3]
                            break
        
        # Get dates
        for event in data.get('events', []):
            action = event.get('eventAction', '')
            date_str = event.get('eventDate', '')
            
            if date_str:
                try:
                    parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted = parsed_date.strftime('%Y-%m-%d')
                    
                    if action == 'registration':
                        result['creation_date'] = formatted
                    elif action == 'expiration':
                        result['expiration_date'] = formatted
                        result['days_until_expiration'] = (parsed_date.replace(tzinfo=None) - datetime.now()).days
                    elif action == 'last changed':
                        result['updated_date'] = formatted
                except Exception:
                    pass
        
        # Get nameservers
        for ns in data.get('nameservers', []):
            ns_name = ns.get('ldhName', '')
            if ns_name:
                result['name_servers'].append(ns_name)
        
        # Get status
        result['status'] = data.get('status', [])
        
        return result
    
    def _try_whois_cli(self, domain: str) -> Optional[Dict[str, Any]]:
        """Try system whois CLI command"""
        try:
            result = subprocess.run(
                ['whois', domain],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                return None
            
            return self._parse_whois_text(result.stdout)
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"    ⚠ CLI whois failed: {e}")
            return None
    
    def _parse_whois_text(self, text: str) -> Dict[str, Any]:
        """Parse raw WHOIS text output"""
        result = {
            'registrar': 'Unknown',
            'creation_date': 'Unknown',
            'expiration_date': 'Unknown',
            'updated_date': 'Unknown',
            'days_until_expiration': None,
            'name_servers': [],
            'status': [],
            'emails': [],
            'org': 'Unknown',
            'raw_text': text[:2000]
        }
        
        lines = text.split('\n')
        
        patterns = {
            'registrar': [
                r'Registrar:\s*(.+)',
                r'Sponsoring Registrar:\s*(.+)',
                r'registrar:\s*(.+)'
            ],
            'creation_date': [
                r'Creation Date:\s*(.+)',
                r'Created Date:\s*(.+)',
                r'created:\s*(.+)',
                r'Registration Date:\s*(.+)'
            ],
            'expiration_date': [
                r'Registry Expiry Date:\s*(.+)',
                r'Expir(?:y|ation) Date:\s*(.+)',
                r'expires:\s*(.+)',
                r'Expiration Date:\s*(.+)'
            ],
            'updated_date': [
                r'Updated Date:\s*(.+)',
                r'Last Updated:\s*(.+)',
                r'modified:\s*(.+)'
            ],
            'name_server': [
                r'Name Server:\s*(.+)',
                r'nserver:\s*(.+)',
                r'ns\d*:\s*(.+)'
            ],
            'org': [
                r'Registrant Organization:\s*(.+)',
                r'Organisation:\s*(.+)',
                r'org:\s*(.+)'
            ],
            'email': [
                r'Registrant Email:\s*(.+)',
                r'e-mail:\s*(.+)',
                r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
            ],
            'status': [
                r'Domain Status:\s*(.+)',
                r'status:\s*(.+)'
            ]
        }
        
        for line in lines:
            line = line.strip()
            
            for field, field_patterns in patterns.items():
                for pattern in field_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        
                        if field == 'name_server':
                            ns = value.lower().split()[0]
                            if ns not in result['name_servers']:
                                result['name_servers'].append(ns)
                        elif field == 'email':
                            if value not in result['emails'] and '@' in value:
                                result['emails'].append(value)
                        elif field == 'status':
                            status = value.split()[0]
                            if status not in result['status']:
                                result['status'].append(status)
                        elif field in ['creation_date', 'expiration_date', 'updated_date']:
                            if result[field] == 'Unknown':
                                parsed = self._parse_date_string(value)
                                if parsed:
                                    result[field] = parsed.strftime('%Y-%m-%d')
                                    if field == 'expiration_date':
                                        result['days_until_expiration'] = (parsed - datetime.now()).days
                        else:
                            if result.get(field) == 'Unknown':
                                result[field] = value
                        break
        
        return result
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats"""
        date_formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d',
            '%d-%b-%Y',
            '%d.%m.%Y',
            '%Y.%m.%d',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%b %d %Y',
            '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.split()[0], fmt)
            except ValueError:
                continue
        
        return None
    
    def _try_python_whois(self, domain: str) -> Optional[Dict[str, Any]]:
        """Try python-whois library"""
        try:
            w = whois.whois(domain)
            
            creation_date = self._parse_date(w.creation_date)
            expiration_date = self._parse_date(w.expiration_date)
            updated_date = self._parse_date(w.updated_date)
            
            days_until_expiration = None
            if expiration_date:
                days_until_expiration = (expiration_date - datetime.now()).days
            
            return {
                'registrar': w.registrar if hasattr(w, 'registrar') and w.registrar else 'Unknown',
                'creation_date': creation_date.strftime('%Y-%m-%d') if creation_date else 'Unknown',
                'expiration_date': expiration_date.strftime('%Y-%m-%d') if expiration_date else 'Unknown',
                'updated_date': updated_date.strftime('%Y-%m-%d') if updated_date else 'Unknown',
                'days_until_expiration': days_until_expiration,
                'name_servers': list(w.name_servers) if hasattr(w, 'name_servers') and w.name_servers else [],
                'status': list(w.status) if hasattr(w, 'status') and w.status else [],
                'emails': list(w.emails) if hasattr(w, 'emails') and w.emails else [],
                'org': w.org if hasattr(w, 'org') and w.org else 'Unknown'
            }
        except Exception as e:
            print(f"    ⚠ python-whois failed: {e}")
            return None
    
    def _merge_whois_data(self, primary: Dict, secondary: Dict) -> Dict:
        """Merge two WHOIS results, preferring primary but filling gaps"""
        result = primary.copy()
        
        for key, value in secondary.items():
            if key in ['source', 'confidence', 'raw_text', 'error']:
                continue
            
            if result.get(key) in [None, 'Unknown', [], '']:
                result[key] = value
            elif isinstance(value, list) and isinstance(result.get(key), list):
                for item in value:
                    if item not in result[key]:
                        result[key].append(item)
        
        return result
    
    def _get_infrastructure_info(self, domain: str) -> Dict[str, Any]:
        """Get infrastructure information (CDN, WAF, hosting provider)"""
        print("  [+] Detecting infrastructure...")
        
        info = {
            'cdn': None,
            'waf': None,
            'hosting': None,
            'asn': None
        }
        
        try:
            ips = self._get_ip_addresses(domain)
            if ips:
                ip = ips[0]
                info['hosting'] = self._detect_hosting_provider(ip)
                info['asn'] = self._get_asn_info(ip)
            
            # CDN detection via DNS CNAME
            try:
                cname_records = dns.resolver.resolve(domain, 'CNAME')
                for cname in cname_records:
                    cname_str = str(cname).lower()
                    if 'cloudflare' in cname_str:
                        info['cdn'] = 'Cloudflare'
                        info['waf'] = 'Cloudflare WAF'
                    elif 'akamai' in cname_str:
                        info['cdn'] = 'Akamai'
                    elif 'fastly' in cname_str:
                        info['cdn'] = 'Fastly'
                    elif 'cloudfront' in cname_str:
                        info['cdn'] = 'Amazon CloudFront'
                    elif 'azure' in cname_str:
                        info['cdn'] = 'Azure CDN'
            except:
                pass
            
        except Exception as e:
            print(f"    ⚠ Infrastructure detection error: {e}")
        
        return info
    
    def _detect_hosting_provider(self, ip: str) -> str:
        """Detect hosting provider from IP"""
        known_ranges = {
            '104.16.': 'Cloudflare',
            '104.17.': 'Cloudflare',
            '104.18.': 'Cloudflare',
            '104.19.': 'Cloudflare',
            '104.20.': 'Cloudflare',
            '172.67.': 'Cloudflare',
            '34.': 'Google Cloud',
            '35.': 'Google Cloud',
            '52.': 'Amazon AWS',
            '54.': 'Amazon AWS',
            '13.': 'Amazon AWS',
            '157.240.': 'Facebook/Meta',
            '20.': 'Microsoft Azure',
            '40.': 'Microsoft Azure',
            '185.199.': 'GitHub Pages',
            '151.101.': 'Fastly',
            '217.182.': 'OVH',
            '5.9.': 'Hetzner',
            '195.201.': 'Hetzner'
        }
        
        for prefix, provider in known_ranges.items():
            if ip.startswith(prefix):
                return provider
        
        return 'Unknown'
    
    def _get_asn_info(self, ip: str) -> Optional[str]:
        """Get ASN info for IP"""
        try:
            reversed_ip = '.'.join(reversed(ip.split('.')))
            query = f"{reversed_ip}.origin.asn.cymru.com"
            
            answers = dns.resolver.resolve(query, 'TXT')
            for answer in answers:
                return str(answer).strip('"')
        except:
            pass
        
        return None
    
    def _get_dns_info(self, domain: str) -> Dict[str, List[str]]:
        """Get DNS records for domain"""
        print("  [+] Fetching DNS records...")
        dns_info = {
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'CNAME': [],
            'SOA': []
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                for rdata in answers:
                    if record_type == 'MX':
                        dns_info[record_type].append(f"{rdata.preference} {rdata.exchange}")
                    elif record_type == 'SOA':
                        dns_info[record_type].append(f"{rdata.mname} {rdata.rname}")
                    else:
                        dns_info[record_type].append(str(rdata))
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                print(f"  [-] Domain {domain} does not exist")
                break
            except Exception:
                pass
        
        return dns_info
    
    def _get_ip_addresses(self, domain: str) -> List[str]:
        """Get IP addresses for domain"""
        try:
            ip_addresses = []
            
            try:
                ipv4_info = socket.getaddrinfo(domain, None, socket.AF_INET)
                for info in ipv4_info:
                    ip = info[4][0]
                    if ip not in ip_addresses:
                        ip_addresses.append(ip)
            except socket.gaierror:
                pass
            
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
        """Parse date value from WHOIS data"""
        if not date_value:
            return None
        
        if isinstance(date_value, list):
            date_value = date_value[0]
        
        if isinstance(date_value, datetime):
            return date_value
        
        return None
