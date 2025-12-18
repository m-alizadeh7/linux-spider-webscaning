# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-12-19

### 🎯 Major Update: Content Intelligence & Advanced SEO Analysis

This release adds comprehensive content extraction, advanced SEO modules, and enhanced reporting capabilities.

### ✨ New Features

#### 📝 Content Scanner Module (NEW)
- **Article Extractor**: Automatic detection and extraction of blog posts and articles
  - Title, date, author, excerpt extraction
  - Content structure analysis
  - Word count and reading time estimation
- **Product Extractor**: E-commerce product catalog detection
  - Product name, price, availability
  - WooCommerce, Shopify, and generic product detection
  - Schema.org Product markup parsing
- **Sitemap Discovery**: Comprehensive XML sitemap parsing
  - Support for sitemap index files
  - URL categorization (articles, products, categories, pages)
  - Nested sitemap handling
- **RSS/Atom Discovery**: Feed detection and content sampling
  - Multiple feed format support
  - Recent post extraction

#### ⚙️ Technical SEO Module (NEW)
- **HTTPS Analysis**: SSL/TLS configuration verification
- **Canonical URL Check**: Proper canonical tag validation
- **robots.txt Analysis**: Existence and content verification
- **XML Sitemap Check**: Sitemap presence and robots.txt reference
- **Mobile Viewport**: Viewport meta tag verification
- **Page Speed Metrics**: TTFB and load time measurement
- **Indexability Check**: Meta robots and X-Robots-Tag analysis
- **Score Calculation**: 0-100 technical SEO score

#### 📄 On-Page SEO Module (NEW)
- **Title Tag Analysis**: Length optimization (30-60 chars)
- **Meta Description Analysis**: Length optimization (120-160 chars)
- **Heading Hierarchy Check**: H1-H6 structure validation
- **Content Quality Analysis**: Word count, paragraph structure
- **Link Analysis**: Internal, external, and nofollow link counting
- **Image Optimization**: Alt text coverage analysis
- **Score Calculation**: 0-100 on-page SEO score

#### 🔍 Schema.org Validator (NEW)
- **JSON-LD Parsing**: JavaScript-embedded structured data
- **Microdata Parsing**: HTML5 microdata extraction
- **RDFa Parsing**: RDFa structured data support
- **Validation Engine**: Required property checking
- **Schema Types**: Support for Article, Product, Organization, WebSite, etc.

### 📊 Enhanced Reporting

#### 12-Section Comprehensive Reports
1. Domain Information
2. Hosting & Infrastructure
3. Technology Stack
4. CMS Analysis
5. Security Analysis
6. SEO Analysis
7. Articles & Content (NEW)
8. Products Analysis (NEW)
9. Schema.org Validation (NEW)
10. Technical SEO Analysis (NEW)
11. On-Page SEO Analysis (NEW)
12. Summary & Recommendations

#### Visual Enhancements
- **Score Grades**: 🟢 Excellent (90+) | 🟡 Good (70-89) | 🟠 Fair (50-69) | 🔴 Needs Improvement (<50)
- **Issues Section**: Prioritized issues with impact levels (CRITICAL, HIGH, MEDIUM, LOW)
- **Warnings Section**: Non-critical items to review
- **Passed Checks**: Successfully validated items

### 🔧 Bug Fixes
- Fixed `NoneType` errors in report generation with comprehensive null checks
- Fixed duplicate section numbering (Summary now correctly section 12)
- Fixed article author/date slicing errors with proper string conversion

### 🤖 AI Reporter Improvements
- Added fallback from `gemini-2.5-flash` to `gemini-2.0-flash` for 403 errors
- Multiple API version attempts (v1, v1beta) for better compatibility
- Improved error handling and retry logic

### 📁 New Files
```
scanner/content_scanner.py          # Content analysis orchestrator
scanner/content/article_extractor.py # Article detection
scanner/content/product_extractor.py # E-commerce products
scanner/content/sitemap_discovery.py # XML sitemap parsing
scanner/content/rss_discovery.py     # RSS/Atom feeds
scanner/content/url_sampler.py       # URL sampling
scanner/seo/technical.py             # Technical SEO analysis
scanner/seo/onpage.py                # On-page SEO analysis
scanner/seo/schema_validator.py      # Schema.org validation
```

### 📦 New Dependencies
- `extruct>=0.16.0` - Structured data extraction
- `feedparser>=6.0.10` - RSS/Atom feed parsing
- `tldextract>=5.1.0` - Domain extraction
- `validators>=0.22.0` - URL validation

