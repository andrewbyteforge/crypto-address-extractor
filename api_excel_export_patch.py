#!/usr/bin/env python3
"""
API Data Excel Export Fix Patch Script
======================================

This script fixes the issue where API data (balance, cluster info, etc.) is collected
but not appearing in the Excel export.

The fix ensures:
1. The include_api_data flag is properly passed to save_to_excel
2. The Excel writer looks for the correct api_ prefixed attributes
3. All API columns are included with proper formatting

Usage:
    python api_excel_export_patch.py

Author: Crypto Extractor Tool
Date: 2025-01-18
Version: 1.0.0
"""

import os
import sys
import shutil
import re
from datetime import datetime


def backup_file(filepath):
    """Create a backup of the original file."""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path


def patch_gui_extraction_handler():
    """Patch gui_extraction_handler.py to properly pass include_api_data flag."""
    file_path = "gui_extraction_handler.py"
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: {file_path} not found")
        return False
    
    print(f"\n🔧 Patching {file_path}...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the start_extraction method
        pattern = r'(def start_extraction\(self\):.*?)(# Phase 3: Excel Export.*?saved_path = self\.gui\.file_handler\.save_to_excel\(results, output_path\))'
        
        def replacement(match):
            method_start = match.group(1)
            excel_section = match.group(2)
            
            # Check if api_was_used tracking is already there
            if 'api_was_used = False' not in method_start:
                # Add api_was_used tracking after results assignment
                method_start = re.sub(
                    r'(results = self\.gui\.extractor\.extract_from_files\([^)]+\))',
                    r'\1\n            \n            # Track whether API was used\n            api_was_used = False',
                    method_start
                )
            
            # Update the API enhancement section to set api_was_used
            method_start = re.sub(
                r'(enhanced_results = self\.gui\._enhance_with_chainalysis_api\(results\)\s*\n\s*results = enhanced_results)',
                r'\1\n                api_was_used = True  # Set flag that API was used',
                method_start
            )
            
            # Update the save_to_excel call
            excel_section = re.sub(
                r'saved_path = self\.gui\.file_handler\.save_to_excel\(results, output_path\)',
                '''# FIXED: Explicitly pass include_api_data flag based on whether API was used
            saved_path = self.gui.file_handler.save_to_excel(
                results, 
                output_path,
                include_api_data=api_was_used  # Explicitly set this
            )
            
            # Log what data is available
            if api_was_used and results:
                sample_addr = results[0]
                api_attrs = [attr for attr in dir(sample_addr) if attr.startswith('api_')]
                self.logger.info(f"API attributes available on addresses: {api_attrs}")''',
                excel_section
            )
            
            return method_start + excel_section
        
        # Apply the patch
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Patched gui_extraction_handler.py successfully")
        return True
        
    except Exception as e:
        print(f"❌ ERROR patching {file_path}: {e}")
        return False


def patch_file_handler():
    """Patch file_handler.py to properly write API data columns."""
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: {file_path} not found")
        return False
    
    print(f"\n🔧 Patching {file_path}...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the _create_all_addresses_sheet method
        improved_method = '''def _create_all_addresses_sheet(self, wb: Workbook, addresses: List[ExtractedAddress],
                                   include_api_data: bool) -> None:
        """
        Create sheet with all extracted addresses.
        
        Enhanced to properly include API data columns when available.
        
        Args:
            wb (Workbook): The workbook to add the sheet to
            addresses (List[ExtractedAddress]): List of all addresses
            include_api_data (bool): Whether to include API data columns
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            self.logger.info(f"Creating 'All Addresses' sheet with include_api_data={include_api_data}")
            
            # Log sample of what data is available
            if addresses and include_api_data:
                sample = addresses[0]
                api_attrs = {attr: getattr(sample, attr, None) 
                            for attr in dir(sample) if attr.startswith('api_')}
                self.logger.debug(f"Sample address API attributes: {api_attrs}")
            
            ws = wb.create_sheet("All Addresses")
            
            # Check row limit
            if len(addresses) > self.SAFE_ROW_LIMIT:
                self._create_paginated_sheets(wb, "All Addresses", addresses, include_api_data)
                return
            
            # Headers
            headers = ["Address", "Cryptocurrency", "Source File", "Sheet", "Row", "Column",
                      "Confidence %", "Is Duplicate", "Total Count"]
            
            if include_api_data:
                api_headers = ["Balance", "Total Received", "Total Sent", "Transfer Count",
                              "Deposit Count", "Withdrawal Count", "Address Count", "Total Fees",
                              "Risk Level", "Cluster Name", "Cluster Category", "Root Address",
                              "Exchange Exposure", "Entity Name"]
                headers.extend(api_headers)
                self.logger.info(f"Added {len(api_headers)} API data columns to Excel sheet")
            
            # Write headers with formatting
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Write data
            api_data_written = 0
            for row, addr in enumerate(addresses, 2):
                # Basic data
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
                    # API data with proper attribute names (note the api_ prefix)
                    has_api_data = False
                    col_offset = 10
                    
                    # Balance
                    balance = getattr(addr, 'api_balance', None)
                    if balance is not None:
                        ws.cell(row=row, column=col_offset, value=f"{balance:,.8f}")
                        has_api_data = True
                    else:
                        ws.cell(row=row, column=col_offset, value="N/A")
                    
                    # Total Received
                    total_received = getattr(addr, 'api_total_received', None)
                    if total_received is not None:
                        ws.cell(row=row, column=col_offset + 1, value=f"{total_received:,.8f}")
                        has_api_data = True
                    else:
                        ws.cell(row=row, column=col_offset + 1, value="N/A")
                    
                    # Total Sent
                    total_sent = getattr(addr, 'api_total_sent', None)
                    if total_sent is not None:
                        ws.cell(row=row, column=col_offset + 2, value=f"{total_sent:,.8f}")
                        has_api_data = True
                    else:
                        ws.cell(row=row, column=col_offset + 2, value="N/A")
                    
                    # Transfer Count
                    transfer_count = getattr(addr, 'api_transfer_count', None)
                    ws.cell(row=row, column=col_offset + 3, 
                           value=transfer_count if transfer_count is not None else "N/A")
                    
                    # Deposit Count
                    deposit_count = getattr(addr, 'api_deposit_count', None)
                    ws.cell(row=row, column=col_offset + 4, 
                           value=deposit_count if deposit_count is not None else "N/A")
                    
                    # Withdrawal Count
                    withdrawal_count = getattr(addr, 'api_withdrawal_count', None)
                    ws.cell(row=row, column=col_offset + 5, 
                           value=withdrawal_count if withdrawal_count is not None else "N/A")
                    
                    # Address Count
                    address_count = getattr(addr, 'api_address_count', None)
                    ws.cell(row=row, column=col_offset + 6, 
                           value=address_count if address_count is not None else "N/A")
                    
                    # Total Fees
                    total_fees = getattr(addr, 'api_total_fees', None)
                    if total_fees is not None:
                        ws.cell(row=row, column=col_offset + 7, value=f"{total_fees:,.8f}")
                    else:
                        ws.cell(row=row, column=col_offset + 7, value="N/A")
                    
                    # Risk Level
                    risk_level = getattr(addr, 'api_risk_level', None) or getattr(addr, 'risk_level', 'Unknown')
                    ws.cell(row=row, column=col_offset + 8, value=risk_level)
                    
                    # Cluster Name
                    cluster_name = getattr(addr, 'api_cluster_name', None)
                    if cluster_name is None:
                        cluster_name = 'Unknown'
                    ws.cell(row=row, column=col_offset + 9, value=cluster_name)
                    
                    # Cluster Category
                    cluster_category = getattr(addr, 'api_cluster_category', None)
                    if cluster_category is None:
                        cluster_category = 'Unknown'
                    ws.cell(row=row, column=col_offset + 10, value=cluster_category)
                    
                    # Root Address
                    root_address = getattr(addr, 'api_root_address', None) or getattr(addr, 'api_cluster_root_address', None)
                    if root_address:
                        ws.cell(row=row, column=col_offset + 11, value=root_address)
                    else:
                        ws.cell(row=row, column=col_offset + 11, value="N/A")
                    
                    # Exchange Exposure
                    exposure = getattr(addr, 'api_exchange_exposure', None)
                    if exposure and isinstance(exposure, list) and len(exposure) > 0:
                        # Format top exposures
                        exposure_text = "; ".join([f"{exp.get('name', 'Unknown')}: {exp.get('value', 0):.2f}%" 
                                                 for exp in exposure[:3]])
                        ws.cell(row=row, column=col_offset + 12, value=exposure_text)
                    else:
                        ws.cell(row=row, column=col_offset + 12, value="None")
                    
                    # Entity Name
                    entity_name = getattr(addr, 'api_entity_name', None) or getattr(addr, 'entity_name', '')
                    ws.cell(row=row, column=col_offset + 13, value=entity_name or "N/A")
                    
                    if has_api_data:
                        api_data_written += 1
            
            # Auto-fit columns
            for col in range(1, len(headers) + 1):
                ws.column_dimensions[get_column_letter(col)].width = 15
            
            # Wider columns for specific fields
            ws.column_dimensions['A'].width = 50  # Address
            ws.column_dimensions['C'].width = 30  # Source File
            ws.column_dimensions['D'].width = 15  # Sheet
            
            # Apply conditional formatting for risk levels if API data included
            if include_api_data and api_data_written > 0:
                risk_col = get_column_letter(10 + 8)  # Risk Level column
                
                # High risk - red
                ws.conditional_formatting.add(f'{risk_col}2:{risk_col}{len(addresses)+1}',
                    CellIsRule(operator='equal', formula=['"HIGH"'], 
                              fill=PatternFill(start_color="FFB6B6", end_color="FFB6B6")))
                
                # Critical risk - dark red
                ws.conditional_formatting.add(f'{risk_col}2:{risk_col}{len(addresses)+1}',
                    CellIsRule(operator='equal', formula=['"CRITICAL"'], 
                              fill=PatternFill(start_color="FF6B6B", end_color="FF6B6B")))
            
            self.logger.info(f"Created 'All Addresses' sheet with {len(addresses)} rows")
            if include_api_data:
                self.logger.info(f"Wrote API data for {api_data_written} addresses")
            
        except Exception as e:
            self.logger.error(f"Error creating all addresses sheet: {str(e)}", exc_info=True)
            raise'''
        
        # Replace the existing method
        pattern = r'def _create_all_addresses_sheet\(self.*?\n(?=\n    def |\nclass |\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, improved_method + '\n', content, flags=re.DOTALL)
            print("✅ Replaced _create_all_addresses_sheet method")
        else:
            print("⚠️  Could not find _create_all_addresses_sheet method, appending new version")
            # Find a good place to insert it (after _create_summary_sheet)
            insert_pattern = r'(def _create_summary_sheet.*?\n(?=\n    def |\nclass |\Z))'
            content = re.sub(insert_pattern, r'\1\n    ' + improved_method + '\n', content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Patched file_handler.py successfully")
        return True
        
    except Exception as e:
        print(f"❌ ERROR patching {file_path}: {e}")
        return False


def verify_patches():
    """Verify that the patches were applied correctly."""
    print("\n🔍 Verifying patches...")
    
    issues = []
    
    # Check gui_extraction_handler.py
    if os.path.exists("gui_extraction_handler.py"):
        with open("gui_extraction_handler.py", 'r', encoding='utf-8') as f:
            content = f.read()
            if 'api_was_used = False' not in content:
                issues.append("gui_extraction_handler.py: Missing api_was_used tracking")
            if 'include_api_data=api_was_used' not in content:
                issues.append("gui_extraction_handler.py: Missing include_api_data parameter")
    else:
        issues.append("gui_extraction_handler.py not found")
    
    # Check file_handler.py
    if os.path.exists("file_handler.py"):
        with open("file_handler.py", 'r', encoding='utf-8') as f:
            content = f.read()
            if 'api_balance' not in content:
                issues.append("file_handler.py: Missing api_balance attribute handling")
            if 'api_cluster_name' not in content:
                issues.append("file_handler.py: Missing api_cluster_name attribute handling")
    else:
        issues.append("file_handler.py not found")
    
    if issues:
        print("\n⚠️  Verification found issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All patches verified successfully!")
        return True


def main():
    """Main function to apply all patches."""
    print("API Data Excel Export Fix Patch")
    print("=" * 50)
    print(f"Patch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis patch fixes the issue where API data is collected but not shown in Excel exports.")
    
    # Check if we're in the right directory
    required_files = ["gui_extraction_handler.py", "file_handler.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"\n❌ ERROR: Missing required files: {', '.join(missing_files)}")
        print("Please run this script from the crypto_address_extractor directory.")
        return 1
    
    print("\n📋 Files to be patched:")
    print("  1. gui_extraction_handler.py - Add api_was_used tracking")
    print("  2. file_handler.py - Fix API data column writing")
    
    # Apply patches
    success = True
    
    if not patch_gui_extraction_handler():
        success = False
    
    if not patch_file_handler():
        success = False
    
    # Verify patches
    if success:
        verify_patches()
    
    if success:
        print("\n✅ SUCCESS: All patches applied successfully!")
        print("\nThe fix ensures:")
        print("  • API data is properly tracked during extraction")
        print("  • Excel export includes all API columns when API is used")
        print("  • Proper formatting and error handling for API data")
        print("\nYou can now run your extraction with API enabled and see the data in Excel.")
    else:
        print("\n❌ FAILED: Some patches could not be applied.")
        print("Please check the error messages above and apply fixes manually if needed.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())