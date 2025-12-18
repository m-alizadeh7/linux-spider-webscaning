# 🕷️ Linux Spider - Advanced Web Intelligence Platform

[![Version](https://img.shields.io/badge/version-1.5.0-blue.svg)](https://github.com/m-alizadeh7/linux-spider-webscaning)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.org/)

A comprehensive web intelligence and SEO analysis platform for Linux. Performs deep analysis of websites including domain information, hosting infrastructure, technology detection, CMS analysis, security auditing, SEO evaluation, content extraction, and AI-powered reporting.

---

## ✨ Features Overview

| Module | Description |
|--------|-------------|
| 📡 **Domain Scanner** | WHOIS, DNS records, domain age, expiration alerts |
| 🖥️ **Host Scanner** | Server info, SSL/TLS, security headers, response metrics |
| 🔧 **Technology Detection** | CMS, frameworks, libraries, meta generators |
| 📦 **CMS Analysis** | WordPress deep scan, plugins, themes, vulnerabilities |
| 🔒 **Security Scanner** | Headers, SSL grading, sensitive files, port scanning |
| 📊 **SEO Analysis** | Meta tags, headings, content analysis, performance |
| 📝 **Content Scanner** | Article extraction, product detection, sitemap parsing |
| ⚙️ **Technical SEO** | Canonical, robots.txt, sitemap, mobile-friendliness |
| 📄 **On-Page SEO** | Title, meta description, heading hierarchy, content quality |
| 🔍 **Schema Validator** | JSON-LD, Microdata, RDFa validation |
| 🤖 **AI Analysis** | Expert reports via Gemini, OpenAI, OpenRouter |

---

## 🆕 What's New in v1.5.0

### Content & SEO Intelligence Suite
- **Article Extractor**: Automatic detection and extraction of blog posts and articles
- **Product Extractor**: E-commerce product catalog detection with pricing
- **Sitemap Discovery**: Parse XML sitemaps with URL categorization
- **RSS/Atom Discovery**: Feed detection and content sampling

### Advanced SEO Modules
- **Technical SEO Analysis**: HTTPS, canonical, robots.txt, sitemap, mobile viewport, TTFB
- **On-Page SEO Analysis**: Title optimization, meta description, heading hierarchy, content quality
- **Schema.org Validator**: Validate structured data (JSON-LD, Microdata, RDFa)

### Enhanced Reporting
- **12-Section Reports**: Comprehensive markdown reports with all scan data
- **Score Grades**: Visual grading system (🟢 Excellent → 🔴 Needs Improvement)
- **Issues & Recommendations**: Prioritized fixes with impact levels
- **Bilingual AI Reports**: Professional analysis in English and Persian

### Bug Fixes & Improvements
- Fixed NoneType errors in report generation
- Improved Gemini API fallback (2.5 → 2.0 model)
- Better error handling throughout

---

## 📋 Requirements

| Requirement | Version |
|-------------|---------|
| Linux OS | Any distribution |
| Python | 3.8+ |
| nmap | Latest |
| pip | Latest |

### Python Dependencies

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
python-whois>=0.8.0
dnspython>=2.4.0
python-nmap>=0.7.1
builtwith>=1.3.13
colorama>=0.4.6
tldextract>=5.1.0
validators>=0.22.0
extruct>=0.16.0
feedparser>=6.0.10
```

---

## 🚀 Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/m-alizadeh7/linux-spider-webscaning.git
cd linux-spider-webscaning
chmod +x install.sh
./install.sh
```

### Debug Installation

```bash
./install.sh --debug
```

### Manual Installation

```bash
# System dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nmap

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Python packages
pip install -r requirements.txt
```

---

## 💻 Usage

### Running the Scanner

```bash
# Activate environment
source venv/bin/activate

# Run scanner
python3 main.py

# Or use the run script
./run.sh
```

### Debug Mode

```bash
python3 main.py --debug
```

### Command Line Options

```bash
python3 main.py --help      # Show help
python3 main.py --version   # Show version (1.5.0)
python3 main.py --debug     # Enable debug logging
```

---

## 🎯 Scan Modules

### Module Selection Menu

```
[✓] 1. Domain Information
[✓] 2. Hosting & Infrastructure  
[✓] 3. Technology Detection
[✓] 4. CMS Analysis
[✓] 5. Security Scanning
[✓] 6. SEO Analysis
[✓] 7. Content & Products (NEW)

8. Run All (Default)
9. Continue with selection
```

---

## 📊 Report Structure (12 Sections)

| # | Section | Content |
|---|---------|---------|
| 1 | Domain Information | WHOIS, DNS records, IP addresses |
| 2 | Hosting & Infrastructure | Server, SSL/TLS, security headers |
| 3 | Technology Stack | CMS, frameworks, libraries, generators |
| 4 | CMS Analysis | WordPress/Joomla/Drupal deep scan |
| 5 | Security Analysis | Score, headers, vulnerabilities, ports |
| 6 | SEO Analysis | Meta tags, headings, content, links |
| 7 | Articles & Content | Sitemap URLs, RSS feeds, articles |
| 8 | Products Analysis | E-commerce products, pricing |
| 9 | Schema.org Validation | Structured data, validity rate |
| 10 | Technical SEO | HTTPS, canonical, robots, sitemap |
| 11 | On-Page SEO | Title, description, headings, images |
| 12 | Summary & Recommendations | All scores, overall grade, actions |

---

## 📁 Project Structure

```
linux-spider-webscaning/
├── main.py                      # Main entry point
├── version.py                   # Version info (1.5.0)
├── install.sh                   # Installation script
├── run.sh                       # Quick run script
├── requirements.txt             # Python dependencies
│
├── scanner/                     # Scanner modules
│   ├── domain_scanner.py        # Domain & WHOIS
│   ├── host_scanner.py          # Hosting & SSL
│   ├── tech_scanner.py          # Technology detection
│   ├── cms_scanner.py           # CMS analysis
│   ├── security_scanner.py      # Security scanning
│   ├── seo_scanner.py           # SEO analysis
│   ├── discovery_scanner.py     # robots.txt & sitemap
│   ├── content_scanner.py       # Content orchestrator
│   │
│   ├── content/                 # Content extraction
│   │   ├── article_extractor.py # Article detection
│   │   ├── product_extractor.py # E-commerce products
│   │   ├── sitemap_discovery.py # XML sitemap parsing
│   │   ├── rss_discovery.py     # RSS/Atom feeds
│   │   └── url_sampler.py       # URL sampling
│   │
│   ├── seo/                     # SEO modules
│   │   ├── technical.py         # Technical SEO checks
│   │   ├── onpage.py            # On-page SEO analysis
│   │   └── schema_validator.py  # Schema.org validation
│   │
│   └── providers/               # External integrations
│       └── builtwith_provider.py
│
├── utils/                       # Utility modules
│   ├── http_client.py           # HTTP client
│   ├── report_generator.py      # Markdown report generator
│   ├── ai_reporter.py           # AI analysis (Gemini/OpenAI)
│   ├── logger.py                # Debug logger
│   └── helpers.py               # Helper functions
│
├── config/                      # Configuration
│   ├── ai_services.txt          # API keys (not in git)
│   └── prompts/                 # AI prompts
│       └── ai_analysis_prompt.txt
│
├── reports/                     # Generated reports
└── logs/                        # Debug logs
```

---

## 🤖 AI Analysis

### Supported Providers

| Provider | Models | Configuration |
|----------|--------|---------------|
| **Google Gemini** | gemini-2.0-flash, gemini-2.5-flash | API key in config |
| **OpenAI** | gpt-4, gpt-3.5-turbo | API key in config |
| **OpenRouter** | Various models | API key in config |

### Configuration

Create `config/ai_services.txt`:

```
gemini=YOUR_GEMINI_API_KEY
openai=YOUR_OPENAI_API_KEY
openrouter=YOUR_OPENROUTER_API_KEY
```

### Analysis Types

- **Own Site Analysis**: Optimization recommendations for your website
- **Competitor Analysis**: Competitive intelligence and market positioning

---

## 🔍 Example Output

### Quick Summary

```
═══════════════════════════════════════════════════════════════
                    QUICK SUMMARY
═══════════════════════════════════════════════════════════════

Security Score: 45/100
SEO Score: 97/100
Technical SEO Score: 81/100
On-Page SEO Score: 95/100
CMS Detected: WordPress
HTTPS: ✗ Not Enabled
Articles Found: 12
Products Found: 10
Schema.org Validation: 5/7 valid
```

### Score Grades

| Score | Grade | Emoji |
|-------|-------|-------|
| 90-100 | Excellent | 🟢 |
| 70-89 | Good | 🟡 |
| 50-69 | Fair | 🟠 |
| 0-49 | Needs Improvement | 🔴 |

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `python3-venv not found` | `sudo apt install python3.x-venv` |
| `Permission denied` | `chmod +x install.sh run.sh` |
| `Module not found` | `pip install -r requirements.txt` |
| `Gemini 403 error` | API automatically falls back to 2.0 model |

### Debug Mode

```bash
python3 main.py --debug
```

Check logs in `logs/` directory for detailed diagnostics.

---

## 🗺️ Roadmap

- [ ] Subdomain enumeration
- [ ] Parallel multi-URL scanning
- [ ] Export to JSON/CSV/HTML
- [ ] Web dashboard interface
- [ ] Docker container
- [ ] API endpoint scanning
- [ ] Lighthouse integration
- [ ] Core Web Vitals metrics

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/m-alizadeh7/linux-spider-webscaning/issues)
- **Discussions**: [GitHub Discussions](https://github.com/m-alizadeh7/linux-spider-webscaning/discussions)

---

## ⭐ Star History

If you find this project useful, please give it a star!

---

**⚠️ Disclaimer**: Always ensure you have proper authorization before scanning any website. This tool is intended for legitimate security testing, SEO analysis, and research purposes only.

---

<p align="center">
  Developed with ❤️ for the Linux community<br>
  <strong>Linux Spider v1.5.0</strong>
</p>
