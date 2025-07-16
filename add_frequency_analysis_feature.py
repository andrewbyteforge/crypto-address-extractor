#!/usr/bin/env python3
"""
Address Frequency Analysis Feature Update Script
===============================================

File: add_frequency_analysis_feature.py
Function: Updates file_handler.py to include the new Address Frequency Analysis sheet

This script safely updates the existing file_handler.py to add the new frequency
analysis functionality without breaking existing code.

Usage:
    python add_frequency_analysis_feature.py

Author: Crypto Extractor Tool  
Date: 2025-07-16
Version: 1.0.0 - Initial implementation
"""

import os
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def backup_file_handler():
    """Create a backup of the current file_handler.py."""
    try:
        if os.path.exists('file_handler.py'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'file_handler_backup_{timestamp}.py'
            
            with open('file_handler.py', 'r', encoding='utf-8') as original:
                content = original.read()
            
            with open(backup_name, 'w', encoding='utf-8') as backup:
                backup.write(content)
            
            logger.info(f"✅ Created backup: {backup_name}")
            return backup_name
        else:
            logger.error("❌ file_handler.py not found")
            return None
    except Exception as e:
        logger.error(f"❌ Failed to create backup: {e}")
        return None

def read_file_handler():
    """Read the current file_handler.py content."""
    try:
        with open('file_handler.py', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"❌ Failed to read file_handler.py: {e}")
        return None

def check_if_feature_exists(content):
    """Check if the frequency analysis feature already exists."""
    patterns = [
        r'_create_frequency_analysis_sheet',
        r'Address Frequency Analysis',
        r'cluster_address_frequency'
    ]
    
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False

def add_import_if_missing(content):
    """Add Counter import if not present."""
    if 'from collections import Counter' not in content and 'from collections import' in content:
        # Add Counter to existing collections import
        content = re.sub(
            r'from collections import ([^\\n]+)',
            lambda m: f"from collections import {m.group(1)}, Counter" if 'Counter' not in m.group(1) else m.group(0),
            content
        )
    elif 'from collections import' not in content:
        # Add new import after existing imports
        import_pos = content.find('from extractor import')
        if import_pos != -1:
            content = content[:import_pos] + 'from collections import Counter\\n' + content[import_pos:]
    
    return content

def update_write_to_excel_method(content):
    """Update the write_to_excel method to include the frequency analysis sheet."""
    
    # Find the write_to_excel method
    pattern = r'(def write_to_excel.*?# 2\\..*?Column Definitions sheet.*?\\n)(.*?)(# 3\\. All Addresses sheet)'
    
    replacement = r'\\1            # 3. Address Frequency Analysis sheet (position 2) - NEW FEATURE\n            self._create_frequency_analysis_sheet(wb, addresses, include_api_data)\n            \n            \\3'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Update the position numbers in comments
    updated_content = re.sub(r'# 3\\. All Addresses sheet \\(position 2\\)', '# 4. All Addresses sheet (position 3)', updated_content)
    updated_content = re.sub(r'# 4\\. Individual crypto sheets \\(positions 3\\+\\)', '# 5. Individual crypto sheets (positions 4+)', updated_content)
    updated_content = re.sub(r'# 5\\. Optional: Create duplicate analysis', '# 6. Optional: Create duplicate analysis', updated_content)
    
    return updated_content

def add_frequency_analysis_methods(content):
    """Add the new frequency analysis methods to the FileHandler class."""
    
    methods_code = '''
    def _create_frequency_analysis_sheet(self, wb: Workbook, addresses: List[ExtractedAddress], 
                                       include_api_data: bool = False) -> None:
        """
        Create Address Frequency Analysis sheet showing cluster address frequencies.
        
        File: file_handler.py
        Function: _create_frequency_analysis_sheet()
        
        This sheet shows how many times each cluster address appears across all datasets,
        using existing Chainalysis API data without making additional API calls.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            addresses (List[ExtractedAddress]): List of all extracted addresses
            include_api_data (bool): Whether API data is available
            
        Raises:
            Exception: If frequency analysis sheet creation fails
        """
        try:
            self.logger.info("Creating Address Frequency Analysis sheet")
            
            # Create frequency data structure
            frequency_data = self._analyze_cluster_frequency(addresses, include_api_data)
            
            # Create worksheet
            ws = wb.create_sheet("Address Frequency Analysis")
            
            # Add statistics summary at the top (will insert rows)
            self._add_frequency_statistics(ws, frequency_data, len(addresses))
            
            # Define headers (now starting at row 5 due to statistics)
            headers = [
                "Cluster Address",
                "Cluster Name", 
                "Frequency Count",
                "Cryptocurrency Type",
                "Files Containing Address",
                "Sheets Containing Address"
            ]
            
            # Write headers with styling at row 5
            self._write_frequency_headers_with_styling(ws, headers, start_row=5)
            
            # Sort frequency data by count (highest first)
            sorted_data = sorted(frequency_data, key=lambda x: x['frequency'], reverse=True)
            
            # Write frequency data starting at row 6
            for row_idx, freq_data in enumerate(sorted_data, start=6):
                self._write_frequency_row(ws, row_idx, freq_data)
            
            # Apply color coding based on frequency (skip statistics rows)
            self._apply_frequency_color_coding(ws, sorted_data, start_row=6)
            
            # Auto-fit columns
            self._auto_fit_frequency_columns(ws)
            
            self.logger.info(f"✓ Created Address Frequency Analysis sheet with {len(frequency_data)} cluster addresses")
            
        except Exception as e:
            self.logger.error(f"Failed to create Address Frequency Analysis sheet: {str(e)}", exc_info=True)
            raise

    def _analyze_cluster_frequency(self, addresses: List[ExtractedAddress], 
                                 include_api_data: bool) -> List[Dict]:
        """
        Analyze cluster address frequencies from extracted addresses.
        
        File: file_handler.py
        Function: _analyze_cluster_frequency()
        
        Args:
            addresses (List[ExtractedAddress]): List of extracted addresses
            include_api_data (bool): Whether API data is available
            
        Returns:
            List[Dict]: List of frequency analysis data
        """
        self.logger.info("Analyzing cluster address frequencies")
        
        # Group addresses by cluster address
        cluster_groups = defaultdict(lambda: {
            'addresses': [],
            'cluster_name': 'Unknown',
            'crypto_types': set(),
            'files': set(),
            'sheets': set()
        })
        
        for addr in addresses:
            # Determine the cluster address to use
            if include_api_data and hasattr(addr, 'api_cluster_root_address') and addr.api_cluster_root_address:
                cluster_address = addr.api_cluster_root_address
                cluster_name = getattr(addr, 'api_cluster_name', 'Unknown')
            else:
                # Fallback to original address if no cluster data
                cluster_address = addr.address
                cluster_name = 'Unknown'
            
            # Add to cluster group
            cluster_groups[cluster_address]['addresses'].append(addr)
            cluster_groups[cluster_address]['cluster_name'] = cluster_name
            cluster_groups[cluster_address]['crypto_types'].add(addr.crypto_type)
            cluster_groups[cluster_address]['files'].add(addr.filename)
            
            # Add sheet name if available
            if hasattr(addr, 'sheet_name') and addr.sheet_name:
                cluster_groups[cluster_address]['sheets'].add(addr.sheet_name)
        
        # Convert to frequency analysis format
        frequency_data = []
        for cluster_address, group_data in cluster_groups.items():
            frequency_data.append({
                'cluster_address': cluster_address,
                'cluster_name': group_data['cluster_name'],
                'frequency': len(group_data['addresses']),
                'crypto_types': ', '.join(sorted(group_data['crypto_types'])),
                'files': ', '.join(sorted(group_data['files'])),
                'sheets': ', '.join(sorted(group_data['sheets'])) if group_data['sheets'] else 'N/A'
            })
        
        self.logger.info(f"Analyzed {len(frequency_data)} unique cluster addresses")
        return frequency_data

    def _write_frequency_headers_with_styling(self, ws: Worksheet, headers: List[str], start_row: int = 1) -> None:
        """
        Write headers with professional styling.
        
        File: file_handler.py
        Function: _write_frequency_headers_with_styling()
        """
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=start_row, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"), 
                top=Side(style="thin"),
                bottom=Side(style="thin")
            )

    def _write_frequency_row(self, ws: Worksheet, row_idx: int, freq_data: Dict) -> None:
        """
        Write a single frequency data row.
        
        File: file_handler.py
        Function: _write_frequency_row()
        """
        ws.cell(row=row_idx, column=1, value=freq_data['cluster_address'])
        ws.cell(row=row_idx, column=2, value=freq_data['cluster_name'])
        ws.cell(row=row_idx, column=3, value=freq_data['frequency'])
        ws.cell(row=row_idx, column=4, value=freq_data['crypto_types'])
        ws.cell(row=row_idx, column=5, value=freq_data['files'])
        ws.cell(row=row_idx, column=6, value=freq_data['sheets'])

    def _apply_frequency_color_coding(self, ws: Worksheet, sorted_data: List[Dict], start_row: int = 2) -> None:
        """
        Apply color coding to frequency analysis sheet based on frequency ranges.
        
        File: file_handler.py
        Function: _apply_frequency_color_coding()
        
        Color Scheme:
        - Red: 10+ occurrences (very high frequency)
        - Orange: 5-9 occurrences (high frequency)  
        - Yellow: 3-4 occurrences (medium frequency)
        - Light Green: 2 occurrences (low frequency)
        - White: 1 occurrence (single occurrence)
        """
        self.logger.info("Applying frequency-based color coding")
        
        # Define color fills
        colors = {
            'very_high': PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid"),  # Red
            'high': PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid"),       # Orange  
            'medium': PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid"),     # Yellow
            'low': PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid"),        # Light Green
            'single': PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")      # White
        }
        
        # Apply colors based on frequency
        for idx, freq_data in enumerate(sorted_data):
            row_idx = start_row + idx
            frequency = freq_data['frequency']
            
            # Determine color based on frequency
            if frequency >= 10:
                fill_color = colors['very_high']
            elif frequency >= 5:
                fill_color = colors['high']
            elif frequency >= 3:
                fill_color = colors['medium']
            elif frequency == 2:
                fill_color = colors['low']
            else:  # frequency == 1
                fill_color = colors['single']
            
            # Apply color to all cells in the row
            for col in range(1, 7):  # 6 columns
                ws.cell(row=row_idx, column=col).fill = fill_color

    def _auto_fit_frequency_columns(self, ws: Worksheet) -> None:
        """
        Auto-fit columns for optimal display.
        
        File: file_handler.py
        Function: _auto_fit_frequency_columns()
        """
        # Set specific column widths for frequency analysis
        column_widths = {
            'A': 50,  # Cluster Address
            'B': 30,  # Cluster Name
            'C': 15,  # Frequency Count
            'D': 20,  # Cryptocurrency Type
            'E': 40,  # Files Containing Address
            'F': 30   # Sheets Containing Address
        }
        
        for column, width in column_widths.items():
            ws.column_dimensions[column].width = width

    def _add_frequency_statistics(self, ws: Worksheet, frequency_data: List[Dict], 
                                total_addresses: int) -> None:
        """
        Add statistical summary to the frequency analysis sheet.
        
        File: file_handler.py
        Function: _add_frequency_statistics()
        
        This adds summary statistics above the main data table.
        """
        # Calculate statistics
        if not frequency_data:
            # Handle empty data case
            ws.cell(row=1, column=1, value="ADDRESS FREQUENCY ANALYSIS SUMMARY").font = Font(bold=True, size=14)
            ws.cell(row=2, column=1, value=f"Total Addresses Analyzed: {total_addresses}")
            ws.cell(row=2, column=3, value="Unique Cluster Addresses: 0")
            ws.cell(row=3, column=1, value="No frequency data available")
            return
        
        frequencies = [data['frequency'] for data in frequency_data]
        total_unique_clusters = len(frequency_data)
        avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0
        max_frequency = max(frequencies) if frequencies else 0
        
        # Find the most frequent cluster
        most_frequent = max(frequency_data, key=lambda x: x['frequency']) if frequency_data else None
        
        # Write statistics
        ws.cell(row=1, column=1, value="ADDRESS FREQUENCY ANALYSIS SUMMARY").font = Font(bold=True, size=14)
        ws.cell(row=2, column=1, value=f"Total Addresses Analyzed: {total_addresses}")
        ws.cell(row=2, column=3, value=f"Unique Cluster Addresses: {total_unique_clusters}")
        ws.cell(row=3, column=1, value=f"Average Frequency: {avg_frequency:.1f}")
        ws.cell(row=3, column=3, value=f"Maximum Frequency: {max_frequency}")
        
        if most_frequent:
            ws.cell(row=4, column=1, value=f"Most Frequent Cluster: {most_frequent['cluster_name']} ({most_frequent['frequency']} occurrences)")
        
        # Style the statistics section
        for row in range(1, 5):
            for col in range(1, 7):
                cell = ws.cell(row=row, column=col)
                if cell.value:  # Only style cells with content
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="F0F0F0", end_color="F0F0F0", fill_type="solid")
'''
    
    # Find the last method in the FileHandler class
    # Look for the end of the class (next class definition or end of file)
    class_end_pattern = r'(class FileHandler:.*?)(\n\nclass|\n\n# |$)'
    
    match = re.search(class_end_pattern, content, re.DOTALL)
    if match:
        class_content = match.group(1)
        # Add methods before the class ends
        updated_class = class_content + methods_code
        content = content.replace(class_content, updated_class)
    else:
        # Fallback: add at end of file
        content += methods_code
    
    return content

def write_updated_file(content):
    """Write the updated content back to file_handler.py."""
    try:
        with open('file_handler.py', 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info("✅ Successfully updated file_handler.py")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to write updated file: {e}")
        return False

def main():
    """Main function to update file_handler.py with frequency analysis feature."""
    logger.info("🚀 Starting Address Frequency Analysis Feature Update")
    
    # Step 1: Create backup
    backup_file = backup_file_handler()
    if not backup_file:
        return 1
    
    # Step 2: Read current file
    content = read_file_handler()
    if not content:
        return 1
    
    # Step 3: Check if feature already exists
    if check_if_feature_exists(content):
        logger.info("⚠️  Address Frequency Analysis feature already exists")
        return 0
    
    # Step 4: Apply updates
    logger.info("📝 Adding Counter import...")
    content = add_import_if_missing(content)
    
    logger.info("📝 Updating write_to_excel method...")
    content = update_write_to_excel_method(content)
    
    logger.info("📝 Adding frequency analysis methods...")
    content = add_frequency_analysis_methods(content)
    
    # Step 5: Write updated file
    if write_updated_file(content):
        logger.info("🎉 Address Frequency Analysis feature successfully added!")
        logger.info(f"📦 Backup saved as: {backup_file}")
        logger.info("")
        logger.info("📋 Summary of changes:")
        logger.info("  ✅ Added _create_frequency_analysis_sheet() method")
        logger.info("  ✅ Added _analyze_cluster_frequency() method")
        logger.info("  ✅ Added _write_frequency_headers_with_styling() method")
        logger.info("  ✅ Added _write_frequency_row() method")
        logger.info("  ✅ Added _apply_frequency_color_coding() method")
        logger.info("  ✅ Added _auto_fit_frequency_columns() method")
        logger.info("  ✅ Added _add_frequency_statistics() method")
        logger.info("  ✅ Updated write_to_excel() to include new sheet")
        logger.info("")
        logger.info("🔧 Next steps:")
        logger.info("  1. Test the updated functionality")
        logger.info("  2. Run an extraction to see the new 'Address Frequency Analysis' sheet")
        logger.info("  3. Verify color coding and statistics are working correctly")
        return 0
    else:
        logger.error("❌ Failed to apply updates")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())