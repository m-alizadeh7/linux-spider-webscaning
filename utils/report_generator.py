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
            
            # Content & Articles Analysis (NEW)
            if 'articles' in scan_results or 'content' in scan_results:
                f.write(self._generate_articles_section(scan_results))
            
            # Products Analysis (NEW)
            if 'products' in scan_results:
                f.write(self._generate_products_section(scan_results['products']))
            
            # Schema Validation (NEW)
            if 'schema_validation' in scan_results:
                f.write(self._generate_schema_section(scan_results['schema_validation']))
            
            # Technical SEO (NEW)
            if 'technical_seo' in scan_results:
                f.write(self._generate_technical_seo_section(scan_results['technical_seo']))
            
            # On-Page SEO (NEW)
            if 'onpage_seo' in scan_results:
                f.write(self._generate_onpage_seo_section(scan_results['onpage_seo']))
            
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
        if not domain_data:
            return "## 1. Domain Information\n\n*Domain information not available*\n\n---\n\n"
        
        whois = domain_data.get('whois', {}) or {}
        dns = domain_data.get('dns', {}) or {}
        ips = domain_data.get('ip_addresses', []) or []
        
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
        if not host_data:
            return "## 2. Hosting & Infrastructure\n\n*Hosting information not available*\n\n---\n\n"
        
        server_info = host_data.get('server_info', {}) or {}
        ssl_info = host_data.get('ssl_info', {}) or {}
        response_info = host_data.get('response_info', {}) or {}
        
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
        if not tech_data:
            return "## 3. Technology Stack\n\n*Technology information not available*\n\n---\n\n"
        
        manual = tech_data.get('manual_detection', {}) or {}
        js_libs = tech_data.get('javascript_libraries', []) or []
        generators = tech_data.get('meta_generators', []) or []
        
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
        if not cms_data:
            return "## 4. CMS Analysis\n\n*CMS information not available*\n\n---\n\n"
        
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
        if not security_data:
            return "## 5. Security Analysis\n\n*Security information not available*\n\n---\n\n"
        
        score = security_data.get('security_score', 0)
        headers = security_data.get('security_headers', {}) or {}
        ssl = security_data.get('ssl_analysis', {}) or {}
        common_files = security_data.get('common_files', {}) or {}
        info_disclosure = security_data.get('information_disclosure', {}) or {}
        ports = security_data.get('port_scan', {}) or {}
        
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
        if not seo_data:
            return "## 6. SEO Analysis\n\n*SEO information not available*\n\n---\n\n"
        
        score = seo_data.get('seo_score', 0)
        meta = seo_data.get('meta_tags', {}) or {}
        headings = seo_data.get('headings', {}) or {}
        content = seo_data.get('content_analysis', {}) or {}
        links = seo_data.get('links', {}) or {}
        images = seo_data.get('images', {}) or {}
        mobile = seo_data.get('mobile_friendly', {}) or {}
        performance = seo_data.get('performance', {}) or {}
        
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
        section = """## 12. Summary & Recommendations

### Overall Assessment

"""
        
        # Collect scores
        security_score = scan_results.get('security', {}).get('security_score', 0)
        seo_score = scan_results.get('seo', {}).get('seo_score', 0)
        
        # Also include new scores if available
        tech_seo_score = scan_results.get('technical_seo', {}).get('score', 0)
        onpage_seo_score = scan_results.get('onpage_seo', {}).get('score', 0)
        
        section += f"- **Security Score:** {security_score}/100\n"
        section += f"- **SEO Score:** {seo_score}/100\n"
        
        if tech_seo_score:
            section += f"- **Technical SEO Score:** {tech_seo_score}/100\n"
        if onpage_seo_score:
            section += f"- **On-Page SEO Score:** {onpage_seo_score}/100\n"
        
        # Overall grade
        scores = [security_score, seo_score]
        if tech_seo_score:
            scores.append(tech_seo_score)
        if onpage_seo_score:
            scores.append(onpage_seo_score)
        
        avg_score = sum(scores) / len(scores) if scores else 0
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

    def _generate_articles_section(self, scan_results: Dict[str, Any]) -> str:
        """Generate articles analysis section"""
        section = "## 7. Articles & Content Analysis\n\n"
        
        articles_data = scan_results.get('articles', {}) or {}
        content_data = scan_results.get('content', {}) or {}
        
        # Discovery info
        discovery = content_data.get('discovery', {}) or {}
        if discovery:
            section += "### Content Discovery\n\n"
            
            sitemap_urls = discovery.get('sitemap_urls', [])
            rss_feeds = discovery.get('rss_feeds', [])
            
            section += f"- **Sitemap URLs Found:** {len(sitemap_urls)}\n"
            section += f"- **RSS/Atom Feeds Found:** {len(rss_feeds)}\n"
            
            if rss_feeds:
                section += "\n**RSS Feeds:**\n"
                for feed in rss_feeds[:5]:
                    title = feed.get('title', 'Untitled')
                    url = feed.get('url', '')
                    section += f"- {title}: `{url}`\n"
            
            section += "\n"
        
        # Articles list
        articles_list = articles_data.get('articles', [])
        total_articles = articles_data.get('total_found', len(articles_list))
        
        section += "### Articles Found\n\n"
        section += f"- **Total Articles Detected:** {total_articles}\n"
        
        if articles_list:
            section += "\n**Recent Articles:**\n\n"
            section += "| # | Title | Date | Author |\n"
            section += "|---|-------|------|--------|\n"
            
            for i, article in enumerate(articles_list[:20], 1):
                title = str(article.get('title', 'Untitled') or 'Untitled')[:50]
                date = article.get('date_published', 'N/A')
                if date and len(str(date)) > 10:
                    date = str(date)[:10]
                author = str(article.get('author', 'Unknown') or 'Unknown')[:20]
                section += f"| {i} | {title} | {date} | {author} |\n"
            
            if len(articles_list) > 20:
                section += f"\n*... and {len(articles_list) - 20} more articles*\n"
        else:
            section += "\n*No articles detected on this website*\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_products_section(self, products_data: Dict[str, Any]) -> str:
        """Generate products analysis section"""
        section = "## 8. Products Analysis (E-commerce)\n\n"
        
        if not products_data:
            section += "*Product information not available*\n\n---\n\n"
            return section
        
        products_list = products_data.get('products', []) or []
        total_products = products_data.get('total_found', len(products_list))
        
        section += f"- **Total Products Detected:** {total_products}\n"
        section += f"- **E-commerce Detected:** {'✓ Yes' if total_products > 0 else '✗ No'}\n\n"
        
        if products_list:
            section += "### Product Catalog Sample\n\n"
            section += "| # | Product Name | Price | Availability |\n"
            section += "|---|--------------|-------|-------------|\n"
            
            for i, product in enumerate(products_list[:20], 1):
                name = str(product.get('name', 'Untitled') or 'Untitled')[:40]
                price = product.get('price', 'N/A')
                if isinstance(price, dict):
                    price = f"{price.get('value', 'N/A')} {price.get('currency', '')}"
                elif price is None:
                    price = 'N/A'
                availability = product.get('availability', 'Unknown') or 'Unknown'
                if 'InStock' in str(availability):
                    availability = '✓ In Stock'
                elif 'OutOfStock' in str(availability):
                    availability = '✗ Out of Stock'
                section += f"| {i} | {name} | {price} | {availability} |\n"
            
            if len(products_list) > 20:
                section += f"\n*... and {len(products_list) - 20} more products*\n"
        else:
            section += "*No products detected - this may not be an e-commerce website*\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_schema_section(self, schema_data: Dict[str, Any]) -> str:
        """Generate schema validation section"""
        section = "## 9. Schema.org Structured Data\n\n"
        
        if not schema_data:
            section += "*Schema information not available*\n\n---\n\n"
            return section
        
        schemas = schema_data.get('schemas', []) or []
        valid_count = schema_data.get('valid_schemas', 0)
        total_count = schema_data.get('total_schemas', len(schemas))
        
        if total_count > 0:
            validity_pct = (valid_count / total_count) * 100
            status = "✓ Good" if validity_pct >= 80 else "⚠️ Needs Improvement" if validity_pct >= 50 else "✗ Poor"
            section += f"### Schema Validation: {status}\n\n"
            section += f"- **Total Schemas Found:** {total_count}\n"
            section += f"- **Valid Schemas:** {valid_count}\n"
            section += f"- **Validity Rate:** {validity_pct:.1f}%\n\n"
            
            section += "### Detected Schema Types\n\n"
            section += "| Schema Type | Valid | Issues |\n"
            section += "|-------------|-------|--------|\n"
            
            for schema in schemas[:15]:
                schema_type = schema.get('type', 'Unknown')
                is_valid = "✓" if schema.get('is_valid', False) else "✗"
                errors = schema.get('errors', [])
                issues = ', '.join(errors[:2]) if errors else 'None'
                section += f"| {schema_type} | {is_valid} | {issues[:50]} |\n"
        else:
            section += "### ⚠️ No Schema.org Markup Found\n\n"
            section += "**Recommendation:** Implement structured data for better SEO:\n\n"
            section += "- Add `Organization` schema for brand identity\n"
            section += "- Add `WebSite` schema with SearchAction\n"
            section += "- Add `Article` schema for blog posts\n"
            section += "- Add `Product` schema for e-commerce\n"
            section += "- Add `BreadcrumbList` for navigation\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_technical_seo_section(self, tech_seo: Dict[str, Any]) -> str:
        """Generate technical SEO section"""
        section = "## 10. Technical SEO Analysis\n\n"
        
        if not tech_seo:
            section += "*Technical SEO information not available*\n\n---\n\n"
            return section
        
        score = tech_seo.get('score', tech_seo.get('overall_score', 0))
        grade = self._get_score_grade(score)
        section += f"### Technical SEO Score: {score}/100 - {grade}\n\n"
        
        section += "| Check | Status | Details |\n"
        section += "|-------|--------|--------|\n"
        
        # Direct field mapping from TechnicalSEOResult.to_dict()
        https_status = tech_seo.get('is_https', False)
        section += f"| HTTPS Enabled | {'✓' if https_status else '✗'} | {'Secure connection' if https_status else 'Not using HTTPS'} |\n"
        
        canonical = tech_seo.get('canonical_url', None)
        canonical_matches = tech_seo.get('canonical_matches', False)
        section += f"| Canonical Tag | {'✓' if canonical else '✗'} | {str(canonical)[:40] if canonical else 'Not set'}{'...' if canonical and len(str(canonical)) > 40 else ''} |\n"
        
        robots_txt = tech_seo.get('robots_txt_exists', False)
        section += f"| robots.txt | {'✓' if robots_txt else '✗'} | {'Found' if robots_txt else 'Not found'} |\n"
        
        sitemap = tech_seo.get('sitemap_exists', False)
        sitemap_in_robots = tech_seo.get('sitemap_in_robots', False)
        section += f"| XML Sitemap | {'✓' if sitemap else '✗'} | {'Found' + (' (in robots.txt)' if sitemap_in_robots else '') if sitemap else 'Not found'} |\n"
        
        mobile_viewport = tech_seo.get('mobile_viewport', False)
        section += f"| Mobile Friendly | {'✓' if mobile_viewport else '✗'} | {'Viewport meta tag present' if mobile_viewport else 'No viewport meta tag'} |\n"
        
        ttfb = tech_seo.get('ttfb_ms', 0)
        load_time = tech_seo.get('load_time_ms', 0)
        ttfb_ok = ttfb < 600 if ttfb else False
        section += f"| Page Speed | {'✓' if ttfb_ok else '✗'} | TTFB: {ttfb}ms, Load: {load_time}ms |\n"
        
        is_indexable = tech_seo.get('is_indexable', True)
        section += f"| Indexability | {'✓' if is_indexable else '✗'} | {'Indexable' if is_indexable else 'Blocked from indexing'} |\n"
        
        # Issues
        issues = tech_seo.get('issues', []) or []
        if issues:
            section += "\n### Issues Found\n\n"
            for issue in issues[:10]:
                if isinstance(issue, dict):
                    section += f"- **{issue.get('issue', 'Unknown')}** ({issue.get('impact', 'N/A')}): {issue.get('fix', '')}\n"
                else:
                    section += f"- {issue}\n"
        
        # Warnings
        warnings = tech_seo.get('warnings', []) or []
        if warnings:
            section += "\n### Warnings\n\n"
            for warning in warnings[:10]:
                if isinstance(warning, dict):
                    section += f"- {warning.get('issue', warning)}\n"
                else:
                    section += f"- {warning}\n"
        
        # Passed checks
        passed = tech_seo.get('passed', []) or []
        if passed:
            section += "\n### Passed Checks\n\n"
            for p in passed[:10]:
                section += f"- ✓ {p}\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_onpage_seo_section(self, onpage_seo: Dict[str, Any]) -> str:
        """Generate on-page SEO section"""
        section = "## 11. On-Page SEO Analysis\n\n"
        
        if not onpage_seo:
            section += "*On-page SEO information not available*\n\n---\n\n"
            return section
        
        score = onpage_seo.get('score', onpage_seo.get('overall_score', 0))
        grade = self._get_score_grade(score)
        section += f"### On-Page SEO Score: {score}/100 - {grade}\n\n"
        
        # Title analysis - directly from onpage_seo dict
        title = onpage_seo.get('title', {}) or {}
        section += "### Title Tag\n\n"
        title_content = title.get('content', 'Not set') or 'Not set'
        section += f"- **Content:** {title_content[:80]}{'...' if len(str(title_content)) > 80 else ''}\n"
        section += f"- **Length:** {title.get('length', len(str(title_content)) if title_content != 'Not set' else 0)} characters\n"
        section += f"- **Status:** {'✓ Optimal' if title.get('optimal', False) else '⚠️ Needs optimization'}\n\n"
        
        # Meta description - directly from onpage_seo dict
        meta_desc = onpage_seo.get('meta_description', {}) or {}
        section += "### Meta Description\n\n"
        desc_content = meta_desc.get('content', 'Not set') or 'Not set'
        section += f"- **Content:** {str(desc_content)[:100]}{'...' if len(str(desc_content)) > 100 else ''}\n"
        section += f"- **Length:** {meta_desc.get('length', 0)} characters\n"
        section += f"- **Status:** {'✓ Optimal' if meta_desc.get('optimal', False) else '⚠️ Needs optimization'}\n\n"
        
        # Headings - directly from onpage_seo dict
        headings = onpage_seo.get('headings', {}) or {}
        section += "### Heading Structure\n\n"
        section += f"- **H1 Tags:** {headings.get('h1_count', 0)}\n"
        h1_content = headings.get('h1_content', [])
        if h1_content:
            section += f"- **H1 Content:** {', '.join(str(h)[:50] for h in h1_content[:3])}\n"
        section += f"- **H2 Tags:** {headings.get('h2_count', 0)}\n"
        section += f"- **H3 Tags:** {headings.get('h3_count', 0)}\n"
        hierarchy_valid = headings.get('hierarchy_valid', headings.get('optimal', False))
        section += f"- **Status:** {'✓ Good hierarchy' if hierarchy_valid else '⚠️ Review heading hierarchy'}\n\n"
        
        # Content quality - directly from onpage_seo dict
        content = onpage_seo.get('content', {}) or {}
        section += "### Content Quality\n\n"
        word_count = content.get('word_count', 0)
        section += f"- **Word Count:** {word_count}\n"
        section += f"- **Paragraphs:** {content.get('paragraph_count', 0)}\n"
        is_thin = content.get('is_thin_content', word_count < 300 if word_count else True)
        section += f"- **Content Status:** {'⚠️ Thin content (< 300 words)' if is_thin else '✓ Adequate content'}\n\n"
        
        # Links - directly from onpage_seo dict
        links = onpage_seo.get('links', {}) or {}
        section += "### Link Analysis\n\n"
        section += f"- **Internal Links:** {links.get('internal', 0)}\n"
        section += f"- **External Links:** {links.get('external', 0)}\n"
        section += f"- **Nofollow Links:** {links.get('nofollow', 0)}\n\n"
        
        # Images - directly from onpage_seo dict
        images = onpage_seo.get('images', {}) or {}
        section += "### Image Optimization\n\n"
        section += f"- **Total Images:** {images.get('total', 0)}\n"
        section += f"- **With Alt Text:** {images.get('with_alt', 0)}\n"
        section += f"- **Missing Alt Text:** {images.get('missing_alt', 0)}\n"
        alt_coverage = images.get('alt_coverage_percent', 0)
        if isinstance(alt_coverage, (int, float)):
            section += f"- **Alt Coverage:** {alt_coverage:.1f}%\n\n"
        else:
            section += f"- **Alt Coverage:** N/A\n\n"
        
        # Issues
        issues = onpage_seo.get('issues', []) or []
        if issues:
            section += "### Issues Found\n\n"
            for issue in issues[:10]:
                if isinstance(issue, dict):
                    section += f"- **{issue.get('issue', 'Unknown')}** ({issue.get('impact', 'N/A')}): {issue.get('fix', '')}\n"
                else:
                    section += f"- {issue}\n"
        
        # Warnings
        warnings = onpage_seo.get('warnings', []) or []
        if warnings:
            section += "\n### Warnings\n\n"
            for warning in warnings[:10]:
                if isinstance(warning, dict):
                    section += f"- {warning.get('issue', warning)}\n"
                else:
                    section += f"- {warning}\n"
        
        # Passed checks
        passed = onpage_seo.get('passed', []) or []
        if passed:
            section += "\n### Passed Checks\n\n"
            for p in passed[:10]:
                section += f"- ✓ {p}\n"
        
        section += "\n---\n\n"
        return section
    
    def _get_score_grade(self, score: int) -> str:
        """Get grade emoji based on score"""
        if score >= 90:
            return "🟢 Excellent"
        elif score >= 70:
            return "🟡 Good"
        elif score >= 50:
            return "🟠 Fair"
        else:
            return "🔴 Needs Improvement"
