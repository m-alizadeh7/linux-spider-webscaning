# Debug Logger Documentation

## Overview

The internal debug logger provides comprehensive logging capabilities with colored console output and file logging for the Linux Spider Web Scanner.

## Features

- **Colored Console Output**: Different colors for different log levels
- **File Logging**: Automatic log file generation with timestamps
- **Debug Mode**: Detailed logging for troubleshooting
- **Structured Data Logging**: Log dictionaries and lists in formatted way
- **Progress Tracking**: Built-in progress bars and step counters
- **Execution Time Tracking**: Monitor performance of operations
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Usage

### Basic Usage

```python
from utils.logger import get_logger

# Get logger instance
logger = get_logger(debug_mode=True)

# Log messages
logger.debug("Debug message")
logger.info("Info message")
logger.success("Success message")
logger.warning("Warning message")
logger.error("Error message")
```

### Advanced Features

#### Section Headers
```python
logger.section("Database Operations")
# Outputs a formatted section header
```

#### Progress Tracking
```python
# Step-by-step progress
logger.step(1, 5, "Loading configuration")
logger.step(2, 5, "Connecting to database")

# Progress bar
logger.progress("Scanning", 50, 100)
# Outputs: Scanning: [███████████████░░░░░░░░░░░░░░░] 50/100 (50.0%)
```

#### Structured Data
```python
# Log dictionary
config = {"host": "localhost", "port": 8080}
logger.log_dict("Configuration", config)

# Log list
items = ["item1", "item2", "item3"]
logger.log_list("Items", items)
```

#### Banners
```python
logger.banner("Installation Complete")
# Outputs a formatted banner with the text
```

#### Execution Time
```python
logger.execution_time("Data processing")
# Outputs: ⏱️  Data processing completed in X.XX seconds
```

#### Exception Logging
```python
try:
    # Some code that might fail
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")
    # Automatically logs the exception with stack trace
```

## Configuration

### Creating a Logger

```python
from utils.logger import DebugLogger

logger = DebugLogger(
    name="MyApp",           # Logger name
    log_dir="logs",         # Log directory
    console_level=logging.INFO,  # Console log level
    file_level=logging.DEBUG,    # File log level
    debug_mode=True         # Enable debug mode
)
```

### Using Global Logger

```python
from utils.logger import get_logger, set_debug_mode

# Get global logger
logger = get_logger(debug_mode=True)

# Change debug mode later
set_debug_mode(True)
```

## Log Files

### File Structure

When debug mode is enabled, the logger creates two files:

1. **Main Log File**: `logs/scanner_YYYYMMDD_HHMMSS.log`
   - Contains all log messages
   - Includes timestamps and function names
   - Human-readable format

2. **Debug Log File**: `logs/debug_YYYYMMDD_HHMMSS.log`
   - Created only in debug mode
   - Contains detailed debug information
   - Includes line numbers

### Log Format

```
YYYY-MM-DD HH:MM:SS - LoggerName - LEVEL - function:line - message
```

Example:
```
2025-12-17 00:03:15 - WebScanner - INFO - scan_website:45 - Starting scan for example.com
```

## Log Levels

| Level    | Icon | Color  | Use Case                           |
|----------|------|--------|------------------------------------|
| DEBUG    | 🔍   | Cyan   | Detailed debugging information     |
| INFO     | ℹ️    | Blue   | General informational messages     |
| WARNING  | ⚠️    | Yellow | Warning messages                   |
| ERROR    | ❌   | Red    | Error messages                     |
| CRITICAL | 🔥   | Red/BG | Critical errors that stop execution|

## Examples

### Example 1: Basic Logging

```python
from utils.logger import get_logger

logger = get_logger()

logger.info("Application started")
logger.success("Configuration loaded")
logger.warning("Using default settings")
logger.error("Connection failed")
```

### Example 2: Scanning Progress

```python
logger.banner("Web Scanning Started")
logger.section("Domain Information")

for i, domain in enumerate(domains, 1):
    logger.step(i, len(domains), f"Scanning {domain}")
    # Perform scan
    logger.success(f"Completed scanning {domain}")

logger.execution_time("Domain scanning")
```

### Example 3: Error Handling

```python
try:
    logger.info("Connecting to server...")
    response = connect_to_server()
    logger.success("Connected successfully")
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    logger.debug(f"Server details: {server_config}")
except Exception as e:
    logger.exception("Unexpected error occurred")
```

### Example 4: Configuration Logging

```python
logger.section("Application Configuration")

config = {
    "mode": "production",
    "host": "0.0.0.0",
    "port": 8080,
    "debug": False
}

logger.log_dict("Settings", config)

features = [
    "Auto-update",
    "Background scanning",
    "Report generation"
]

logger.log_list("Enabled Features", features)
```

## Best Practices

1. **Always Close Logger**: Call `logger.close()` when done
2. **Use Appropriate Levels**: DEBUG for development, INFO for production
3. **Enable Debug Mode for Troubleshooting**: Use `--debug` flag
4. **Check Log Files**: Review log files for detailed information
5. **Use Structured Logging**: Log dictionaries and lists for complex data
6. **Track Progress**: Use progress bars for long-running operations
7. **Log Exceptions**: Always log exceptions with stack traces

## Integration with Main Application

The logger is integrated into `main.py`:

```bash
# Run with debug mode
python3 main.py --debug

# This will:
# - Enable detailed console output
# - Create log files in logs/ directory
# - Show execution time for operations
# - Log all debug information
```

## Troubleshooting

### Logger Not Creating Files

Check that the `logs/` directory exists or can be created:
```bash
mkdir -p logs
chmod 755 logs
```

### No Colored Output

Make sure `colorama` is installed:
```bash
pip install colorama
```

### Log Files Too Large

Adjust log levels:
```python
logger = DebugLogger(
    console_level=logging.WARNING,  # Only warnings and errors
    file_level=logging.INFO          # Info and above to file
)
```

## Performance Considerations

- File logging has minimal performance impact
- Debug mode adds ~5-10% overhead
- Use INFO level in production for optimal performance
- Debug mode is recommended for development and troubleshooting

## Summary

The debug logger provides a comprehensive logging solution with:
- ✅ Colored output for easy reading
- ✅ File logging for persistence
- ✅ Multiple log levels
- ✅ Progress tracking
- ✅ Structured data logging
- ✅ Exception handling
- ✅ Execution time tracking

Perfect for both development and production use!
