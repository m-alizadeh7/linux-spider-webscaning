# 🚀 Linux Spider v1.5.0 - Quick Start Guide

## Quick Installation

```bash
git clone https://github.com/m-alizadeh7/linux-spider-webscaning.git
cd linux-spider-webscaning
chmod +x install.sh
./install.sh
```

## Quick Run

```bash
./run.sh
# or
source venv/bin/activate && python3 main.py
```

## Debug Mode

```bash
python3 main.py --debug
```

---

## 📋 Command Reference

### Installation

| Command | Description |
|---------|-------------|
| `./install.sh` | Standard installation |
| `./install.sh --debug` | Installation with debug logging |

### Running

| Command | Description |
|---------|-------------|
| `./run.sh` | Quick start |
| `python3 main.py` | Interactive mode |
| `python3 main.py --debug` | Debug mode |
| `python3 main.py --version` | Show version |
| `python3 main.py --help` | Show help |

---

## 🎯 Scan Modules (v1.5.0)

| # | Module | Description |
|---|--------|-------------|
| 1 | Domain Information | WHOIS, DNS records, expiration |
| 2 | Hosting & Infrastructure | Server, SSL, headers |
| 3 | Technology Detection | CMS, frameworks, libraries |
| 4 | CMS Analysis | WordPress/Joomla deep scan |
| 5 | Security Scanning | Vulnerabilities, ports |
| 6 | SEO Analysis | Meta tags, content, links |
| 7 | **Content & Products** | Articles, products, sitemaps |

---

## 📊 Report Sections (12 Total)

| # | Section | New in v1.5.0 |
|---|---------|---------------|
| 1 | Domain Information | |
| 2 | Hosting & Infrastructure | |
| 3 | Technology Stack | |
| 4 | CMS Analysis | |
| 5 | Security Analysis | |
| 6 | SEO Analysis | |
| 7 | Articles & Content | ✓ NEW |
| 8 | Products Analysis | ✓ NEW |
| 9 | Schema.org Validation | ✓ NEW |
| 10 | Technical SEO | ✓ NEW |
| 11 | On-Page SEO | ✓ NEW |
| 12 | Summary & Recommendations | |

---

## 🔍 Common Workflows

### Full Website Scan

1. Start: `./run.sh`
2. Enter target URL (e.g., `example.com`)
3. Select option `8` (Run All)
4. Wait for scan completion
5. Check report in `reports/` directory

### SEO-Focused Scan

1. Start: `python3 main.py`
2. Enter URL
3. Toggle modules: `6`, `7` (SEO + Content)
4. Select `9` to continue
5. Review SEO scores and recommendations

### Security Audit

1. Start: `python3 main.py`
2. Enter URL
3. Toggle modules: `5` (Security)
4. Select `9` to continue
5. Check security score and vulnerabilities

### E-commerce Analysis

1. Start: `python3 main.py`
2. Enter store URL
3. Toggle modules: `4`, `7` (CMS + Content)
4. Select `9` to continue
5. View product catalog and schema validation

---

## 🤖 AI Analysis Setup

### Configuration

Create `config/ai_services.txt`:

```
gemini=YOUR_GEMINI_API_KEY
openai=YOUR_OPENAI_API_KEY
openrouter=YOUR_OPENROUTER_API_KEY
```

### Analysis Types

| Type | Use Case |
|------|----------|
| Own Site | Optimization recommendations |
| Competitor | Market analysis |

---

## 📈 Score Interpretation

| Score | Grade | Action |
|-------|-------|--------|
| 90-100 | 🟢 Excellent | Maintain |
| 70-89 | 🟡 Good | Minor improvements |
| 50-69 | 🟠 Fair | Priority fixes needed |
| 0-49 | 🔴 Poor | Critical issues |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `python3-venv not found` | `sudo apt install python3.x-venv` |
| `Permission denied` | `chmod +x install.sh run.sh` |
| `Module not found` | `pip install -r requirements.txt` |
| `Gemini 403` | API auto-fallback to 2.0 model |

### Debug Logs

Check `logs/` directory for:
- `scanner_YYYYMMDD_HHMMSS.log` - General logs
- `debug_YYYYMMDD_HHMMSS.log` - Debug mode logs

---

## 📁 Output Files

### Reports Location

```
reports/scan_<domain>_<timestamp>.md
reports/ai_analysis_<domain>_<type>_<timestamp>.md
```

### Example Report Names

```
scan_example.com_20251219_143022.md
ai_analysis_example.com_own_20251219_143522.md
```

---

## 🔗 Useful Links

- [README.md](README.md) - Full documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guide
- [LICENSE](LICENSE) - MIT License

---

<p align="center">
  <strong>Linux Spider v1.5.0</strong><br>
  Advanced Web Intelligence Platform
</p>
