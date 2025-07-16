"""
Cryptocurrency Address Extractor - Main Entry Point
==================================================

This is the refactored main entry point that uses modular components.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 2.0.0 - Refactored for better maintainability
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

from config import Config
from gui_extraction_handler import ExtractionHandler
from gui_tabs import GUITabs
from gui_handlers import GUIHandlers
from gui_api_processor import APIProcessor
from gui_styles import GUIStyles
from extractor import CryptoExtractor
from logger_config import setup_logging
from file_handler import FileHandler
from iapi_service import IAPIService


class CryptoExtractorGUI(GUITabs, GUIHandlers, GUIStyles):
    """
    Main GUI class for the Cryptocurrency Address Extractor application.
    
    Uses modular mixins for better code organization:
    - GUITabs: Tab creation and management
    - GUIHandlers: Event handlers and actions
    - GUIStyles: Visual styling and theming
    """
    
    def __init__(self, initial_files=None):
        """
        Initialize the GUI application.
        
        Args:
            initial_files (List[str], optional): List of files to load initially
            
        Raises:
            Exception: If critical components fail to initialize
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Crypto Extractor GUI")
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Cryptocurrency Address Extractor")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Store tkinter modules for use in mixins
        self.tk = tk
        self.ttk = ttk
        
        # Load configuration
        try:
            self.config = Config.load()
            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.config = Config.DEFAULT_CONFIG.copy()
        
        # Initialize API service
        self.api_key = self.config.get('chainalysis_api_key', '')
        self.api_service = None
        if self.api_key:
            try:
                self.api_service = IAPIService(self.api_key)
                self.logger.info("Chainalysis API service initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize API service: {e}")
        
        # Apply modern styling
        try:
            self._apply_styling()
            self.logger.debug("GUI styling applied")
        except Exception as e:
            self.logger.warning(f"Failed to apply styling: {e}")
        
        # Initialize components IN CORRECT ORDER
        try:
            # 1. FIRST - Create file_handler
            self.file_handler = FileHandler()
            
            # 2. SECOND - Create extractor with file_handler
            self.extractor = CryptoExtractor(file_handler=self.file_handler)
            self.logger.info("Connected extractor to file_handler for enhanced tracking")
            
            # 3. THIRD - Initialize other components
            self.selected_files = initial_files or []
            self.custom_cryptos = self.config.get('custom_cryptos', [])
            
            # Initialize processors
            self.api_processor = APIProcessor(self)
            self.extraction_handler = ExtractionHandler(self)
            
            self.logger.info("Core components initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create all tabs
        try:
            self._create_extraction_tab()
            self._create_custom_crypto_tab()
            self._create_crypto_list_tab()
            self._create_api_tab()
            self._create_settings_tab()
            self.logger.info("All GUI tabs created")
        except Exception as e:
            self.logger.error(f"Failed to create GUI tabs: {e}")
            raise
        
        # Load initial files if provided
        if self.selected_files:
            for file in self.selected_files:
                self.files_listbox.insert(tk.END, os.path.basename(file))
            self.logger.info(f"Loaded {len(self.selected_files)} initial files")
        
        self.logger.info("GUI initialization complete")





    def _enhance_with_chainalysis_api(self, addresses):
        """
        Delegate API enhancement to the API processor.
        
        Args:
            addresses (List[ExtractedAddress]): Addresses to enhance
            
        Returns:
            List[ExtractedAddress]: Enhanced addresses with API data
        """
        return self.api_processor.enhance_with_chainalysis_api(addresses)
    
    def _start_extraction(self):
        """
        Delegate extraction to the extraction handler.
        
        This method is called when the user clicks the Extract button.
        """
        self.extraction_handler.start_extraction()
    
    def run(self):
        """
        Start the GUI application main loop.
        
        This method blocks until the application window is closed.
        """
        self.logger.info("Starting GUI application main loop")
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI error: {e}")
            raise
        finally:
            self.logger.info("GUI application closed")


def run_cli(args):
    """
    Run the extractor in command-line mode.
    
    Args:
        args: Parsed command-line arguments containing:
            - input: List of input files
            - output: Output file path (optional)
            - output_dir: Output directory (optional)
            - validate_checksum: Whether to validate checksums
            
    Raises:
        Exception: If extraction fails
    """
    logger = logging.getLogger(__name__)
    logger.info("Running in CLI mode")
    
    # Load config for defaults
    try:
        config = Config.load()
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        config = Config.DEFAULT_CONFIG.copy()
    
    # Initialize extractor
    # ENHANCEMENT: Initialize file_handler and extractor with tracking
    file_handler = FileHandler()
    extractor = CryptoExtractor(file_handler=file_handler)  # Connect for tracking
    logger.info("Initialized extractor with enhanced file tracking")
    
    # Add custom cryptocurrencies from config
    custom_cryptos = config.get('custom_cryptos', [])
    if custom_cryptos:
        extractor.add_custom_cryptos(custom_cryptos)
        logger.info(f"Added {len(custom_cryptos)} custom cryptocurrencies")
    
    # Prepare output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = config.get('output_filename_pattern', 'crypto_addresses_{timestamp}.xlsx')
        output_name = output_name.replace('{timestamp}', timestamp)
        output_dir = args.output_dir or config.get('default_output_directory', os.getcwd())
        output_path = os.path.join(output_dir, output_name)
    
    # Validate checksum setting
    validate = args.validate_checksum if args.validate_checksum is not None else config.get('validate_checksums', True)
    
    logger.info(f"Processing {len(args.input)} files")
    logger.info(f"Output will be saved to: {output_path}")
    logger.info(f"Checksum validation: {validate}")
    
    # Simple progress callback for CLI
    def cli_progress(current, total, message):
        """Update progress in CLI mode."""
        print(f"\rProgress: {current}/{total} - {message}", end='', flush=True)
    
    try:
        # Extract addresses
        results = extractor.extract_from_files(
            args.input,
            progress_callback=cli_progress,
            validate_checksum=validate
        )
        
        print()  # New line after progress
        
        # Check if any addresses were found
        if not results:
            logger.warning("No cryptocurrency addresses found in the input files")
            print("\nNo cryptocurrency addresses found!")
            return
        
        # Save results
        saved_path = file_handler.write_to_excel(
            addresses=results, 
            output_path=output_path,
            include_api_data=False,  # CLI mode doesn't use API by default
            selected_files=args.input  # Enable comprehensive file tracking
        )
        
        # Print statistics
        stats = extractor.get_statistics(results)
        print("\nExtraction Complete!")
        print("-" * 40)
        print(f"Total addresses found: {stats.get('TOTAL', 0)}")
        print(f"Unique addresses: {stats.get('UNIQUE', 0)}")
        print(f"Duplicates: {stats.get('DUPLICATES', 0)}")
        print("\nBreakdown by cryptocurrency:")
        
        for crypto, count in sorted(stats.items()):
            if crypto not in ['TOTAL', 'UNIQUE', 'DUPLICATES', 'FILES_PROCESSED', 'EXCEL_SHEETS_PROCESSED']:
                if not crypto.startswith('UNIQUE_IN_'):
                    print(f"  {crypto}: {count}")
        
        print(f"\nResults saved to: {saved_path}")
        
    except Exception as e:
        logger.error(f"CLI extraction failed: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        sys.exit(1)


def main():
    """
    Main entry point for the application.
    
    Parses command-line arguments and runs either GUI or CLI mode.
    Sets up logging and handles fatal errors.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Cryptocurrency Address Extractor - Extract crypto addresses from CSV and Excel files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # GUI mode (default)
  python main.py
  
  # Process single file
  python main.py -i data.csv
  python main.py -i data.xlsx
  
  # Process multiple files (mixed types)
  python main.py -i file1.csv file2.xlsx file3.xls -o results.xlsx
  
  # Process files with custom output directory
  python main.py -i *.csv *.xlsx --output-dir C:/Results/
  
  # Process without checksum validation
  python main.py -i data.xlsx --no-validate
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        nargs='+',
        help='Input CSV or Excel file(s) to process. Supports .csv, .xlsx, and .xls files. If not specified, opens GUI.'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output Excel file path. If not specified, uses default naming.'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for results. Defaults to config or current directory.'
    )
    
    parser.add_argument(
        '--validate-checksum',
        dest='validate_checksum',
        action='store_true',
        default=None,
        help='Enable checksum validation (default from config)'
    )
    
    parser.add_argument(
        '--no-validate',
        dest='validate_checksum',
        action='store_false',
        help='Disable checksum validation'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging with specified level
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Cryptocurrency Address Extractor")
    logger.debug(f"Command line args: {args}")
    
    try:
        if args.input:
            # Validate input files exist and check extensions
            supported_extensions = ('.csv', '.xlsx', '.xls')
            for file in args.input:
                if not os.path.exists(file):
                    print(f"Error: File not found: {file}")
                    sys.exit(1)
                if not file.lower().endswith(supported_extensions):
                    print(f"Warning: {file} may not be a supported file type (supported: {', '.join(supported_extensions)})")
            
            # Run in CLI mode
            run_cli(args)
        else:
            # Run in GUI mode
            app = CryptoExtractorGUI()
            app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        if args.input:  # CLI mode
            print(f"Fatal error: {str(e)}")
        else:  # GUI mode
            try:
                messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
            except:
                pass  # Ignore if GUI is not available
        sys.exit(1)
    
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()