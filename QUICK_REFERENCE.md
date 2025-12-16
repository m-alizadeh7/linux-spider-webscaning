# 📋 Quick Reference - Linux Spider Web Scanner v2.0

## 🚀 Quick Start

```bash
# Install
./install.sh

# Run
source venv/bin/activate
python3 main.py

# Or use shortcut
./run.sh
```

## 🔧 Installation Commands

```bash
# Normal installation
./install.sh

# Debug installation (shows detailed logs)
./install.sh --debug

# Check installation log
cat install_debug.log
```

## 💻 Running Commands

```bash
# Normal mode
python3 main.py

# Debug mode (detailed logging)
python3 main.py --debug

# Show help
python3 main.py --help

# Show version
python3 main.py --version
```

## 📂 Directory Structure

```
linux-spider-webscaning/
├── install.sh          # Enhanced installer
├── run.sh             # Quick run script
├── main.py            # Main program
├── requirements.txt   # Dependencies
├── scanner/           # Scanner modules
├── utils/            # Utilities
│   └── logger.py     # Debug logger
├── reports/          # Scan reports
└── logs/             # Debug logs (--debug mode)
```

## 🎨 Installation Features

| Feature | Description |
|---------|-------------|
| Progress Bars | Visual installation progress |
| Color Output | Green (success), Red (error), Yellow (warning) |
| Auto-Install | Installs missing dependencies |
| Debug Mode | `./install.sh --debug` |
| Error Recovery | Clear error messages |
| Multi-Distro | Ubuntu, Debian, Fedora, RHEL, Arch |

## 🔍 Debug Logger Features

| Feature | Usage |
|---------|-------|
| Enable Debug | `python3 main.py --debug` |
| Log Files | `logs/scanner_*.log` |
| Debug Files | `logs/debug_*.log` |
| Color Output | Yes (all log levels) |
| Progress Bars | Built-in |
| Time Tracking | Automatic |

## 📊 Log Levels

| Level | Icon | Color | When to Use |
|-------|------|-------|-------------|
| DEBUG | 🔍 | Cyan | Development/troubleshooting |
| INFO | ℹ️ | Blue | General information |
| WARNING | ⚠️ | Yellow | Potential issues |
| ERROR | ❌ | Red | Errors occurred |
| CRITICAL | 🔥 | Red+BG | Critical failures |

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Installation fails | `./install.sh --debug` |
| Python3-venv missing | Auto-installed by script |
| Permission denied | `chmod +x install.sh run.sh` |
| Virtual env fails | Script auto-fixes |
| Package conflicts | Fixed in requirements.txt |

## 📝 Log File Locations

| File | Purpose |
|------|---------|
| `install_debug.log` | Installation debugging |
| `logs/scanner_*.log` | Main runtime logs |
| `logs/debug_*.log` | Detailed debug logs |
| `reports/scan_*.md` | Scan reports |

## ⚡ Quick Debugging

```bash
# Problem during installation?
./install.sh --debug
cat install_debug.log

# Problem during runtime?
python3 main.py --debug
cat logs/scanner_*.log

# Check latest log
ls -lt logs/ | head -n 2
```

## 🎯 Common Commands

```bash
# Full installation with debug
./install.sh --debug

# Activate environment
source venv/bin/activate

# Run with debug
python3 main.py --debug

# Check logs
ls -lh logs/
cat logs/scanner_*.log

# View reports
ls -lh reports/
cat reports/scan_*.md

# Deactivate environment
deactivate
```

## 📚 Documentation Files

| File | Contents |
|------|----------|
| `README.md` | Main documentation |
| `LOGGER.md` | Logger usage guide |
| `IMPROVEMENTS.md` | Version 2.0 changes |
| `QUICK_REFERENCE.md` | This file |

## 🎉 Key Improvements in v2.0

✅ Fixed installation errors
✅ Added progress bars
✅ Added debug mode
✅ Created internal logger
✅ Enhanced error messages
✅ Auto-dependency installation
✅ Multi-distribution support
✅ Comprehensive logging
✅ Better documentation
✅ Command line arguments

## 💡 Tips

1. **Always use debug mode for troubleshooting**
   ```bash
   python3 main.py --debug
   ```

2. **Check logs when something fails**
   ```bash
   cat logs/scanner_*.log
   ```

3. **Installation problems? Use debug install**
   ```bash
   ./install.sh --debug
   ```

4. **Keep virtual environment activated**
   ```bash
   source venv/bin/activate
   ```

5. **Reports saved automatically**
   ```bash
   ls reports/
   ```

## 🔗 Quick Links

- Installation: See `README.md`
- Logger Usage: See `LOGGER.md`
- What's New: See `IMPROVEMENTS.md`
- Issues: Check `install_debug.log` or `logs/`

## 📞 Getting Help

1. Check error message
2. Enable debug mode: `--debug`
3. Check log files in `logs/`
4. Review documentation
5. Check `install_debug.log` for installation issues

---

**Version**: 2.0  
**Last Updated**: December 17, 2025  
**Status**: ✅ All features working
