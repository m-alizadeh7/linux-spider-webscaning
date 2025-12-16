"""
Report Generator Module
Generates comprehensive scan reports in Markdown format
"""

import os
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    """Generate comprehensive scan reports"""
    
    def __init__(self, output_dir: str = 'reports'):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_report(self, scan_results: Dict[str, Any], url: str, domain: str) -> str:
        """
        Generate comprehensive scan report
        
        Args:
            scan_results: Dictionary containing all scan results
            url: Target URL
            domain: Domain name
            
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scan_{domain}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        print(f"\n[*] Generating report: {filename}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(self._generate_header(url, domain, timestamp))
            
            # Domain Information
            if 'domain' in scan_results:
                f.write(self._generate_domain_section(scan_results['domain']))
            
            # Hosting Information
            if 'host' in scan_results:
                f.write(self._generate_host_section(scan_results['host']))
            
            # Technology Detection
            if 'technology' in scan_results:
                f.write(self._generate_technology_section(scan_results['technology']))
            
            # CMS Analysis
            if 'cms' in scan_results:
                f.write(self._generate_cms_section(scan_results['cms']))
            
            # Security Analysis
            if 'security' in scan_results:
                f.write(self._generate_security_section(scan_results['security']))
            
            # SEO Analysis
            if 'seo' in scan_results:
                f.write(self._generate_seo_section(scan_results['seo']))
            
            # Summary and Recommendations
            f.write(self._generate_summary(scan_results))
            
            # Footer
            f.write(self._generate_footer())
        
        print(f"[+] Report saved: {filepath}")
        return filepath
    
    def _generate_header(self, url: str, domain: str, timestamp: str) -> str:
        """Generate report header"""
        date_formatted = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""# Website Scan Report

## Scan Information

- **Target URL:** {url}
- **Domain:** {domain}
- **Scan Date:** {date_formatted}
- **Scanner:** Linux Spider Web Scanner v1.0

---

"""
    
    def _generate_domain_section(self, domain_data: Dict[str, Any]) -> str:
        """Generate domain information section"""
        whois = domain_data.get('whois', {})
        dns = domain_data.get('dns', {})
        ips = domain_data.get('ip_addresses', [])
        
        section = """## 1. Domain Information

### WHOIS Information

"""
        
        section += f"- **Registrar:** {whois.get('registrar', 'Unknown')}\n"
        section += f"- **Organization:** {whois.get('org', 'Unknown')}\n"
        section += f"- **Creation Date:** {whois.get('creation_date', 'Unknown')}\n"
        section += f"- **Expiration Date:** {whois.get('expiration_date', 'Unknown')}\n"
        section += f"- **Updated Date:** {whois.get('updated_date', 'Unknown')}\n"
        
        if whois.get('days_until_expiration'):
            section += f"- **Days Until Expiration:** {whois['days_until_expiration']} days\n"
        
        section += "\n### DNS Records\n\n"
        
        for record_type, records in dns.items():
            if records:
                section += f"**{record_type} Records:**\n"
                for record in records:
                    section += f"- {record}\n"
                section += "\n"
        
        section += "### IP Addresses\n\n"
        if ips:
            for ip in ips:
                section += f"- {ip}\n"
        else:
            section += "- No IP addresses resolved\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_host_section(self, host_data: Dict[str, Any]) -> str:
        """Generate hosting information section"""
        server_info = host_data.get('server_info', {})
        ssl_info = host_data.get('ssl_info', {})
        response_info = host_data.get('response_info', {})
        
        section = """## 2. Hosting & Infrastructure

### Server Information

"""
        
        section += f"- **Server:** {server_info.get('server', 'Unknown')}\n"
        section += f"- **Powered By:** {server_info.get('powered_by', 'Unknown')}\n"
        section += f"- **Content Type:** {server_info.get('content_type', 'Unknown')}\n"
        
        section += "\n### SSL/TLS Configuration\n\n"
        
        if ssl_info.get('enabled'):
            section += f"- **HTTPS:** ✓ Enabled\n"
            if 'version' in ssl_info:
                section += f"- **Protocol Version:** {ssl_info['version']}\n"
            if 'cipher' in ssl_info:
                section += f"- **Cipher Suite:** {ssl_info['cipher']}\n"
        else:
            section += "- **HTTPS:** ✗ Not enabled\n"
            section += "- **Warning:** Site does not use HTTPS encryption\n"
        
        section += "\n### Security Headers\n\n"
        
        security_headers = {
            'Strict-Transport-Security': server_info.get('strict_transport_security', 'Not set'),
            'X-Frame-Options': server_info.get('x_frame_options', 'Not set'),
            'X-Content-Type-Options': server_info.get('x_content_type_options', 'Not set'),
            'Content-Security-Policy': server_info.get('content_security_policy', 'Not set')
        }
        
        for header, value in security_headers.items():
            status = "✓" if value != 'Not set' else "✗"
            section += f"- **{header}:** {status} {value}\n"
        
        section += "\n### Response Metrics\n\n"
        
        if response_info:
            section += f"- **Status Code:** {response_info.get('status_code', 'Unknown')}\n"
            section += f"- **Response Time:** {response_info.get('response_time', 0):.2f} seconds\n"
            section += f"- **Content Length:** {response_info.get('content_length', 0):,} bytes\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_technology_section(self, tech_data: Dict[str, Any]) -> str:
        """Generate technology detection section"""
        manual = tech_data.get('manual_detection', {})
        js_libs = tech_data.get('javascript_libraries', [])
        generators = tech_data.get('meta_generators', [])
        
        section = """## 3. Technology Stack

### Detected Technologies

"""
        
        # CMS
        if manual.get('cms'):
            section += "**Content Management System:**\n"
            for cms in manual['cms']:
                section += f"- {cms}\n"
            section += "\n"
        
        # Frameworks
        if manual.get('frameworks'):
            section += "**Frameworks & Libraries:**\n"
            for framework in manual['frameworks']:
                section += f"- {framework}\n"
            section += "\n"
        
        # JavaScript Libraries
        if js_libs:
            section += "**JavaScript Libraries:**\n"
            for lib in js_libs:
                section += f"- {lib}\n"
            section += "\n"
        
        # Web Server
        if manual.get('web_servers'):
            section += "**Web Server:**\n"
            for server in manual['web_servers']:
                section += f"- {server}\n"
            section += "\n"
        
        # Analytics
        if manual.get('analytics'):
            section += "**Analytics & Tracking:**\n"
            for tool in manual['analytics']:
                section += f"- {tool}\n"
            section += "\n"
        
        # CDN
        if manual.get('cdn'):
            section += "**Content Delivery Network:**\n"
            for cdn in manual['cdn']:
                section += f"- {cdn}\n"
            section += "\n"
        
        # Meta Generators
        if generators:
            section += "**Meta Generators:**\n"
            for gen in generators:
                section += f"- {gen}\n"
            section += "\n"
        
        section += "---\n\n"
        return section
    
    def _generate_cms_section(self, cms_data: Dict[str, Any]) -> str:
        """Generate CMS analysis section"""
        cms_type = cms_data.get('cms_detected', 'Unknown')
        
        section = f"""## 4. CMS Analysis

### Detected CMS: {cms_type}

"""
        
        if cms_type == 'WordPress' and cms_data.get('wordpress'):
            wp = cms_data['wordpress']
            
            # Handle version - can be string or dict
            version_info = wp.get('version', 'Unknown')
            if isinstance(version_info, dict):
                version_str = version_info.get('version', 'Unknown')
                section += f"**WordPress Version:** {version_str}\n"
                if version_info.get('security_note'):
                    section += f"- ⚠️ {version_info['security_note']}\n"
            else:
                section += f"**WordPress Version:** {version_info}\n"
            section += "\n"
            
            theme = wp.get('theme', {})
            if theme:
                section += f"**Active Theme:** {theme.get('name', 'Unknown')}\n"
                if theme.get('path'):
                    section += f"- Path: {theme['path']}\n"
                section += "\n"
            
            # Handle plugins - can be list or dict with 'detected' key
            plugins_data = wp.get('plugins', [])
            if isinstance(plugins_data, dict):
                plugins = plugins_data.get('detected', [])
            else:
                plugins = plugins_data if isinstance(plugins_data, list) else []
            
            if plugins:
                section += f"**Detected Plugins:** ({len(plugins)})\n"
                for plugin in plugins[:20]:  # Limit to first 20
                    if isinstance(plugin, dict):
                        plugin_name = plugin.get('name', str(plugin))
                        plugin_cat = plugin.get('category', '')
                        if plugin_cat:
                            section += f"- {plugin_name} ({plugin_cat})\n"
                        else:
                            section += f"- {plugin_name}\n"
                    else:
                        section += f"- {plugin}\n"
                if len(plugins) > 20:
                    section += f"- ... and {len(plugins) - 20} more\n"
                section += "\n"
            
            # Handle API - can be bool or dict
            api_info = wp.get('api', wp.get('api_exposed'))
            if isinstance(api_info, dict):
                api_exposed = api_info.get('enabled', False)
            else:
                api_exposed = bool(api_info)
            section += f"**REST API Exposed:** {'Yes' if api_exposed else 'No'}\n\n"
            
            # SEO config
            seo_config = wp.get('seo_config', {})
            if seo_config.get('has_seo_plugin'):
                section += f"**SEO Plugin:** {seo_config.get('seo_plugin_name', 'Detected')}\n\n"
        
        elif cms_type == 'Joomla' and cms_data.get('joomla'):
            joomla = cms_data['joomla']
            
            components = joomla.get('components', [])
            if components:
                section += f"**Detected Components:** ({len(components)})\n"
                for comp in components[:15]:
                    section += f"- {comp}\n"
                section += "\n"
        
        elif cms_type == 'Drupal' and cms_data.get('drupal'):
            drupal = cms_data['drupal']
            section += f"**Drupal Version:** {drupal.get('version', 'Unknown')}\n\n"
            
            modules = drupal.get('modules', [])
            if modules:
                section += f"**Detected Modules:** ({len(modules)})\n"
                for mod in modules[:15]:
                    section += f"- {mod}\n"
                section += "\n"
        
        elif cms_type == 'Unknown':
            section += "No specific CMS detected or custom-built website.\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_security_section(self, security_data: Dict[str, Any]) -> str:
        """Generate security analysis section"""
        score = security_data.get('security_score', 0)
        headers = security_data.get('security_headers', {})
        ssl = security_data.get('ssl_analysis', {})
        common_files = security_data.get('common_files', {})
        info_disclosure = security_data.get('information_disclosure', {})
        ports = security_data.get('port_scan', {})
        
        # Determine security level
        if score >= 80:
            level = "🟢 Good"
        elif score >= 60:
            level = "🟡 Fair"
        else:
            level = "🔴 Needs Improvement"
        
        section = f"""## 5. Security Analysis

### Security Score: {score}/100 - {level}

### Security Headers Status

"""
        
        for header, info in headers.items():
            if isinstance(info, dict):
                status = "✓" if info.get('present') else "✗"
                section += f"**{header}:** {status}\n"
                if not info.get('present') and info.get('recommendation'):
                    section += f"- *Recommendation: {info['recommendation']}*\n"
                section += "\n"
        
        section += "### SSL/TLS Analysis\n\n"
        
        if ssl.get('https_enabled'):
            section += "- **HTTPS:** ✓ Enabled\n"
            if 'protocol_version' in ssl:
                section += f"- **Protocol:** {ssl['protocol_version']}\n"
        else:
            section += "- **HTTPS:** ✗ Not enabled\n"
            section += "- **WARNING:** Site does not use HTTPS encryption\n"
        
        section += "\n### Common Files Check\n\n"
        
        # Handle new format: {'accessible': [...], 'checked': N}
        if isinstance(common_files, dict) and 'accessible' in common_files:
            exposed_files = common_files.get('accessible', [])
        else:
            # Legacy format: {file: bool, ...}
            exposed_files = [f for f, accessible in common_files.items() if accessible]
        
        if exposed_files:
            section += "**Exposed Files:**\n"
            for file in exposed_files:
                section += f"- ⚠️ {file}\n"
        else:
            section += "- No sensitive files publicly accessible\n"
        
        section += "\n### Information Disclosure\n\n"
        
        issues = info_disclosure.get('issues', [])
        if issues:
            section += "**Potential Issues Found:**\n"
            for issue in issues:
                section += f"- ⚠️ {issue}\n"
        else:
            section += "- No obvious information disclosure issues detected\n"
        
        section += "\n### Open Ports\n\n"
        
        open_ports = ports.get('open_ports', [])
        if open_ports:
            section += f"**Open Ports Detected:** {', '.join(map(str, open_ports))}\n"
        else:
            section += "- Standard ports only\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_seo_section(self, seo_data: Dict[str, Any]) -> str:
        """Generate SEO analysis section"""
        score = seo_data.get('seo_score', 0)
        meta = seo_data.get('meta_tags', {})
        headings = seo_data.get('headings', {})
        content = seo_data.get('content_analysis', {})
        links = seo_data.get('links', {})
        images = seo_data.get('images', {})
        mobile = seo_data.get('mobile_friendly', {})
        performance = seo_data.get('performance', {})
        
        # Determine SEO level
        if score >= 80:
            level = "🟢 Excellent"
        elif score >= 60:
            level = "🟡 Good"
        elif score >= 40:
            level = "🟠 Fair"
        else:
            level = "🔴 Needs Work"
        
        section = f"""## 6. SEO Analysis

### SEO Score: {score}/100 - {level}

### Meta Tags

"""
        
        # Title
        title_info = meta.get('title', {})
        title_status = "✓" if title_info.get('optimal') else "✗"
        section += f"**Title Tag:** {title_status}\n"
        section += f"- Content: {title_info.get('content', 'Not set')}\n"
        section += f"- Length: {title_info.get('length', 0)} characters\n"
        if title_info.get('recommendation'):
            section += f"- *{title_info['recommendation']}*\n"
        section += "\n"
        
        # Description
        desc_info = meta.get('description', {})
        desc_status = "✓" if desc_info.get('optimal') else "✗"
        section += f"**Meta Description:** {desc_status}\n"
        section += f"- Length: {desc_info.get('length', 0)} characters\n"
        if desc_info.get('recommendation'):
            section += f"- *{desc_info['recommendation']}*\n"
        section += "\n"
        
        # Other meta
        section += f"**Canonical URL:** {'✓ Set' if meta.get('canonical') else '✗ Not set'}\n"
        section += f"**Open Graph Tags:** {'✓ Present' if meta.get('open_graph') else '✗ Not set'}\n"
        section += f"**Twitter Cards:** {'✓ Present' if meta.get('twitter_cards') else '✗ Not set'}\n\n"
        
        section += "### Content Analysis\n\n"
        
        section += f"- **Word Count:** {content.get('word_count', 0)}\n"
        section += f"- **Text to HTML Ratio:** {content.get('text_to_html_ratio', 0)}%\n"
        section += f"- **Language Tag:** {content.get('language', 'Not set')}\n"
        
        if content.get('recommendations'):
            section += "\n**Recommendations:**\n"
            for rec in content['recommendations']:
                section += f"- {rec}\n"
        
        section += "\n### Heading Structure\n\n"
        
        section += f"- **H1 Tags:** {headings.get('h1_count', 0)} "
        section += f"({'✓ Optimal' if headings.get('h1_optimal') else '✗ Should have exactly one'})\n"
        section += f"- **Total Headings:** {headings.get('total_headings', 0)}\n\n"
        
        section += "### Links\n\n"
        
        section += f"- **Total Links:** {links.get('total_links', 0)}\n"
        section += f"- **Internal Links:** {links.get('internal_links', 0)}\n"
        section += f"- **External Links:** {links.get('external_links', 0)}\n\n"
        
        section += "### Images\n\n"
        
        section += f"- **Total Images:** {images.get('total_images', 0)}\n"
        section += f"- **Images with Alt Tags:** {images.get('images_with_alt', 0)}\n"
        section += f"- **Alt Tag Coverage:** {images.get('alt_tag_percentage', 0)}%\n\n"
        
        section += "### Mobile Friendliness\n\n"
        
        viewport_status = "✓" if mobile.get('has_viewport_meta') else "✗"
        section += f"- **Viewport Meta Tag:** {viewport_status}\n"
        section += f"- **Media Queries Detected:** {'Yes' if mobile.get('has_media_queries') else 'No'}\n\n"
        
        section += "### Performance\n\n"
        
        section += f"- **Page Load Time:** {performance.get('load_time', 0)} seconds\n"
        section += f"- **Page Size:** {performance.get('page_size_readable', 'Unknown')}\n"
        
        if performance.get('recommendations'):
            section += "\n**Performance Recommendations:**\n"
            for rec in performance['recommendations']:
                section += f"- {rec}\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_summary(self, scan_results: Dict[str, Any]) -> str:
        """Generate summary and recommendations"""
        section = """## 7. Summary & Recommendations

### Overall Assessment

"""
        
        # Collect scores
        security_score = scan_results.get('security', {}).get('security_score', 0)
        seo_score = scan_results.get('seo', {}).get('seo_score', 0)
        
        section += f"- **Security Score:** {security_score}/100\n"
        section += f"- **SEO Score:** {seo_score}/100\n"
        
        # Overall grade
        avg_score = (security_score + seo_score) / 2
        if avg_score >= 80:
            grade = "A - Excellent"
        elif avg_score >= 70:
            grade = "B - Good"
        elif avg_score >= 60:
            grade = "C - Fair"
        elif avg_score >= 50:
            grade = "D - Needs Improvement"
        else:
            grade = "F - Critical Issues"
        
        section += f"- **Overall Grade:** {grade}\n\n"
        
        section += "### Key Recommendations\n\n"
        
        recommendations = []
        
        # Security recommendations
        if security_score < 80:
            recommendations.append("🔒 **Security:** Implement missing security headers and enable HTTPS")
        
        # SEO recommendations
        if seo_score < 80:
            seo_meta = scan_results.get('seo', {}).get('meta_tags', {})
            if not seo_meta.get('title', {}).get('optimal'):
                recommendations.append("📝 **SEO:** Optimize title tag length (30-60 characters)")
            if not seo_meta.get('description', {}).get('optimal'):
                recommendations.append("📝 **SEO:** Optimize meta description (120-160 characters)")
        
        # Mobile recommendations
        mobile = scan_results.get('seo', {}).get('mobile_friendly', {})
        if not mobile.get('has_viewport_meta'):
            recommendations.append("📱 **Mobile:** Add viewport meta tag for mobile responsiveness")
        
        # Performance recommendations
        perf = scan_results.get('seo', {}).get('performance', {})
        if perf.get('load_time', 0) > 3:
            recommendations.append("⚡ **Performance:** Optimize page load time (currently >3 seconds)")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                section += f"{i}. {rec}\n"
        else:
            section += "✓ Website follows most best practices. Continue monitoring and improving.\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return """## Report Information

This report was generated by **Linux Spider Web Scanner**.

**Disclaimer:** This automated scan provides a general overview of the website's technical aspects. 
For comprehensive security audits or detailed SEO analysis, consider consulting with specialists.

---

*Report End*
"""
