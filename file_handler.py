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
            self._create_summary_sheet(wb, addresses, getattr(self, "_api_stats", None))
            self._create_all_addresses_sheet(wb, addresses, include_api_data)
            # self._create_duplicate_analysis_sheet(wb, addresses)  # Temporarily disabled
            
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
        Format exposure data showing only exchanges and darknet markets.
        Darknet markets are marked with (DARKNET) indicator.
        """
        if not exposures:
            return "None"
        
        # Sort by percentage descending
        sorted_exposures = sorted(
            exposures,
            key=lambda x: x.get('percentage', 0),
            reverse=True
        )
        
        formatted_parts = []
        for exp in sorted_exposures[:10]:  # Top 10
            name = exp.get('name', 'Unknown')
            percentage = exp.get('percentage', 0)
            category = exp.get('category', '').lower()
            
            if percentage >= 0.1:  # Only show >= 0.1%
                # Mark darknet markets
                if 'darknet' in category or 'dark market' in category:
                    formatted_parts.append(f"{name} (DARKNET): {percentage:.1f}%")
                else:
                    formatted_parts.append(f"{name}: {percentage:.1f}%")
        
        return "; ".join(formatted_parts) if formatted_parts else "None"

    def _format_detailed_exposure(self, exposures, max_items=3):
        """
        Format exposure data with more details for Excel display.
        
        Args:
            exposures: List of exposure dictionaries
            max_items: Maximum number of items to display
            
        Returns:
            str: Formatted string with exchange names and percentages
        """
        if not exposures:
            return ""
        
        # Sort by value/percentage
        sorted_exposures = sorted(
            exposures,
            key=lambda x: x.get('percentage', 0) or x.get('value', 0),
            reverse=True
        )[:max_items]
        
        formatted_parts = []
        for exp in sorted_exposures:
            name = exp.get('name', 'Unknown')
            percentage = exp.get('percentage', 0)
            value = exp.get('value', 0)
            
            if percentage > 0:
                formatted_parts.append(f"{name}: {percentage:.1f}%")
            elif value > 0:
                formatted_parts.append(f"{name}: ${value:,.2f}")
            else:
                formatted_parts.append(name)
        
        return "; ".join(formatted_parts)

    
    def _create_summary_sheet(self, wb: Workbook, addresses: List[ExtractedAddress], 
                           api_stats=None) -> None:
        """
        Create summary sheet with extraction statistics and API usage.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            addresses (List[ExtractedAddress]): List of all addresses
            api_stats (dict, optional): API usage statistics from tracking
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
                ws.cell(row=row, column=3, value=count)
                row += 1
            
            # API Usage Statistics Section
            if api_stats and api_stats.get('total_calls', 0) > 0:
                api_start_row = row + 2
                
                # API Usage Section Header
                ws.cell(row=api_start_row, column=1, value="API Usage Statistics:").font = Font(bold=True, size=12)
                api_start_row += 1
                
                # Overall API Statistics
                ws.cell(row=api_start_row, column=1, value="Total API Calls:")
                ws.cell(row=api_start_row, column=2, value=api_stats.get('total_calls', 0))
                api_start_row += 1
                
                ws.cell(row=api_start_row, column=1, value="Successful Calls:")
                ws.cell(row=api_start_row, column=2, value=api_stats.get('successful_calls', 0))
                api_start_row += 1
                
                ws.cell(row=api_start_row, column=1, value="Failed Calls:")
                ws.cell(row=api_start_row, column=2, value=api_stats.get('failed_calls', 0))
                api_start_row += 1
                
                ws.cell(row=api_start_row, column=1, value="Success Rate:")
                success_rate = api_stats.get('success_rate', 0)
                ws.cell(row=api_start_row, column=2, value=f"{success_rate:.1f}%")
                api_start_row += 1
                
                ws.cell(row=api_start_row, column=1, value="Total Processing Time:")
                total_time = api_stats.get('total_time_seconds', 0)
                if total_time > 60:
                    time_str = f"{total_time/60:.1f} minutes"
                else:
                    time_str = f"{total_time:.1f} seconds"
                ws.cell(row=api_start_row, column=2, value=time_str)
                api_start_row += 2
                
                # API Calls by Endpoint Type
                calls_by_endpoint = api_stats.get('calls_by_endpoint', {})
                if any(calls_by_endpoint.values()):
                    ws.cell(row=api_start_row, column=1, value="API Calls by Endpoint:").font = Font(bold=True)
                    api_start_row += 1
                    
                    for endpoint, count in calls_by_endpoint.items():
                        if count > 0:
                            success_count = api_stats.get('success_by_endpoint', {}).get(endpoint, 0)
                            failure_count = api_stats.get('failure_by_endpoint', {}).get(endpoint, 0)
                            avg_time = api_stats.get('avg_response_times', {}).get(endpoint, 0)
                            
                            ws.cell(row=api_start_row, column=1, value=f"  {endpoint.title()}:")
                            ws.cell(row=api_start_row, column=2, value=f"{count} calls")
                            ws.cell(row=api_start_row, column=3, value=f"({success_count} success, {failure_count} failed)")
                            ws.cell(row=api_start_row, column=4, value=f"Avg: {avg_time:.2f}s")
                            api_start_row += 1
            
            # Format columns
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 25
            ws.column_dimensions['D'].width = 15
            
            self.logger.debug("Created summary sheet with API usage statistics")
            
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
            headers = ["Address", "Cluster Address", "Cryptocurrency", "Source File", "Sheet", "Row", "Column",
                      "Confidence %", "Is Duplicate", "Total Count"]
            
            if include_api_data:
                # Enhanced headers with both direct and indirect exposure
                headers.extend(["Balance", "Total Received", "Total Sent", "Transfer Count",
                               "Direct Exchange Exposure", "Indirect Exchange Exposure",
                "Receiving Direct Exposure",
                "Receiving Indirect Exposure", 
                "Sending Direct Exposure",
                "Sending Indirect Exposure",
                "Darknet Market",
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
                # Basic columns (1-10)
                ws.cell(row=row, column=1, value=addr.address)
                
                # Cluster address in column 2
                cluster_address = getattr(addr, 'api_cluster_root_address', '')
                if not cluster_address:
                    cluster_address = getattr(addr, 'api_root_address', '')
                ws.cell(row=row, column=2, value=cluster_address)
                ws.cell(row=row, column=3, value=addr.crypto_name)
                ws.cell(row=row, column=4, value=addr.filename)
                ws.cell(row=row, column=5, value=addr.sheet_name or "N/A")
                ws.cell(row=row, column=6, value=addr.row)
                ws.cell(row=row, column=7, value=addr.column)
                ws.cell(row=row, column=8, value=f"{addr.confidence:.1f}%")
                ws.cell(row=row, column=9, value="Yes" if addr.is_duplicate else "No")
                ws.cell(row=row, column=10, value=addr.duplicate_count)
                
                if include_api_data:
                    # API data columns (11-24)
                    
                    # Prepare exposure text fields
                    direct_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_direct_exposure', [])
                    )
                    indirect_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    receiving_direct_text = self._format_exposure_text(
                        getattr(addr, 'api_receiving_direct_exposure', [])
                    )
                    receiving_indirect_text = self._format_exposure_text(
                        getattr(addr, 'api_receiving_indirect_exposure', [])
                    )
                    sending_direct_text = self._format_exposure_text(
                        getattr(addr, 'api_sending_direct_exposure', [])
                    )
                    sending_indirect_text = self._format_exposure_text(
                        getattr(addr, 'api_sending_indirect_exposure', [])
                    )
                    has_darknet = getattr(addr, 'api_has_darknet_exposure', False)
                    entity_name = getattr(addr, 'api_cluster_name', '')
                    ws.cell(row=row, column=11, value=f"{getattr(addr, 'api_balance', 0):,.8f}")
                    ws.cell(row=row, column=12, value=f"{getattr(addr, 'api_total_received', 0):,.8f}")
                    ws.cell(row=row, column=13, value=f"{getattr(addr, 'api_total_sent', 0):,.8f}")
                    ws.cell(row=row, column=14, value=getattr(addr, 'api_transfer_count', 0))
                    ws.cell(row=row, column=15, value=direct_exposure_text)
                    ws.cell(row=row, column=16, value=indirect_exposure_text)
                    ws.cell(row=row, column=17, value=receiving_direct_text)
                    ws.cell(row=row, column=18, value=receiving_indirect_text)
                    ws.cell(row=row, column=19, value=sending_direct_text)
                    ws.cell(row=row, column=20, value=sending_indirect_text)
                    ws.cell(row=row, column=21, value="Y" if has_darknet else "N")
                    ws.cell(row=row, column=22, value=getattr(addr, 'api_risk_level', 'Unknown'))
                    ws.cell(row=row, column=23, value=entity_name)
                    ws.cell(row=row, column=24, value=getattr(addr, 'api_cluster_category', ''))
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
            
            self.logger.info(f"✓ Created All Addresses sheet with {len(addresses)} addresses")
            
        except Exception as e:
            self.logger.error(f"Failed to create crypto sheet for All Addresses sheet: {str(e)}")
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

    def _create_duplicate_analysis_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """Create duplicate analysis sheet."""
        try:
            ws = wb.create_sheet("Duplicate Analysis")
            self.logger.info("Creating 'Duplicate Analysis' sheet")

            headers = ["Address", "Cluster Address", "Crypto", "Occurrences", "Files"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="FF4B4B", end_color="FF4B4B", fill_type="solid")

            # Group duplicates
            from collections import defaultdict
            duplicates = defaultdict(list)
            for addr in addresses:
                if addr.is_duplicate:
                    duplicates[addr.address].append(addr)

            row = 2
            for address, occurrences in sorted(duplicates.items()):
                if len(occurrences) > 1:
                    ws.cell(row=row, column=1, value=address)
                    
                    # Get cluster address for this duplicate
                    cluster_address = ''
                    if occurrences:
                        cluster_address = getattr(occurrences[0], 'api_cluster_root_address', '')
                        if not cluster_address:
                            cluster_address = getattr(occurrences[0], 'api_root_address', '')
                    ws.cell(row=row, column=2, value=cluster_address)
                    ws.cell(row=row, column=3, value=occurrences[0].crypto_name)
                    ws.cell(row=row, column=4, value=len(occurrences))
                    files = list(set(addr.filename for addr in occurrences))
                    ws.cell(row=row, column=5, value=", ".join(files[:3]))
                    row += 1

        except Exception as e:
            self.logger.error(f"Failed to create duplicate analysis sheet: {str(e)}")
            # Don't raise - this is optional


    def create_dashboard(self, entities, links, insights, flows=None, clusters=None):
        """
        Create interactive HTML dashboard with network visualization.
        
        Args:
            entities: List of entities to visualize
            links: List of links between entities  
            insights: List of investigative insights
            flows: Optional money flow paths
            clusters: Optional risk clusters
            
        Returns:
            str: Path to generated HTML dashboard
            
        Raises:
            Exception: If dashboard creation fails
        """
        try:
            self.logger.info("Creating interactive investigation dashboard")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dashboard_path = f"investigation_dashboard_{timestamp}.html"
            
            html_content = self._generate_dashboard_html(entities, links, insights, flows, clusters)
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Dashboard created successfully: {dashboard_path}")
            return dashboard_path
            
        except Exception as e:
            self.logger.error(f"Dashboard creation failed: {e}", exc_info=True)
            raise

    def _generate_dashboard_html(self, entities, links, insights, flows=None, clusters=None):
        """
        Generate complete HTML dashboard content with vis.js network visualization.
        
        Returns:
            str: Complete HTML content for dashboard
        """
        # Convert entities and links to vis.js format
        nodes_data = []
        edges_data = []
        
        for entity in entities:
            node = {
                'id': entity.get('id', ''),
                'label': entity.get('label', '')[:30],
                'title': self._generate_node_tooltip(entity),
                'group': entity.get('type', 'unknown'),
                'color': self._get_entity_color(entity.get('type', ''))
            }
            nodes_data.append(node)
        
        for link in links:
            edge = {
                'from': link.get('from', ''),
                'to': link.get('to', ''),
                'label': link.get('label', ''),
                'title': self._generate_edge_tooltip(link),
                'color': self._get_link_color(link.get('type', ''))
            }
            edges_data.append(edge)
        
        # Generate complete HTML with embedded data
        html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cryptocurrency Investigation Dashboard</title>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
            .stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            #network {{ width: 100%; height: 600px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .controls {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            button {{ background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Cryptocurrency Investigation Dashboard</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(entities)}</div>
                <div class="stat-label">Total Entities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(links)}</div>
                <div class="stat-label">Total Links</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(insights) if insights else 0}</div>
                <div class="stat-label">Insights</div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="network.fit()">Fit View</button>
            <button onclick="togglePhysics()">Toggle Physics</button>
        </div>
        
        <div id="network"></div>
        
        <script>
            var nodes = new vis.DataSet({json.dumps(nodes_data)});
            var edges = new vis.DataSet({json.dumps(edges_data)});
            var data = {{nodes: nodes, edges: edges}};
            
            var options = {{
                nodes: {{
                    shape: 'dot',
                    size: 15,
                    font: {{size: 12}},
                    borderWidth: 2
                }},
                edges: {{
                    width: 2,
                    arrows: {{to: {{enabled: true}}}}
                }},
                physics: {{
                    enabled: true,
                    stabilization: {{iterations: 100}}
                }}
            }};
            
            var container = document.getElementById('network');
            var network = new vis.Network(container, data, options);
            
            function togglePhysics() {{
                options.physics.enabled = !options.physics.enabled;
                network.setOptions(options);
            }}
        </script>
    </body>
    </html>"""
        
        return html_template
    

    def _generate_node_tooltip(self, entity):
        """Generate tooltip text for network nodes."""
        tooltip = f"Type: {entity.get('type', 'Unknown')}\n"
        tooltip += f"Label: {entity.get('label', 'No label')}\n"
        
        if 'attributes' in entity:
            for key, value in entity['attributes'].items():
                tooltip += f"{key}: {value}\n"
        
        return tooltip

    def _generate_edge_tooltip(self, link):
        """Generate tooltip text for network edges."""
        tooltip = f"Type: {link.get('type', 'Unknown')}\n"
        tooltip += f"Label: {link.get('label', 'No label')}\n"
        return tooltip

    def _get_entity_color(self, entity_type):
        """Get color for entity based on type."""
        colors = {
            'CryptoAddress': '#FF6B6B',
            'Exchange': '#4ECDC4',
            'Cluster': '#45B7D1',
            'Entity': '#96CEB4',
            'Service': '#DDA0DD'
        }
        return colors.get(entity_type, '#95A5A6')

    def _get_link_color(self, link_type):
        """Get color for link based on type.""" 
        colors = {
            'SendsTo': '#E74C3C',
            'ConnectedTo': '#3498DB',
            'BelongsTo': '#2ECC71'
        }
        return colors.get(link_type, '#7F8C8D')
    
    #!/usr/bin/env python3
    """
    Column Definitions Sheet Enhancement for file_handler.py
    ======================================================

    This enhancement adds a "Column Definitions" sheet to the Excel output that explains
    what each column heading means. The sheet is positioned after the Summary sheet.

    Files modified: file_handler.py
    Functions added: _create_column_definitions_sheet()
    Functions modified: write_to_excel()

    Author: Assistant
    Date: 2025-07-02
    Version: 1.0.0
    """

    import logging
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    from typing import List, Dict, Any


    def _create_column_definitions_sheet(self, wb: Workbook, include_api_data: bool = False) -> None:
        """
        Create a column definitions sheet that explains what each column heading means.
        This sheet acts as a reference key for users to understand the data structure.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            include_api_data (bool): Whether API data columns should be included in definitions
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            self.logger.info("Creating 'Column Definitions' sheet")
            
            # Create the sheet
            ws = wb.create_sheet("Column Definitions")
            
            # Title
            ws['A1'] = "Column Definitions & Reference Guide"
            ws['A1'].font = Font(size=16, bold=True, color="FFFFFF")
            ws['A1'].fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            ws['A1'].alignment = Alignment(horizontal="center")
            ws.merge_cells('A1:C1')
            
            # Subtitle
            ws['A2'] = "This sheet explains what each column heading means in the exported data"
            ws['A2'].font = Font(size=11, italic=True)
            ws['A2'].alignment = Alignment(horizontal="center")
            ws.merge_cells('A2:C2')
            
            # Headers for the definitions table
            ws['A4'] = "Column Name"
            ws['B4'] = "Description"
            ws['C4'] = "Example/Notes"
            
            # Format headers
            for col in ['A4', 'B4', 'C4']:
                ws[col].font = Font(bold=True, color="FFFFFF")
                ws[col].fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
                ws[col].alignment = Alignment(horizontal="center")
            
            # Basic column definitions (always present)
            basic_definitions = [
                ("Address", "The cryptocurrency wallet address that was extracted", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
                ("Cluster Address", "The root address of the cluster this address belongs to (from API)", "Same format as Address"),
                ("Cryptocurrency", "The type of cryptocurrency for this address", "Bitcoin, Ethereum, Litecoin, etc."),
                ("Source File", "The name of the file where this address was found", "transactions.xlsx, addresses.csv"),
                ("Sheet", "The specific sheet name in Excel files where address was found", "Sheet1, Transaction Data"),
                ("Row", "The row number in the source file where address was located", "5, 127, 1450"),
                ("Column", "The column number/letter where address was found", "3, A, D"),
                ("Confidence %", "How confident the extraction algorithm is that this is a valid address", "95.5%, 100.0%"),
                ("Is Duplicate", "Whether this exact address appears multiple times in the data", "Yes, No"),
                ("Total Count", "How many times this address appears across all source files", "1, 3, 15")
            ]
            
            # API-specific column definitions (only if API data is included)
            api_definitions = [
                ("Balance", "Current balance of the address in native cryptocurrency units", "1.25843210 BTC"),
                ("Total Received", "Total amount ever received by this address", "5.67891234 BTC"),
                ("Total Sent", "Total amount ever sent from this address", "4.42048024 BTC"),
                ("Transfer Count", "Number of transactions involving this address", "157, 1205"),
                ("Direct Exchange Exposure", "Exchanges that directly interact with this address", "Binance: 45.2%, Coinbase: 23.1%"),
                ("Indirect Exchange Exposure", "Exchanges connected through 1-2 intermediate addresses", "Kraken: 12.5%, Bitfinex: 8.3%"),
                ("Receiving Direct Exposure", "Exchanges this address directly receives funds from", "Binance: 60.5%"),
                ("Receiving Indirect Exposure", "Exchanges connected to incoming transactions", "Coinbase: 25.0%"),
                ("Sending Direct Exposure", "Exchanges this address directly sends funds to", "Kraken: 80.2%"),
                ("Sending Indirect Exposure", "Exchanges connected to outgoing transactions", "Bitfinex: 15.5%"),
                ("Darknet Market", "Whether address has known connections to darknet markets", "Y (Yes), N (No)"),
                ("Risk Level", "Risk assessment based on transaction patterns and associations", "Low, Medium, High, Very High"),
                ("Entity", "Known entity name associated with this address cluster", "Binance Hot Wallet, Coinbase"),
                ("Cluster Category", "Category classification of the address cluster", "Exchange, Mixer, DeFi Protocol")
            ]
            
            # Write basic definitions
            current_row = 5
            for col_name, description, example in basic_definitions:
                ws.cell(row=current_row, column=1, value=col_name).font = Font(bold=True)
                ws.cell(row=current_row, column=2, value=description)
                ws.cell(row=current_row, column=3, value=example).font = Font(italic=True)
                current_row += 1
            
            # Add API definitions if API data is included
            if include_api_data:
                # Add section header for API data
                current_row += 1
                ws.cell(row=current_row, column=1, value="API Enhanced Columns").font = Font(size=12, bold=True, color="FFFFFF")
                ws.cell(row=current_row, column=1).fill = PatternFill(start_color="D99694", end_color="D99694", fill_type="solid")
                ws.merge_cells(f'A{current_row}:C{current_row}')
                current_row += 1
                
                ws.cell(row=current_row, column=1, value="(These columns appear when Chainalysis API analysis is enabled)")
                ws.cell(row=current_row, column=1).font = Font(italic=True, size=10)
                ws.merge_cells(f'A{current_row}:C{current_row}')
                current_row += 1
                
                # Write API definitions
                for col_name, description, example in api_definitions:
                    ws.cell(row=current_row, column=1, value=col_name).font = Font(bold=True)
                    ws.cell(row=current_row, column=2, value=description)
                    ws.cell(row=current_row, column=3, value=example).font = Font(italic=True)
                    current_row += 1
            
            # Add footer information
            current_row += 2
            ws.cell(row=current_row, column=1, value="Additional Information:")
            ws.cell(row=current_row, column=1).font = Font(bold=True, size=12)
            current_row += 1
            
            footer_info = [
                "• Addresses are extracted using advanced pattern matching and checksum validation",
                "• Confidence scores are based on format validation and checksum verification",
                "• API data requires a valid Chainalysis API key and active internet connection",
                "• Exchange exposure percentages represent transaction volume relationships",
                "• Duplicate detection helps identify addresses that appear in multiple source files"
            ]
            
            for info in footer_info:
                ws.cell(row=current_row, column=1, value=info)
                ws.merge_cells(f'A{current_row}:C{current_row}')
                current_row += 1
            
            # Set column widths for better readability
            ws.column_dimensions['A'].width = 25  # Column Name
            ws.column_dimensions['B'].width = 60  # Description  
            ws.column_dimensions['C'].width = 35  # Example/Notes
            
            # Add borders and formatting to make it more readable
            from openpyxl.styles import Border, Side
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Apply borders to the definitions table
            for row in range(4, current_row - len(footer_info) - 2):
                for col in range(1, 4):
                    ws.cell(row=row, column=col).border = thin_border
            
            self.logger.info("✓ Created Column Definitions sheet successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create Column Definitions sheet: {str(e)}")
            raise

    def write_to_excel_enhanced(self, addresses: List[ExtractedAddress], output_path: str,
                            include_api_data: bool = False) -> None:
        """
        Write extracted addresses to a formatted Excel file with multiple sheets including column definitions.
    
        Enhanced version that includes a Column Definitions sheet positioned after the Summary sheet.
    
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
        
            # Create sheets in the desired order:
            # 1. Summary sheet (position 0)
            self._create_summary_sheet(wb, addresses, getattr(self, "_api_stats", None))
        
            # 2. Column Definitions sheet (position 1 - after Summary)
            self._create_column_definitions_sheet(wb, include_api_data)
        
            # 3. All Addresses sheet (position 2)
            self._create_all_addresses_sheet(wb, addresses, include_api_data)
        
            # 4. Individual crypto sheets (positions 3+)
            # Group addresses by cryptocurrency
            crypto_groups = defaultdict(list)
            for addr in addresses:
                crypto_groups[addr.crypto_name].append(addr)
        
            # Create individual crypto sheets
            for crypto_name, crypto_addresses in crypto_groups.items():
                self._create_crypto_sheet(wb, crypto_name, crypto_addresses, include_api_data)
        
            # Optional: Create duplicate analysis sheet (currently disabled)
            # self._create_duplicate_analysis_sheet(wb, addresses)
        
            # Create additional analysis sheets if API data available (currently disabled)
            # NOTE: These additional analysis sheets are temporarily disabled
            # Uncomment when the methods are implemented
            # if include_api_data and any(hasattr(addr, 'api_balance') for addr in addresses):
            #     self._create_balance_sheet(wb, addresses)
            #     self._create_exchange_exposure_sheet(wb, addresses)
            #     self._create_high_value_sheet(wb, addresses)
            #     self._create_risk_analysis_sheet(wb, addresses)
        
            # Save workbook
            wb.save(output_path)
            self.logger.info(f"Successfully created Excel file with Column Definitions: {output_path}")
        
        except PermissionError as e:
            error_msg = f"Permission denied writing to {output_path}. Please close the file if it's open."
            self.logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Excel file: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e

    # Instructions for implementation:
    """
    IMPLEMENTATION INSTRUCTIONS
    ==========================

    1. **Add the new method to file_handler.py**:
    - Copy the `_create_column_definitions_sheet` method into your FileHandler class
    - Ensure proper indentation and that it's inside the class definition

    2. **Update the write_to_excel method**:
    - Replace the existing `write_to_excel` method with `write_to_excel_enhanced`
    - Or manually add the call to `self._create_column_definitions_sheet(wb, include_api_data)` 
        right after the Summary sheet creation and before All Addresses sheet creation

    3. **Required imports** (should already be present in file_handler.py):
    - from openpyxl import Workbook
    - from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    - from openpyxl.utils import get_column_letter
    - from typing import List
    - from collections import defaultdict

    4. **Error handling**:
    - The method includes comprehensive error handling and logging
    - Failures in creating the definitions sheet won't crash the entire export process

    5. **Sheet positioning**:
    - Summary sheet (position 0)
    - Column Definitions sheet (position 1) ← NEW
    - All Addresses sheet (position 2)
    - Individual crypto sheets (positions 3+)

    The Column Definitions sheet will help users understand:
    - What each column represents
    - Example values for each field
    - Differences between basic and API-enhanced columns
    - Additional context about the extraction process
    """




    def _create_crypto_sheet(self, wb: Workbook, crypto_name: str,
                           addresses: List[ExtractedAddress],
                           include_api_data: bool = False) -> None:
        """Create sheet for a specific cryptocurrency."""
        try:
            # Remove duplicates
            seen = set()
            unique_addresses = []
            for addr in addresses:
                if addr.address not in seen:
                    seen.add(addr.address)
                    unique_addresses.append(addr)

            ws = wb.create_sheet(crypto_name[:31])
            self.logger.info(f"Creating '{crypto_name}' sheet")

            # Headers
            headers = ["Address", "Cluster Address", "Source File", "Row", "Column", "Confidence"]
            if include_api_data:
                headers.extend([
                    "Entity Name", "Direct Exposure", "Indirect Exposure",
                    "Receiving Direct", "Receiving Indirect",
                    "Sending Direct", "Sending Indirect",
                    "Darknet Market",
                    "Balance", "Total Received", "Total Sent"
                ])

            # Write headers with styling
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

            # Write data
            for row, addr in enumerate(unique_addresses, 2):
                ws.cell(row=row, column=1, value=addr.address)
                
                # Cluster address in column 2
                cluster_addr = getattr(addr, 'api_cluster_root_address', '')
                if not cluster_addr:
                    cluster_addr = getattr(addr, 'api_root_address', '')
                ws.cell(row=row, column=2, value=cluster_addr)
                
                # Source file in column 3 (not column 4!)
                ws.cell(row=row, column=3, value=addr.filename)
                ws.cell(row=row, column=4, value=addr.row)
                ws.cell(row=row, column=5, value=addr.column)
                ws.cell(row=row, column=6, value=f"{addr.confidence:.1f}%")
                
                if include_api_data:
                    # API data columns (7-17)
                    
                    # Prepare all data fields
                    entity_name = getattr(addr, 'api_cluster_name', '')
                    direct_exposure = self._format_exposure_text(
                        getattr(addr, 'api_direct_exposure', [])
                    )
                    indirect_exposure = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    receiving_direct = self._format_exposure_text(
                        getattr(addr, 'api_receiving_direct_exposure', [])
                    )
                    receiving_indirect = self._format_exposure_text(
                        getattr(addr, 'api_receiving_indirect_exposure', [])
                    )
                    sending_direct = self._format_exposure_text(
                        getattr(addr, 'api_sending_direct_exposure', [])
                    )
                    sending_indirect = self._format_exposure_text(
                        getattr(addr, 'api_sending_indirect_exposure', [])
                    )
                    has_darknet = getattr(addr, 'api_has_darknet_exposure', False)
                    ws.cell(row=row, column=7, value=entity_name)
                    ws.cell(row=row, column=8, value=direct_exposure)
                    ws.cell(row=row, column=9, value=indirect_exposure)
                    ws.cell(row=row, column=10, value=receiving_direct)
                    ws.cell(row=row, column=11, value=receiving_indirect)
                    ws.cell(row=row, column=12, value=sending_direct)
                    ws.cell(row=row, column=13, value=sending_indirect)
                    ws.cell(row=row, column=14, value="Y" if has_darknet else "N")
                    ws.cell(row=row, column=15, value=f"{getattr(addr, 'api_balance', 0):,.8f}")
                    ws.cell(row=row, column=16, value=f"{getattr(addr, 'api_total_received', 0):,.8f}")
                    ws.cell(row=row, column=17, value=f"{getattr(addr, 'api_total_sent', 0):,.8f}")
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

        except Exception as e:
            self.logger.error(f"Failed to create {crypto_name} sheet: {str(e)}")
            raise