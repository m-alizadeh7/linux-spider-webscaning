# Contributing to Linux Spider Web Scanner

First off, thank you for considering contributing to Linux Spider Web Scanner! 🎉

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and explain what behavior you expected
- **Include screenshots** if possible
- **Include your environment details**: OS, Python version, etc.
- **Run with `--debug` flag** and include relevant log files

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Provide specific examples** to demonstrate the feature
- **Explain why this enhancement would be useful**

### Pull Requests

1. **Fork the repository** and create your branch from `master`
2. **Install development dependencies**: `./install.sh --debug`
3. **Make your changes**
4. **Test your changes** thoroughly
5. **Update documentation** if needed
6. **Ensure the code follows the project style**
7. **Write clear commit messages**
8. **Create a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/linux-spider-webscaning.git
cd linux-spider-webscaning

# Install dependencies
./install.sh --debug

# Activate virtual environment
source venv/bin/activate

# Make your changes
# ...

# Test your changes
python3 main.py --debug
```

### Coding Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes
- Keep functions small and focused
- Handle errors gracefully
- Use the internal logger for debugging

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add WordPress plugin detection feature

- Implement plugin enumeration
- Add version detection
- Update documentation
- Add tests

Fixes #123
```

### Testing

Before submitting a PR:

1. Test your changes with different websites
2. Run with `--debug` flag to check for errors
3. Test on different Linux distributions if possible
4. Verify all scanners work correctly
5. Check that reports are generated properly

### Documentation

- Update README.md if you change functionality
- Update LOGGER.md if you modify the logger
- Add examples for new features
- Keep documentation clear and concise

## Project Structure

```
linux-spider-webscaning/
├── main.py                 # Entry point
├── scanner/               # Scanner modules
│   ├── domain_scanner.py
│   ├── host_scanner.py
│   ├── tech_scanner.py
│   ├── cms_scanner.py
│   ├── security_scanner.py
│   └── seo_scanner.py
└── utils/                 # Utilities
    ├── logger.py          # Debug logger
    ├── http_client.py
    ├── report_generator.py
    └── helpers.py
```

## Adding New Features

### Adding a New Scanner Module

1. Create a new file in `scanner/` directory
2. Follow the existing scanner structure
3. Implement error handling
4. Use the logger for debugging
5. Update `main.py` to include your scanner
6. Update documentation

Example scanner structure:

```python
#!/usr/bin/env python3
"""
New Scanner Module
Description of what this scanner does
"""

from utils.logger import get_logger

class NewScanner:
    def __init__(self, url, logger=None):
        self.url = url
        self.logger = logger or get_logger()
        self.results = {}
    
    def scan(self):
        """Perform the scan"""
        try:
            self.logger.info(f"Starting new scan for: {self.url}")
            # Your scanning logic here
            self.logger.success("Scan completed")
            return self.results
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            return {}
```

### Adding New Utilities

1. Create or update files in `utils/` directory
2. Keep utilities generic and reusable
3. Add documentation
4. Add examples in docstrings

## Questions?

Feel free to open an issue for questions or clarifications!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You! 🎉

Your contributions make this project better for everyone!
