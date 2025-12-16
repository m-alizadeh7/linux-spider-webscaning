# 🕷️ Linux Spider - Web Scanning Tool v2.0

A comprehensive web scanning tool for Linux with enhanced debugging capabilities and attractive installation process. Performs detailed analysis of websites including domain information, hosting details, technologies, CMS detection, security, and SEO scanning.

## ✨ Features

- **Domain Information**: Registration date, renewal date, expiration date
- **Hosting Information**: Server details, IP addresses, DNS records
- **Technology Detection**: Identify frameworks, libraries, and technologies used
- **CMS Scanning**: Detect CMS platforms (especially WordPress), plugins, and themes
- **Security Scanning**: Check for common security issues and vulnerabilities
- **SEO Analysis**: Analyze SEO-related factors and website structure
- **Comprehensive Reports**: Generate detailed reports in TXT/MD format
- **🆕 Internal Debug Logger**: Advanced logging with colored output and file logging
- **🆕 Enhanced Installation**: Beautiful progress bars and detailed error reporting
- **🆕 Debug Mode**: Run with `--debug` flag for detailed troubleshooting

## 📋 Requirements

- Linux operating system (compatible with all distributions)
- Python 3.8 or higher
- nmap (for port scanning)
- python3-venv (automatically installed by the installer)

## 🚀 Quick Installation

### Automatic Installation (Recommended)

Simply run the enhanced installation script:

```bash
chmod +x install.sh
./install.sh
```

The installer will:
- ✅ Check all system requirements
- ✅ Automatically install missing dependencies
- ✅ Create and configure virtual environment
- ✅ Install all Python packages
- ✅ Show beautiful progress bars
- ✅ Provide detailed error messages

### Debug Installation

If you encounter any issues during installation, run with debug mode:

```bash
./install.sh --debug
```

This will:
- Show detailed debug information
- Log everything to `install_debug.log`
- Help diagnose any installation problems

### Manual Installation

If you prefer manual installation:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nmap

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## 💻 Usage

### Basic Usage

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run the scanner
python3 main.py

# Or use the run script
./run.sh
```

### Debug Mode

For detailed logging and troubleshooting:

```bash
python3 main.py --debug
```

Debug mode features:
- 📝 Detailed console output with debug messages
- 📋 Comprehensive log files in `logs/` directory
- 🎨 Colored output for better readability
- ⏱️ Execution time tracking
- 🔍 Step-by-step process logging

### Interactive Menu

Follow the interactive menu to:
1. Enter the target website URL
2. Select scanning modules
3. View progress and results
4. Generate comprehensive report

### Command Line Options

```bash
python3 main.py --help      # Show help message
python3 main.py --version   # Show version
python3 main.py --debug     # Enable debug mode
```

## Report Output

Reports are saved in the `reports/` directory with the following naming format:
```
scan_<domain>_<timestamp>.md
```

Each report includes:
- Scan metadata (date, time, target)
- Domain information
- Hosting and infrastructure details
- Detected technologies
- CMS analysis (if applicable)
- Security findings
- SEO metrics
- Recommendations

## 📁 Project Structure

```
linux-spider-webscaning/
├── main.py                    # Main entry point with interactive menu
├── install.sh                 # Enhanced installation script with debug mode
├── run.sh                     # Quick run script
├── requirements.txt           # Python dependencies
├── scanner/                   # Scanner modules
│   ├── __init__.py
│   ├── domain_scanner.py      # Domain information scanning
│   ├── host_scanner.py        # Hosting and infrastructure scanning
│   ├── tech_scanner.py        # Technology detection
│   ├── cms_scanner.py         # CMS detection (WordPress focus)
│   ├── security_scanner.py    # Security scanning
│   └── seo_scanner.py         # SEO analysis
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── http_client.py         # HTTP client with random User-Agent
│   ├── report_generator.py    # Report generation
│   ├── logger.py              # 🆕 Internal debug logger with colored output
│   └── helpers.py             # Helper functions
├── reports/                   # Generated scan reports
└── logs/                      # 🆕 Debug and execution logs (created in debug mode)
```

## 🎯 Features in Detail

### 🆕 Enhanced Installation Script

The new installation script provides:

- **Visual Progress Bars**: See installation progress in real-time
- **Colored Output**: Easy-to-read colored messages for success, warnings, and errors
- **Automatic Dependency Detection**: Automatically detects and installs missing system packages
- **Distribution Detection**: Supports Debian/Ubuntu, Fedora, RHEL/CentOS, and Arch Linux
- **Debug Mode**: Run `./install.sh --debug` for detailed logging
- **Error Recovery**: Clear error messages with suggestions for fixing issues
- **Smart Virtual Environment Management**: Cleans old environments and creates fresh ones

### 🆕 Internal Debug Logger

The new logger utility provides:

- **Colored Console Output**: Different colors for different log levels
- **File Logging**: Automatic log file generation with timestamps
- **Debug Mode**: Enable with `--debug` flag for detailed diagnostics
- **Structured Logging**: Log dictionaries, lists, and complex data structures
- **Progress Tracking**: Built-in progress bars and step counters
- **Execution Time Tracking**: Monitor performance of operations
- **Exception Handling**: Automatic exception logging with stack traces

### User-Agent Randomization

The tool uses random User-Agent headers to avoid detection and blocking.

### Error Handling

If any module fails, the tool continues scanning other modules and displays appropriate messages without crashing.

### Portability

The project is designed to be easily portable across different Linux systems. Simply install dependencies and run.

## 🐛 Troubleshooting

### Installation Issues

1. **Python3-venv not found**: 
   ```bash
   sudo apt-get install python3.10-venv  # Replace 3.10 with your Python version
   ```

2. **Permission denied**:
   ```bash
   chmod +x install.sh
   chmod +x run.sh
   ```

3. **Package installation fails**:
   ```bash
   ./install.sh --debug  # Run in debug mode to see detailed error messages
   ```

### Runtime Issues

1. **Enable debug mode** to see detailed logs:
   ```bash
   python3 main.py --debug
   ```

2. **Check log files** in the `logs/` directory (created in debug mode)

3. **Check installation log**: `install_debug.log` (if you ran installer with --debug)

## 📝 Changelog

### Version 2.0 (Current)
- ✨ Added enhanced installation script with progress bars
- ✨ Added internal debug logger with colored output
- ✨ Added `--debug` command line flag
- ✨ Added comprehensive error handling and logging
- ✨ Improved installation process with better error messages
- ✨ Added automatic dependency detection and installation
- 🐛 Fixed `builtwith` package version compatibility
- 🐛 Fixed virtual environment creation issues
- 📚 Enhanced documentation with troubleshooting section

### Version 1.0
- Initial release with basic scanning functionality

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 👨‍💻 Author

Developed with ❤️ for the Linux community
