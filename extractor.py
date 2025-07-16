"""
Cryptocurrency Address Extractor Module - Enhanced with Excel Support
====================================================================

This module contains the main extraction logic for finding and extracting
cryptocurrency addresses from CSV and Excel files, including multi-sheet processing.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.1.0 - Added Excel support
"""

import csv
import logging
import os
import pandas as pd
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass
from collections import defaultdict

from patterns import CryptoPatterns, CryptoPattern
from validators import ValidatorFactory
from logger_config import LogContext, log_function_call


@dataclass
class ExtractedAddress:
    """
    Data class representing an extracted cryptocurrency address.
    
    Attributes:
        address (str): The cryptocurrency address
        crypto_type (str): The type of cryptocurrency (BTC, ETH, etc.)
        crypto_name (str): Full name of the cryptocurrency
        filename (str): Source filename
        sheet_name (str): Sheet name (for Excel files, empty for CSV)
        row (int): Row number in the file (1-indexed)
        column (int): Column number in the file (1-indexed)
        confidence (float): Confidence score (0-100)
        is_duplicate (bool): Whether this address appears multiple times
        duplicate_count (int): Number of times this address appears
    """
    address: str
    crypto_type: str
    crypto_name: str
    filename: str
    sheet_name: str = ""  # New field for Excel sheet names
    row: int = 0
    column: int = 0
    confidence: float = 0.0
    is_duplicate: bool = False
    duplicate_count: int = 1


