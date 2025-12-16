## 🚀 Installation & Quick Start

### Quick Install
```bash
git clone https://github.com/YOUR_USERNAME/linux-spider-webscaning.git
cd linux-spider-webscaning
chmod +x install.sh
./install.sh
```

### Quick Run
```bash
./run.sh
# or
source venv/bin/activate && python3 main.py
```

### Debug Mode
```bash
python3 main.py --debug
```

---

## 📝 Command Reference

### Installation Commands
```bash
# Standard installation
./install.sh

# Debug installation
./install.sh --debug

# Manual installation
sudo apt-get install python3 python3-pip python3-venv nmap
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Scanner
```bash
# Activate virtual environment
source venv/bin/activate

# Run interactive mode
python3 main.py

# Run with debug logging
python3 main.py --debug

# Show version
python3 main.py --version

# Show help
python3 main.py --help

# Quick run script
./run.sh
```

### Common Workflows

#### Full Website Scan
1. Start the tool: `./run.sh`
2. Enter target URL (e.g., `https://example.com`)
3. Select all modules (press Enter for all)
4. Wait for scan completion
5. Check report in `reports/` directory

#### Security-Focused Scan
1. Start: `python3 main.py`
2. Enter URL
3. Select modules: `4,5` (Security, SEO)
4. Review security findings in report

#### CMS Analysis
1. Start: `python3 main.py`
2. Enter WordPress site URL
3. Select module: `4` (CMS Scanner)
4. Check for plugins and themes

---

## 🔍 Module Reference

### 1. Domain Scanner
**What it does**: Analyzes domain registration and ownership
- WHOIS information
- Registration dates
- Expiration dates
- Registrar details

**Best for**: Domain research, expiration monitoring

### 2. Host Scanner
**What it does**: Examines hosting infrastructure
- DNS records (A, AAAA, MX, NS, TXT, CNAME)
- IP address resolution
- Server identification
- Open ports

**Best for**: Infrastructure analysis, migration planning

### 3. Technology Scanner
**What it does**: Identifies web technologies
- Web frameworks
- Programming languages
- JavaScript libraries
- Server software

**Best for**: Technology stack analysis, competitor research

### 4. CMS Scanner
**What it does**: Detects and analyzes CMS platforms
- CMS identification (WordPress focus)
- Version detection
- Plugin enumeration
- Theme identification

**Best for**: WordPress sites, plugin audits

### 5. Security Scanner
**What it does**: Checks security configurations
- SSL/TLS validation
- Security headers
- HTTP security
- Common vulnerabilities

**Best for**: Security audits, compliance checks

### 6. SEO Scanner
**What it does**: Analyzes SEO factors
- Meta tags
- robots.txt
- Sitemap
- Page structure

**Best for**: SEO audits, optimization planning

---

## 📂 File Locations

### Configuration
- No configuration file needed (uses defaults)

### Logs
- `logs/debug_YYYYMMDD_HHMMSS.log` - Debug logs (when using --debug)
- `install_debug.log` - Installation logs (when using --debug)

### Reports
- `reports/scan_<domain>_<timestamp>.md` - Scan reports

### Source Code
- `scanner/` - Scanner modules
- `utils/` - Utility functions
- `main.py` - Main entry point

---

## 🐛 Troubleshooting Quick Reference

### Installation Issues
```bash
# Permission denied
chmod +x install.sh run.sh

# Python venv not found
sudo apt-get install python3.10-venv  # Adjust version

# Nmap not found
sudo apt-get install nmap

# Debug installation issues
./install.sh --debug
cat install_debug.log
```

### Runtime Issues
```bash
# Enable debug mode
python3 main.py --debug

# Check logs
ls -la logs/
cat logs/debug_*.log

# Verify virtual environment
which python3
pip list

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Common Errors

**"Module not found"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"Permission denied: nmap"**
```bash
# Some nmap features require sudo
sudo python3 main.py  # Not recommended
# Or run without port scanning
```

**"WHOIS lookup failed"**
- Some domains don't have public WHOIS data
- Check domain spelling
- Try again later

**"Connection timeout"**
- Check internet connection
- Verify target URL is accessible
- Target might have rate limiting

---

## 💡 Tips & Best Practices

### Performance
- Run on a server with good bandwidth for faster scans
- Use debug mode only when troubleshooting
- Close other network-intensive applications

### Accuracy
- Always use full URLs with protocol (https://)
- Wait for scans to complete (don't interrupt)
- Some results depend on target's response

### Security
- Always get permission before scanning
- Don't scan production sites aggressively
- Review reports before sharing (may contain sensitive data)

### Report Management
```bash
# View latest report
ls -t reports/ | head -1
cat reports/$(ls -t reports/ | head -1)

# Clean old reports
find reports/ -name "*.md" -mtime +30 -delete

# Archive reports
tar -czf reports_backup.tar.gz reports/
```

---

## 🔗 Quick Links

- [Full Documentation](README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Logger Documentation](LOGGER.md)

---

## 📞 Getting Help

1. **Check documentation**: README.md
2. **Enable debug mode**: `python3 main.py --debug`
3. **Check logs**: `logs/debug_*.log`
4. **Search issues**: GitHub Issues
5. **Ask for help**: Open a new issue with debug logs

---

**Last Updated**: December 2025
