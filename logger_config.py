"""
Logging Configuration Module
===========================

This module handles the logging configuration for the cryptocurrency address extractor.
It sets up both file and console logging with appropriate formatting and log levels.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.0
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_dir="logs"):
    """
    Configure logging for the application.
    
    Sets up both file and console logging handlers with appropriate formatting.
    Creates a rotating file handler to prevent log files from growing too large.
    
    Args:
        log_level (int): The logging level (default: logging.INFO)
        log_dir (str): Directory to store log files (default: "logs")
    
    Returns:
        logging.Logger: The configured root logger
    
    Raises:
        OSError: If unable to create the log directory
    """
    try:
        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"crypto_extractor_{timestamp}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove any existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Log initial message
        root_logger.info("=" * 80)
        root_logger.info("Cryptocurrency Address Extractor - Logging Initialized")
        root_logger.info(f"Log file: {log_file}")
        root_logger.info("=" * 80)
        
        return root_logger
        
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.error(f"Failed to set up logging: {str(e)}")
        return logging.getLogger()


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): The name for the logger (typically __name__)
    
    Returns:
        logging.Logger: A logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for logging operations with automatic error handling.
    
    This class provides a convenient way to log the start and end of operations,
    including automatic error logging if exceptions occur.
    
    Example:
        with LogContext("Processing file", logger):
            # Your code here
            pass
    """
    
    def __init__(self, operation_name, logger=None):
        """
        Initialize the logging context.
        
        Args:
            operation_name (str): Description of the operation being performed
            logger (logging.Logger): Logger instance (uses root logger if None)
        """
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger()
        self.start_time = None
    
    def __enter__(self):
        """Enter the context and log the operation start."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and log the operation result."""
        duration = datetime.now() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"Completed: {self.operation_name} "
                f"(Duration: {duration.total_seconds():.2f}s)"
            )
        else:
            self.logger.error(
                f"Failed: {self.operation_name} "
                f"(Duration: {duration.total_seconds():.2f}s) - "
                f"Error: {exc_type.__name__}: {exc_val}"
            )
        
        # Don't suppress the exception
        return False


def log_function_call(func):
    """
    Decorator to automatically log function calls and their results.
    
    This decorator logs when a function is called, its arguments,
    and whether it completed successfully or raised an exception.
    
    Args:
        func: The function to decorate
    
    Returns:
        The decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        func_name = func.__name__
        
        # Log function call
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"{func_name} failed with error: {str(e)}", exc_info=True)
            raise
    
    return wrapper