class CryptoExtractor:
    """
    Main class for extracting cryptocurrency addresses from CSV and Excel files.
    
    This class handles the core extraction logic, including pattern matching,
    validation, and deduplication of addresses. Enhanced to support Excel files
    with multiple sheets.
    """
    
    def __init__(self, file_handler=None):
        """
        Initialize the extractor with patterns and validators.
        
        File: extractor.py
        Function: __init__()
        
        Args:
            file_handler: Optional FileHandler instance for enhanced tracking
        """
        self.logger = logging.getLogger(__name__)
        self.patterns = CryptoPatterns.get_all_patterns()
        self.validator_factory = ValidatorFactory()
        
        # Store file handler for enhanced tracking
        self.file_handler = file_handler
        
        self.logger.info(f"Initialized CryptoExtractor with {len(self.patterns)} cryptocurrency patterns")
    
    def add_custom_cryptos(self, custom_cryptos: List[Dict]):
        """
        Add custom cryptocurrency patterns to the extractor.
        
        Args:
            custom_cryptos: List of dictionaries with 'name', 'symbol', and 'pattern'
        """
        import re
        
        for crypto in custom_cryptos:
            try:
                # Create pattern object
                pattern = CryptoPattern(
                    name=crypto['name'],
                    symbol=crypto['symbol'],
                    patterns=[
                        re.compile(f"\\b{crypto['pattern']}\\b"),  # With word boundaries
                        re.compile(crypto['pattern'])  # Without boundaries
                    ],
                    min_length=1,  # Accept any length for custom patterns
                    max_length=200,
                    has_checksum=False,  # No validation for custom cryptos
                    confidence_boost=0.0,
                    description=f"Custom: {crypto['name']}"
                )
                
                # Add to patterns dictionary
                self.patterns[crypto['symbol']] = pattern
                
                self.logger.info(f"Added custom cryptocurrency: {crypto['name']} ({crypto['symbol']})")
                
            except Exception as e:
                self.logger.error(f"Failed to add custom crypto {crypto['name']}: {str(e)}")
    
    def extract_from_files(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable] = None,
        validate_checksum: bool = True
    ) -> List[ExtractedAddress]:
        """
        Extract cryptocurrency addresses from multiple CSV and Excel files.
        
        Args:
            file_paths (List[str]): List of CSV/Excel file paths to process
            progress_callback (Optional[Callable]): Callback for progress updates
            validate_checksum (bool): Whether to validate address checksums
        
        Returns:
            List[ExtractedAddress]: List of all extracted addresses
        
        Raises:
            FileNotFoundError: If a file doesn't exist
            Exception: If there's an error reading the file
        """
        all_addresses = []
        total_files = len(file_paths)
        
        self.logger.info(f"Starting extraction from {total_files} files with enhanced tracking")
            
        # Pass selected files count to file_handler for tracking
        if self.file_handler and hasattr(self.file_handler, 'file_processing_stats'):
            self.file_handler.file_processing_stats['total_files_selected'] = total_files
        
        for idx, file_path in enumerate(file_paths):
            try:
                with LogContext(f"Processing file: {os.path.basename(file_path)}", self.logger):
                    if progress_callback:
                        progress_callback(
                            idx,
                            total_files,
                            f"Processing {os.path.basename(file_path)}..."
                        )
                    
                    # Determine file type and process accordingly
                    if file_path.lower().endswith(('.xlsx', '.xls')):
                        addresses = self._extract_from_excel_file(file_path, validate_checksum)
                    else:
                        addresses = self._extract_from_csv_file(file_path, validate_checksum)
                    
                    # Record empty file if no addresses found
                    if self.file_handler and len(addresses) == 0:
                        self.file_handler.record_empty_file(file_path, len(addresses))
                    
                    all_addresses.extend(addresses)
                    if self.file_handler and len(addresses) == 0:
                    # Record empty file if no addresses found
                        if self.file_handler and len(addresses) == 0:
                            self.file_handler.record_empty_file(file_path, len(addresses))
                    
                    self.logger.info(
                        f"Extracted {len(addresses)} addresses from {os.path.basename(file_path)}"
                    )
                    
            except Exception as e:
                self.logger.error(
                    f"Failed to process {file_path}: {str(e)}",
                    exc_info=True
                )
                # Continue with other files - error already tracked by file_handler
        
        # Mark duplicates
        self._mark_duplicates(all_addresses)
        
        if progress_callback:
            progress_callback(total_files, total_files, "Extraction complete")
        
        self.logger.info(f"Total addresses extracted: {len(all_addresses)}")
        
        return all_addresses
    
    def _extract_from_excel_file(
        self,
        file_path: str,
        validate_checksum: bool
    ) -> List[ExtractedAddress]:
        """
        Extract addresses from an Excel file using enhanced tracking.
        
        File: extractor.py
        Function: _extract_from_excel_file()
        
        Enhanced to use file_handler's tracking methods for comprehensive error handling.
        
        Args:
            file_path (str): Path to the Excel file
            validate_checksum (bool): Whether to validate checksums
        
        Returns:
            List[ExtractedAddress]: Extracted addresses from all sheets
        """
        addresses = []
        filename = os.path.basename(file_path)
        
        try:
            # Use file_handler's enhanced tracking method if available
            if self.file_handler and hasattr(self.file_handler, 'read_excel_with_tracking'):
                sheets_data = self.file_handler.read_excel_with_tracking(file_path)
            else:
                # Fallback to basic method
                self.logger.warning("Using fallback Excel reading method - tracking not available")
                excel_file = pd.ExcelFile(file_path)
                sheets_data = {}
                for sheet_name in excel_file.sheet_names:
                    sheets_data[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                excel_file.close()
            
            # Process each sheet
            for sheet_name, df in sheets_data.items():
                self.logger.info(f"Processing sheet: {sheet_name}")
                
                try:
                    # Convert DataFrame to list of lists for processing
                    sheet_data = df.fillna('').astype(str).values.tolist()
                    
                    # Process each row and column
                    for row_num, row in enumerate(sheet_data, start=1):
                        for col_num, cell_value in enumerate(row, start=1):
                            if cell_value and str(cell_value).strip():
                                # Extract addresses from this cell
                                cell_addresses = self._extract_from_cell(
                                    str(cell_value),
                                    filename,
                                    sheet_name,
                                    row_num,
                                    col_num,
                                    validate_checksum
                                )
                                
                                addresses.extend(cell_addresses)
                
                except Exception as e:
                    self.logger.error(f"Error processing sheet '{sheet_name}' in {file_path}: {str(e)}")
                    continue
        
        except Exception as e:
            # Error already logged and tracked by file_handler's read_excel_with_tracking
            self.logger.error(f"Error processing Excel file {file_path}: {str(e)}")
            raise
        
        return addresses





    def _extract_from_csv_file(
        self,
        file_path: str,
        validate_checksum: bool
    ) -> List[ExtractedAddress]:
        """
        Extract addresses from a single CSV file using enhanced tracking.
        
        File: extractor.py
        Function: _extract_from_csv_file()
        
        Enhanced to use file_handler's tracking methods for comprehensive error handling.
        
        Args:
            file_path (str): Path to the CSV file
            validate_checksum (bool): Whether to validate checksums
        
        Returns:
            List[ExtractedAddress]: Extracted addresses from the file
        """
        addresses = []
        filename = os.path.basename(file_path)
        
        try:
            # Use file_handler's enhanced tracking method if available
            if self.file_handler and hasattr(self.file_handler, 'read_csv_with_tracking'):
                df = self.file_handler.read_csv_with_tracking(file_path)
            else:
                # Fallback to basic method
                self.logger.warning("Using fallback CSV reading method - tracking not available")
                df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            
            # Convert DataFrame to list of lists for processing
            csv_data = df.fillna('').astype(str).values.tolist()
            
            # Process headers as row 0
            headers = df.columns.tolist() if not df.empty else []
            if headers:
                csv_data.insert(0, headers)
            
            # Process each row and column
            for row_num, row in enumerate(csv_data, start=1):
                for col_num, cell_value in enumerate(row, start=1):
                    if cell_value and str(cell_value).strip():
                        # Extract addresses from this cell
                        cell_addresses = self._extract_from_cell(
                            str(cell_value),
                            filename,
                            'Sheet1',  # CSV files don't have sheet names
                            row_num,
                            col_num,
                            validate_checksum
                        )
                        
                        addresses.extend(cell_addresses)
        
        except Exception as e:
            # Error already logged and tracked by file_handler's read_csv_with_tracking
            self.logger.error(f"Error processing CSV file {file_path}: {str(e)}")
            raise
        
        return addresses






    def _extract_from_cell(
        self,
        cell_content: str,
        filename: str,
        sheet_name: str,
        row: int,
        column: int,
        validate_checksum: bool
    ) -> List[ExtractedAddress]:
        """
        Extract all cryptocurrency addresses from a single cell.
        
        Enhanced version with aggressive pattern matching and post-processing.
        
        Args:
            cell_content (str): The content of the cell
            filename (str): Source filename
            sheet_name (str): Sheet name (empty for CSV files)
            row (int): Row number
            column (int): Column number
            validate_checksum (bool): Whether to validate checksums
        
        Returns:
            List[ExtractedAddress]: Addresses found in the cell
        """
        found_addresses = []
        
        # Track addresses already found in this cell to avoid duplicates
        cell_addresses = set()
        
        for crypto_type, pattern in self.patterns.items():
            # Skip aliases
            if crypto_type in ['MONERO', 'RIPPLE', 'CARDANO', 'LITECOIN', 'DOGECOIN', 'TETHER', 'SHIBA INU']:
                continue
            
            potential_addresses = CryptoPatterns.extract_potential_addresses(
                cell_content,
                pattern
            )
            
            # Post-process to reduce false positives
            potential_addresses = CryptoPatterns.post_process_addresses(
                potential_addresses,
                cell_content
            )
            
            for address, pattern_idx, start, end in potential_addresses:
                # Skip if we've already found this address in this cell
                if address in cell_addresses:
                    continue
                
                # Calculate base confidence
                confidence = CryptoPatterns.calculate_base_confidence(
                    address,
                    pattern,
                    pattern_idx
                )
                
                # Validate if requested
                if validate_checksum and pattern.has_checksum:
                    validator = self.validator_factory.get_validator(crypto_type)
                    if validator:
                        is_valid, confidence_boost = validator.validate_with_logging(
                            address,
                            crypto_type
                        )
                        
                        if not is_valid:
                            # Check if this is an aggressive pattern
                            standard_patterns = sum(1 for p in pattern.patterns if r'\b' in p.pattern)
                            
                            if pattern_idx < standard_patterns:
                                continue  # Skip if standard pattern and invalid
                            else:
                                confidence = max(20.0, confidence - 30.0)  # Heavy penalty but keep it
                        else:
                            confidence = min(100.0, confidence + confidence_boost)
                
                # Create extracted address object
                extracted = ExtractedAddress(
                    address=address,
                    crypto_type=pattern.symbol,
                    crypto_name=pattern.name,
                    filename=filename,
                    sheet_name=sheet_name,
                    row=row,
                    column=column,
                    confidence=confidence
                )
                
                found_addresses.append(extracted)
                cell_addresses.add(address)
                
                # Enhanced logging with sheet information
                location_info = f"{filename}"
                if sheet_name:
                    location_info += f"[{sheet_name}]"
                location_info += f"[{row}:{column}]"
                
                self.logger.debug(
                    f"Found {crypto_type} address in {location_info}: {address} (confidence: {confidence:.1f}%)"
                )
        
        return found_addresses
    
    def _mark_duplicates(self, addresses: List[ExtractedAddress]) -> None:
        """
        Mark duplicate addresses in the list.
        
        Rules:
        - First occurrence of an address within a file/sheet = NOT marked as duplicate (white)
        - Subsequent occurrences = marked as duplicate (yellow)
        - Duplicates are counted within the same file/sheet combination
        - Same address across different crypto types = duplicates
        
        Args:
            addresses (List[ExtractedAddress]): List of addresses to check
        """
        from collections import defaultdict
        
        # Track first occurrence of each address within each file/sheet
        # Key: (filename, sheet_name, address)
        # Value: list of ExtractedAddress objects
        file_sheet_address_groups = defaultdict(list)
        
        # Group addresses by file/sheet/address combination
        for addr in addresses:
            # Create unique key for file/sheet/address combination
            key = (addr.filename, addr.sheet_name, addr.address.lower())  # Case-insensitive
            file_sheet_address_groups[key].append(addr)
        
        # Process each group
        for key, addr_list in file_sheet_address_groups.items():
            if len(addr_list) > 1:
                # Sort by processing order (row, then column) to determine first occurrence
                addr_list.sort(key=lambda x: (x.row, x.column))
                
                # First occurrence stays as is_duplicate = False (white background)
                first_addr = addr_list[0]
                first_addr.is_duplicate = False
                first_addr.duplicate_count = len(addr_list)
                
                # Mark subsequent occurrences as duplicates (yellow background)
                for addr in addr_list[1:]:
                    addr.is_duplicate = True
                    addr.duplicate_count = len(addr_list)
                
                filename, sheet_name, address = key
                location = f"{filename}"
                if sheet_name:
                    location += f"[{sheet_name}]"
                
                self.logger.debug(
                    f"Found {len(addr_list)} occurrences of address {address} in {location}. "
                    f"First at row {first_addr.row}, subsequent marked as duplicates."
                )
            else:
                # Single occurrence - not a duplicate
                addr_list[0].is_duplicate = False
                addr_list[0].duplicate_count = 1
    
    def get_statistics(self, addresses: List[ExtractedAddress]) -> Dict[str, int]:
        """
        Get statistics about extracted addresses.
        
        Enhanced to correctly count first occurrences vs duplicates.
        
        Args:
            addresses (List[ExtractedAddress]): List of extracted addresses
        
        Returns:
            Dict[str, int]: Statistics by cryptocurrency type and file info
        """
        from collections import defaultdict, Counter
        
        stats = defaultdict(int)
        
        # Count by cryptocurrency name (includes custom cryptos)
        for addr in addresses:
            stats[addr.crypto_name] += 1
        
        # Add total counts
        stats['TOTAL'] = len(addresses)
        
        # Count unique addresses (first occurrences only)
        unique_addresses = sum(1 for addr in addresses if not addr.is_duplicate)
        stats['UNIQUE'] = unique_addresses
        
        # Count duplicates (subsequent occurrences only)
        duplicate_addresses = sum(1 for addr in addresses if addr.is_duplicate)
        stats['DUPLICATES'] = duplicate_addresses
        
        # Count files and sheets processed
        unique_files = len(set(addr.filename for addr in addresses))
        stats['FILES_PROCESSED'] = unique_files
        
        # Count Excel sheets processed
        excel_sheets = set()
        for addr in addresses:
            if addr.sheet_name:  # Only count if there's a sheet name (Excel files)
                excel_sheets.add(f"{addr.filename}:{addr.sheet_name}")
        stats['EXCEL_SHEETS_PROCESSED'] = len(excel_sheets)
        
        # Additional duplicate analysis
        file_sheet_groups = defaultdict(set)
        for addr in addresses:
            key = (addr.filename, addr.sheet_name)
            file_sheet_groups[key].add(addr.address.lower())
        
        # Count unique addresses per file/sheet
        for key, unique_addrs in file_sheet_groups.items():
            filename, sheet_name = key
            location = filename
            if sheet_name:
                location += f"[{sheet_name}]"
            stats[f'UNIQUE_IN_{location}'] = len(unique_addrs)
        
        return dict(stats)


    def get_addresses_by_crypto(
        self,
        addresses: List[ExtractedAddress]
    ) -> Dict[str, List[ExtractedAddress]]:
        """
        Group addresses by cryptocurrency type.
        
        Args:
            addresses (List[ExtractedAddress]): List of addresses
        
        Returns:
            Dict[str, List[ExtractedAddress]]: Addresses grouped by crypto type
        """
        grouped = defaultdict(list)
        
        for addr in addresses:
            grouped[addr.crypto_name].append(addr)
        
        return dict(grouped)
    
    def get_addresses_by_file(
        self,
        addresses: List[ExtractedAddress]
    ) -> Dict[str, List[ExtractedAddress]]:
        """
        Group addresses by source file and sheet.
        
        Args:
            addresses (List[ExtractedAddress]): List of addresses
        
        Returns:
            Dict[str, List[ExtractedAddress]]: Addresses grouped by file/sheet
        """
        grouped = defaultdict(list)
        
        for addr in addresses:
            # Create a key that includes sheet information for Excel files
            if addr.sheet_name:
                key = f"{addr.filename} [{addr.sheet_name}]"
            else:
                key = addr.filename
            grouped[key].append(addr)
        
        return dict(grouped)
    
def get_duplicate_summary(self, addresses: List[ExtractedAddress]) -> Dict[str, any]:
    """
    Get detailed duplicate analysis.
    
    Returns:
        Dict with duplicate statistics and examples
    """
    from collections import defaultdict, Counter
    
    # Group by file/sheet/address
    file_sheet_duplicates = defaultdict(lambda: defaultdict(list))
    
    for addr in addresses:
        key = (addr.filename, addr.sheet_name)
        file_sheet_duplicates[key][addr.address.lower()].append(addr)
    
    duplicate_summary = {
        'total_unique_addresses': 0,
        'total_duplicate_instances': 0,
        'files_with_duplicates': [],
        'most_duplicated_addresses': [],
        'duplicate_examples': []
    }
    
    all_duplicates = []
    
    for file_sheet_key, address_groups in file_sheet_duplicates.items():
        filename, sheet_name = file_sheet_key
        location = filename
        if sheet_name:
            location += f"[{sheet_name}]"
        
        file_duplicates = []
        file_unique_count = 0
        file_duplicate_count = 0
        
        for address, addr_list in address_groups.items():
            if len(addr_list) > 1:
                # This address has duplicates in this file/sheet
                file_duplicates.append({
                    'address': address,
                    'count': len(addr_list),
                    'locations': [(a.row, a.column) for a in addr_list],
                    'crypto_types': list(set(a.crypto_name for a in addr_list))
                })
                file_duplicate_count += len(addr_list) - 1  # Don't count first occurrence
                all_duplicates.append((address, len(addr_list), location))
            
            file_unique_count += 1
        
        if file_duplicates:
            duplicate_summary['files_with_duplicates'].append({
                'location': location,
                'unique_addresses': file_unique_count,
                'duplicate_instances': file_duplicate_count,
                'duplicates': file_duplicates[:5]  # Top 5 for examples
            })
    
    # Overall statistics
    duplicate_summary['total_unique_addresses'] = sum(1 for addr in addresses if not addr.is_duplicate)
    duplicate_summary['total_duplicate_instances'] = sum(1 for addr in addresses if addr.is_duplicate)
    
    # Most duplicated addresses across all files
    duplicate_summary['most_duplicated_addresses'] = sorted(all_duplicates, key=lambda x: x[1], reverse=True)[:10]
    
    return duplicate_summary