### 🧪 Tested On
- mecaco-machine.com (10 products, Technical SEO 85/100)
- gutteronline.ir (10 products, On-Page SEO 95/100)
- persiangutter.ir (validation successful)

---

## [1.4.0] - 2025-12-17

### 🎯 Major Update: Professional Web Intelligence Platform

This release transforms Linux Spider into a comprehensive web intelligence and competitor analysis platform.

### ✨ New Features

#### 🔍 Discovery Scanner (Phase 0)
- **robots.txt Analysis**: Parse and analyze robots.txt for security insights
- **Sitemap Discovery**: Automatic sitemap.xml parsing and URL extraction
- **URL Categorization**: Automatic classification of discovered URLs
  - Main pages, Money pages, Blog pages, Admin pages
- **Security Insights**: Identify sensitive paths exposed in robots.txt

#### 🌐 Enhanced Domain Scanner
- **Multi-source WHOIS**: Three-tier lookup system
  1. RDAP (most reliable, structured data)
  2. System whois CLI
  3. python-whois library (fallback)
- **Confidence Level**: Data reliability scoring (0-100%)
- **Infrastructure Detection**: CDN, WAF, Hosting provider identification
- **ASN Lookup**: Autonomous System Number detection

#### 🔐 Advanced Security Scanner
- **Severity Classification**: Critical / High / Medium / Low / Info
- **Actionable Recommendations**: Specific fix instructions for each finding
- **Sensitive File Detection**: Extended checks for exposed files
- **Admin Path Discovery**: Identify exposed admin panels
- **Security Score**: Calculated based on findings severity
- **SSL/TLS Grading**: A-F grade for SSL configuration

#### 📦 Deep WordPress Analysis
- **Plugin Categorization**: SEO, Security, Performance, Builder, E-commerce
- **Vulnerability Warnings**: Known vulnerable plugin detection
- **Security Checks**: XML-RPC, debug.log, readme.html exposure
- **SEO Configuration**: Detect SEO plugins and schema markup
- **User Enumeration**: Limited ethical author enumeration
- **Recommendations Engine**: WordPress-specific improvement suggestions

#### 🤖 AI Report Improvements
- **Persian-First Reports**: Default output in professional Persian (Farsi)
- **Analysis Types**: Competitor analysis vs Own site analysis
- **Structured Output**: Executive summary, Security, SEO, Technical, Action checklist
- **Improved Prompts**: Professional management-ready reports

### 🔧 Bug Fixes
- Fixed `Path not defined` error in Settings menu
- Fixed menu handler for 5-option menu structure

### 📁 New Files
- `scanner/discovery_scanner.py` - Site discovery and crawling
- `config/prompts/ai_analysis_prompt.txt` - Persian AI prompt template

### 🔄 Changed
- Domain scanner now returns infrastructure info
- Security scanner outputs prioritized recommendations
- CMS scanner provides deep WordPress insights
- AI reporter supports target_type parameter

---

## [1.1.0] - 2025-07-29

### ✨ Added

#### AI-Powered Analysis
- **AI Expert Analysis**: Intelligent report analysis using multiple AI providers
  - OpenAI integration (GPT models)
  - Google Gemini integration (gemini-2.5-flash)
  - OpenRouter integration (multiple models)
  - Bilingual reports (English + Persian/Farsi)
  - Expert-level security and SEO recommendations

#### UI Improvements
- **New ASCII Art Banner**: Modern and clean terminal interface
- **Settings Menu**: New configuration menu (option 3)
- **Improved Menu Design**: Better visual organization with emojis

#### Project Organization
- **Config Directory**: Centralized configuration files
- **Better .gitignore**: Enhanced security for API keys and reports
- **Documentation Updates**: Improved README and guides

### 🔒 Security
- API keys are now stored in `config/ai_services.txt` (not tracked by git)
- Scan reports excluded from version control
- Sensitive data protection improvements

### 📁 Changed
- Menu structure updated (5 options instead of 4)
- Configuration files moved to `config/` directory
- Version display updated in banner

---

## [1.0.0] - 2025-12-17

### 🎉 Initial Release

The first stable release of Linux Spider Web Scanning Tool!

### ✨ Added

#### Core Features
- **Domain Scanner**: Complete domain information analysis
  - WHOIS lookup with registration, renewal, and expiration dates
  - Domain age calculation
  - Registrar information
  
