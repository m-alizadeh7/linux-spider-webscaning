"""
Version information for Linux Spider Web Scanner
"""

__version__ = "1.0.0"
__author__ = "Linux Spider Contributors"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Linux Spider Contributors"
__url__ = "https://github.com/YOUR_USERNAME/linux-spider-webscaning"
__description__ = "A comprehensive web scanning tool for Linux systems"

VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "release": "stable",
    "build": "20251217"
}

def get_version():
    """Return the version string"""
    return __version__

def get_version_info():
    """Return detailed version information"""
    return VERSION_INFO
