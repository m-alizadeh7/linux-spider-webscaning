"""
Security Scanner Module
Performs security analysis including headers, SSL, common vulnerabilities
With severity levels and actionable recommendations
"""

import re
import socket
import ssl
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional
from utils.http_client import HTTPClient


class SecurityScanner:
    """Scanner for security analysis with severity classification"""
    
    # Severity levels
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    INFO = 'info'
    
    def __init__(self):
        """Initialize security scanner"""
        self.http_client = HTTPClient()
        self.results = {}
        self.findings = []
    
    def scan(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive security scan
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary containing security findings
        """
        print(f"[*] Scanning security for: {url}")
        
        self.findings = []
        
        results = {
            'url': url,
            'security_headers': self._check_security_headers(url),
            'ssl_analysis': self._analyze_ssl(url),
            'common_files': self._check_common_files(url),
            'sensitive_paths': self._check_sensitive_paths(url),
            'information_disclosure': self._check_information_disclosure(url),
            'port_scan': self._basic_port_scan(url),
            'findings_summary': {},
            'security_score': 0,
            'recommendations': []
        }
        
        # Summarize findings by severity
        results['findings_summary'] = self._summarize_findings()
        
        # Calculate security score
        results['security_score'] = self._calculate_security_score(results)
        
        # Generate prioritized recommendations
        results['recommendations'] = self._generate_recommendations()
        
        self.results = results
        return results
    
    def _add_finding(self, severity: str, category: str, title: str, 
                     description: str, recommendation: str, evidence: str = None):
        """Add a security finding"""
        self.findings.append({
            'severity': severity,
            'category': category,
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'evidence': evidence
        })
    
    def _check_security_headers(self, url: str) -> Dict[str, Any]:
        """Check for security-related HTTP headers"""
        try:
            print("  [+] Checking security headers...")
            response = self.http_client.get(url)
            
            if not response:
                return {'error': 'Failed to fetch headers'}
            
            headers = response.headers
            
            security_headers = {
                'Strict-Transport-Security': {
                    'present': False,
                    'value': None,
                    'severity': self.HIGH,
                    'description': 'HSTS forces HTTPS connections',
                    'recommendation': 'Add header: Strict-Transport-Security: max-age=31536000; includeSubDomains'
                },
                'X-Frame-Options': {
                    'present': False,
                    'value': None,
                    'severity': self.MEDIUM,
                    'description': 'Prevents clickjacking attacks',
                    'recommendation': 'Add header: X-Frame-Options: DENY or SAMEORIGIN'
                },
                'X-Content-Type-Options': {
                    'present': False,
                    'value': None,
                    'severity': self.MEDIUM,
                    'description': 'Prevents MIME-type sniffing',
                    'recommendation': 'Add header: X-Content-Type-Options: nosniff'
                },
                'Content-Security-Policy': {
                    'present': False,
                    'value': None,
                    'severity': self.HIGH,
                    'description': 'Prevents XSS and injection attacks',
                    'recommendation': "Add CSP header with appropriate directives for your site"
                },
                'Referrer-Policy': {
                    'present': False,
                    'value': None,
                    'severity': self.LOW,
                    'description': 'Controls referrer information leakage',
                    'recommendation': 'Add header: Referrer-Policy: strict-origin-when-cross-origin'
                },
                'Permissions-Policy': {
                    'present': False,
                    'value': None,
                    'severity': self.LOW,
                    'description': 'Controls browser features and APIs',
                    'recommendation': 'Add Permissions-Policy to restrict unnecessary features'
                },
                'X-XSS-Protection': {
                    'present': False,
                    'value': None,
                    'severity': self.LOW,
                    'description': 'Legacy XSS protection (CSP is preferred)',
                    'recommendation': 'Add header: X-XSS-Protection: 1; mode=block'
                }
            }
            
            # Check each header
            for header_name, info in security_headers.items():
                if header_name in headers:
                    info['present'] = True
                    info['value'] = headers[header_name]
                else:
                    # Add as finding
                    self._add_finding(
                        severity=info['severity'],
                        category='Security Headers',
                        title=f'Missing {header_name} Header',
                        description=info['description'],
                        recommendation=info['recommendation']
                    )
            
            # Check for headers that shouldn't be present
            if 'Server' in headers and re.search(r'[\d.]+', headers['Server']):
                self._add_finding(
                    severity=self.LOW,
                    category='Information Disclosure',
                    title='Server Version Exposed',
                    description='Server header reveals version information',
                    recommendation='Remove or obfuscate Server header version',
                    evidence=headers['Server']
                )
            
            if 'X-Powered-By' in headers:
                self._add_finding(
                    severity=self.LOW,
                    category='Information Disclosure',
                    title='Technology Stack Exposed',
                    description='X-Powered-By header reveals technology stack',
                    recommendation='Remove X-Powered-By header',
                    evidence=headers['X-Powered-By']
                )
            
            return security_headers
        except Exception as e:
            print(f"  [-] Security header check failed: {e}")
            return {'error': str(e)}
    
    def _analyze_ssl(self, url: str) -> Dict[str, Any]:
        """Analyze SSL/TLS configuration"""
        try:
            print("  [+] Analyzing SSL/TLS...")
            
            if not url.startswith('https://'):
                self._add_finding(
                    severity=self.CRITICAL,
                    category='SSL/TLS',
                    title='HTTPS Not Enabled',
                    description='Website does not use HTTPS - all traffic is unencrypted',
                    recommendation='Enable HTTPS with a valid SSL certificate (e.g., Let\'s Encrypt)'
                )
                return {
                    'https_enabled': False,
                    'grade': 'F',
                    'issues': ['HTTPS not enabled']
                }
            
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            
            result = {
                'https_enabled': True,
                'protocol_version': None,
                'cipher_suite': None,
                'certificate': {},
                'grade': 'A',
                'issues': []
            }
            
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()
                    version = ssock.version()
                    cert = ssock.getpeercert()
                    
                    result['protocol_version'] = version
                    result['cipher_suite'] = cipher[0] if cipher else 'Unknown'
                    result['encryption_bits'] = cipher[2] if cipher and len(cipher) > 2 else None
                    
                    # Certificate info
                    if cert:
                        result['certificate'] = {
                            'subject': dict(x[0] for x in cert.get('subject', [])),
                            'issuer': dict(x[0] for x in cert.get('issuer', [])),
                            'expires': cert.get('notAfter'),
                            'san': [x[1] for x in cert.get('subjectAltName', [])]
                        }
                    
                    # Check TLS version
                    if version in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.0']:
                        self._add_finding(
                            severity=self.CRITICAL,
                            category='SSL/TLS',
                            title='Outdated TLS Version',
                            description=f'Server supports {version} which is insecure',
                            recommendation='Upgrade to TLS 1.2 or 1.3 minimum'
                        )
                        result['grade'] = 'F'
                        result['issues'].append(f'Outdated {version}')
                    elif version == 'TLSv1.1':
                        self._add_finding(
                            severity=self.HIGH,
                            category='SSL/TLS',
                            title='TLS 1.1 Detected',
                            description='TLS 1.1 is deprecated',
                            recommendation='Upgrade to TLS 1.2 or 1.3'
                        )
                        result['grade'] = 'C'
                        result['issues'].append('TLS 1.1 deprecated')
                    elif version == 'TLSv1.2':
                        result['grade'] = 'B+'
                    elif version == 'TLSv1.3':
                        result['grade'] = 'A'
                    
                    # Check cipher strength
                    if cipher and cipher[2] < 128:
                        self._add_finding(
                            severity=self.HIGH,
                            category='SSL/TLS',
                            title='Weak Cipher',
                            description=f'Cipher uses only {cipher[2]} bits encryption',
                            recommendation='Use 128-bit or higher encryption'
                        )
                        result['issues'].append('Weak cipher')
            
            return result
            
        except ssl.SSLCertVerificationError as e:
            self._add_finding(
                severity=self.CRITICAL,
                category='SSL/TLS',
                title='Invalid SSL Certificate',
                description='SSL certificate verification failed',
                recommendation='Install a valid SSL certificate from a trusted CA',
                evidence=str(e)
            )
            return {'https_enabled': True, 'error': str(e), 'grade': 'F'}
        except Exception as e:
            print(f"  [-] SSL analysis failed: {e}")
            return {'https_enabled': url.startswith('https://'), 'error': str(e)}
    
    def _check_common_files(self, url: str) -> Dict[str, Any]:
        """Check for common sensitive files"""
        try:
            print("  [+] Checking for sensitive files...")
            
            base_url = url.rstrip('/')
            
            sensitive_files = {
                '/.git/config': {'severity': self.CRITICAL, 'desc': 'Git repository exposed'},
                '/.env': {'severity': self.CRITICAL, 'desc': 'Environment file exposed'},
                '/.htaccess': {'severity': self.HIGH, 'desc': 'Apache config exposed'},
                '/.htpasswd': {'severity': self.CRITICAL, 'desc': 'Password file exposed'},
                '/config.php': {'severity': self.CRITICAL, 'desc': 'PHP config exposed'},
                '/wp-config.php': {'severity': self.CRITICAL, 'desc': 'WordPress config exposed'},
                '/phpinfo.php': {'severity': self.HIGH, 'desc': 'PHP info exposed'},
                '/server-status': {'severity': self.MEDIUM, 'desc': 'Apache status exposed'},
                '/backup.sql': {'severity': self.CRITICAL, 'desc': 'Database backup exposed'},
                '/backup.zip': {'severity': self.CRITICAL, 'desc': 'Backup archive exposed'},
                '/debug.log': {'severity': self.HIGH, 'desc': 'Debug log exposed'},
                '/error.log': {'severity': self.MEDIUM, 'desc': 'Error log exposed'},
                '/.DS_Store': {'severity': self.LOW, 'desc': 'macOS metadata exposed'},
                '/crossdomain.xml': {'severity': self.LOW, 'desc': 'Flash policy file'},
                '/clientaccesspolicy.xml': {'severity': self.LOW, 'desc': 'Silverlight policy file'}
            }
            
            results = {'accessible': [], 'checked': len(sensitive_files)}
            
            for path, info in sensitive_files.items():
                try:
                    file_url = base_url + path
                    response = self.http_client.head(file_url)
                    
                    if response and response.status_code == 200:
                        results['accessible'].append(path)
                        self._add_finding(
                            severity=info['severity'],
                            category='Sensitive Files',
                            title=f'Sensitive File Accessible: {path}',
                            description=info['desc'],
                            recommendation=f'Block access to {path} or remove the file',
                            evidence=file_url
                        )
                except:
                    pass
            
            return results
        except Exception as e:
            print(f"  [-] Sensitive files check failed: {e}")
            return {'error': str(e)}
    
    def _check_sensitive_paths(self, url: str) -> Dict[str, Any]:
        """Check for sensitive admin/login paths"""
        try:
            print("  [+] Checking for sensitive paths...")
            
            base_url = url.rstrip('/')
            
            admin_paths = [
                '/admin', '/administrator', '/wp-admin', '/wp-login.php',
                '/login', '/signin', '/auth', '/panel',
                '/cpanel', '/phpmyadmin', '/pma', '/adminer',
                '/manager', '/backend', '/dashboard'
            ]
            
            results = {'found': [], 'checked': len(admin_paths)}
            
            for path in admin_paths:
                try:
                    test_url = base_url + path
                    response = self.http_client.get(test_url, allow_redirects=False)
                    
                    if response and response.status_code in [200, 301, 302, 401, 403]:
                        results['found'].append({
                            'path': path,
                            'status': response.status_code
                        })
                        
                        if response.status_code == 200:
                            self._add_finding(
                                severity=self.MEDIUM,
                                category='Admin Paths',
                                title=f'Admin Panel Found: {path}',
                                description='Admin panel is accessible',
                                recommendation='Ensure strong authentication and consider IP restriction'
                            )
                except:
                    pass
            
            return results
        except Exception as e:
            print(f"  [-] Sensitive paths check failed: {e}")
            return {'error': str(e)}
    
    def _check_information_disclosure(self, url: str) -> Dict[str, Any]:
        """Check for information disclosure issues"""
        try:
            print("  [+] Checking for information disclosure...")
            
            response = self.http_client.get(url)
            if not response:
                return {'error': 'Failed to fetch page'}
            
            issues = []
            html_content = response.text.lower() if response.text else ''
            
            # Error patterns
            error_patterns = [
                (r'sql syntax', self.HIGH, 'SQL error message exposed'),
                (r'mysql error', self.HIGH, 'MySQL error exposed'),
                (r'warning:.*line \d+', self.MEDIUM, 'PHP warning exposed'),
                (r'fatal error', self.HIGH, 'PHP fatal error exposed'),
                (r'undefined index', self.MEDIUM, 'PHP undefined index error'),
                (r'stack trace', self.HIGH, 'Stack trace exposed'),
                (r'exception.*at line', self.HIGH, 'Exception details exposed'),
                (r'debug mode.*enabled', self.MEDIUM, 'Debug mode enabled')
            ]
            
            for pattern, severity, desc in error_patterns:
                if re.search(pattern, html_content):
                    issues.append(desc)
                    self._add_finding(
                        severity=severity,
                        category='Information Disclosure',
                        title=desc,
                        description='Error message could reveal sensitive information',
                        recommendation='Disable debug mode and configure proper error handling'
                    )
            
            # Directory listing
            if re.search(r'Index of /', html_content) or re.search(r'<title>Index of', html_content):
                issues.append('Directory listing enabled')
                self._add_finding(
                    severity=self.MEDIUM,
                    category='Information Disclosure',
                    title='Directory Listing Enabled',
                    description='Server allows directory browsing',
                    recommendation='Disable directory listing in web server config'
                )
            
            return {
                'issues_found': len(issues),
                'issues': issues
            }
        except Exception as e:
            print(f"  [-] Information disclosure check failed: {e}")
            return {'error': str(e)}
    
    def _basic_port_scan(self, url: str) -> Dict[str, Any]:
        """Perform basic port scan on common ports"""
        try:
            print("  [+] Performing basic port scan...")
            
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            
            # Port info with risk assessment
            port_info = {
                21: ('FTP', self.MEDIUM, 'FTP is unencrypted'),
                22: ('SSH', self.INFO, 'SSH access'),
                23: ('Telnet', self.HIGH, 'Telnet is unencrypted'),
                25: ('SMTP', self.LOW, 'Mail server'),
                80: ('HTTP', self.INFO, 'Web server'),
                443: ('HTTPS', self.INFO, 'Secure web server'),
                3306: ('MySQL', self.CRITICAL, 'Database directly accessible'),
                3389: ('RDP', self.HIGH, 'Remote desktop exposed'),
                5432: ('PostgreSQL', self.CRITICAL, 'Database directly accessible'),
                8080: ('HTTP-Alt', self.LOW, 'Alternative web server'),
                8443: ('HTTPS-Alt', self.LOW, 'Alternative secure web server'),
                27017: ('MongoDB', self.CRITICAL, 'Database directly accessible'),
                6379: ('Redis', self.CRITICAL, 'Cache/DB directly accessible')
            }
            
            open_ports = []
            risky_ports = []
            
            for port, (service, severity, desc) in port_info.items():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((hostname, port))
                    
                    if result == 0:
                        open_ports.append({'port': port, 'service': service})
                        
                        if severity in [self.HIGH, self.CRITICAL]:
                            risky_ports.append(port)
                            self._add_finding(
                                severity=severity,
                                category='Network',
                                title=f'Risky Port Open: {port} ({service})',
                                description=desc,
                                recommendation=f'Close port {port} or restrict access with firewall'
                            )
                    
                    sock.close()
                except:
                    pass
            
            return {
                'open_ports': open_ports,
                'risky_ports': risky_ports,
                'total_scanned': len(port_info)
            }
        except Exception as e:
            print(f"  [-] Port scan failed: {e}")
            return {'error': str(e)}
    
    def _summarize_findings(self) -> Dict[str, int]:
        """Summarize findings by severity"""
        summary = {
            self.CRITICAL: 0,
            self.HIGH: 0,
            self.MEDIUM: 0,
            self.LOW: 0,
            self.INFO: 0
        }
        
        for finding in self.findings:
            severity = finding.get('severity', self.INFO)
            summary[severity] = summary.get(severity, 0) + 1
        
        return summary
    
    def _calculate_security_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall security score (0-100)"""
        try:
            score = 100
            
            # Deduct based on severity
            summary = results.get('findings_summary', {})
            score -= summary.get(self.CRITICAL, 0) * 25
            score -= summary.get(self.HIGH, 0) * 15
            score -= summary.get(self.MEDIUM, 0) * 8
            score -= summary.get(self.LOW, 0) * 3
            
            return max(0, min(100, score))
        except Exception:
            return 0
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        # Sort findings by severity priority
        severity_order = {
            self.CRITICAL: 0,
            self.HIGH: 1,
            self.MEDIUM: 2,
            self.LOW: 3,
            self.INFO: 4
        }
        
        sorted_findings = sorted(
            self.findings,
            key=lambda x: severity_order.get(x['severity'], 5)
        )
        
        recommendations = []
        for i, finding in enumerate(sorted_findings[:10], 1):  # Top 10 recommendations
            recommendations.append({
                'priority': i,
                'severity': finding['severity'],
                'title': finding['title'],
                'action': finding['recommendation']
            })
        
        return recommendations
    
    def get_grade(self) -> str:
        """Get security grade based on score"""
        score = self.results.get('security_score', 0)
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
