#!/usr/bin/env python3
"""
Linux Spider Web Scanner
A comprehensive web scanning tool for Linux systems

Main entry point with interactive CLI menu
"""

import sys
import os
import argparse
from pathlib import Path
from colorama import init, Fore, Style
from version import __version__, __description__
from utils.helpers import normalize_url, extract_domain
from utils.report_generator import ReportGenerator
from utils.enhanced_report import EnhancedReportGenerator
from utils.logger import get_logger, set_debug_mode
from utils.ai_reporter import generate_ai_report_from_text, save_aggregated_report
from scanner.discovery_scanner import DiscoveryScanner
from scanner.content_scanner import ContentScanner
from scanner.domain_scanner import DomainScanner
from scanner.host_scanner import HostScanner
from scanner.tech_scanner import TechnologyScanner
from scanner.cms_scanner import CMSScanner
from scanner.security_scanner import SecurityScanner
from scanner.seo_scanner import SEOScanner

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)


class WebScanner:
    """Main web scanner orchestrator"""
    
    def __init__(self, debug_mode=False):
        """Initialize web scanner"""
        self.url = None
        self.domain = None
        self.scan_results = {}
        self.report_generator = ReportGenerator()
        self.logger = get_logger(debug_mode=debug_mode)
        self.debug_mode = debug_mode
    
    def display_banner(self):
        """Display application banner"""
        banner = f"""
{Fore.CYAN}
    ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗    ███████╗██████╗ ██╗██████╗ ███████╗██████╗ 
    ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝    ██╔════╝██╔══██╗██║██╔══██╗██╔════╝██╔══██╗
    ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝     ███████╗██████╔╝██║██║  ██║█████╗  ██████╔╝
    ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗     ╚════██║██╔═══╝ ██║██║  ██║██╔══╝  ██╔══██╗
    ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗    ███████║██║     ██║██████╔╝███████╗██║  ██║
    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝    ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}
{Fore.GREEN}                    🕷️  Web Scanning Tool v{__version__}  🕷️{Style.RESET_ALL}
{Fore.YELLOW}                     Comprehensive Website Analysis{Style.RESET_ALL}

{Fore.WHITE}┌─────────────────────────────────────────────────────────────────┐
│  📡 Domain & WHOIS    │  🖥️  Hosting & DNS   │  🔧 Technology    │
│  📦 CMS Detection     │  🔒 Security Scan    │  📊 SEO Analysis  │
│  🤖 AI Expert Report  │  📝 Detailed Reports │  🌐 Multi-Target  │
└─────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
"""
        print(banner)
    
    def display_menu(self):
        """Display main menu"""
        menu = f"""
{Fore.CYAN}┌─────────────────────────────────────────────────────────────────┐
│                         MAIN MENU                               │
├─────────────────────────────────────────────────────────────────┤{Style.RESET_ALL}
│  {Fore.GREEN}[1]{Style.RESET_ALL} 🔍 Start New Scan                                        │
│  {Fore.GREEN}[2]{Style.RESET_ALL} 📂 View Recent Reports                                   │
│  {Fore.GREEN}[3]{Style.RESET_ALL} ⚙️  Settings & Configuration                             │
│  {Fore.GREEN}[4]{Style.RESET_ALL} ℹ️  About                                                 │
│  {Fore.GREEN}[5]{Style.RESET_ALL} 🚪 Exit                                                  │
{Fore.CYAN}└─────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
"""
        print(menu)
    
    def get_target_url(self):
        """Get target URL from user"""
        while True:
            print(f"\n{Fore.YELLOW}Enter target website URL:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}(e.g., example.com or https://example.com){Style.RESET_ALL}")
            
            url_input = input(f"{Fore.GREEN}URL > {Style.RESET_ALL}").strip()
            
            if not url_input:
                print(f"{Fore.RED}✗ URL cannot be empty{Style.RESET_ALL}")
                continue
            
            # Normalize URL
            normalized_url = normalize_url(url_input)
            
            if not normalized_url:
                print(f"{Fore.RED}✗ Invalid URL format{Style.RESET_ALL}")
                continue
            
            # Extract domain
            domain = extract_domain(normalized_url)
            
            if not domain:
                print(f"{Fore.RED}✗ Could not extract domain from URL{Style.RESET_ALL}")
                continue
            
            # Confirm with user
            print(f"\n{Fore.CYAN}Target Information:{Style.RESET_ALL}")
            print(f"  URL: {Fore.WHITE}{normalized_url}{Style.RESET_ALL}")
            print(f"  Domain: {Fore.WHITE}{domain}{Style.RESET_ALL}")
            
            confirm = input(f"\n{Fore.YELLOW}Proceed with this target? (y/n): {Style.RESET_ALL}").lower()
            
            if confirm == 'y':
                self.url = normalized_url
                self.domain = domain
                return True
            
            return False
    
    def select_scan_modules(self):
        """Allow user to select which scan modules to run"""
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════════════")
        print(f"                   SELECT SCAN MODULES")
        print(f"═══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"\n{Fore.WHITE}Select which modules to run:{Style.RESET_ALL}\n")
        
        modules = {
            '1': {'name': 'Domain Information', 'key': 'domain', 'selected': True},
            '2': {'name': 'Hosting & Infrastructure', 'key': 'host', 'selected': True},
            '3': {'name': 'Technology Detection', 'key': 'tech', 'selected': True},
            '4': {'name': 'CMS Analysis', 'key': 'cms', 'selected': True},
            '5': {'name': 'Security Scanning', 'key': 'security', 'selected': True},
            '6': {'name': 'SEO Analysis', 'key': 'seo', 'selected': True},
            '7': {'name': 'Content & Products (NEW)', 'key': 'content', 'selected': True}
        }
        
        for key, module in modules.items():
            status = f"{Fore.GREEN}[✓]{Style.RESET_ALL}" if module['selected'] else f"{Fore.RED}[ ]{Style.RESET_ALL}"
            print(f"{status} {key}. {module['name']}")
        
        print(f"\n{Fore.CYAN}8. Run All (Default)")
        print(f"9. Continue with selection{Style.RESET_ALL}")
        
        while True:
            choice = input(f"\n{Fore.GREEN}Select option (1-9) or press Enter to run all: {Style.RESET_ALL}").strip()
            
            if not choice or choice == '8':
                # Run all modules
                return {module['key']: True for module in modules.values()}
            
            elif choice == '9':
                # Continue with current selection
                return {module['key']: module['selected'] for module in modules.values()}
            
            elif choice in modules:
                # Toggle module
                modules[choice]['selected'] = not modules[choice]['selected']
                # Redisplay
                return self.select_scan_modules()
            
            else:
                print(f"{Fore.RED}✗ Invalid option{Style.RESET_ALL}")
    
    def run_scan(self, selected_modules):
        """Run the actual scanning process"""
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════════════")
        print(f"                    STARTING SCAN")
        print(f"═══════════════════════════════════════════════════════════════{Style.RESET_ALL}\n")
        
        print(f"{Fore.WHITE}Target: {self.url}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Domain: {self.domain}{Style.RESET_ALL}\n")
        
        total_modules = sum(1 for v in selected_modules.values() if v)
        current = 0
        
        # Domain Scanner
        if selected_modules.get('domain', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] Domain Information{Style.RESET_ALL}")
                domain_scanner = DomainScanner()
                self.scan_results['domain'] = domain_scanner.scan(self.domain)
                print(f"{Fore.GREEN}✓ Domain scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ Domain scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['domain'] = {'error': str(e)}
        
        # Host Scanner
        if selected_modules.get('host', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] Hosting & Infrastructure{Style.RESET_ALL}")
                host_scanner = HostScanner()
                self.scan_results['host'] = host_scanner.scan(self.url, self.domain)
                print(f"{Fore.GREEN}✓ Host scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ Host scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['host'] = {'error': str(e)}
        
        # Technology Scanner
        if selected_modules.get('tech', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] Technology Detection{Style.RESET_ALL}")
                tech_scanner = TechnologyScanner()
                self.scan_results['technology'] = tech_scanner.scan(self.url)
                print(f"{Fore.GREEN}✓ Technology scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ Technology scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['technology'] = {'error': str(e)}
        
        # CMS Scanner
        if selected_modules.get('cms', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] CMS Analysis{Style.RESET_ALL}")
                cms_scanner = CMSScanner()
                self.scan_results['cms'] = cms_scanner.scan(self.url)
                print(f"{Fore.GREEN}✓ CMS scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ CMS scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['cms'] = {'error': str(e)}
        
        # Security Scanner
        if selected_modules.get('security', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] Security Analysis{Style.RESET_ALL}")
                security_scanner = SecurityScanner()
                self.scan_results['security'] = security_scanner.scan(self.url)
                print(f"{Fore.GREEN}✓ Security scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ Security scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['security'] = {'error': str(e)}
        
        # SEO Scanner
        if selected_modules.get('seo', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] SEO Analysis{Style.RESET_ALL}")
                seo_scanner = SEOScanner()
                self.scan_results['seo'] = seo_scanner.scan(self.url)
                print(f"{Fore.GREEN}✓ SEO scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ SEO scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['seo'] = {'error': str(e)}
        
        # Content & Products Scanner (NEW)
        if selected_modules.get('content', False):
            current += 1
            try:
                print(f"{Fore.CYAN}[{current}/{total_modules}] Content & Products Analysis{Style.RESET_ALL}")
                content_scanner = ContentScanner()
                content_results = content_scanner.scan(self.url)
                self.scan_results['content'] = content_results
                self.scan_results['articles'] = content_results.get('articles', {})
                self.scan_results['products'] = content_results.get('products', {})
                self.scan_results['schema_validation'] = content_results.get('schema_validation', {})
                self.scan_results['technical_seo'] = content_results.get('technical_seo', {})
                self.scan_results['onpage_seo'] = content_results.get('onpage_seo', {})
                print(f"{Fore.GREEN}✓ Content & Products scan completed{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"{Fore.RED}✗ Content scan failed: {e}{Style.RESET_ALL}\n")
                self.scan_results['content'] = {'error': str(e)}
        
        print(f"{Fore.GREEN}═══════════════════════════════════════════════════════════════")
        print(f"                  SCAN COMPLETED")
        print(f"═══════════════════════════════════════════════════════════════{Style.RESET_ALL}\n")
    
    def generate_report(self):
        """Generate scan report"""
        try:
            report_path = self.report_generator.generate_report(
                self.scan_results,
                self.url,
                self.domain
            )
            
            print(f"\n{Fore.GREEN}✓ Report generated successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Report saved to: {Fore.WHITE}{report_path}{Style.RESET_ALL}\n")
            
            # Display quick summary
            self.display_quick_summary()
            
            return report_path
        except Exception as e:
            print(f"{Fore.RED}✗ Report generation failed: {e}{Style.RESET_ALL}")
            return None
    
    def run_ai_analysis(self, report_path: str):
        """Run AI analysis on the generated report"""
        config_path = "config/ai_services.txt"
        
        # Check if AI config exists
        if not os.path.exists(config_path):
            print(f"\n{Fore.YELLOW}⚠ AI analysis config not found ({config_path}){Style.RESET_ALL}")
            print(f"{Fore.WHITE}To enable AI analysis, copy config/ai_services.txt.example to config/ai_services.txt")
            print(f"and add your API keys (OpenAI, OpenRouter, or Gemini).{Style.RESET_ALL}")
            return None
        
        # Ask user if they want AI analysis
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════════════")
        print(f"                    AI ANALYSIS")
        print(f"═══════════════════════════════════════════════════════════════{Style.RESET_ALL}\n")
        
        print(f"{Fore.WHITE}Would you like to generate an AI-powered expert analysis?{Style.RESET_ALL}")
        print(f"{Fore.WHITE}The analysis will be provided in both English and Persian (Farsi).{Style.RESET_ALL}\n")
        
        choice = input(f"{Fore.GREEN}Generate AI analysis? (y/n): {Style.RESET_ALL}").strip().lower()
        
        if choice not in ['y', 'yes', 'بله', 'آره']:
            print(f"{Fore.YELLOW}Skipping AI analysis.{Style.RESET_ALL}")
            return None
        
        try:
            print(f"\n{Fore.CYAN}Generating AI analysis... Please wait...{Style.RESET_ALL}")
            
            # Read the report content
            with open(report_path, 'r', encoding='utf-8') as f:
                report_text = f.read()
            
            # Generate AI analysis
            results = generate_ai_report_from_text(report_text, config_path=config_path)
            
            # Check for errors
            if 'error' in results:
                print(f"{Fore.RED}✗ AI analysis failed: {results['error']}{Style.RESET_ALL}")
                return None
            
            # Save the AI report
            ai_report_path = save_aggregated_report(results, domain=self.domain, out_dir='reports')
            
            print(f"\n{Fore.GREEN}✓ AI analysis completed!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}AI Report saved to: {Fore.WHITE}{ai_report_path}{Style.RESET_ALL}")
            
            # Show preview of results
            for provider, res in results.items():
                if isinstance(res, dict) and 'result' in res:
                    print(f"\n{Fore.GREEN}✓ {provider}: Analysis generated successfully{Style.RESET_ALL}")
                elif isinstance(res, dict) and 'error' in res:
                    print(f"{Fore.RED}✗ {provider}: {res['error']}{Style.RESET_ALL}")
            
            return ai_report_path
            
        except Exception as e:
            print(f"{Fore.RED}✗ AI analysis failed: {e}{Style.RESET_ALL}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return None

    def display_quick_summary(self):
        """Display quick summary of scan results"""
        print(f"{Fore.CYAN}═══════════════════════════════════════════════════════════════")
        print(f"                    QUICK SUMMARY")
        print(f"═══════════════════════════════════════════════════════════════{Style.RESET_ALL}\n")
        
        # Security Score
        if 'security' in self.scan_results:
            security_score = self.scan_results['security'].get('security_score', 0)
            print(f"{Fore.WHITE}Security Score: {Fore.YELLOW}{security_score}/100{Style.RESET_ALL}")
        
        # SEO Score
        if 'seo' in self.scan_results:
            seo_score = self.scan_results['seo'].get('seo_score', 0)
            print(f"{Fore.WHITE}SEO Score: {Fore.YELLOW}{seo_score}/100{Style.RESET_ALL}")
        
        # Technical SEO Score (NEW)
        if 'technical_seo' in self.scan_results:
            tech_seo = self.scan_results['technical_seo']
            tech_score = tech_seo.get('overall_score', 0)
            print(f"{Fore.WHITE}Technical SEO Score: {Fore.YELLOW}{tech_score}/100{Style.RESET_ALL}")
        
        # On-Page SEO Score (NEW)
        if 'onpage_seo' in self.scan_results:
            onpage_seo = self.scan_results['onpage_seo']
            onpage_score = onpage_seo.get('overall_score', 0)
            print(f"{Fore.WHITE}On-Page SEO Score: {Fore.YELLOW}{onpage_score}/100{Style.RESET_ALL}")
        
        # CMS Detection
        if 'cms' in self.scan_results:
            cms_type = self.scan_results['cms'].get('cms_detected', 'Unknown')
            print(f"{Fore.WHITE}CMS Detected: {Fore.YELLOW}{cms_type}{Style.RESET_ALL}")
        
        # HTTPS Status
        if 'host' in self.scan_results:
            ssl_info = self.scan_results['host'].get('ssl_info', {})
            https_status = "✓ Enabled" if ssl_info.get('enabled') else "✗ Not Enabled"
            color = Fore.GREEN if ssl_info.get('enabled') else Fore.RED
            print(f"{Fore.WHITE}HTTPS: {color}{https_status}{Style.RESET_ALL}")
        
        # Articles Found (NEW)
        if 'articles' in self.scan_results:
            articles = self.scan_results['articles']
            article_count = articles.get('total_found', 0)
            print(f"{Fore.WHITE}Articles Found: {Fore.YELLOW}{article_count}{Style.RESET_ALL}")
        
        # Products Found (NEW)
        if 'products' in self.scan_results:
            products = self.scan_results['products']
            product_count = products.get('total_found', 0)
            print(f"{Fore.WHITE}Products Found: {Fore.YELLOW}{product_count}{Style.RESET_ALL}")
        
        # Schema Validation (NEW)
        if 'schema_validation' in self.scan_results:
            schema = self.scan_results['schema_validation']
            valid_count = schema.get('valid_schemas', 0)
            total_count = schema.get('total_schemas', 0)
            if total_count > 0:
                color = Fore.GREEN if valid_count == total_count else Fore.YELLOW
                print(f"{Fore.WHITE}Schema.org Validation: {color}{valid_count}/{total_count} valid{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Check the full report for detailed analysis and recommendations.{Style.RESET_ALL}\n")
    
    def view_recent_reports(self):
        """View list of recent reports"""
        reports_dir = 'reports'
        
        if not os.path.exists(reports_dir):
            print(f"\n{Fore.YELLOW}No reports found.{Style.RESET_ALL}\n")
            return
        
        reports = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
        
        if not reports:
            print(f"\n{Fore.YELLOW}No reports found.{Style.RESET_ALL}\n")
            return
        
        # Sort by modification time (newest first)
        reports.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
        
        print(f"\n{Fore.CYAN}Recent Reports:{Style.RESET_ALL}\n")
        
        for i, report in enumerate(reports[:10], 1):  # Show last 10 reports
            report_path = os.path.join(reports_dir, report)
            mod_time = os.path.getmtime(report_path)
            from datetime import datetime
            date_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{Fore.GREEN}{i}.{Style.RESET_ALL} {report}")
            print(f"   {Fore.WHITE}Created: {date_str}{Style.RESET_ALL}")
            print(f"   {Fore.WHITE}Path: {report_path}{Style.RESET_ALL}\n")
    
    def display_about(self):
        """Display about information"""
        about = f"""
{Fore.CYAN}═══════════════════════════════════════════════════════════════
                        ABOUT
═══════════════════════════════════════════════════════════════{Style.RESET_ALL}

{Fore.GREEN}Linux Spider Web Scanner v1.0{Style.RESET_ALL}

A comprehensive web scanning tool designed for Linux systems that
performs detailed analysis of websites including:

• Domain & WHOIS Information
• Hosting & Infrastructure Details
• Technology Stack Detection
• CMS Analysis (WordPress, Joomla, Drupal)
• Security Assessment
• SEO Analysis

{Fore.CYAN}Features:{Style.RESET_ALL}
• Random User-Agent rotation for stealth
• Comprehensive error handling
• Detailed markdown reports
• Modular architecture
• Easy to use CLI interface

{Fore.CYAN}Requirements:{Style.RESET_ALL}
• Python 3.8+
• Linux OS (all distributions)
• Internet connection

{Fore.CYAN}Report Location:{Style.RESET_ALL}
All scan reports are saved in the 'reports/' directory with
the format: scan_<domain>_<timestamp>.md

{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
        print(about)
    
    def display_settings(self):
        """Display settings and configuration menu"""
        ai_config_path = Path("config/ai_services.txt")
        ai_status = f"{Fore.GREEN}✓ Configured{Style.RESET_ALL}" if ai_config_path.exists() else f"{Fore.YELLOW}✗ Not configured{Style.RESET_ALL}"
        
        settings = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                    ⚙️  SETTINGS & CONFIGURATION                 ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.WHITE}📁 Configuration Files:{Style.RESET_ALL}
────────────────────────────────────────────────────
  AI Services Config:  config/ai_services.txt
  Status:              {ai_status}
  
{Fore.WHITE}📂 Output Directories:{Style.RESET_ALL}
────────────────────────────────────────────────────
  Reports:   reports/
  Logs:      logs/

{Fore.WHITE}🤖 AI Analysis Setup:{Style.RESET_ALL}
────────────────────────────────────────────────────
  1. Copy 'config/ai_services.txt.example' to 'config/ai_services.txt'
  2. Add your API key for one of the services:
     • OpenAI (OPENAI_API_KEY=sk-...)
     • Gemini (GEMINI_API_KEY=...)
     • OpenRouter (OPENROUTER_API_KEY=...)

{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
        print(settings)
    
    def run(self):
        """Main application loop"""
        self.display_banner()
        
        while True:
            self.display_menu()
            
            choice = input(f"{Fore.GREEN}Select option (1-5): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                # Start new scan
                if self.get_target_url():
                    selected_modules = self.select_scan_modules()
                    self.run_scan(selected_modules)
                    report_path = self.generate_report()
                    
                    # Offer AI analysis
                    if report_path:
                        self.run_ai_analysis(report_path)
                    
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                
            elif choice == '2':
                # View recent reports
                self.view_recent_reports()
                input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
            
            elif choice == '3':
                # Settings & Configuration
                self.display_settings()
                input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
            
            elif choice == '4':
                # About
                self.display_about()
                input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
            
            elif choice == '5':
                # Exit
                print(f"\n{Fore.CYAN}Thank you for using Linux Spider Web Scanner!{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Goodbye!{Style.RESET_ALL}\n")
                sys.exit(0)
            
            else:
                print(f"\n{Fore.RED}✗ Invalid option. Please select 1-5.{Style.RESET_ALL}\n")


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Linux Spider Web Scanner - Comprehensive Website Analysis Tool'
    )
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with detailed logging'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'Linux Spider Web Scanner v{__version__}'
    )
    
    args = parser.parse_args()
    
    try:
        scanner = WebScanner(debug_mode=args.debug)
        
        if args.debug:
            scanner.logger.banner("DEBUG MODE ENABLED")
            scanner.logger.info(f"Log file: {scanner.logger.get_log_file_path()}")
            scanner.logger.info(f"Debug file: {scanner.logger.get_debug_file_path()}")
            scanner.logger.separator()
        
        scanner.run()
        
        if args.debug:
            scanner.logger.close()
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Scan interrupted by user.{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Goodbye!{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}\n")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