- **Host Scanner**: Infrastructure and hosting details
  - DNS record analysis (A, AAAA, MX, NS, TXT, CNAME)
  - IP address resolution
  - Server identification
  - Port scanning with nmap integration
  
- **Technology Scanner**: Web technology detection
  - Framework identification
  - Library detection
  - Server-side technology recognition
  - Frontend technology analysis
  
- **CMS Scanner**: Content Management System detection
  - WordPress detection and analysis
  - Plugin enumeration
  - Theme identification
  - Version detection
  - Security configuration checks
  
- **Security Scanner**: Security analysis
  - SSL/TLS certificate validation
  - Security header analysis
  - Common vulnerability checks
  - HTTP security configuration
  
- **SEO Scanner**: Search engine optimization analysis
  - Meta tags analysis
  - Robots.txt parsing
  - Sitemap detection
  - Page structure analysis
  - Performance indicators

#### User Experience
- **Interactive CLI Menu**: User-friendly command-line interface
  - Step-by-step workflow
  - Colorful output with emoji support
  - Progress indicators
  - Clear error messages
  
- **Enhanced Installation**:
  - Automatic dependency detection
  - Progress bars during installation
  - Multi-distribution support (Debian, Ubuntu, Fedora, RHEL, Arch)
  - Debug mode for troubleshooting
  
- **Debug Logger**:
  - Colored console output
  - File logging with timestamps
  - Structured data logging
  - Exception tracking
  - Performance monitoring

#### Report Generation
- **Comprehensive Reports**:
  - Markdown format output
  - Organized sections
  - Timestamp and metadata
  - Detailed findings
  - Recommendations
  
#### Documentation
- Complete README with examples
- Contributing guidelines
- Code of Conduct
- Security policy
- Quick reference guide
- Logger documentation

### 🔧 Technical Details

- Python 3.8+ support
- Linux-compatible (all major distributions)
- Virtual environment support
- Modular architecture
- Error handling and recovery
- Random User-Agent rotation
- HTTP client with retry logic

### 📦 Dependencies

- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- python-whois >= 0.8.0
- dnspython >= 2.4.0
- builtwith >= 1.3.4
- wappalyzer >= 0.3.1
- colorama >= 0.4.6
- python-nmap >= 0.7.1
- validators >= 0.22.0
- lxml >= 4.9.3
- pyOpenSSL >= 23.3.0

### 🎯 Platform Support

- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ Fedora 36+
- ✅ RHEL/CentOS 8+
- ✅ Arch Linux
- ✅ Other Linux distributions with Python 3.8+

### 📖 Documentation Files

- README.md - Main documentation
- CONTRIBUTING.md - Contribution guidelines
- CODE_OF_CONDUCT.md - Community guidelines
- SECURITY.md - Security policy
- LICENSE - MIT License
- CHANGELOG.md - This file
- QUICK_REFERENCE.md - Quick commands reference
- LOGGER.md - Debug logger documentation

### 🙏 Acknowledgments

Thanks to all contributors and the open-source community for the amazing tools and libraries that made this project possible.

---

## Release Notes

### What's New in v1.0.0?

This is the first stable release of Linux Spider, a comprehensive web scanning tool designed for Linux systems. It provides an all-in-one solution for website analysis, security assessment, and technology detection.

**Key Highlights:**
- 🔍 Six specialized scanning modules
- 🎨 Beautiful CLI interface with colors
- 📊 Detailed report generation
- 🐛 Debug mode for troubleshooting
- 📦 Easy installation with automatic dependency handling
- 🔒 Security-focused design
- 📝 Comprehensive documentation

**Perfect For:**
- Security researchers
- Web developers
- System administrators
- Digital marketers
- SEO specialists
- Anyone interested in web technology analysis

**Get Started:**
```bash
git clone https://github.com/YOUR_USERNAME/linux-spider-webscaning.git
cd linux-spider-webscaning
chmod +x install.sh
./install.sh
./run.sh
```

### Breaking Changes
None (initial release)

### Deprecations
None (initial release)

### Known Issues
- Some CMS platforms besides WordPress have limited detection
- Port scanning requires root/sudo for some features
- WHOIS data may be limited for some TLDs

### Upgrade Guide
N/A (initial release)

---

[1.0.0]: https://github.com/m-alizadeh7/linux-spider-webscaning/releases/tag/v1.0.0
