"""
Configuration Management Module
==============================
This module handles configuration loading and saving for the application.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.0
"""

import json
import os
import logging


class Config:
    """Configuration management for the application."""
    
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "default_input_directory": "",
        "default_output_directory": "",
        "validate_checksums": True,
        "output_filename_pattern": "crypto_addresses_{timestamp}.xlsx",
        "log_directory": "logs",
        "chainalysis_api_key": "",
        "generate_pdf": False,
        "generate_word": False,
        "custom_cryptos": []
    }
    
    @classmethod
    def load(cls):
        """Load configuration from file or create default."""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in cls.DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logging.warning(f"Failed to load config: {e}. Using defaults.")
        
        # Create default config file
        cls.save(cls.DEFAULT_CONFIG)
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config):
        """Save configuration to file."""
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")