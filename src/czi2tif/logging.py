"""Centralized logging configuration for czi2tif application."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
    file_output: bool = False,
    quiet: bool = False
) -> logging.Logger:
    """
    Set up centralized logging for the czi2tif application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None and file_output=True, uses default location
        console_output: Whether to output logs to console
        file_output: Whether to output logs to file
        quiet: If True, completely disable all logging
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("czi2tif")
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # If quiet mode, disable all logging
    if quiet:
        logger.setLevel(logging.CRITICAL + 1)  # Set level higher than CRITICAL to disable all
        logger.propagate = False
        # Add a null handler to prevent any output
        null_handler = logging.NullHandler()
        logger.addHandler(null_handler)
        return logger
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if file_output:
        if log_file is None:
            # Default log file location
            log_file = Path.cwd() / "czi2tif.log"
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging initialized with level: {log_level}")
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"czi2tif.{name}")
    return logging.getLogger("czi2tif")


def configure_module_logger(module_name: str) -> logging.Logger:
    """
    Configure a logger for a specific module.
    
    Args:
        module_name: Name of the module (typically __name__)
        
    Returns:
        Configured logger for the module
    """
    # Extract just the module name without package path
    clean_name = module_name.split('.')[-1] if '.' in module_name else module_name
    return get_logger(clean_name)


# Convenience function for quick setup
def init_default_logging(verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """
    Initialize logging with default settings.
    
    Args:
        verbose: If True, sets DEBUG level; otherwise INFO level
        quiet: If True, disables all logging
        
    Returns:
        Configured logger instance
    """
    if quiet:
        return setup_logging(quiet=True)
    
    level = "DEBUG" if verbose else "INFO"
    return setup_logging(
        log_level=level,
        console_output=True,
        file_output=False,
        quiet=quiet
    )


# Module-level logger for this logging module itself
_logger = logging.getLogger(__name__)
