"""
Linux Spider Web Scanner - Internal Debug Logger
Provides comprehensive logging and debugging capabilities
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.BLUE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.ICONS.get(levelname, '')} {levelname}{Style.RESET_ALL}"
        
        # Format the message
        return super().format(record)


class DebugLogger:
    """Enhanced logger with file and console output"""
    
    def __init__(
        self,
        name: str = "WebScanner",
        log_dir: str = "logs",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        debug_mode: bool = False
    ):
        self.name = name
        self.log_dir = Path(log_dir)
        self.debug_mode = debug_mode
        
        # Create log directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # Clear existing handlers
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level if not debug_mode else logging.DEBUG)
        console_formatter = ColoredFormatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler - main log
        log_file = self.log_dir / f"scanner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Debug file handler (only in debug mode)
        if debug_mode:
            debug_file = self.log_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            debug_handler = logging.FileHandler(debug_file, encoding='utf-8')
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(file_formatter)
            self.logger.addHandler(debug_handler)
            self.debug_file = debug_file
        else:
            self.debug_file = None
        
        self.log_file = log_file
        self.start_time = datetime.now()
        
        # Log initialization
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Logger initialized: {name}")
        self.logger.info(f"Log file: {log_file}")
        if debug_mode:
            self.logger.debug(f"Debug mode enabled")
            self.logger.debug(f"Debug file: {self.debug_file}")
        self.logger.info(f"{'='*60}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, **kwargs)
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    def section(self, title: str):
        """Log a section header"""
        separator = "━" * 60
        self.logger.info(f"\n{Fore.CYAN}{separator}{Style.RESET_ALL}")
        self.logger.info(f"{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}")
        self.logger.info(f"{Fore.CYAN}{separator}{Style.RESET_ALL}")
    
    def step(self, step_num: int, total_steps: int, message: str):
        """Log a step in a process"""
        percentage = (step_num / total_steps) * 100
        self.logger.info(
            f"{Fore.YELLOW}[Step {step_num}/{total_steps} - {percentage:.0f}%]{Style.RESET_ALL} {message}"
        )
    
    def progress(self, message: str, current: int, total: int):
        """Log progress information"""
        percentage = (current / total) * 100
        bar_length = 30
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        self.logger.info(
            f"{message}: [{Fore.CYAN}{bar}{Style.RESET_ALL}] {current}/{total} ({percentage:.1f}%)"
        )
    
    def log_dict(self, title: str, data: dict, level: str = "info"):
        """Log dictionary data in formatted way"""
        getattr(self.logger, level)(f"{title}:")
        for key, value in data.items():
            getattr(self.logger, level)(f"  {key}: {value}")
    
    def log_list(self, title: str, items: list, level: str = "info"):
        """Log list data in formatted way"""
        getattr(self.logger, level)(f"{title}:")
        for i, item in enumerate(items, 1):
            getattr(self.logger, level)(f"  {i}. {item}")
    
    def execution_time(self, operation: str):
        """Log execution time for an operation"""
        elapsed = datetime.now() - self.start_time
        self.logger.info(
            f"{Fore.MAGENTA}⏱️  {operation} completed in {elapsed.total_seconds():.2f} seconds{Style.RESET_ALL}"
        )
    
    def separator(self):
        """Log a separator line"""
        self.logger.info("-" * 60)
    
    def banner(self, text: str):
        """Log a banner with text"""
        border = "═" * (len(text) + 4)
        self.logger.info(f"\n{Fore.YELLOW}{border}{Style.RESET_ALL}")
        self.logger.info(f"{Fore.YELLOW}║ {Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.YELLOW} ║{Style.RESET_ALL}")
        self.logger.info(f"{Fore.YELLOW}{border}{Style.RESET_ALL}\n")
    
    def get_log_file_path(self) -> Path:
        """Get the current log file path"""
        return self.log_file
    
    def get_debug_file_path(self) -> Optional[Path]:
        """Get the debug file path if debug mode is enabled"""
        return self.debug_file
    
    def close(self):
        """Close all handlers"""
        elapsed = datetime.now() - self.start_time
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total execution time: {elapsed.total_seconds():.2f} seconds")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info(f"Logger closed: {self.name}")
        self.logger.info(f"{'='*60}")
        
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)


# Global logger instance
_global_logger: Optional[DebugLogger] = None


def get_logger(
    name: str = "WebScanner",
    debug_mode: bool = False,
    **kwargs
) -> DebugLogger:
    """Get or create global logger instance"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = DebugLogger(
            name=name,
            debug_mode=debug_mode,
            **kwargs
        )
    
    return _global_logger


def set_debug_mode(enabled: bool):
    """Enable or disable debug mode for global logger"""
    global _global_logger
    if _global_logger:
        _global_logger.debug_mode = enabled
        for handler in _global_logger.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.DEBUG if enabled else logging.INFO)


# Example usage
if __name__ == "__main__":
    # Test the logger
    logger = DebugLogger(debug_mode=True)
    
    logger.banner("Debug Logger Test")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.success("This is a success message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    logger.section("Testing Structured Logging")
    logger.log_dict("Configuration", {
        "mode": "debug",
        "output": "console",
        "level": "DEBUG"
    })
    
    logger.log_list("Features", [
        "Colored output",
        "File logging",
        "Debug mode",
        "Structured data"
    ])
    
    logger.section("Testing Progress")
    for i in range(1, 6):
        logger.step(i, 5, f"Processing step {i}")
    
    logger.section("Testing Progress Bar")
    import time
    for i in range(0, 101, 20):
        logger.progress("Scanning", i, 100)
        time.sleep(0.3)
    
    logger.execution_time("Test operations")
    logger.close()
