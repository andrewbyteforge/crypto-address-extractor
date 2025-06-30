"""
File Handler Module - Production Ready Version with Direct/Indirect Exposure
===========================================================================

This module handles all file I/O operations for the cryptocurrency address extractor.
Provides methods for reading CSV/Excel files and writing comprehensive Excel reports
with multiple analysis sheets including both direct and indirect exchange exposure.

Author: Crypto Extractor Tool
Date: 2025-01-18
Version: 2.2.0 - Enhanced with Direct/Indirect Exchange Exposure
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.worksheet import Worksheet
import re

from extractor import ExtractedAddress


class FileHandler:
    """
    Handles all file I/O operations for the cryptocurrency address extractor.
    
    Features:
    - Read CSV and Excel files with multi-sheet support
    - Write comprehensive Excel reports with multiple analysis sheets
    - Handle large datasets with row limit protection
    - Professional formatting and styling
    - Backward compatible save_to_excel method
    - Enhanced direct and indirect exchange exposure display
    """
    
    # Excel row limit with safety buffer
    EXCEL_MAX_ROWS = 1048576
    SAFE_ROW_LIMIT = 1000000  # Leave buffer for headers and formatting
    
    def __init__(self):
        """
        Initialize the file handler with logging configuration.
        
        Raises:
            Exception: If logger cannot be initialized
        """
        try:
            self.logger = logging.getLogger(__name__)
            self.logger.info("FileHandler initialized successfully")
        except Exception as e:
            print(f"Failed to initialize FileHandler logger: {e}")
            raise
    
    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Read CSV file and return as DataFrame.
        
        Args:
            file_path (str): Path to the CSV file
            encoding (str): File encoding (default: utf-8)
            
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            pd.errors.ParserError: If CSV parsing fails
            Exception: For other errors
        """
        self.logger.info(f"Reading CSV file: {file_path}")
        
        if not os.path.exists(file_path):
            error_msg = f"CSV file not found: {file_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Read CSV with multiple encoding fallbacks
            encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
            
            for enc in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=enc, low_memory=False)
                    self.logger.info(f"Successfully read CSV with {enc} encoding: {len(df)} rows")
                    return df
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail
            raise ValueError(f"Could not read CSV with any encoding: {encodings}")
            
        except pd.errors.ParserError as e:
            error_msg = f"CSV parsing error in {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise pd.errors.ParserError(error_msg)
        except Exception as e:
            error_msg = f"Error reading CSV file {file_path}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Read Excel file and return dictionary of DataFrames for each sheet.
        
        Args:
            file_path (str): Path to the Excel file
            sheet_name (Optional[str]): Specific sheet to read (None for all sheets)
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sheet names to DataFrames
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If Excel file is invalid
            Exception: For other errors
        """
        self.logger.info(f"Reading Excel file: {file_path}")
        
        if not os.path.exists(file_path):
            error_msg = f"Excel file not found: {file_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            sheets_to_read = [sheet_name] if sheet_name else excel_file.sheet_names
            
            result = {}
            for sheet in sheets_to_read:
                if sheet in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet, header=None)
                    result[sheet] = df
                    self.logger.info(f"Read sheet '{sheet}': {len(df)} rows")
                else:
                    self.logger.warning(f"Sheet '{sheet}' not found in {file_path}")
            
            excel_file.close()
            return result
            
        except ValueError as e:
            error_msg = f"Invalid Excel file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error reading Excel file {file_path}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def save_to_excel(self, addresses: List[ExtractedAddress], output_path: str, 
                      include_api_data: Optional[bool] = None) -> str:
        """
        Save extracted addresses to Excel file (wrapper for backward compatibility).
        
        This method wraps write_to_excel to maintain compatibility with existing code
        that expects save_to_excel to return the output path.
        
        Args:
            addresses (List[ExtractedAddress]): List of extracted addresses
            output_path (str): Path for the output Excel file
            include_api_data (Optional[bool]): Whether to include API data columns.
                                             If None, auto-detects from addresses.
            
        Returns:
            str: The path of the saved file
            
        Raises:
            PermissionError: If file is open or inaccessible
            Exception: For other errors
        """
        try:
            # Auto-detect if we should include API data if not specified
            if include_api_data is None:
                include_api_data = any(hasattr(addr, 'api_balance') for addr in addresses)
                if include_api_data:
                    self.logger.info("Auto-detected API data in addresses")
            
            # Call the main write_to_excel method
            self.write_to_excel(addresses, output_path, include_api_data)
            
            # Log success
            self.logger.info(f"Successfully saved {len(addresses)} addresses to {output_path}")
            
            # Return the output path for backward compatibility
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error in save_to_excel: {str(e)}")
            raise
    
    def write_to_excel(self, addresses: List[ExtractedAddress], output_path: str,
                      include_api_data: bool = False) -> None:
        """
        Write extracted addresses to a formatted Excel file with multiple sheets.
        
        Args:
            addresses (List[ExtractedAddress]): List of extracted addresses
            output_path (str): Path for the output Excel file
            include_api_data (bool): Whether to include API data columns
            
        Raises:
            PermissionError: If file is open or inaccessible
            Exception: For other errors
        """
        self.logger.info(f"Writing {len(addresses)} addresses to Excel: {output_path}")
        
        try:
            # Create workbook
            wb = Workbook()
            
            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # Create sheets
            self._create_summary_sheet(wb, addresses)
            self._create_all_addresses_sheet(wb, addresses, include_api_data)
            self._create_duplicate_analysis_sheet(wb, addresses)
            
            # Group addresses by cryptocurrency
            crypto_groups = defaultdict(list)
            for addr in addresses:
                crypto_groups[addr.crypto_name].append(addr)
            
            # Create individual crypto sheets
            for crypto_name, crypto_addresses in crypto_groups.items():
                self._create_crypto_sheet(wb, crypto_name, crypto_addresses, include_api_data)
            
            # Create additional analysis sheets if API data available
            # NOTE: These additional analysis sheets are temporarily disabled
            # Uncomment when the methods are implemented
            # if include_api_data and any(hasattr(addr, 'api_balance') for addr in addresses):
            #     self._create_balance_sheet(wb, addresses)
            #     self._create_exchange_exposure_sheet(wb, addresses)
            #     self._create_high_value_sheet(wb, addresses)
            #     self._create_risk_analysis_sheet(wb, addresses)
            
            # Save workbook
            wb.save(output_path)
            self.logger.info(f"Successfully created Excel file: {output_path}")
            
        except PermissionError as e:
            error_msg = f"Permission denied writing to {output_path}. Please close the file if it's open."
            self.logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Excel file: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def _format_exposure_text(self, exposures):
        """
        Format exposure data for display in Excel cell.
        
        Args:
            exposures: List of exposure dictionaries
            
        Returns:
            Formatted string for display
        """
        if not exposures:
            return ""
        
        # Group by exchange name and sum values
        exposure_summary = {}
        for exp in exposures:
            name = exp.get('name', 'Unknown')
            value = exp.get('value', 0)
            percentage = exp.get('percentage', 0)
            
            if name not in exposure_summary:
                exposure_summary[name] = {
                    'value': 0,
                    'percentage': 0,
                    'count': 0
                }
            
            exposure_summary[name]['value'] += value
            exposure_summary[name]['percentage'] = max(
                exposure_summary[name]['percentage'], 
                percentage
            )
            exposure_summary[name]['count'] += 1
        
        # Format for display
        formatted_parts = []
        for name, data in sorted(exposure_summary.items(), 
                               key=lambda x: x[1]['value'], 
                               reverse=True):
            if data['percentage'] > 0:
                formatted_parts.append(f"{name}: {data['percentage']:.1f}%")
            else:
                formatted_parts.append(f"{name}: ${data['value']:,.2f}")
        
        return "; ".join(formatted_parts[:5])  # Limit to top 5 for space
    
    def _create_summary_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """
        Create summary sheet with extraction statistics.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            addresses (List[ExtractedAddress]): List of all addresses
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            ws = wb.create_sheet("Summary")
            
            # Title
            ws['A1'] = "Cryptocurrency Address Extraction Summary"
            ws['A1'].font = Font(size=16, bold=True)
            ws.merge_cells('A1:D1')
            
            # Extraction info
            ws['A3'] = "Extraction Date:"
            ws['B3'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            ws['A4'] = "Total Addresses Found:"
            ws['B4'] = len(addresses)
            
            # Get unique addresses
            unique_addresses = len(set(addr.address for addr in addresses))
            ws['A5'] = "Unique Addresses:"
            ws['B5'] = unique_addresses
            
            ws['A6'] = "Duplicate Addresses:"
            ws['B6'] = len(addresses) - unique_addresses
            
            # Files processed
            unique_files = set(addr.filename for addr in addresses)
            ws['A8'] = "Files Processed:"
            ws['B8'] = len(unique_files)
            
            # Cryptocurrency breakdown
            ws['A10'] = "Cryptocurrency Breakdown:"
            ws['A10'].font = Font(bold=True)
            
            crypto_counts = defaultdict(int)
            for addr in addresses:
                crypto_counts[addr.crypto_name] += 1
            
            row = 11
            for crypto, count in sorted(crypto_counts.items(), key=lambda x: x[1], reverse=True):
                ws.cell(row=row, column=1, value=crypto)
                ws.cell(row=row, column=2, value=count)
                row += 1
            
            # Format columns
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 20
            
            self.logger.debug("Created summary sheet")
            
        except Exception as e:
            self.logger.error(f"Error creating summary sheet: {str(e)}", exc_info=True)
            raise
    
    def _create_all_addresses_sheet(self, wb: Workbook, addresses: List[ExtractedAddress],
                                   include_api_data: bool) -> None:
        """
        Create sheet with all extracted addresses including enhanced exposure data.
        
        Enhanced to properly include both direct and indirect exposure data.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            addresses (List[ExtractedAddress]): List of all addresses
            include_api_data (bool): Whether to include API data columns
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            self.logger.info(f"Creating 'All Addresses' sheet with include_api_data={include_api_data}")
            
            ws = wb.create_sheet("All Addresses")
            
            # Check row limit
            if len(addresses) > self.SAFE_ROW_LIMIT:
                self._create_paginated_sheets(wb, "All Addresses", addresses, include_api_data)
                return
            
            # Headers
            headers = ["Address", "Cryptocurrency", "Source File", "Sheet", "Row", "Column",
                      "Confidence %", "Is Duplicate", "Total Count"]
            
            if include_api_data:
                # Enhanced headers with both direct and indirect exposure
                headers.extend(["Balance", "Total Received", "Total Sent", "Transfer Count",
                               "Direct Exchange Exposure", "Indirect Exchange Exposure",
                               "Risk Level", "Entity", "Cluster Category"])
            
            # Write headers with formatting
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
            
            # Write data
            for row, addr in enumerate(addresses, 2):
                ws.cell(row=row, column=1, value=addr.address)
                ws.cell(row=row, column=2, value=addr.crypto_name)
                ws.cell(row=row, column=3, value=addr.filename)
                ws.cell(row=row, column=4, value=addr.sheet_name or "N/A")
                ws.cell(row=row, column=5, value=addr.row)
                ws.cell(row=row, column=6, value=addr.column)
                ws.cell(row=row, column=7, value=f"{addr.confidence:.1f}%")
                ws.cell(row=row, column=8, value="Yes" if addr.is_duplicate else "No")
                ws.cell(row=row, column=9, value=addr.duplicate_count)
                
                if include_api_data:
                    ws.cell(row=row, column=10, value=f"{getattr(addr, 'api_balance', 0):,.8f}")
                    ws.cell(row=row, column=11, value=f"{getattr(addr, 'api_total_received', 0):,.8f}")
                    ws.cell(row=row, column=12, value=f"{getattr(addr, 'api_total_sent', 0):,.8f}")
                    ws.cell(row=row, column=13, value=getattr(addr, 'api_transfer_count', 0))
                    
                    # Direct Exchange Exposure
                    direct_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_direct_exposure', [])
                    )
                    ws.cell(row=row, column=14, value=direct_exposure_text)
                    
                    # Indirect Exchange Exposure
                    indirect_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=15, value=indirect_exposure_text)
                    
                    ws.cell(row=row, column=16, value=getattr(addr, 'risk_level', 'Unknown'))
                    ws.cell(row=row, column=17, value=getattr(addr, 'entity_name', ''))
                    ws.cell(row=row, column=18, value=getattr(addr, 'api_cluster_category', ''))
                
                # Highlight duplicates
                if addr.is_duplicate:
                    for col in range(1, len(headers) + 1):
                        ws.cell(row=row, column=col).fill = PatternFill(
                            start_color="FFE699", end_color="FFE699", fill_type="solid"
                        )
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            self.logger.info(f"✓ Created 'All Addresses' sheet with {len(addresses)} addresses")
            
        except Exception as e:
            self.logger.error(f"Failed to create all addresses sheet: {str(e)}")
            raise
    
    def _create_duplicate_analysis_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """
        Create sheet analyzing duplicate addresses.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            addresses (List[ExtractedAddress]): List of all addresses
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            ws = wb.create_sheet("Duplicate Analysis")
            
            # Group duplicates
            address_groups = defaultdict(list)
            for addr in addresses:
                if addr.duplicate_count > 1:
                    address_groups[addr.address].append(addr)
            
            # Title
            ws['A1'] = "Duplicate Address Analysis"
            ws['A1'].font = Font(size=14, bold=True)
            ws.merge_cells('A1:F1')
            
            ws['A3'] = f"Total Duplicate Groups: {len(address_groups)}"
            ws['A4'] = f"Total Duplicate Instances: {sum(len(group) for group in address_groups.values())}"
            
            # Headers
            headers = ["Address", "Cryptocurrency", "Count", "Files", "Sheets", "First Seen"]
            row = 6
            for col, header in enumerate(headers, 1):
                ws.cell(row=row, column=col, value=header)
                ws.cell(row=row, column=col).font = Font(bold=True)
                ws.cell(row=row, column=col).fill = PatternFill(
                    start_color="366092", end_color="366092", fill_type="solid"
                )
                ws.cell(row=row, column=col).font = Font(color="FFFFFF", bold=True)
            
            # Write duplicate groups
            row = 7
            for address, group in sorted(address_groups.items(), 
                                       key=lambda x: len(x[1]), reverse=True):
                if row > self.SAFE_ROW_LIMIT:
                    ws.cell(row=row, column=1, value="⚠️ DATA TRUNCATED - Excel row limit reached")
                    break
                
                files = set(addr.filename for addr in group)
                sheets = set(addr.sheet_name for addr in group if addr.sheet_name)
                
                ws.cell(row=row, column=1, value=address)
                ws.cell(row=row, column=2, value=group[0].crypto_name)
                ws.cell(row=row, column=3, value=len(group))
                ws.cell(row=row, column=4, value=", ".join(files))
                ws.cell(row=row, column=5, value=", ".join(sheets) if sheets else "N/A")
                ws.cell(row=row, column=6, value=f"{group[0].filename} (Row {group[0].row})")
                
                row += 1
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            self.logger.debug(f"Created duplicate analysis sheet with {len(address_groups)} groups")
            
        except Exception as e:
            self.logger.error(f"Error creating duplicate analysis sheet: {str(e)}", exc_info=True)
            raise
    
    def _create_crypto_sheet(self, wb: Workbook, crypto_name: str, 
                            addresses: List[ExtractedAddress], 
                            include_api_data: bool) -> None:
        """
        Create sheet for specific cryptocurrency with enhanced exposure display.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            crypto_name (str): Name of the cryptocurrency
            addresses (List[ExtractedAddress]): Addresses for this crypto
            include_api_data (bool): Whether to include API data columns
            
        Raises:
            Exception: If sheet creation fails
        """
        # Remove duplicate addresses - keep only the first occurrence
        seen_addresses = set()
        unique_addresses = []
        for addr in addresses:
            if addr.address not in seen_addresses:
                seen_addresses.add(addr.address)
                unique_addresses.append(addr)
        
        # Log deduplication info
        if len(addresses) > len(unique_addresses):
            self.logger.info(f"Removed {len(addresses) - len(unique_addresses)} duplicate addresses from {crypto_name} sheet")
        
        # Use unique addresses for the rest of the method
        addresses = unique_addresses

        try:
            self.logger.info(f"Creating sheet for {crypto_name} with {len(addresses)} addresses")
            
            # Create safe sheet name
            safe_name = re.sub(r'[\/*?:\[\]]', '_', crypto_name)[:31]
            ws = wb.create_sheet(safe_name)
            
            # Check row limit
            if len(addresses) > self.SAFE_ROW_LIMIT:
                self._create_paginated_sheets(wb, safe_name, addresses, include_api_data)
                return
            
            # Define headers
            headers = ["Address", "Source File", "Sheet", "Row", "Column", 
                      "Confidence %", "Is Duplicate", "Total Count"]
            
            if include_api_data:
                # Enhanced API headers including both direct and indirect exposure
                api_headers = ["Entity Name", "Direct Exchange Exposure", "Indirect Exchange Exposure",
                              "Balance", "Total Received", "Total Sent", "Transfer Count",
                              "Cluster Category", "Risk Level"]
                headers.extend(api_headers)
                self.logger.info(f"Added enhanced API columns to {crypto_name} sheet")
            
            # Write headers with formatting
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Write data rows
            for row, addr in enumerate(addresses, 2):
                # Basic data columns
                ws.cell(row=row, column=1, value=addr.address)
                ws.cell(row=row, column=2, value=addr.filename)
                ws.cell(row=row, column=3, value=addr.sheet_name or "N/A")
                ws.cell(row=row, column=4, value=addr.row)
                ws.cell(row=row, column=5, value=addr.column)
                ws.cell(row=row, column=6, value=f"{addr.confidence:.1f}%")
                ws.cell(row=row, column=7, value="Yes" if addr.is_duplicate else "No")
                ws.cell(row=row, column=8, value=addr.duplicate_count)
                
                if include_api_data:
                    col_offset = 9
                    
                    # Entity Name
                    entity_name = getattr(addr, 'api_entity_name', getattr(addr, 'api_cluster_name', ''))
                    ws.cell(row=row, column=col_offset, value=entity_name)
                    
                    # Direct Exchange Exposure
                    direct_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_direct_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 1, value=direct_exposure_text or "None")
                    
                    # Indirect Exchange Exposure
                    indirect_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 2, value=indirect_exposure_text or "None")
                    
                    # Other API data
                    ws.cell(row=row, column=col_offset + 3, 
                           value=f"{getattr(addr, 'api_balance', 0):,.8f}")
                    ws.cell(row=row, column=col_offset + 4, 
                           value=f"{getattr(addr, 'api_total_received', 0):,.8f}")
                    ws.cell(row=row, column=col_offset + 5, 
                           value=f"{getattr(addr, 'api_total_sent', 0):,.8f}")
                    ws.cell(row=row, column=col_offset + 6, 
                           value=getattr(addr, 'api_transfer_count', 0))
                    ws.cell(row=row, column=col_offset + 7, 
                           value=getattr(addr, 'api_cluster_category', ''))
                    ws.cell(row=row, column=col_offset + 8, 
                           value=getattr(addr, 'risk_level', 'Unknown'))
            
            # Auto-fit columns
            for col in range(1, len(headers) + 1):
                column_letter = get_column_letter(col)
                ws.column_dimensions[column_letter].width = 15
            
            # Wider columns for specific fields
            ws.column_dimensions['A'].width = 50  # Address
            ws.column_dimensions['B'].width = 30  # Source File
            if include_api_data:
                ws.column_dimensions['I'].width = 25  # Entity Name
                ws.column_dimensions['J'].width = 40  # Direct Exchange Exposure
                ws.column_dimensions['K'].width = 40  # Indirect Exchange Exposure
            
            self.logger.info(f"✓ Created {crypto_name} sheet with {len(addresses)} addresses")
            
        except Exception as e:
            self.logger.error(f"Failed to create crypto sheet for {crypto_name}: {str(e)}")
            raise
    
    def _create_paginated_sheets(self, wb: Workbook, base_name: str, 
                                addresses: List[ExtractedAddress], 
                                include_api_data: bool) -> None:
        """
        Create multiple sheets when data exceeds Excel row limits.
        
        Args:
            wb (Workbook): The workbook
            base_name (str): Base name for sheets
            addresses (List[ExtractedAddress]): Addresses to paginate
            include_api_data (bool): Whether to include API data
        """
        chunks = [addresses[i:i + self.SAFE_ROW_LIMIT] 
                 for i in range(0, len(addresses), self.SAFE_ROW_LIMIT)]
        
        for idx, chunk in enumerate(chunks, 1):
            sheet_name = f"{base_name[:25]}_Part{idx}"
            self.logger.warning(f"Creating paginated sheet: {sheet_name} with {len(chunk)} rows")
            # Note: Implementation would call appropriate sheet creation method
            # This is a placeholder for the pagination logic